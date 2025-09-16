from typing import List, Dict, Any
from dataclasses import dataclass
from app.tools.search import search_latest_items
from app.extractors.content import extract_markdown
from app.agents.summarize import summarize
@dataclass
class Result:
    items: List[Dict[str, Any]]
    summary_markdown: str
def run_pipeline(top_k: int = 10) -> Result:
    items = search_latest_items(top_k=top_k)
    for it in items: it["markdown"] = extract_markdown(it["url"])
    return Result(items=items, summary_markdown=summarize(items))
