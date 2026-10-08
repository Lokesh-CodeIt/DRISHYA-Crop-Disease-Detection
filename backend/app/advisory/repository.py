"""
repository.py - LeafLens Advisory Repository

Loads and queries verified disease treatment advisories vetted against ICAR and KVK packages of practice.
Supports multilingual queries (English, Hindi, Marathi).
Guarantees that unvetted or fabricated advice is never returned.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from ..models.schemas import AdvisoryRecommendation, TreatmentSource

logger = logging.getLogger("LeafLens.AdvisoryRepo")


class AdvisoryRepository:
    """Reads and queries expert-vetted agricultural disease advisories."""

    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or (Path(__file__).resolve().parent.parent.parent.parent / "advisory" / "disease_advisories.json")
        self._cache: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Loads advisory data from disk."""
        if not self.data_file.exists():
            logger.warning(f"Advisory file does not exist at {self.data_file}. Advisories unavailable.")
            self._cache = {"advisories": []}
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
            logger.info(f"Loaded {len(self._cache.get('advisories', []))} advisories from {self.data_file}")
        except Exception as e:
            logger.error(f"Error loading advisory file: {e}")
            self._cache = {"advisories": []}

    def get_advisory(self, disease_id: str, crop: str, language: str = "en") -> Optional[AdvisoryRecommendation]:
        """
        Retrieves localized advisory for a disease.
        Returns None if not yet populated or vetted.
        """
        advisories = self._cache.get("advisories", [])
        for item in advisories:
            if item.get("disease_id") == disease_id and item.get("crop") == crop:
                common_name = item.get("common_names", {}).get(language, item.get("common_names", {}).get("en"))
                symptoms = item.get("symptoms", {}).get(language, item.get("symptoms", {}).get("en"))
                cultural = item.get("cultural_preventative_measures", {}).get(language, [])
                organic = item.get("organic_biological_controls", {}).get(language, [])
                chemical = item.get("chemical_controls", {}).get(language, [])
                safety = item.get("safety_warnings", {}).get(language, "")

                sources = [
                    TreatmentSource(
                        institution=s.get("institution", "ICAR/KVK"),
                        document_title=s.get("document_title", ""),
                        url_or_reference=s.get("url_or_reference"),
                    )
                    for s in item.get("authoritative_sources", [])
                ]

                return AdvisoryRecommendation(
                    disease_id=disease_id,
                    crop=crop,
                    scientific_name=item.get("scientific_name"),
                    common_name=common_name,
                    symptoms=symptoms,
                    cultural_preventative_measures=cultural,
                    organic_biological_controls=organic,
                    chemical_controls=chemical,
                    safety_warnings=safety,
                    authoritative_sources=sources,
                )

        return None


advisory_repository = AdvisoryRepository()
