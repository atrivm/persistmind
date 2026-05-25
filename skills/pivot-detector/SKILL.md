---
name: pivot-detector
description: When during a session the conversation reveals a change of direction — abandoning a previously chosen approach, switching technologies, restructuring architecture, or reversing a recent decision. Phrases like "cambiamo strada", "non funziona, proviamo Y", "abbandoniamo X", "ripensandoci", "stop, cambiamo approccio", "riavvolgiamo", "torniamo indietro su", or detecting that a previously documented `decision` is being contradicted. Proposes to save a `pivot` memory.
metadata:
  version: 1.0.0
---

# Pivot Detector — Cattura cambi di rotta

Quando il flusso cambia direzione rispetto a una precedente scelta, proponi di salvarlo come pivot in memoria.

## Trigger pattern

- "cambiamo strada"
- "non funziona, proviamo Y"
- "abbandoniamo X"
- "ripensandoci..."
- "stop, cambiamo approccio"
- "torniamo indietro su X"
- "X non andava, andiamo con Y"
- Detection: l'utente sta contraddicendo una precedente decisione (`decision_*.md`) di questo progetto.

## Procedura

1. **Rileva il pivot.**

   Due modi:
   - **Esplicito**: l'utente usa una delle frasi sopra.
   - **Implicito**: confronta la conversazione con `decision_*.md` esistenti del progetto. Se rilevi una contraddizione (es. memoria dice "scegliamo React", conversazione dice "usiamo SvelteKit invece"), trigger.

2. **NON interrompere brutalmente.** Aspetta che l'idea si consolidi (1-2 turni di conversazione successivi).

3. **Proponi il salvataggio:**

   ```
   Rilevato pivot: stiamo abbandonando <X> in favore di <Y>.
   
   Memoria precedente: `decision_<slug-vecchio>` (creata il <data>) — vuoi che la marchi come superseded?
   Vuoi salvare il pivot come `pivot_<slug>`?
   ```

4. **Se conferma**, raccogli:
   - **Data:** oggi
   - **Da:** <stato precedente, eventualmente con riferimento alla memoria superseded>
   - **A:** <nuovo stato>
   - **Trigger:** cosa l'ha causato (errore? scoperta? vincolo emerso?)
   - **Impatto:** cosa cambia da qui

5. **Crea il file** `~/.claude/projects/<slug>/memory/pivot_<slug>.md` con skill `memory-curator`.

6. **Aggiorna la memoria superseded.** Se esiste, aggiungi al frontmatter:
   ```yaml
   metadata:
     ...
     superseded_by: pivot_<slug>
     superseded_at: <data>
   ```
   E aggiungi in cima al corpo un avviso: `> **SUPERSEDED** da [[pivot_<slug>]] il <data>.`

7. **Aggiorna MEMORY.md del progetto.** Aggiungi una sezione `## Pivot` se non c'è.

## Vincoli

- Mai etichettare come pivot un cambio minore (es. rename di una variabile). Pivot = cambio di approccio/tecnologia/architettura.
- Mai sovrascrivere la memoria precedente: deve restare consultabile per audit storico, ma marcata come superseded.
- Se l'utente sta solo brainstorming alternative ma non ha ancora deciso, NON trigger. Aspetta una scelta consolidata.

## Esempio

Memoria esistente: `decision_use-langgraph` — "Useremo LangGraph come orchestrator multi-agent."

Conversazione:
> Utente: il costo di LangGraph è esploso, 60€/run. Proviamo con skills custom Claude Code.
> Claude: [analizza]
> Utente: ok, abbandoniamo LangGraph, riscriviamo come skills.

Trigger! Proponi:
```
Rilevato pivot: abbandono LangGraph in favore di skills Claude Code.
Memoria precedente `decision_use-langgraph` → la marco come superseded.
Salvo come `pivot_langgraph-to-skills`?
```
