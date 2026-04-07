# Wiki Operations — Detailed Reference

## Ingest Workflow

When a new source is added to `raw/`:

1. **Read the source** — full content, note format (article, paper, dataset, image)
2. **Extract key information:**
   - Main claims, findings, or arguments
   - Named entities (people, orgs, tools, products)
   - Concepts and themes
   - Data points, statistics, quotes worth preserving
   - Contradictions with existing wiki content
3. **Discuss with user** (if interactive) — share 3-5 key takeaways, ask what to emphasize
4. **Write source summary** — `wiki/sources/{slug}.md` with frontmatter:
   ```yaml
   ---
   title: "Article Title"
   type: source
   tags: [topic1, topic2]
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   original: raw/filename.md
   ---
   ```
   Body: structured summary (not a copy), key quotes, main arguments, relevance to existing wiki topics.

5. **Create or update concept pages** — for each significant concept:
   - If `wiki/concepts/{concept}.md` exists: add new information, update synthesis, note if source confirms or contradicts existing claims
   - If new concept: create page with definition, context, connections to other concepts
   - Add `[[wikilinks]]` to related concepts and entities

6. **Create or update entity pages** — for each significant entity:
   - If `wiki/entities/{entity}.md` exists: add new data points, update timeline
   - If new entity: create page with description, role, connections
   - Add `[[wikilinks]]` to related entities and concepts

7. **Update cross-references** — ensure all new pages link to relevant existing pages and vice versa. Check for:
   - Concepts mentioned in the source that have existing pages
   - Entities that appear across multiple sources
   - Themes that connect previously unrelated pages

8. **Update `wiki/overview.md`** — if the new source shifts the big picture, update the synthesis. Note new themes, strengthened arguments, or emerging contradictions.

9. **Update `wiki/index.md`** — add entries for all new pages, update summaries for modified pages.

10. **Append to `wiki/log.md`:**
    ```markdown
    ## [YYYY-MM-DD] ingest | Article Title
    - Source: raw/filename.md
    - Pages created: concepts/new-concept.md, entities/new-entity.md
    - Pages updated: concepts/existing.md, overview.md
    - Total pages touched: N
    ```

**Target: one source should touch 10-15 wiki pages.** Don't just summarize — weave the source into the existing knowledge graph.

## Compile Workflow

When building missing articles after ingest:

1. **Read all source summaries** in `wiki/sources/`
2. **Extract all `[[wikilinks]]`** across every source
3. **Identify missing pages** — referenced but no file in `wiki/concepts/` or `wiki/entities/`
4. **For each missing concept or entity:**
   - Read all sources that mention it
   - Write 300-800 word encyclopedic article
   - Cross-reference with `[[wikilinks]]` to all related pages
   - Include `## Sources` section
5. **Rebuild `wiki/index.md`** — categorize all pages:
   ```markdown
   ## Concepts
   - [Concept Name](concepts/slug.md) — one-line summary (N sources, YYYY-MM-DD)
   
   ## Entities
   - [Entity Name](entities/slug.md) — one-line summary (N sources, YYYY-MM-DD)
   ```
6. **Append to log**

## Query Workflow

When the user asks a question:

1. **Read `wiki/index.md`** — scan for relevant pages by topic, tags, summaries
2. **Read relevant pages** — follow `[[wikilinks]]` to gather connected information
3. **Synthesize answer:**
   - Cite wiki pages: `According to [[concepts/x]]...`
   - Note confidence level — well-supported (multiple sources) vs. single-source claims
   - Flag contradictions if sources disagree
   - Identify gaps — what the wiki doesn't cover that would help answer fully
4. **Decide whether to file the answer:**
   - Does it synthesize across multiple pages in a new way? → File in `wiki/queries/`
   - Is it a simple lookup? → Don't file
   - Did it reveal a new connection? → File and add cross-references
5. **If filing:** write `wiki/queries/{slug}.md` with frontmatter, update `wiki/index.md`
6. **Append to `wiki/log.md`:**
   ```markdown
   ## [YYYY-MM-DD] query | How does X relate to Y?
   - Pages consulted: concepts/x.md, concepts/y.md, entities/z.md
   - Answer filed: queries/x-relates-to-y.md (or: not filed — simple lookup)
   ```

## Lint Workflow

Periodic health check:

1. **Read all pages** — build a map of the wiki's state
2. **Check for issues:**

   | Check | What to look for |
   |-------|------------------|
   | Contradictions | Two pages making conflicting claims about the same thing |
   | Stale claims | Older pages superseded by newer sources |
   | Orphan pages | Pages with no inbound `[[wikilinks]]` |
   | Missing concepts | Terms mentioned frequently but lacking their own page |
   | Broken links | `[[wikilinks]]` pointing to non-existent pages |
   | Data gaps | Topics partially covered — need more sources |
   | Thin pages | Pages with very little content that could be expanded |

3. **Fix what you can** — update stale claims, add missing cross-references, create pages for frequently-mentioned concepts
4. **Report what needs user input** — suggest sources to find, questions to investigate, contradictions that need human judgment
5. **Write to `wiki/health-report.md`**
6. **Append to `wiki/log.md`:**
   ```markdown
   ## [YYYY-MM-DD] lint | Health check
   - Issues found: N orphans, N contradictions, N missing concepts
   - Fixed: added cross-references, created N stubs
   - Needs attention: contradiction between sources/a.md and sources/b.md on topic Z
   - Suggested sources: [list]
   ```

## Link Normalization

All of these should resolve to `concepts/gpt-series.md`:

| Input | Normalized |
|-------|-----------|
| `[[gpt-series]]` | `gpt-series` |
| `[[GPT_series]]` | `gpt-series` |
| `[[GPT Series]]` | `gpt-series` |
| `[[concepts/gpt-series]]` | `gpt-series` |
| `[[gpt-series\|GPT Family]]` | `gpt-series` |
| `[[gpt-series#scaling]]` | `gpt-series` |

Rules: strip path prefix → replace `_` and ` ` with `-` → lowercase → strip `|text` and `#section`

## Index Conventions

```markdown
# Wiki Index

## Overview
- [Overview](overview.md) — High-level synthesis (updated YYYY-MM-DD)

## Concepts
- [Attention Mechanisms](concepts/attention.md) — Self-attention, cross-attention, variants (3 sources, YYYY-MM-DD)

## Entities
- [GPT-4](entities/gpt-4.md) — OpenAI's multimodal model (2 sources, YYYY-MM-DD)

## Sources
- [Attention Is All You Need](sources/attention-is-all-you-need.md) — Original transformer paper (YYYY-MM-DD)

## Queries
- [How does attention scale?](queries/attention-scaling.md) — Attention variant comparison (YYYY-MM-DD)
```

## Log Conventions

```markdown
# Wiki Log

## [YYYY-MM-DD] ingest | New Paper
- Source: raw/new-paper.md
- Pages created: concepts/new-idea.md
- Pages updated: overview.md, concepts/related.md
- Total pages touched: 8

## [YYYY-MM-DD] query | How does X compare to Y?
- Pages consulted: concepts/x.md, concepts/y.md
- Answer filed: queries/x-vs-y.md

## [YYYY-MM-DD] lint | Weekly check
- Issues found: 2 orphans, 1 broken link
- Fixed: all resolved
```

Parseable: `grep "^## \[" wiki/log.md | tail -5` shows last 5 operations.
