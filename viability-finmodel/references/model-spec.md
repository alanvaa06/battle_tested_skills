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
