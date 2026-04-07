---
name: vaultweaver
description: "Build and maintain a persistent knowledge base — a compounding vault of interlinked markdown files based on Karpathy's LLM Wiki pattern. TRIGGER when: user adds sources to raw/ (articles, papers, notes, images), pastes content to ingest, says 'add to wiki' or 'ingest this', asks synthesis questions ('what do we know about X', 'compare A and B', 'summarize research on Y'), requests health checks ('lint the wiki', 'find gaps'), or runs /wiki commands. Also triggers when raw/ has unprocessed files. DO NOT TRIGGER when: user asks about project source code or architecture, wants simple file operations, or asks general questions unrelated to a knowledge base."
---

# Vaultweaver

Build a persistent, compounding knowledge base. Sources are ingested once, compiled
into an interconnected wiki of markdown files, and kept current as new material arrives.
The LLM writes and maintains the wiki — the user curates sources and asks questions.

Viewable in Obsidian with graph view and backlinks.

## Decision Tree

```
Does wiki/ exist in current directory?
├── NO → Run INIT (create structure, ask for wiki name)
└── YES
    ├── Are there unprocessed files in raw/?
    │   └── YES → Run INGEST
    ├── Is user adding content or pasting text?
    │   └── YES → Save to raw/, then INGEST
    ├── Is user asking a question about wiki topics?
    │   └── YES → Run QUERY
    ├── Is user asking to compile/build articles?
    │   └── YES → Run COMPILE
    ├── Is user asking for health check?
    │   └── YES → Run LINT
    └── Is user asking to search?
        └── YES → Run SEARCH
```

## Wiki Structure

```
raw/                     User-curated sources (NEVER modify or delete)
wiki/
├── index.md             Categorized page index — update after every change
├── log.md               Parseable activity log — append after every operation
├── overview.md           High-level synthesis of all knowledge (optional)
├── schema.md            Wiki conventions (auto-generated on init)
├── concepts/            Concept and theme articles
├── entities/            Named entities (people, orgs, tools, products)
├── sources/             Source summaries (one per raw file)
└── queries/             Filed Q&A results that compound over time
search.py                BM25 search engine (see scripts/search.py)
```

## Commands

```
/wiki init [name]        Create wiki structure
/wiki ingest             Process new raw/ files
/wiki compile            Build missing concept + entity articles
/wiki query <question>   Answer from wiki, optionally file back
/wiki lint               Health check with fix suggestions
/wiki search <term>      Local BM25 search (runs search.py)
/wiki status             Stats and recent activity
/wiki serve [port]       Web search UI
```

---

## INIT

Create the wiki structure. Ask for wiki name if not provided.

1. Create directories: `raw/`, and under `wiki/`: `concepts/`, `entities/`, `sources/`, `queries/`
2. Write `wiki/index.md`:
   ```markdown
   # {Name} Index
   
   ## Overview
   - [Overview](overview.md) — High-level synthesis (not yet written)
   
   ## Concepts
   (none yet — run /wiki ingest then /wiki compile)
   
   ## Entities
   (none yet)
   
   ## Sources
   (none yet — add files to raw/ then run /wiki ingest)
   
   ## Queries
   (none yet — ask questions with /wiki query)
   ```
3. Write `wiki/log.md`: `# Wiki Log\n`
4. Write `wiki/schema.md` documenting the conventions (copy from Page Conventions below)
5. Copy `search.py` from skill scripts if available
6. Tell user: "Drop source files in `raw/` then say **ingest** or run `/wiki ingest`."

---

## INGEST

Process new sources. **One source should touch 10-15 wiki pages.**

1. **Scan** `raw/` for all files
2. **Identify new** — files not mentioned in `wiki/log.md`
3. **For each new source:**

   a. Read full content (images via multimodal Read tool)

   b. Extract: main claims, named entities, concepts, data points, contradictions with existing wiki

   c. **Write source summary** → `wiki/sources/{slug}.md`:
      ```yaml
      ---
      title: "{Title}"
      type: source
      tags: [topic1, topic2]
      created: {YYYY-MM-DD}
      original: raw/{filename}
      ---
      ```
      Body: structured summary, key quotes, main arguments, relevance to existing topics.

   d. **Create or update concept pages** → `wiki/concepts/{slug}.md`:
      - Existing page: add new information, update synthesis, note confirmations or contradictions
      - New concept: create with definition, context, connections
      - Add `[[wikilinks]]` to related concepts and entities

   e. **Create or update entity pages** → `wiki/entities/{slug}.md`:
      - Existing page: add new data points
      - New entity: create with description, role, connections

   f. **Update cross-references** — ensure new pages link to relevant existing pages and vice versa

   g. **Update `wiki/overview.md`** if the source shifts the big picture

   h. **Update `wiki/index.md`** — add entries for new pages, update summaries for modified pages

   i. **Append to `wiki/log.md`:**
      ```markdown
      ## [{YYYY-MM-DD}] ingest | {Source Title}
      - Source: raw/{filename}
      - Pages created: concepts/new.md, entities/new.md
      - Pages updated: concepts/existing.md, overview.md
      - Total pages touched: {N}
      ```

