---
name: implementation-review
description: Validates that code changes follow patterns from docs/AI-AGENT-IMPLEMENTATION.md — event-driven architecture, naming conventions, initialization patterns, modal handler steps, and all 10 pre-commit checklist items.
---
# Implementation Review

## Overview
Run this skill after writing code to confirm it follows every rule in `docs/AI-AGENT-IMPLEMENTATION.md`. It walks through naming conventions, event-driven patterns, initialization gotchas, modal steps, and all 10 validation checks. Fix any violation before declaring done.

## Trigger
User runs `/implementation-review`, or you have finished writing code and need to validate it against the full implementation guide.

---

## Step-by-Step Procedure

### 1. Determine what changed
Identify which categories apply to this change. Run:
```bash
git diff --name-only HEAD
```
Map each changed file to one or more review categories below.

---

### 2. Naming Convention Check

Verify every new file and function follows the module-type naming rules:

| Module Type | File Pattern | Namespace Pattern |
|-------------|-------------|-------------------|
| Store | `{entity}Store.js` | `_.services.{entity}Store` |
| Repo | `{entity}Repo.js` | `_.bids.{entity}` or `_.org.{entity}` |
| Service | `{functionality}.js` | `_.services.{functionality}` |
| UI | `{purpose}.js` | `_.bids.ui` or `_.ui.{component}` |
| Controller | `{feature}Controller.js` | `_.ui.{controller}` |
| Modal | `{feature}Modals.js` | `_.modals.{feature}.{entity}` |

Function naming rules:
- CRUD: `add{Entity}`, `update{Entity}`, `delete{Entity}`, `read{Entity}`
- Inline handlers: `clicked{Action}` — e.g., `clickedBtnAddNewBid`
- Render functions: `render{What}` — e.g., `renderHeader`
- Modal submit handlers: `clickedBtnSubmit{Action}`

Flag any mismatch before proceeding.

---

### 3. Event-Driven Pattern Check

Verify the event-driven pattern is used for all cross-layer communication:

**✅ Required:**
- Repos emit events via `emitAppEvent(APP_EVENTS.X, payload)` — never call UI directly
- UI files (sidebar, mainContent, modals) listen via `onAppEvent(APP_EVENTS.X, handler)`
- Guard event wiring: `if (typeof onAppEvent === 'function' && typeof APP_EVENTS !== 'undefined')`

**❌ Violations to reject:**
- `renderBidList()` or `selectBid()` called from repo code
- UI function called directly from a repo or store
- Modal calling a repo function directly without the callback + event pattern
- Forcing `renderBidList()` / `renderSelectedBid()` from `BID_STATUS_CHANGED` when real-time listeners already handle it

---

### 4. Initialization Pattern Check

If the change touches `auth.js`, `sidebar.js`, or any code that runs at page load:

**Async Auth Flow:**
- Partials must load *inside* `handleSignedInUser` after `await initApp()`
- DOM elements must not be accessed before `initApp()` resolves

**Null-Safety:**
- Use `safeUpdateElement(id, fn)` or `if (!el) return` before any `document.getElementById` result is used
- Firebase listeners fire before partials load — always guard DOM access

**Global Scope:**
- Use `var` (not `const`/`let`) for any symbol that must be `window.foo`
- This is a no-bundler app — `const`/`let` at top level do not attach to `window`

**Sign-Out Lifecycle:**
- `handleSignedOutUser` must: detach listeners → `resetInitState()` → clear `currentUser`/`userOrgId` → reset DOM → restart FirebaseUI (in that order)

---

### 5. Modal Handler Pattern Check

For every new or modified modal handler, verify all 7 required steps are present in order:

| Step | Requirement |
|------|-------------|
| 1 | Read DOM values with `document.getElementById(...).value` |
| 2 | Sanitize with `DOMPurify.sanitize(value)` |
| 3 | Validate after sanitize: `if (!sanitized.trim()) return;` |
| 4 | Call **repo** function (not store or service directly) |
| 5 | Handle error in callback: `(error) => { if (error) { alert(...); return; } }` |
| 6 | Close modal on success: `bootstrap.Modal.getInstance(el)?.hide()` |
| 7 | Emit app event: `emitAppEvent('bid.updated', { bidId })` |

Registration checklist for new handlers:
- [ ] Function added to `public/js/ui/modals/{domain}Modals.js`
- [ ] Registered in `INLINE_HANDLERS` in `public/js/core/handlersMap.js`
- [ ] Exposed in `public/js/entry/index.js` under correct namespace
- [ ] `onclick` added to button in `public/modals.html`
- [ ] Added to `public/js/ui/modals/index.js` registry

