import re, urllib.parse
from datetime import datetime

import feedparser
import gradio as gr
import torch
import wikipedia
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL = "sshleifer/distilbart-cnn-12-6"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL).eval()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model.to(DEVICE)

TOP_WORDS = {"", "top", "top news", "headlines", "top headlines", "news", "latest news"}


def split_title_source(title: str):
    if " - " in title:
        head, src = title.rsplit(" - ", 1)
        return head.strip(), src.strip()
    return title.strip(), ""


def chunk_text(text: str, max_chars: int = 900):
    chunks, current = [], ""
    for s in re.split(r"(?<=[.!?])\s+", text):
        if current and len(current) + len(s) > max_chars:
            chunks.append(current.strip())
            current = ""
        current += s + " "
    if current.strip():
        chunks.append(current.strip())
    return chunks


def safe_summarize(chunk: str):
    inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=1024).to(model.device)
    n = inputs["input_ids"].shape[1]
    if n < 30:
        return chunk
    max_len = max(20, min(100, int(n * 0.6)))
    min_len = max(10, min(40, max_len - 10))
    with torch.no_grad():
        ids = model.generate(**inputs, max_length=max_len, min_length=min_len,
                             num_beams=4, do_sample=False, early_stopping=True)
    return tokenizer.decode(ids[0], skip_special_tokens=True)


def fetch_google_news_rss(query: str, country="IN", max_items=10):
    try:
        base = "https://news.google.com/rss"
        params = f"hl=en-{country}&gl={country}&ceid={country}:en"
        if query.strip().lower() in TOP_WORDS:
            url = f"{base}?{params}"
        else:
            url = f"{base}/search?q={urllib.parse.quote_plus(query)}&{params}"
        feed = feedparser.parse(url)
        items = []
        for e in feed.entries[:max_items]:
            head, src = split_title_source(e.get("title", ""))
            src = (e.get("source", {}) or {}).get("title", src)
            items.append({"title": head, "source": src, "link": e.get("link", "")})
        return items
    except Exception:
        return []


def wikipedia_fallback(query: str):
    for title in wikipedia.search(query)[:3]:
        try:
            page = wikipedia.page(title, auto_suggest=False)
            return page.content[:2500], page.url
        except Exception:
            continue
    return None, None


def ask_news(query, history=None):
    try:
        query = (query or "").strip()
        items = fetch_google_news_rss(query)
        timestamp = datetime.now().strftime("%d %b %Y, %H:%M")

        if items:
            text = ". ".join(it["title"].rstrip(".") for it in items) + "."
            chunks = chunk_text(text)
            summary = " ".join(safe_summarize(c) for c in chunks)
            lines = [
                f"{i}. [{it['title']}]({it['link']})"
                + (f" — *{it['source']}*" if it["source"] else "")
                for i, it in enumerate(items[:8], 1)
            ]
            return (
                f"📰 **Inshorts-style Summary:** {summary}\n\n"
                f"🔗 **Headlines:**\n" + "\n".join(lines) + "\n\n"
                f"💡 *Summarized from {len(items)} live Google News headlines "
                f"using {MODEL.split('/')[-1]}.*\n🕒 {timestamp} (server time)"
            )

        text, url = wikipedia_fallback(query)
        if not text:
            return "😕 Sorry, no recent news found for that query."
        summary = " ".join(safe_summarize(c) for c in chunk_text(text)[:3])
        return (f"📚 *No recent news found, here's a background summary:*\n\n{summary}\n\n"
                f"🔗 {url}\n🕒 {timestamp} (server time)")
    except Exception as e:
        return f"⚠️ Error: {e}"


demo = gr.ChatInterface(
    fn=ask_news,
    title="🧠 Inshorts-style AI News Assistant",
    description="Ask for the latest news on any topic. Type 'top headlines' for general news.",
    examples=[["Top headlines"], ["World news"], ["AI trends"],
              ["Space exploration"], ["Indian politics"]],
)

if __name__ == "__main__":
    demo.launch()
