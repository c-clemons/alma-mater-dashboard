#!/bin/bash
# Run the Alma Mater Client Dashboard

cd "$(dirname "$0")"
streamlit run app_client.py --server.port 8501 --server.address 0.0.0.0
