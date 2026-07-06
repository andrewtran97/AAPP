# Operating Rules

## Ownership

This repository belongs to Andrew Tran.

## AI worker policy

Claude Code may build locally only.
Claude Code must not commit.
Claude Code must not create pull requests.
Claude Code must not push.
Claude Code must not add attribution.

Codex may review and test locally only.
Codex must not push.
Codex must not create pull requests.
Codex must not modify files unless explicitly instructed.

## Human control

Human reviews all diffs.
Human creates signed commits.
Human pushes feature branches.
Human opens pull requests.
Human merges only after required checks pass.

## Main branch

Never push directly to main.
All changes must go through pull requests.
Signed commits are required.
GitHub Actions required check must pass.

## Local setup after clone

Run:

git config core.hooksPath .githooks

## Kill condition

Stop if Claude/Anthropic attribution appears in commit message, PR text, history, or CI output.
Stop if GitHub ruleset allows direct push to main.
