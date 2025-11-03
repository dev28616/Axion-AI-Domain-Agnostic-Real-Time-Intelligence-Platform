import streamlit as st
import pandas as pd
import io
import json
import time
import asyncio
import threading
from queue import Queue, Empty
from kafka import KafkaProducer
from kafka.errors import KafkaError
import sys
import os
import importlib

# --- Add project root to path for core imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.kafka_client import get_kafka_consumer
from core.schemas import FinalDecision

# --- CONFIGURATION ---
st.set_page_config(page_title="Axion Interactive Hub", page_icon="⚡️", layout="wide")

KAFKA_BROKER_URL = "kafka:29092"
INPUT_TOPIC = "user-input-events"
TELEMETRY_TOPIC = "axion-telemetry-events"
SUPPORTED_DSPS = ["finance", "logistics", "healthcare"]
PIPELINE_STAGES = ["Ingestion", "Enrichment", "Decision"]

# --- UI STATE & INTER-THREAD COMMUNICATION ---
# This robust initialization prevents all AttributeError issues.
if 'domain' not in st.session_state:
    st.session_state.domain = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'pipeline_started' not in st.session_state:
    st.session_state.pipeline_started = False
if 'consumer_thread' not in st.session_state:
    st.session_state.consumer_thread = None
if 'message_queue' not in st.session_state:
    st.session_state.message_queue = Queue()
if 'status_queue' not in st.session_state:
    st.session_state.status_queue = Queue()
if 'consumer_status' not in st.session_state:
    st.session_state.consumer_status = "Initializing..."
if 'mapping' not in st.session_state:
    st.session_state.mapping = {}
if 'event_progress' not in st.session_state:
    st.session_state.event_progress = {}

for dsp in SUPPORTED_DSPS:
    if f"{dsp}_decisions" not in st.session_state:
        st.session_state[f"{dsp}_decisions"] = []

# --- KAFKA PRODUCER ---
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)
    )
except KafkaError as e:
    st.error(f"Failed to connect to Kafka Producer. Please ensure the environment is running. Error: {e}")
    st.stop()
    
# --- MOCK DATA SAMPLES ---
SAMPLES = {
    "finance": """event_id,source_id,event_value,source_name,description,timestamp\ntxn_101,user_a,125.50,CoffeeBean Inc.,"Morning coffee",2025-09-12T08:30:00Z\ntxn_103,user_a,2500.00,GadgetGalaxy,"New headphones",2025-09-12T11:15:30Z""",
    "logistics": """event_id,source_id,event_value,source_name,description,timestamp\nship_201,truck_a,3.5,Warehouse A -> B,"Fresh produce",2025-09-15T18:00:00Z\nship_204,truck_c,9.2,Warehouse E -> F,"CRITICAL TEMP",2025-09-15T18:15:00Z""",
    "healthcare": """event_id,source_id,event_value,source_name,description,timestamp\nclaim_301,patient_x,150.00,City Clinic,"Standard consultation",2025-09-15T09:00:00Z\nclaim_303,patient_z,12500.00,Surgical Center,"Complex procedure",2025-09-15T09:10:00Z"""
}
REQUIRED_FIELDS = ['event_id', 'source_id', 'event_value', 'source_name', 'description', 'timestamp']

# --- ASYNC KAFKA CONSUMER LOGIC (runs in a separate thread) ---
async def consume_messages(q: Queue, dsp_configs, status_q: Queue):
    try:
        decision_topics = [config.TOPIC_DECISIONS for config in dsp_configs.values()]
        all_topics_to_consume = decision_topics + [TELEMETRY_TOPIC]
        consumer = await get_kafka_consumer(all_topics_to_consume, "master-ui-group")
        status_q.put("Consumer connected successfully.")
        async for msg in consumer:
            message_data = json.loads(msg.value.decode('utf-8'))
            message_data['topic'] = msg.topic
            q.put(message_data)
    except Exception as e:
        status_q.put(f"Consumer Error: {e}")
    finally:
        if 'consumer' in locals():
            await consumer.stop()

def start_consumer_thread(q: Queue, status_q: Queue):
    dsp_configs = {}
    for dsp in SUPPORTED_DSPS:
        dsp_module = importlib.import_module(f"dsps.{dsp}.config")
        dsp_configs[dsp] = getattr(dsp_module, f"{dsp.capitalize()}DSPConfig")

    def thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(consume_messages(q, dsp_configs, status_q))
        loop.close()

    thread = threading.Thread(target=thread_target, daemon=True)
    thread.start()
    return thread

# --- UI LAYOUT & LOGIC ---
st.title("⚡️ Axion Interactive Intelligence Hub")

# Start consumer thread once and handle message processing
if st.session_state.consumer_thread is None:
    st.session_state.consumer_thread = start_consumer_thread(st.session_state.message_queue, st.session_state.status_queue)

try:
    status_update = st.session_state.status_queue.get_nowait()
    st.session_state.consumer_status = status_update
except Empty:
    pass

while not st.session_state.message_queue.empty():
    msg = st.session_state.message_queue.get()
    topic = msg.pop('topic', None)
    if topic == TELEMETRY_TOPIC:
        event_id, agent = msg.get("event_id"), msg.get("agent")
        if event_id not in st.session_state.event_progress:
            st.session_state.event_progress[event_id] = set()
        st.session_state.event_progress[event_id].add(agent)
    else:
        for dsp in SUPPORTED_DSPS:
            if topic and dsp in topic:
                st.session_state[f"{dsp}_decisions"].append(msg)

