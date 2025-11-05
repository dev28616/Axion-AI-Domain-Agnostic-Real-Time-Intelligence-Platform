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
    subgraph "User and UI"
        UI_HUB["🚀 Interactive UI Hub<br/>(Streamlit)"]
    end

    subgraph "Kafka Event Bus - The Nervous System"
        direction LR
        KAFKA_INPUT["user-input-events"]
        KAFKA_RAW["domain-raw-events"]
        KAFKA_ANALYTICS["domain-analytics-results"]
        KAFKA_DECISIONS["domain-decisions"]
    end

    subgraph "Axion Core Engine - Always-On Backend"
        subgraph "Central Services - The Brain"
            MODEL_SERVER["Model Server (FastAPI)<br/>• NER Model<br/>• Vector Model"]
        end

        subgraph "Autonomous Agents - The Workers"
            INGESTION["Ingestion Agent<br/>(Smart Router)"]
            ENRICHMENT["Enrichment Agent<br/>(AI & .joblib Models)"]
            DECISION["Decision Agent<br/>(Rule Engine)"]
        end
    end

    UI_HUB -->|"1️⃣ User Submits Data"| KAFKA_INPUT
    KAFKA_INPUT -->|"2️⃣ Consumed by"| INGESTION
    INGESTION -->|"3️⃣ Routed to Domain"| KAFKA_RAW
    KAFKA_RAW -->|"4️⃣ Processed by"| ENRICHMENT
    ENRICHMENT -->|"5️⃣ Async API Call → PII Mask + Vectorize"| MODEL_SERVER
    MODEL_SERVER -->|"6️⃣ AI Results"| ENRICHMENT
    ENRICHMENT -->|"7️⃣ Enriched Result"| KAFKA_ANALYTICS
    KAFKA_ANALYTICS -->|"8️⃣ Consumed by"| DECISION
    DECISION -->|"9️⃣ Produces Final Decision"| KAFKA_DECISIONS
    KAFKA_DECISIONS -->|"🔟 Displayed in"| UI_HUB
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

## 🧩 3. High-Level Architecture Diagram

![Axion AI System Architecture](assets/axion_architecture.png)
