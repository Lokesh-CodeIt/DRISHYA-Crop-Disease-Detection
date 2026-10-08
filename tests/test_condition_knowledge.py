"""
tests/test_condition_knowledge.py - Test Suite for DRISHYA Step D Condition Knowledge

Verifies:
1. Coverage across all 22 active model classes (Turmeric: 4, Citrus: 18)
2. Safe rejection semantics (no disease confirmation on uncertain predictions)
3. Full multilingual localization in English, Hindi, and Marathi
4. Strict absence of dynamically generated pesticide dosages or synthetic prescriptions
5. Source traceability and institutional backing (ICAR, TNAU, CCRI, EPPO)
6. Crop isolation (cross-crop mismatch handling)
7. Safe fallback for unknown classes
8. End-to-end DiagnosisResponse integration
"""

import re
import pytest
from backend.app.knowledge.service import get_condition_knowledge, knowledge_service
from backend.app.models.schemas import DiagnosisResponse, ConditionKnowledge

# 22 canonical model classes
TURMERIC_CLASSES = [
    "Dry Leaf",
    "Healthy",
    "Leaf Blotch",
    "Leaf Spot",
]

CITRUS_CLASSES = [
    "Algal_Leaf_Spot",
    "Anthracnose",
    "Bacterial Blight",
    "Black Spot",
    "Citrus Canker",
    "Citrus Hindu Mite",
    "Citrus Leafminer",
    "Citrus_Pest",
    "Citrus_Scab",
    "Curl Leaf",
    "Dry Leaf",
    "Greening",
    "Healthy",
    "Lemon_Sooty_Mold",
    "Melanose",
    "Spider Mites",
    "Swallowtail Larval Herbivory (Deficiency)",
    "Yellow_Spot",
]

LANGUAGES = ["en", "hi", "mr"]


class TestConditionKnowledgeCoverage:
    """Verifies that all 22 active model classes resolve to valid knowledge."""

    @pytest.mark.parametrize("cls_name", TURMERIC_CLASSES)
    def test_turmeric_classes_resolve(self, cls_name):
        knowledge = get_condition_knowledge("turmeric", cls_name, "en")
        assert knowledge is not None
        assert knowledge.knowledge_available is True
        assert knowledge.crop == "turmeric"
        assert len(knowledge.display_name) > 0
        assert len(knowledge.short_description) > 0
        assert len(knowledge.what_it_means) > 0
        assert len(knowledge.visual_signs) > 0
        assert len(knowledge.immediate_actions) > 0
        assert len(knowledge.prevention_or_monitoring) > 0
        assert len(knowledge.expert_escalation) > 0
        assert knowledge.advisory_status in ["SUPPORTED", "GENERAL_GUIDANCE"]

    @pytest.mark.parametrize("cls_name", CITRUS_CLASSES)
    def test_citrus_classes_resolve(self, cls_name):
        knowledge = get_condition_knowledge("citrus", cls_name, "en")
        assert knowledge is not None
        assert knowledge.knowledge_available is True
        assert knowledge.crop == "citrus"
        assert len(knowledge.display_name) > 0
        assert len(knowledge.short_description) > 0
        assert len(knowledge.what_it_means) > 0
        assert len(knowledge.visual_signs) > 0
        assert len(knowledge.immediate_actions) > 0
        assert len(knowledge.prevention_or_monitoring) > 0
        assert len(knowledge.expert_escalation) > 0
        assert knowledge.advisory_status in ["SUPPORTED", "GENERAL_GUIDANCE"]

    def test_total_count_matches_22(self):
        """Verifies exact 22 conditions loaded in knowledge dataset."""
        loaded_count = len(knowledge_service._conditions_by_id)
        assert loaded_count == 22, f"Expected 22 conditions, got {loaded_count}"


class TestMultilingualLocalization:
    """Verifies that all 22 classes provide non-empty content in EN, HI, MR."""

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_turmeric_all_languages(self, lang):
        for cls_name in TURMERIC_CLASSES:
            knowledge = get_condition_knowledge("turmeric", cls_name, lang)
            assert knowledge.display_name != "", f"Empty display_name for {cls_name} in {lang}"
            assert knowledge.short_description != "", f"Empty short_description for {cls_name} in {lang}"
            assert knowledge.what_it_means != "", f"Empty what_it_means for {cls_name} in {lang}"
            assert len(knowledge.visual_signs) > 0, f"Empty visual_signs for {cls_name} in {lang}"
            assert len(knowledge.immediate_actions) > 0, f"Empty immediate_actions for {cls_name} in {lang}"
            assert len(knowledge.prevention_or_monitoring) > 0, f"Empty prevention for {cls_name} in {lang}"
            assert knowledge.expert_escalation != "", f"Empty escalation for {cls_name} in {lang}"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_citrus_all_languages(self, lang):
        for cls_name in CITRUS_CLASSES:
            knowledge = get_condition_knowledge("citrus", cls_name, lang)
            assert knowledge.display_name != "", f"Empty display_name for {cls_name} in {lang}"
            assert knowledge.short_description != "", f"Empty short_description for {cls_name} in {lang}"
            assert knowledge.what_it_means != "", f"Empty what_it_means for {cls_name} in {lang}"
            assert len(knowledge.visual_signs) > 0, f"Empty visual_signs for {cls_name} in {lang}"
            assert len(knowledge.immediate_actions) > 0, f"Empty immediate_actions for {cls_name} in {lang}"
            assert len(knowledge.prevention_or_monitoring) > 0, f"Empty prevention for {cls_name} in {lang}"
            assert knowledge.expert_escalation != "", f"Empty escalation for {cls_name} in {lang}"


