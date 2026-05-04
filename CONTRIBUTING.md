# Contributing

Thanks for helping improve this project. This document describes the usual GitHub workflow so changes stay reviewable and safe to merge.

## Workflow

1. **Fork** the repository on GitHub (if you do not have write access to the upstream repo).
2. **Clone** your fork and add `upstream` if you plan to sync often:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/ORIGINAL_REPO.git
   ```
3. **Create a branch** off the default branch (`main`) *before* you commit (or as soon as you know what you are building). Use a short, descriptive name, for example:
   - `feat/reset-all-progress`
   - `fix/save-path-on-linux`
   - `docs/readme-steam-deck`
   If you already edited files on `main` but have not committed yet, run `git checkout -b your-branch-name` — your uncommitted work stays in the working tree on the new branch.
4. **Make focused changes** — one logical change per PR when possible.
5. **Commit** with clear messages. [Conventional Commits](https://www.conventionalcommits.org/) are welcome, e.g. `feat:`, `fix:`, `docs:`.
6. **Push** your branch to your fork and open a **Pull Request** against `main`.
7. In the PR description, briefly explain **what** changed and **why**, and how you **tested** it (e.g. closed game, ran script, verified in-game).

## Before you open a PR

- Close the game before editing saves; the README already warns about this.
- Install deps once: `python3 -m pip install -r requirements.txt`
- If you change `spell_brigade_unlocker.py`, sanity-check syntax:
  ```bash
  python3 -m py_compile spell_brigade_unlocker.py
  ```
- Do **not** commit real save files, personal paths, or anything under `save_backup_*/` (those folders are gitignored).

## Questions

Open an issue on GitHub if something in the save format or script behavior is unclear before spending time on a large change.
