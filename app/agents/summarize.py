import os, textwrap, json, time, requests
from typing import List, Dict
from datetime import datetime

SYSTEM = ("You are a cybersecurity analyst for software teams. "
          "Return one page Markdown about SSDF (SP 800-218), SDLC/CI/CD, cloud native/IaC, "
          "SBOM and supply chain, CUI and PII, mapped to 800-53 and 800-171.")

def _pack(items: List[Dict]) -> str:
    blocks=[]
    # Keep inputs lean to avoid token bloat & 429s
    for it in items:
        body = (it.get('markdown','') or '').replace('\n', ' ')
        blocks.append(
            f"- TITLE: {it.get('title','')}\n"
            f"  DATE: {it.get('date','')}\n"
            f"  URL: {it.get('url','')}\n"
            f"  MARKDOWN:\n{body[:1500]}\n---"
        )
    return "\n".join(blocks)

def _chat(messages, key: str) -> str:
    url = os.getenv("OPENAI_API_BASE", "https://api.openai.com") + "/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = {"model": "gpt-4o-mini", "messages": messages, "temperature": 0.2}
    # Exponential backoff with Retry-After support
    for attempt in range(6):
        r = requests.post(url, headers=headers, data=json.dumps(data), timeout=90)
        if r.status_code in (429, 500, 502, 503, 504):
            ra = r.headers.get("retry-after")
            base = int(ra) if (ra and ra.isdigit()) else 2
            wait = min(base * (2 ** attempt), 30)
            time.sleep(wait); continue
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    raise RuntimeError("Exhausted retries")

def _fallback(items: List[Dict]) -> str:
    date = datetime.utcnow().strftime("%Y-%m-%d")
    lines = [f"# NIST SP 800 Updates — {date}",
             "*Offline brief generated due to API limits; content filtered for software relevance.*",
             "", "## Highlights"]
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. **{it.get('title','')}** ({it.get('date','')}) — {it.get('url','')}")
    lines += ["", "## Why it matters for software teams",
              "- Focuses on SSDF/SDLC, CI/CD pipelines, cloud/IaC, SBOM/supply chain, and protection of CUI/PII.",
              "- Use updates to harden build, release, and runtime controls and align with auditors.",
              "", "## Action checklist (with mappings)",
              "- Enforce artifact signing in CI/CD  **[SSDF PW/RV; NIST 800-53 CM/SA]**",
              "- Maintain SBOM per release; verify dependencies  **[SSDF PW; 800-53 CM-8; 800-171 3.4.1]**",
              "- Scan IaC and enforce least privilege in cloud  **[SSDF RV; 800-53 AC/SC; 800-171 3.1]**",
              "- Protect CUI/PII at rest and in transit  **[800-171 3.13; 800-53 SC-12/SC-13]**",
              "- Map controls to policy/runbooks and track evidence.",
              "", "## Citations"]
    for i, it in enumerate(items, 1):
        lines.append(f"[{i}] {it.get('url','')}")
    return "\n".join(lines)

def summarize(items: List[Dict]) -> str:
    key = os.getenv("OPENAI_API_KEY")
    user = textwrap.dedent(f"""
    From the items below, keep only parts relevant to software and IT (SSDF, SDLC/CI/CD,
    cloud native and IaC, SBOM, CUI and PII). Write a one page Markdown (~500 words) that includes:
    - What changed (doc + date/version)
    - Why it matters for software teams
    - Action checklist with [control mappings] to 800-53, 800-171, and SSDF
    - Numbered citations with URLs

    INPUT ITEMS:
    {_pack(items)}
    """)
    if not key:
        return _fallback(items)
    try:
        return _chat([{"role":"system","content":SYSTEM},{"role":"user","content":user}], key)
    except Exception:
        return _fallback(items)
