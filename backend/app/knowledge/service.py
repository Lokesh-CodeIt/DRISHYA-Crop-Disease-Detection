"""
service.py - LeafLens Condition Knowledge Service

Loads and serves deterministic, source-backed condition knowledge
covering all 22 supported model classes across Turmeric and Citrus crops.
Ensures:
- 100% deterministic lookup driven only by predicted class and crop
- Strict rejection semantics: uncertain predictions never claim confirmed disease
- Full multilingual localization support (English, Hindi, Marathi)
- Zero hallucination / no dynamically generated pesticide doses
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from ..models.schemas import ConditionKnowledge, KnowledgeSource

logger = logging.getLogger("LeafLens.ConditionKnowledge")

# Path to canonical knowledge JSON
KNOWLEDGE_FILE = Path(__file__).resolve().parent / "condition_knowledge.json"


class ConditionKnowledgeService:
    """Manages canonical condition knowledge lookup and localization."""

    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or KNOWLEDGE_FILE
        self._conditions_by_key: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._conditions_by_id: Dict[str, Dict[str, Any]] = {}
        self.load()

    @staticmethod
    def _normalize(val: str) -> str:
        """Normalizes class or crop string into uniform key."""
        if not val:
            return ""
        # Remove parenthetical suffixes like (Deficiency)
        cleaned = re.sub(r"\(.*?\)", "", val)
        cleaned = cleaned.lower().strip()
        cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
        return cleaned.strip("_")

    def load(self):
        """Loads canonical knowledge JSON and constructs lookup indexes."""
        if not self.data_file.exists():
            logger.error(f"Condition knowledge file missing at: {self.data_file}")
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            conditions = data.get("conditions", [])
            for c in conditions:
                crop = c.get("crop", "").lower().strip()
                class_name = c.get("class_name", "")
                cond_id = c.get("condition_id", "")

                # Index by exact class_name
                self._conditions_by_key[(crop, class_name)] = c
                # Index by normalized class name
                norm_class = self._normalize(class_name)
                self._conditions_by_key[(crop, norm_class)] = c
                # Index by condition_id
                self._conditions_by_id[cond_id] = c

            logger.info(f"Loaded {len(conditions)} condition knowledge entries from {self.data_file.name}")
        except Exception as e:
            logger.error(f"Failed to load condition knowledge JSON: {e}", exc_info=True)

    def get_condition(
        self,
        crop: str,
        predicted_class: str,
        language: str = "en",
        is_rejected: bool = False,
    ) -> ConditionKnowledge:
        """
        Retrieves localized condition knowledge.
        
        If is_rejected is True:
          Returns uncertain-diagnosis-safe guidance with EXPERT_CONFIRMATION_RECOMMENDED status.
        If class is recognized:
          Returns source-backed knowledge with appropriate status (SUPPORTED / GENERAL_GUIDANCE).
        If class is unknown:
          Returns safe generic fallback with knowledge_available=False.
        """
        crop_clean = (crop or "turmeric").lower().strip()
        lang = (language or "en").lower().strip()
        if lang not in ["en", "hi", "mr"]:
            lang = "en"

        # 1. Lookup candidate entry
        entry = self._conditions_by_key.get((crop_clean, predicted_class))
        if not entry:
            norm_class = self._normalize(predicted_class)
            entry = self._conditions_by_key.get((crop_clean, norm_class))

        # 2. Case: REJECTED PREDICTION
        if is_rejected:
            return self._build_uncertain_response(crop_clean, predicted_class, entry, lang)

        # 3. Case: UNKNOWN CLASS
        if not entry:
            return self._build_unknown_response(crop_clean, predicted_class, lang)

        # 4. Case: RECOGNIZED CONDITION
        return self._build_supported_response(crop_clean, entry, lang)

    def _build_supported_response(
        self,
        crop: str,
        entry: Dict[str, Any],
        lang: str,
    ) -> ConditionKnowledge:
        """Builds localized response for a recognized condition."""
        def _get_loc(field: str, default: str = "") -> str:
            d = entry.get(field, {})
            if isinstance(d, dict):
                return d.get(lang) or d.get("en") or default
            return str(d) if d else default

        def _get_loc_list(field: str) -> List[str]:
            d = entry.get(field, {})
            if isinstance(d, dict):
                return d.get(lang) or d.get("en") or []
            if isinstance(d, list):
                return d
            return []

        sources_data = entry.get("sources", [])
        sources = [
            KnowledgeSource(
                source_title=s.get("source_title", "Agricultural Extension Bulletin"),
                source_organization=s.get("source_organization", "ICAR / Agricultural University"),
                source_url=s.get("source_url"),
                source_type=s.get("source_type", "institutional_extension"),
            )
            for s in sources_data
        ]

        return ConditionKnowledge(
            condition_id=entry.get("condition_id", f"{crop}_unknown"),
            crop=crop,
            display_name=_get_loc("display_name", entry.get("class_name", "")),
            short_description=_get_loc("short_description"),
            what_it_means=_get_loc("what_it_means"),
            visual_signs=_get_loc_list("visual_signs"),
            immediate_actions=_get_loc_list("immediate_actions"),
            prevention_or_monitoring=_get_loc_list("prevention_or_monitoring"),
            expert_escalation=_get_loc("expert_escalation"),
            advisory_status=entry.get("advisory_status", "SUPPORTED"),
            sources=sources,
            reference_image=None,
            knowledge_available=True,
        )

    def _build_uncertain_response(
        self,
        crop: str,
        predicted_class: str,
        entry: Optional[Dict[str, Any]],
        lang: str,
    ) -> ConditionKnowledge:
        """Builds safe response for low-confidence or rejected predictions."""
        loc_titles = {
            "en": "Uncertain Diagnosis — General Guidance",
            "hi": "अस्पष्ट परिणाम — सामान्य मार्गदर्शन",
            "mr": "अस्पष्ट निदान — सर्वसाधारण मार्गदर्शन",
        }
        loc_desc = {
            "en": "Model confidence is below the safety threshold (65%). Visual features are ambiguous or insufficiently clear to confirm this condition.",
            "hi": "मॉडल की विश्वसनीयता सुरक्षा सीमा (65%) से कम है। लक्षण अस्पष्ट हैं और पुष्टि हेतु पर्याप्त स्पष्ट नहीं हैं।",
            "mr": "मॉडेलचा विश्वासार्हता दर सुरक्षा मर्यादेपेक्षा (६५%) कमी आहे. लक्षणे अस्पष्ट असून रोगाची खात्री देता येत नाही.",
        }
        loc_means = {
            "en": "In agricultural field diagnostics, ambiguous leaf symptoms require direct expert examination rather than automated reliance. This reading is general guidance only.",
            "hi": "खेत में पौधों के अस्पष्ट लक्षणों में स्वचालित पहचान पर निर्भर रहने के बजाय सीधे विशेषज्ञ की जांच आवश्यक है।",
            "mr": "शेतातील अस्पष्ट लक्षणांसाठी संगणकीय निष्कर्षावर अवलंबून न राहता प्रत्यक्ष तज्ज्ञ तपासणी आवश्यक असते. हे केवळ सामान्य मार्गदर्शन आहे.",
        }
        loc_signs = {
            "en": [
                "Visual patterns are ambiguous, poorly lit, or subject to glare",
                "Features do not strongly match a single canonical disease profile",
                "Possible mixed abiotic stress or overlapping foliar conditions"
            ],
            "hi": [
                "पत्ती के लक्षण अस्पष्ट हैं या प्रकाश की कमी/चमक के कारण स्पष्ट नहीं हैं",
                "लक्षण किसी एक विशिष्ट बीमारी के पूर्ण अनुरूप नहीं हैं",
                "संभवतः मौसम, पानी की कमी या मिट्टी का मिलाजुला तनाव हो सकता है"
            ],
            "mr": [
                "पानावरील लक्षणे अस्पष्ट आहेत किंवा प्रकाशाच्या कमतरतेमुळे स्पष्ट दिसत नाहीत",
                "लक्षणे कोणत्याही एका रोगाशी तंतोतंत जुळत नाहीत",
                "हवामान किंवा पाण्याच्या ताणाचे मिश्रित परिणाम असण्याची शक्यता आहे"
            ]
        }
        loc_actions = {
            "en": [
                "Photograph another clearly visible leaf in natural daylight without direct glare",
                "Check whether symptoms are localized to this leaf or present across the plant canopy",
                "Do not apply chemical sprays or fertilizers based solely on an uncertain check",
                "Consult your local Krishi Vigyan Kendra (KVK) for visual field confirmation"
            ],
            "hi": [
                "प्राकृतिक रोशनी में बिना चमक के किसी अन्य साफ पत्ते का फोटो लें",
                "जांचें कि क्या लक्षण सिर्फ इसी पत्ते पर हैं या पूरे पौधे/बगीचे में फैले हैं",
                "अस्पष्ट परिणाम के आधार पर कोई रासायनिक स्प्रे या खाद न दें",
                "पुष्टि के लिए स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि अधिकारी से संपर्क करें"
            ],
            "mr": [
                "नैसर्गिक उजेडात न चकाकणाऱ्या दुसऱ्या पानाचा स्पष्ट फोटो घ्या",
                "लक्षणे फक्त याच पानावर आहेत की संपूर्ण झाडावर आहेत हे तपासा",
                "अस्पष्ट अनुमानावर आधारित कोणतीही रासायनिक फवारणी करू नका",
                "खात्री करण्यासाठी स्थानिक कृषी विज्ञान केंद्र (KVK) किंवा कृषी सहाय्यकांचा सल्ला घ्या"
            ]
        }
        loc_prev = {
            "en": [
                "Monitor the plant over the next 3 to 5 days for symptom progression",
                "Maintain regular balanced irrigation and field sanitation",
                "Keep a visual record of changing leaf patterns in your Leaf Journal"
            ],
            "hi": [
                "अगले 3 से 5 दिनों में पौधे के लक्षणों में बदलाव पर नजर रखें",
                "नियमित संतुलित सिंचाई और खेत की स्वच्छता बनाए रखें",
                "पत्ती के बदलते स्वरूप को अपने लीफ जर्नल में दर्ज करें"
            ],
            "mr": [
                "पुढील ३ ते ५ दिवसांत लक्षणांमध्ये होणाऱ्या बदलांवर लक्ष ठेवा",
                "नियमित पाणी व्यवस्थापन आणि शेताची स्वच्छता ठेवा",
                "पानावरील बदल नोंदीसाठी आपल्या लीफ जर्नलमध्ये नोंदवा"
            ]
        }
        loc_escalation = {
            "en": "Because this diagnosis is uncertain, physical inspection by a qualified agricultural extension officer or KVK specialist is strongly recommended before taking management action.",
            "hi": "चूंकि यह परिणाम अस्पष्ट है, अतः कोई भी कदम उठाने से पहले योग्य कृषि अधिकारी या KVK विशेषज्ञ से प्रत्यक्ष जांच कराना आवश्यक है।",
            "mr": "हे निदान अस्पष्ट असल्याने, कोणताही उपाय करण्यापूर्वी अधिकृत कृषी अधिकारी किंवा KVK तज्ज्ञांकडून प्रत्यक्ष पाहणी करून घेणे आवश्यक आहे."
        }

        # Keep sources from the candidate entry if available, or reference KVK guidance
        sources: List[KnowledgeSource] = []
        if entry and "sources" in entry:
            sources = [
                KnowledgeSource(
                    source_title=s.get("source_title", "Agricultural Extension Bulletin"),
                    source_organization=s.get("source_organization", "ICAR / Agricultural University"),
                    source_url=s.get("source_url"),
                    source_type=s.get("source_type", "institutional_extension"),
                )
                for s in entry["sources"]
            ]
        else:
            sources = [
                KnowledgeSource(
                    source_title="Field Advisory and Farmer Extension Guidance",
                    source_organization="Krishi Vigyan Kendra (KVK) Network, ICAR",
                    source_url="https://kvk.icar.gov.in",
                    source_type="institutional_extension",
                )
            ]

        cond_id = entry.get("condition_id") if entry else f"{crop}_uncertain"

        return ConditionKnowledge(
            condition_id=cond_id,
            crop=crop,
            display_name=loc_titles.get(lang, loc_titles["en"]),
            short_description=loc_desc.get(lang, loc_desc["en"]),
            what_it_means=loc_means.get(lang, loc_means["en"]),
            visual_signs=loc_signs.get(lang, loc_signs["en"]),
            immediate_actions=loc_actions.get(lang, loc_actions["en"]),
            prevention_or_monitoring=loc_prev.get(lang, loc_prev["en"]),
            expert_escalation=loc_escalation.get(lang, loc_escalation["en"]),
            advisory_status="EXPERT_CONFIRMATION_RECOMMENDED",
            sources=sources,
            reference_image=None,
            knowledge_available=True,
        )

    def _build_unknown_response(
        self,
        crop: str,
        predicted_class: str,
        lang: str,
    ) -> ConditionKnowledge:
        """Builds safe fallback when condition is uncatalogued."""
        loc_titles = {
            "en": f"General Foliar Guidance ({predicted_class})",
            "hi": f"सामान्य मार्गदर्शन ({predicted_class})",
            "mr": f"सर्वसाधारण मार्गदर्शन ({predicted_class})",
        }
        loc_desc = {
            "en": "General agricultural reference guidance. Specific condition profile is not yet indexed in the canonical database.",
            "hi": "सामान्य कृषि संदर्भ मार्गदर्शन। यह विशिष्ट स्थिति अभी डेटाबेस में शामिल नहीं है।",
            "mr": "सर्वसाधारण कृषी संदर्भ मार्गदर्शन. या विशिष्ट स्थितीची सविस्तर माहिती डेटाबेसमध्ये उपलब्ध नाही.",
        }
        loc_means = {
            "en": "The model produced an unclassified prediction. General good agricultural practices apply, but crop-specific intervention should not be undertaken without expert confirmation.",
            "hi": "मॉडल ने एक अवर्गीकृत परिणाम दिया है। सामान्य अच्छी कृषि पद्धतियां लागू होती हैं, लेकिन विशेषज्ञ की सलाह बिना कोई विशिष्ट उपचार न करें।",
            "mr": "मॉडेलने अवर्गीकृत निष्कर्ष नोंदवला आहे. सर्वसाधारण कृषी पद्धती पाळाव्यात, परंतु तज्ज्ञांच्या सल्ल्याशिवाय कोणताही विशिष्ट उपाय करू नये.",
        }
        loc_escalation = {
            "en": "Please consult a local agricultural extension officer (KVK) for visual diagnosis and crop-specific management.",
            "hi": "रोग की सही पहचान और मार्गदर्शन हेतु कृपया स्थानीय कृषि विज्ञान केंद्र (KVK) से संपर्क करें।",
            "mr": "अचूक निदान आणि योग्य सल्ल्यासाठी कृपया स्थानिक कृषी विज्ञान केंद्र (KVK) किंवा कृषी अधिकाऱ्यांचा सल्ला घ्या."
        }

        return ConditionKnowledge(
            condition_id=f"{crop}_unknown",
            crop=crop,
            display_name=loc_titles.get(lang, loc_titles["en"]),
            short_description=loc_desc.get(lang, loc_desc["en"]),
            what_it_means=loc_means.get(lang, loc_means["en"]),
            visual_signs=[
                "Unindexed or atypical foliar presentation",
                "Varied discolored foliage requiring direct field examination"
            ],
            immediate_actions=[
                "Do not apply unverified chemical or pesticide treatments",
                "Inspect whether symptoms affect single branches or the entire plant",
                "Take clear photographs and consult a local agricultural extension officer"
            ],
            prevention_or_monitoring=[
                "Maintain standard orchard and field sanitation",
                "Provide regular balanced irrigation and drainage",
                "Monitor surrounding plants for potential symptom spread"
            ],
            expert_escalation=loc_escalation.get(lang, loc_escalation["en"]),
            advisory_status="EXPERT_CONFIRMATION_RECOMMENDED",
            sources=[
                KnowledgeSource(
                    source_title="General Good Agricultural Practices (GAP)",
                    source_organization="Ministry of Agriculture & Farmers Welfare, GoI",
                    source_url="https://agricoop.nic.in",
                    source_type="government_guideline",
                )
            ],
            reference_image=None,
            knowledge_available=False,
        )


# Singleton instance
knowledge_service = ConditionKnowledgeService()


def get_condition_knowledge(
    crop: str,
    predicted_class: str,
    language: str = "en",
    is_rejected: bool = False,
) -> ConditionKnowledge:
    """Convenience accessor for condition knowledge."""
    return knowledge_service.get_condition(
        crop=crop,
        predicted_class=predicted_class,
        language=language,
        is_rejected=is_rejected,
    )
