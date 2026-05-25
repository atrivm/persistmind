---
name: session-onboarding
description: When a new Claude Code session starts and the user has not yet given a specific task, OR when the user says "che stavamo facendo?", "ricordami dove eravamo", "stato del progetto", "ultimo checkpoint", "brief". Provides a concise briefing of the current project state from memory — recent decisions, open pivots, applicable feedback rules, last checkpoint.
metadata:
  version: 1.0.0
---

# Session Onboarding — Brief di apertura sessione

All'inizio di una sessione, o su richiesta, riepiloghi all'utente lo stato del progetto corrente da memoria, in modo da continuare da dove eravate.

## Procedura

1. **Identifica il progetto corrente.** `pwd` → slug.

2. **Carica i tre strati di memoria:**

   - **Globale (User):** leggi `~/.claude/MEMORY.md` per l'elenco di regole trasversali attive.

   - **Progetto:** leggi `~/.claude/projects/<slug>/memory/MEMORY.md` (se esiste). Se manca, dillo all'utente.

   - **Recent activity:** esegui via Bash su DUE project (globale + corrente):
     ```bash
     # globale
     basic-memory tool recent-activity --page-size 5 --project "${PM_GLOBAL_PROJECT:-persistmind-global}"
     # progetto corrente — derivare lo slug da cwd
     # (es. /home/dev/my-project → "my-project" oppure schema "-home-dev-my-project")
     basic-memory tool recent-activity --page-size 5 --project <slug>
     ```
     Per ottenere lo slug del progetto corrente leggi `~/.basic-memory/config.json` e trova l'entry il cui `path` corrisponde a `~/.claude/projects/<encoded-cwd>/memory`.

3. **Componi il brief in 3 sezioni:**

   ```markdown
   ## Brief di apertura — <progetto>

   ### Stato corrente
   <2-3 righe sintetiche derivate dai file `project_*.md` più recenti>

   ### Decisioni recenti
   <Top 3-5 `decision_*.md` o `pivot_*.md` ordinati per `created` desc>

   ### Regole attive (filtrate per rilevanza al progetto)
   <Top 3-5 `feedback_*.md` globali rilevanti — es. se è Flutter, mostra flutter; se è Python, mostra python-related>

   ### Open issues / TODO (da memoria)
   <Eventuali memorie tipo `project_*` o `decision_*` con stato "open" o "in progress">

   ### Last checkpoint
   <Data dell'ultimo `/checkpoint` (cerca in MEMORY.md di progetto o filesystem mtime)>
   ```

4. **Stampalo all'utente.** Massimo 30-40 righe totali. Brevità prima di completezza.

5. **Chiudi con una domanda aperta:** "Da dove vuoi ripartire?" o "Cosa vuoi fare oggi?".

## Quando NON eseguire

- L'utente ha già un task specifico in mano. In quel caso vai diretto al task.
- Sessioni `/loop` o automatizzate.
- Quando il context window non è ancora "freddo" (l'utente sta riprendendo una sessione lunga).

## Vincoli

- Mai inventare attività non documentate.
- Se non c'è memoria di progetto, dichiaralo: "Nessuna memoria di progetto trovata. Vuoi che inizializzi?".
- Niente filler ("Sono lieto di aiutarti..."). Brief asciutto e operativo.
