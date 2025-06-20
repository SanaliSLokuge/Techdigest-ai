import os
import streamlit as st
from educhain import Educhain, LLMConfig
from langchain_openai import ChatOpenAI  # OpenAI‑compatible wrapper

# 1️⃣ Set your OpenRouter API key & base URL
os.environ["OPENAI_API_KEY"]  = "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"
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

# 2️⃣ Initialize LangChain’s ChatOpenAI, pointing at OpenRouter
openrouter_model = ChatOpenAI(
    model_name="openai/gpt-3.5-turbo",          # or any model you have access to on OpenRouter
    openai_api_key=os.environ["OPENAI_API_KEY"],
    openai_api_base=os.environ["OPENAI_API_BASE"]
)

# 3️⃣ Wrap it in Educhain
llm_config = LLMConfig(custom_model=openrouter_model)
client     = Educhain(llm_config)

# 4️⃣ Now use `client` exactly as before (generate_questions, generate_summary, etc.)
st.title("EduChain + OpenRouter Demo")
topic = st.text_input("Topic", "Solar System")
if st.button("Generate MCQs"):
    with st.spinner("Calling OpenRouter…"):
        mcqs = client.qna_engine.generate_questions(
            topic=topic, num=3, question_type="Multiple Choice"
        )
        st.json(mcqs.model_dump())
