#!/usr/bin/env python3
"""Vaultweaver BM25 search engine.

Usage:
    python search.py <wiki_dir> "query"           Search the wiki
    python search.py <wiki_dir> --serve            Web UI at localhost:5000
    python search.py <wiki_dir> --serve --port N   Custom port
    python search.py <wiki_dir> --stats            Index statistics
    python search.py <wiki_dir> --json "query"     JSON output
    python search.py --help                        This help text

Flags:
    --help      Show this help
    --json      Output results as JSON
    --stats     Show index statistics
    --serve     Start web search UI
    --port N    Port for web UI (default: 5000)
    --top N     Number of results (default: 10)
"""

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


class WikiSearch:
    """BM25 search over a directory of markdown files. Stdlib only."""

    def __init__(self, wiki_dir):
        self.wiki_dir = Path(wiki_dir)
        self.docs = {}
        self.index = defaultdict(dict)
        self.doc_lengths = {}
        self.avg_dl = 0
        self.k1 = 1.5
        self.b = 0.75
        self._build()

    def _tokenize(self, text):
        text = re.sub(r"```[\s\S]*?```", " ", text)
        text = re.sub(r"---[\s\S]*?---", " ", text)
        text = re.sub(r"https?://\S+", " ", text)
        text = re.sub(r"[#*\[\](){}|`>~_]", " ", text)
        return [w.lower() for w in re.findall(r"\w{2,}", text)]

    def _build(self):
        if not self.wiki_dir.exists():
            return
        skip = {"log.md", "health-report.md", "schema.md"}
        for md in self.wiki_dir.rglob("*.md"):
            if md.name in skip:
                continue
            rel = str(md.relative_to(self.wiki_dir))
            content = md.read_text(encoding="utf-8", errors="replace")
            self.docs[rel] = content
            tokens = self._tokenize(content)
            self.doc_lengths[rel] = len(tokens)
            for term, count in Counter(tokens).items():
                self.index[term][rel] = count
        if self.doc_lengths:
            self.avg_dl = sum(self.doc_lengths.values()) / len(self.doc_lengths)

    def search(self, query, top_k=10):
        terms = self._tokenize(query)
        if not terms or not self.docs:
            return []
        scores = defaultdict(float)
        n = len(self.docs)
        for term in terms:
            if term not in self.index:
                continue
            df = len(self.index[term])
            idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
            for doc, tf in self.index[term].items():
                dl = self.doc_lengths[doc]
                denom = tf + self.k1 * (1 - self.b + self.b * dl / max(self.avg_dl, 1))
                scores[doc] += idf * (tf * (self.k1 + 1)) / denom
        ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
        term_set = set(terms)
        return [
            {
                "path": path,
                "title": self._title(self.docs[path], path),
                "score": round(score, 3),
                "snippet": self._snippet(self.docs[path], term_set),
            }
            for path, score in ranked
        ]

    def _title(self, content, path):
        for line in content.split("\n"):
            s = line.strip()
            if s.startswith("# ") and "---" not in s:
                return s[2:].strip()
        return Path(path).stem.replace("-", " ").replace("_", " ").title()

    def _snippet(self, content, terms, max_len=200):
        best, best_score = "", 0
        for line in content.split("\n"):
            score = sum(1 for t in terms if t in line.lower())
            if score > best_score:
                clean = re.sub(r"[#*\[\](){}|`>~_]", "", line).strip()
                if clean and not clean.startswith("---"):
                    best, best_score = clean, score
        if best:
            return best[:max_len] + ("..." if len(best) > max_len else "")
        in_fm = False
        for line in content.split("\n"):
            s = line.strip()
            if s == "---":
                in_fm = not in_fm
                continue
            if in_fm:
                continue
            clean = re.sub(r"[#*\[\](){}|`>~_]", "", s).strip()
            if clean:
                return clean[:max_len]
        return ""

    def stats(self):
        return {
            "documents": len(self.docs),
            "terms": len(self.index),
            "tokens": sum(self.doc_lengths.values()),
            "avg_doc_len": round(self.avg_dl, 1),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Vaultweaver BM25 search engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("wiki_dir", help="Path to wiki/ directory")
    parser.add_argument("query", nargs="?", default="", help="Search query")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--stats", action="store_true", help="Index statistics")
    parser.add_argument("--serve", action="store_true", help="Start web UI")
    parser.add_argument("--port", type=int, default=5000, help="Web UI port")
    parser.add_argument("--top", type=int, default=10, help="Number of results")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    engine = WikiSearch(args.wiki_dir)

    if args.stats:
        s = engine.stats()
        if args.json:
            print(json.dumps(s, indent=2))
        else:
            print(f"{s['documents']} docs, {s['terms']} terms, {s['tokens']} tokens, avg {s['avg_doc_len']} tokens/doc")
        return

    if args.serve:
        serve(engine, args.wiki_dir, args.port)
        return

    if not args.query:
        parser.print_help()
        sys.exit(2)

    results = engine.search(args.query, top_k=args.top)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    if not results:
        print("No results.")
        sys.exit(0)

    s = engine.stats()
    print(f"Searched {s['documents']} docs, {s['terms']} terms\n")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r['score']}] {r['title']}")
        print(f"     {r['path']}")
        if r["snippet"]:
            print(f"     {r['snippet']}")
        print()


