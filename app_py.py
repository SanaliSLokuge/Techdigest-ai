import streamlit as st
from educhain import Educhain, LLMConfig
from langchain_openai import ChatOpenAI  # For OpenAI GPT
# from langchain_google_genai import ChatGoogleGenerativeAI  # For Gemini (if you have keys)

# -------------- Config ----------------
OPENAI_API_KEY = "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"  # Replace with your actual key

# Setup custom LLM config with OpenAI GPT-4
openai_model = ChatOpenAI(
    model_name="gpt-4.1",
    openai_api_key=OPENAI_API_KEY
)
llm_config = LLMConfig(custom_model=openai_model)

# Initialize Educhain client
client = Educhain(llm_config)

# -------------- Streamlit UI --------------
st.set_page_config(page_title="EduChain Demo", layout="wide")

st.title("EduChain Q&A Generation Demo")

topic = st.text_input("Enter a topic for MCQ generation", "Solar System")
num_questions = st.slider("Number of questions to generate", min_value=1, max_value=10, value=3)
difficulty = st.selectbox("Select difficulty level", ["Easy", "Medium", "Hard"])

if st.button("Generate Questions"):
    with st.spinner("Generating questions..."):
        try:
            mcqs = client.qna_engine.generate_questions(
                topic=topic,
                num=num_questions,
                question_type="Multiple Choice",
                difficulty_level=difficulty
            )
            st.success("Questions generated successfully!")
            # Display questions JSON
            st.json(mcqs.model_dump())
        except Exception as e:
            st.error(f"Failed to generate questions: {e}")

st.markdown("---")
st.caption("EduChain powered by OpenAI GPT-4 API")
