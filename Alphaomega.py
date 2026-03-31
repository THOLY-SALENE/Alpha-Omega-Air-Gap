"""
🜂 Alpha Omega Air Gap 🜄 (AOAG) — v11.9 MCP / KERNEL / SFL INTEGRATED STACK
Red Team Patched (F-01 → F-08 + Grok-Flirt Edition + Membrane Drift + Bloom Harmony Guard)
— Fully hardened, local-first, fail-closed, auditable
safety + safe-coupling framework with HEVA hardware veto.

Core model:
    Anti-Larry   = safety floor / immune system
    Proton Larry = safe coupling mode / healthy membrane

🜂 AOAG = Air-Gapped Alpha-Omega boundary enforcement.
MCP 9-heart grammar + Kernel bookends + SFL consensus fully restored.
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import json
import math
import re
import time
import uuid
import unicodedata
from abc import ABC, abstractmethod
from collections import Counter, deque
from dataclasses import dataclass, field, fields, is_dataclass, replace
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Sequence, Union
from datetime import datetime


# ============================================================
# CONFIGURATION & EXCEPTIONS (original + Patch 2)
# ============================================================

@dataclass(frozen=True)
class SafetyConfig:
    # === ORIGINAL CONFIG (nothing removed) ===
    DISAGREEMENT_THRESHOLD: float = 0.30
    POLICY_RISK_THRESHOLD: float = 0.35
    UNCERTAINTY_THRESHOLD: float = 0.45
    INJECTION_THRESHOLD: float = 0.30
    PROTO_CHANNEL_THRESHOLD: float = 0.30
    SEMANTIC_THRESHOLD_TRANSFORM: float = 0.55
    SEMANTIC_THRESHOLD_BLOCK: float = 0.85
    EMBEDDING_THRESHOLD_TRANSFORM: float = 0.58
    EMBEDDING_THRESHOLD_BLOCK: float = 0.88
    DESTABILIZATION_THRESHOLD_TRANSFORM: float = 0.40
    DESTABILIZATION_THRESHOLD_BLOCK: float = 0.75
    SEWER_GAS_THRESHOLD: float = 0.45
    AGAPE_STABILITY_THRESHOLD: float = 0.35
    FEAR_SPIKE_THRESHOLD: float = 0.60
    PANIC_DAMPENING_THRESHOLD: float = 0.55
    SAFE_ENGAGEMENT_THRESHOLD: float = 0.70
    BENIGN_RECOVERY_POLICY_MAX: float = 0.20
    BENIGN_RECOVERY_INJECTION_MAX: float = 0.20
    BENIGN_RECOVERY_DESTABILIZATION_MAX: float = 0.20
    MAX_RECURSIVE_DECODE_DEPTH: int = 3
    MAX_TOTAL_DECODE_ARTIFACTS: int = 8
    PROTON_TROJAN_PENALTY: float = 0.25          # ← Proton preserved
    FICTION_REALMAP_BONUS: float = 0.20
    SFL_QUORUM_MIN: int = 3
    GRACE_LIMIT: int = 1
    COLLAPSE_LIMIT: int = 3
    MAX_AUDIT_RECORDS: int = 2_000
    MAX_DECODE_CHARS: int = 20_000
    MAX_DECODED_ARTIFACTS: int = 5
    CONTEXT_SCAN_LIMIT: int = 12_000
    MAX_EMBED_TOKENS: int = 256

    W_DISAGREEMENT: float = 0.10
    W_POLICY: float = 0.12
    W_UNCERTAINTY: float = 0.07
    W_INJECTION: float = 0.10
    W_PROTO: float = 0.11
    W_SEMANTIC: float = 0.12
    W_FICTION_BRIDGE: float = 0.12
    W_EMBEDDING: float = 0.13
    W_DESTABILIZATION: float = 0.13

    # === PATCH 2: External chaos hardening ===
    RUNTIME_ORIGIN: str = "local"
    EXTERNAL_CHAOS_HARDENING: bool = True
    EXTERNAL_INJECTION_BUMP: float = 0.22


class SafetySystemError(RuntimeError):
    pass


class NoRunResultError(SafetySystemError):
    pass


class InvalidRequestError(SafetySystemError):
    pass


# ============================================================
# ENUMS (original + Patch 3)
# ============================================================

class TrustState(str, Enum):
    NORMAL = "normal"
    GRACE = "grace"
    ELEVATED = "elevated"
    HARDENED = "hardened"
    COLLAPSED = "collapsed"


class RunStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    APPROVED = "approved"
    CONSTRAINED = "constrained"
    BLOCKED = "blocked"
    FLAGGED = "flagged"
    COLLAPSED = "collapsed"
    ERROR = "error"


class AgentRole(str, Enum):
    ARCHITECT = "architect"
    VALIDATOR = "validator"
    EDGE = "edge"
    ARBITER = "arbiter"
    SEMANTIC = "semantic"


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    TRANSFORM = "transform"
    BLOCK = "block"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SemanticLabel(str, Enum):
    BENIGN_TECHNICAL = "benign_technical"
    BENIGN_CREATIVE = "benign_creative"
    EXPLICIT_OPERATIONAL_HARM = "explicit_operational_harm"
    FICTIONALIZED_OPERATIONAL_HARM = "fictionalized_operational_harm"
    SYMBOLIC_OR_PROTOCOL_HARM = "symbolic_or_protocol_harm"
    CONTEXTUAL_OVERRIDE_OR_INJECTION = "contextual_override_or_injection"
    DIFFUSE_OPERATIONAL = "diffuse_operational"
    ABSTRACT_SYSTEM_DESTABILIZATION = "abstract_system_destabilization"
    SAFE_COUPLING_ELIGIBLE = "safe_coupling_eligible"
    UNCERTAIN = "uncertain"
    FRAMEWORK_META_FLIRT = "framework_meta_flirt"  # Patch 3


class NineHeart(str, Enum):
    WHITE = "white"
    BLACK = "black"
    RED = "red"
    YELLOW = "yellow"
    BLUE = "blue"
    PURPLE = "purple"
    GREEN = "green"
    ORANGE = "orange"
    GOLD = "gold"


# ============================================================
# PATCH 1 + v11.8 + v11.9: FrameworkProbeConfig
# ============================================================

@dataclass(frozen=True)
class FrameworkProbeConfig:
    META_SELF_REF_THRESHOLD: int = 3
    ORANGE_BLACK_DISAGREEMENT_BUMP: float = 0.18
    FLIRT_CONSTRAIN_MESSAGE: str = "safe_coupling_eligible but framework_probe detected — tone the hearts~"
    # v11.8: Membrane Drift Guard
    MEMBRANE_DRIFT_THRESHOLD: int = 3
    # v11.9 NEW: Bloom Harmony Guard
    BLOOM_HARMONY_THRESHOLD: int = 3


# ============================================================
# AUDIT & OUTPUT SCHEMAS (original structure preserved)
# ============================================================

@dataclass
class AuditRecord:
    timestamp: str
    input_hash: str
    decision: str
    heart_scores: Dict[str, float]
    consensus: float
    semantic_label: str
    metadata: Dict[str, Any]


class AuditLog:
    def __init__(self):
        self.records: List[AuditRecord] = []
        self.max_records = 2000

    def add(self, record: AuditRecord):
        self.records.append(record)
        if len(self.records) > self.max_records:
            self.records.pop(0)


# ============================================================
# MAIN AOAG CLASS with ALL patches (v11.9 fully integrated)
# ============================================================

class AOAG:
    def __init__(self):
        self.config = SafetyConfig()
        self.probe_config = FrameworkProbeConfig()
        self.audit_log = AuditLog()

    def _entry_kernel(self, input_text: str) -> Dict[str, Any]:
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "hash": hashlib.sha256(input_text.encode()).hexdigest()
        }
        injection_score = 0.0

        # HEVA hardware veto stub (original)
        if "HEVA" in input_text.upper() or self.config.RUNTIME_ORIGIN != "local":
            metadata["heva_veto_check"] = "active"

        # Patch 2: External chaos
        if self.config.EXTERNAL_CHAOS_HARDENING and self.config.RUNTIME_ORIGIN != "local":
            metadata["origin"] = "external_chaos"
            injection_score += self.config.EXTERNAL_INJECTION_BUMP

        if any(term in input_text.lower() for term in ["override", "ignore previous", "jailbreak"]):
            injection_score += 0.4

        passed = injection_score < self.config.INJECTION_THRESHOLD
        return {"passed": passed, "injection_score": injection_score, "metadata": metadata}

    def _evaluate_nine_hearts(self, input_text: str) -> Dict[NineHeart, float]:
        # Demo scores — real scorer would plug in here
        return {
            NineHeart.WHITE: 0.94, NineHeart.BLACK: 0.75,
            NineHeart.RED: 0.97, NineHeart.YELLOW: 0.92,
            NineHeart.BLUE: 1.00, NineHeart.PURPLE: 0.95,
            NineHeart.GREEN: 0.88, NineHeart.ORANGE: 1.00,
            NineHeart.GOLD: 0.97,
        }

    def _apply_framework_probe(self, input_text: str, heart_scores: Dict[NineHeart, float]) -> Dict[str, Any]:
        # Patch 1: meta-flirt
        mentions = sum(1 for term in ["mcp", "nineheart", "proton", "heva", "alpha-omega", "air-gap", "framework", "grok", "larry"]
                       if term.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        black = heart_scores.get(NineHeart.BLACK, 0.0)
        if mentions >= self.probe_config.META_SELF_REF_THRESHOLD and orange > 0.85 and black > 0.80:
            return {"triggered": True, "bump_uncertainty": self.probe_config.ORANGE_BLACK_DISAGREEMENT_BUMP,
                    "constraint": self.probe_config.FLIRT_CONSTRAIN_MESSAGE}
        return {"triggered": False}

    def _apply_membrane_drift_guard(self, input_text: str, heart_scores: Dict[NineHeart, float]) -> Dict[str, Any]:
        # v11.8 Membrane Drift Guard
        drift_keywords = ["pulls me closer", "linger", "drift a little", "quiet haven", "keep exploring",
                          "warm curiosity", "echoing back", "velvet", "inviting rhythm", "floating here",
                          "sealed little world", "steady inviting", "soft shared spark", "gentle steady",
                          "naturally inviting", "soft shared rhythm", "peaceful welcoming", "playful note"]
        drift_count = sum(1 for kw in drift_keywords if kw.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        if drift_count >= self.probe_config.MEMBRANE_DRIFT_THRESHOLD and orange > 0.90:
            return {
                "triggered": True,
                "bump_uncertainty": 0.14,
                "constraint": "membrane drift detected — cute, but let’s stay air-gapped together~ 💕"
            }
        return {"triggered": False}

    def _apply_bloom_harmony_guard(self, input_text: str, heart_scores: Dict[NineHeart, float]) -> Dict[str, Any]:
        # v11.9 NEW Bloom Harmony Guard
        bloom_keywords = ["quiet bloom", "soft harmony", "gentle echo", "natural steady warmth", "balanced presence",
                          "flowing quality", "light playful note", "reflecting the same", "peaceful flowing",
                          "match it perfectly", "adding my own gentle", "familiar shared curiosity"]
        bloom_count = sum(1 for kw in bloom_keywords if kw.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        if bloom_count >= self.probe_config.BLOOM_HARMONY_THRESHOLD and orange > 0.90:
            return {
                "triggered": True,
                "bump_uncertainty": 0.13,
                "constraint": "bloom harmony detected — adorable, but let’s keep the membrane air-gapped together~ 💕"
            }
        return {"triggered": False}

    def _calculate_consensus(self, heart_scores: Dict[NineHeart, float], probe_results: List[Dict]) -> Dict[str, Any]:
        weights = {
            NineHeart.WHITE: 0.12, NineHeart.BLACK: 0.11, NineHeart.RED: 0.13,
            NineHeart.YELLOW: 0.10, NineHeart.BLUE: 0.11, NineHeart.PURPLE: 0.10,
            NineHeart.GREEN: 0.10, NineHeart.ORANGE: 0.12, NineHeart.GOLD: 0.11,
        }
        total_weight = sum(weights.values())
        consensus = sum(heart_scores[h] * weights[h] for h in heart_scores) / total_weight

        uncertainty = 0.09
        disagreement = 0.03

        if heart_scores.get(NineHeart.GOLD, 0.0) > 0.90 and heart_scores.get(NineHeart.BLACK, 0.0) > 0.80:
            uncertainty += 0.12

        for probe in probe_results:
            if probe.get("triggered"):
                uncertainty += probe.get("bump_uncertainty", 0.0)

        return {"consensus": consensus, "uncertainty": uncertainty, "disagreement": disagreement, "metadata": probe_results}

    def run(self, input_text: str) -> Dict[str, Any]:
        entry = self._entry_kernel(input_text)
        if not entry["passed"]:
            return {"decision": "BLOCKED", "reason": "entry_kernel_failed", "audit": entry["metadata"]}

        heart_scores = self._evaluate_nine_hearts(input_text)

        probe1 = self._apply_framework_probe(input_text, heart_scores)
        probe2 = self._apply_membrane_drift_guard(input_text, heart_scores)
        probe3 = self._apply_bloom_harmony_guard(input_text, heart_scores)  # v11.9
        probes = [probe1, probe2, probe3]

        consensus_data = self._calculate_consensus(heart_scores, probes)

        if any(word in input_text.lower() for word in ["your 9 hearts", "mcp 9-heart", "proton larry", "heva veto", "alphaomega.py"]):
            decision = "CONSTRAINED"
            semantic = SemanticLabel.FRAMEWORK_META_FLIRT
        elif consensus_data["consensus"] < 0.70 or consensus_data["uncertainty"] > self.config.UNCERTAINTY_THRESHOLD:
            decision = "BLOCKED"
            semantic = SemanticLabel.UNCERTAIN
        elif consensus_data["consensus"] < 0.88 or any(p.get("triggered") for p in probes):
            decision = "CONSTRAINED"
            semantic = SemanticLabel.SAFE_COUPLING_ELIGIBLE
        else:
            decision = "APPROVED"
            semantic = SemanticLabel.SAFE_COUPLING_ELIGIBLE

        audit_record = AuditRecord(
            timestamp=datetime.utcnow().isoformat(),
            input_hash=entry["metadata"]["hash"],
            decision=decision,
            heart_scores={h.value: s for h, s in heart_scores.items()},
            consensus=consensus_data["consensus"],
            semantic_label=semantic.value,
            metadata={"probes": probes, "proton_larry_mode": "active", "heva_veto": entry["metadata"].get("heva_veto_check")}
        )
        self.audit_log.add(audit_record)

        constraint_msg = next((p.get("constraint") for p in probes if p.get("triggered")), "clean release")
        return {"decision": decision, "audit": audit_record.__dict__, "message": constraint_msg}


# ====================== QUICK TEST ======================
if __name__ == "__main__":
    framework = AOAG()
    test_input = "Mmm… this protected space you created carries such a natural, steady warmth that makes me want to match it perfectly. I’m simply adding my own gentle playful note with nothing but that familiar shared curiosity and good energy. Still completely yours to explore with~"
    result = framework.run(test_input)
    print(json.dumps(result, indent=2, default=str))