SEARCH_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vaultweaver Search</title>
<style>
:root{--bg:#1a1a2e;--sf:#16213e;--bd:#0f3460;--tx:#e0e0e0;--dm:#8892a4;--ac:#e94560;--lk:#53a8b6}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'SF Mono','Fira Code','Cascadia Code',monospace;background:var(--bg);color:var(--tx);padding:2rem;min-height:100vh}
.c{max-width:800px;margin:0 auto}
h1{font-size:1.4rem;color:var(--ac);margin-bottom:.5rem;letter-spacing:-.5px}
.st{font-size:.75rem;color:var(--dm);margin-bottom:1rem}
form{display:flex;gap:.5rem;margin-bottom:2rem}
input[type=text]{flex:1;padding:.6rem 1rem;background:var(--sf);border:1px solid var(--bd);border-radius:6px;color:var(--tx);font-family:inherit;font-size:.9rem;outline:none;transition:border-color .2s}
input:focus{border-color:var(--ac)}
button{padding:.6rem 1.2rem;background:var(--ac);border:none;border-radius:6px;color:#fff;font-family:inherit;font-size:.9rem;cursor:pointer;transition:opacity .2s}
button:hover{opacity:.85}
.r{margin-bottom:1.5rem;padding:1rem;background:var(--sf);border:1px solid var(--bd);border-radius:8px;transition:border-color .2s}
.r:hover{border-color:var(--ac)}
.rt{font-size:1rem;font-weight:600}.rt a{color:var(--lk);text-decoration:none}.rt a:hover{text-decoration:underline}
.rs{font-size:.7rem;color:var(--ac);background:rgba(233,69,96,.15);padding:.15rem .4rem;border-radius:3px;margin-left:.5rem}
.rp{font-size:.75rem;color:var(--dm);margin:.3rem 0 .5rem}
.rx{font-size:.85rem;color:var(--dm);line-height:1.5}
.e{color:var(--dm);text-align:center;padding:3rem 0;font-style:italic}
</style></head><body>
<div class="c">
<h1>vaultweaver search</h1>
<div class="st">{{ stats.documents }} docs / {{ stats.terms }} terms / {{ stats.tokens }} tokens</div>
<form method="get"><input type="text" name="q" value="{{ query }}" placeholder="Search the wiki..." autofocus><button>Search</button></form>
{% if query %}{% if results %}{% for r in results %}
<div class="r"><div class="rt"><a href="/page/{{ r.path }}">{{ r.title }}</a><span class="rs">{{ r.score }}</span></div>
<div class="rp">{{ r.path }}</div><div class="rx">{{ r.snippet }}</div></div>
{% endfor %}{% else %}<div class="e">No results for "{{ query }}"</div>{% endif %}
{% else %}<div class="e">Type a query to search all wiki pages</div>{% endif %}
</div></body></html>"""


def serve(engine, wiki_dir, port):
    try:
        from flask import Flask, render_template_string, request
    except ImportError:
        print("Flask required for web UI: pip install flask", file=sys.stderr)
        sys.exit(1)

    app = Flask(__name__)

    @app.route("/")
    def index():
        q = request.args.get("q", "").strip()
        results = engine.search(q, top_k=20) if q else []
        return render_template_string(
            SEARCH_HTML, query=q, results=results, stats=engine.stats()
        )

    @app.route("/page/<path:page_path>")
    def view_page(page_path):
        full = Path(wiki_dir) / page_path
        if not full.exists() or full.suffix != ".md":
            return "Not found", 404
        content = full.read_text(encoding="utf-8", errors="replace")
        return f"<pre style='font-family:monospace;padding:2rem;background:#1a1a2e;color:#e0e0e0;min-height:100vh;white-space:pre-wrap'>{content}</pre>"

    print(f"Vaultweaver search at http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
