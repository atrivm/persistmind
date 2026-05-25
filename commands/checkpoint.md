---
description: Analizza la sessione corrente e propone cosa salvare in memoria prima di /clear
argument-hint: "(opzionale) area di focus, es. 'decisioni architetturali'"
---

# /checkpoint — Consolidamento fine sessione

Analizza l'intera conversazione corrente e proponi una lista di memorie da salvare PRIMA che venga lanciato `/clear`.

**Focus area opzionale:** $ARGUMENTS

## Procedura

1. **Scan della conversazione.** Rileggi mentalmente tutta la sessione corrente e estrai:
   - **Decisioni prese** (esplicite o implicite) — con motivazione e alternative scartate.
   - **Fatti scoperti** sul progetto (architettura, vincoli, stack, dipendenze).
   - **Pivot/cambi di rotta** (eravamo su A, siamo passati a B perché C).
   - **Regole emerse** che potrebbero valere come feedback (es. utente ha corretto un comportamento).
   - **Pointer esterni** menzionati (URL, percorsi, comandi non documentati).
   - **Errori/incidenti** e le loro cause emerse.

2. **Categorizza per scope.**
   Per ogni elemento, valuta: è specifico di questo progetto, o è universale?
   - Universale → globale
   - Specifico → progetto
   - In dubbio → progetto (potrai sempre promuoverlo dopo con `/promote`)

3. **Categorizza per tipo.** project | decision | pivot | feedback | reference.

4. **Presenta la lista all'utente** in formato tabella o bullet, con:
   - Slug proposto
   - Tipo
   - Scope (progetto/globale)
   - 1 riga di sintesi
   - 1 riga di why

5. **Chiedi conferma con AskUserQuestion** (multiSelect) — l'utente seleziona quali salvare. Aggiungi opzione "tutti" e "nessuno".

6. **Per ogni voce confermata**, applica la procedura di `/remember` o `/remember-global` come appropriato. NON usare i comandi come slash, usa direttamente Write su filesystem + aggiornamento indice + `basic-memory sync`.

7. **Report finale.** Lista in una riga ciascuno dei file scritti.

## Vincoli
- Se la conversazione è lunghissima (>50 turni), proponi al massimo 10 memorie. Privilegia decisioni e regole sopra fatti minori.
- Niente cattura silenziosa: ogni salvataggio passa per la conferma dell'utente.
- Niente cattura di credenziali, token, dati personali sensibili.
- Se la sessione era puramente esplorativa (no decisioni, no fatti), dillo: "Non ho trovato elementi rilevanti da salvare."
