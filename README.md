# rolodexter/ai

A living magazine-style AI portal updated intraday with a hub-and-spoke architecture.

## Structure

- **Hubs**: Learn, Build, Govern, Apply, Research, Tools
- **Atoms**: Books, Papers, Posts, Prompts, Datasets, Snippets, Notes

## Workflow

drop → build → publish

## Licensing & Citation (TL;DR)

- Code & scripts: **MIT** → see `LICENSE.code`
- Docs & knowledge: **CC-BY 4.0** (attribution required) → see `LICENSE.docs`
- Cite this portal:  
  `Joe Maristela et al. *rolodexter/ai Portal*. GitHub repository, 2025. https://github.com/rolodexter/ai`
- **Map-only**: This repo hosts indexes, abstracts, TOC-lite. Full manuscripts live in their own repos.

## Dev Setup
```bash
pip install -r requirements.txt
python tools/scripts/lint-frontmatter.py
python tools/scripts/build-portal.py
```

Optional Git hook (Windows/PowerShell):

```powershell
tools\scripts\hooks\install-hooks.ps1
```

CI runs linter + portal generator on every PR/push.
