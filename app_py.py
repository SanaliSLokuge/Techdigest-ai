import requests
import feedparser
import os
from educhain import Educhain

# Your OpenRouter API key and base
API_KEY = "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"
API_BASE = "https://openrouter.ai/v1"

# Set environment for Educhain
os.environ["OPENAI_API_KEY"] = API_KEY
os.environ["OPENAI_API_BASE"] = API_BASE
os.environ["EDUCHAIN_MODEL"] = "openrouter/llama3"

# Educhain client
educhain_client = Educhain()

def generate_summary(text):
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/o4-mini",  # fixed here
        "messages": [{"role": "user", "content": f"Summarize the following text briefly:\n\n{text}"}],
        "max_tokens": 150,
        "temperature": 0.3
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

# Demo run
feed_url = "https://techcrunch.com/feed/"
news = get_latest_news(feed_url, 3)

for idx, (title, content) in enumerate(news, 1):
    print(f"Article {idx}: {title}\n")

    summary = generate_summary(content)
    print(f"Summary:\n{summary}\n")

    flashcards = generate_flashcards(content)
    print("Flashcards:")
    for card in flashcards:
        print(f"Q: {card.question}")
        for opt in card.options:
            print(f" - {opt}")
        print(f"Answer: {card.answer}\n")
    print("-----\n")
