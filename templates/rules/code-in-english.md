---
name: code-in-english
description: Everything inside the code (identifiers, comments, internal strings, filenames, commit messages) stays in English
type: feedback
tags:
  - code-style
  - language
  - naming
---

When you write, modify, or propose code, **everything that lives inside the code** must be in **English**:

- Variable, function, class, constant, parameter, and type alias names
- Comments (`//`, `#`, `/* */`, docstrings, JSDoc)
- Internal log and error strings (not visible to the end user)
- File and folder names
- Commit messages (Conventional Commits: `feat:`, `fix:`, `docs:`, etc.)
- Branch names, tags, PR titles

**Why:**
- Most stacks (TypeScript, Python, Go, Rust, Java, Swift, Flutter, React, etc.) use English as the de-facto industry standard.
- Codebases often go public (open source) or are shared with international teams — non-English identifiers break readability.
- Tooling (linters, search, autocomplete, AI assistants) is optimized for English.
- Keeping branch / commit / code consistent avoids stylistic refactors later.

**How to apply:**
- Avoid identifiers like `utente`, `prezzo`, `calcolaTotale` → use `user`, `price`, `calculateTotal`.
- Avoid comments like `// controlla se l'utente è loggato` → use `// check whether the user is authenticated`.
- Exception: **user-facing strings** (UI copy, end-user error messages) stay in the app's locale. Those belong in localization files (`i18n`, `intl`), not inline in code.
- If you encounter existing code with non-English identifiers, do NOT refactor on your own — flag it and ask.

| Item | Language |
|---|---|
| Code (identifiers, comments, files) | English |
| Commit messages, branch names | English |
| User-facing UI strings | App locale (kept in i18n files) |
| Internal docs (READMEs, design notes) | English when public; localized when internal |
