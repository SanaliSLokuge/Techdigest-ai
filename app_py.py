import streamlit as st
import requests
import feedparser
from bs4 import BeautifulSoup

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# --- API Key ---
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# --- Initialize Free OpenRouter Model ---
openai_model = ChatOpenAI(
    model_name="openai/o3-mini",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    max_tokens=300,
    temperature=0.3
)

# --- Prompt Templates ---
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

summary_chain = summary_prompt | openai_model | StrOutputParser()
flashcard_chain = flashcard_prompt | openai_model | StrOutputParser()

# --- Utilities ---
def truncate(text, max_chars=1000):
    return text if len(text) <= max_chars else text[:max_chars] + "..."

def extract_text_from_web(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        return truncate(text)
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return ""

def get_rss_articles(url, max_items=3):
    return feedparser.parse(url).entries[:max_items]

def generate_summary(text):
    try:
        return summary_chain.invoke({"text": truncate(text)}).strip()
    except Exception as e:
        st.error(f"Summarization failed: {e}")
        return ""

def generate_flashcards(text, num=3):
    try:
        result = flashcard_chain.invoke({"text": truncate(text), "num": num})
        if not result.strip():
            st.warning("No flashcards generated.")
            return []
        return result.strip().split("\n\n")
    except Exception as e:
        st.warning(f"Flashcard generation failed: {e}")
        return []

# --- UI ---
st.set_page_config("🧠 Smart Article Summarizer", layout="wide")
st.title("📄 Smart Article Assistant — Summary + Flashcards")

mode = st.radio("Select Input Mode", ["RSS Feed", "Article URL"])

if mode == "RSS Feed":
    rss_url = st.text_input("Enter RSS Feed URL:", value="https://techcrunch.com/feed/")
    count = st.slider("Number of Articles", 1, 10, 3)
    
    if st.button("Fetch & Generate"):
        with st.spinner("Fetching and processing..."):
            articles = get_rss_articles(rss_url, count)
            for idx, entry in enumerate(articles, 1):
                st.subheader(f"{idx}. {entry.title}")
                summary = generate_summary(entry.summary)
                st.markdown(f"**Summary:** {summary}")
                flashcards = generate_flashcards(entry.summary)
                st.markdown("**Flashcards:**")
                for fc in flashcards:
                    st.markdown(fc)
                st.divider()

else:  # Article URL
    article_url = st.text_input("Enter article URL:")

    if st.button("Analyze Article"):
        with st.spinner("Extracting and analyzing article..."):
            text = extract_text_from_web(article_url)
            if text:
                st.subheader("📌 Summary")
                summary = generate_summary(text)
                st.markdown(summary)
                
                st.subheader("🧠 Flashcards")
                flashcards = generate_flashcards(text)
                for fc in flashcards:
                    st.markdown(fc)
            else:
                st.warning("No text could be extracted from the URL.")
