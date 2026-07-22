# Manifest canónico — viability-gate

Folder de proyecto esperado. Nombres numerados = orden de lectura.

| Doc | Contenido mínimo | Alimenta | Obligatorio |
|---|---|---|---|
| `00-tesis.md` | Apuesta en ≤10 líneas + falsificadores (condiciones que matarían la tesis) | Todos | Sí |
| `01-identidad-producto.md` | Problema, propuesta de valor, diferenciación, por qué ahora | Producto | Sí |
| `02-cliente-ideal.md` | ICP, job-to-be-done, disposición a pagar, cómo alcanzarlo | Mercado | Sí |
| `03-mercado.md` | TAM/SAM/SOM con fuentes citadas, competidores, alternativas actuales del cliente | Mercado | Sí |
| `04-modelo-financiero.md` o `.xlsx` | Pricing, volumen proyectado, unit economics (CAC/LTV/margen), costos de operación, breakeven, runway | Finanzas | Sí |
| `05-stack-arquitectura.md` | Stack, subscripciones y costos de infra/APIs, build-vs-buy, límites de escala | Técnico | Sí |
| `06-plan-ejecucion.md` | Scope del MVP, ciclo de desarrollo, milestones, quién construye/vende | Ejecución | Sí |
| `07-gtm.md` | Canales, motion de venta, primeros 10 clientes | Mercado/Ejecución | No |

## Reglas de ingesta

1. **Doc obligatorio faltante** = gap declarado. Nunca bloquea la corrida. El gap
   capa la confianza del segmento afectado a máximo "media" (uno faltante) o
   "baja" (dos o más faltantes que alimenten ese segmento).
2. `07-gtm.md` faltante: GTM se estresa desde `02-cliente-ideal.md` y
   `06-plan-ejecucion.md`; no cuenta como gap.
3. Formato `.md` preferido. `.xlsx` aceptado solo para el modelo financiero
   (leer con la skill de xlsx disponible en el harness).
4. `00-tesis.md` sin falsificadores explícitos → registrar hallazgo automático:
   `F-AUTO-1 | severidad: grave | "Tesis no falsificable: el autor no declaró
   condiciones que matarían el proyecto"` asignado al segmento Ejecución.
5. Archivos extra en el folder (no listados aquí): leerlos, citarlos si son
   útiles, pero no crean segmentos ni obligaciones nuevas.
6. Mapeo doc→segmento de la tabla es *principal*, no exclusivo: cualquier crítico
   puede citar cualquier doc.
