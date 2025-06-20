import streamlit as st
import feedparser
import requests
import os
from educhain.client import EduchainClient  # ✅ Correct import

# === CONFIG ===
API_KEY  = "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"
API_BASE = "https://openrouter.ai/api/v1"

# Set environment variables for Educhain
os.environ["OPENAI_API_KEY"]  = API_KEY
os.environ["OPENAI_API_BASE"] = API_BASE
os.environ["EDUCHAIN_MODEL"]  = "openrouter/llama3"

# Initialize Educhain client
educhain = EduchainClient()
educhain.qna_engine.set_model("openrouter/llama3")

# === FUNCTIONS ===
def generate_summary(text: str) -> str:
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json"
    }
    payload = {
        "model": "openai/o4-mini",  # ✅ this one is free & reliable on OpenRouter
        "messages": [{"role": "user", "content": f"Summarize the following text briefly:\n\n{text}"}],
        "max_tokens": 150,
        "temperature": 0.3
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        st.error(f"Summarization API error {resp.status_code}")
        st.text(f"Raw response:\n{resp.text}")
        return ""
    try:
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        st.error("Failed to parse JSON from summarization response")
        st.text(resp.text)
        return ""

def generate_flashcards(text: str, num: int = 3):
    try:
        return educhain.qna_engine.generate_mcq(topic=text, num=num)
    except Exception as e:
        st.warning(f"Flashcard generation skipped: {e}")
        return []

def get_latest_news(feed_url: str, max_items: int = 3):
    feed = feedparser.parse(feed_url)
    return feed.entries[:max_items]

# === STREAMLIT UI ===
st.set_page_config(page_title="TechDigest AI", layout="wide")
st.title("🔍 TechDigest AI – News Summaries & Flashcards")

with st.sidebar:
    st.header("Configuration")
    feed_url      = st.text_input("RSS Feed URL",    value="https://techcrunch.com/feed/")
    max_articles  = st.slider("Number of articles", 1, 10, 3)
    generate_btn  = st.button("Fetch & Process")

if generate_btn:
    entries = get_latest_news(feed_url, max_articles)
    for idx, entry in enumerate(entries, start=1):
        st.subheader(f"Article {idx}: {entry.title}")
        with st.expander("Summary & Flashcards"):
            summary = generate_summary(entry.summary)
            if summary:
                st.markdown(f"**Summary:**  {summary}")

            cards = generate_flashcards(entry.summary)
            if cards:
                st.markdown("**Flashcards:**")
                for card in cards:
                    st.markdown(f"- **Q:** {card['question']}")
                    for opt in card['options']:
                        st.markdown(f"  - {opt}")
                    st.markdown(f"  - **Answer:** {card['correct_answer']}")
    st.success("Done processing.")
else:
    st.info("Configure in the sidebar and click 'Fetch & Process' to get started.")
