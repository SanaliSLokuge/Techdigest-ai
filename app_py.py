import streamlit as st
import feedparser
import requests

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

# --- Load API key securely ---
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# --- Initialize LangChain ChatOpenAI with OpenRouter endpoint ---
openai_model = ChatOpenAI(
    model_name="openai/o3-mini",  # This is OpenRouter's naming format
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",  # Required for OpenRouter
)

# --- Prompt for flashcard generation ---
flashcard_prompt = PromptTemplate.from_template("""
You are a helpful AI tutor. Based on the following text, generate {num} flashcards.
Each flashcard should contain:
- One multiple choice question
- 3 answer options (A, B, C)
- One clearly marked correct answer

Text:
{text}
""")

flashcard_chain = LLMChain(
    llm=openai_model,
    prompt=flashcard_prompt,
    output_parser=StrOutputParser()
)

# --- Your utility functions ---
def generate_summary(text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-4",
        "messages": [{"role": "user", "content": f"Summarize this:\n\n{text}"}],
        "max_tokens": 150,
        "temperature": 0.3
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        st.error(f"Summarization failed: {resp.status_code}")
        st.text(resp.text)
        return ""
    return resp.json()["choices"][0]["message"]["content"].strip()

def get_latest_news(url, max_items=3):
    return feedparser.parse(url).entries[:max_items]

def generate_flashcards(text, num=3):
    try:
        result = flashcard_chain.invoke({"text": text, "num": num})
        return result.strip().split("\n\n")
    except Exception as e:
        st.warning(f"Flashcard generation failed: {e}")
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

        flashcards = generate_flashcards(entry.summary)
        st.markdown("**Flashcards:**")
        for fc in flashcards:
            st.markdown(fc)
        st.divider()
else:
    st.info("Configure options and press the button.")
