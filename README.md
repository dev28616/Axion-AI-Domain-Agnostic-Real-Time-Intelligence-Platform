# 🚀 Project Axion AI

### A domain-agnostic, multi-agent, high-performance platform for real-time intelligence.

This repository contains the complete **"Golden Master" MVP** for **Axion AI** — a fully containerized, microservices-based system that can ingest, analyze, and act on real-time data from multiple domains (e.g., Finance, Logistics) simultaneously, delivering AI-driven decisions in seconds.

---

## 🎬 Interactive Demo (Most Important Part)

> **Author’s Note:**  
> Record and embed a short GIF here showing the UI in action — selecting the **"Finance"** domain, clicking **"Start Pipeline"**, and seeing **real-time decisions** appear.  
> This is the “wow” factor that proves your project works.

---

## 🧠 1. The Core Vision: Solving the “Decision Latency Gap”

### ❌ The Problem
Enterprises are drowning in data but starving for insight.  
The time between a critical event happening and an intelligent decision being made is often measured in **hours** — this **“decision latency gap”** leads to risk and lost revenue.

### ✅ The Solution
**Axion AI** acts as an **Operating System for Real-Time Intelligence**.

Instead of a single-purpose pipeline, Axion provides:
- A **Core Engine** of autonomous agents, and
- A **Domain Solution Pack (DSP)** model.

This allows instant adaptation to any domain — from **financial fraud prevention** to **supply chain spoilage prediction** — simply by plugging in a new DSP.

---

## ⚙️ 2. Key Features

| Feature | Description |
|----------|--------------|
| **Domain-Agnostic Architecture** | A fully generic "Core Engine" can run pipelines for any domain (Finance, Logistics, Healthcare) in parallel. |
| **High-Performance & Low-Latency** | A decoupled Model Server and aiohttp-based Enrichment Agent ensure sub-second processing. |
| **Resilient & Stable** | Deterministic startup sequence using Docker health checks eliminates race conditions. |
| **Self-Healing Backend** | Supervisor automatically restarts crashed agents — zero downtime. |
| **Trustworthy AI** | MLOps workflow generates a *Model Trust Score* (Accuracy, Precision, Recall) visible in the UI. |
| **Fully Interactive UI** | Streamlit dashboard for real-time, color-coded decision display. |

---

## 🧩 3. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph User & UI
        UI_HUB["🚀 Interactive UI Hub<br/>(Streamlit)"]:::uiStyle
    end

    subgraph Kafka Event Bus (The "Nervous System")
        direction LR
        KAFKA_INPUT(("[user-input-events]")):::kafkaStyle
        KAFKA_RAW(("[domain-raw-events]")):::kafkaStyle
        KAFKA_ANALYTICS(("[domain-analytics-results]")):::kafkaStyle
        KAFKA_DECISIONS(("[domain-decisions]")):::kafkaStyle
    end

    subgraph "Axion Core Engine (Always-On Backend)"
        subgraph "Central Services (The 'Brain')"
            MODEL_SERVER["Model Server (FastAPI)<br/>- NER Model<br/>- Vector Model"]:::serviceStyle
        end

        subgraph "Autonomous Agents (The 'Workers')"
            INGESTION["Ingestion Agent<br/>(Smart Router)"]:::agentStyle
            ENRICHMENT["Enrichment Agent<br/>(AI & .joblib Models)"]:::agentStyle
            DECISION["Decision Agent<br/>(Rule Engine)"]:::agentStyle
        end
    end

    UI_HUB -- "1. User Submits Data" --> KAFKA_INPUT
    KAFKA_INPUT -- "2. Consumes Input" --> INGESTION
    INGESTION -- "3. Routes to Domain" --> KAFKA_RAW
    KAFKA_RAW -- "4. Consumes Raw Event" --> ENRICHMENT
    ENRICHMENT -- "5. Async API Call<br/>(PII Mask, Vectorize)" --> MODEL_SERVER
    MODEL_SERVER -- "6. AI Results" --> ENRICHMENT
    ENRICHMENT -- "7. Produces Enriched Result" --> KAFKA_ANALYTICS
    KAFKA_ANALYTICS -- "8. Consumes Enriched Result" --> DECISION
    DECISION -- "9. Produces Final Decision" --> KAFKA_DECISIONS
    KAFKA_DECISIONS -- "10. Consumes for Display" --> UI_HUB

    %% Styling
    classDef uiStyle fill:#E6F7FF,stroke:#007BFF,stroke-width:2px,color:#0056b3
    classDef kafkaStyle fill:#F8F9FA,stroke:#ADB5BD,stroke-width:2px,shape:cylinder
    classDef agentStyle fill:#E8F5E9,stroke:#28A745,stroke-width:2px
    classDef serviceStyle fill:#FFF3CD,stroke:#FFC107,stroke-width:2px,color:#856404
