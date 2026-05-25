---
description: Salva un fatto/regola/decisione nel progetto corrente come frammento tipizzato
argument-hint: "<contenuto da ricordare> [--type project|decision|pivot|reference|feedback]"
---

# /remember — Cattura memoria di progetto

Salva la seguente informazione come frammento di memoria nel progetto corrente.

**Input:** $ARGUMENTS

## Procedura

1. **Identifica il progetto corrente.** Esegui `pwd` via Bash, prendi il percorso, slugificalo (es. `/Users/alessio/AI Projects/Tonee` → `-Users-alessio-AI-Projects-Tonee`). Il path memoria di progetto è `~/.claude/projects/<slug>/memory/`.

2. **Determina il tipo.** Se l'utente non lo specifica, inferisci tra:
   - `project` — fatto stabile sul progetto (architettura, stack, vincolo)
   - `decision` — scelta consapevole (cosa, perché, alternative scartate)
   - `pivot` — cambio di direzione (data, da X a Y, trigger, impatto)
   - `reference` — pointer esterno (URL, path, comando ricorrente)
   - `feedback` — regola di interazione per Claude

3. **Genera frontmatter.** Slug kebab-case dal contenuto. Frontmatter:
```yaml
---
name: <kebab-slug>
description: <una riga, specifica>
metadata:
  type: <tipo>
  created: <YYYY-MM-DD da `date '+%Y-%m-%d'`>
  tags: [<2-4 tag rilevanti>]
---
```

4. **Genera corpo** secondo il tipo:
   - `feedback`/`project`: la regola/fatto, poi `**Why:**`, poi `**How to apply:**`.
   - `decision`: cosa | perché | alternative scartate | reversibile?
   - `pivot`: data | da X a Y | trigger | impatto.
   - `reference`: cosa è | URL/path | quando consultarlo.

5. **Scrivi il file** in `~/.claude/projects/<slug>/memory/<type>_<slug>.md` via Write tool. Crea la cartella se non esiste.

6. **Aggiorna l'indice** `~/.claude/projects/<slug>/memory/MEMORY.md`: aggiungi una riga nella sezione appropriata con `- [<slug>](<type>_<slug>.md) — <description>`.

7. **Sync semantico** (opzionale, se basic-memory ha un project che mappa questa cartella): notifica l'utente che è stato salvato e che la sincronizzazione avverrà al prossimo `basic-memory sync`.

8. **Conferma all'utente** in una riga: "Memoria salvata: `<path>` (tipo: <type>, slug: <slug>)".

## Vincoli
- NON sovrascrivere file esistenti senza chiedere conferma.
- Se trovi una memoria simile (slug uguale o descrizione vicina), proponi all'utente di fare `edit` invece di una nuova.
- Mai salvare credenziali, token, password (rifiuta esplicitamente).
