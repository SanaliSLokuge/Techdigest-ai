import os
import requests
import feedparser
import streamlit as st
from educhain import Educhain

# Environment variables setup — ideally set externally or via secrets
API_KEY = "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"  # Your OpenRouter key
API_BASE = "https://openrouter.ai/api/v1"
os.environ["OPENAI_API_KEY"] = API_KEY
os.environ["OPENAI_API_BASE"] = API_BASE
os.environ["EDUCHAIN_MODEL"] = "openrouter/llama3"

educhain_client = Educhain()

def generate_summary(text):
    url = f"{API_BASE}/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"Summarize the following text briefly:\n\n{text}"}],
        "max_tokens": 150,
        "temperature": 0.3,
    }
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

def get_latest_news(feed_url, max_items=3):
    feed = feedparser.parse(feed_url)
    entries = feed.entries[:max_items]
    return [(entry.title, entry.summary) for entry in entries]

def generate_flashcards(text, num=3):
    mcqs = educhain_client.qna_engine.generate_questions(topic=text, num=num)
    return mcqs.questions

# Streamlit UI
st.title("TechDigest AI - News Summarizer & Flashcards")

feed_url = st.selectbox("Select news source", ["https://techcrunch.com/feed/", "https://news.ycombinator.com/rss"])
num_articles = st.slider("Number of articles", min_value=1, max_value=5, value=3)

if st.button("Fetch & Summarize"):
    news = get_latest_news(feed_url, num_articles)
    for idx, (title, content) in enumerate(news, 1):
        st.subheader(f"{idx}. {title}")
        summary = generate_summary(content)
        st.write(f"**Summary:** {summary}")
        st.write("**Flashcards:**")
        flashcards = generate_flashcards(content)
        for card in flashcards:
            st.markdown(f"- **Q:** {card.question}")
            for opt in card.options:
                st.markdown(f"    - {opt}")
            st.markdown(f"  - **Answer:** {card.answer}")
        st.markdown("---")
