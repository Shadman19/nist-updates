import random, string
from typing import Optional
from github import Github
def _rand_branch(prefix="nist-updates/") -> str:
    s="".join(random.choice(string.ascii_lowercase+string.digits) for _ in range(6))
    return f"{prefix}{s}"
def create_pr_with_file(repo: str, token: str, file_path: str,
                        base_branch: str = "main",
                        commit_message: str = "Add NIST SP 800 summary",
                        pr_title: str = "NIST SP 800 Updates",
                        pr_body: str = "Automated summary PR.") -> Optional[str]:
    g=Github(token); r=g.get_repo(repo)
    base=r.default_branch or base_branch
    sha=r.get_branch(base).commit.sha
    branch=_rand_branch(); r.create_git_ref(ref=f"refs/heads/{branch}", sha=sha)
    with open(file_path,"r",encoding="utf-8") as f: content=f.read()
    try: r.create_file(file_path, commit_message, content, branch=branch)
    except Exception:
        existing=r.get_contents(file_path, ref=branch)
        r.update_file(file_path, commit_message, content, sha=existing.sha, branch=branch)
    pr=r.create_pull(title=pr_title, body=pr_body, head=branch, base=base); return pr.html_url
