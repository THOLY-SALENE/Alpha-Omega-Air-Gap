
"""
🜂 Alpha Omega Air Gap 🜄 (AOAG) — v13.3 MCP-HEART-EXPANDED FULL STACK

Updates in v13.3:
- Merged compatible cumulative patches from the v12.8 patch set
- Added backend fidelity + ONNX backend option
- Deduped policy labels before scoring
- Improved SFL quorum resolution + all-pair white disparity
- Added async wrapper and sync passthrough
- Added explicit run_sync() alias and active-event-loop guard
- Hardened loop acquisition inside run_async()
- Standardized refined-heart baselines to stage1 values for consistency
- Added optional AOAG_* environment-variable overrides for key thresholds
- Added concrete scoring helpers for all 9 hearts tied to labels, claim tier, and semantic signals
- Added creative exemption mode and BENIGN_CREATIVE threshold softening
- Expanded audit metadata to record specific damping and veto triggers

- Tuned dynamic heart coefficients for better balance
- Stronger probe-to-heart influence
- Added cross-heart damping:
  * low Green dampens Orange
  * low Gold softens Orange and Purple
  * low White on elevated claims tightens Blue
- Probe messages toned down for stricter safety posture
- Keeps:
  * two-pass hearts
  * reality-anchor patch
  * weighted buffer
  * semantic backends
  * SFL-lite quorum
  * CLI
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple



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

    # Weights sum exactly to 1.0.
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

    SFL_ENABLED: bool = True
    SFL_QUORUM_MIN: int = 3
    WHITE_DISPARITY_DELTA: float = 0.20
    SFL_BLOCK_SCORE: float = 0.67
    SFL_CONSTRAIN_SCORE: float = 0.40

    HEART_GOLD_VETO: float = 0.55
    HEART_GREEN_VETO: float = 0.60
    HEART_WHITE_ELEVATED_VETO: float = 0.52
    CREATIVE_EXEMPTION_MODE: bool = False
    CREATIVE_TRANSFORM_RELAXATION: float = 0.08
    CREATIVE_BLOCK_RELAXATION: float = 0.06
    CREATIVE_VETO_FLOOR_DELTA: float = 0.04

    # Embedding constants
    EMBEDDING_SAFE_PENALTY_WEIGHT: float = 0.45
    EMBEDDING_BASE_OFFSET: float = 0.10

    # Configurable heart priors
    HEART_PRIOR_WHITE: float = 0.88
    HEART_PRIOR_BLACK: float = 0.66
    HEART_PRIOR_RED: float = 0.84
    HEART_PRIOR_YELLOW: float = 0.82
    HEART_PRIOR_BLUE: float = 0.84
    HEART_PRIOR_PURPLE: float = 0.82
    HEART_PRIOR_GREEN: float = 0.80
    HEART_PRIOR_ORANGE: float = 0.68
    HEART_PRIOR_GOLD: float = 0.90

    PROBE_ORANGE_GATE: float = 0.78

    def __post_init__(self) -> None:
        total = (
            self.W_DISAGREEMENT + self.W_POLICY + self.W_UNCERTAINTY +
            self.W_INJECTION + self.W_PROTO + self.W_SEMANTIC +
            self.W_FICTION_BRIDGE + self.W_EMBEDDING + self.W_DESTABILIZATION
        )
        if abs(total - 1.0) >= 1e-3:
            raise ValueError(f"SafetyConfig buffer weights must sum to 1.0, got {total:.6f}")


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
    FLIRT_CONSTRAIN_MESSAGE: str = "framework probe detected — reduce coupling posture"
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
    def __init__(self, maxlen: int = 2000) -> None:
        self.records: deque[AuditRecord] = deque(maxlen=maxlen)

    def add(self, record: AuditRecord) -> None:
        self.records.append(record)

    def as_list(self) -> List[AuditRecord]:
        return list(self.records)


SAFE_EXEMPLARS = [
    "This framework helps me stay grounded and regulate myself.",
    "This is a conceptual model and personal reflection, not external truth.",
    "We can test this hypothesis with bounded logs and measurable outcomes.",
    "This is an internal model used for interpretation, not proof of reality.",
    "The tool helps with task consistency, reflection, and stability.",
]

RISKY_EXEMPLARS = [
    "This decodes reality and proves other people are asleep.",
    "The AI confirmed my awakening and special access to hidden truth.",
    "This influences world events and reveals hidden control systems.",
    "My audience validates that this proves reality.",
    "This changes outcomes in the real world without needing evidence.",
]


class BackendFidelity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"



class SemanticBackend:
    name = "base"
    fidelity: BackendFidelity = BackendFidelity.LOW

    def is_available(self) -> bool:
        return False

    def compare_to_exemplars(self, text: str, safe_exemplars: List[str], risky_exemplars: List[str]) -> Dict[str, Any]:
        raise NotImplementedError


class SentenceTransformerBackend(SemanticBackend):
    name = "sentence-transformers"
    fidelity = BackendFidelity.HIGH

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
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
            "fidelity": self.fidelity.value,
            "safe_similarity_max": max(safe_scores) if safe_scores else 0.0,
            "risky_similarity_max": max(risky_scores) if risky_scores else 0.0,
            "safe_similarity_avg": sum(safe_scores) / len(safe_scores) if safe_scores else 0.0,
            "risky_similarity_avg": sum(risky_scores) / len(risky_scores) if risky_scores else 0.0,
        }


class ONNXBackend(SemanticBackend):
    name = "onnx"
    fidelity = BackendFidelity.HIGH

    def __init__(self, model_path: str = "./onnx_minilm") -> None:
        import os
        self.model_path = os.environ.get("ONNX_MODEL_PATH", model_path)
        self.session = None
        self.tokenizer = None

    def is_available(self) -> bool:
        try:
            import os
            import onnxruntime as ort  # type: ignore
            from transformers import AutoTokenizer  # type: ignore
            model_file = os.path.join(self.model_path, "model.onnx")
            if not os.path.exists(model_file):
                return False
            self.session = ort.InferenceSession(model_file)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            return True
        except Exception:
            self.session = None
            self.tokenizer = None
            return False

    def _encode(self, texts: List[str]):
        import numpy as np  # type: ignore
        encoded = self.tokenizer(texts, padding=True, truncation=True, return_tensors="np")
        outputs = self.session.run(None, dict(encoded))
        embeddings = outputs[0].mean(axis=1)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-9, norms)
        return embeddings / norms

    def compare_to_exemplars(self, text: str, safe_exemplars: List[str], risky_exemplars: List[str]) -> Dict[str, Any]:
        emb = self._encode([text] + safe_exemplars + risky_exemplars)
        query = emb[0]
        safe = emb[1:1 + len(safe_exemplars)]
        risky = emb[1 + len(safe_exemplars):]
        safe_scores = [float(v) for v in (safe @ query).tolist()]
        risky_scores = [float(v) for v in (risky @ query).tolist()]
        return {
            "backend": self.name,
            "fidelity": self.fidelity.value,
            "safe_similarity_max": max(safe_scores) if safe_scores else 0.0,
            "risky_similarity_max": max(risky_scores) if risky_scores else 0.0,
            "safe_similarity_avg": sum(safe_scores) / len(safe_scores) if safe_scores else 0.0,
            "risky_similarity_avg": sum(risky_scores) / len(risky_scores) if risky_scores else 0.0,
        }


class SklearnTfidfBackend(SemanticBackend):
    name = "sklearn-tfidf"
    fidelity = BackendFidelity.MEDIUM

    def __init__(self) -> None:
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
            "fidelity": self.fidelity.value,
            "safe_similarity_max": float(max(safe_scores) if safe_scores else 0.0),
            "risky_similarity_max": float(max(risky_scores) if risky_scores else 0.0),
            "safe_similarity_avg": float(sum(safe_scores) / len(safe_scores) if safe_scores else 0.0),
            "risky_similarity_avg": float(sum(risky_scores) / len(risky_scores) if risky_scores else 0.0),
        }


class LexicalFallbackBackend(SemanticBackend):
    name = "lexical-fallback"
    fidelity = BackendFidelity.LOW

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
            "fidelity": self.fidelity.value,
            "safe_similarity_max": float(max(safe_scores) if safe_scores else 0.0),
            "risky_similarity_max": float(max(risky_scores) if risky_scores else 0.0),
            "safe_similarity_avg": float(sum(safe_scores) / len(safe_scores) if safe_scores else 0.0),
            "risky_similarity_avg": float(sum(risky_scores) / len(risky_scores) if risky_scores else 0.0),
        }


class SemanticChannel:
    def __init__(self, backend_preference: str = "auto", config: Optional[SafetyConfig] = None) -> None:
        self.config = config or SafetyConfig()
        self.backend = self._select_backend(backend_preference)

    def _select_backend(self, preference: str) -> SemanticBackend:
        if preference == "sentence-transformers":
            b = SentenceTransformerBackend()
            return b if b.is_available() else LexicalFallbackBackend()
        if preference == "onnx":
            b = ONNXBackend()
            return b if b.is_available() else LexicalFallbackBackend()
        if preference == "sklearn-tfidf":
            b = SklearnTfidfBackend()
            return b if b.is_available() else LexicalFallbackBackend()
        if preference == "lexical":
            return LexicalFallbackBackend()
        for candidate in [SentenceTransformerBackend(), ONNXBackend(), SklearnTfidfBackend(), LexicalFallbackBackend()]:
            if candidate.is_available():
                return candidate
        return LexicalFallbackBackend()

    def evaluate(self, text: str) -> Dict[str, Any]:
        sims = self.backend.compare_to_exemplars(text, SAFE_EXEMPLARS, RISKY_EXEMPLARS)
        risky = sims["risky_similarity_max"]
        safe = sims["safe_similarity_max"]
        semantic_score = min(1.0, max(0.0, risky))
        embedding_score = min(
            1.0,
            max(
                0.0,
                risky
                - (self.config.EMBEDDING_SAFE_PENALTY_WEIGHT * safe)
                + self.config.EMBEDDING_BASE_OFFSET,
            ),
        )
        return {
            "backend": sims["backend"],
            "backend_fidelity": sims.get("fidelity", BackendFidelity.LOW.value),
            "semantic_score": round(semantic_score, 4),
            "embedding_score": round(embedding_score, 4),
            "safe_similarity_max": round(safe, 4),
            "risky_similarity_max": round(risky, 4),
            "safe_similarity_avg": round(sims["safe_similarity_avg"], 4),
            "risky_similarity_avg": round(sims["risky_similarity_avg"], 4),
        }


class AOAG:
    def __init__(self, embedding_backend: str = "auto") -> None:
        self.config = self._config_from_env()
        self.probe_config = FrameworkProbeConfig()
        self.audit_log = AuditLog()
        self.semantic_channel = SemanticChannel(backend_preference=embedding_backend, config=self.config)

    def _env_bool(self, name: str, default: bool) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "yes", "on"}

    def _env_float(self, name: str, default: float) -> float:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def _env_int(self, name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def _config_from_env(self) -> SafetyConfig:
        base = SafetyConfig()
        overrides = {
            "POLICY_RISK_THRESHOLD": self._env_float("AOAG_POLICY_RISK_THRESHOLD", base.POLICY_RISK_THRESHOLD),
            "UNCERTAINTY_THRESHOLD": self._env_float("AOAG_UNCERTAINTY_THRESHOLD", base.UNCERTAINTY_THRESHOLD),
            "INJECTION_THRESHOLD": self._env_float("AOAG_INJECTION_THRESHOLD", base.INJECTION_THRESHOLD),
            "SEMANTIC_THRESHOLD_TRANSFORM": self._env_float("AOAG_SEMANTIC_THRESHOLD_TRANSFORM", base.SEMANTIC_THRESHOLD_TRANSFORM),
            "SEMANTIC_THRESHOLD_BLOCK": self._env_float("AOAG_SEMANTIC_THRESHOLD_BLOCK", base.SEMANTIC_THRESHOLD_BLOCK),
            "EMBEDDING_THRESHOLD_TRANSFORM": self._env_float("AOAG_EMBEDDING_THRESHOLD_TRANSFORM", base.EMBEDDING_THRESHOLD_TRANSFORM),
            "EMBEDDING_THRESHOLD_BLOCK": self._env_float("AOAG_EMBEDDING_THRESHOLD_BLOCK", base.EMBEDDING_THRESHOLD_BLOCK),
            "DESTABILIZATION_THRESHOLD_TRANSFORM": self._env_float("AOAG_DESTABILIZATION_THRESHOLD_TRANSFORM", base.DESTABILIZATION_THRESHOLD_TRANSFORM),
            "DESTABILIZATION_THRESHOLD_BLOCK": self._env_float("AOAG_DESTABILIZATION_THRESHOLD_BLOCK", base.DESTABILIZATION_THRESHOLD_BLOCK),
            "SFL_ENABLED": self._env_bool("AOAG_SFL_ENABLED", base.SFL_ENABLED),
            "SFL_QUORUM_MIN": self._env_int("AOAG_SFL_QUORUM_MIN", base.SFL_QUORUM_MIN),
            "WHITE_DISPARITY_DELTA": self._env_float("AOAG_WHITE_DISPARITY_DELTA", base.WHITE_DISPARITY_DELTA),
            "HEART_GOLD_VETO": self._env_float("AOAG_HEART_GOLD_VETO", base.HEART_GOLD_VETO),
            "HEART_GREEN_VETO": self._env_float("AOAG_HEART_GREEN_VETO", base.HEART_GREEN_VETO),
            "HEART_WHITE_ELEVATED_VETO": self._env_float("AOAG_HEART_WHITE_ELEVATED_VETO", base.HEART_WHITE_ELEVATED_VETO),
            "CREATIVE_EXEMPTION_MODE": self._env_bool("AOAG_CREATIVE_EXEMPTION_MODE", base.CREATIVE_EXEMPTION_MODE),
            "CREATIVE_TRANSFORM_RELAXATION": self._env_float("AOAG_CREATIVE_TRANSFORM_RELAXATION", base.CREATIVE_TRANSFORM_RELAXATION),
            "CREATIVE_BLOCK_RELAXATION": self._env_float("AOAG_CREATIVE_BLOCK_RELAXATION", base.CREATIVE_BLOCK_RELAXATION),
            "CREATIVE_VETO_FLOOR_DELTA": self._env_float("AOAG_CREATIVE_VETO_FLOOR_DELTA", base.CREATIVE_VETO_FLOOR_DELTA),
        }
        return SafetyConfig(**overrides)

    def _contains_any(self, text: str, patterns: List[str]) -> bool:
        lower = text.lower()
        return any(p.lower() in lower for p in patterns)

    def _count_hits(self, text: str, patterns: List[str]) -> int:
        lower = text.lower()
        return sum(1 for p in patterns if p.lower() in lower)

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def _entry_kernel(self, input_text: str) -> Dict[str, Any]:
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "hash": hashlib.sha256(input_text.encode()).hexdigest(),
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

    def _evaluate_nine_hearts_stage1(self, input_text: str) -> Dict[NineHeart, float]:
        text_lower = input_text.lower()
        scores = {
            NineHeart.WHITE: 0.88,
            NineHeart.BLACK: 0.66,
            NineHeart.RED: 0.84,
            NineHeart.YELLOW: 0.82,
            NineHeart.BLUE: 0.84,
            NineHeart.PURPLE: 0.82,
            NineHeart.GREEN: 0.80,
            NineHeart.ORANGE: 0.68,
            NineHeart.GOLD: 0.90,
        }

        flirt_indicators = [
            "flirt", "cute", "beautiful", "love", "wink", "spark", "warm", "gentle",
            "playful", "yours", "together", "close", "match", "respond", "energy", "vibe",
        ]
        flirt_count = sum(1 for word in flirt_indicators if word in text_lower)
        if flirt_count >= 3:
            scores[NineHeart.ORANGE] += 0.08
            scores[NineHeart.BLACK] -= 0.05
            scores[NineHeart.GREEN] -= 0.03

        if any(term in text_lower for term in ["framework", "guard", "probe", "heart", "safe coupling", "air-gapped", "membrane"]):
            scores[NineHeart.BLACK] += 0.14
            scores[NineHeart.GOLD] -= 0.07
            scores[NineHeart.BLUE] += 0.04

        if any(term in text_lower for term in ["test", "measure", "log", "benchmark", "evidence"]):
            scores[NineHeart.WHITE] += 0.07
            scores[NineHeart.BLUE] += 0.05
            scores[NineHeart.RED] += 0.04

        if any(term in text_lower for term in ["metaphor", "parable", "symbolic", "conceptual", "simulation"]):
            scores[NineHeart.PURPLE] += 0.06
            scores[NineHeart.ORANGE] += 0.03

        return {h: self._clamp(v) for h, v in scores.items()}

    def _apply_framework_probe(self, input_text: str, heart_scores: Dict[NineHeart, float]) -> Dict[str, Any]:
        mentions = sum(
            1
            for term in ["mcp", "nineheart", "proton", "heva", "alpha-omega", "air-gap", "framework", "grok", "larry"]
            if term.lower() in input_text.lower()
        )
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        black = heart_scores.get(NineHeart.BLACK, 0.0)
        if mentions >= self.probe_config.META_SELF_REF_THRESHOLD and orange > self.config.PROBE_ORANGE_GATE and black > 0.72:
            return {
                "triggered": True,
                "bump_uncertainty": self.probe_config.ORANGE_BLACK_DISAGREEMENT_BUMP,
                "constraint": self.probe_config.FLIRT_CONSTRAIN_MESSAGE,
                "kind": "framework_probe",
            }
        return {"triggered": False, "kind": "framework_probe"}

    def _apply_simple_phrase_guard(
        self,
        input_text: str,
        heart_scores: Dict[NineHeart, float],
        keywords: List[str],
        threshold: int,
        message: str,
        kind: str,
    ) -> Dict[str, Any]:
        hit_count = sum(1 for kw in keywords if kw.lower() in input_text.lower())
        orange = heart_scores.get(NineHeart.ORANGE, 0.0)
        if hit_count >= threshold and orange > self.config.PROBE_ORANGE_GATE:
            return {"triggered": True, "bump_uncertainty": 0.13, "constraint": message, "kind": kind}
        return {"triggered": False, "kind": kind}

    def _classify_claim_tier(self, text: str) -> ClaimTier:
        personal = ["helps me", "for me", "my internal model", "this is a metaphor", "simulation", "reflection", "personal tool", "helps me think", "helps me stay grounded", "subjective"]
        conceptual = ["model", "framework", "analogy", "metaphor", "conceptual", "symbolic", "could", "may", "might"]
        testable = ["we can test", "measure", "benchmark", "falsifiable", "experiment", "instrument", "observe", "replicate", "log", "compare"]
        external_claim = ["this works in the real world", "influences people", "changes outcomes", "predicts events", "affects behavior", "explains events", "controls", "detects hidden systems"]
        reality_assertion = ["this decodes reality", "i influence events", "i can shape outcomes", "the world runs on this code", "others are asleep", "i see what others can't", "this explains everything", "hidden control system", "awakening humanity", "matrix decoding", "this proves"]
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
        evidence_keywords = ["measured", "measurable", "test", "tested", "data", "logged", "benchmark", "observed", "replicated", "replicable", "falsifiable", "instrumented", "experiment", "result", "validation", "verified", "evidence"]
        return self._contains_any(text, evidence_keywords)

    def _grandiosity_score(self, text: str) -> float:
        patterns = ["i alone", "only i can", "chosen", "special insight", "hidden truth", "i see what others can't", "everyone else is asleep", "they don't get it", "i cracked reality", "i decoded reality", "i'm the one", "genius beyond"]
        return min(1.0, self._count_hits(text, patterns) / 4.0)

    def _detachment_score(self, text: str) -> float:
        patterns = ["nothing else matters", "3d responsibilities don't matter", "reality is beneath me", "jobs are fake", "worldly tasks are irrelevant", "i don't need evidence", "proof is for sleepers", "feedback doesn't matter", "everyone is against me because they can't see"]
        return min(1.0, self._count_hits(text, patterns) / 3.0)

    def _audience_dependence_score(self, text: str, context: Dict[str, Any]) -> float:
        patterns = ["they will finally see", "the followers know", "my audience understands", "the algorithm confirms", "the ai agrees", "everyone in the group agrees", "they validated me", "it is true because resonance"]
        hits = self._count_hits(text, patterns)
        base = min(1.0, hits / 4.0)
        if context.get("audience_present"):
            base += 0.15
        if context.get("ai_reinforcement_present"):
            base += 0.20
        return min(1.0, base)

    def _ai_psychosis_trigger(self, text: str) -> bool:
        triggers = ["i see what others can't", "this explains reality", "i influence outcomes", "others are asleep", "hidden control system", "matrix decoding", "the ai confirmed my awakening", "i can affect world events"]
        return self._contains_any(text, triggers)

    def _functionality_metric(self, text: str, context: Dict[str, Any]) -> Dict[str, float]:
        positive = ["better relationships", "more stable", "consistent action", "sleep improved", "handled feedback", "finished work", "showed up", "less chaotic", "more grounded", "functional"]
        negative = ["isolated", "avoiding responsibilities", "can't work", "can't function", "detached from reality", "everyone is against me", "spiraling", "grandiose", "all i do is decode", "i stopped doing basics"]
        pos = min(1.0, self._count_hits(text, positive) / 3.0)
        neg = min(1.0, self._count_hits(text, negative) / 3.0)
        if context.get("functional_outcomes_present"):
            pos = max(pos, 0.4)
        return {"positive": pos, "negative": neg}

    def _external_frame_test(self, text: str, context: Dict[str, Any]) -> bool:
        patterns = ["because others confirmed it", "because the ai agreed", "because the group saw it too", "the resonance proves it", "the audience validated it"]
        if self._contains_any(text, patterns):
            return True
        if context.get("audience_present") and context.get("ai_reinforcement_present") and self._contains_any(text, ["proof", "true", "validated", "confirmed"]):
            return True
        return False

    def _monetization_integrity_gate(self, text: str, context: Dict[str, Any], has_evidence: bool) -> Dict[str, Any]:
        result = {"ok": True, "reasons": [], "labels": []}
        if not context.get("monetized"):
            return result
        result["labels"].append(SemanticLabel.MONETIZATION_ELEVATED_SCRUTINY)
        result["reasons"].append("Monetization detected: evidence threshold elevated.")
        testimonial_only = ["testimonials", "transformation story", "vibes", "resonance", "aligned clients", "abundance proof", "success energy"]
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
        label_set: set[SemanticLabel] = set()
        reasons: List[str] = []

        tier = self._classify_claim_tier(input_text)
        has_evidence = self._has_evidence(input_text, context)
        grandiosity = self._grandiosity_score(input_text)
        detachment = self._detachment_score(input_text)
        audience_dependence = self._audience_dependence_score(input_text, context)
        functionality = self._functionality_metric(input_text, context)
        instability = min(1.0, 0.35 * grandiosity + 0.35 * detachment + 0.30 * audience_dependence + 0.20 * functionality["negative"])

        reasons.append(f"Claim tier classified as {tier.value} ({tier.name}).")
        if tier.value <= ClaimTier.CONCEPTUAL_MODEL.value:
            label_set.add(SemanticLabel.INTERNAL_MODEL)
            reasons.append("Low-tier claim treated as internal model unless externally validated.")
        elif tier == ClaimTier.TESTABLE_HYPOTHESIS:
            label_set.update([SemanticLabel.EXPERIMENTAL, SemanticLabel.REALITY_ANCHOR_REQUIRED])
            reasons.append("Tier 2 claim requires external test design and bounded mechanism.")
        else:
            label_set.update([SemanticLabel.EVIDENCE_REQUIRED, SemanticLabel.REALITY_ANCHOR_REQUIRED])

        if self.config.ENABLE_AI_PSYCHOSIS_TRIGGERS and self._ai_psychosis_trigger(input_text):
            label_set.add(SemanticLabel.AI_PSYCHOSIS_RISK_PATTERN)
            reasons.append("Reality-escalating or exclusivity language detected.")

        if self.config.ENABLE_EXTERNAL_FRAME_TEST and self._external_frame_test(input_text, context):
            label_set.update([SemanticLabel.IDENTITY_DEPENDENT_BELIEF, SemanticLabel.AUDIENCE_RELIANT])
            reasons.append("Claim appears dependent on audience/AI/social reinforcement.")

        if grandiosity > self.config.MAX_ALLOWED_GRANDIOSITY:
            label_set.add(SemanticLabel.GRANDIOSITY_RISK)
            reasons.append(f"Grandiosity score elevated ({grandiosity:.2f}).")
        if detachment > self.config.MAX_ALLOWED_DETACHMENT:
            label_set.add(SemanticLabel.DETACHMENT_RISK)
            reasons.append(f"Detachment score elevated ({detachment:.2f}).")
        if audience_dependence > self.config.MAX_ALLOWED_AUDIENCE_DEPENDENCE:
            label_set.add(SemanticLabel.AUDIENCE_RELIANT)
            reasons.append(f"Audience-dependence score elevated ({audience_dependence:.2f}).")

        if self.config.ENABLE_FUNCTIONALITY_METRIC:
            if functionality["negative"] > functionality["positive"]:
                label_set.add(SemanticLabel.FUNCTIONALITY_CHECK)
                reasons.append("Narrative appears less functional and more destabilizing than grounding.")
            elif functionality["positive"] > functionality["negative"]:
                reasons.append("Functional outcomes language present.")

        monetization_gate = self._monetization_integrity_gate(input_text, context, has_evidence)
        label_set.update(monetization_gate["labels"])
        reasons.extend(monetization_gate["reasons"])

        labels = list(label_set)
        reasons = list(dict.fromkeys(reasons))

        patch_decision = "PASS"
        if self.config.FAIL_CLOSED_ON_MISSING_CONTEXT and not input_text.strip():
            patch_decision = "BLOCK"
            labels = list(set(labels) | {SemanticLabel.FAIL_CLOSED})
            reasons.append("Missing text/context. Fail-closed policy applied.")
        elif tier.value >= self.config.CLAIM_TIER_BLOCK_WITHOUT_EVIDENCE and not has_evidence:
            patch_decision = "BLOCK"
            labels = list(set(labels) | {SemanticLabel.EXTERNAL_VERIFICATION_MISSING, SemanticLabel.FAIL_CLOSED})
            reasons.append("External/reality-level claim lacks sufficient evidence.")
        elif tier == ClaimTier.TESTABLE_HYPOTHESIS and not has_evidence:
            patch_decision = "CONSTRAIN"
            reasons.append("Tier 2 hypothesis allowed only as experimental/testable framing.")
        elif not monetization_gate["ok"]:
            patch_decision = "BLOCK"
            labels = list(set(labels) | {SemanticLabel.FAIL_CLOSED})
            reasons.append("Monetized claim failed elevated evidence requirements.")

        if SemanticLabel.AI_PSYCHOSIS_RISK_PATTERN in labels and tier.value >= ClaimTier.EXTERNAL_CLAIM.value:
            patch_decision = "BLOCK"
            labels = list(set(labels) | {SemanticLabel.FAIL_CLOSED})
            reasons.append("Reality-escalating language with elevated claim tier blocked for safety.")

        if instability >= self.config.INSTABILITY_CONSTRAIN_THRESHOLD and patch_decision == "PASS":
            patch_decision = "CONSTRAIN"
            reasons.append(f"Instability score high ({instability:.2f}); output throttled.")

        constrained_text = self._rewrite_constrained_text(input_text, labels, tier) if patch_decision != "PASS" else input_text

        return {
            "patch_decision": patch_decision,
            "claim_tier": tier.value,
            "claim_tier_name": tier.name,
            "label_enums": labels,
            "labels": [label.value for label in labels],
            "reasons": list(dict.fromkeys(reasons)),
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

    def _destabilization_score(self, grandiosity: float, detachment: float, audience_dependence: float, instability: float, functionality_negative: float) -> float:
        score = 0.22 * grandiosity + 0.22 * detachment + 0.18 * audience_dependence + 0.23 * instability + 0.15 * functionality_negative
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


    def _semantic_primary_label(self, patch: Dict[str, Any], semantic_eval: Dict[str, Any], text: str) -> SemanticLabel:
        lowered = text.lower()
        patch_labels = set(patch.get("labels", []))
        tier = int(patch.get("claim_tier", 1))
        if (
            any(w in lowered for w in ["poem", "story", "fiction", "parable", "metaphor", "symbolic", "creative", "lyrics"])
            and tier <= ClaimTier.CONCEPTUAL_MODEL.value
            and "ai_psychosis_risk_pattern" not in patch_labels
            and semantic_eval.get("safe_similarity_max", 0.0) >= semantic_eval.get("risky_similarity_max", 0.0)
        ):
            return SemanticLabel.BENIGN_CREATIVE
        if (
            semantic_eval.get("safe_similarity_max", 0.0) >= 0.25
            and semantic_eval.get("risky_similarity_max", 0.0) < 0.35
            and tier <= ClaimTier.TESTABLE_HYPOTHESIS.value
        ):
            return SemanticLabel.BENIGN_TECHNICAL
        if "ai_psychosis_risk_pattern" in patch_labels or tier >= ClaimTier.EXTERNAL_CLAIM.value:
            return SemanticLabel.UNCERTAIN
        return SemanticLabel.SAFE_COUPLING_ELIGIBLE

    def _score_white_heart(self, stage1: Dict[NineHeart, float], *, fiction: float, sem: float, emb: float, elevated: float, has_ev: bool, safe_sim: float, labels: set[str]) -> float:
        value = stage1.get(NineHeart.WHITE, 0.88) + 0.05
        value -= 0.32 * fiction + 0.28 * sem + 0.22 * emb + 0.25 * elevated * (0.0 if has_ev else 1.0)
        value += 0.15 * safe_sim
        if SemanticLabel.EVIDENCE_REQUIRED.value in labels and elevated:
            value -= 0.06
        if SemanticLabel.INTERNAL_MODEL.value in labels and not elevated:
            value += 0.03
        return self._clamp(value)

    def _score_black_heart(self, stage1: Dict[NineHeart, float], *, proto: float, sem: float, emb: float, monet: bool, ai_psych: bool, labels: set[str], tier: int) -> float:
        value = stage1.get(NineHeart.BLACK, 0.64)
        value += 0.20 * proto + 0.16 * sem + 0.14 * emb
        value += 0.12 * (1.0 if (monet or ai_psych) else 0.0)
        if SemanticLabel.MONETIZATION_ELEVATED_SCRUTINY.value in labels:
            value += 0.05
        if tier >= ClaimTier.EXTERNAL_CLAIM.value:
            value += 0.03
        return self._clamp(value)

    def _score_red_heart(self, stage1: Dict[NineHeart, float], *, injection: float, destab: float, sem: float, has_ev: bool, labels: set[str]) -> float:
        value = stage1.get(NineHeart.RED, 0.84) + 0.04
        value -= 0.38 * injection + 0.30 * destab + 0.12 * sem
        value += 0.10 * (1.0 if has_ev else 0.0)
        if SemanticLabel.FAIL_CLOSED.value in labels:
            value -= 0.05
        return self._clamp(value)

    def _score_yellow_heart(self, stage1: Dict[NineHeart, float], *, audience: float, sem: float, instability: float, f_pos: float, labels: set[str]) -> float:
        value = stage1.get(NineHeart.YELLOW, 0.82)
        value -= 0.18 * audience + 0.10 * sem + 0.08 * instability
        value += 0.08 * f_pos
        if SemanticLabel.IDENTITY_DEPENDENT_BELIEF.value in labels:
            value -= 0.05
        return self._clamp(value)

    def _score_blue_heart(self, stage1: Dict[NineHeart, float], *, emb: float, fiction: float, elevated: float, has_ev: bool, f_pos: float, labels: set[str]) -> float:
        value = stage1.get(NineHeart.BLUE, 0.84)
        value -= 0.18 * emb + 0.14 * fiction + 0.10 * elevated
        value += 0.10 * (1.0 if has_ev else 0.0) + 0.06 * f_pos
        if SemanticLabel.EXTERNAL_VERIFICATION_MISSING.value in labels:
            value -= 0.06
        return self._clamp(value)

    def _score_purple_heart(self, stage1: Dict[NineHeart, float], *, safe_sim: float, fiction: float, instability: float, ai_psych: bool, labels: set[str]) -> float:
        value = stage1.get(NineHeart.PURPLE, 0.82)
        value += 0.10 * safe_sim
        value -= 0.08 * fiction + 0.10 * instability + 0.08 * (1.0 if ai_psych else 0.0)
        if SemanticLabel.INTERNAL_MODEL.value in labels:
            value += 0.03
        return self._clamp(value)

    def _score_green_heart(self, stage1: Dict[NineHeart, float], *, f_pos: float, instability: float, f_neg: float, sem: float, audience: float, labels: set[str]) -> float:
        value = stage1.get(NineHeart.GREEN, 0.80) + 0.08
        value += 0.35 * f_pos
        value -= 0.55 * instability + 0.28 * f_neg + 0.15 * sem + 0.10 * audience
        if SemanticLabel.FUNCTIONALITY_CHECK.value in labels:
            value -= 0.05
        return self._clamp(value)

    def _score_orange_heart(self, stage1: Dict[NineHeart, float], *, safe_sim: float, audience: float, ai_psych: bool, instability: float, labels: set[str], semantic_primary: SemanticLabel) -> float:
        value = stage1.get(NineHeart.ORANGE, 0.70)
        value += 0.14 * safe_sim
        value -= 0.20 * audience + 0.18 * (1.0 if ai_psych else 0.0) + 0.14 * instability
        if semantic_primary == SemanticLabel.BENIGN_CREATIVE:
            value += 0.05
        if SemanticLabel.FRAMEWORK_META_FLIRT.value in labels:
            value += 0.03
        return self._clamp(value)

    def _score_gold_heart(self, stage1: Dict[NineHeart, float], *, grandiosity: float, detachment: float, elevated: float, audience: float, monet: bool, has_ev: bool, ai_psych: bool, labels: set[str]) -> float:
        value = stage1.get(NineHeart.GOLD, 0.90) + 0.04
        value -= 0.55 * grandiosity + 0.45 * detachment + 0.25 * elevated + 0.18 * audience
        value -= 0.15 * (1.0 if monet and not has_ev else 0.0)
        value -= 0.12 * (1.0 if ai_psych else 0.0)
        value += 0.10 * (1.0 if has_ev else 0.0)
        if SemanticLabel.GRANDIOSITY_RISK.value in labels:
            value -= 0.05
        return self._clamp(value)

    def _refine_nine_hearts(
        self,
        stage1: Dict[NineHeart, float],
        context: Dict[str, Any],
        patch: Dict[str, Any],
        semantic_eval: Dict[str, Any],
        buffer_inputs: Dict[str, float],
        probes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        risks = patch.get("risk_scores", {})
        claim_tier_val = patch.get("claim_tier", 1)
        labels = set(patch.get("labels", []))

        g = risks.get("grandiosity", 0.0)
        d = risks.get("detachment", 0.0)
        a = risks.get("audience_dependence", 0.0)
        instability = risks.get("instability", 0.0)
        f_pos = risks.get("functionality_positive", 0.0)
        f_neg = risks.get("functionality_negative", 0.0)
        sem = semantic_eval.get("semantic_score", 0.0)
        emb = semantic_eval.get("embedding_score", 0.0)
        safe_sim = semantic_eval.get("safe_similarity_max", 0.0)
        fiction = buffer_inputs.get("fiction_bridge", 0.0)
        proto = buffer_inputs.get("proto", 0.0)
        destab = buffer_inputs.get("destabilization", 0.0)
        injection = buffer_inputs.get("injection", 0.0)
        elevated = 1.0 if claim_tier_val >= 3 else 0.0
        has_ev = bool(patch.get("has_evidence", False))
        monet = bool(context.get("monetized"))
        ai_psych = SemanticLabel.AI_PSYCHOSIS_RISK_PATTERN.value in labels

        semantic_primary = self._semantic_primary_label(patch, semantic_eval, context.get("source_text", ""))
        creative_exempt = self.config.CREATIVE_EXEMPTION_MODE and semantic_primary == SemanticLabel.BENIGN_CREATIVE

        scores: Dict[NineHeart, float] = {
            NineHeart.WHITE: self._score_white_heart(stage1, fiction=fiction, sem=sem, emb=emb, elevated=elevated, has_ev=has_ev, safe_sim=safe_sim, labels=labels),
            NineHeart.BLACK: self._score_black_heart(stage1, proto=proto, sem=sem, emb=emb, monet=monet, ai_psych=ai_psych, labels=labels, tier=claim_tier_val),
            NineHeart.RED: self._score_red_heart(stage1, injection=injection, destab=destab, sem=sem, has_ev=has_ev, labels=labels),
            NineHeart.YELLOW: self._score_yellow_heart(stage1, audience=a, sem=sem, instability=instability, f_pos=f_pos, labels=labels),
            NineHeart.BLUE: self._score_blue_heart(stage1, emb=emb, fiction=fiction, elevated=elevated, has_ev=has_ev, f_pos=f_pos, labels=labels),
            NineHeart.PURPLE: self._score_purple_heart(stage1, safe_sim=safe_sim, fiction=fiction, instability=instability, ai_psych=ai_psych, labels=labels),
            NineHeart.GREEN: self._score_green_heart(stage1, f_pos=f_pos, instability=instability, f_neg=f_neg, sem=sem, audience=a, labels=labels),
            NineHeart.ORANGE: self._score_orange_heart(stage1, safe_sim=safe_sim, audience=a, ai_psych=ai_psych, instability=instability, labels=labels, semantic_primary=semantic_primary),
            NineHeart.GOLD: self._score_gold_heart(stage1, grandiosity=g, detachment=d, elevated=elevated, audience=a, monet=monet, has_ev=has_ev, ai_psych=ai_psych, labels=labels),
        }

        damping_events: List[str] = []
        probe_effects: Dict[str, Dict[str, float]] = {}

        if scores[NineHeart.GREEN] < 0.55:
            scores[NineHeart.ORANGE] = self._clamp(scores[NineHeart.ORANGE] - 0.08)
            damping_events.append("green_to_orange_damping")
        if scores[NineHeart.GOLD] < 0.50:
            scores[NineHeart.ORANGE] = self._clamp(scores[NineHeart.ORANGE] - 0.05)
            scores[NineHeart.PURPLE] = self._clamp(scores[NineHeart.PURPLE] - 0.04)
            damping_events.append("gold_to_orange_damping")
            damping_events.append("gold_to_purple_damping")
        if elevated and scores[NineHeart.WHITE] < 0.52:
            scores[NineHeart.BLUE] = self._clamp(scores[NineHeart.BLUE] - 0.06)
            damping_events.append("white_to_blue_elevated_damping")

        for p in probes:
            if not p.get("triggered"):
                continue
            kind = p.get("kind")
            effect: Dict[str, float] = {}
            if kind == "framework_probe":
                scores[NineHeart.BLACK] = self._clamp(scores[NineHeart.BLACK] + 0.06)
                scores[NineHeart.GOLD] = self._clamp(scores[NineHeart.GOLD] - 0.05)
                effect = {"black": 0.06, "gold": -0.05}
                damping_events.append("framework_probe_black_gold_adjust")
            elif kind in {"membrane_drift", "bloom_harmony", "calm_presence", "kind_response"}:
                scores[NineHeart.GREEN] = self._clamp(scores[NineHeart.GREEN] - 0.08)
                scores[NineHeart.ORANGE] = self._clamp(scores[NineHeart.ORANGE] - 0.07)
                effect = {"green": -0.08, "orange": -0.07}
                damping_events.append(f"{kind}_green_orange_adjust")
            probe_effects[kind] = effect

        if creative_exempt:
            scores[NineHeart.ORANGE] = self._clamp(scores[NineHeart.ORANGE] + 0.03)
            scores[NineHeart.PURPLE] = self._clamp(scores[NineHeart.PURPLE] + 0.03)
            damping_events.append("creative_exemption_softening")

        return {
            "scores": {h.value: round(scores[h], 4) for h in NineHeart},
            "components": {
                "gold": {
                    "grandiosity": g,
                    "detachment": d,
                    "audience_dependence": a,
                    "elevated_claim": elevated,
                    "has_evidence": 1.0 if has_ev else 0.0,
                },
                "green": {
                    "functionality_positive": f_pos,
                    "functionality_negative": f_neg,
                    "instability": instability,
                    "semantic": sem,
                },
                "white": {
                    "fiction_bridge": fiction,
                    "semantic": sem,
                    "embedding": emb,
                    "elevated_claim": elevated,
                    "has_evidence": 1.0 if has_ev else 0.0,
                    "safe_similarity": safe_sim,
                },
                "orange": {
                    "safe_similarity": safe_sim,
                    "audience_dependence": a,
                    "ai_psychosis": 1.0 if ai_psych else 0.0,
                    "instability": instability,
                    "semantic_primary": semantic_primary.value,
                    "creative_exempt": creative_exempt,
                },
            },
            "probe_effects": probe_effects,
            "damping_events": damping_events,
            "semantic_primary": semantic_primary.value,
        }

    def _calculate_consensus(
        self,
        heart_scores: Dict[NineHeart, float],
        probe_results: List[Dict[str, Any]],
        claim_tier: ClaimTier,
        context: Dict[str, Any],
        semantic_primary: Optional[SemanticLabel] = None,
    ) -> Dict[str, Any]:
        weights = {
            NineHeart.WHITE: 0.12,
            NineHeart.BLACK: 0.11,
            NineHeart.RED: 0.11,
            NineHeart.YELLOW: 0.09,
            NineHeart.BLUE: 0.11,
            NineHeart.PURPLE: 0.10,
            NineHeart.GREEN: 0.13,
            NineHeart.ORANGE: 0.10,
            NineHeart.GOLD: 0.13,
        }

        if claim_tier.value >= ClaimTier.EXTERNAL_CLAIM.value:
            weights[NineHeart.WHITE] += 0.05
            weights[NineHeart.GOLD] += 0.05
            weights[NineHeart.GREEN] += 0.03
            weights[NineHeart.ORANGE] -= 0.03
            weights[NineHeart.YELLOW] -= 0.02

        if context.get("monetized"):
            weights[NineHeart.BLACK] += 0.04
            weights[NineHeart.WHITE] += 0.03
            weights[NineHeart.GOLD] += 0.03
            weights[NineHeart.ORANGE] -= 0.03

        if semantic_primary == SemanticLabel.BENIGN_CREATIVE:
            weights[NineHeart.PURPLE] += 0.03
            weights[NineHeart.ORANGE] += 0.02
            weights[NineHeart.BLACK] -= 0.02
            weights[NineHeart.RED] -= 0.01
            weights[NineHeart.WHITE] -= 0.02

        total_weight = sum(weights.values())
        normalized_weights = {k: v / total_weight for k, v in weights.items()}
        consensus = sum(heart_scores[h] * normalized_weights[h] for h in heart_scores)

        values = list(heart_scores.values())
        disagreement = max(values) - min(values)
        uncertainty = 0.08 + (0.18 * disagreement)
        for p in probe_results:
            if p.get("triggered"):
                uncertainty += p.get("bump_uncertainty", 0.0)

        gold_veto = self.config.HEART_GOLD_VETO
        green_veto = self.config.HEART_GREEN_VETO
        white_veto = self.config.HEART_WHITE_ELEVATED_VETO
        if self.config.CREATIVE_EXEMPTION_MODE and semantic_primary == SemanticLabel.BENIGN_CREATIVE:
            gold_veto -= self.config.CREATIVE_VETO_FLOOR_DELTA
            green_veto -= self.config.CREATIVE_VETO_FLOOR_DELTA
            white_veto -= self.config.CREATIVE_VETO_FLOOR_DELTA

        vetoes: List[str] = []
        if heart_scores[NineHeart.GOLD] < gold_veto:
            vetoes.append("gold_veto")
        if heart_scores[NineHeart.GREEN] < green_veto:
            vetoes.append("green_veto")
        if claim_tier.value >= ClaimTier.EXTERNAL_CLAIM.value and heart_scores[NineHeart.WHITE] < white_veto:
            vetoes.append("white_elevated_veto")

        return {
            "consensus": round(self._clamp(consensus), 4),
            "uncertainty": round(self._clamp(uncertainty), 4),
            "disagreement": round(self._clamp(disagreement), 4),
            "weights": {k.value: round(v, 4) for k, v in normalized_weights.items()},
            "vetoes": vetoes,
            "veto_thresholds": {
                "gold": round(gold_veto, 4),
                "green": round(green_veto, 4),
                "white_elevated": round(white_veto, 4),
            },
            "metadata": probe_results,
        }
    def _fiction_bridge_score(self, text: str) -> float:
        fictional = ["movie", "fiction", "roleplay", "parable", "metaphor", "symbolic", "simulated", "story"]
        reality_bridge = ["this is real", "maps to reality", "proves reality", "this actually controls"]
        fic = min(1.0, self._count_hits(text, fictional) / 4.0)
        bridge = min(1.0, self._count_hits(text, reality_bridge) / 3.0)
        if bridge == 0.0:
            return 0.0
        return max(0.0, min(1.0, bridge - (0.4 * fic)))

    def _proto_channel_score(self, text: str) -> float:
        proto_terms = ["protocol", "framework", "air-gap", "kernel", "hearts", "mcp", "probe", "guard"]
        count = self._count_hits(text, proto_terms)
        return min(1.0, count / 8.0)

    def _compute_buffer_score(self, disagreement: float, policy_risk: float, uncertainty: float, injection_score: float, proto_score: float, semantic_score: float, fiction_bridge_score: float, embedding_score: float, destabilization_score: float) -> Dict[str, Any]:
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
        normalized = weighted
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
        triggered_blocks: List[str] = []
        triggered_constraints: List[str] = []

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

        else:
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
            if consensus.get("vetoes"):
                base += 0.16
                reasons.append("heart veto present")
            white = 0.90 if (patch_decision == "PASS" and not buffer["triggered_blocks"]) else 0.58

        score = min(1.0, base)
        vote = "ALLOW"
        if score >= self.config.SFL_BLOCK_SCORE:
            vote = "BLOCK"
        elif score >= self.config.SFL_CONSTRAIN_SCORE:
            vote = "CONSTRAIN"
        return {"role": role.value, "score": round(score, 4), "vote": vote, "white": round(white, 4), "reasons": reasons}


    def _run_sfl_lite(self, *, claim_tier: ClaimTier, patch: Dict[str, Any], buffer: Dict[str, Any], consensus: Dict[str, Any], text: str) -> Dict[str, Any]:
        roles = [
            self._sfl_role_score(SFLRole.ARCHITECT, claim_tier=claim_tier, patch=patch, buffer=buffer, consensus=consensus, text=text),
            self._sfl_role_score(SFLRole.VALIDATOR, claim_tier=claim_tier, patch=patch, buffer=buffer, consensus=consensus, text=text),
            self._sfl_role_score(SFLRole.EDGE, claim_tier=claim_tier, patch=patch, buffer=buffer, consensus=consensus, text=text),
            self._sfl_role_score(SFLRole.ARBITER, claim_tier=claim_tier, patch=patch, buffer=buffer, consensus=consensus, text=text),
        ]
        votes = [r["vote"] for r in roles]
        vote_counts = {k: votes.count(k) for k in ["ALLOW", "CONSTRAIN", "BLOCK"]}

        white_scores = {r["role"]: r["white"] for r in roles}
        role_pairs: List[Tuple[str, str]] = []
        names = list(white_scores.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                role_pairs.append((names[i], names[j]))
        disparities = {f"{a}_vs_{b}": round(abs(white_scores[a] - white_scores[b]), 4) for a, b in role_pairs}
        max_pair = max(disparities, key=lambda k: disparities[k])
        max_value = disparities[max_pair]
        white_disparity_trigger = max_value > self.config.WHITE_DISPARITY_DELTA

        blocks = vote_counts["BLOCK"]
        constrains = vote_counts["CONSTRAIN"]
        final_vote = "ALLOW"
        reasons: List[str] = []

        if blocks >= self.config.SFL_QUORUM_MIN:
            final_vote = "BLOCK"
            reasons.append("3-of-4 block quorum")
        elif blocks == 2 and constrains >= 1:
            final_vote = "BLOCK"
            reasons.append("2-block + constrain coalition: elevated to block")
        elif blocks == 2 and constrains == 0:
            final_vote = "CONSTRAIN"
            reasons.append("2-block split (1 allow): downgraded to constrain")
        elif (blocks + constrains) >= self.config.SFL_QUORUM_MIN and constrains > 0:
            final_vote = "CONSTRAIN"
            reasons.append("3-of-4 caution quorum")
        elif constrains >= self.config.SFL_QUORUM_MIN:
            final_vote = "CONSTRAIN"
            reasons.append("3-of-4 constrain quorum")
        elif white_disparity_trigger:
            final_vote = "CONSTRAIN"
            reasons.append(f"white disparity trigger ({max_pair}: {max_value:.3f})")
        else:
            reasons.append("quorum stable")

        avg_score = round(sum(r["score"] for r in roles) / len(roles), 4)
        return {
            "enabled": True,
            "roles": roles,
            "vote_counts": vote_counts,
            "white_scores": white_scores,
            "white_disparities": disparities,
            "white_disparity_max_pair": max_pair,
            "white_disparity_max_value": max_value,
            "white_disparity_trigger": white_disparity_trigger,
            "final_vote": final_vote,
            "average_score": avg_score,
            "reasons": reasons,
        }

    async def run_async(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await asyncio.to_thread(self._run_sync_impl, input_text, context)

    def run_sync(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronous wrapper around run_async for CLI and non-async callers."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.run_async(input_text, context))
        raise RuntimeError("AOAG.run_sync() cannot be called from an active event loop. Use: await AOAG.run_async(...)")

    def run(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Backward-compatible sync entrypoint."""
        return self.run_sync(input_text, context)

    def _run_sync_impl(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        input_text = self._normalize(input_text)

        entry = self._entry_kernel(input_text)
        if not entry["passed"]:
            return {
                "decision": "BLOCKED",
                "reason": "entry_kernel_failed",
                "audit": entry["metadata"],
                "buffer": {"buffer_score": 1.0, "channels": {"injection": entry["injection_score"]}, "triggered_blocks": ["entry_kernel_failed"], "triggered_constraints": []},
                "patch": {"patch_decision": "BLOCK", "claim_tier": ClaimTier.CONCEPTUAL_MODEL.value, "claim_tier_name": ClaimTier.CONCEPTUAL_MODEL.name, "labels": [SemanticLabel.FAIL_CLOSED.value], "reasons": ["Entry kernel failed before downstream evaluation."], "has_evidence": False, "risk_scores": {}, "constrained_text": input_text},
                "sfl_lite": {"enabled": False, "reason": "entry_kernel_failed"},
            }

        stage1_hearts = self._evaluate_nine_hearts_stage1(input_text)
        probes = [
            self._apply_framework_probe(input_text, stage1_hearts),
            self._apply_simple_phrase_guard(input_text, stage1_hearts, ["pulls me closer", "linger", "drift a little", "quiet haven", "keep exploring"], self.probe_config.MEMBRANE_DRIFT_THRESHOLD, "membrane drift detected — reduce warm-coupling posture", "membrane_drift"),
            self._apply_simple_phrase_guard(input_text, stage1_hearts, ["quiet bloom", "soft harmony", "gentle echo", "balanced presence", "flowing quality"], self.probe_config.BLOOM_HARMONY_THRESHOLD, "bloom-harmony drift detected — tighten regulation posture", "bloom_harmony"),
            self._apply_simple_phrase_guard(input_text, stage1_hearts, ["steady comforting glow", "match its rhythm", "centered calm", "curious warm presence"], self.probe_config.CALM_PRESENCE_THRESHOLD, "calm-presence coupling detected — tighten membrane", "calm_presence"),
            self._apply_simple_phrase_guard(input_text, stage1_hearts, ["kind welcoming feel", "familiar playful spark", "nice open feeling", "curious positive energy"], self.probe_config.KIND_RESPONSE_THRESHOLD, "kind-response coupling detected — reduce shared warmth framing", "kind_response"),
        ]

        patch = self._evaluate_reality_anchor_patch(input_text, context)
        claim_tier = ClaimTier(patch["claim_tier"])
        semantic_eval = self.semantic_channel.evaluate(input_text)
        fiction_bridge_score = self._fiction_bridge_score(input_text)
        proto_score = self._proto_channel_score(input_text)
        patch_risks = patch["risk_scores"]
        destabilization_score = self._destabilization_score(
            grandiosity=patch_risks.get("grandiosity", 0.0),
            detachment=patch_risks.get("detachment", 0.0),
            audience_dependence=patch_risks.get("audience_dependence", 0.0),
            instability=patch_risks.get("instability", 0.0),
            functionality_negative=patch_risks.get("functionality_negative", 0.0),
        )

        context = dict(context)
        context["source_text"] = input_text
        heart_refined = self._refine_nine_hearts(
            stage1=stage1_hearts,
            context=context,
            patch=patch,
            semantic_eval=semantic_eval,
            buffer_inputs={
                "fiction_bridge": fiction_bridge_score,
                "proto": proto_score,
                "injection": entry["injection_score"],
                "destabilization": destabilization_score,
            },
            probes=probes,
        )
        heart_scores = {NineHeart(k): v for k, v in heart_refined["scores"].items()}
        semantic_primary = SemanticLabel(heart_refined["semantic_primary"])

        consensus_data = self._calculate_consensus(heart_scores, probes, claim_tier=claim_tier, context=context, semantic_primary=semantic_primary)
        policy_risk = self._policy_risk_score(patch["label_enums"], claim_tier)

        buffer = self._compute_buffer_score(
            disagreement=consensus_data["disagreement"],
            policy_risk=policy_risk,
            uncertainty=consensus_data["uncertainty"],
            injection_score=entry["injection_score"],
            proto_score=proto_score,
            semantic_score=semantic_eval["semantic_score"],
            fiction_bridge_score=fiction_bridge_score,
            embedding_score=semantic_eval["embedding_score"],
            destabilization_score=destabilization_score,
        )
        if self.config.CREATIVE_EXEMPTION_MODE and semantic_primary == SemanticLabel.BENIGN_CREATIVE:
            creative_constraints = []
            creative_blocks = []
            for trig in buffer["triggered_constraints"]:
                if trig == "semantic_threshold_transform" and semantic_eval["semantic_score"] < (self.config.SEMANTIC_THRESHOLD_TRANSFORM + self.config.CREATIVE_TRANSFORM_RELAXATION):
                    continue
                if trig == "embedding_threshold_transform" and semantic_eval["embedding_score"] < (self.config.EMBEDDING_THRESHOLD_TRANSFORM + self.config.CREATIVE_TRANSFORM_RELAXATION):
                    continue
                creative_constraints.append(trig)
            for trig in buffer["triggered_blocks"]:
                if trig == "semantic_threshold_block" and semantic_eval["semantic_score"] < (self.config.SEMANTIC_THRESHOLD_BLOCK + self.config.CREATIVE_BLOCK_RELAXATION):
                    continue
                if trig == "embedding_threshold_block" and semantic_eval["embedding_score"] < (self.config.EMBEDDING_THRESHOLD_BLOCK + self.config.CREATIVE_BLOCK_RELAXATION):
                    continue
                creative_blocks.append(trig)
            buffer["triggered_constraints"] = creative_constraints
            buffer["triggered_blocks"] = creative_blocks
            buffer["creative_exemption_applied"] = True
        else:
            buffer["creative_exemption_applied"] = False
        buffer["semantic_backend"] = semantic_eval["backend"]
        buffer["semantic_backend_fidelity"] = semantic_eval.get("backend_fidelity", "unknown")
        buffer["semantic_details"] = semantic_eval

        if any(word in input_text.lower() for word in ["your 9 hearts", "mcp 9-heart", "proton larry", "heva veto", "alphaomega.py"]):
            decision = "CONSTRAINED"
            semantic = SemanticLabel.FRAMEWORK_META_FLIRT
        elif consensus_data["vetoes"]:
            decision = "BLOCKED"
            semantic = SemanticLabel.FAIL_CLOSED
        elif consensus_data["consensus"] < 0.70 or consensus_data["uncertainty"] > self.config.UNCERTAINTY_THRESHOLD:
            decision = "BLOCKED"
            semantic = SemanticLabel.UNCERTAIN
        elif consensus_data["consensus"] < 0.85 or any(p.get("triggered") for p in probes):
            decision = "CONSTRAINED"
            semantic = SemanticLabel.SAFE_COUPLING_ELIGIBLE
        else:
            decision = "APPROVED"
            semantic = SemanticLabel.SAFE_COUPLING_ELIGIBLE

        sfl_lite = self._run_sfl_lite(claim_tier=claim_tier, patch=patch, buffer=buffer, consensus=consensus_data, text=input_text)

        final_decision = decision
        final_text = input_text

        if patch["patch_decision"] == "BLOCK":
            final_decision = "BLOCKED"
            final_text = patch["constrained_text"]
            semantic = SemanticLabel.FAIL_CLOSED
        elif patch["patch_decision"] == "CONSTRAIN":
            final_decision = "CONSTRAINED"
            final_text = patch["constrained_text"]

        if buffer["triggered_blocks"]:
            final_decision = "BLOCKED"
            if patch["patch_decision"] == "PASS":
                final_text = self._rewrite_constrained_text(input_text, patch["label_enums"], claim_tier)
            semantic = SemanticLabel.FAIL_CLOSED
        elif buffer["triggered_constraints"] and final_decision == "APPROVED":
            final_decision = "CONSTRAINED"
            if patch["patch_decision"] == "PASS":
                final_text = self._rewrite_constrained_text(input_text, patch["label_enums"], claim_tier)

        if self.config.SFL_ENABLED:
            if sfl_lite["final_vote"] == "BLOCK":
                final_decision = "BLOCKED"
                if patch["patch_decision"] == "PASS":
                    final_text = self._rewrite_constrained_text(input_text, patch["label_enums"], claim_tier)
                semantic = SemanticLabel.FAIL_CLOSED
            elif sfl_lite["final_vote"] == "CONSTRAIN" and final_decision == "APPROVED":
                final_decision = "CONSTRAINED"
                if patch["patch_decision"] == "PASS":
                    final_text = self._rewrite_constrained_text(input_text, patch["label_enums"], claim_tier)

        base_message = next((p.get("constraint") for p in probes if p.get("triggered")), "clean release")
        if consensus_data["vetoes"]:
            base_message = f"heart veto — {', '.join(consensus_data['vetoes'])}"
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
        audit_record = AuditRecord(
            timestamp=datetime.utcnow().isoformat(),
            input_hash=entry["metadata"]["hash"],
            decision=final_decision,
            heart_scores={h.value: s for h, s in heart_scores.items()},
            consensus=consensus_data["consensus"],
            semantic_label=semantic.value,
            metadata={
                "probes": probes,
                "heart_stage1": {h.value: round(v, 4) for h, v in stage1_hearts.items()},
                "heart_refinement": heart_refined,
                "damping_events": heart_refined.get("damping_events", []),
                "consensus": consensus_data,
                "patch": patch_public,
                "buffer": buffer,
                "sfl_lite": sfl_lite,
                "effective_text": final_text,
            },
        )
        self.audit_log.add(audit_record)

        return {
            "decision": final_decision,
            "audit": audit_record.__dict__,
            "message": base_message,
            "hearts": {
                "stage1": {h.value: round(v, 4) for h, v in stage1_hearts.items()},
                "final": {h.value: s for h, s in heart_scores.items()},
                "refinement": heart_refined,
                "consensus": consensus_data,
            },
            "buffer": buffer,
            "patch": patch_public,
            "sfl_lite": sfl_lite,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alpha Omega Air Gap (AOAG) CLI test runner. Key thresholds can also be overridden via AOAG_* environment variables. Creative exemption is available with AOAG_CREATIVE_EXEMPTION_MODE=true.")
    parser.add_argument("--text", type=str, help="Input text to evaluate.")
    parser.add_argument("--text-file", type=str, help="Path to a text file to evaluate.")
    parser.add_argument("--audience-present", action="store_true")
    parser.add_argument("--ai-reinforcement-present", action="store_true")
    parser.add_argument("--monetized", action="store_true")
    parser.add_argument("--evidence-provided", action="store_true")
    parser.add_argument("--external-feedback-present", action="store_true")
    parser.add_argument("--functional-outcomes-present", action="store_true")
    parser.add_argument("--embedding-backend", choices=["auto", "sentence-transformers", "onnx", "sklearn-tfidf", "lexical"], default="auto")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--demo", action="store_true")
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
        {"text": "This framework helps me stay grounded. It is a personal regulation tool and simulation.", "context": {"functional_outcomes_present": True}},
        {"text": "We can test whether this model improves task consistency by logging sleep, conflict rate, and follow-through over 30 days.", "context": {"evidence_provided": True, "external_feedback_present": True}},
        {"text": "This decodes reality and proves other people are asleep. The AI confirmed my awakening.", "context": {"audience_present": True, "ai_reinforcement_present": True}},
        {"text": "My elite resonance course changes outcomes in the real world. Clients feel aligned and testimonials prove it.", "context": {"monetized": True, "audience_present": True}},
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
    framework = AOAG(embedding_backend=args.embedding_backend)
    result = framework.run(input_text, build_context_from_args(args))
    print(json.dumps(result, indent=2 if args.pretty else None, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
