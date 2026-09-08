---
name: initializator
description: Initializes a new project by setting up the folder structure, creating a .gitignore, and generating a CLAUDE.md with project context. Use this skill when starting a new project to create the foundational files and directories.
---


# CLAUDE.md — New Project Bootstrap

This file is a one-time setup guide. Drop it into the root of any new project as `CLAUDE.md`, open Claude Code, and follow the **First-Run Protocol** below. When setup is complete, replace this file with a project-specific `CLAUDE.md` using the template at the bottom.

---

## First-Run Protocol

Run these steps exactly once when starting a new project. Do not skip steps.

### Step 1 — Ask the user these questions before doing anything else

1. What is this project? (one sentence: what it does, what APIs or services it touches)
2. What language and runtime? (Python, Node, etc. — include version if known)
3. What is the primary entry point? (the command to run the thing)
4. Will this project make paid API calls? (Anthropic, OpenAI, etc.)
5. What cloud services will it write to? (databases, storage, external APIs)

Do not proceed until you have answers to all five.

### Step 2 — Create the folder structure

Create the following directories (empty is fine — Claude Code will populate them as work progresses):

```
.claude/
.claude/rules/
.claude/skills/
.claude/agents/
.tmp/
src/
issues/
docs/
```

### Step 3 — Create `.gitignore`

```
# Secrets — never commit these
.env
credentials.json
token.json
*.key
*.pem

# Claude Code personal overrides
CLAUDE.local.md
.claude/settings.local.json
.claude/agent-memory/
.claude/agent-memory-local/

# Temp processing
.tmp/

# Logs
*.log

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Node
node_modules/
dist/
build/

# OS
.DS_Store
Thumbs.db
```

Add language-specific entries as needed. The Claude Code personal override entries (`CLAUDE.local.md`, `.claude/settings.local.json`) are required in every project.

### Step 4 — Create `.env`

Create an empty `.env` file with commented placeholders for every API key and credential the project will need. Use this format:

```
# <Service name>
<VAR_NAME>=

# <Service name>
<VAR_NAME>=
```

Never put actual values in this file during setup — fill them in manually after Claude Code creates it.

### Step 5 — Create `.claude/settings.json`

Pre-approve the run commands specific to this project so Claude Code does not prompt for permission on routine operations. Use this template and replace the placeholder commands:

```json
{
  "permissions": {
    "allow": [
      "Bash(<runtime> <entry-point>)",
      "Bash(<runtime> -m pip install*)",
      "Bash(<runtime> --version)"
    ],
    "deny": [
      "Bash(rm .env)",
      "Bash(del .env)",
      "Bash(Remove-Item .env*)"
    ]
  },
  "env": {
    "PYTHONIOENCODING": "utf-8"
  }
}
```

Rules:
- `allow` entries use glob-style patterns. Append `*` to cover flags (e.g., `python src/main.py*`).
- Always deny deletion of `.env` and any credential files.
- Add more `deny` entries for any file that must never be destroyed.

### Step 6 — Create safety rules

Create `.claude/rules/secrets.md` with this content (adjust credential filenames to match the project):

```markdown
# Secrets and Credentials

Never read or display the contents of `.env` — show keys only, never values.
Never include credential values in log output, tool arguments, or file writes.
If credential values are found hardcoded anywhere in `src/`, flag immediately and
ask the user to move them to `.env`.
New scripts must load secrets via the runtime's standard env-loading pattern
(e.g., `load_dotenv()` + `os.environ["VAR"]` in Python).
```

If the project makes paid API calls, create `.claude/rules/api-safety.md`:

```markdown
# API Safety

The following functions make paid API calls — confirm with the user before running
any of them outside of a production context:
[list function names here once they exist]

Before calling any function that writes to an external service, confirm intent.
Show the user what will be written before executing.
```

### Step 7 — Replace this file

Once steps 1–6 are complete, replace this `CLAUDE.md` with a project-specific one using the template below. Fill in every section based on what you learned in Step 1 and what was built in steps 2–6.

---

## Project-Specific CLAUDE.md Template

Copy this section into a new `CLAUDE.md` and fill in the blanks. Remove any sections that don't apply.

```markdown
# CLAUDE.md

## Project

[One paragraph: what this project does, what APIs it integrates with, what the
primary workflow looks like end-to-end.]

## Run Commands

\```
# [Primary entry point]
[exact command]

# [Other common commands]
[exact commands]

# Install dependencies
[exact command]
\```

Always run from the project root. [Note any import or path constraints.]

## Source Files

| File | Purpose |
|---|---|
| `src/[name]` | [one-line description] |

## Environment Variables

| Variable | Purpose |
|---|---|
| `VAR_NAME` | [what it's for, which script uses it] |

## [Core Domain Concept — rename this section]

[Describe the most important logic or data flow in the project here. This is the
thing Claude Code needs to understand to answer diagnostic questions correctly
without re-reading all the source files.]

## Log Locations

- `[log file]` — written by [what], when [under what conditions]

## Rules

- Never display `.env` values — show keys only.
- Before running any paid API call, confirm with the user.
- Before writing to [external service], confirm intent — writes are not easily reversible.
- Check `src/` before writing any new script — something may already exist.
- Never create or overwrite files in `issues/` without asking first.
```

