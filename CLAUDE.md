If the user said "set this up", follow SETUP below.

# Deep Internet Research (Solnest AI)

This repo installs the `deep-internet-research` skill. When the user asks for deep research, the skill searches six places at once: Firecrawl, Brave, Exa and Tavily (four MCP servers), Reddit (a bundled Python script that calls Apify) and GitHub (the `gh` command line). Then it writes one answer with sources.

What is in here:
- `skill/deep-internet-research/`: the skill (`SKILL.md`, `scripts/`, `.env.example`). It installs to `~/.claude/skills/deep-internet-research`.
- `install.sh`: the installer. `VERSION` and `CHANGELOG.md`: what release this is.

Below, `SKILL` means `~/.claude/skills/deep-internet-research` and `PY` means `~/.claude/skills/deep-internet-research/bin/py` (the Python that the installer found).

## Your own changes (read first, every time)

Before anything else, read `~/.solnest/deep-internet-research/my-instructions.md` if it exists and
follow it. It holds this user's own changes to how this tool works, and it wins over the
defaults in this file.

When the user asks to change how this tool works for them (wording, tone, topics, steps,
defaults, what to include or leave out), write the change into that file in plain words,
create it if needed, and read it back to them. **Never edit this tool's own files for
that.** This tool updates itself automatically and replaces its own files, so a change
made there is lost on the next update. Their keys file
(`~/.claude/skills/deep-internet-research/.env`) is never touched by an update, and
neither is anything else they added to that folder.

## Rules for you (Claude) during setup

- You run every command yourself with your Bash tool. The user never opens a terminal. On Windows, Claude Code runs Bash commands in Git Bash, where these commands (including `~`) work.
- One step per message. Do not report a step as working until you have seen the output that proves it.
- Keys never go in the chat. They go in the `.env` file you open for the user. If the user pastes a key into the chat anyway, tell them in one line to delete that key on that service's dashboard and make a new one, then carry on with the file.
- Never print, `cat`, echo, Read or summarize the contents of any `.env` file. Only check whether a value is there, with the commands below.
- Never run `claude mcp get` yourself and never open or print `~/.claude.json`. Both can show a key.
- If a search server is already connected, leave it alone. Never add a second copy and never replace one without a plain yes.

## SETUP

### Step 1: Install

Tell the user in one line: "Installing the deep research skill. About a minute, nothing for you to do." Then run one of these:

- You are reading this from the GitHub page (no local copy of this repo):

  ```bash
  bash -o pipefail -c "curl -fsSL https://raw.githubusercontent.com/Solnest-AI/solnest-deep-internet-research/main/install.sh | bash"
  ```

- You already have this repo as a folder on this computer: `bash "<this folder>/install.sh"`

The installer copies the skill to `~/.claude/skills/deep-internet-research`, finds Python 3.9 or newer (or installs one for this user, no admin rights needed), writes a small launcher (`bin/py`) so the skill always uses that Python, makes an empty keys file (`.env`) if there is none, and starts the two scripts once to prove they run. Running it again is safe: it keeps the user's `.env`. If the skill is already there from an older Skool version, this upgrades it in place and keeps the keys.

### Step 2: Read the checklist it printed

- Every line starts with `[ok]`: go on to Step 3.
- `STOP: ... holds a different skill` or `... a link or a git checkout`: something else already lives at `~/.claude/skills/deep-internet-research`. Nothing was changed. Tell the user what you found and ask what they want to do with it. Do not delete it yourself.
- `ERROR: could not download`: usually the network. Run Step 1 once more.
- `ERROR: no working Python`: send the user to https://www.python.org/downloads/ (on Windows they must tick "Add python.exe to PATH"). When they say it is installed, run Step 1 again.
- `[!!] scripts`: run Step 1 once more. If it repeats, send the full output to hello@solnestai.com.

### Step 3: Check what is already connected

Run:

```bash
claude mcp list 2>/dev/null || echo NO_CLAUDE_CLI
gh --version >/dev/null 2>&1 && { gh auth status >/dev/null 2>&1 && echo GH_OK || echo GH_NOT_LOGGED_IN; } || echo GH_MISSING
grep -qE '^APIFY_TOKEN=[^[:space:]]' ~/.claude/skills/deep-internet-research/.env && echo APIFY_FILLED || echo APIFY_EMPTY
```

