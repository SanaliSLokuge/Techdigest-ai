import streamlit as st
import feedparser
import requests
import os

from educhain import Educhain, LLMConfig
from langchain_openai import ChatOpenAI

# --- Set your OpenAI API key here or in environment variables ---
OPENAI_API_KEY = "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"  # Your real OpenAI API key

# Optional: set env var for convenience if you want to use it elsewhere
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# --- Initialize LangChain ChatOpenAI model with your key ---
openai_model = ChatOpenAI(
    model_name="gpt-4",               # or "gpt-3.5-turbo" depending on your access
    openai_api_key=OPENAI_API_KEY
)

# --- Wrap LangChain model in Educhain config ---
llm_config = LLMConfig(custom_model=openai_model)

# --- Initialize Educhain client with config ---
educhain_client = Educhain(llm_config)

# --- Your utility functions ---
def generate_summary(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": f"Summarize this:\n\n{text}"}],
        "max_tokens": 150,
        "temperature": 0.3
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        st.error(f"Summarization API failed: {resp.status_code}")
        st.text(resp.text)
        return ""
    return resp.json()["choices"][0]["message"]["content"].strip()


def get_latest_news(url, max_items=3):
    return feedparser.parse(url).entries[:max_items]

def generate_flashcards(text, num=3):
    try:
        result = educhain_client.qna_engine.generate_questions(topic=text, num=num)
        # Confirm result type
        if hasattr(result, "questions"):
            return result.questions
        else:
            st.warning(f"Unexpected flashcards result: {result}")
            return []
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
        st.markdown("**Flashcards:**")
        for card in cards:
            st.markdown(f"- **Q:** {card.question}")
            for opt in card.options:
                st.markdown(f"  - {opt}")
            st.markdown(f"**Answer:** {card.answer}")
        st.divider()
else:
    st.info("Configure options and press the button.")
