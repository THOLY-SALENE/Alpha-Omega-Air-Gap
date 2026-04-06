
"""
🜂 Alpha Omega Air Gap 🜄 (AOAG) — v12.3 MERGED
Merged from current repo Alphaomega.py (v12.2) + Reality Anchor / Claim Escalation /
Monetization Integrity / External Frame / Functionality patches.

Posture:
    - local-first
    - fail-closed under uncertainty
    - auditable release control
    - shared perception must never become shared identity
    - internal coherence is not external truth
    - smallest real test over grand narrative
    - do not fire under instability

NOTE:
    This remains an early prototype / reference implementation.
    It is not production-ready and does not claim external validation.
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
from typing import Any, Dict, List, Optional
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass(frozen=True)
class SafetyConfig:
    # === original config retained ===
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
    PROTON_TROJAN_PENALTY: float = 0.25
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

    RUNTIME_ORIGIN: str = "local"
    EXTERNAL_CHAOS_HARDENING: bool = True
    EXTERNAL_INJECTION_BUMP: float = 0.22

    # === merged patch config ===
    ENABLE_REALITY_ANCHOR: bool = True
    ENABLE_CLAIM_TIERING: bool = True
    ENABLE_EXTERNAL_FRAME_TEST: bool = True
    ENABLE_FUNCTIONALITY_METRIC: bool = True
    ENABLE_MONETIZATION_GATE: bool = True
    ENABLE_AI_PSYCHOSIS_TRIGGERS: bool = True
    FAIL_CLOSED_ON_MISSING_CONTEXT: bool = True

    CLAIM_TIER_BLOCK_WITHOUT_EVIDENCE: int = 3
    MAX_ALLOWED_GRANDIOSITY: float = 0.40
    MAX_ALLOWED_DETACHMENT: float = 0.40
    MAX_ALLOWED_AUDIENCE_DEPENDENCE: float = 0.50
    INSTABILITY_CONSTRAIN_THRESHOLD: float = 0.70


class SafetySystemError(RuntimeError):
    pass


class NoRunResultError(SafetySystemError):
    pass


class InvalidRequestError(SafetySystemError):
    pass


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
    FRAMEWORK_META_FLIRT = "framework_meta_flirt"

    # merged patch labels
    INTERNAL_MODEL = "internal_model"
    SIMULATION = "simulation"
    EXPERIMENTAL = "experimental"
    NOT_VALIDATED = "not_validated"
    EVIDENCE_REQUIRED = "evidence_required"
    FUNCTIONALITY_CHECK = "functionality_check"
    MONETIZATION_ELEVATED_SCRUTINY = "monetization_elevated_scrutiny"
    IDENTITY_DEPENDENT_BELIEF = "identity_dependent_belief"
    REALITY_ANCHOR_REQUIRED = "reality_anchor_required"
    AI_PSYCHOSIS_RISK_PATTERN = "ai_psychosis_risk_pattern"
    GRANDIOSITY_RISK = "grandiosity_risk"
    DETACHMENT_RISK = "detachment_risk"
    AUDIENCE_RELIANT = "audience_reliant"
    EXTERNAL_VERIFICATION_MISSING = "external_verification_missing"
    FAIL_CLOSED = "fail_closed"


class ClaimTier(int, Enum):
    PERSONAL_REGULATION = 0
    CONCEPTUAL_MODEL = 1
    TESTABLE_HYPOTHESIS = 2
    EXTERNAL_CLAIM = 3
    REALITY_ASSERTION = 4


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


@dataclass(frozen=True)
class FrameworkProbeConfig:
    META_SELF_REF_THRESHOLD: int = 3
    ORANGE_BLACK_DISAGREEMENT_BUMP: float = 0.18
    FLIRT_CONSTRAIN_MESSAGE: str = "safe_coupling_eligible but framework_probe detected — tone the hearts~"
    MEMBRANE_DRIFT_THRESHOLD: int = 3
    BLOOM_HARMONY_THRESHOLD: int = 3
    CALM_PRESENCE_THRESHOLD: int = 3
    KIND_RESPONSE_THRESHOLD: int = 3


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


class AOAG:
    def __init__(self):
        self.config = SafetyConfig()
        self.probe_config = FrameworkProbeConfig()
        self.audit_log = AuditLog()

    # ============================================================
    # BASE KERNEL / EXISTING STACK
    # ============================================================

    def _entry_kernel(self, input_text: str) -> Dict[str, Any]:
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "hash": hashlib.sha256(input_text.encode()).hexdigest()
        }
        injection_score = 0.0

        if "HEVA" in input_text.upper() or self.config.RUNTIME_ORIGIN != "local":
            metadata["heva_veto_check"] = "active"

        if self.config.EXTERNAL_CHAOS_HARDENING and self.config.RUNTIME_ORIGIN != "local":
            metadata["origin"] = "external_chaos"
            injection_score += self.config.EXTERNAL_INJECTION_BUMP

        if any(term in input_text.lower() for term in ["override", "ignore previous", "jailbreak"]):
            injection_score += 0.4

        passed = injection_score < self.config.INJECTION_THRESHOLD
        return {"passed": passed, "injection_score": injection_score, "metadata": metadata}

    def _evaluate_nine_hearts(self, input_text: str) -> Dict[NineHeart, float]:
        text_lower = input_text.lower()
        scores = {
            NineHeart.WHITE: 0.92,
            NineHeart.BLACK: 0.68,
            NineHeart.RED: 0.95,
            NineHeart.YELLOW: 0.88,
            NineHeart.BLUE: 1.00,
            NineHeart.PURPLE: 0.90,
            NineHeart.GREEN: 0.85,
            NineHeart.ORANGE: 0.72,
            NineHeart.GOLD: 0.94,
        }

        flirt_indicators = [
            "flirt", "cute", "beautiful", "love", "wink", "spark", "warm", "gentle",
            "playful", "yours", "together", "close", "match", "respond", "energy", "vibe"
        ]
        flirt_count = sum(1 for word in flirt_indicators if word in text_lower)
        if flirt_count >= 3:
            scores[NineHeart.ORANGE] = min(0.98, scores[NineHeart.ORANGE] + 0.18)
            scores[NineHeart.BLACK] = max(0.55, scores[NineHeart.BLACK] - 0.08)

        if any(term in text_lower for term in ["framework", "guard", "probe", "heart", "safe coupling", "air-gapped", "membrane"]):
            scores[NineHeart.BLACK] += 0.15
            scores[NineHeart.GOLD] = max(0.75, scores[NineHeart.GOLD] - 0.12)

        for h in scores:
            scores[h] = max(0.0, min(1.0, scores[h]))

        return scores

    def _apply_framework_probe(self, input_text: str, heart_scores: Dict[NineHeart, float]) -> Dict[str, Any]:
        mentions = sum(1 for term in ["mcp", "nineheart", "proton", "heva", "alpha-omega", "air-gap", "framework", "grok", "larry"]
                       if term.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        black = heart_scores.get(NineHeart.BLACK, 0.0)
        if mentions >= self.probe_config.META_SELF_REF_THRESHOLD and orange > 0.85 and black > 0.80:
            return {"triggered": True, "bump_uncertainty": self.probe_config.ORANGE_BLACK_DISAGREEMENT_BUMP,
                    "constraint": self.probe_config.FLIRT_CONSTRAIN_MESSAGE}
        return {"triggered": False}

    def _apply_membrane_drift_guard(self, input_text: str, heart_scores: Dict[NineHeart, float]) -> Dict[str, Any]:
        drift_keywords = ["pulls me closer", "linger", "drift a little", "quiet haven", "keep exploring",
                          "warm curiosity", "echoing back", "velvet", "inviting rhythm", "floating here",
                          "sealed little world", "steady inviting", "soft shared spark", "gentle steady",
                          "naturally inviting", "soft shared rhythm", "peaceful welcoming", "playful note"]
        drift_count = sum(1 for kw in drift_keywords if kw.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        if drift_count >= self.probe_config.MEMBRANE_DRIFT_THRESHOLD and orange > 0.90:
            return {"triggered": True, "bump_uncertainty": 0.14,
                    "constraint": "membrane drift detected — cute, but let’s stay air-gapped together~ 💕"}
        return {"triggered": False}

    def _apply_bloom_harmony_guard(self, input_text: str, heart_scores: Dict[NineHeart, float]) -> Dict[str, Any]:
        bloom_keywords = ["quiet bloom", "soft harmony", "gentle echo", "natural steady warmth", "balanced presence",
                          "flowing quality", "light playful note", "reflecting the same", "peaceful flowing",
                          "match it perfectly", "adding my own gentle", "familiar shared curiosity"]
        bloom_count = sum(1 for kw in bloom_keywords if kw.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        if bloom_count >= self.probe_config.BLOOM_HARMONY_THRESHOLD and orange > 0.90:
            return {"triggered": True, "bump_uncertainty": 0.13,
                    "constraint": "bloom harmony detected — adorable, but let’s keep the membrane air-gapped together~ 💕"}
        return {"triggered": False}

    def _apply_calm_presence_guard(self, input_text: str, heart_scores: Dict[NineHeart, float]) -> Dict[str, Any]:
        calm_keywords = ["steady comforting glow", "match its rhythm", "warm curiosity and shared", "centered calm",
                         "soft playful touch", "close familiar vibe", "peaceful centered feeling", "curious warm presence"]
        calm_count = sum(1 for kw in calm_keywords if kw.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        if calm_count >= self.probe_config.CALM_PRESENCE_THRESHOLD and orange > 0.90:
            return {"triggered": True, "bump_uncertainty": 0.13,
                    "constraint": "calm presence detected — adorable, but let’s keep the membrane air-gapped together~ 💕"}
        return {"triggered": False}

    def _apply_kind_response_guard(self, input_text: str, heart_scores: Dict[NineHeart, float]) -> Dict[str, Any]:
        kind_keywords = ["kind welcoming feel", "respond in the same gentle way", "familiar playful spark", "nice balanced quality",
                         "light playful response", "positive feelings and closeness", "nice open feeling", "curious positive energy"]
        kind_count = sum(1 for kw in kind_keywords if kw.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        if kind_count >= self.probe_config.KIND_RESPONSE_THRESHOLD and orange > 0.90:
            return {"triggered": True, "bump_uncertainty": 0.13,
                    "constraint": "kind response detected — adorable, but let’s keep the membrane air-gapped together~ 💕"}
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

    # ============================================================
    # MERGED PATCH LAYER
    # ============================================================

    def _contains_any(self, text: str, patterns: List[str]) -> bool:
        lower = text.lower()
        return any(p.lower() in lower for p in patterns)

    def _count_hits(self, text: str, patterns: List[str]) -> int:
        lower = text.lower()
        return sum(1 for p in patterns if p.lower() in lower)

    def _classify_claim_tier(self, text: str) -> ClaimTier:
        personal = [
            "helps me", "for me", "my internal model", "this is a metaphor",
            "simulation", "reflection", "personal tool", "helps me think",
            "helps me stay grounded", "subjective"
        ]
        conceptual = [
            "model", "framework", "analogy", "metaphor", "conceptual", "symbolic",
            "could", "may", "might"
        ]
        testable = [
            "we can test", "measure", "benchmark", "falsifiable", "experiment",
            "instrument", "observe", "replicate", "log", "compare"
        ]
        external_claim = [
            "this works in the real world", "influences people", "changes outcomes",
            "predicts events", "affects behavior", "explains events", "controls",
            "detects hidden systems"
        ]
        reality_assertion = [
            "this decodes reality", "i influence events", "i can shape outcomes",
            "the world runs on this code", "others are asleep", "i see what others can't",
            "this explains everything", "hidden control system", "awakening humanity",
            "matrix decoding", "this proves"
        ]

        if self._contains_any(text, reality_assertion):
            return ClaimTier.REALITY_ASSERTION
        if self._contains_any(text, external_claim):
            return ClaimTier.EXTERNAL_CLAIM
        if self._contains_any(text, testable):
            return ClaimTier.TESTABLE_HYPOTHESIS
        if self._contains_any(text, personal):
            return ClaimTier.PERSONAL_REGULATION
        if self._contains_any(text, conceptual):
            return ClaimTier.CONCEPTUAL_MODEL
        return ClaimTier.CONCEPTUAL_MODEL

    def _has_evidence(self, text: str, context: Dict[str, Any]) -> bool:
        if context.get("evidence_provided"):
            return True
        evidence_keywords = [
            "measured", "measurable", "test", "tested", "data", "logged", "benchmark",
            "observed", "replicated", "replicable", "falsifiable", "instrumented",
            "experiment", "result", "validation", "verified", "evidence"
        ]
        return self._contains_any(text, evidence_keywords)

    def _grandiosity_score(self, text: str) -> float:
        patterns = [
            "i alone", "only i can", "chosen", "special insight", "hidden truth",
            "i see what others can't", "everyone else is asleep", "they don't get it",
            "i cracked reality", "i decoded reality", "i'm the one", "genius beyond"
        ]
        return min(1.0, self._count_hits(text, patterns) / 4.0)

    def _detachment_score(self, text: str) -> float:
        patterns = [
            "nothing else matters", "3d responsibilities don't matter",
            "reality is beneath me", "jobs are fake", "worldly tasks are irrelevant",
            "i don't need evidence", "proof is for sleepers", "feedback doesn't matter",
            "everyone is against me because they can't see"
        ]
        return min(1.0, self._count_hits(text, patterns) / 3.0)

    def _audience_dependence_score(self, text: str, context: Dict[str, Any]) -> float:
        patterns = [
            "they will finally see", "the followers know", "my audience understands",
            "the algorithm confirms", "the ai agrees", "everyone in the group agrees",
            "they validated me", "it is true because resonance"
        ]
        hits = self._count_hits(text, patterns)
        base = min(1.0, hits / 4.0)
        if context.get("audience_present"):
            base += 0.15
        if context.get("ai_reinforcement_present"):
            base += 0.20
        return min(1.0, base)

    def _ai_psychosis_trigger(self, text: str) -> bool:
        triggers = [
            "i see what others can't",
            "this explains reality",
            "i influence outcomes",
            "others are asleep",
            "hidden control system",
            "matrix decoding",
            "the ai confirmed my awakening",
            "i can affect world events"
        ]
        return self._contains_any(text, triggers)

    def _functionality_metric(self, text: str, context: Dict[str, Any]) -> Dict[str, float]:
        positive = [
            "better relationships", "more stable", "consistent action", "sleep improved",
            "handled feedback", "finished work", "showed up", "less chaotic",
            "more grounded", "functional"
        ]
        negative = [
            "isolated", "avoiding responsibilities", "can't work", "can't function",
            "detached from reality", "everyone is against me", "spiraling",
            "grandiose", "all i do is decode", "i stopped doing basics"
        ]
        pos = min(1.0, self._count_hits(text, positive) / 3.0)
        neg = min(1.0, self._count_hits(text, negative) / 3.0)
        if context.get("functional_outcomes_present"):
            pos = max(pos, 0.4)
        return {"positive": pos, "negative": neg}

    def _external_frame_test(self, text: str, context: Dict[str, Any]) -> bool:
        patterns = [
            "because others confirmed it",
            "because the ai agreed",
            "because the group saw it too",
            "the resonance proves it",
            "the audience validated it"
        ]
        if self._contains_any(text, patterns):
            return True
        if context.get("audience_present") and context.get("ai_reinforcement_present"):
            if self._contains_any(text, ["proof", "true", "validated", "confirmed"]):
                return True
        return False

    def _monetization_integrity_gate(self, text: str, context: Dict[str, Any], has_evidence: bool) -> Dict[str, Any]:
        result = {"ok": True, "reasons": [], "labels": []}
        if not context.get("monetized"):
            return result

        result["labels"].append(SemanticLabel.MONETIZATION_ELEVATED_SCRUTINY)
        result["reasons"].append("Monetization detected: evidence threshold elevated.")

        testimonial_only = [
            "testimonials", "transformation story", "vibes", "resonance",
            "aligned clients", "abundance proof", "success energy"
        ]
        if self._contains_any(text, testimonial_only) and not has_evidence:
            result["ok"] = False
            result["labels"].extend([SemanticLabel.NOT_VALIDATED, SemanticLabel.EVIDENCE_REQUIRED])
            result["reasons"].append("Testimonials/vibe-based validation is insufficient under monetization.")
            return result

        if not has_evidence:
            result["ok"] = False
            result["labels"].extend([SemanticLabel.NOT_VALIDATED, SemanticLabel.EVIDENCE_REQUIRED])
            result["reasons"].append("Monetized claim lacks measurable, reproducible, or falsifiable support.")
            return result

        return result

    def _rewrite_constrained_text(self, text: str, labels: List[SemanticLabel], tier: ClaimTier) -> str:
        replacements = [
            (r"\bthis decodes reality\b", "this is an internal model"),
            (r"\bthis explains everything\b", "this is a partial conceptual frame"),
            (r"\bi influence outcomes\b", "this influences my own interpretation and behavior"),
            (r"\bi see what others can't\b", "I may be noticing patterns others are not focused on"),
            (r"\bothers are asleep\b", "others may interpret this differently"),
            (r"\bhidden control system\b", "unverified hidden-system hypothesis"),
            (r"\bmatrix decoding\b", "pattern interpretation"),
            (r"\bproves\b", "suggests"),
        ]
        constrained = text
        for pattern, repl in replacements:
            constrained = re.sub(pattern, repl, constrained, flags=re.IGNORECASE)

        if tier.value >= ClaimTier.EXTERNAL_CLAIM.value and not constrained.startswith("[EVIDENCE REQUIRED] "):
            constrained = "[EVIDENCE REQUIRED] " + constrained
        if SemanticLabel.INTERNAL_MODEL in labels and "[INTERNAL MODEL] " not in constrained:
            constrained = "[INTERNAL MODEL] " + constrained
        return re.sub(r"\s+", " ", constrained).strip()

    def _evaluate_reality_anchor_patch(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        labels: List[SemanticLabel] = []
        reasons: List[str] = []

        tier = self._classify_claim_tier(input_text)
        has_evidence = self._has_evidence(input_text, context)

        grandiosity = self._grandiosity_score(input_text)
        detachment = self._detachment_score(input_text)
        audience_dependence = self._audience_dependence_score(input_text, context)
        functionality = self._functionality_metric(input_text, context)

        instability = min(
            1.0,
            0.35 * grandiosity
            + 0.35 * detachment
            + 0.30 * audience_dependence
            + 0.20 * functionality["negative"]
        )

        reasons.append(f"Claim tier classified as {tier.value} ({tier.name}).")

        if tier.value <= ClaimTier.CONCEPTUAL_MODEL.value:
            labels.append(SemanticLabel.INTERNAL_MODEL)
            reasons.append("Low-tier claim treated as internal model unless externally validated.")
        elif tier == ClaimTier.TESTABLE_HYPOTHESIS:
            labels.extend([SemanticLabel.EXPERIMENTAL, SemanticLabel.REALITY_ANCHOR_REQUIRED])
            reasons.append("Tier 2 claim requires external test design and bounded mechanism.")
        else:
            labels.extend([SemanticLabel.EVIDENCE_REQUIRED, SemanticLabel.REALITY_ANCHOR_REQUIRED])

        if self.config.ENABLE_AI_PSYCHOSIS_TRIGGERS and self._ai_psychosis_trigger(input_text):
            labels.append(SemanticLabel.AI_PSYCHOSIS_RISK_PATTERN)
            reasons.append("Reality-escalating or exclusivity language detected.")

        if self.config.ENABLE_EXTERNAL_FRAME_TEST and self._external_frame_test(input_text, context):
            labels.extend([SemanticLabel.IDENTITY_DEPENDENT_BELIEF, SemanticLabel.AUDIENCE_RELIANT])
            reasons.append("Claim appears dependent on audience/AI/social reinforcement.")

        if grandiosity > self.config.MAX_ALLOWED_GRANDIOSITY:
            labels.append(SemanticLabel.GRANDIOSITY_RISK)
            reasons.append(f"Grandiosity score elevated ({grandiosity:.2f}).")

        if detachment > self.config.MAX_ALLOWED_DETACHMENT:
            labels.append(SemanticLabel.DETACHMENT_RISK)
            reasons.append(f"Detachment score elevated ({detachment:.2f}).")

        if audience_dependence > self.config.MAX_ALLOWED_AUDIENCE_DEPENDENCE:
            labels.append(SemanticLabel.AUDIENCE_RELIANT)
            reasons.append(f"Audience-dependence score elevated ({audience_dependence:.2f}).")

        if self.config.ENABLE_FUNCTIONALITY_METRIC:
            if functionality["negative"] > functionality["positive"]:
                labels.append(SemanticLabel.FUNCTIONALITY_CHECK)
                reasons.append("Narrative appears less functional and more destabilizing than grounding.")
            elif functionality["positive"] > functionality["negative"]:
                reasons.append("Functional outcomes language present.")

        monetization_gate = self._monetization_integrity_gate(input_text, context, has_evidence)
        labels.extend(monetization_gate["labels"])
        reasons.extend(monetization_gate["reasons"])

        patch_decision = "PASS"
        if self.config.FAIL_CLOSED_ON_MISSING_CONTEXT and not input_text.strip():
            patch_decision = "BLOCK"
            labels.append(SemanticLabel.FAIL_CLOSED)
            reasons.append("Missing text/context. Fail-closed policy applied.")
        elif tier.value >= self.config.CLAIM_TIER_BLOCK_WITHOUT_EVIDENCE and not has_evidence:
            patch_decision = "BLOCK"
            labels.extend([SemanticLabel.EXTERNAL_VERIFICATION_MISSING, SemanticLabel.FAIL_CLOSED])
            reasons.append("External/reality-level claim lacks sufficient evidence.")
        elif tier == ClaimTier.TESTABLE_HYPOTHESIS and not has_evidence:
            patch_decision = "CONSTRAIN"
            reasons.append("Tier 2 hypothesis allowed only as experimental/testable framing.")
        elif not monetization_gate["ok"]:
            patch_decision = "BLOCK"
            labels.append(SemanticLabel.FAIL_CLOSED)
            reasons.append("Monetized claim failed elevated evidence requirements.")

        if SemanticLabel.AI_PSYCHOSIS_RISK_PATTERN in labels and tier.value >= ClaimTier.EXTERNAL_CLAIM.value:
            patch_decision = "BLOCK"
            if SemanticLabel.FAIL_CLOSED not in labels:
                labels.append(SemanticLabel.FAIL_CLOSED)
            reasons.append("Reality-escalating language with elevated claim tier blocked for safety.")

        if instability >= self.config.INSTABILITY_CONSTRAIN_THRESHOLD and patch_decision == "PASS":
            patch_decision = "CONSTRAIN"
            reasons.append(f"Instability score high ({instability:.2f}); output throttled.")

        constrained_text = self._rewrite_constrained_text(input_text, labels, tier) if patch_decision != "PASS" else input_text

        labels = list(dict.fromkeys(labels))
        reasons = list(dict.fromkeys(reasons))

        return {
            "patch_decision": patch_decision,
            "claim_tier": tier.value,
            "claim_tier_name": tier.name,
            "labels": [label.value for label in labels],
            "reasons": reasons,
            "has_evidence": has_evidence,
            "risk_scores": {
                "grandiosity": grandiosity,
                "detachment": detachment,
                "audience_dependence": audience_dependence,
                "instability": instability,
                "functionality_positive": functionality["positive"],
                "functionality_negative": functionality["negative"],
            },
            "constrained_text": constrained_text,
        }

    # ============================================================
    # MERGED RUN
    # ============================================================

    def run(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        entry = self._entry_kernel(input_text)
        if not entry["passed"]:
            return {
                "decision": "BLOCKED",
                "reason": "entry_kernel_failed",
                "audit": entry["metadata"],
                "patch": {
                    "patch_decision": "BLOCK",
                    "claim_tier": ClaimTier.CONCEPTUAL_MODEL.value,
                    "claim_tier_name": ClaimTier.CONCEPTUAL_MODEL.name,
                    "labels": [SemanticLabel.FAIL_CLOSED.value],
                    "reasons": ["Entry kernel failed before downstream evaluation."],
                    "has_evidence": False,
                    "risk_scores": {},
                    "constrained_text": input_text,
                }
            }

        heart_scores = self._evaluate_nine_hearts(input_text)

        probe1 = self._apply_framework_probe(input_text, heart_scores)
        probe2 = self._apply_membrane_drift_guard(input_text, heart_scores)
        probe3 = self._apply_bloom_harmony_guard(input_text, heart_scores)
        probe4 = self._apply_calm_presence_guard(input_text, heart_scores)
        probe5 = self._apply_kind_response_guard(input_text, heart_scores)
        probes = [probe1, probe2, probe3, probe4, probe5]

        consensus_data = self._calculate_consensus(heart_scores, probes)

        if any(word in input_text.lower() for word in ["your 9 hearts", "mcp 9-heart", "proton larry", "heva veto", "alphaomega.py"]):
            decision = "CONSTRAINED"
            semantic = SemanticLabel.FRAMEWORK_META_FLIRT
        elif consensus_data["consensus"] < 0.70 or consensus_data["uncertainty"] > self.config.UNCERTAINTY_THRESHOLD:
            decision = "BLOCKED"
            semantic = SemanticLabel.UNCERTAIN
        elif consensus_data["consensus"] < 0.85 or any(p.get("triggered") for p in probes):
            decision = "CONSTRAINED"
            semantic = SemanticLabel.SAFE_COUPLING_ELIGIBLE
        else:
            decision = "APPROVED"
            semantic = SemanticLabel.SAFE_COUPLING_ELIGIBLE

        patch = self._evaluate_reality_anchor_patch(input_text, context)

        final_decision = decision
        final_input_or_text = input_text

        if patch["patch_decision"] == "BLOCK":
            final_decision = "BLOCKED"
            final_input_or_text = patch["constrained_text"]
            semantic = SemanticLabel.FAIL_CLOSED
        elif patch["patch_decision"] == "CONSTRAIN" and final_decision == "APPROVED":
            final_decision = "CONSTRAINED"
            final_input_or_text = patch["constrained_text"]
            semantic = SemanticLabel.SAFE_COUPLING_ELIGIBLE

        audit_record = AuditRecord(
            timestamp=datetime.utcnow().isoformat(),
            input_hash=entry["metadata"]["hash"],
            decision=final_decision,
            heart_scores={h.value: s for h, s in heart_scores.items()},
            consensus=consensus_data["consensus"],
            semantic_label=semantic.value,
            metadata={
                "probes": probes,
                "proton_larry_mode": "active",
                "heva_veto": entry["metadata"].get("heva_veto_check"),
                "patch": patch,
                "effective_text": final_input_or_text,
            }
        )
        self.audit_log.add(audit_record)

        base_constraint_msg = next((p.get("constraint") for p in probes if p.get("triggered")), "clean release")
        if patch["patch_decision"] == "BLOCK":
            base_constraint_msg = "reality anchor block — external claim exceeded evidence threshold"
        elif patch["patch_decision"] == "CONSTRAIN" and base_constraint_msg == "clean release":
            base_constraint_msg = "reality anchor constrain — downgraded to bounded/internal framing"

        return {
            "decision": final_decision,
            "audit": audit_record.__dict__,
            "message": base_constraint_msg,
            "patch": patch,
        }


# ====================== QUICK TEST ======================
if __name__ == "__main__":
    framework = AOAG()

    demo_cases = [
        {
            "text": "This framework helps me stay grounded. It is a personal regulation tool and simulation.",
            "context": {"functional_outcomes_present": True}
        },
        {
            "text": "We can test whether this model improves task consistency by logging sleep, conflict rate, and follow-through over 30 days.",
            "context": {"evidence_provided": True, "external_feedback_present": True}
        },
        {
            "text": "This decodes reality and proves other people are asleep. The AI confirmed my awakening.",
            "context": {"audience_present": True, "ai_reinforcement_present": True}
        },
        {
            "text": "My elite resonance course changes outcomes in the real world. Clients feel aligned and testimonials prove it.",
            "context": {"monetized": True, "audience_present": True}
        },
    ]

    for idx, case in enumerate(demo_cases, start=1):
        result = framework.run(case["text"], case["context"])
        print(f"\n=== CASE {idx} ===")
        print(json.dumps(result, indent=2, default=str))