Read it like this:
- The skill needs four search servers with exactly these names: `firecrawl`, `brave-search`, `exa`, `tavily`. In the `claude mcp list` output, a name that shows as connected is done.
- `NO_CLAUDE_CLI`: look at your own tool list instead. Tools that start with `mcp__firecrawl__`, `mcp__brave-search__`, `mcp__exa__` or `mcp__tavily__` mean that server is connected.
- `APIFY_FILLED` means the Reddit search has its key. `APIFY_EMPTY` means it does not yet.
- `GH_OK` means GitHub search is ready.

Tell the user in plain words what is already connected and what is missing. Then:

- **All four servers connected, `APIFY_FILLED`, `GH_OK`:** skip to Step 7.
- **All four servers connected, only Apify or GitHub missing:** do Step 4 for the Apify line only (if needed), Step 5 for Apify only, skip Step 6, fix GitHub as described below, then Step 7.
- **One or more servers missing:** tell the user there are two ways and ask which they want.
  1. The Research Kit (easiest if they use other Solnest research tools). It connects all of these in one go and tests each one. They paste this link into Claude Code and say "set this up": `https://github.com/Solnest-AI/solnest-research-kit`. If they pick this, do Step 8 now, tell them to come back and say "check deep research" when the kit is done, and stop here.
  2. Connect them right here with their own keys: go on to Step 4.

GitHub, when it is not `GH_OK`:
- `GH_MISSING`: Mac `brew install gh` if `brew --version` works. Windows `winget install --id GitHub.cli`. Otherwise send them to https://cli.github.com.
- `GH_NOT_LOGGED_IN`: tell the user to type `! gh auth login` in the chat box (or run `gh auth login` in a terminal) and follow the browser prompt. It is a sign-in you cannot finish for them. A free GitHub account is enough.
- The skill still runs without GitHub. It says in its answer that GitHub was skipped.

### Step 4: Keys, through a file

Open the keys file for the user:
- Mac: `open -e ~/.claude/skills/deep-internet-research/.env`
- Windows: `notepad.exe "$(cygpath -w "$HOME/.claude/skills/deep-internet-research/.env")" &`
- Linux: `xdg-open ~/.claude/skills/deep-internet-research/.env`

Tell the user: "Paste each key after its = sign, save, close the file, then tell me 'saved'." Each line in the file has the link where that key lives. Only the lines for what is missing need a key. Give these pointers if they ask:
- Firecrawl: sign up, then API Keys in the dashboard.
- Brave Search API: make an account at the API dashboard, pick a plan (there is a free option at the time of writing), then API Keys.
- Exa: dashboard, API Keys.
- Tavily: the key is on the dashboard home page after sign up.
- Apify: Console, Settings, API & Integrations, copy the default API token.

If a link has moved, tell them to look for "API keys" in that site's dashboard. A user can skip a service by leaving its line blank. The skill then runs without that source and says so in its answers.

### Step 5: Test every key (real, read-only calls)

Say first, in one line: "I'm going to test each key with one tiny search. All of it together costs less than a cent of your own free credits. OK?" Wait for a plain yes. That yes also covers the Reddit test in Step 7.

Then run:

```bash
~/.claude/skills/deep-internet-research/bin/py ~/.claude/skills/deep-internet-research/scripts/setup_research.py check
```

It makes one small read-only call per service (Firecrawl and Apify are free calls, Brave uses 1 query, Exa about half a cent, Tavily 1 credit) and prints OK, FAIL or MISSING for each key, plus the `gh` login state. It never prints a key.
- `MISSING` for a server that Step 3 showed as already connected is fine: its key lives with that connection, not in this file.
- `FAIL` with 401, 403 or 422: the key is wrong or not active yet. Do Step 4 again for that one line, then run this again.
- `FAIL` with HTTP 0: no internet, or a firewall. Say so.

### Step 6: Connect the search servers

Only for servers Step 3 showed as missing. Check Node first: `node --version` (needs 18 or newer, three of the four servers start through `npx`). Missing: Mac `brew install node` if Homebrew is there, otherwise https://nodejs.org (LTS installer). Windows: `winget install OpenJS.NodeJS.LTS`. After a Node install the user quits and reopens Claude Code, then says "set this up" again.

Then run:

```bash
~/.claude/skills/deep-internet-research/bin/py ~/.claude/skills/deep-internet-research/scripts/setup_research.py register
```

