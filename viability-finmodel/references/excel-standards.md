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
