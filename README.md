Project Axion AI

A domain-agnostic, multi-agent, high-performance platform for real-time intelligence.

This repository contains the complete "Golden Master" MVP for Axion AI. It is a fully containerized, microservices-based system that can ingest, analyze, and act on real-time data from multiple domains (e.g., Finance, Logistics) simultaneously, delivering AI-driven decisions in seconds.

[A GIF of the Interactive UI in action]

(Author's Note: This is the most important part of your README. Record a short GIF of the UI, showing you selecting the "Finance" domain, clicking "Start Pipeline," and the decisions appearing in real-time. This is the "wow" factor that proves your project works.)

1. The Core Vision: Solving the "Decision Latency Gap"

The Problem: Enterprises are drowning in data but starving for insight. The time between a critical event happening and an intelligent decision being made is often measured in hours. This "decision latency gap" is a massive source of risk and missed revenue.

The Solution: Axion AI is an "Operating System for Real-To-Intelligence." We didn't just build a single pipeline; we built a Core Engine of autonomous agents and a "Domain Solution Pack" (DSP) model. This allows the entire platform to be instantly re-tasked to any domain, from stopping financial fraud to preventing spoilage in a supply chain, by simply plugging in a new DSP.

2. Key Features

Domain-Agnostic Architecture: Fully generic "Core Engine" can run pipelines for any domain (Finance, Logistics, Healthcare) in parallel.

High-Performance & Low-Latency: A decoupled Model Server microservice and an aiohttp-based Enrichment Agent ensure a sub-second processing path, unbound by slow model loading.

Resilient & Stable: A deterministic startup sequence using Docker's health checks and dependency conditions eliminates all startup race conditions.

Self-Healing Backend: A master Supervisor monitors all backend agents and automatically restarts any that crash, ensuring zero downtime.

Trustworthy & Transparent AI: Our MLOps workflow uses k-fold cross-validation to generate a "Model Trust Score" (Accuracy, Precision, Recall) that is displayed directly in the UI for each domain.

Fully Interactive UI: A "single pane of glass" dashboard built in Streamlit allows any user to select a domain, upload their own data, and see real-time, color-coded decisions.

3. High-Level Architecture Diagram

This diagram shows the complete, end-to-end flow of data for a single event. This entire pipeline runs in parallel for every configured DSP.

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
        subgraph "Central Services (The "Brain")"
            MODEL_SERVER["Model Server (FastAPI)<br/>- NER Model<br/>- Vector Model"]:::serviceStyle
        end

        subgraph "Autonomous Agents (The "Workers")"
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


4. Component Deep Dive

docker-compose.yml: The master blueprint. It defines all our services (kafka, model_server, axion_agents, ui_agent) and, most importantly, enforces a deterministic startup order with depends_on and healthcheck conditions. This is the key to our platform's stability.

Dockerfile: A simple, fast, single-stage build file. It installs all dependencies from requirements.txt and sets the PYTHONPATH, ensuring a consistent environment.

model_downloader (Service): A one-time service that pre-downloads the large AI models into a persistent Docker Volume. This is our solution to the "slow startup" problem, ensuring the Model Server boots in seconds.

model_server (Service): A high-performance FastAPI server that loads the cached AI models (NER, Vectorizer) once into memory. It exposes simple API endpoints (/mask_pii, /vectorize) for the functional agents to use.

axion_agents (Service): The "factory floor." This container runs the supervisor.py script.

supervisor.py: The "factory floor manager." A master script that launches and monitors all backend agents (ingestion, enrichment, decision) for all DSPs in parallel. It includes self-healing logic to automatically restart any agent that crashes.

agents/enrichment_agent.py: The "heavy lifter." This is our high-performance agent that:

Consumes from a raw topic.

Makes fast, asynchronous (aiohttp) calls to the Model Server.

Loads the small, DSP-specific .joblib model.

Produces the final, enriched message.

ui_agent (Service): The "front door." A multi-threaded Streamlit application that:

Acts as a Producer to send user data into the pipeline.

Acts as a Consumer, listening to all final decisions topics to display results in real-time.

5. Detailed Technology Stack

Category

Technology

Purpose

Infrastructure

Docker & Docker Compose

Containerization, orchestration, and deterministic startup.

Messaging Bus

Apache Kafka

The asynchronous "nervous system" of the entire platform.

Backend

Python 3.10

The core language for all services and agents.



asyncio

For high-performance, concurrent agent operations.



aiokafka

The asynchronous Kafka client for our backend agents.

Model Serving

FastAPI & Uvicorn

For our high-speed, internal AI Model Server.



aiohttp

The asynchronous client used by agents to query the Model Server.

AI & MLOps

transformers

For the dslim/bert-base-NER model (PII masking).



sentence-transformers

For the all-MiniLM-L6-v2 model (vectorization).



scikit-learn

For training and running our lightweight DSP-specific models.



joblib

For model serialization (.joblib files).



pydantic

For strict, self-documenting data schemas (RawEvent, etc.).

Frontend

Streamlit

For the all-in-one, interactive user dashboard.



pandas

For easy CSV handling in the UI.



kafka-python

The synchronous client for the Streamlit consumer thread.

6. How to Run This Project (The Golden Path)

This is the definitive, step-by-step guide to run the platform from a clean slate.

Phase 1: The "Golden Build" (One-Time Setup)

This is the initial process to build the platform and prepare all its assets.

Step 1.1: The "Nuke from Orbit" Reset
This is the most important first step. It destroys any old, corrupted Docker state on your machine and ensures a perfect, clean start.

docker system prune -a --volumes


(It will ask for confirmation; type y and press Enter.)

Step 1.2: The "Golden Build" and Launch
This command builds the Docker images and starts all services in the correct, deterministic order.

docker-compose up --build -d


Step 1.3: Monitor the One-Time Model Download (Optional but Recommended)
The system will now be downloading several gigabytes of AI models. You can watch this happen in real-time.

docker-compose logs -f model_downloader


Expected Output: You will see download progress bars. Once it says "All models have been downloaded and cached successfully," this service will exit, and the rest of the platform will continue starting up.

Step 1.4: Train the DSP Models (Mandatory)
Once the build is complete, we must train the scikit-learn models for each domain. This creates the .joblib and model_metrics.json files.

docker-compose exec axion_agents python scripts/train_finance_model.py
docker-compose exec axion_agents python scripts/train_logistics_model.py
docker-compose exec axion_agents python scripts/train_healthcare_model.py