---

### 6. Run the 10-Item Pre-Commit Checklist

Work through only the checks that apply to this change:

#### Check 1 — Load Order (if new script files added)
Open `public/index.html`. Confirm phase order:
- Phase 1: `auth.js`, `app.js`
- Phase 1.7: `core/appContext.js`, `core/handlersMap.js`, `core/loadOrder.js`
- Phase 2: `shared/eventBus.js`, `shared/money.js`
- Phase 2.3: `core/appEvents.js`
- Phase 2.5: `constants/index.js`, `services/errorHandler.js`
- Phase 3: all `services/*`
- Phase 4: base UI (sidebar, topbar, minisidebar)
- Phase 5: feature repos
- Phase 5.1: bid rendering UI (header, sections, items, totals)
- Phase 5.3: `baseModalHandler.js`
- Phase 5.5: modal handlers
- Phase 5.7: `ui/urlParams.js`, `ui/bidFilesController.js`
- Phase 6: `ui/mainContent.js`
- Phase 7: utilities
- Phase 7.5: feature registries
- Phase 8: `entry/index.js` **(MUST BE LAST)**

#### Check 2 — Canonical Bid Write (if bid writes added/modified)
```bash
grep -rE "db\.(doc|collection)\(.*organizations/.*/bids" public/js/ --exclude-dir=services
```
All matches must route through `updateBidFields()` or `writeBidDualStore()` in `bidStore.js`.

#### Check 3 — Cents-Based Money Math (if financial calculations changed)
```bash
grep -rE "\* 0\.\d+|\* 1\.\d+|/ 100[^0-9]" public/js/features/ public/js/ui/ public/js/utils/
```
Must return zero matches. All money math uses `toCents()`, `formatCents()`, `calcItemAmts()`, `computeBidTotalsFromSnapshot()`.

#### Check 4 — DOMPurify Sanitization (if user input → Firestore)
```bash
grep -rE "\.value(?!\))" public/js/ui/modals/ | grep -v "DOMPurify"
```
Every `.value` read must have a corresponding `DOMPurify.sanitize()` before the Firestore write.

#### Check 5 — Snapshot Guard (if Firestore reads added)
```bash
grep -rn "snapshot\.data()" public/js/
```
Every `snapshot.data()` call must be preceded by `if (snapshot.exists)` or `snapshot.exists ? ... : null`.

#### Check 6 — Namespace Exposure (if new public functions added)
- Open `public/js/entry/index.js`
- Confirm every new public function is listed under `window._.*`
- Confirm `typeof functionName === 'function' ? functionName : undefined` guard is used

#### Check 7 — Feature Registry (if new module files added)
Run in browser console after page load:
```javascript
window._.validateFeatureRegistries()
```
All 4 registries (bids, bidsUI, org, modals) must show ✅.

#### Check 8 — Inline Handler Mapping (if new HTML event handlers added)
```bash
grep -rohE "on[a-z]+=\"[^\"]+\"" public/*.html | sort -u
```
Compare results against `INLINE_HANDLERS` in `public/js/core/handlersMap.js`. Zero missing handlers.

#### Check 9 — Static Deployment Validation (always run before declaring done)
```bash
node scripts/validateDeployment.js
```
Exit code must be `0`. Use `--strict` if warnings should be blocking.

#### Check 10 — Runtime Namespace Validation (run in browser)
```javascript
window._.appReady()             // Boot readiness
window._.validateNamespaces()   // All critical namespaces ✅
window._validateHandlers()      // 0 missing handlers
```

---

### 7. Report findings

Output a concise table:

```
Check                        Result    Notes
---------------------------  --------  ---------------------------------
Naming conventions           ✅ Pass
Event-driven pattern         ✅ Pass
Initialization patterns      N/A       No auth/DOM changes
Modal handler steps          ⚠️  Fix   Missing step 7 (emitAppEvent)
Load order (Check 1)         N/A       No new scripts
Canonical bid write (Check 2) ✅ Pass
Cents math (Check 3)         N/A       No financial code
DOMPurify (Check 4)          ✅ Pass
Snapshot guard (Check 5)     ❌ Fail   snapshot.data() at bidRepo.js:42 unguarded
Namespace exposure (Check 6) ✅ Pass
Feature registry (Check 7)   N/A       No new modules
Handler mapping (Check 8)    N/A       No new HTML handlers
Static validation (Check 9)  ✅ Pass
```

Fix all ❌ failures and ⚠️ warnings before declaring done.
