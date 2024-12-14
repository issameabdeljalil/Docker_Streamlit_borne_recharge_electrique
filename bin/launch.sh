#!/bin/bash

echo "Launch app"
source .venv/bin/activate
streamlit run app.py --server.port 5150  --server.address 0.0.0.0
echo "App launched"

