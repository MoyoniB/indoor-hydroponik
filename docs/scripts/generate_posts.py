import os, csv, datetime, json, re, textwrap, pathlib
from openai import OpenAI   # neue Client-Klasse ab openai-python 1.x

# ➊ API-Key aus GitHub-Secret ziehen
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ➋ Pfade
ROOT      = pathlib.Path(__file__).parent.parent
POSTS_DIR = ROOT / "_posts"
CSV_FILE  = ROOT / "top50_keywords.csv"
LOG_FILE  = ROOT / "scripts/generated.json"

POSTS_DIR.mkdir(exist_ok=True)      # falls Ordner noch nicht da
done = json.loads(LOG_FILE.read_text()) if LOG_FILE.exists() else []

# ➌ Hilfsfunktion: hübsche URL-Slugs
def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]

# ➍ Hauptschleife: Keywords abarbeiten
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        kw = row["keyword"]
        if kw in done:
            continue                 # bereits veröffentlicht

        today = datetime.date.today().isoformat()
        md_file = POSTS_DIR / f"{today}-{slug(kw)}.md"

        # ➎ OpenAI-Aufruf
        prompt = (
            f"Schreibe einen SEO-optimierten Blogpost (≈900 Wörter) "
            f"zum Keyword „{kw}“ mit H2-Abschnitten, einer Tabelle, "
            f"und einem FAQ-Abschnitt im Schema.org-FAQ-Format."
        )

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        txt = resp.choices[0].message.content.strip()

        # ➏ Markdown-Datei bauen
        md = f"""---
title: "{kw.title()}"
date: {today}
description: "Indoor-Hydroponik: {kw}"
tags: [hydroponik, indoor]
layout: post
---

{txt}
"""
        md_file.write_text(textwrap.dedent(md), encoding="utf-8")

        done.append(kw)

        # pro Lauf max. 5 Artikel
        if len(done) % 5 == 0:
            break

# ➐ Log aktualisieren
LOG_FILE.write_text(json.dumps(done, ensure_ascii=False, indent=2), encoding="utf-8")