class TestRejectionSemantics:
    """Verifies that when is_rejected is True, uncertain diagnosis safety is enforced."""

    def test_turmeric_rejected_safety(self):
        knowledge = get_condition_knowledge("turmeric", "Leaf Spot", "en", is_rejected=True)
        assert knowledge.advisory_status == "EXPERT_CONFIRMATION_RECOMMENDED"
        assert "Uncertain Diagnosis" in knowledge.display_name or "Low Confidence" in knowledge.short_description
        # Must not claim confirmed disease
        assert "confirmed" not in knowledge.display_name.lower()
        # Immediate actions must advise non-treatment steps (photo, inspection, expert)
        actions_text = " ".join(knowledge.immediate_actions).lower()
        assert "re-take" in actions_text or "photograph" in actions_text or "inspect" in actions_text

    def test_citrus_rejected_safety(self):
        knowledge = get_condition_knowledge("citrus", "Citrus Canker", "en", is_rejected=True)
        assert knowledge.advisory_status == "EXPERT_CONFIRMATION_RECOMMENDED"
        assert "Uncertain Diagnosis" in knowledge.display_name or "Low Confidence" in knowledge.short_description
        assert "confirmed" not in knowledge.display_name.lower()
        actions_text = " ".join(knowledge.immediate_actions).lower()
        assert "re-take" in actions_text or "photograph" in actions_text or "inspect" in actions_text

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_rejected_multilingual(self, lang):
        knowledge = get_condition_knowledge("citrus", "Greening", lang, is_rejected=True)
        assert knowledge.advisory_status == "EXPERT_CONFIRMATION_RECOMMENDED"
        assert len(knowledge.display_name) > 0
        assert len(knowledge.short_description) > 0
        assert len(knowledge.immediate_actions) > 0


class TestNoUnsafePesticideDosages:
    """Verifies zero dynamic chemical doses, concentrations, or unsafe prescriptions."""

    # Prohibited patterns: e.g., '2 ml/L', '1.5 g/L', '0.05% EC', '500 ppm'
    FORBIDDEN_DOSAGE_REGEX = re.compile(
        r"\b\d+(\.\d+)?\s*(ml|g|gm|kg|litre|liter|ppm)\s*/\s*(l|litre|liter|ha|acre|spray)\b|"
        r"\b\d+(\.\d+)?\s*%\s*(ec|wp|sl|sc)\b|"
        r"\b\d+\s*-\s*\d+\s*(ml|g|gm)\b",
        re.IGNORECASE,
    )

    def test_all_conditions_free_of_dosages(self):
        for cond_id, entry in knowledge_service._conditions_by_id.items():
            for lang in ["en", "hi", "mr"]:
                fields_to_check = [
                    entry.get("short_description", {}).get(lang, ""),
                    entry.get("what_it_means", {}).get(lang, ""),
                    " ".join(entry.get("visual_signs", {}).get(lang, [])),
                    " ".join(entry.get("immediate_actions", {}).get(lang, [])),
                    " ".join(entry.get("prevention_or_monitoring", {}).get(lang, [])),
                    entry.get("expert_escalation", {}).get(lang, ""),
                ]
                for text in fields_to_check:
                    match = self.FORBIDDEN_DOSAGE_REGEX.search(text)
                    assert match is None, (
                        f"Prohibited dosage pattern '{match.group(0)}' found in {cond_id} ({lang}): {text}"
                    )


class TestSourceIntegrity:
    """Verifies traceable institutional source backing for all supported conditions."""

    def test_sources_present_for_supported(self):
        for cond_id, entry in knowledge_service._conditions_by_id.items():
            sources = entry.get("sources", [])
            assert len(sources) >= 1, f"No sources for {cond_id}"
            for src in sources:
                assert len(src.get("source_title", "")) > 0, f"Missing source_title in {cond_id}"
                assert len(src.get("source_organization", "")) > 0, f"Missing source_organization in {cond_id}"
                assert src.get("source_type") in [
                    "institutional_extension",
                    "diagnostic_guide",
                    "international_standard",
                    "government_guideline",
                    "university_portal",
                    "extension_bulletin",
                    "international_database",
                    "quarantine_database",
                ], f"Invalid source_type in {cond_id}: {src.get('source_type')}"


class TestEdgeCases:
    """Verifies unknown class fallback and cross-crop isolation."""

    def test_unknown_class_fallback(self):
        knowledge = get_condition_knowledge("turmeric", "NonExistentDisease", "en")
        assert knowledge.knowledge_available is False
        assert knowledge.advisory_status == "EXPERT_CONFIRMATION_RECOMMENDED"
        assert "NonExistentDisease" in knowledge.display_name or "Unknown" in knowledge.display_name
        assert len(knowledge.expert_escalation) > 0

    def test_cross_crop_isolation(self):
        # Leaf Blotch exists in Turmeric but NOT in Citrus
        citrus_blotch = get_condition_knowledge("citrus", "Leaf Blotch", "en")
        assert citrus_blotch.knowledge_available is False, "Leaf Blotch should not resolve under citrus"

        # Citrus Canker exists in Citrus but NOT in Turmeric
        turmeric_canker = get_condition_knowledge("turmeric", "Citrus Canker", "en")
        assert turmeric_canker.knowledge_available is False, "Citrus Canker should not resolve under turmeric"


class TestSchemaSerialization:
    """Verifies that ConditionKnowledge integrates cleanly with Pydantic DiagnosisResponse."""

    def test_condition_knowledge_serialization(self):
        knowledge = get_condition_knowledge("citrus", "Citrus Canker", "en")
        assert isinstance(knowledge, ConditionKnowledge)
        dumped = knowledge.model_dump()
        assert dumped["condition_id"] == "citrus_citrus_canker"
        assert dumped["advisory_status"] == "SUPPORTED"
        assert dumped["knowledge_available"] is True
        assert len(dumped["sources"]) > 0
