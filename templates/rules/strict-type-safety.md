---
name: strict-type-safety
description: TypeScript strict and Python type hints are mandatory — no any / @ts-ignore / # type: ignore without justification
type: feedback
tags:
  - type-safety
  - typescript
  - python
  - code-quality
---

When writing or modifying TypeScript or Python code, apply strict type safety.

**TypeScript:**
- Never use bare `any`. If absolutely needed, use `unknown` plus narrowing, or a more specific type.
- Never use `@ts-ignore` or `@ts-expect-error` without a justification comment on the line above.
- Prefer expressive generic types (`Array<User>`, `Record<string, X>`) over `object`.

**Python:**
- Type hints on parameters, return values, and class attributes — always.
- Never use `# type: ignore` without an explicit justification comment.
- For complex dict / list shapes use `TypedDict`, `dataclass`, or `pydantic.BaseModel` — not `dict[str, Any]`.

**Why:** The most expensive bugs are type bugs that explode in production. The type system is the first line of tests that runs for free. `any` and `# type: ignore` disable that defense.

**How to apply:**
- If you encounter `any` in existing code, do NOT replace it autonomously (see [[surgical-code-edits]]) — flag it.
- If you MUST write `any` or an ignore for a legitimate reason (e.g. untyped third-party lib), add a justification comment on the line above. Example:

```ts
// upstream lib has no types as of v3.2; replace when types ship
const result = (api as any).legacyMethod();
```

```python
# fastembed returns dynamic shape depending on backend; runtime-validated below
embeddings = model.encode(texts)  # type: ignore[no-any-return]
```
