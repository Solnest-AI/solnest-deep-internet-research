---
name: deep-internet-research
description: Multi-source deep research. Trigger whenever the user says "do deep internet research", "deep research", "deep dive on X", "research X thoroughly", "find everything about/on X", "what's out there on X", or otherwise asks for a thorough, well-sourced answer rather than a quick lookup. Fans out across SIX sources in parallel, FireCrawl, Brave, Exa, Tavily, the Apify Reddit scraper, and all of GitHub (repos, code, READMEs, issues, PRs, Discussions), then synthesizes one cited answer. Always include Reddit and GitHub. Use for any "deep research" request; for a quick single-source Reddit pull use reddit-search instead.
---

# Deep Internet Research

When the user asks for deep research, you do NOT rely on one search tool. You hit **all six sources**, read the best hits, and synthesize a single cited answer. Reddit and GitHub are always included.

## Your own changes (read first, every time)

Before anything else, read `~/.solnest/deep-internet-research/my-instructions.md` if it exists and
follow it. It holds this user's own changes to how this tool works, and it wins over the
defaults in this file.

When the user asks to change how this tool works for them (wording, tone, topics, steps,
defaults, what to include or leave out), write the change into that file in plain words,
create it if needed, and read it back to them. **Never edit this tool's own files for
that.** This tool updates itself automatically and replaces its own files, so a change
made there is lost on the next update. Their keys file (`.env` in this folder) is never
touched by an update, and neither is anything else they added to this folder.

## Step 1, Frame the question
Restate what the user wants in one line. If it's badly underspecified (e.g. "research cars" with no budget/use), ask 1-2 quick clarifying questions first. Otherwise go.

## Step 2, Fan out across all six sources IN PARALLEL
Issue these in a **single message with multiple tool calls** so they run concurrently. Vary the phrasing per source (each engine rewards different queries).

1. **FireCrawl**, `mcp__firecrawl__firecrawl_search` (query, limit ~6, sources web). Richest: returns page content.
2. **Brave**, `mcp__brave-search__brave_web_search` (query, count ~8). Broad web + fresh.
3. **Exa**, `mcp__exa__web_search_exa` (describe the ideal page, numResults ~6). Best for semantic/neural matches, papers, niche blogs.
4. **Tavily**, `mcp__tavily__tavily_search` (query, max_results ~8). Good aggregated answers + recency.
5. **Reddit (Apify)**, Bash, using the script bundled in this skill's `scripts/` folder:
   `~/.claude/skills/deep-internet-research/bin/py ~/.claude/skills/deep-internet-research/scripts/reddit_scrape.py -q "<topic>" -n 25`
   (`bin/py` is the Python that setup found. On Windows, Claude Code's Git Bash shell understands `~`. If `bin/py` is missing, use `python3`, or `py` on Windows.)
   It reads `APIFY_TOKEN` from the `.env` in this skill's folder. This is the real "what do actual users think" signal.
6. **GitHub, everything**, Bash, run these together (it's the "what builders + people are saying" signal):
   ```bash
   gh search repos  "<topic>" --limit 15 --sort stars \
     --json fullName,stargazersCount,description,updatedAt
   gh search code   "<topic>" --limit 15 --json repository,path
   gh search issues "<topic>" --limit 20 --json repository,title,state,url   # issues + comments = people talking
   gh search prs    "<topic>" --limit 10 --json repository,title,url
   gh api graphql -f query='{ search(query:"<topic>", type:DISCUSSION, first:15){ nodes{ ... on Discussion{ title url repository{nameWithOwner} } } } }'
   ```
   (READMEs surface through repo descriptions + code hits; `gh api repos/<owner>/<repo>/readme` to read one in full when it matters.)

## Step 3, Deep-read the best hits
From everything that came back, pick the 5-10 most relevant/authoritative and read them in full:
- web pages → `mcp__firecrawl__firecrawl_scrape` (markdown) or `WebFetch`
- a key repo's README → `gh api repos/<owner>/<repo>/readme --jq .content | base64 -d`
- a hot issue/discussion thread → `gh api` the comments
Prefer primary sources over listicles. (Note: Reddit pages can't be fetched directly, the Apify pull in Step 2 already has the content.)

## Step 4, Verify before trusting
For any load-bearing or surprising claim, confirm it appears in **2+ independent sources**. If sources disagree, say so explicitly rather than papering over it. Flag anything you couldn't corroborate as `(unverified)`.

## Step 5, Synthesize one cited answer
Structure:
- **Bottom line**, the direct answer in 2-4 sentences.
- **Key findings**, bullets, each with an inline source link.
- **What the community thinks**, distinct Reddit + GitHub signal (sentiment, complaints, what builders actually use). Call these out separately; they're the reason we scrape them.
- **Disagreements / caveats / confidence**, where sources clash or evidence is thin.
- **Sources**, the URLs you actually used.

## Scaling
- Default: run the fan-out directly as above (fastest, keeps you in the loop).
- For a big/broad topic, you may spawn one subagent per source cluster (web vs Reddit vs GitHub) to parallelize the heavy reading and keep the main context clean, but only when the topic is genuinely large. Don't over-engineer small asks.

## If a source is missing
If one MCP is not connected or a key is missing, run the other sources anyway, say plainly which source was skipped and why in the final answer, and do not pretend its coverage exists. GitHub needs the `gh` CLI logged in (`gh auth status`).

## Don't
- Don't skip Reddit or GitHub, they're the whole point of this skill.
- Don't answer from a single engine's results.
- Don't bury disagreement; surface it.
