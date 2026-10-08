# 🧠 AI News Assistant

An Inshorts-style news assistant: it pulls **live Google News RSS** headlines (no API key) and condenses them into a short summary with a **DistilBART** summarization model.

| Part | Folder | Stack |
|---|---|---|
| Original app (chatbot UI) | [`python-gradio/`](python-gradio) + Colab notebook | Python, Gradio, Hugging Face Transformers, PyTorch, feedparser, Wikipedia fallback |
| Live web app (deployed on Render) | [`render-app/`](render-app) | Python/Flask backend + HTML/JS frontend, Transformers.js (in-browser DistilBART) |

**Live demo:** _add your Render link here_

## How it works
1. Query → Google News RSS (fetched server-side by a Flask endpoint `/api/news` in the web app, direct `feedparser` in the Python version).
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
- Free hosting has ~512 MB RAM, too small for PyTorch → built a web version where a small Flask server fetches news and the summarization model runs in the visitor's browser (Transformers.js), deployed on Render's free tier.
