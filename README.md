Project Axion: A Domain-Agnostic AI Pipeline (MVP)
Status: Platform MVP Complete | Timeline: 45-Day Sprint

Project Axion is a high-fidelity prototype of a domain-agnostic, multi-agent autonomous data intelligence platform. It demonstrates a generic, event-driven pipeline that can be instantly re-tasked to new domains (e.g., Finance, Logistics, Healthcare) by plugging in a "Domain Solution Pack" (DSP).

Core Architecture: The Engine and the "Cartridge"
The system is built on a decoupled architecture that separates the generic framework from the domain-specific logic.

The Axion Core Engine: A set of generic, reusable agents (ingestion, cleaning, analytics, decision) and a master runner (main.py). The engine knows how to run a pipeline but knows nothing about the data it's processing.

Domain Solution Packs (DSPs): These are the "cartridges." A DSP is a directory containing the specific configuration, data, and ML models for a particular use case. The core engine loads a DSP at runtime to configure itself for that domain.

Implemented DSPs
Finance: Real-time credit card fraud detection.

Logistics: Real-time anomaly detection for refrigerated truck temperatures.

Healthcare: Real-time insurance claim pre-approval.

Tech Stack
Containerization: Docker, Docker Compose

Messaging/Orchestration: Apache Kafka

Agents & ML: Python, aiokafka, pydantic

AI Models: transformers, torch, sentence-transformers, scikit-learn

Dashboard: Streamlit

How to Run a Demo
Prerequisites: Docker and Docker Compose installed with sufficient resources (>=6GB RAM recommended).

Step 1: Start the Environment
This command builds the Docker image and starts all services in the background.

docker-compose up --build -d

Step 2: Train the DSP Models
Run the one-time scripts to create the model artifacts for all DSPs.

docker-compose exec axion_agents python scripts/train_finance_model.py
docker-compose exec axion_agents python scripts/train_logistics_model.py
docker-compose exec axion_agents python scripts/train_healthcare_model.py

Step 3: Run the Pipeline for a Specific Domain
Choose which domain you want to demo (e.g., logistics).

3.1. Start the Backend Agents
Open three separate terminals and run one command in each, specifying your chosen DSP.

# In Terminal 1 (Cleaning):

docker-compose exec axion_agents python main.py --agent cleaning --dsp logistics

# In Terminal 2 (Analytics):

docker-compose exec axion_agents python main.py --agent analytics --dsp logistics

# In Terminal 3 (Decision):

docker-compose exec axion_agents python main.py --agent decision --dsp logistics

3.2. Start the UI Agent
In a fourth terminal, start the UI, also specifying the DSP.

docker-compose exec axion_agents python main.py --agent ui --dsp logistics

Now, open your browser to http://localhost:8501. The dashboard title will show "LOGISTICS".

3.3. Trigger the Pipeline
In a fifth terminal, run the Ingestion Agent for your chosen DSP to start the data flow.

docker-compose exec axion_agents python main.py --agent ingestion --dsp logistics

Watch the dashboard update in real-time with logistics decisions.

To switch domains, simply stop the agents (Ctrl+C) and restart them with a new DSP name (e.g., --dsp finance).

To Shut Down:

docker-compose down --rmi all -v
