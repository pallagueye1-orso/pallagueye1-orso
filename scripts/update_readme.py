"""Met à jour la section « Tous mes dépôts » du README du profil GitHub."""
import json
import os
import re
import urllib.request

USER = "pallagueye1-orso"
PROFILE_REPO = "pallagueye1-orso"
# Projets déjà détaillés à la main dans « Projets phares » : on ne les répète pas.
FEATURED = {"education-employment-analysis", "jeu_donnees_YUKA", "bidabi-clone-alone"}
START, END = "<!--REPOS:START-->", "<!--REPOS:END-->"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def get(url, raw=False):
    headers = {
        "Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json",
        "User-Agent": "readme-updater",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read().decode("utf-8", "replace")
    return data if raw else json.loads(data)


def first_paragraph(repo):
    """Première phrase du README du dépôt, utilisée si le dépôt n'a pas de description."""
    try:
        text = get(f"https://api.github.com/repos/{USER}/{repo}/readme", raw=True)
    except Exception:
        return ""
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "<", "!", "[", "`", "-", "*", ">", "|")):
            return line[:140]
    return ""


def build_block():
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated")
    rows = []
    for repo in repos:
        if repo["fork"] or repo["archived"]:
            continue
        if repo["name"] in FEATURED or repo["name"] == PROFILE_REPO:
            continue
        description = repo.get("description") or first_paragraph(repo["name"]) or "—"
        description = description.replace("|", "\\|")
        language = repo.get("language") or "—"
        updated = repo["pushed_at"][:7]
        rows.append(f"| [{repo['name']}]({repo['html_url']}) | {description} | {language} | {updated} |")
    if not rows:
        return "_D’autres projets arrivent bientôt._"
    header = "| Dépôt | Description | Langage | Mis à jour |\n|:--|:--|:--|:--|"
    return header + "\n" + "\n".join(rows)


def main():
    block = build_block()
    with open("README.md", encoding="utf-8") as f:
        content = f.read()
    pattern = re.escape(START) + r".*?" + re.escape(END)
    updated = re.sub(pattern, lambda _: f"{START}\n{block}\n{END}", content, flags=re.S)
    if updated != content:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated)


if __name__ == "__main__":
    main()
