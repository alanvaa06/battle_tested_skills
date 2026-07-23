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
