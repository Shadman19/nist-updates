import os
from datetime import datetime
from dotenv import load_dotenv
import argparse
from app.agents.workflow import run_pipeline
from app.publishers.github_pr import create_pr_with_file
def main():
    load_dotenv()
    p=argparse.ArgumentParser()
    p.add_argument("--topk", type=int, default=10)
    p.add_argument("--no_pr", action="store_true")
    p.add_argument("--out_dir", default="updates")
    args=p.parse_args()
    res=run_pipeline(top_k=args.topk)
    os.makedirs(args.out_dir, exist_ok=True)
    date=datetime.utcnow().strftime("%Y-%m-%d")
    out_path=os.path.join(args.out_dir, f"{date}.md")
    with open(out_path,"w",encoding="utf-8") as f: f.write(res.summary_markdown)
    print(f"Summary written to {out_path}")
    if not args.no_pr:
        repo=os.getenv("GITHUB_REPO"); token=os.getenv("GITHUB_TOKEN")
        if not repo or not token: 
            print("Missing GITHUB_REPO or GITHUB_TOKEN, skipping PR"); return
        url=create_pr_with_file(repo=repo, token=token, file_path=out_path,
                                pr_title=f"NIST SP 800 Updates — {date}",
                                pr_body="Automated summary for recent SP 800 items.")
        print(f"Opened PR: {url}")
if __name__=="__main__": main()
