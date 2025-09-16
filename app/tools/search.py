import requests, re
from bs4 import BeautifulSoup
from typing import List, Dict
INDEX = "https://csrc.nist.gov/publications/sp800"
def _fetch(url: str) -> str:
    r = requests.get(url, timeout=30); r.raise_for_status(); return r.text
def _parse_index(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser"); items=[]
    for a in soup.find_all("a", href=True):
        text=" ".join(a.get_text(" ", strip=True).split())
        if text and re.search(r"\bSP\s*800-\d+\b", text, flags=re.I):
            url=a["href"]; 
            if url.startswith("/"): url=f"https://csrc.nist.gov{url}"
            row=a.find_parent(["div","li","tr"]) or a; date=None
            if row:
                m=re.search(r"(20\d{2}|19\d{2})", row.get_text(" ", strip=True))
                if m: date=m.group(1)
            items.append({"title":text,"url":url,"date":date})
    seen,out=set(),[]
    for it in items:
        if it["url"] in seen: continue
        seen.add(it["url"]); out.append(it)
    return out
def search_latest_items(top_k: int = 10) -> List[Dict]:
    try: items=_parse_index(_fetch(INDEX))
    except Exception: items=[]
    seeds=[{"title":"SP 800-171 Rev. 3 (Final)","url":"https://csrc.nist.gov/pubs/sp/800/171/r3/final","date":"2024-05-14"},
           {"title":"SP 800-53 (Rev. 5)","url":"https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final","date":"2020"}]
    seen,out=set(),[]
    for it in seeds+items:
        if it["url"] in seen: continue
        seen.add(it["url"]); out.append(it)
    return out[:top_k]
