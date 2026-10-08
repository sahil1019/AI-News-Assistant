import os
import requests
from flask import Flask, request, Response, send_from_directory

app = Flask(__name__, static_folder=None)
HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS = "hl=en-IN&gl=IN&ceid=IN:en"
TOP = {"", "top", "top news", "headlines", "top headlines", "news", "latest news"}


@app.get("/")
def index():
    return send_from_directory(HERE, "index.html")


@app.get("/api/news")
def news():
    """Fetch Google News RSS server-side and return the raw XML."""
    q = request.args.get("q", "").strip()
    if q.lower() in TOP:
        url = f"https://news.google.com/rss?{PARAMS}"
    else:
        url = "https://news.google.com/rss/search"
    try:
        r = requests.get(
            url,
            params=None if q.lower() in TOP else {"q": q, "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        return Response(r.content, r.status_code, {
            "Content-Type": "application/xml; charset=utf-8",
            "Cache-Control": "public, max-age=300",
        })
    except requests.RequestException:
        return Response("Upstream error", 502)


@app.get("/health")
def health():
    return Response("ok", 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
