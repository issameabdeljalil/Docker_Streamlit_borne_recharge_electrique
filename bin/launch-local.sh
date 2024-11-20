#!/bin/bash

echo "Launch app"
bash data_collector/bin/run.sh
streamlit run app.py
echo "App launch"

