# supervisor.py
import asyncio
import sys
import os

# If you want to override DSP discovery, set DSPS_DIR env var
DSPS_DIR = os.getenv("DSPS_DIR", "dsps")

def discover_dsps():
    try:
        items = os.listdir(DSPS_DIR)
    except FileNotFoundError:
        return []
    dsps = [d for d in items if os.path.isdir(os.path.join(DSPS_DIR, d))]
    return sorted(dsps)

async def stream_logs(stream, prefix):
    while True:
        line = await stream.readline()
        if line:
            print(f"[{prefix}]: {line.decode().rstrip()}")
        else:
            break

async def run_and_monitor_agent(agent_name, dsp_name=None):
    """
    Launches `python main.py --agent <agent_name>` and optionally `--dsp <dsp_name>`.
    Restarts any agent that exits.
    """
    while True:
        if dsp_name:
            dsp_prefix = dsp_name.upper()
            log_prefix = f"{dsp_prefix}-{agent_name.upper()}"
            cmd = f"python main.py --agent {agent_name} --dsp {dsp_name}"
        else:
            log_prefix = f"GENERIC-{agent_name.upper()}"
            cmd = f"python main.py --agent {agent_name}"

        print(f"[SUPERVISOR]: Starting {log_prefix} with command: {cmd}")
        process = await asyncio.create_subprocess_shell(cmd,
                                                        stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE)
        print(f"[SUPERVISOR]: {log_prefix} is running with PID {process.pid}.")

        await asyncio.gather(
            stream_logs(process.stdout, log_prefix),
            stream_logs(process.stderr, f"{log_prefix}-ERROR")
        )

        await process.wait()
        print(f"[SUPERVISOR-WARN]: {log_prefix} exited with code {process.returncode}. Restarting in 5s...")
        await asyncio.sleep(5)

async def main():
    print("--- Axion Supervisor (Self-Healing Mode) starting ---")

    dsps = discover_dsps()
    print(f"[SUPERVISOR]: Discovered DSPs: {dsps}")

    tasks = []
    # Generic ingestion agent (no --dsp)
    tasks.append(run_and_monitor_agent("ingestion"))

    # Launch one enrichment and one decision agent per discovered DSP
    for dsp in dsps:
        tasks.append(run_and_monitor_agent("enrichment", dsp))
        tasks.append(run_and_monitor_agent("decision", dsp))

    # If no DSPs found, still run generic enrichment/decision? no — safe to wait.
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    sys.path.append('.')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("--- Axion Supervisor shutting down ---")
