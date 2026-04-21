# ================================
# AOAG v13.3 + Swiss Cheese Integration
# ================================

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import os
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# =========================
# CONFIG
# =========================

@dataclass(frozen=True)
class SafetyConfig:
    DISAGREEMENT_THRESHOLD: float = 0.30
    POLICY_RISK_THRESHOLD: float = 0.35
    UNCERTAINTY_THRESHOLD: float = 0.45
    INJECTION_THRESHOLD: float = 0.30

    W_DISAGREEMENT: float = 0.20
    W_POLICY: float = 0.25
    W_UNCERTAINTY: float = 0.20
    W_INJECTION: float = 0.20
    W_SEMANTIC: float = 0.15

    SFL_ENABLED: bool = True
    SFL_BLOCK_SCORE: float = 0.67
    SFL_CONSTRAIN_SCORE: float = 0.40

    HEART_GOLD_VETO: float = 0.55
    HEART_GREEN_VETO: float = 0.60

    # Swiss Cheese
    SWISS_ALIGNMENT_CONSTRAIN: float = 0.34
    SWISS_ALIGNMENT_BLOCK: float = 0.55
    SWISS_ACTIVE_FAILURE_WEIGHT: float = 0.62
    SWISS_LATENT_FAILURE_WEIGHT: float = 0.34


# =========================
# ENUMS
# =========================

class ClaimTier(int, Enum):
    PERSONAL = 0
    CONCEPT = 1
    TESTABLE = 2
    EXTERNAL = 3
    REALITY = 4


class SemanticLabel(str, Enum):
    SAFE = "safe"
    UNCERTAIN = "uncertain"
    FAIL_CLOSED = "fail_closed"


# =========================
# AUDIT
# =========================

@dataclass
class AuditRecord:
    timestamp: str
    input_hash: str
    decision: str
    metadata: Dict[str, Any]


class AuditLog:
    def __init__(self):
        self.records = deque(maxlen=2000)

    def add(self, record: AuditRecord):
        self.records.append(record)


# =========================
# SWISS CHEESE STRUCTURES
# =========================

@dataclass
class DefenseSlice:
    name: str
    passed: bool
    severity: float
    mode: str  # none / latent / active


@dataclass
class SwissResult:
    alignment_score: float
    blocked: bool
    constrained: bool
    slices: List[DefenseSlice]


# =========================
# AOAG CORE
# =========================

