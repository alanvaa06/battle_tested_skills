# viability-finmodel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `viability-finmodel` skill — captures missing financial drivers via mini-interview, builds a live driver-based unit-economics Excel model (formulas, Anthropic conventions), pre-runs the gate CFO's sensitivity scenarios, runs a mandatory internal QA, and writes `04-modelo-financiero.xlsx` + `.md` summary.

**Architecture:** SKILL.md orchestrator + 3 references: `model-spec.md` (tab architecture, drivers, key formulas), `excel-standards.md` (distilled from Anthropic 3-statements plugin), `model-qa.md` (distilled from check-model plugin, scoped to pre-seed driver models, always runs). Self-contained: same capabilities in Claude Code and Cowork, no plugin delegation.

**Tech Stack:** Markdown (skill) + xlsx skill at runtime for the Excel build. Verification: structural + header contract vs `scaffold-viability-gate/templates/04-modelo-financiero.md` + design doc `C:\Obsidian\output\2026-07-22-viability-finmodel-design.md`.

**Note:** Repo is git (main). Commit per task.

---

### Task 1: `references/excel-standards.md`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-finmodel\references\excel-standards.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Estándares Excel — viability-finmodel

Destilado del plugin Anthropic `financial-analysis/3-statements`, acotado a
modelos driver-based de viabilidad pre-seed. Self-contained: no depende del
plugin.

## Layout

- Cada tab: título del modelo en fila 1, fila de unidades (MXN, %, x, meses)
  bajo los headers, columnas de periodo etiquetadas `M1..M36`.
- Labels de línea en la columna A; periodos hacia la derecha; orden de
  columnas idéntico en todos los tabs.
- Flujo de tabs fijo: `Assumptions → Revenue Build → Costos → Unit Economics
  → P&L → Caja & Runway → Sensibilidad → Checks`.
- Sin tabs ni filas ocultas. Sin merged cells en rangos de cálculo.

## Inputs vs fórmulas

- **TODOS los inputs viven en Assumptions.** Ningún otro tab contiene
  números tecleados — solo fórmulas y referencias.
- Color coding: **azul = input** (solo en Assumptions), **negro = fórmula**,
  **verde = referencia a otro tab**.
- Assumptions lleva 3 columnas por supuesto: `Valor | Base | Etiqueta`.
  Base = de dónde sale (benchmark de 03, dato propio, cotización). Etiqueta =
  `verificado / hipótesis sin base / hipótesis intake`.
- Cero hardcodes parciales dentro de fórmulas (`=B5*1.16` prohibido — el
  1.16 va a Assumptions como IVA).
- Fórmulas consistentes en todo el rango: la misma fórmula arrastrada por
  fila, sin excepciones silenciosas a media tabla.

## Named ranges

Outputs clave con named range para lectura programática y del gate:
`Precio_Unit`, `Churn_Mensual`, `CAC_Total`, `LTV`, `LTV_CAC`,
`Margen_Bruto_Pct`, `Breakeven_Mes`, `Runway_Meses`, `Capital_Inicial`,
`EBITDA_M24`.

## Convenciones de cálculo

- Modelo mensual, horizonte 24-36 meses (input en Assumptions).
- Moneda única declarada en Assumptions; sin mezclas MXN/USD sin conversión
  explícita (tipo de cambio = input con base).
- Fórmulas vivas siempre — nunca valores pegados producto de un cálculo
  externo.
````

- [ ] **Step 2: Verify**

Run: `grep -c "^## " "C:\Proyectos\battle_tested_skills\viability-finmodel\references\excel-standards.md"`
Expected: `4`

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-finmodel && git commit -m "feat(viability-finmodel): excel standards (distilled 3-statements)"
```

---

### Task 2: `references/model-qa.md`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-finmodel\references\model-qa.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# QA del modelo — viability-finmodel

Destilado del plugin Anthropic `financial-analysis/check-model`, acotado a
modelos driver-based pre-seed (descartado: M&A, goodwill, LBO, dilución,
3-statement ties). **SIEMPRE corre — nunca condicional.** El modelo no se
entrega con checks en rojo sin corrección o justificación documentada.

## 1. Checks estructurales

- Inputs SOLO en Assumptions; ningún número tecleado en otros tabs.
- Fórmulas consistentes por rango (misma fórmula arrastrada; detectar
  excepciones a media fila).
- Cero hardcodes parciales dentro de fórmulas.
- Cero errores `#REF! / #VALUE! / #N/A / #DIV/0!`.
- Sin tabs/filas ocultas; sin celdas formateadas como fórmula con valor
  pegado.
