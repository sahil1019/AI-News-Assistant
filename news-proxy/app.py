import requests
from flask import Flask, request, Response

app = Flask(__name__)
ALLOWED_PREFIX = "https://news.google.com/rss"
CORS = {"Access-Control-Allow-Origin": "*"}


@app.get("/")
def proxy():
    """Fetch a Google News RSS URL server-side and return it with CORS enabled."""
    url = request.args.get("url", "")
    if not url.startswith(ALLOWED_PREFIX):
        return Response("Only Google News RSS URLs are allowed", 400, CORS)
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        headers = {**CORS, "Content-Type": "application/xml; charset=utf-8",
                   "Cache-Control": "public, max-age=300"}
        return Response(r.content, r.status_code, headers)
    except requests.RequestException:
        return Response("Upstream error", 502, CORS)


@app.get("/health")
def health():
    return Response("ok", 200, CORS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