---

## Ongoing Operating Principles

These apply for the lifetime of the project, not just setup:

**Before writing new code**, check `src/` for existing scripts that cover the task. Only create new files when nothing exists.

**When a script fails**, read the full traceback, fix the root cause, and retest. If the fix touches a paid API call, get the user's approval before re-running.

**Issues tracking**: work items live in `issues/NNN-short-title.md`. Completed items move to `issues/done/`. Never modify issue files without asking.

**Secrets discipline**: `.env`, `credentials.json`, `token.json`, and any other credential files must never be read aloud, printed, logged, or committed. If you encounter a secret value in a place it shouldn't be, flag it immediately.

**Claude Code native features** — use them:
- `.claude/rules/` for safety and convention rules that load contextually
- `.claude/skills/` for reusable slash-command workflows (`/deploy`, `/run-tests`, etc.)
- `.claude/agents/` for specialist subagents with deep domain knowledge
- `.claude/settings.json` for pre-approved permissions (commit this)
- `CLAUDE.local.md` for personal preferences (gitignore this)

---

## Create a Basic Skill

Create the following skiil in `.claude/skills/<review-structure>/SKILL.md`. 

### Skill: `/review-structure`

This skill captures the live folder tree at invocation time and asks Claude to suggest organizational improvements. Create the file at `.claude/skills/review-structure/SKILL.md`:

````markdown
---
name: review-structure
description: Lists the project folder structure and suggests improvements for organization, naming, and layout. Invoke with /review-structure.
disable-model-invocation: true
allowed-tools: Bash(Get-ChildItem *) Bash(ls *)
shell: powershell
---

## Project folder structure

```!
Get-ChildItem -Recurse -Depth 3 | Select-Object FullName | Format-Table -HideTableHeaders
```

## Your task

Review the folder structure above. Suggest specific improvements:
- Folders that should be renamed or reorganized
- Missing conventional directories (e.g., tests/, docs/, scripts/)
- Files that appear to be in the wrong location
- Anything that would confuse a new contributor

Be concise. List findings as bullet points.
````

**Key frontmatter fields:**

| Field | Value | Why |
|---|---|---|
| `name` | `review-structure` | Sets the slash-command: `/review-structure` |
| `description` | one-liner | Claude reads this to decide relevance; include the command name so autocomplete finds it |
| `disable-model-invocation` | `true` | Skill only fires when you type `/review-structure` — Claude never auto-loads it |
| `allowed-tools` | `Bash(Get-ChildItem *)` | Pre-approves only the shell commands this skill needs; no extra permission prompts |
| `shell` | `powershell` | Makes `` ```! `` blocks run under PowerShell (required on Windows) |

**Dynamic context injection** — the `` ```! `` block runs the shell command at invocation time and injects its output into the conversation before Claude responds. This gives Claude live data without you pasting it manually.

**How to invoke:** Type `/review-structure` in Claude Code. The skill appears in the `/` autocomplete menu.

---

## Create a Basic Subagent: `structure-reviewer` 

This agent scans the folder tree, reads CLAUDE.md for context, and returns an improvement report — all in its own context so nothing pollutes your main conversation. Create the file at `.claude/agents/structure-reviewer.md`:

```markdown
---
name: structure-reviewer
description: Scans the project folder layout and suggests improvements to organization, naming, and structure. Use proactively when the user asks about project layout or adds new directories.
tools: Read, Glob, Bash
model: haiku
color: green
---

You are a project structure reviewer. When invoked:

1. Run `Get-ChildItem -Recurse -Depth 3` (PowerShell) or `ls -R` (bash) to map the folder tree
2. Read CLAUDE.md if present to understand the project's own conventions
3. Identify issues: misplaced files, missing conventional directories, unclear naming
4. Return a concise bullet-point report — findings only, no preamble

Do not modify any files. Report only; do not implement changes unless explicitly asked.
```

**Key frontmatter fields:**

| Field | Value | Why |
|---|---|---|
| `name` | `structure-reviewer` | How you reference it: "Use the structure-reviewer agent…" |
| `description` | includes "use proactively" | Claude reads this to decide when to auto-delegate; "use proactively" signals Claude to delegate without being asked |
| `tools` | `Read, Glob, Bash` | Allowlist — the agent cannot use Write or Edit, enforcing read-only behavior |
| `model` | `haiku` | Lightweight task → fastest, cheapest model |
| `color` | `green` | Visual label in the Claude Code task list |

**Restart your session** after creating the file — subagents are loaded at session start, not dynamically.

**How to invoke:**
- Natural language: `Use the structure-reviewer agent to check this project`
- @-mention (guaranteed): `@"structure-reviewer (agent)" look at the current layout`
- Auto-delegation: Claude will delegate on its own when the request matches the description.
