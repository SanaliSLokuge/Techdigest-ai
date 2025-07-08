import streamlit as st
import requests
from bs4 import BeautifulSoup

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# --- API key ---
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# --- Initialize OpenRouter model (o3-mini:free) ---
openai_model = ChatOpenAI(
    model_name="openai/o3-mini",  # Use free-tier model
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    max_tokens=300,
    temperature=0.3
)

# --- Prompt templates ---
summary_prompt = PromptTemplate.from_template("Summarize this in 2–3 sentences:\n\n{text}")
flashcard_prompt = PromptTemplate.from_template("""
You are a helpful AI tutor. Based on the text, generate {num} multiple choice flashcards.
Each should be:

Q: question  
A) Option A  
B) Option B  
C) Option C  
Answer: <letter>

Text:
{text}
""")

# --- Chains ---
summary_chain = summary_prompt | openai_model | StrOutputParser()
flashcard_chain = flashcard_prompt | openai_model | StrOutputParser()

# --- Utility functions ---
def truncate(text, max_chars=1000):
    return text if len(text) <= max_chars else text[:max_chars] + "..."

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        return truncate(text)
    except Exception as e:
        st.error(f"Failed to extract article: {e}")
        return ""

def generate_summary(text):
    try:
        return summary_chain.invoke({"text": text}).strip()
    except Exception as e:
        st.error(f"Summarization failed: {e}")
        return ""

def generate_flashcards(text, num=3):
    try:
        result = flashcard_chain.invoke({"text": text, "num": num})
        if not result.strip():
            st.warning("No flashcards generated. Possibly due to quota or token limit.")
            return []
        return result.strip().split("\n\n")
    except Exception as e:
        st.warning(f"Flashcard generation failed: {e}")
        return []

# --- Streamlit UI ---
st.set_page_config("📄 Article Summarizer & Flashcards", layout="wide")
st.title("📄 Smart Article Assistant — Summary + Flashcards")

article_url = st.text_input("Enter the article URL:", value="")

if st.button("Analyze Article"):
    if not article_url:
        st.warning("Please enter a valid article URL.")
    else:
        with st.spinner("Extracting content and generating insights..."):
            text = extract_text_from_url(article_url)

        if text:
            st.subheader("📌 Summary")
            summary = generate_summary(text)
            st.markdown(summary)

            st.subheader("🧠 Flashcards")
            flashcards = generate_flashcards(text)
            for fc in flashcards:
                st.markdown(fc)
        else:
            st.error("No text extracted from the page.")
