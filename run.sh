#!/bin/bash
# 🎬 The Show Runner - Launch Script

cd "$(dirname "$0")"

echo "🎬 Starting The Show Runner..."
echo ""

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Installing Streamlit..."
    pip3 install streamlit requests Pillow
fi

# Run the app
python3 -m streamlit run app.py --server.headless true

