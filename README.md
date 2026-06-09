# 📊 Life Sciences Commercial Analytics Engine

[![License: MIT](https://shields.io)](https://opensource.org)
[![Python: 3.9+](https://shields.io)](https://python.org)

## 🎯 Project Overview
This repository presents an end-to-end data science and engineering architecture tailored to the global life sciences industry.

Designed to emulate a **4–12 week agile analytics engagement**, the project demonstrates how raw, complex healthcare commercial data can be transformed into scalable, high-signal strategic insights that support **Brand Strategy, Patient Analytics, and Sales Operations**.

I plan to continue developing this project to further bridge the gap between rigorous mathematical modeling and business strategy. The ultimate goal is to provide global pharmaceutical leaders with actionable narratives that improve patient access to therapies while maximizing operational efficiency.

All data used in this project comes from the [Centers for Medicare & Medicaid Services \(CMS\)](https://data.cms.gov/provider-summary-by-type-of-service/medicare-part-d-prescribers/medicare-part-d-prescribers-by-geography-and-drug), a U.S. government organization that provides open-access healthcare data for public use. Specifically, this project utilizes publicly available Medicare Part D prescribing data published through the CMS Open Data platform.

---

## 🏗️ Project Architecture & Hierarchy


```text
├── config
│   └── config.yaml                 # Centralized business logic and schema parameters
├── data
│   ├── processed
│   └── raw
│       └── Medicare Part D Prescribers - by Geography and Drug
│           └── 2024
│               ├── MUP_DPR_RY25_20250401_DD_Geo_508.pdf
│               ├── MUP_DPR_RY26_20260421_Methodology_508.pdf
│               ├── MUP_DPR_RY26_P04_V10_DY24_Geo.csv
│               ├── MUP_DPR_RY26_P06_V10_DYT24_DLSum.xlsx
│               └── MUP_DPR_RY26_P06_V10_DYT24_HLSum.xlsx
├── figures
│   └── Therapeutic_brand_market_share_estradiol_indiana.png
├── notebooks
│   └── exploratory_analysis.ipynb  # Executive workspace & pipeline simulation
├── README.md                       # Strategic overview & documentation
└── src
    ├── __init__.py                 # Package initializer
    ├── data_ingestion.py           # Real-world data validation & signal preservation
    ├── patient_analytics.py        # Longitudinal patient journey & adherence modeling
    └── sales_ops.py                # Prescriber market dynamics & brand targeting
```

---

## 🏗️ Pipeline Flow

```text
       [ Messy Real-World Data Sources ]
  (Pharmacy Claims, Prescriber Trends, Payer Schemas)
                         │
                         ▼
        [ src/data_ingestion.py ]
       (Handles anomalies & filters out noise)
                         │
                         ▼
       [ src/patient_analytics.py ]
   (Feature engineering: Adherence & Drop-off rates)
                         │
                         ▼
             [ src/sales_ops.py ]
  (Statistical modeling / Market Share Forecasting)
                         │
                         ▼
     [ notebooks/exploratory_analysis.ipynb ]
  (Strategic narratives for non-technical leadership)
```

---

## 💡 Core Competencies & Implementation

### 🛠️ 1. Real-World Data Mapping & Value Translation (`src/data_ingestion.py`)
*   **The Blueprint:** Reconciles disparate, messy commercial events—such as structured **pharmacy claims, longitudinal patient data, and prescriber trends**—into unified analytics schemas.
*   **The Value:** Converts complex healthcare transaction data into interpretable analytical metrics while filtering data quality issues (such as negative day-supply values or duplicate claim reversals) to preserve meaningful business signals.

### 📐 2. Patient-Centric Analytics Framework (`src/patient_analytics.py`)
*   **The Blueprint:** Tracks the longitudinal patient journey by calculating the industry-standard **Medication Possession Ratio (MPR)** to monitor patient compliance over specific therapy windows.
*   **The Value:** Segments patients into adherence cohorts to identify discontinuation risk, therapy gaps, and potential barriers to treatment access.

### 💼 3. Sales Operations & Market Dynamics (`src/sales_ops.py`)
*   **The Blueprint:** Aggregates multi-brand transactional volumes across complex provider networks to derive relative regional market shares.
*   **The Value:** Provides corporate field teams with clear targeting frameworks by mapping physician prescribing behaviors directly to territory sales strategies.

### 🚀 4. Scalable Infrastructure & Configuration (`config/config.yaml`)
*   **The Blueprint:** Separates business rules from application logic through a YAML-based configuration framework.
*   **The Value:** Enables analysts and consultants to modify business parameters—such as adherence thresholds and analysis windows—without modifying the underlying Python codebase.

---

## 🚀 Getting Started & Execution

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/anupgp/pharma_analytics_engagement.git
cd pharma_analytics_engagement
pip install pandas numpy pyyaml jupyter
```

### 2. Simulating the Analytics Pipeline
To run the full pipeline, execute the exploratory workspace notebook:
```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```
This notebook initializes the `MedicalDataIngestor`, cleans raw transactional noise, evaluates patient adherence trends, and spits out executive market share metrics directly in your local environment.

### 3. 📈 Market Intelligence Report: Estradiol Therapeutic Class Analysis

This case study demonstrates how the Life Sciences Commercial Analytics Engine processes longitudinal CMS prescribing data to identify prescribing patterns, market concentration, and commercial trends within a therapeutic class.

Below is an evaluation of the **Estradiol** (hormone therapy) molecular class market dynamics, generated dynamically via our interactive Bokeh pipeline.

---

## 📊 Market Share Distribution

![Estradiol Market Share Split](https://github.com/anupgp/pharma_analytics_engagement/blob/main/figures/Therapeutic_brand_market_share_estradiol_indiana.png)

---

## 💡 Key Commercial Insights & Brand Strategy

Analyzing the relative market share distribution reveals a classic life sciences product lifecycle narrative:

### 1. The Generic Erosion Cliff
The unbranded generic variant **`Estradiol` dominates the market with nearly 80% relative market share**. The high market share of generic Estradiol suggests a mature therapeutic category in which generic formulations account for the majority of prescription volume. Additional pricing and payer data would be required to determine the specific drivers of generic adoption.

### 2. High-Value Differentiated Formulations
Once-weekly and twice-weekly Estradiol formulations collectively account for approximately 12% of total prescription volume, suggesting that dosing convenience or formulation-specific preferences may contribute to continued utilization despite strong generic competition.

| Drug | Market Share (%) |
|-------|------------------|
| Estradiol | 79.8 |
| Estradiol (Twice Weekly) | 6.2 |
| Estradiol (Once Weekly) | 5.5 |
| Yuvafem | 4.5 |
| Dotti | 1.2 |

### 3. Isolated Niche Branded Footprints
Brands like **`Yuvafem`** (Approx. 4.5% market share) and **`Dotti`** (Approx. 1.2% market share) maintain smaller but measurable market shares. Further geographic and provider-level analyses could help determine whether these products derive their volume from specific prescriber segments, regional preferences, or differentiated clinical positioning.

---

## 🛠️ Data Provenance & Reproducibility
*   **Source Data:** CMS Medicare Part D Prescriber Summary - By Geography and Drug Class.
*   **Pipeline Scope:** Out-of-core chunk aggregation processing multi-gigabyte raw transactional rows.
*   **Execution Abstraction:** 
    ```python
    df_global_insights = analyzer.compute_global_metrics_from_file(full_dataset_path)
    # Visual metrics isolated dynamically via client-side JavaScript engine
    ```


---

## 📄 License
This project is licensed under the terms of the **MIT License**. Feel free to use, modify, and distribute this pipeline infrastructure across open-source or commercial platforms.