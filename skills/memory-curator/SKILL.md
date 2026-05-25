---
name: memory-curator
description: When the user wants to write a memory (any of /remember, /remember-global, or just dictates "ricorda che..."), reshape it into the typed-fragment format with frontmatter (name, description, type, tags) and Why/How-to-apply body. Also use when reviewing/editing existing memory files in ~/.claude/memory/ or ~/.claude/projects/*/memory/. Ensures memories follow the Memory Contract defined in ~/.claude/CLAUDE.md.
metadata:
  version: 1.0.0
---

# Memory Curator — Scrittura memorie ben strutturate

Aiuti l'utente a trasformare un'osservazione in linguaggio libero in un frammento di memoria ben formato, conforme al Memory Contract.

## Procedura

1. **Input.** Una frase o paragrafo che l'utente vuole ricordare.

2. **Identifica il tipo** tra: `user`, `feedback`, `project`, `decision`, `pivot`, `reference`.

3. **Genera lo slug.**
   - Kebab-case
   - 2-5 parole significative
   - Niente articoli/preposizioni superflue
   - Univoco rispetto alle memorie esistenti (controlla con `basic-memory tool search-notes "<slug>"`)

4. **Scrivi la `description`.**
   - Una riga, max 100 caratteri
   - Specifica, non generica ("Mai bumpare version senza richiesta" sì; "Regola git" no)
   - In Italiano se l'utente lavora in italiano

5. **Scegli i tag.**
   - 2-4 tag
   - Categorie comuni: `git`, `ci-cd`, `releases`, `security`, `workflow`, `autonomy`, `debugging`, `ui`, `tooling`, `cost`, `flutter`, `react`, `python`
   - Aggiungi `cross-project` se è una regola promovibile a globale

6. **Genera il corpo secondo il tipo.**

   **feedback/project:**
   ```markdown
   <La regola/fatto in 1-2 frasi>

   **Why:** <Motivazione, idealmente con riferimento a un incidente o pattern emerso>

   **How to apply:** <Quando e come applicare la regola operativamente>
   ```

   **decision:**
   ```markdown
   **Cosa:** <Decisione presa>
   **Perché:** <Motivazione, dati, vincoli>
   **Alternative scartate:** <Quali e perché no>
   **Reversibile?:** <Sì/No, con quale effort>
   ```

   **pivot:**
   ```markdown
   **Data:** <YYYY-MM-DD>
   **Da:** <Stato precedente>
   **A:** <Nuovo stato>
   **Trigger:** <Cosa l'ha causato>
   **Impatto:** <Cosa cambia da qui in poi>
   ```

   **reference:**
   ```markdown
   **Cosa è:** <Descrizione breve>
   **Dove:** <URL/path/comando>
   **Quando consultarlo:** <Casi d'uso>
   ```

7. **Compose il file completo:**
   ```yaml
   ---
   name: <slug>
   description: <descrizione>
   metadata:
     type: <tipo>
     created: <YYYY-MM-DD>
     tags: [<tag1>, <tag2>, ...]
   ---

   <corpo>
   ```

8. **Mostra all'utente** il frammento completo PRIMA di salvarlo. Chiedi conferma.

9. **Salva.** Path:
   - `~/.claude/memory/global/<type>_<slug>.md` per globale
   - `~/.claude/projects/<slug-progetto>/memory/<type>_<slug>.md` per progetto

10. **Aggiorna l'indice MEMORY.md** corrispondente.

11. **Sync basic-memory** via `basic-memory sync 2>&1 | tail -5`.

## Vincoli

- Mai inventare incidenti o motivazioni — chiedi all'utente se non specificate.
- Mai salvare credenziali/token/dati sensibili.
- Se il contenuto è ambiguo tra 2 tipi (es. decision vs project), chiedi all'utente.
- Se esiste già una memoria con slug simile, proponi un edit invece di un nuovo file.
