# app.py
import streamlit as st
import feedparser
import requests
import os

from educhain import Educhain
from educhain.llm_config import LLMConfig  # Correct import

# --- CONFIG ---
OPENAI_API_KEY ="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"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# --- Initialize Educhain client with LangChain OpenAI model ---
llm_config = LLMConfig(
    model_name="gpt-3.5-turbo",
    api_key=OPENAI_API_KEY,
    api_base="https://api.openai.com/v1"
)

client = Educhain(llm_config)

# --- Utility functions ---
def generate_summary(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"Summarize this:\n\n{text}"}],
        "max_tokens": 150,
        "temperature": 0.3,
    }
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

def get_latest_news(url, max_items=3):
    return feedparser.parse(url).entries[:max_items]

def generate_flashcards(text, num=3):
    try:
        result = client.qna_engine.generate_questions(topic=text, num=num)
        return getattr(result, "questions", [])
    except Exception as e:
        st.warning(f"Flashcard generation skipped: {e}")
        return []

# --- Streamlit UI ---
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
        if cards:
            st.markdown("**Flashcards:**")
            for card in cards:
                st.markdown(f"- **Q:** {card.question}")
                for opt in card.options:
                    st.markdown(f"  - {opt}")
                st.markdown(f"**Answer:** {card.answer}")
        else:
            st.markdown("_No flashcards generated._")

        st.divider()
else:
    st.info("Configure options and press the button.")
