import os
import base64
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI(title="GitHub Onboarding Assistant")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_client = Groq(api_key=GROQ_API_KEY)

class RepoRequest(BaseModel):
    repo_url: str

def parse_repo_url(url: str):
    parts = url.rstrip("/").split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    owner, repo = parts[-2], parts[-1]
    return owner, repo

def github_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

def fetch_repo_tree(owner: str, repo: str):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=github_headers())
    if r.status_code != 200:
        raise HTTPException(status_code=404, detail="Repo not found, private, or rate-limited")
    default_branch = r.json()["default_branch"]

    r2 = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1",
        headers=github_headers(),
    )
    tree = r2.json().get("tree", [])
    files = [item["path"] for item in tree if item["type"] == "blob"]
    return files, default_branch

def fetch_readme(owner: str, repo: str) -> str:
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/readme", headers=github_headers())
    if r.status_code != 200:
        return ""
    content = r.json().get("content", "")
    try:
        return base64.b64decode(content).decode("utf-8", errors="ignore")
    except Exception:
        return ""

def fetch_file_content(owner: str, repo: str, path: str, branch: str) -> str:
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}",
        headers=github_headers(),
    )
    if r.status_code != 200:
        return ""
    data = r.json()
    if data.get("encoding") == "base64":
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        except Exception:
            return ""
    return ""

KEY_FILE_HINTS = [
    "package.json", "requirements.txt", "pyproject.toml", "main.py", "app.py",
    "index.js", "index.ts", "server.js", "manage.py", "Dockerfile", "docker-compose.yml",
]


@app.get("/")
def health_check():
    return {"status": "ok", "message": "GitHub Onboarding Assistant API is running"}

@app.post("/analyze-repo")
def analyze_repo(req: RepoRequest):
    owner, repo = parse_repo_url(req.repo_url)
    files, branch = fetch_repo_tree(owner, repo)
    readme = fetch_readme(owner, repo)

    key_files_found = [f for f in files if os.path.basename(f) in KEY_FILE_HINTS]
    key_contents = {}
    for f in key_files_found[:5]:
        key_contents[f] = fetch_file_content(owner, repo, f, branch)[:3000]

    prompt = build_prompt(repo, readme, files, key_contents)

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a senior engineer writing a friendly onboarding guide for a new open-source contributor."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    guide = completion.choices[0].message.content

    return {
        "repo": f"{owner}/{repo}",
        "file_count": len(files),
        "file_tree": files[:300],
        "key_files_analyzed": list(key_contents.keys()),
        "onboarding_guide": guide,
    }

def build_prompt(repo: str, readme: str, files: list, key_contents: dict) -> str:
    tree_preview = "\n".join(files[:150])
    key_files_text = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in key_contents.items()
    )
    return f"""
    Repository: {repo}

    README:{readme[:4000]}

    File tree (partial):
    {tree_preview}

    Key file contents:
    {key_files_text}

"""