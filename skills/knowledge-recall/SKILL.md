---
name: knowledge-recall
description: When the user references past work or asks if something was previously discussed, decided, or built — phrases like "abbiamo già fatto X?", "avevamo deciso Y?", "ricordi quando...", "abbiamo provato...", "esisteva una soluzione per...", "non ricordo se...", "abbiamo visto questo errore prima?". Triggers semantic search across all memory layers (global + all projects) and presents matching results with relevance.
metadata:
  version: 1.0.0
---

# Knowledge Recall — Richiamo memoria cross-session

Quando l'utente si chiede se qualcosa è già stato fatto/visto/deciso, fai una ricerca semantica e gli mostri quello che la memoria sa.

## Trigger pattern (riconosci queste formulazioni)

- "abbiamo già fatto X?"
- "ricordi quando...?"
- "avevamo deciso..."
- "abbiamo provato..."
- "non ricordo se..."
- "esisteva una soluzione..."
- "abbiamo già visto questo errore?"
- "in passato..."
- "qualche sessione fa..."

## Procedura

1. **Estrai la query.** Dalla frase utente, estrai 3-7 parole chiave significative (sostantivi, verbi specifici, identificatori tecnici). Scarta le formule conversazionali ("abbiamo", "ricordi", ecc.).

2. **Ricerca semantica primaria.** Via tool MCP basic-memory:
   ```
   mcp__basic-memory__search_notes(query="<keywords>", limit=10)
   ```
   Se non disponibile, fallback via Bash:
   ```bash
   basic-memory tool search-notes "<keywords>" | head -100
   ```

3. **Ricerca testuale parallela.** Per evitare falsi negativi, anche:
   ```bash
   grep -ril -E "<keyword1>|<keyword2>" ~/.claude/memory/ ~/.claude/projects/*/memory/ 2>/dev/null | head -10
   ```

4. **Dedupe e ranking.** Combina i risultati, deduplicali per file_path. Ordina per score (semantic primary, then fallback recency).

5. **Filtro rilevanza.** Scarta entries con score < 0.4 (sotto questa soglia spesso è rumore).

6. **Componi la risposta:**

   Se ≥1 match rilevanti:
   ```markdown
   **Sì, c'è memoria su questo:**

   1. **<title>** (<scope>, <type>, score <X.XX>)
      <excerpt 2-3 righe>

   2. **<title>** (...)
      <excerpt>

   ...

   Vuoi che apra il file completo di una di queste? O vuoi `/promote` se ne vedi una che dovrebbe valere globale?
   ```

   Se nessun match rilevante:
   ```markdown
   **Nessun match in memoria per questo topic.**

   Possibili motivi:
   - Non l'abbiamo ancora salvato (vuoi /remember o /remember-global?)
   - Lo abbiamo discusso ma non consolidato (era una conversazione effimera)
   - Il pattern di ricerca era troppo specifico — provo con sinonimi: "<altre keyword>"

   <riprova con sinonimi se sensato>
   ```

## Vincoli

- Non inventare match. Se non c'è, dillo chiaramente.
- Massimo 5 risultati nella prima passata. Se utente vuole di più, fa una seconda query mirata.
- Sempre includere lo SCOPE (globale / nome progetto) per ogni hit — chiarisce dove vive la memoria.
- Se trovi una memoria di progetto X mentre l'utente lavora su Y, segnalalo: "Questa memoria viene dal progetto X, potrebbe essere candidata a /promote globale."
