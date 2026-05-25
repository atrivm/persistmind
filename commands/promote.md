---
description: Promuovi una memoria da progetto a globale (User)
argument-hint: "<nome-memoria-da-promuovere>"
---

# /promote — Promozione memoria a globale

Promuovi la memoria `$ARGUMENTS` dal progetto corrente allo strato globale User.

## Procedura

1. **Identifica il progetto corrente.** `pwd` → slug.

2. **Trova la memoria.** Cerca un file in `~/.claude/projects/<slug>/memory/` che matcha il nome dato:
   - Match esatto sul filename (senza estensione)
   - Match sul campo `name:` del frontmatter
   - Match sullo slug nel filename

   Se nessuno: messaggio "Memoria '$ARGUMENTS' non trovata nel progetto corrente. Memorie disponibili: <lista>".

3. **Read del file.** Carica il contenuto e parse del frontmatter.

4. **Conferma con l'utente** mostrando:
   - Origine: `<path-progetto>`
   - Destinazione: `~/.claude/memory/global/<tipo>_<slug>.md`
   - Anteprima del contenuto (3-5 righe).

   Usa AskUserQuestion: "Promuovere a globale?" — opzioni: Sì sposta / Sì copia (lascia anche nel progetto) / No annulla.

5. **Esegui la promozione:**
   - **Sposta**: copia il file in `~/.claude/memory/global/<tipo>_<slug>.md`, rimuovi l'originale, aggiorna MEMORY.md di entrambi gli strati.
   - **Copia**: copia il file in globale, lascia l'originale, aggiorna entrambi gli indici.

6. **Aggiorna frontmatter del file globale** se serve: `tags` può guadagnare `[global, promoted-from-<slug>]`.

7. **Sync** via `basic-memory sync 2>&1 | tail -5`.

8. **Conferma** in una riga.

## Quando usare
- Una regola che applicavi al progetto X si rivela utile anche per Y e Z → promuovila.
- Un pattern di lavoro emerso → diventa preferenza globale.
- Un pointer a una risorsa esterna che vale per più progetti.

## Quando NON usare
- Decisioni di architettura specifiche di un progetto (es. "abbiamo scelto Postgres") — restano locali.
- Fatti sul codice di un progetto.
- Pivot storici di un progetto.
