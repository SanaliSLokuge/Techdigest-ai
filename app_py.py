import streamlit as st
import feedparser
import requests
import os
from educhain import Educhain  # ✅ Correct import

# === CONFIG ===
API_KEY  = "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""
API_BASE = "https://openrouter.ai/api/v1"

# Initialize Educhain client
client = Educhain()
client.qna_engine.set_model("openrouter/llama3")  # Ensure flashcards use correct model

# === FUNCTIONS ===
def generate_summary(text: str) -> str:
    url = f"{API_BASE}/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "openai/o4-mini", 
        "messages": [{"role": "user", "content": f"Summarize this:\n\n{text}"}],
        "max_tokens": 150,
        "temperature": 0.3
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        st.error(f"Summarization API error {resp.status_code}")
        st.text(resp.text)
        return ""
    try:
        return resp.json()["choices"][0]["message"]["content"].strip()
    except:
        st.error("JSON decode failed")
        st.text(resp.text)
        return ""

def generate_flashcards(text: str, num: int = 3):
    try:
        return client.qna_engine.generate_questions(topic=text, num=num)
    except Exception as e:
        st.warning(f"Flashcards skipped: {e}")
        return []

def get_latest_news(url, n=3):
    return feedparser.parse(url).entries[:n]

# === UI ===
st.set_page_config("TechDigest AI", layout="wide")
st.title("🔍 TechDigest AI")

with st.sidebar:
    url = st.text_input("RSS Feed", value="https://techcrunch.com/feed/")
    n = st.slider("Articles", 1, 10, 3)
    if st.button("Fetch"):
        for idx, entry in enumerate(get_latest_news(url, n), 1):
            st.header(f"{idx}. {entry.title}")
            summary = generate_summary(entry.summary)
            if summary: st.write("**Summary:**", summary)
            cards = generate_flashcards(entry.summary)
            if cards:
                st.write("**Flashcards:**")
                for c in cards:
                    st.write(f"- Q: {c.question}")
                    for o in c.options: st.write(f"  - {o}")
                    st.write(f"  - Answer: {c.answer}")
