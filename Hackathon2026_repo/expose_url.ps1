# Requires cloudflared installed and available on PATH
streamlit run src/app.py --server.port 8501
# In another terminal:
# cloudflared tunnel --url http://localhost:8501
