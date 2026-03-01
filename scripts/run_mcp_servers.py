#!/usr/bin/env python3
"""
Script to run both MCP servers (Agmarknet and Weather)
"""

import subprocess
import sys
import time
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent.parent

# Paths to the MCP servers
agmarknet_server = project_root / "src" / "mcp" / "servers" / "agmarknet_server.py"
weather_server = project_root / "src" / "mcp" / "servers" / "weather_server.py"

print("🚀 Starting MCP Servers...")
print("=" * 60)

# Start Agmarknet server
print("\n📊 Starting Agmarknet Server (port 8001)...")
agmarknet_process = subprocess.Popen(
    [sys.executable, str(agmarknet_server)],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(2)

# Start Weather server
print("🌤️  Starting Weather Server (port 8002)...")
weather_process = subprocess.Popen(
    [sys.executable, str(weather_server)],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(2)

print("\n" + "=" * 60)
print("✓ MCP Servers Started!")
print("=" * 60)
print("\n📊 Agmarknet Server: http://localhost:8001")
print("🌤️  Weather Server: http://localhost:8002")
print("\nPress Ctrl+C to stop all servers\n")

try:
    # Keep the script running
    agmarknet_process.wait()
    weather_process.wait()
except KeyboardInterrupt:
    print("\n\n🛑 Stopping MCP Servers...")
    agmarknet_process.terminate()
    weather_process.terminate()
    print("✓ Servers stopped")
