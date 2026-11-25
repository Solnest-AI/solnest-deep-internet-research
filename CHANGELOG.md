# Changelog

## 1.0.0

First release as its own GitHub repo.
- Install by pasting the repo link into Claude Code and saying "set this up".
- The skill installs to `~/.claude/skills/deep-internet-research`. Setup finds Python (or installs it) and the skill always uses that one.
- Setup checks what is already connected first. If the Solnest Research Kit connected your search tools, nothing is set up twice.
- Updates install themselves once a day, in the background, from published releases only. If a new release does not start, the old one is put back by itself.
- An update never touches your keys file (`.env`) or any file you added. Changes you ask for are kept in `~/.solnest/deep-internet-research/my-instructions.md`.
