import requests, trafilatura
from markdownify import markdownify as md
def extract_markdown(url: str) -> str:
    try:
        html = requests.get(url, timeout=30).text
        mdown = md(html, heading_style="ATX")
        clean = trafilatura.extract(html, include_tables=True) or ""
        return mdown if len(mdown)>=len(clean) else clean
    except Exception:
        return f"(Could not extract content from {url})"
