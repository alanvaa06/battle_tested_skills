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