```

---

## 🔍 4. Component Deep Dive

### 🧩 docker-compose.yml
Defines all services — **Kafka**, **Model Server**, **Axion Agents**, **UI Agent** — and enforces deterministic startup with `depends_on` and `healthcheck`.

### 🧱 Dockerfile
Single-stage build for fast, consistent container creation.  
Installs dependencies and sets `PYTHONPATH`.

### 🧠 model_downloader
Pre-downloads large AI models into a persistent Docker volume — ensuring **instant startup** for the Model Server.

### ⚡ model_server
High-performance **FastAPI** service that loads cached AI models once (NER, Vectorizer) and exposes endpoints:

- `/mask_pii`
- `/vectorize`

### 🏭 axion_agents
Runs `supervisor.py` — the factory manager that:
- Launches and monitors all backend agents (ingestion, enrichment, decision)
- Implements **self-healing logic** for crash recovery.

### 🔬 enrichment_agent.py
Consumes raw events, calls Model Server asynchronously (`aiohttp`), loads domain-specific `.joblib` model, and produces enriched messages.

### 🖥️ ui_agent
Streamlit-based frontend that:
- Produces data to Kafka  
- Consumes real-time decision topics for live visualization

---

## 🧰 5. Detailed Technology Stack

| Category | Technology | Purpose |
|-----------|-------------|----------|
| **Infrastructure** | Docker, Docker Compose | Containerization & orchestration |
| **Messaging Bus** | Apache Kafka | Asynchronous event flow |
| **Backend** | Python 3.10, asyncio, aiokafka | High-performance async agents |
| **Model Serving** | FastAPI, Uvicorn, aiohttp | Fast AI inference server |
| **AI & MLOps** | transformers, sentence-transformers, scikit-learn, joblib, pydantic | PII masking, vectorization, and model training |
| **Frontend** | Streamlit, pandas, kafka-python | Interactive real-time dashboard |

---

## 🧭 6. How to Run This Project (The Golden Path)

### 🥇 Phase 1: The “Golden Build” (One-Time Setup)

#### Step 1.1 — Nuke from Orbit (Clean Reset)
Removes all old Docker states.

```bash
docker system prune -a --volumes
```
Type `y` when prompted.

---

### Step 1.2 — Build & Launch
Builds Docker images and starts all services deterministically.

```bash
docker-compose up --build -d
```

---

### Step 1.3 — Monitor Model Download (Optional)

Watch the one-time model cache download.

```bash
docker-compose logs -f model_downloader
```

✅ **Expected output:**  
“All models have been downloaded and cached successfully.”

---

### Step 1.4 — Train DSP Models (Mandatory)

Train scikit-learn models for each domain.

```bash
docker-compose exec axion_agents python scripts/train_finance_model.py
docker-compose exec axion_agents python scripts/train_logistics_model.py
docker-compose exec axion_agents python scripts/train_healthcare_model.py
```

---

## 🏁 Done!

You can now open the **Streamlit UI** in your browser and start real-time AI pipelines for any domain.

---

## 🧩 Future Plans

- Integrate GPT-based reasoning layer for adaptive decision logic  
- Add real-time anomaly detection  
- Support for on-premise and hybrid deployments  

---

## 🧑‍💻 Author

**Project Axion AI** — built for speed, resilience, and intelligence.

---

✅ **Ready to use:**  
- Just copy and paste this file into your GitHub repo as `README.md`.  
- GitHub automatically supports Mermaid diagrams, emoji, and tables.  
- You can later embed your GIF at the top by replacing the placeholder section with:

```markdown
![Axion AI Demo](path/to/demo.gif)
```
