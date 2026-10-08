# LeafLens: Citrus Class Taxonomy & Phytopathological Categorization
## Phase 3 Dataset Curation

This report documents the official phytopathological taxonomy for all 18 classes in the primary citrus dataset:
**Large-Scale Lemon Leaf Disease and Pest Image Data**.

In accordance with LeafLens clinical curation guidelines:
1. All 18 original classes and folder names are **strictly preserved** without alteration.
2. Every class is annotated with an orthogonal metadata field: `condition_type`.
3. Allowed values for `condition_type`:
   - `disease` (Bacterial, Fungal, or Algal plant pathogens)
   - `pest` (Insect, Arachnid, or Larval arthropod infestations)
   - `deficiency_or_stress` (Nutritional deficiency, moisture stress, or abiotic physiological disorders)
   - `healthy` (Normal asymptomatic foliage)

---

### Comprehensive 18-Class Taxonomy Table

| Class # | Original Source Class Label | condition_type | Causal Agent / Botanical Classification | Pathogen / Pest Scientific Name | Phytopathological Evidence & Diagnostic Presentation |
|---------|-----------------------------|----------------|-----------------------------------------|--------------------------------|------------------------------------------------------|
| 1 | `Algal_Leaf_Spot` | disease | Parasitic Green Alga | *Cephaleuros virescens* | Circular velvety orange-brown to grey-green spots on upper leaf surfaces. Common in warm humid citrus groves. |
| 2 | `Anthracnose` | disease | Ascomycete Fungus | *Colletotrichum gloeosporioides* | Brown to black foliar necrotic lesions, often with concentric rings of acervuli (fruiting bodies). Frequently initiates from leaf margins. |
| 3 | `Bacterial Blight` | disease | Gram-negative Bacterium | *Pseudomonas syringae* pv. *syringae* | Black-brown necrotic lesions along veins and petioles, water-soaked appearance leading to rapid shoot and foliar collapse. |
| 4 | `Black Spot` | disease | Fungal Pathogen | *Phyllosticta citricarpa* (*Guignardia citricarpa*) | Round, sunken dark brown to black necrotic spots with elevated margins and yellow halos. Quarantined international citrus disease. |
| 5 | `Citrus Canker` | disease | Bacterial Pathogen | *Xanthomonas axonopodis* pv. *citri* | Raised, corky, blister-like brown pustules surrounded by prominent chlorotic yellow halos on both leaf surfaces. |
| 6 | `Citrus Hindu Mite` | pest | Phytophagous Spider Mite | *Schizotetranychus hindustanicus* | Punctate stippling, chlorotic feeding lesions, and dense webbing nests on the lower leaf epidermis. |
| 7 | `Citrus Leafminer` | pest | Lepidopteran Micro-moth Larva | *Phyllocnistis citrella* | Characteristic serpentine silvery translucent tunnels/mines etched inside the leaf parenchyma, leading to leaf distortion and curling. |
| 8 | `Citrus_Pest` | pest | Mixed Arthropod Complex | *Aphidoidea* / *Coccoidea* / *Thripidae* | Generalized insect feeding, piercing-sucking puncture marks, foliar distortion, or superficial mechanical chewing damage. |
| 9 | `Citrus_Scab` | disease | Fungal Pathogen | *Elsinoë fawcettii* | Corky, wart-like conical or irregular excrescences on young leaves and twigs, causing puckering and leaf distortion. |
| 10 | `Curl Leaf` | deficiency_or_stress | Abiotic Stress / Physiological | Moisture Stress / Viral Distortions | Severe upward or downward epinastic leaf rolling caused by water stress, high vapor pressure deficits, or root zone dysfunction. |
| 11 | `Dry Leaf` | deficiency_or_stress | Abiotic Environmental Stress | Desiccation / Hyperthermia | Leaf senescence, severe drought desiccation, marginal scorching, and brittle foliar necrosis. |
| 12 | `Greening` | disease | Fastidious Bacterial Endophyte | *Candidatus* Liberibacter asiaticus (HLB) | Asymmetrical blotchy foliar mottle, vein yellowing, zinc-like deficiency patterns. Transmitted by the Asian citrus psyllid (*Diaphorina citri*). |
| 13 | `Healthy` | healthy | Normal Foliage | Asymptomatic | Vibrant, turgid, uniformly dark-green foliage devoid of lesions, stippling, or chlorosis. |
| 14 | `Lemon_Sooty_Mold` | disease | Epiphytic Ascomycete Fungus | *Capnodium citri* / *Chaetothyrium* spp. | Black superficial velvety fungal crust on upper leaf surfaces. Non-parasitic but severely impairs photosynthesis; grows on insect honeydew. |
| 15 | `Melanose` | disease | Fungal Pathogen | *Diaporthe citri* | Minute dark brown to black raised pustules with rough sandpaper texture on leaves and twigs, typically originating from dead wood inocula. |
| 16 | `Spider Mites` | pest | Arachnid Acari | *Tetranychus urticae* / *Panonychus citri* | Fine chlorotic stippling along leaf midribs, loss of chlorophyll, pale grey cast to foliage, accompanied by fine silken webbing. |
| 17 | `Swallowtail Larval Herbivory (Deficiency)` | pest | Butterfly Larva (Caterpillar) | *Papilio demoleus* / *Papilio cresphontes* | Massive marginal foliar chewing defoliation where large portions of leaf blades are eaten down to the midrib by swallowtail caterpillars. |
| 18 | `Yellow_Spot` | deficiency_or_stress | Nutritional Deficiency | Molybdenum (Mo) Deficiency | Large round, interveinal bright yellow chlorotic spots on leaves, with gummy brown exudate on the abaxial surface in severe stages. |

---

### Condition Type Breakdown

| condition_type | Number of Classes | Classes | Total Raw Images |
|----------------|-------------------|---------|------------------|
| **disease** | 8 | `Algal_Leaf_Spot`, `Anthracnose`, `Bacterial Blight`, `Black Spot`, `Citrus Canker`, `Citrus_Scab`, `Greening`, `Lemon_Sooty_Mold`, `Melanose` *(Note: 9 classes total)* | 9,482 |
| **pest** | 5 | `Citrus Hindu Mite`, `Citrus Leafminer`, `Citrus_Pest`, `Spider Mites`, `Swallowtail Larval Herbivory (Deficiency)` | 3,576 |
| **deficiency_or_stress** | 3 | `Curl Leaf`, `Dry Leaf`, `Yellow_Spot` | 2,913 |
| **healthy** | 1 | `Healthy` | 1,638 |
| **TOTAL** | **18** | | **17,586** |

*(Note: Disease has 9 distinct pathogen classes; pest has 5; deficiency/stress has 3; healthy has 1. 9+5+3+1 = 18 classes).*
