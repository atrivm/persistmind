---
description: Salva una regola/preferenza nello strato globale User (vale per tutti i progetti)
argument-hint: "<contenuto da ricordare globalmente> [--type feedback|reference|user]"
---

# /remember-global — Cattura memoria globale (User)

Salva la seguente informazione come frammento di memoria GLOBALE — visibile in tutti i progetti.

**Input:** $ARGUMENTS

## Quando usare /remember-global vs /remember
- Globale: regola di interazione universale, preferenza personale, pointer cross-progetto, identità.
- Progetto: fatto/decisione/pivot specifico di un singolo progetto.

In caso di dubbio: PROGETTO. Poi semmai usa `/promote` quando diventa chiaro che vale ovunque.

## Procedura

1. **Determina il tipo.** Se non specificato:
   - `feedback` — regola di interazione che Claude deve seguire
   - `reference` — pointer cross-progetto (URL, path, comando)
   - `user` — fatto sull'utente (chi è, cosa preferisce, cosa sa)

2. **Genera frontmatter.** Slug kebab-case. Frontmatter:
```yaml
---
name: <kebab-slug>
description: <una riga, specifica>
metadata:
  type: <tipo>
  created: <YYYY-MM-DD>
  tags: [<2-4 tag>]
---
```

3. **Genera corpo:**
   - `feedback`: la regola, **Why:**, **How to apply:**.
   - `reference`: cosa è, URL/path, quando consultarlo.
   - `user`: il fatto, contesto, eventuali implicazioni per le risposte.

4. **Scrivi il file** in `~/.claude/memory/global/<type>_<slug>.md` via Write tool.

5. **Aggiorna l'indice** `~/.claude/MEMORY.md` — aggiungi una riga nella sezione appropriata:
   - Identità → `## Identità`
   - Feedback → `## Feedback (regole trasversali — derivate dai progetti)`
   - Reference → `## Reference`

6. **Sync basic-memory.** Esegui via Bash: `basic-memory sync 2>&1 | tail -5` per indicizzare il nuovo file.

7. **Conferma** in una riga: "Memoria GLOBALE salvata: `~/.claude/memory/global/<file>` (tipo: <type>)".

## Vincoli
- Non duplicare. Prima cerca con `basic-memory tool search-notes "<topic>"` se esiste già una memoria simile.
- Le memorie globali sono SEMPRE visibili in contesto: scrivile breve e operativa, no prosa.
- Mai salvare credenziali.
