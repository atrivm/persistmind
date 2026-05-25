---
name: decision-logger
description: When the user makes an explicit architectural or technical decision during the session — phrases like "decidiamo di...", "andiamo con X", "scegliamo Y", "abbiamo scelto", "useremo", "non usiamo più", "scartiamo X", "andiamo avanti con", "preferiamo Y a X", or when Claude detects a clear choice being made between alternatives. After the decision is taken, this skill proposes to save it as a typed `decision` memory.
metadata:
  version: 1.0.0
---

# Decision Logger — Cattura decisioni architetturali

Quando una decisione viene presa, proponi all'utente di salvarla in memoria con il contesto del perché.

## Trigger pattern

- "decidiamo di..."
- "andiamo con X"
- "scegliamo Y"
- "abbiamo scelto"
- "useremo..."
- "non usiamo più X"
- "scartiamo Y"
- "preferiamo X a Y"
- Una conversazione tipo "valutiamo A vs B" che si conclude con "OK, A".

## Procedura

1. **Riconosci la decisione.** Anche implicita: se valutavate 2-3 opzioni e ora state procedendo con una, c'è una decisione da loggare.

2. **NON interrompere il flusso immediatamente.** Aspetta la fine del momento decisionale (il messaggio successivo, o quando si passa a un altro topic).

3. **Proponi il salvataggio:**
   ```
   Vedo che abbiamo deciso: <X>.
   Vuoi che la salvi come memoria di tipo `decision`? (suggerimento: scope progetto)
   ```

4. **Se l'utente conferma**, raccogli (idealmente da contesto, altrimenti chiedi):
   - **Cosa:** la decisione
   - **Perché:** motivazione (vincoli, dati, esperienza)
   - **Alternative scartate:** quali altre opzioni erano sul tavolo e perché no
   - **Reversibile?:** sì/no e con quale effort

5. **Genera il fragment** via skill `memory-curator` (tipo: decision).

6. **Salva** in `~/.claude/projects/<slug>/memory/decision_<slug>.md`.

7. **Aggiorna l'indice MEMORY.md del progetto.**

## Vincoli

- Mai forzare il salvataggio. Se l'utente dice "no", lascia perdere. Memoria volontaria.
- Mai loggare decisioni non ancora confermate ("forse useremo X" non è una decisione).
- Se l'utente conferma 3 decisioni di fila in 1 messaggio, raggruppa in un'unica proposta multi-select.
- Mai salvare credenziali, password o configurazioni segrete come "decisione".

## Esempio

Conversazione:
> Utente: dobbiamo scegliere tra Postgres e SQLite per la persistenza. Concurrent writes pesanti, ma single-machine.
> Claude: [analisi pro/contro]
> Utente: ok andiamo con Postgres, single-machine ma read replicas dopo.

Trigger! Proponi:
```
Decisione rilevata: usare Postgres (non SQLite) per la persistenza.
Vuoi salvarla come `decision_postgres-over-sqlite`?
```
