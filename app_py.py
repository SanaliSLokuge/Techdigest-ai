# app.py
import streamlit as st
import feedparser
import requests
from educhain import Educhain
from educhain.config import LLMConfig 


# === CONFIG ===
API_KEY  = "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"  # 👈 OpenRouter Key
API_BASE = "https://openrouter.ai/api/v1"

# === Initialize Educhain Client with OpenRouter ===
llm_config = LLMConfig(
    model_name="openrouter/llama3",
    api_key=API_KEY,
    api_base=API_BASE
)
educhain_client = Educhain(llm_config)

# === Utility Functions ===
def generate_summary(text):
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/o4-mini",
        "messages": [{"role": "user", "content": f"Summarize this:\n\n{text}"}],
        "max_tokens": 150,
        "temperature": 0.3
    }
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

def get_latest_news(url, max_items=3):
    return feedparser.parse(url).entries[:max_items]

def generate_flashcards(text, num=3):
    return educhain_client.qna_engine.generate_questions(topic=text, num=num).questions

# === Streamlit UI ===
st.set_page_config("📰 TechDigest AI", layout="wide")
st.title("🔍 TechDigest AI — Summarizer + Flashcards")

url = st.text_input("RSS Feed URL", value="https://techcrunch.com/feed/")
count = st.slider("Number of Articles", 1, 10, 3)

if st.button("Fetch & Generate"):
    with st.spinner("Fetching and processing..."):
        articles = get_latest_news(url, count)

    for idx, entry in enumerate(articles, 1):
        st.subheader(f"{idx}. {entry.title}")
        summary = generate_summary(entry.summary)
        st.markdown(f"**Summary:** {summary}")

        cards = generate_flashcards(entry.summary)
        st.markdown("**Flashcards:**")
        for card in cards:
            st.markdown(f"- **Q:** {card.question}")
            for opt in card.options:
                st.markdown(f"  - {opt}")
            st.markdown(f"**Answer:** {card.answer}")
        st.divider()
else:
    st.info("Configure options and press the button.")
