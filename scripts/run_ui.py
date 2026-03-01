#!/usr/bin/env python3
"""
Script to run the Streamlit UI
"""

import subprocess
import sys
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent.parent

# Path to the Streamlit app
app_path = project_root / "src" / "ui" / "app.py"

# Run Streamlit
print("🚀 Starting GramSetu UI...")
print(f"📂 App location: {app_path}")
print("🌐 Open your browser to: http://localhost:8501")
print("\nPress Ctrl+C to stop the server\n")

subprocess.run([
    sys.executable, "-m", "streamlit", "run",
    str(app_path),
    "--server.port=8501",
    "--server.address=localhost"
])
