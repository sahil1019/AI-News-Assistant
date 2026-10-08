# 🧠 AI News Assistant

An Inshorts-style news assistant: it pulls **live Google News RSS** headlines (no API key) and condenses them into a short summary with a **DistilBART** summarization model.

| Part | Folder | Stack |
|---|---|---|
| Original app (chatbot UI) | [`python-gradio/`](python-gradio) + Colab notebook | Python, Gradio, Hugging Face Transformers, PyTorch, feedparser, Wikipedia fallback |
| Live browser demo | [`web-demo/`](web-demo) | HTML/JS, Transformers.js (in-browser DistilBART), hosted on Hugging Face Spaces (static) |
| News proxy | [`news-proxy/`](news-proxy) | Python, Flask, gunicorn, hosted on Render |

**Live demo:** _add your Hugging Face Space link here_

## How it works
1. Query → Google News RSS (server-side Flask proxy for the browser version, direct `feedparser` in the Python version).
2. Headlines are cleaned and chunked.
3. DistilBART summarizes each chunk → short "Inshorts-style" summary + clickable source links.
4. If no news is found, it falls back to a Wikipedia summary.

## Run the Python/Gradio version
```bash
cd python-gradio
pip install -r requirements.txt
python app.py
```
Or with Docker:
```bash
cd python-gradio
docker build -t news-assistant .
docker run -p 7860:7860 news-assistant
```
Or open the notebook in Google Colab.

## Challenges solved
- Fixed `transformers` version break (`summarization` pipeline removed) by loading the model with `AutoModelForSeq2SeqLM` directly.
- Google News RSS summaries are HTML duplicates of the title → stripped and summarized clean headlines instead.
- Scaled `max_length` to input size to stop BART warnings/crashes on short chunks.
- Hugging Face moved Gradio Spaces behind a paid plan → ported the UI to a static, in-browser Transformers.js version and added a Flask proxy to get around browser CORS limits.
