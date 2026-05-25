---
description: Rimuovi una memoria (globale o di progetto) dopo conferma
argument-hint: "<nome-memoria-da-rimuovere>"
---

# /forget — Rimozione memoria

Rimuovi la memoria `$ARGUMENTS`.

## Procedura

1. **Cerca la memoria** in tutti gli strati:
   - `~/.claude/memory/global/` (globale)
   - `~/.claude/projects/*/memory/` (tutti i progetti)

   Match su filename (senza estensione) o sul campo `name:` del frontmatter.

2. **Se più di un match**, presenta lista all'utente con AskUserQuestion: quale rimuovere?

3. **Se nessun match**, lista le memorie disponibili con nomi simili (fuzzy match) e proponi correzione.

4. **Conferma rimozione** mostrando:
   - Path completo
   - 3 righe di anteprima del contenuto
   - "Sei sicuro? La rimozione è definitiva (ma il backup giornaliero `~/.claude/backups/` la conserva)."

5. **Esegui** se confermato:
   - Backup prima: `cp <file> ~/.claude/backups/forgotten_<timestamp>_<slug>.md`
   - Rimuovi il file: `rm <file>`
   - Rimuovi la riga dall'indice MEMORY.md (globale o progetto).
   - Rebuild basic-memory index: `basic-memory reindex 2>&1 | tail -5`

6. **Conferma finale** in una riga: "Rimossa: `<path>` (backup in `<backup-path>`)".

## Vincoli
- MAI rimuovere senza conferma esplicita.
- Sempre fare backup prima della rimozione.
- Se la memoria è linkata da altre (`[[<slug>]]` nel contenuto di altre memorie), avvisa l'utente di possibili dangling reference.
