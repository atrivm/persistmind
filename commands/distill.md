---
description: Distilla la conversazione corrente in un elenco di fatti consolidati (senza salvare)
argument-hint: "(opzionale) area di focus"
---

# /distill — Distillazione conversazione

Estrai dalla conversazione corrente solo i fatti consolidati, in forma sintetica e operativa. NON salvare nulla — produci solo un report leggibile.

**Focus opzionale:** $ARGUMENTS

## Procedura

1. **Scan della sessione.** Rileggi mentalmente la conversazione.

2. **Estrai e categorizza:**
   - **Decisioni** (cosa, perché, alternative)
   - **Fatti** consolidati sul progetto (cose ora vere)
   - **Pivot** (cambi di rotta)
   - **Regole** emerse (cose che Claude dovrebbe ricordarsi di fare/non fare)
   - **Reference** menzionati (URL, comandi, path)

3. **Filtra il rumore.** Escludi:
   - Tentativi falliti che non hanno prodotto apprendimenti utili.
   - Frasi conversazionali generiche.
   - Domande chiarificatrici esaurite.

4. **Presenta in formato strutturato:**

```markdown
# Distillazione sessione — <data>

## Decisioni
- ...

## Fatti consolidati
- ...

## Pivot
- ...

## Regole emerse
- ...

## Reference
- ...
```

5. **Non salvare nulla.** Solo output.

6. **Suggerisci a fine output**: "Per salvare queste voci, usa `/checkpoint`. Per salvare singole voci, usa `/remember` o `/remember-global`."

## Quando usare
- Per fare il punto a metà sessione.
- Prima di un meeting per portare un summary.
- Quando vuoi vedere "cosa abbiamo concluso?" senza ancora committarti al salvataggio.
