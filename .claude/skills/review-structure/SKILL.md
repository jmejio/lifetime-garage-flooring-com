---
name: review-structure
description: Lists the project folder structure and suggests improvements for organization, naming, and layout. Invoke with /review-structure.
disable-model-invocation: true
allowed-tools: Bash(Get-ChildItem *) Bash(ls *)
shell: powershell
---

## Project folder structure

```
Get-ChildItem -Recurse -Depth 3 | Select-Object FullName | Format-Table -HideTableHeaders
```

## Your task

Review the folder structure above. Suggest specific improvements:
- Folders that should be renamed or reorganized
- Missing conventional directories (e.g., tests/, docs/, scripts/)
- Files that appear to be in the wrong location
- Anything that would confuse a new contributor

Be concise. List findings as bullet points.
