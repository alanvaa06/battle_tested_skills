# Template — Veredicto de Viabilidad

Escribir en el folder analizado como `veredicto-YYYY-MM-DD.md` (fecha del día;
versionado por fecha = historial de re-corridas; nunca sobrescribir un
veredicto previo).

```markdown
# Veredicto de Viabilidad — [Proyecto] — [YYYY-MM-DD]

## Veredicto: GO | PIVOT | NO-GO

[1-2 líneas: la razón dominante del veredicto, en lenguaje directo.]

## Tesis (steelman confirmado)

[1 párrafo — la versión más fuerte de la tesis, confirmada por el usuario
en fase 2.]

## Tablero por segmento

| Segmento | Semáforo | Confianza | Hallazgo dominante |
|---|---|---|---|
| Mercado | 🟢/🟡/🔴 | alta/media/baja | [una línea] |
| Finanzas | 🟢/🟡/🔴 | alta/media/baja | [una línea] |
| Técnico | 🟢/🟡/🔴 | alta/media/baja | [una línea] |
| Ejecución | 🟢/🟡/🔴 | alta/media/baja | [una línea] |

## Hallazgos por segmento

### [Segmento]
[Por hallazgo, en orden de severidad:]
- **[F-ID] [severidad: fatal/grave/menor]** — [hallazgo en una oración].
  Evidencia: `[doc]` — "[cita breve]". Verificación: [verificado/contradicho/
  no-verificable/no-aplica + fuente]. Crítico: [lente]. Lo resolvería:
  [evidencia concreta].

## Contradicciones no resueltas

[Cruces entre críticos que quedaron abiertos tras el consenso. Si ninguna:
"Ninguna."]

## Gaps de documentación

[Docs/datos faltantes y qué segmento capan. Si ninguno: "Manifest completo."]

## Qué cambiaría el veredicto

[Por cada segmento rojo/amarillo: la evidencia concreta y verificable que lo
voltearía. Este es el TODO list del usuario.]

## Condiciones de re-evaluación

[Cuándo volver a correr el gate: qué docs actualizar, qué evidencia conseguir,
qué trigger temporal.]
```

## Reglas del reporte
- Todo hallazgo cita doc fuente; sin evidencia citada no entra al reporte.
- Severidad y semáforos vienen de las reglas deterministas del SKILL.md —
  el reporte no re-litiga el veredicto.
- Si el veredicto es GO, decirlo con la misma franqueza que un NO-GO: falsos
  rojos queman confianza en el gate (regla heredada de roast-me).