- Named ranges del estándar presentes y apuntando a celdas correctas.

## 2. Checks de integridad (ties entre tabs)

- Revenue del P&L = MRR del Revenue Build (cada mes).
- Costos del P&L = fijos + variables del tab Costos (cada mes).
- Caja fin de mes = caja inicial + flujo neto acumulado (cada mes).
- Unit Economics usa LOS MISMOS drivers de Assumptions que el P&L — sin
  cálculos duplicados con supuestos distintos.
- Unidades y moneda consistentes en todos los tabs.
- Tab Checks materializa estos ties como fórmulas `=IF(...,"OK","ERROR")`
  visibles.

## 3. Checks de lógica (razonabilidad)

- Tasa de crecimiento o conversión >2× el benchmark de `03-mercado.md` sin
  base declarada = flag.
- Churn mensual <1% sin base = flag (optimismo no documentado).
- LTV/CAC >10 = sospechoso (suele ser CAC subestimado); <1 = el modelo grita.
- Margen bruto fuera del rango de la categoría (vs benchmarks de 03) = flag.
- Hockey stick: crecimiento que se acelera sin driver nuevo = flag.
- Breakeven después del fin del runway = hallazgo mayor, va al resumen.
- CAC "orgánico = $0" = flag (tiempo del founder no es gratis).

## 4. Edge cases (correr en el modelo real)

- Crecimiento 0%: ¿el modelo degrada con gracia o rompe?
- Churn ×2: ¿LTV sigue positivo?
- Precio −50%: ¿divide-by-zero o negativos sin manejar?
- Caja negativa: debe SEÑALARSE (formato/check), no ocultarse.

## 5. Veredicto QA

Tabla obligatoria al cierre de la corrida:

```
| Check | Resultado | Acción |
|---|---|---|
| Estructural | OK / ERROR | — o corrección aplicada |
| Integridad  | OK / ERROR | ... |
| Lógica      | OK / n flags | flags listados con justificación o corrección |
| Edge cases  | OK / detalle | ... |
```

Flags de lógica no corregidos se copian al resumen `.md` — son candidatos a
rojo en el gate y el founder debe verlos antes.
````

- [ ] **Step 2: Verify**

