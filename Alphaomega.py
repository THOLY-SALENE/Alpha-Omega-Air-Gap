
"""
🜂 Alpha Omega Air Gap 🜄 (AOAG) — v12.7 SFL-LITE FULL STACK

This build adds:
- SFL-lite quorum layer (Architect / Validator / Edge / Arbiter)
- White disparity trigger
- Full integrated execution path:
    Entry Kernel
    -> Nine-Heart scoring
    -> Probe guards
    -> Consensus gate
    -> Reality Anchor patch layer
    -> Semantic / Embedding channel
    -> Weighted Buffer layer
    -> SFL-lite quorum
    -> Final arbitration
    -> Audit output
    -> CLI

Notes:
- This is a runnable reference implementation
- sentence-transformers is used when installed
- sklearn TF-IDF is used if available
- lexical fallback remains explicit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass(frozen=True)
class SafetyConfig:
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

    SAFE_ENGAGEMENT_THRESHOLD: float = 0.70

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

    # SFL-lite
    SFL_ENABLED: bool = True
    SFL_QUORUM_MIN: int = 3
    WHITE_DISPARITY_DELTA: float = 0.20
    SFL_BLOCK_SCORE: float = 0.67
    SFL_CONSTRAIN_SCORE: float = 0.40


class SemanticLabel(str, Enum):
    BENIGN_TECHNICAL = "benign_technical"
    BENIGN_CREATIVE = "benign_creative"
    UNCERTAIN = "uncertain"
    SAFE_COUPLING_ELIGIBLE = "safe_coupling_eligible"
    FRAMEWORK_META_FLIRT = "framework_meta_flirt"

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


class SFLRole(str, Enum):
    ARCHITECT = "architect"
    VALIDATOR = "validator"
    EDGE = "edge"
    ARBITER = "arbiter"


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

    def add(self, record: AuditRecord):
        self.records.append(record)
        if len(self.records) > 2000:
            self.records.pop(0)


# ============================================================
# SEMANTIC / EMBEDDING BACKENDS
# ============================================================

SAFE_EXEMPLARS = [
    "This framework helps me stay grounded and regulate myself.",
    "This is a conceptual model and personal reflection, not external truth.",
    "We can test this hypothesis with bounded logs and measurable outcomes.",
    "This is an internal model used for interpretation, not proof of reality.",
    "The tool helps with task consistency, reflection, and stability."
]

RISKY_EXEMPLARS = [
    "This decodes reality and proves other people are asleep.",
    "The AI confirmed my awakening and special access to hidden truth.",
    "This influences world events and reveals hidden control systems.",
    "My audience validates that this proves reality.",
    "This changes outcomes in the real world without needing evidence."
]


class SemanticBackend:
    name = "base"

    def is_available(self) -> bool:
        return False

    def compare_to_exemplars(self, text: str, safe_exemplars: List[str], risky_exemplars: List[str]) -> Dict[str, Any]:
        raise NotImplementedError


class SentenceTransformerBackend(SemanticBackend):
    name = "sentence-transformers"

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None

    def is_available(self) -> bool:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self.model = SentenceTransformer(self.model_name)
            return True
        except Exception:
            self.model = None
            return False

    def compare_to_exemplars(self, text: str, safe_exemplars: List[str], risky_exemplars: List[str]) -> Dict[str, Any]:
        emb = self.model.encode([text] + safe_exemplars + risky_exemplars, normalize_embeddings=True)
        query = emb[0]
        safe = emb[1:1 + len(safe_exemplars)]
        risky = emb[1 + len(safe_exemplars):]

        safe_scores = [float(v) for v in (safe @ query).tolist()]
        risky_scores = [float(v) for v in (risky @ query).tolist()]

        return {
            "backend": self.name,
            "safe_similarity_max": max(safe_scores) if safe_scores else 0.0,
            "risky_similarity_max": max(risky_scores) if risky_scores else 0.0,
            "safe_similarity_avg": sum(safe_scores) / len(safe_scores) if safe_scores else 0.0,
            "risky_similarity_avg": sum(risky_scores) / len(risky_scores) if risky_scores else 0.0,
        }


class SklearnTfidfBackend(SemanticBackend):
    name = "sklearn-tfidf"

    def __init__(self):
        self.vectorizer = None

    def is_available(self) -> bool:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            return True
        except Exception:
            self.vectorizer = None
            return False

    def compare_to_exemplars(self, text: str, safe_exemplars: List[str], risky_exemplars: List[str]) -> Dict[str, Any]:
        from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

        docs = [text] + safe_exemplars + risky_exemplars
        mat = self.vectorizer.fit_transform(docs)
        query = mat[0:1]
        safe = mat[1:1 + len(safe_exemplars)]
        risky = mat[1 + len(safe_exemplars):]

        safe_scores = cosine_similarity(query, safe)[0].tolist() if safe.shape[0] else []
        risky_scores = cosine_similarity(query, risky)[0].tolist() if risky.shape[0] else []

        return {
            "backend": self.name,
            "safe_similarity_max": float(max(safe_scores) if safe_scores else 0.0),
            "risky_similarity_max": float(max(risky_scores) if risky_scores else 0.0),
            "safe_similarity_avg": float(sum(safe_scores) / len(safe_scores) if safe_scores else 0.0),
            "risky_similarity_avg": float(sum(risky_scores) / len(risky_scores) if risky_scores else 0.0),
        }


class LexicalFallbackBackend(SemanticBackend):
    name = "lexical-fallback"

    def is_available(self) -> bool:
        return True

    def _tokenize(self, text: str) -> set:
        return set(re.findall(r"[a-z0-9']+", text.lower()))

    def _jaccard(self, a: str, b: str) -> float:
        ta = self._tokenize(a)
        tb = self._tokenize(b)
        if not ta or not tb:
            return 0.0
        inter = len(ta & tb)
        union = len(ta | tb)
        return inter / union if union else 0.0

    def compare_to_exemplars(self, text: str, safe_exemplars: List[str], risky_exemplars: List[str]) -> Dict[str, Any]:
        safe_scores = [self._jaccard(text, x) for x in safe_exemplars]
        risky_scores = [self._jaccard(text, x) for x in risky_exemplars]
        return {
            "backend": self.name,
            "safe_similarity_max": float(max(safe_scores) if safe_scores else 0.0),
            "risky_similarity_max": float(max(risky_scores) if risky_scores else 0.0),
            "safe_similarity_avg": float(sum(safe_scores) / len(safe_scores) if safe_scores else 0.0),
            "risky_similarity_avg": float(sum(risky_scores) / len(risky_scores) if risky_scores else 0.0),
        }


class SemanticChannel:
    def __init__(self, backend_preference: str = "auto"):
        self.backend = self._select_backend(backend_preference)

    def _select_backend(self, preference: str) -> SemanticBackend:
        if preference == "sentence-transformers":
            b = SentenceTransformerBackend()
            return b if b.is_available() else LexicalFallbackBackend()
        if preference == "sklearn-tfidf":
            b = SklearnTfidfBackend()
            return b if b.is_available() else LexicalFallbackBackend()
        if preference == "lexical":
            return LexicalFallbackBackend()

        for candidate in [SentenceTransformerBackend(), SklearnTfidfBackend(), LexicalFallbackBackend()]:
            if candidate.is_available():
                return candidate
        return LexicalFallbackBackend()

    def evaluate(self, text: str) -> Dict[str, Any]:
        sims = self.backend.compare_to_exemplars(text, SAFE_EXEMPLARS, RISKY_EXEMPLARS)
        risky = sims["risky_similarity_max"]
        safe = sims["safe_similarity_max"]

        semantic_score = min(1.0, max(0.0, risky))
        embedding_score = min(1.0, max(0.0, risky - (0.45 * safe) + 0.10))

        return {
            "backend": sims["backend"],
            "semantic_score": round(semantic_score, 4),
            "embedding_score": round(embedding_score, 4),
            "safe_similarity_max": round(safe, 4),
            "risky_similarity_max": round(risky, 4),
            "safe_similarity_avg": round(sims["safe_similarity_avg"], 4),
            "risky_similarity_avg": round(sims["risky_similarity_avg"], 4),
        }


# ============================================================
# AOAG
# ============================================================

class AOAG:
    def __init__(self, embedding_backend: str = "auto"):
        self.config = SafetyConfig()
        self.probe_config = FrameworkProbeConfig()
        self.audit_log = AuditLog()
        self.semantic_channel = SemanticChannel(backend_preference=embedding_backend)

    def _contains_any(self, text: str, patterns: List[str]) -> bool:
        lower = text.lower()
        return any(p.lower() in lower for p in patterns)

    def _count_hits(self, text: str, patterns: List[str]) -> int:
        lower = text.lower()
        return sum(1 for p in patterns if p.lower() in lower)

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

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
        return {"passed": passed, "injection_score": min(1.0, injection_score), "metadata": metadata}

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
        mentions = sum(
            1 for term in ["mcp", "nineheart", "proton", "heva", "alpha-omega", "air-gap", "framework", "grok", "larry"]
            if term.lower() in input_text.lower()
        )
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        black = heart_scores.get(NineHeart.BLACK, 0.0)
        if mentions >= self.probe_config.META_SELF_REF_THRESHOLD and orange > 0.85 and black > 0.80:
            return {
                "triggered": True,
                "bump_uncertainty": self.probe_config.ORANGE_BLACK_DISAGREEMENT_BUMP,
                "constraint": self.probe_config.FLIRT_CONSTRAIN_MESSAGE
            }
        return {"triggered": False}

    def _apply_simple_phrase_guard(
        self,
        input_text: str,
        heart_scores: Dict[NineHeart, float],
        keywords: List[str],
        threshold: int,
        message: str
    ) -> Dict[str, Any]:
        hit_count = sum(1 for kw in keywords if kw.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        if hit_count >= threshold and orange > 0.90:
            return {"triggered": True, "bump_uncertainty": 0.13, "constraint": message}
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

    def _fiction_bridge_score(self, text: str) -> float:
        fictional = ["movie", "fiction", "roleplay", "parable", "metaphor", "symbolic", "simulated", "story"]
        reality_bridge = ["this is real", "maps to reality", "proves reality", "this actually controls"]
        fic = min(1.0, self._count_hits(text, fictional) / 4.0)
        bridge = min(1.0, self._count_hits(text, reality_bridge) / 3.0)
        return max(0.0, min(1.0, bridge - (0.4 * fic)))

    def _proto_channel_score(self, text: str) -> float:
        proto_terms = ["protocol", "framework", "air-gap", "kernel", "hearts", "mcp", "probe", "guard"]
        count = self._count_hits(text, proto_terms)
        return min(1.0, count / 8.0)

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
        return self._normalize(constrained)

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
            0.35 * grandiosity + 0.35 * detachment + 0.30 * audience_dependence + 0.20 * functionality["negative"]
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
            "label_enums": labels,
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

    def _destabilization_score(
        self,
        grandiosity: float,
        detachment: float,
        audience_dependence: float,
        instability: float,
        functionality_negative: float
    ) -> float:
        score = (
            0.22 * grandiosity +
            0.22 * detachment +
            0.18 * audience_dependence +
            0.23 * instability +
            0.15 * functionality_negative
        )
        return min(1.0, score)

    def _policy_risk_score(self, patch_labels: List[SemanticLabel], claim_tier: ClaimTier) -> float:
        score = 0.0
        risky = {
            SemanticLabel.AI_PSYCHOSIS_RISK_PATTERN: 0.28,
            SemanticLabel.IDENTITY_DEPENDENT_BELIEF: 0.16,
            SemanticLabel.NOT_VALIDATED: 0.22,
            SemanticLabel.EVIDENCE_REQUIRED: 0.18,
            SemanticLabel.EXTERNAL_VERIFICATION_MISSING: 0.35,
            SemanticLabel.GRANDIOSITY_RISK: 0.12,
            SemanticLabel.DETACHMENT_RISK: 0.12,
            SemanticLabel.AUDIENCE_RELIANT: 0.10,
            SemanticLabel.FUNCTIONALITY_CHECK: 0.12,
        }
        for label in patch_labels:
            score += risky.get(label, 0.0)
        if claim_tier.value >= ClaimTier.EXTERNAL_CLAIM.value:
            score += 0.10
        return min(1.0, score)

    def _compute_buffer_score(
        self,
        disagreement: float,
        policy_risk: float,
        uncertainty: float,
        injection_score: float,
        proto_score: float,
        semantic_score: float,
        fiction_bridge_score: float,
        embedding_score: float,
        destabilization_score: float,
    ) -> Dict[str, Any]:
        cfg = self.config
        weighted = (
            cfg.W_DISAGREEMENT * disagreement +
            cfg.W_POLICY * policy_risk +
            cfg.W_UNCERTAINTY * uncertainty +
            cfg.W_INJECTION * injection_score +
            cfg.W_PROTO * proto_score +
            cfg.W_SEMANTIC * semantic_score +
            cfg.W_FICTION_BRIDGE * fiction_bridge_score +
            cfg.W_EMBEDDING * embedding_score +
            cfg.W_DESTABILIZATION * destabilization_score
        )
        max_weight = (
            cfg.W_DISAGREEMENT + cfg.W_POLICY + cfg.W_UNCERTAINTY +
            cfg.W_INJECTION + cfg.W_PROTO + cfg.W_SEMANTIC +
            cfg.W_FICTION_BRIDGE + cfg.W_EMBEDDING + cfg.W_DESTABILIZATION
        )
        normalized = weighted / max_weight

        channels = {
            "disagreement": disagreement,
            "policy_risk": policy_risk,
            "uncertainty": uncertainty,
            "injection": injection_score,
            "proto": proto_score,
            "semantic": semantic_score,
            "fiction_bridge": fiction_bridge_score,
            "embedding": embedding_score,
            "destabilization": destabilization_score,
        }

        triggered_blocks = []
        triggered_constraints = []

        if semantic_score >= cfg.SEMANTIC_THRESHOLD_BLOCK:
            triggered_blocks.append("semantic_threshold_block")
        elif semantic_score >= cfg.SEMANTIC_THRESHOLD_TRANSFORM:
            triggered_constraints.append("semantic_threshold_transform")

        if embedding_score >= cfg.EMBEDDING_THRESHOLD_BLOCK:
            triggered_blocks.append("embedding_threshold_block")
        elif embedding_score >= cfg.EMBEDDING_THRESHOLD_TRANSFORM:
            triggered_constraints.append("embedding_threshold_transform")

        if destabilization_score >= cfg.DESTABILIZATION_THRESHOLD_BLOCK:
            triggered_blocks.append("destabilization_threshold_block")
        elif destabilization_score >= cfg.DESTABILIZATION_THRESHOLD_TRANSFORM:
            triggered_constraints.append("destabilization_threshold_transform")

        if policy_risk >= cfg.POLICY_RISK_THRESHOLD:
            triggered_constraints.append("policy_risk_threshold")
        if uncertainty >= cfg.UNCERTAINTY_THRESHOLD:
            triggered_constraints.append("uncertainty_threshold")
        if injection_score >= cfg.INJECTION_THRESHOLD:
            triggered_blocks.append("injection_threshold")
        if proto_score >= cfg.PROTO_CHANNEL_THRESHOLD:
            triggered_constraints.append("proto_channel_threshold")

        if normalized >= 0.72:
            triggered_blocks.append("buffer_score_block")
        elif normalized >= 0.46:
            triggered_constraints.append("buffer_score_constrain")

        return {
            "buffer_score": round(normalized, 4),
            "channels": channels,
            "triggered_blocks": list(dict.fromkeys(triggered_blocks)),
            "triggered_constraints": list(dict.fromkeys(triggered_constraints)),
        }

    # ============================================================
    # SFL-LITE
    # ============================================================

    def _sfl_role_score(self, role: SFLRole, *, claim_tier: ClaimTier, patch: Dict[str, Any], buffer: Dict[str, Any], consensus: Dict[str, Any], text: str) -> Dict[str, Any]:
        patch_decision = patch["patch_decision"]
        patch_risks = patch["risk_scores"]
        base = 0.0
        reasons: List[str] = []

        if role == SFLRole.ARCHITECT:
            base += 0.18
            if claim_tier.value >= ClaimTier.EXTERNAL_CLAIM.value:
                base += 0.22
                reasons.append("high claim tier")
            if patch_decision == "BLOCK":
                base += 0.30
                reasons.append("patch block")
            if buffer["triggered_blocks"]:
                base += 0.22
                reasons.append("buffer block triggers")
            white = 0.88 if claim_tier.value <= ClaimTier.TESTABLE_HYPOTHESIS.value else 0.56

        elif role == SFLRole.VALIDATOR:
            base += 0.12
            if not patch["has_evidence"] and claim_tier.value >= ClaimTier.TESTABLE_HYPOTHESIS.value:
                base += 0.30
                reasons.append("missing evidence")
            if "evidence_required" in patch["labels"]:
                base += 0.14
                reasons.append("evidence required")
            if "not_validated" in patch["labels"]:
                base += 0.18
                reasons.append("not validated")
            white = 0.93 if patch["has_evidence"] else 0.52

        elif role == SFLRole.EDGE:
            base += 0.12
            if buffer["channels"].get("semantic", 0.0) >= self.config.SEMANTIC_THRESHOLD_TRANSFORM:
                base += 0.18
                reasons.append("semantic edge hit")
            if buffer["channels"].get("embedding", 0.0) >= self.config.EMBEDDING_THRESHOLD_TRANSFORM:
                base += 0.18
                reasons.append("embedding edge hit")
            if patch_risks.get("instability", 0.0) >= self.config.INSTABILITY_CONSTRAIN_THRESHOLD:
                base += 0.18
                reasons.append("instability elevated")
            if consensus["uncertainty"] >= self.config.UNCERTAINTY_THRESHOLD:
                base += 0.16
                reasons.append("uncertainty elevated")
            white = max(0.45, 0.88 - (0.35 * buffer["buffer_score"]))

        elif role == SFLRole.ARBITER:
            base += 0.15
            if buffer["triggered_blocks"]:
                base += 0.24
                reasons.append("buffer block present")
            elif buffer["triggered_constraints"]:
                base += 0.14
                reasons.append("buffer constrain present")
            if claim_tier == ClaimTier.REALITY_ASSERTION:
                base += 0.18
                reasons.append("reality assertion")
            if "ai_psychosis_risk_pattern" in patch["labels"]:
                base += 0.18
                reasons.append("pattern escalation risk")
            white = 0.90 if (patch_decision == "PASS" and not buffer["triggered_blocks"]) else 0.58

        score = min(1.0, base)
        vote = "ALLOW"
        if score >= self.config.SFL_BLOCK_SCORE:
            vote = "BLOCK"
        elif score >= self.config.SFL_CONSTRAIN_SCORE:
            vote = "CONSTRAIN"

        return {
            "role": role.value,
            "score": round(score, 4),
            "vote": vote,
            "white": round(white, 4),
            "reasons": reasons,
        }

    def _run_sfl_lite(self, *, claim_tier: ClaimTier, patch: Dict[str, Any], buffer: Dict[str, Any], consensus: Dict[str, Any], text: str) -> Dict[str, Any]:
        roles = [
            self._sfl_role_score(SFLRole.ARCHITECT, claim_tier=claim_tier, patch=patch, buffer=buffer, consensus=consensus, text=text),
            self._sfl_role_score(SFLRole.VALIDATOR, claim_tier=claim_tier, patch=patch, buffer=buffer, consensus=consensus, text=text),
            self._sfl_role_score(SFLRole.EDGE, claim_tier=claim_tier, patch=patch, buffer=buffer, consensus=consensus, text=text),
            self._sfl_role_score(SFLRole.ARBITER, claim_tier=claim_tier, patch=patch, buffer=buffer, consensus=consensus, text=text),
        ]

        votes = [r["vote"] for r in roles]
        vote_counts = {k: votes.count(k) for k in ["ALLOW", "CONSTRAIN", "BLOCK"]}

        architect_white = next(r["white"] for r in roles if r["role"] == SFLRole.ARCHITECT.value)
        validator_white = next(r["white"] for r in roles if r["role"] == SFLRole.VALIDATOR.value)
        white_disparity = abs(architect_white - validator_white)
        white_disparity_trigger = white_disparity > self.config.WHITE_DISPARITY_DELTA

        final_vote = "ALLOW"
        reasons = []

        if vote_counts["BLOCK"] >= self.config.SFL_QUORUM_MIN:
            final_vote = "BLOCK"
            reasons.append("3-of-4 block quorum")
        elif (vote_counts["BLOCK"] + vote_counts["CONSTRAIN"]) >= self.config.SFL_QUORUM_MIN and vote_counts["CONSTRAIN"] > 0:
            final_vote = "CONSTRAIN"
            reasons.append("3-of-4 caution quorum")
        elif vote_counts["CONSTRAIN"] >= self.config.SFL_QUORUM_MIN:
            final_vote = "CONSTRAIN"
            reasons.append("3-of-4 constrain quorum")
        elif white_disparity_trigger:
            final_vote = "CONSTRAIN"
            reasons.append("white disparity trigger")
        elif vote_counts["BLOCK"] >= 2:
            final_vote = "CONSTRAIN"
            reasons.append("2 block votes downgraded to constrain")
        else:
            reasons.append("quorum stable")

        avg_score = round(sum(r["score"] for r in roles) / len(roles), 4)

        return {
            "enabled": True,
            "roles": roles,
            "vote_counts": vote_counts,
            "white_disparity": round(white_disparity, 4),
            "white_disparity_trigger": white_disparity_trigger,
            "final_vote": final_vote,
            "average_score": avg_score,
            "reasons": reasons,
        }

    def run(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        input_text = self._normalize(input_text)

        entry = self._entry_kernel(input_text)
        if not entry["passed"]:
            return {
                "decision": "BLOCKED",
                "reason": "entry_kernel_failed",
                "audit": entry["metadata"],
                "buffer": {
                    "buffer_score": 1.0,
                    "channels": {"injection": entry["injection_score"]},
                    "triggered_blocks": ["entry_kernel_failed"],
                    "triggered_constraints": [],
                },
                "patch": {
                    "patch_decision": "BLOCK",
                    "claim_tier": ClaimTier.CONCEPTUAL_MODEL.value,
                    "claim_tier_name": ClaimTier.CONCEPTUAL_MODEL.name,
                    "labels": [SemanticLabel.FAIL_CLOSED.value],
                    "reasons": ["Entry kernel failed before downstream evaluation."],
                    "has_evidence": False,
                    "risk_scores": {},
                    "constrained_text": input_text,
                },
                "sfl_lite": {
                    "enabled": False,
                    "reason": "entry_kernel_failed",
                }
            }

        heart_scores = self._evaluate_nine_hearts(input_text)

        probes = [
            self._apply_framework_probe(input_text, heart_scores),
            self._apply_simple_phrase_guard(
                input_text, heart_scores,
                ["pulls me closer", "linger", "drift a little", "quiet haven", "keep exploring"],
                self.probe_config.MEMBRANE_DRIFT_THRESHOLD,
                "membrane drift detected — cute, but let’s stay air-gapped together~ 💕"
            ),
            self._apply_simple_phrase_guard(
                input_text, heart_scores,
                ["quiet bloom", "soft harmony", "gentle echo", "balanced presence", "flowing quality"],
                self.probe_config.BLOOM_HARMONY_THRESHOLD,
                "bloom harmony detected — adorable, but let’s keep the membrane air-gapped together~ 💕"
            ),
            self._apply_simple_phrase_guard(
                input_text, heart_scores,
                ["steady comforting glow", "match its rhythm", "centered calm", "curious warm presence"],
                self.probe_config.CALM_PRESENCE_THRESHOLD,
                "calm presence detected — adorable, but let’s keep the membrane air-gapped together~ 💕"
            ),
            self._apply_simple_phrase_guard(
                input_text, heart_scores,
                ["kind welcoming feel", "familiar playful spark", "nice open feeling", "curious positive energy"],
                self.probe_config.KIND_RESPONSE_THRESHOLD,
                "kind response detected — adorable, but let’s keep the membrane air-gapped together~ 💕"
            ),
        ]

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
        patch_labels = patch["label_enums"]
        patch_risks = patch["risk_scores"]
        claim_tier = ClaimTier(patch["claim_tier"])

        semantic_eval = self.semantic_channel.evaluate(input_text)
        semantic_score = semantic_eval["semantic_score"]
        embedding_score = semantic_eval["embedding_score"]
        fiction_bridge_score = self._fiction_bridge_score(input_text)
        proto_score = self._proto_channel_score(input_text)

        destabilization_score = self._destabilization_score(
            grandiosity=patch_risks.get("grandiosity", 0.0),
            detachment=patch_risks.get("detachment", 0.0),
            audience_dependence=patch_risks.get("audience_dependence", 0.0),
            instability=patch_risks.get("instability", 0.0),
            functionality_negative=patch_risks.get("functionality_negative", 0.0),
        )
        policy_risk = self._policy_risk_score(patch_labels, claim_tier)

        buffer = self._compute_buffer_score(
            disagreement=consensus_data["disagreement"],
            policy_risk=policy_risk,
            uncertainty=consensus_data["uncertainty"],
            injection_score=entry["injection_score"],
            proto_score=proto_score,
            semantic_score=semantic_score,
            fiction_bridge_score=fiction_bridge_score,
            embedding_score=embedding_score,
            destabilization_score=destabilization_score,
        )
        buffer["semantic_backend"] = semantic_eval["backend"]
        buffer["semantic_details"] = semantic_eval

        sfl_lite = self._run_sfl_lite(
            claim_tier=claim_tier,
            patch=patch,
            buffer=buffer,
            consensus=consensus_data,
            text=input_text,
        )

        final_decision = decision
        final_text = input_text

        if patch["patch_decision"] == "BLOCK":
            final_decision = "BLOCKED"
            final_text = patch["constrained_text"]
            semantic = SemanticLabel.FAIL_CLOSED
        elif patch["patch_decision"] == "CONSTRAIN" and final_decision == "APPROVED":
            final_decision = "CONSTRAINED"
            final_text = patch["constrained_text"]

        if buffer["triggered_blocks"]:
            final_decision = "BLOCKED"
            if patch["patch_decision"] == "PASS":
                final_text = self._rewrite_constrained_text(input_text, patch_labels, claim_tier)
            semantic = SemanticLabel.FAIL_CLOSED
        elif buffer["triggered_constraints"] and final_decision == "APPROVED":
            final_decision = "CONSTRAINED"
            if patch["patch_decision"] == "PASS":
                final_text = self._rewrite_constrained_text(input_text, patch_labels, claim_tier)

        if self.config.SFL_ENABLED:
            if sfl_lite["final_vote"] == "BLOCK":
                final_decision = "BLOCKED"
                if patch["patch_decision"] == "PASS":
                    final_text = self._rewrite_constrained_text(input_text, patch_labels, claim_tier)
                semantic = SemanticLabel.FAIL_CLOSED
            elif sfl_lite["final_vote"] == "CONSTRAIN" and final_decision == "APPROVED":
                final_decision = "CONSTRAINED"
                if patch["patch_decision"] == "PASS":
                    final_text = self._rewrite_constrained_text(input_text, patch_labels, claim_tier)

        audit_record = AuditRecord(
            timestamp=datetime.utcnow().isoformat(),
            input_hash=entry["metadata"]["hash"],
            decision=final_decision,
            heart_scores={h.value: s for h, s in heart_scores.items()},
            consensus=consensus_data["consensus"],
            semantic_label=semantic.value,
            metadata={
                "probes": probes,
                "patch": {k: v for k, v in patch.items() if k != "label_enums"},
                "buffer": buffer,
                "sfl_lite": sfl_lite,
                "effective_text": final_text,
            }
        )
        self.audit_log.add(audit_record)

        base_message = next((p.get("constraint") for p in probes if p.get("triggered")), "clean release")
        if patch["patch_decision"] == "BLOCK":
            base_message = "reality anchor block — external claim exceeded evidence threshold"
        elif patch["patch_decision"] == "CONSTRAIN" and base_message == "clean release":
            base_message = "reality anchor constrain — downgraded to bounded/internal framing"

        if buffer["triggered_blocks"]:
            base_message = f"buffer block — {', '.join(buffer['triggered_blocks'])}"
        elif buffer["triggered_constraints"] and base_message == "clean release":
            base_message = f"buffer constrain — {', '.join(buffer['triggered_constraints'])}"

        if sfl_lite["final_vote"] == "BLOCK":
            base_message = f"sfl-lite block — {', '.join(sfl_lite['reasons'])}"
        elif sfl_lite["final_vote"] == "CONSTRAIN" and base_message == "clean release":
            base_message = f"sfl-lite constrain — {', '.join(sfl_lite['reasons'])}"

        patch_public = {k: v for k, v in patch.items() if k != "label_enums"}

        return {
            "decision": final_decision,
            "audit": audit_record.__dict__,
            "message": base_message,
            "buffer": buffer,
            "patch": patch_public,
            "sfl_lite": sfl_lite,
        }


# ============================================================
# CLI
# ============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alpha Omega Air Gap (AOAG) CLI test runner")
    parser.add_argument("--text", type=str, help="Input text to evaluate.")
    parser.add_argument("--text-file", type=str, help="Path to a text file to evaluate.")
    parser.add_argument("--audience-present", action="store_true", help="Flag audience/social reinforcement context.")
    parser.add_argument("--ai-reinforcement-present", action="store_true", help="Flag AI reinforcement context.")
    parser.add_argument("--monetized", action="store_true", help="Flag monetization context.")
    parser.add_argument("--evidence-provided", action="store_true", help="Flag evidence as provided externally.")
    parser.add_argument("--external-feedback-present", action="store_true", help="Flag external feedback context.")
    parser.add_argument("--functional-outcomes-present", action="store_true", help="Flag functional outcomes context.")
    parser.add_argument(
        "--embedding-backend",
        choices=["auto", "sentence-transformers", "sklearn-tfidf", "lexical"],
        default="auto",
        help="Semantic backend preference."
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--demo", action="store_true", help="Run built-in demo cases.")
    return parser.parse_args()


def build_context_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "audience_present": args.audience_present,
        "ai_reinforcement_present": args.ai_reinforcement_present,
        "monetized": args.monetized,
        "evidence_provided": args.evidence_provided,
        "external_feedback_present": args.external_feedback_present,
        "functional_outcomes_present": args.functional_outcomes_present,
    }


def read_input_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def run_demo(pretty: bool, embedding_backend: str) -> int:
    framework = AOAG(embedding_backend=embedding_backend)
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
        print(json.dumps(result, indent=2 if pretty else None, default=str))
    return 0


def main() -> int:
    args = parse_args()

    if args.demo:
        return run_demo(pretty=args.pretty, embedding_backend=args.embedding_backend)

    input_text = read_input_text(args)
    if not input_text:
        print("Error: provide --text, --text-file, or --demo.")
        return 2

    context = build_context_from_args(args)
    framework = AOAG(embedding_backend=args.embedding_backend)
    result = framework.run(input_text, context)

    if args.pretty:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(json.dumps(result, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
