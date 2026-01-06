#!/bin/bash
# Quick start script for Linux/Mac

echo "================================================"
echo "   LEGAL COURT AI - QUICK START"
echo "================================================"
echo ""

# Activate environment (try both conda and venv)
if command -v conda &> /dev/null; then
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate legal-court-ai 2>/dev/null || source .venv/bin/activate 2>/dev/null
else
    source .venv/bin/activate 2>/dev/null
fi

# Run the application
python start.py