# --- STEP 1: DOMAIN SELECTION ---
st.header("Step 1: Choose Your Domain")
cols = st.columns(len(SUPPORTED_DSPS))
domain_emojis = {"finance": "🏦", "logistics": "🚚", "healthcare": "⚕️"}

for i, dsp in enumerate(SUPPORTED_DSPS):
    if cols[i].button(f"{domain_emojis[dsp]} {dsp.capitalize()}", key=f"btn_{dsp}"):
        st.session_state.domain = dsp
        st.session_state.pipeline_started = False
        st.session_state.df = None

if st.session_state.domain:
    st.success(f"**Operating in Domain:** {st.session_state.domain.capitalize()}")
    
    # --- MODEL TRUST SCORE ---
    st.subheader("Model Trust Score (via Cross-Validation)")
    metrics_path = f"dsps/{st.session_state.domain}/models/model_metrics.json"
    try:
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        m_cols = st.columns(3)
        accuracy_label = "Avg. Outlier %" if st.session_state.domain == 'logistics' else "Avg. Accuracy"
        m_cols[0].metric(accuracy_label, f"{metrics.get('mean_accuracy', 0)*100:.1f}%")
        m_cols[1].metric("Avg. Precision", f"{metrics.get('mean_precision', 0)*100:.1f}%" if metrics.get('mean_precision', 0) > 0 else "N/A")
        m_cols[2].metric("Avg. Recall", f"{metrics.get('mean_recall', 0)*100:.1f}%" if metrics.get('mean_recall', 0) > 0 else "N/A")
    except FileNotFoundError:
        st.warning("Model metrics not available. Please train the model for this DSP.")

    st.header(f"Step 2: Provide Data for {st.session_state.domain.capitalize()}")
    
    # --- DATA INPUT ---
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv", key=f"uploader_{st.session_state.domain}")
    if uploaded_file is not None:
        try:
            st.session_state.df = pd.read_csv(uploaded_file, dtype=str)
        except Exception as e:
            st.error(f"Could not read uploaded file. Error: {e}")
            st.session_state.df = None
    else:
        st.text_area("Or paste your CSV data here:", SAMPLES[st.session_state.domain], height=150, key="csv_input")
        if st.button("Load Pasted Data"):
            try:
                st.session_state.df = pd.read_csv(io.StringIO(st.session_state.csv_input), dtype=str)
            except Exception as e:
                st.error(f"Could not parse pasted data. Error: {e}")
                st.session_state.df = None
                
    if st.session_state.df is not None:
        st.dataframe(st.session_state.df.head())

        # --- COLUMN MAPPING ---
        st.header("Step 3: Map Your Columns")
        user_cols = st.session_state.df.columns.tolist()
        for field in REQUIRED_FIELDS:
            st.session_state.mapping[field] = st.selectbox(f"Map to '{field}'", user_cols, index=user_cols.index(field) if field in user_cols else 0, key=f"map_{field}")

        # --- RUN PIPELINE ---
        st.header("Step 4: Run the Pipeline")
        if st.button("▶️ Start Pipeline", type="primary"):
            st.session_state.pipeline_started = True
            st.session_state[f"{st.session_state.domain}_decisions"] = []
            st.session_state.event_progress = {} # Clear progress on new run
            with st.spinner("Ingesting data..."):
                for index, row in st.session_state.df.iterrows():
                    message = {"domain": st.session_state.domain, "data": row.to_dict()}
                    producer.send(INPUT_TOPIC, value=message)
                producer.flush()
            st.success("Data sent to the always-on backend for processing!")
    
    # --- LIVE PIPELINE STATUS ---
    st.header("Step 5: Live Pipeline Status")
    status_container = st.container()
    
    with status_container:
        if not st.session_state.pipeline_started:
            st.info("Click 'Start Pipeline' to see the real-time status tracker.")
        else:
            df = st.session_state.get('df')
            if df is not None and 'event_id' in df.columns:
                for event_id in df['event_id'].tolist():
                    progress = st.session_state.event_progress.get(event_id, set())
                    st.write(f"**Event ID: {event_id}**")
                    cols = st.columns(len(PIPELINE_STAGES))
                    for i, stage in enumerate(PIPELINE_STAGES):
                        if stage in progress:
                            cols[i].success(f"✔️ {stage}")
                        else:
                            cols[i].info(f"⏳ {stage}")
            else:
                st.warning("No data loaded to track.")

    # --- FINAL DECISIONS ---
    st.header(f"Step 6: Final Decisions for {st.session_state.domain.capitalize()} (Real-Time)")
    log_container = st.empty()
    
    with log_container.container():
        decisions_for_domain = st.session_state[f"{st.session_state.domain}_decisions"]
        if not decisions_for_domain and st.session_state.pipeline_started:
            st.info(f"Waiting for final decisions... (Consumer status: {st.session_state.consumer_status})")
        elif decisions_for_domain:
            for decision_data in reversed(decisions_for_domain):
                try:
                    decision = FinalDecision(**decision_data)
                    if decision.decision == "ALERT":
                        st.error(f"🔴 REJECTED: Event {decision.event_id} | Reason: {decision.reason}")
                    else:
                        st.success(f"🟢 APPROVED: Event {decision.event_id} | Reason: {decision.reason}")
                except Exception as e:
                    st.warning(f"Could not parse decision message: {decision_data}. Error: {e}")
    
    # Rerun logic to keep the UI live
    time.sleep(1)
    st.rerun()

st.markdown("---")
st.markdown("Built by Axion AI")

