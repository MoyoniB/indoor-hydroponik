import os, csv, datetime, json, re, textwrap, pathlib, openai
openai.api_key = os.environ["OPENAI_API_KEY"]

ROOT = pathlib.Path(__file__).parent.parent
POSTS_DIR = ROOT / "_posts"
CSV_FILE  = ROOT / "top50_keywords.csv"
LOG_FILE  = ROOT / "scripts/generated.json"
done = json.loads(LOG_FILE.read_text()) if LOG_FILE.exists() else []

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]

with open(CSV_FILE) as f:
    for kw in [r["keyword"] for r in csv.DictReader(f) if r["keyword"] not in done]:
        today = datetime.date.today().isoformat()
        md_file = POSTS_DIR / f"{today}-{slug(kw)}.md"

        prompt = f"Schreibe einen 900-Wörter Blogpost über {kw} ..."
        txt = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        ).choices[0].message.content.strip()

        md = f"""---
title: "{kw.title()}"
date: {today}
layout: post
tags: [hydroponik, indoor]
---

{txt}
"""
        md_file.write_text(textwrap.dedent(md))
        done.append(kw)
        if len(done) % 5 == 0:
            break

LOG_FILE.write_text(json.dumps(done, ensure_ascii=False, indent=2))
