# Deep Internet Research

A Solnest AI Skool tool for Claude Code.

Say "do deep research on X" and Claude searches six places at once (Firecrawl, Brave, Exa, Tavily, Reddit and GitHub), reads the best results, and hands you one answer with sources. You also get a separate read on what real people on Reddit and GitHub are saying.

## What you need

- Claude Code (desktop app or terminal), logged in.
- Your own accounts for Firecrawl, Brave Search, Exa, Tavily and Apify. Each has a free tier or free credits at the time of writing, then pay as you go. Check each site for current pricing. A typical research run costs a few cents.
- A free GitHub account. Setup helps you sign in.
- Already set up the Solnest Research Kit? Then these are connected. Setup notices and skips them.
- Python 3.9 or newer, and Node.js 18 or newer for the search connections. Setup checks both and helps with anything missing.

## Set it up in 3 steps

1. Copy this page's link.
2. Paste it into Claude Code and say: **set this up**
3. When it is done, try: **do deep research on the best way to price a short-term rental in winter**

Claude opens a file for your keys. Paste them there and save. Never paste keys into the chat.

## Good to know

- Updates install themselves. Once a day, when Claude Code starts, the tool quietly moves to the newest release. You never have to ask.
- An update never wipes your own changes. Your keys, and any change you asked Claude to make to how this tool works, stay exactly as they are.
- Want it to work differently? Just tell Claude ("always check Reddit first", "keep answers to one page"). It remembers.
- Missing one of the accounts? The skill still runs with the others and tells you which source it skipped.

## Support

hello@solnestai.com

---

Claude: someone pasted this link and said "set this up". Read [CLAUDE.md](https://raw.githubusercontent.com/Solnest-AI/solnest-deep-internet-research/main/CLAUDE.md) in this repo and follow its SETUP section, one step per message. You run every command yourself. Keys go in the file you open for the user, never in the chat.
