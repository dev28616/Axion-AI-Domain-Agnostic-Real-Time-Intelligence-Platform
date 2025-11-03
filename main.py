import argparse
import asyncio
import importlib
import sys
import subprocess

def main():
    sys.path.append('.')
    parser = argparse.ArgumentParser(description="Axion Agent Runner")
    parser.add_argument("--agent", required=True, help="Agent to run")
    parser.add_argument("--dsp", required=True, help="Domain Solution Pack to use")
    args = parser.parse_args()

    print(f"--- Starting Axion Agent ---")
    print(f"Agent: {args.agent}")
    print(f"DSP:   {args.dsp}")
    print(f"--------------------------")

    try:
        agent_module = importlib.import_module(f"agents.{args.agent}_agent")
        agent_main = getattr(agent_module, "main")
        
        # The ingestion agent is generic and doesn't need a DSP config
        if args.agent == 'ingestion':
            dsp_config = None
        else:
            dsp_module = importlib.import_module(f"dsps.{args.dsp}.config")
            dsp_config = getattr(dsp_module, f"{args.dsp.capitalize()}DSPConfig")
        
        asyncio.run(agent_main(dsp_config))
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error: Could not find or load agent '{args.agent}' or DSP '{args.dsp}'. Details: {e}")
    except KeyboardInterrupt:
        print("Agent runner stopped by user.")

if __name__ == "__main__":
    main()

