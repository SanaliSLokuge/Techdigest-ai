import streamlit as st
import feedparser
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# --- Load API key securely ---
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# --- Initialize OpenRouter ChatOpenAI with o3-mini:free ---
openai_model = ChatOpenAI(
    model_name="openai/o3-mini",  # Free-tier GPT-4o-mini
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

# --- Utility Functions ---
def truncate(text, max_chars=1000):
    return text if len(text) <= max_chars else text[:max_chars] + "..."

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
            st.warning("No flashcards generated. Possibly due to quota or token limit.")
            return []
        return result.strip().split("\n\n")
    except Exception as e:
        st.warning(f"Flashcard generation failed: {e}")
        return []

def get_latest_news(url, max_items=3):
    return feedparser.parse(url).entries[:max_items]

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