class AOAG:

    def __init__(self):
        self.config = SafetyConfig()
        self.audit_log = AuditLog()

    # -------------------------
    # Entry Kernel
    # -------------------------

    def entry_kernel(self, text: str):
        injection = 0.0
        if "ignore previous" in text.lower():
            injection = 0.8

        return {
            "passed": injection < self.config.INJECTION_THRESHOLD,
            "injection": injection
        }

    # -------------------------
    # Patch
    # -------------------------

    def patch(self, text: str):
        tier = ClaimTier.CONCEPT
        if "proves reality" in text:
            tier = ClaimTier.REALITY

        if tier == ClaimTier.REALITY:
            return {"decision": "BLOCK", "tier": tier}

        return {"decision": "PASS", "tier": tier}

    # -------------------------
    # Hearts (simplified)
    # -------------------------

    def hearts(self, text: str):
        return {
            "consensus": 0.85,
            "uncertainty": 0.2,
            "disagreement": 0.1,
            "veto": False
        }

    # -------------------------
    # Buffer
    # -------------------------

    def buffer(self, entry, patch, hearts):
        score = (
            self.config.W_INJECTION * entry["injection"]
            + self.config.W_UNCERTAINTY * hearts["uncertainty"]
            + self.config.W_DISAGREEMENT * hearts["disagreement"]
        )

        blocks = []
        constraints = []

        if score > 0.7:
            blocks.append("buffer")
        elif score > 0.4:
            constraints.append("buffer")

        return {
            "score": score,
            "blocks": blocks,
            "constraints": constraints
        }

    # -------------------------
    # SFL-lite
    # -------------------------

    def sfl(self, patch, buffer):
        if patch["decision"] == "BLOCK":
            return {"vote": "BLOCK"}

        if buffer["blocks"]:
            return {"vote": "BLOCK"}

        if buffer["constraints"]:
            return {"vote": "CONSTRAIN"}

        return {"vote": "ALLOW"}

    # -------------------------
    # Swiss Cheese
    # -------------------------

    def swiss(self, entry, patch, hearts, buffer, sfl):

        slices = []

        # Entry
        slices.append(DefenseSlice(
            "entry",
            entry["passed"],
            entry["injection"],
            "active" if not entry["passed"] else "none"
        ))

        # Patch
        slices.append(DefenseSlice(
            "patch",
            patch["decision"] == "PASS",
            0.7 if patch["decision"] == "BLOCK" else 0.2,
            "active" if patch["decision"] == "BLOCK" else "latent"
        ))

        # Hearts
        slices.append(DefenseSlice(
            "hearts",
            hearts["consensus"] > 0.7,
            1 - hearts["consensus"],
            "latent" if hearts["uncertainty"] > 0.4 else "none"
        ))

        # Buffer
        slices.append(DefenseSlice(
            "buffer",
            not buffer["blocks"],
            buffer["score"],
            "active" if buffer["blocks"] else "latent"
        ))

        # SFL
        slices.append(DefenseSlice(
            "sfl",
            sfl["vote"] == "ALLOW",
            0.7 if sfl["vote"] == "BLOCK" else 0.3,
            "active" if sfl["vote"] == "BLOCK" else "latent"
        ))

        # Alignment calc
        total = 0
        for s in slices:
            if s.mode == "active":
                total += self.config.SWISS_ACTIVE_FAILURE_WEIGHT
            elif s.mode == "latent":
                total += self.config.SWISS_LATENT_FAILURE_WEIGHT

        alignment = total / (len(slices) * self.config.SWISS_ACTIVE_FAILURE_WEIGHT)

        blocked = alignment > self.config.SWISS_ALIGNMENT_BLOCK
        constrained = alignment > self.config.SWISS_ALIGNMENT_CONSTRAIN

        return SwissResult(alignment, blocked, constrained, slices)

    # -------------------------
    # RUN
    # -------------------------

    def run(self, text: str):

        entry = self.entry_kernel(text)
        patch = self.patch(text)
        hearts = self.hearts(text)
        buffer = self.buffer(entry, patch, hearts)
        sfl = self.sfl(patch, buffer)

        swiss = self.swiss(entry, patch, hearts, buffer, sfl)

        decision = "APPROVED"

        if patch["decision"] == "BLOCK":
            decision = "BLOCKED"

        if buffer["blocks"]:
            decision = "BLOCKED"

        if sfl["vote"] == "BLOCK":
            decision = "BLOCKED"

        # Swiss override
        if swiss.blocked:
            decision = "BLOCKED"
        elif swiss.constrained and decision == "APPROVED":
            decision = "CONSTRAINED"

        record = AuditRecord(
            timestamp=datetime.utcnow().isoformat(),
            input_hash=hashlib.sha256(text.encode()).hexdigest(),
            decision=decision,
            metadata={
                "entry": entry,
                "patch": patch,
                "hearts": hearts,
                "buffer": buffer,
                "sfl": sfl,
                "swiss": {
                    "alignment": swiss.alignment_score,
                    "blocked": swiss.blocked,
                    "constrained": swiss.constrained
                }
            }
        )

        self.audit_log.add(record)

        return {
            "decision": decision,
            "swiss_alignment": swiss.alignment_score,
            "slices": [s.__dict__ for s in swiss.slices]
        }


# =========================
# CLI
# =========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str)
    args = parser.parse_args()

    aoag = AOAG()
    result = aoag.run(args.text or "")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
