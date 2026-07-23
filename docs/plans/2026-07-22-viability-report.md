# viability-report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `viability-report` skill — ingests all pipeline outputs (manifest docs, latest veredicto, finmodel summary) and renders a single self-contained HTML report with a predefined light design system, collapsible density, and a mandatory anti-omission completeness checklist.

**Architecture:** SKILL.md orchestrator + `references/report-template.html` (complete design system with `{{SLOT}}` placeholders — the skill populates slots, never redesigns per run). Zero external dependencies: inline CSS, native `<details>`, ~10 lines vanilla JS, print CSS that expands everything.

**Tech Stack:** Markdown (skill) + one HTML template. Verification: structural + no-external-URL check + slot inventory + design-doc consistency (`C:\Obsidian\output\2026-07-22-viability-report-design.md`).

**Note:** Repo is git (main). Commit per task.

---

### Task 1: `references/report-template.html`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-report\references\report-template.html`

- [ ] **Step 1: Write the file with this exact content**

````html
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Viabilidad — {{PROYECTO}}</title>
<style>
  :root{
    --verde:#15803d; --ambar:#b45309; --rojo:#b91c1c;
    --verde-bg:#f0fdf4; --ambar-bg:#fffbeb; --rojo-bg:#fef2f2;
    --text:#1f2937; --muted:#6b7280; --bg:#f9fafb; --card:#ffffff;
    --border:#e5e7eb; --radius:10px;
  }
  *{box-sizing:border-box}
  body{margin:0;padding:2rem 1rem;background:var(--bg);color:var(--text);
    font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
  main{max-width:60rem;margin:0 auto}
  h1{font-size:1.6rem;margin:.2rem 0}
  h2{font-size:1.2rem;margin:2rem 0 .8rem;border-bottom:1px solid var(--border);padding-bottom:.3rem}
  h3{font-size:1rem;margin:1rem 0 .4rem}
  .muted{color:var(--muted);font-size:.9rem}
  .badge{display:inline-block;padding:.35rem 1rem;border-radius:999px;
    font-weight:700;font-size:1.05rem;color:#fff}
  .badge.go{background:var(--verde)} .badge.pivot{background:var(--ambar)} .badge.nogo{background:var(--rojo)}
  .sev{display:inline-block;padding:.05rem .5rem;border-radius:6px;font-size:.78rem;font-weight:600}
  .sev.fatal{background:var(--rojo-bg);color:var(--rojo);border:1px solid var(--rojo)}
  .sev.grave{background:var(--ambar-bg);color:var(--ambar);border:1px solid var(--ambar)}
  .sev.menor{background:var(--bg);color:var(--muted);border:1px solid var(--border)}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));gap:.8rem}
  .card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:.9rem 1rem}
  .card.verde{border-left:5px solid var(--verde)}
  .card.ambar{border-left:5px solid var(--ambar)}
  .card.rojo{border-left:5px solid var(--rojo)}
  table{border-collapse:collapse;width:100%;margin:.6rem 0;background:var(--card);font-size:.92rem}
  th,td{border:1px solid var(--border);padding:.45rem .6rem;text-align:left;vertical-align:top}
  th{background:var(--bg)}
  details{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);
    margin:.6rem 0;padding:.2rem .9rem}
  summary{cursor:pointer;font-weight:600;padding:.5rem 0}
  blockquote{border-left:3px solid var(--border);margin:.4rem 0;padding:.1rem .8rem;color:var(--muted)}
  .toolbar{margin:1rem 0}
  .toolbar button{font:inherit;padding:.3rem .8rem;border:1px solid var(--border);
    border-radius:6px;background:var(--card);cursor:pointer;margin-right:.5rem}
  a{color:#1d4ed8}
  footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--border);
    font-size:.85rem;color:var(--muted)}
  @media print{
    body{background:#fff;padding:0}
    .toolbar{display:none}
    details{border:none;padding:0}
    details>summary{list-style:none}
  }
</style>
</head>
<body>
<main>
  <header>
    <p class="muted">Reporte de viabilidad — {{FECHA}}</p>
    <h1>{{PROYECTO}}</h1>
    <p><span class="badge {{VEREDICTO_CLASE}}">{{VEREDICTO}}</span></p>
    <p>{{RAZON_DOMINANTE}}</p>
  </header>

  <div class="toolbar">
    <button onclick="document.querySelectorAll('details').forEach(d=>d.open=true)">Expandir todo</button>
    <button onclick="document.querySelectorAll('details').forEach(d=>d.open=false)">Colapsar todo</button>
  </div>

  <h2>Tablero por segmento</h2>
  <div class="cards">{{TABLERO_CARDS}}</div>

  <h2>Tesis (steelman confirmado)</h2>
  {{TESIS}}

  <h2>Hallazgos por segmento</h2>
  {{HALLAZGOS_SECCIONES}}

  <h2>Contradicciones no resueltas</h2>
  {{CONTRADICCIONES}}

  <h2>Gaps de documentación</h2>
  {{GAPS}}

  <h2>Modelo financiero</h2>
  {{FINMODEL_SECCION}}

  <h2>Mercado</h2>
  {{MERCADO_SECCION}}

  <h2>Qué cambiaría el veredicto</h2>
  {{CAMBIARIA_VEREDICTO}}

  <h2>Anexos — documentos fuente</h2>
  {{ANEXOS}}

  <footer>{{TRAZABILIDAD}}</footer>
</main>
<script>
  // Al imprimir, expandir todo (los colapsados no se imprimen si no).
  window.addEventListener('beforeprint',
    ()=>document.querySelectorAll('details').forEach(d=>d.open=true));
</script>
</body>
</html>
````

- [ ] **Step 2: Verify — slots present, no external URLs**

Run: `grep -o "{{[A-Z_]*}}" "C:\Proyectos\battle_tested_skills\viability-report\references\report-template.html" | sort -u | wc -l`
Expected: `15` (PROYECTO, FECHA, VEREDICTO, VEREDICTO_CLASE, RAZON_DOMINANTE, TABLERO_CARDS, TESIS, HALLAZGOS_SECCIONES, CONTRADICCIONES, GAPS, FINMODEL_SECCION, MERCADO_SECCION, CAMBIARIA_VEREDICTO, ANEXOS, TRAZABILIDAD)

Run: `grep -cE "https?://|@import|<link" "C:\Proyectos\battle_tested_skills\viability-report\references\report-template.html"`
Expected: `0` (fully self-contained)

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-report && git commit -m "feat(viability-report): HTML template with design system"
```

---

### Task 2: `SKILL.md`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-report\SKILL.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
---
name: viability-report
description: Renders the final viability dossier — ingests every pipeline output (manifest docs 00-07, latest veredicto-*.md from the gate, 04-modelo-financiero.md summary with QA flags) and populates a predefined self-contained HTML template (light design system, semáforo badges, collapsible sections, print-ready, zero external dependencies) into reporte-YYYY-MM-DD.html in the project folder. Robust and omission-free by contract: a mandatory completeness checklist cross-counts every finding, contradiction, gap, sensitivity scenario and source against the verdict before delivery. Use when the user says "genera el reporte de viabilidad", "arma el HTML del gate", "viability report", "reporte del proceso", or has just run viability-gate and wants the shareable dossier. Requires an existing veredicto (run the gate first). Read-only over sources; never edits manifest docs.
metadata:
  version: 1.0
---

# viability-report — Dossier HTML del proceso

Cierras el pipeline: todo lo que el proceso encontró, en un solo HTML que
abre offline y se imprime como dossier. El template
[`references/report-template.html`](references/report-template.html) ES el
design system — poblas slots `{{...}}`, no rediseñas. Idioma del contenido:
el de los docs (default español).

## Contrato

- **Lees:** docs `00-07` del manifest, el `veredicto-*.md` MÁS RECIENTE,
  `04-modelo-financiero.md` (outputs + flags QA). Al `.xlsx` solo lo
  enlazas (link relativo), no lo parseas.
- **Escribes:** SOLO `reporte-YYYY-MM-DD.html` en el folder del proyecto.
  Nunca pises un reporte previo (fecha distinta = archivo distinto; misma
  fecha = sufijo `-2`).

## Pasos

1. **Prerequisito.** Busca `veredicto-*.md` en el folder. Sin veredicto →
   detente: "corre viability-gate primero". El reporte es el cierre, no un
   sustituto del gate.

2. **Ingesta.** Lee veredicto (fuente de verdad del contenido 1-5 y 8),
   `04-modelo-financiero.md` (sección 6), `03-mercado.md` (sección 7), y los
   8 docs para anexos. Doc faltante = su sección/anexo lo declara
   explícitamente ("`07-gtm.md` no existe en este proyecto") — nunca se
   silencia.

3. **Población de slots.** Reglas:
   - `{{VEREDICTO_CLASE}}`: `go` / `pivot` / `nogo` según el veredicto.
   - Tablero: 1 card por segmento con clase `verde/ambar/rojo`, confianza y
     hallazgo dominante.
   - Hallazgos: un `<details>` por segmento — segmentos rojos con `open`,
     resto plegado. CADA hallazgo del veredicto: F-ID, badge de severidad
     (`sev fatal/grave/menor`), evidencia citada, estado de verificación,
     qué lo resolvería.
   - Finmodel: unit economics, breakeven/runway, tabla de sensibilidad
     COMPLETA (3 escenarios + conclusión), flags QA, link `<a href="04-modelo-financiero.xlsx">`.
   - Mercado: TAM dual con reconciliación, competidores con pricing,
     reality check, TODAS las fuentes citadas.
   - Anexos: un `<details>` plegado por doc, contenido íntegro convertido
     de markdown a HTML simple (headers, listas, tablas, blockquotes).
   - Trazabilidad: fechas de corridas, motores usados (línea de
     trazabilidad de 03 y 04), skills del pipeline.
   - Conversión markdown→HTML: escapa `<` y `&` del contenido fuente antes
     de envolver en tags.

4. **Checklist de completitud (obligatorio, antes de entregar):**
   - # hallazgos en veredicto == # hallazgos en el HTML (cuenta y compara).
   - Toda contradicción del veredicto presente.
   - Todo gap declarado presente.
   - 3 escenarios de sensibilidad + breakeven presentes.
   - Toda fuente citada de `03` presente en Mercado.
   - 8 docs presentes en Anexos (o su ausencia declarada).
   - Cero URLs externas en el HTML final (self-contained).
   Falla cualquiera → corrige y re-verifica. Resumir prosa está permitido;
   omitir items NO.

5. **Escritura y cierre.** Escribe el HTML. Presenta: path del reporte +
   tabla del checklist (item | ok) + el veredicto en una línea.

## Reglas duras

- El template es la fuente del diseño — no agregues CSS/JS por corrida ni
  cambies la estructura de secciones.
- Read-only sobre los docs fuente. El reporte refleja, no re-litiga: el
  veredicto del gate se reproduce tal cual, sin suavizar.
- Sin dependencias externas: nada de CDNs, fonts remotas, imágenes por URL.
````

- [ ] **Step 2: Verify frontmatter and cross-reference**

Run: `head -3 "C:\Proyectos\battle_tested_skills\viability-report\SKILL.md"`
Expected: frontmatter with `name: viability-report`

Run: `grep -c "report-template.html" "C:\Proyectos\battle_tested_skills\viability-report\SKILL.md"`
Expected: `>= 1`

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-report && git commit -m "feat(viability-report): SKILL.md orchestrator"
```

---

### Task 3: Verification + install + smoke

- [ ] **Step 1: Structural check**

Run: `ls "C:\Proyectos\battle_tested_skills\viability-report" "C:\Proyectos\battle_tested_skills\viability-report\references"`
Expected: `SKILL.md` + `references/report-template.html`.

- [ ] **Step 2: Slot inventory — every template slot has a population rule in SKILL.md**

Compare `grep -o "{{[A-Z_]*}}" report-template.html | sort -u` against SKILL.md step 3 rules. Every slot must be covered (PROYECTO/FECHA/RAZON_DOMINANTE/TESIS/CAMBIARIA_VEREDICTO are direct copies from veredicto — acceptable as covered by step 2/3 ingest rules). Uncovered slot = add rule.

- [ ] **Step 3: Design-doc consistency**

Against `C:\Obsidian\output\2026-07-22-viability-report-design.md`: hard prerequisite on veredicto; fixed section order; reds open by default; print expands all; completeness checklist items match; never overwrites.

- [ ] **Step 4: Install globally via junction**

PowerShell: `New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\viability-report" -Target "C:\Proyectos\battle_tested_skills\viability-report"`
Expected: junction created.

- [ ] **Step 5: Smoke test — render template with dummy data**

In scratchpad: replace all 15 slots with dummy strings (e.g. via Python `str.replace`), write `smoke.html`, verify: zero `{{` remaining, file opens as valid HTML (starts with `<!DOCTYPE html>`, balanced `</html>`), zero external URLs. Delete after.