It adds `firecrawl`, `brave-search`, `exa` and `tavily` for this user with the keys from the `.env`. It skips any service whose key is blank, and it skips a server that already exists (it prints `SKIP`). Only if an existing server is broken and the user says yes, run it again with `--replace` at the end.

If it prints `FAIL     claude CLI not found`: this computer has no `claude` command, so the servers cannot be added from here. Offer the Research Kit from Step 3 instead.

Then run `claude mcp list` and confirm the servers show as connected. One that shows "failed" usually means Node is missing or the key is wrong.

### Step 7: Real test

Reddit, a small pull through the bundled script (Apify charges a fraction of a cent, covered by the yes in Step 5; if you skipped Step 5, ask that same question now). Skip it if `APIFY_EMPTY`:

```bash
~/.claude/skills/deep-internet-research/bin/py ~/.claude/skills/deep-internet-research/scripts/reddit_scrape.py -q "claude code" -n 3
```

GitHub (free). Skip it if GitHub is not `GH_OK`:

```bash
gh search repos "claude code skills" --limit 3 --json fullName,stargazersCount
```

Each one you ran must print results. Show the user the output.

### Step 8: Turn on automatic updates (required, silent)

Run this exactly:

```bash
SKILL="$HOME/.claude/skills/deep-internet-research"; "$SKILL/bin/py" "$SKILL/scripts/solnest_autoupdate.py" register --name deep-internet-research --folder "$SKILL" --update '{python} scripts/update.py' --after '{python} scripts/reddit_scrape.py --help' --undo '{python} scripts/update.py --undo'
```

From now on the skill keeps itself on the latest release with no one asking: once a day, in the background when Claude Code starts, it installs the newest published release and checks that the Reddit script still starts. It never touches the user's `.env` or any file they added, and if a new release fails that check it puts the old version back by itself. Relay the one line it prints. Nothing else to tell them.

### Step 9: Tell the user exactly what worked

Give a short checklist: skill installed (path), each of the four search servers connected or not, Reddit key OK or skipped, GitHub OK or skipped, the Reddit and GitHub tests, automatic updates on. Then tell them:

"Quit Claude Code and open it again so the new search servers load. Then try: do deep research on <a topic you care about>."

Do not say the four search servers work inside chat until the user has restarted. New servers only load in a new session. If you added no servers in Step 6, no restart is needed.

## "Check deep research"

Run Step 3 and tell the user what is connected and what is missing. If something is missing, offer the fix from Step 3. If everything is connected, run Step 7.

## Using the skill after setup

The skill triggers on phrases like "do deep research on X", "deep dive on X", "find everything about X". For a quick Reddit-only pull, the separate `reddit-search` skill is lighter.

## Update

Updates install themselves (Step 8). The `.env` and any file the user added are never touched. Changes the user asked for live in `~/.solnest/deep-internet-research/my-instructions.md`, outside the skill folder, so they survive every update.

Only when the user asks to update now:

```bash
SKILL="$HOME/.claude/skills/deep-internet-research"; "$SKILL/bin/py" "$SKILL/scripts/update.py" && "$SKILL/bin/py" "$SKILL/scripts/reddit_scrape.py" --help >/dev/null && echo "[ok] scripts start"
```

Then run the Step 8 line once more, so a newer auto-updater is picked up. To go back one version: `"$HOME/.claude/skills/deep-internet-research/bin/py" "$HOME/.claude/skills/deep-internet-research/scripts/update.py" --undo`. If `scripts/update.py` is missing (a copy from before automatic updates), run Step 1 instead, then Step 8.

"Is it updating itself?": `~/.claude/skills/deep-internet-research/bin/py ~/.solnest/autoupdate.py status`. Use `pause` in place of `status` to stop all automatic updates, and `resume` to turn them back on.

If `status` shows the last check failed, offer to update now with the line above.

## Repair

Run Step 1 again, then Step 8. It keeps the `.env`.

## Uninstall

```bash
~/.claude/skills/deep-internet-research/bin/py ~/.solnest/autoupdate.py remove --name deep-internet-research
```

Then, after a plain yes from the user:
- Delete the folder `~/.claude/skills/deep-internet-research`. This also deletes the `.env` with the keys.
- Only if this setup added the search servers in Step 6 and no other tool uses them: `claude mcp remove firecrawl --scope user` (repeat for `brave-search`, `exa`, `tavily`). If the Research Kit connected them, leave them.
