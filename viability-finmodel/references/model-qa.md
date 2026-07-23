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