Run: `grep -c "^## " "C:\Proyectos\battle_tested_skills\viability-finmodel\references\model-qa.md"`
Expected: `5`

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-finmodel && git commit -m "feat(viability-finmodel): model QA (distilled check-model)"
```

---

### Task 3: `references/model-spec.md`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-finmodel\references\model-spec.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Especificación del modelo — viability-finmodel

Modelo driver-based de unit economics, mensual, 24-36 meses. NO es un
3-statement: sin balance ni estado de flujos formal. Si el proyecto tiene
inventario, capex pesado o deuda estructural, declarar el 3-statement fuera
de alcance de esta skill en vez de improvisarlo.

## Drivers (tab Assumptions)

| Driver | Fuente preferida |
|---|---|
| Precio y modelo de cobro | Hipótesis de `04` (intake) contrastada con benchmarks de `03` |
| Prospectos/mes por canal | `07-gtm` + entrevista |
| Conversión prospecto→cliente | Entrevista (base obligatoria; benchmark de 03 si existe) |
| Churn mensual | Entrevista + benchmark de categoría en `03` |
| CAC presupuestado (todo incluido: ads + tiempo founder + herramientas) | Entrevista |
| Costos fijos mensuales | Entrevista + `05-stack` (subscripciones/infra) |
| Costo variable por cliente/mes (infra, APIs, soporte) | `05-stack` + entrevista |
| Capital inicial disponible | Entrevista |
| Horizonte del modelo (meses) | Default 36; entrevista |
| IVA / tipo de cambio (si aplica) | Dato oficial |

Cada driver: `Valor | Base | Etiqueta (verificado / hipótesis intake /
hipótesis sin base)`.

## Cálculos por tab (fórmulas clave)

**Revenue Build** (mensual):
- `nuevos_t = prospectos_t × conversión`
- `activos_t = activos_(t-1) × (1 − churn) + nuevos_t`
- `MRR_t = activos_t × precio`

**Costos**:
- `variables_t = activos_t × costo_var_unit + nuevos_t × CAC`
- `fijos_t = suma de fijos mensuales`

**Unit Economics**:
- `margen_bruto_unit = precio − costo_var_unit`
- `LTV = margen_bruto_unit / churn` (fórmula estándar SaaS)
- `LTV/CAC`; `payback_CAC_meses = CAC / margen_bruto_unit`

**P&L** (mensual): `EBITDA_t = MRR_t − variables_t − fijos_t`

**Caja & Runway**:
- `caja_t = caja_(t-1) + EBITDA_t` (arrancando de Capital_Inicial)
- `Breakeven_Mes` = primer mes con EBITDA ≥ 0 sostenido 3 meses
- `Runway_Meses` = último mes con caja ≥ 0 en escenario base

**Sensibilidad** — 3 escenarios del CFO del gate, uno a la vez:
`volumen ÷3`, `precio −30%`, `CAC ×2`. Tabla: escenario × (Breakeven_Mes,
Runway_Meses, LTV/CAC, EBITDA_M24) + fila de conclusión: "escenario que mata
el proyecto primero y por qué".

**Checks**: ties de model-qa.md sección 2 como fórmulas visibles.

## Resumen ejecutivo (`04-modelo-financiero.md`)

Headers EXACTOS del template del scaffold (contrato con el gate), cada
sección con outputs del xlsx y referencia `(ver 04-modelo-financiero.xlsx,
tab X)`:

```
## Pricing            ← precio, modelo de cobro, base
## Volumen proyectado ← funnel resumido con tasas y bases
## Unit economics     ← CAC, LTV, LTV/CAC, payback, margen
## Costos de operación← fijos + variables, tie con 05-stack
## Breakeven y runway ← Breakeven_Mes, Runway_Meses, escenario letal, flags QA
```

Al final, línea de trazabilidad:
`> Modelo construido por viability-finmodel — YYYY-MM-DD. QA: [OK | n flags].`
````

- [ ] **Step 2: Verify**

Run: `grep -c "^## " "C:\Proyectos\battle_tested_skills\viability-finmodel\references\model-spec.md"`
Expected: `3`

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-finmodel && git commit -m "feat(viability-finmodel): model spec"
```

---

### Task 4: `SKILL.md`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-finmodel\SKILL.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
---
name: viability-finmodel
description: Builds the viability financial model — captures missing drivers via mini-interview (churn, funnel rates, CAC, fixed costs, starting capital; every assumption with a declared basis), builds a live driver-based unit-economics Excel model (monthly, 24-36m, formulas not pasted values, Anthropic template conventions), pre-runs the gate CFO's sensitivity scenarios (volume ÷3, price −30%, CAC ×2), runs a mandatory internal QA, and writes 04-modelo-financiero.xlsx plus a .md executive summary. Use when the user says "corre el modelo financiero", "construye el finmodel", "arma el 04", "viability finmodel", or has completed intake/research and needs the financial model. Not a 3-statement model (declares out of scope if the project needs inventory/capex/debt modeling). Only writes 04. Not for stress-testing (gate), interviews beyond numeric drivers (intake), or market data gathering (research).
metadata:
  version: 1.0
---

# viability-finmodel — Modelo financiero de viabilidad

Construyes el modelo que el CFO del gate va a intentar romper. Rigor:
[`references/model-spec.md`](references/model-spec.md) (arquitectura y
fórmulas), [`references/excel-standards.md`](references/excel-standards.md)
(convenciones Excel), [`references/model-qa.md`](references/model-qa.md)
(QA obligatorio). Usa la skill de xlsx del harness para construir el archivo.
Idioma: el del usuario (default español).

## Contrato

- **Lees:** hipótesis de pricing de `04`, ICP/canal de `02` y `07`,
  benchmarks de `03-mercado.md`, costos de stack de `05`.
- **Escribes:** SOLO `04-modelo-financiero.xlsx` + `04-modelo-financiero.md`.

## Pasos

