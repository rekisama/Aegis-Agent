#!/usr/bin/env python3
"""
Quick Start Script for Aegis Agent
A simplified way to run Aegis Agent with different options.
"""

import sys
import argparse
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import AegisAgentCLI
import asyncio


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(
        description="Aegis Agent - General-Purpose Personal Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Start interactive mode
  python run.py --config config.json  # Use custom config
  python run.py --example         # Run examples
  python run.py --test            # Run tests
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--example", "-e",
        action="store_true",
        help="Run examples instead of interactive mode"
    )
    
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run tests instead of interactive mode"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    if args.version:
        print("Aegis Agent v1.0.0")
        print("A general-purpose personal assistant with persistent memory")
        return
    
    if args.test:
        print("🧪 Running tests...")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
        sys.exit(result.returncode)
    
    if args.example:
        print("📚 Running examples...")
        import subprocess
        result = subprocess.run([sys.executable, "examples/basic_usage.py"])
        sys.exit(result.returncode)
    
    # Start interactive mode
    print("🚀 Starting Aegis Agent...")
    cli = AegisAgentCLI()
    
    async def run():
        success = await cli.initialize_agent(args.config)
        if success:
            await cli.run_interactive_mode()
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 