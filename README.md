# 📊 Life Sciences Commercial Analytics Engine

[![License: MIT](https://shields.io)](https://opensource.org)
[![Python: 3.9+](https://shields.io)](https://python.org)

## 🎯 Project Overview
This repository showcases an end-to-end data science and engineering architecture tailored specifically for the global life sciences sector. Built to mirror a high-velocity, **4–12 week agile analytics engagement**, this project demonstrates how to transform raw, complex commercial health transactions into scalable, high-signal strategic insights that optimize **Brand Strategy, Patient Analytics, and Sales Operations**.

By bridging the gap between rigorous mathematical modeling and corporate strategy, this decoupled pipeline provides global pharmaceutical leaders with the actionable narratives required to improve patient access to therapies and maximize operational efficiency.

---

## 🏗️ Project Architecture & Hierarchy

```text
├── config
│   └── config.yaml                 # Centralized business logic and schema parameters
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
*   **The Value:** Converts complex data realities into clear, intuitive metrics while filtering out transactional noise (such as negative day-supply entries or duplicate reversals) to preserve pure business signals.

### 📐 2. Patient-Centric Analytics Framework (`src/patient_analytics.py`)
*   **The Blueprint:** Tracks the longitudinal patient journey by calculating the industry-standard **Medication Possession Ratio (MPR)** to monitor patient compliance over specific therapy windows.
*   **The Value:** Categorizes patient groups into structured compliance cohorts, highlighting drop-off risks and identifying patient access bottlenecks for commercial brand teams.

### 💼 3. Sales Operations & Market Dynamics (`src/sales_ops.py`)
*   **The Blueprint:** Aggregates multi-brand transactional volumes across complex provider networks to derive relative regional market shares.
*   **The Value:** Provides corporate field teams with clear targeting frameworks by mapping physician prescribing behaviors directly to territory sales strategies.

### 🚀 4. Scalable Infrastructure & Configuration (`config/config.yaml`)
*   **The Blueprint:** Segregates engineering code from changing financial boundaries by implementing a yaml-driven parameter core.
*   **The Value:** Allows non-engineering consultants to dynamically modify critical rules—such as adherence threshold barriers or timeline boundaries—without changing underlying python systems.

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

This case study demonstrates the capability of the **Life Sciences Commercial Analytics Engine** to ingest massive, un-sampled federal longitudinal datasets and extract actionable commercial narratives. 

Below is an evaluation of the **Estradiol** (hormone therapy) molecular class market dynamics, generated dynamically via our interactive Bokeh pipeline.

---

## 📊 Market Share Distribution

![Estradiol Market Share Split](https://github.com/anupgp/pharma_analytics_engagement/blob/main/figures/Therapeutic_brand_market_share_estradiol_indiana.png)

---

## 💡 Key Commercial Insights & Brand Strategy

Analyzing the relative market share distribution reveals a classic life sciences product lifecycle narrative:

### 1. The Generic Erosion Cliff
The unbranded generic variant **`Estradiol` dominates the market with nearly 80% relative market share**. This indicates a highly mature therapeutic category where aggressive price-matching and insurance payer preferences have effectively commoditized standard formulations, severely eroding legacy brands like *Climara*, *Divigel*, and *Estrace*.

### 2. High-Value Differentiated Formulations
Despite massive generic erosion, specialized branded variations manage to maintain a resilient commercial foothold:
*   **`Estradiol (Once Weekly)`** (Approx. 5.5% market share)
*   **`Estradiol (Twice Weekly)`** (Approx. 6.2% market share)

**Strategic Takeaway:** In life sciences consulting, this proves that **extended-release delivery mechanisms** or patch formulations create unique patient adherence advantages. Payer and provider loyalty remains high for these premium assets because they reduce dosing frequency, allowing manufacturers to maintain high margins despite cheap generic daily alternatives.

### 3. Isolated Niche Branded Footprints
Brands like **`Yuvafem`** (Approx. 4.5% market share) and **`Dotti`** (Approx. 1.2% market share) continue to capture narrow segments. This suggests targeted territory sales alignment or specific institutional hospital formularies where these niche products are actively insulated from open market competition.

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