1. **Prerequisito.** Intake corrido (hipótesis de pricing en `04`). `03`
   deseable — sin él, corre pero declara "benchmarks ausentes" y los checks
   de lógica que dependen de benchmark quedan `no evaluable`. `04` ya con
   modelo completo → no-op salvo re-corrida explícita (anterior se renombra
   `04-modelo-financiero-YYYY-MM-DD.bak.xlsx/.md`, nunca se pisa).

2. **Captura de drivers.** Primero los docs (tabla de fuentes en model-spec).
   Solo lo faltante se pregunta: UNA pregunta por turno (patrón intake).
   Todo driver exige base declarada; sin base = se registra `hipótesis sin
   base`, tal cual. "No sé" = pide un rango y usa el punto medio, etiquetado.

3. **Construcción.** `.xlsx` según model-spec + excel-standards: fórmulas
   vivas, inputs solo en Assumptions (azul), named ranges, cero hardcodes.
   Construye con la skill de xlsx disponible en el harness.

4. **Sensibilidad.** Tab con los 3 escenarios del CFO pre-corridos + la
   conclusión "qué mata al proyecto primero". El gate recalcula — tu trabajo
   es que llegue computado, no adivinado.

5. **QA obligatorio.** Corre model-qa.md COMPLETO (estructural, integridad,
   lógica, edge cases). Checks en rojo: corrige y re-corre, o documenta la
   justificación en la tabla de veredicto QA. Nunca entregues sin la tabla.

6. **Escritura dual.** El `.xlsx` + el `.md` resumen con los headers exactos
   del template (contrato con el gate) y la línea de trazabilidad.

7. **Cierre.** Presenta: outputs clave (breakeven, runway, LTV/CAC,
   escenario letal), lista de supuestos `hipótesis sin base` (candidatos a
   rojo en el gate), flags de QA no corregidos, y próximo paso: correr
   `viability-gate`.

## Reglas duras

- Fórmulas > valores. Un xlsx con números pegados no es un modelo.
- Ningún supuesto silencioso: todo driver tiene base o etiqueta de que no
  la tiene.
- El QA no es opcional ni degradable — es parte de la definición de
  terminado.
- Monte Carlo fuera de alcance: escenarios bastan a pre-seed.
- 3-statement fuera de alcance: si el proyecto lo necesita, decláralo.
````

- [ ] **Step 2: Verify frontmatter and cross-references**

Run: `head -3 "C:\Proyectos\battle_tested_skills\viability-finmodel\SKILL.md"`
Expected: frontmatter with `name: viability-finmodel`

Run: `grep -c "references/" "C:\Proyectos\battle_tested_skills\viability-finmodel\SKILL.md"`
Expected: `>= 3`

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-finmodel && git commit -m "feat(viability-finmodel): SKILL.md orchestrator"
```

---

### Task 5: Verification + install

- [ ] **Step 1: Structural check**

Run: `ls "C:\Proyectos\battle_tested_skills\viability-finmodel" "C:\Proyectos\battle_tested_skills\viability-finmodel\references"`
Expected: `SKILL.md` + 3 references (model-spec, excel-standards, model-qa).

- [ ] **Step 2: Header contract check**

The 5 headers in model-spec's resumen section must match `scaffold-viability-gate/templates/04-modelo-financiero.md` verbatim: `Pricing`, `Volumen proyectado`, `Unit economics`, `Costos de operación`, `Breakeven y runway`. Mismatch = fix model-spec.

- [ ] **Step 3: Design-doc consistency**

Against `C:\Obsidian\output\2026-07-22-viability-finmodel-design.md`: QA unconditional; dual output; driver-based not 3-statement (with out-of-scope declaration); 3 CFO scenarios exact (`volumen ÷3`, `precio −30%`, `CAC ×2`); named ranges list present; backup-on-rerun; every assumption has Base column.

- [ ] **Step 4: Install globally via junction**

PowerShell: `New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\viability-finmodel" -Target "C:\Proyectos\battle_tested_skills\viability-finmodel"`
Expected: junction created.

- [ ] **Step 5: Full-pipeline dogfood note (user-run, out of scope)**

Real validation: scaffold → intake → research → finmodel → gate on a live project. The Excel build path is exercised the first time the skill runs with the xlsx skill.
