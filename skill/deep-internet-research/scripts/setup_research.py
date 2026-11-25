#!/usr/bin/env python3
"""
Setup helper for the deep-internet-research kit. Works on Mac, Linux and Windows.
Standard library only. Never prints a key.

  python3 setup_research.py check      # test each key in the .env with one tiny read-only API call
  python3 setup_research.py register   # register the 4 MCP servers with `claude mcp add --scope user`
  python3 setup_research.py register --replace   # same, but replace servers that already exist

The .env it reads is the one in the INSTALLED skill folder:
  Mac/Linux:  ~/.claude/skills/deep-internet-research/.env
  Windows:    %USERPROFILE%\\.claude\\skills\\deep-internet-research\\.env
Pass --env <path> to point somewhere else.

Keys it understands:
  FIRECRAWL_API_KEY  BRAVE_API_KEY  EXA_API_KEY  TAVILY_API_KEY  APIFY_TOKEN
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_ENV = Path.home() / ".claude" / "skills" / "deep-internet-research" / ".env"
IS_WINDOWS = os.name == "nt"
KEYS = ["FIRECRAWL_API_KEY", "BRAVE_API_KEY", "EXA_API_KEY", "TAVILY_API_KEY", "APIFY_TOKEN"]


def read_env(path: Path) -> dict:
    vals = {}
    if not path.exists():
        return vals
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        if v:
            vals[k.strip()] = v
    return vals


def http(method: str, url: str, headers: dict, body: dict | None = None) -> tuple[int, str]:
    data = json.dumps(body).encode() if body is not None else None
    if data is not None:
        headers = {**headers, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:200].decode(errors="ignore")
    except urllib.error.URLError as e:
        return 0, str(e.reason)


# One cheap, read-only call per service. Costs: Firecrawl and Apify free,
# Brave 1 query from the free quota, Exa about half a cent, Tavily 1 credit.
TESTS = {
    "FIRECRAWL_API_KEY": lambda k: http("GET", "https://api.firecrawl.dev/v1/team/credit-usage",
                                        {"Authorization": f"Bearer {k}"}),
    "BRAVE_API_KEY": lambda k: http("GET", "https://api.search.brave.com/res/v1/web/search?q=claude%20code&count=1",
                                    {"X-Subscription-Token": k, "Accept": "application/json"}),
    "EXA_API_KEY": lambda k: http("POST", "https://api.exa.ai/search", {"x-api-key": k},
                                  {"query": "claude code skills", "numResults": 1}),
    "TAVILY_API_KEY": lambda k: http("POST", "https://api.tavily.com/search", {"Authorization": f"Bearer {k}"},
                                     {"query": "claude code skills", "max_results": 1}),
    "APIFY_TOKEN": lambda k: http("GET", "https://api.apify.com/v2/users/me", {"Authorization": f"Bearer {k}"}),
}


def cmd_check(env: dict) -> int:
    failed = 0
    for key in KEYS:
        if key not in env:
            print(f"MISSING  {key}: not in the .env (that source will be skipped)")
            failed += 1
            continue
        status, detail = TESTS[key](env[key])
        if 200 <= status < 300:
            print(f"OK       {key}: test call returned HTTP {status}")
        else:
            print(f"FAIL     {key}: HTTP {status} {detail}".rstrip())
            failed += 1
    gh = shutil.which("gh")
    if not gh:
        print("MISSING  gh: GitHub CLI not installed (GitHub source will be skipped)")
        failed += 1
    else:
        r = subprocess.run([gh, "auth", "status"], capture_output=True, text=True)
        print("OK       gh: logged in" if r.returncode == 0 else "FAIL     gh: not logged in (run: gh auth login)")
        failed += r.returncode != 0
    return 1 if failed else 0


def npx_cmd(*args: str) -> list:
    # Claude Code on native Windows needs the cmd /c wrapper to launch npx-based MCP servers.
    return (["cmd", "/c", "npx", *args] if IS_WINDOWS else ["npx", *args])


def server_specs(env: dict) -> list:
    specs = []
    if "FIRECRAWL_API_KEY" in env:
        specs.append(("firecrawl", ["--transport", "http"], ["https://mcp.firecrawl.dev/v2/mcp",
                      "--header", f"Authorization: Bearer {env['FIRECRAWL_API_KEY']}"], None))
    if "BRAVE_API_KEY" in env:
        specs.append(("brave-search", [], None, (f"BRAVE_API_KEY={env['BRAVE_API_KEY']}",
                      npx_cmd("-y", "@modelcontextprotocol/server-brave-search"))))
    if "EXA_API_KEY" in env:
        specs.append(("exa", [], None, (f"EXA_API_KEY={env['EXA_API_KEY']}", npx_cmd("-y", "exa-mcp-server"))))
    if "TAVILY_API_KEY" in env:
        specs.append(("tavily", [], None, (f"TAVILY_API_KEY={env['TAVILY_API_KEY']}", npx_cmd("-y", "tavily-mcp"))))
    return specs


def cmd_register(env: dict, replace: bool) -> int:
    claude = shutil.which("claude")
    if not claude:
        print("FAIL     claude CLI not found on PATH. Install Claude Code first.")
        return 1
    rc_total = 0
    for name, pre, http_args, stdio in server_specs(env):
        exists = subprocess.run([claude, "mcp", "get", name], capture_output=True, text=True).returncode == 0
        if exists and not replace:
            print(f"SKIP     {name}: already registered (left as is; rerun with --replace to overwrite)")
            continue
        if exists:
            subprocess.run([claude, "mcp", "remove", name, "--scope", "user"], capture_output=True, text=True)
        if http_args:
            argv = [claude, "mcp", "add", *pre, "--scope", "user", name, *http_args]
        else:
            envpair, command = stdio
            argv = [claude, "mcp", "add", "--scope", "user", name, "-e", envpair, "--", *command]
        r = subprocess.run(argv, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"OK       {name}: registered (user scope)")
        else:
            # stderr from the CLI does not echo header/env values, but trim it anyway.
            msg = (r.stderr or r.stdout).strip().splitlines()
            print(f"FAIL     {name}: {msg[-1][:200] if msg else 'unknown error'}")
            rc_total = 1
    return rc_total


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["check", "register"])
    ap.add_argument("--env", type=Path, default=DEFAULT_ENV)
    ap.add_argument("--replace", action="store_true")
    a = ap.parse_args()
    if not a.env.exists():
        sys.exit(f"No .env at {a.env}. Create it from .env.example first.")
    env = read_env(a.env)
    sys.exit(cmd_check(env) if a.action == "check" else cmd_register(env, a.replace))


if __name__ == "__main__":
    main()