---

## COMPILE

Build articles for concepts and entities mentioned across sources but lacking their own page.

1. Read all files in `wiki/sources/`
2. Collect every `[[concept]]` and `[[entity]]` referenced
3. Check which already have pages in `wiki/concepts/` and `wiki/entities/`
4. For each **missing** concept or entity, write a page:
   - 300-800 words, encyclopedic, with `[[wikilinks]]` for cross-references
   - Note contradictions between sources
   - Include `## Sources` section citing which source summaries informed it
5. Rebuild `wiki/index.md` — categorize all pages with one-line descriptions and dates
6. Append to log:
   ```markdown
   ## [{YYYY-MM-DD}] compile | {N} new articles
   - Concepts created: {list}
   - Entities created: {list}
   - Index rebuilt
   ```

Skip pages that already exist unless user says "recompile" or "rebuild."

---

## QUERY

Answer questions using the wiki as knowledge source.

1. **Read `wiki/index.md`** — scan for relevant pages
2. **Read relevant pages** — follow `[[wikilinks]]` to gather connected info
3. **Synthesize answer:**
   - Cite wiki pages: `According to [[concepts/x]]...`
   - Note confidence — well-supported (multiple sources) vs. single-source claims
   - Flag contradictions if sources disagree
   - Identify gaps — what the wiki doesn't cover
4. **Decide whether to file:**
   - Synthesizes across multiple pages in a new way? → File in `wiki/queries/`
   - Simple lookup? → Don't file
   - Reveals a new connection? → File and add cross-references
5. **If filing:** write `wiki/queries/{slug}.md` with frontmatter, update index.md
6. **Append to log:**
   ```markdown
   ## [{YYYY-MM-DD}] query | {Question}
   - Pages consulted: concepts/x.md, entities/y.md
   - Answer filed: queries/{slug}.md (or: not filed — simple lookup)
   ```

---

## LINT

Periodic health check. Fix what you can, report what needs user input.

1. **Read all pages** — build a map of the wiki's state
2. **Check for issues:**

   | Check | What to look for |
   |-------|------------------|
   | Contradictions | Two pages making conflicting claims |
   | Stale claims | Older pages superseded by newer sources |
   | Orphan pages | Pages with no inbound `[[wikilinks]]` |
   | Missing concepts | Terms mentioned often but lacking their own page |
   | Broken links | `[[wikilinks]]` to non-existent pages |
   | Data gaps | Topics partially covered — need more sources |
   | Thin pages | Pages with very little content |

3. **Link normalization:** `_` = `-` = ` `, strip path prefixes, case-insensitive, ignore `|display` and `#section`
4. **Fix what you can** — add cross-references, create stubs, update stale claims
5. **Report what needs user input** — suggest sources, flag contradictions needing judgment
6. **Write report** to `wiki/health-report.md`
7. **Append to log:**
   ```markdown
   ## [{YYYY-MM-DD}] lint | Health check
   - Issues found: {N} orphans, {N} contradictions, {N} missing concepts
   - Fixed: added cross-references, created {N} stubs
   - Needs attention: {list}
   - Suggested sources: {list}
   ```

---

## SEARCH

Local BM25 search — no LLM needed.

```bash
python search.py wiki/ "query"              # CLI search
python search.py wiki/ --serve              # Web UI at localhost:5000
python search.py wiki/ --serve --port 8080  # Custom port
python search.py wiki/ --stats              # Index statistics
```

---

## STATUS

Count and display: raw sources, source summaries, concepts, entities, queries, pending ingests, last 5 log entries.

---

## Page Conventions

**Frontmatter** — every page:
```yaml
---
title: "Page Title"
type: concept | entity | source | query
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw/file1.md, raw/file2.md]
---
```

**Wikilinks** — `[[concept-name]]` hyphenated-lowercase. Link to related pages liberally.

**Summaries** — first paragraph after heading should be a 1-2 sentence summary.

**Citations** — attribute claims: `According to [[sources/paper-name]]...`

**Log format** — parseable: `grep "^## \[" wiki/log.md | tail -5`

## Key Rules

1. The LLM writes the wiki. The user curates sources.
2. Never modify or delete `raw/` — sources are immutable.
3. Every operation updates `wiki/index.md` and appends to `wiki/log.md`.
4. One source should touch 10-15 wiki pages — aggressive cross-referencing.
5. Good query answers compound back into the wiki.
6. Note contradictions explicitly — never silently resolve.
7. Wikilinks are the value — use them everywhere.

## Reference Documentation

- [Operations Guide](references/operations.md) — detailed workflows for each operation

$ARGUMENTS
