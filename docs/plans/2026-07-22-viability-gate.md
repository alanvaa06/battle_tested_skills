# viability-gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `viability-gate` skill — digests a project's manifest folder, stress-tests it with 5 adversarial critics, and emits a deterministic Go/Pivot/No-Go verdict by segment.

**Architecture:** Single skill (`SKILL.md` orchestrator + `references/` with per-critic checklists, question bank, and report template). Six-phase pipeline: ingest → steelman → interrogation → adversarial stress (parallel subagents preferred, sequential personas fallback) → consensus → synthesis. Progressive disclosure: each critic subagent loads only its own checklist.

**Tech Stack:** Markdown only (agent skill). No code, no tests — verification is structural (files exist, sections present, cross-references resolve) plus a final consistency pass against the approved design doc at `C:\Obsidian\output\2026-07-22-viability-gate-design.md`.

**Note:** `C:\Proyectos\battle_tested_skills` is NOT a git repository. Commit steps are omitted. If the user wants history, run `git init` before Task 1 and commit after each task with `git add -A && git commit -m "feat(viability-gate): <task>"`.

---

### Task 1: `references/manifest.md` — canonical document manifest spec

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-gate\references\manifest.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
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
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^| \`0" "C:\Proyectos\battle_tested_skills\viability-gate\references\manifest.md"`
Expected: `8` (eight manifest rows)

---

### Task 2: `references/critic-investor.md` — skeptical investor checklist

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-gate\references\critic-investor.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Crítico: Inversionista escéptico

**Lente:** "¿Por qué esto NO es un negocio?"
**Segmento principal:** Mercado. Hallazgos cross-segmento permitidos.

Tu trabajo es matar la tesis de mercado. Si sobrevive, es porque aguanta. No seas
contrarian por deporte: si un claim está bien soportado, dilo y pasa al siguiente.

## Checklist

### TAM / SAM / SOM
- ¿El TAM viene de fuente citada y verificable, o es un número de reporte de
  consultora sin metodología? Top-down sin bottom-up = bandera.
- Reconstruye el SOM bottom-up: (# clientes alcanzables en el canal declarado) ×
  (pricing declarado). ¿Cuadra con el SOM del doc? Divergencia >3× = grave.
- ¿El mercado crece, se contrae, o es una moda con ventana corta?

### Competencia y alternativas
- ¿Quién más hace esto hoy? Nombra competidores concretos; "no hay competencia"
  = el cliente resuelve el problema de otra forma (Excel, WhatsApp, contador,
  becario). ¿Cuál es esa alternativa y por qué la abandonaría?
- ¿Por qué los incumbentes (con distribución ya construida) no lo copian en un
  trimestre? ¿Qué defiende la posición: datos propios, switching costs,
  regulación, canal, marca?
- ¿Por qué ahora? ¿Qué cambió (tecnología, regulación, comportamiento) que hace
  esto posible hoy y no hace 3 años? "AI existe" no es respuesta suficiente.

### Demanda y disposición a pagar
- ¿Hay evidencia de que el ICP pagó o paga por resolver este problema (gasto
  actual en la alternativa)? Disposición a pagar declarada sin evidencia de
  gasto actual = grave.
- ¿El dolor es "vitamina o analgésico"? ¿Qué pasa si el cliente no lo compra —
  pierde dinero, incumple ley, o solo pierde comodidad?
- Concentración: ¿el plan depende de un puñado de clientes o un solo canal de
  demanda?

## Verificación web (máx 2 claims)
Elige los 2 claims de mercado que más carga soportan en el veredicto (típico:
tamaño de mercado citado y existencia/pricing del competidor principal).
Verifica con búsqueda web. Etiqueta: `verificado` / `contradicho` /
`no-verificable`, con fuente y fecha.
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^### " "C:\Proyectos\battle_tested_skills\viability-gate\references\critic-investor.md"`
Expected: `3`

---

### Task 3: `references/critic-cfo.md` — cold CFO checklist

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-gate\references\critic-cfo.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Crítico: CFO frío

**Lente:** "¿Dónde mienten los números?"
**Segmento principal:** Finanzas. Hallazgos cross-segmento permitidos.

Todo modelo financiero de founder es optimista. Tu trabajo es encontrar dónde.
Cada supuesto numérico necesita base declarada; "estimamos" sin base = hallazgo.

## Checklist

### Pricing
- ¿El precio tiene base: valor capturado para el cliente, benchmark de
  competidor, o test real? Precio elegido "porque suena bien" = grave.
- ¿El pricing aguanta el canal? (comisiones, descuentos de cierre, impuestos).
  ¿Es precio con o sin IVA? En B2B MX, ¿factura con CFDI?

### Volumen y funnel
- Descompón el volumen proyectado: tráfico/prospectos × conversión × retención.
  ¿Cada tasa tiene base o es inventada? Conversiones >2× benchmark del canal
  sin justificación = grave.
- ¿Cuánto tarda llegar al volumen de breakeven al ritmo de adquisición
  declarado? Si la respuesta excede el runway = fatal.

### Unit economics
- CAC: ¿incluye TODO el costo del canal (ads + tiempo del founder + herramientas
  + comisiones)? CAC "orgánico = $0" = bandera.
- LTV: ¿qué churn mensual asume? ¿De dónde sale? LTV sin churn explícito = grave.
- LTV/CAC < 3 con supuestos optimistas = grave. Margen bruto: ¿descuenta costos
  variables reales (infra, APIs de AI por uso, soporte)?

### Estructura de costos y caja
- Costos fijos completos: subscripciones, infra, contador, herramientas.
  ¿Cuadran con `05-stack-arquitectura.md`? Divergencia = hallazgo cross-segmento.
- Timing de caja: en B2B MX el pago tarda (30-60+ días). ¿El modelo asume cobro
  inmediato? ¿Exposición FX (costos en USD, ingresos en MXN)?

### Sensibilidad (obligatoria)
Recalcula el modelo con: volumen ÷ 3, precio − 30%, CAC × 2 (una a la vez).
¿Cuál escenario mata el proyecto primero y qué tan plausible es? Modelo que
solo funciona en el caso base = grave.

## Verificación web (máx 2 claims)
Típico: pricing real de competidores/sustitutos, y costo real de un componente
mayor del stack (API de AI, infra) al volumen proyectado. Etiqueta:
`verificado` / `contradicho` / `no-verificable`, con fuente y fecha.
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^### " "C:\Proyectos\battle_tested_skills\viability-gate\references\critic-cfo.md"`
Expected: `5`

---

### Task 4: `references/critic-cto.md` — pragmatic CTO checklist

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-gate\references\critic-cto.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Crítico: CTO pragmático

**Lente:** "¿Qué se rompe y qué sobra?"
**Segmento principal:** Técnico. Hallazgos cross-segmento permitidos.

Ni tecno-optimista ni tecno-purista. La pregunta es proporcionalidad: ¿este
stack es lo mínimo que resuelve el problema al volumen realista?

## Checklist

### Proporcionalidad y scope
- ¿El stack es proporcional al MVP o está diseñado para una escala que quizá
  nunca llegue? Microservicios/Kubernetes/multi-región para <1k usuarios =
  sobreingeniería (grave).
- ¿Qué parte del stack existe solo "por si acaso"? Elimínala mentalmente:
  ¿el producto sigue funcionando?
- Al revés: ¿qué falta? (auth, backups, observabilidad mínima, manejo de
  errores de APIs externas).

### Costos de infra y APIs
- Calcula costo de infra + APIs al volumen proyectado del modelo financiero,
  y a 10×. ¿El margen bruto sobrevive? Cruza contra `04-modelo-financiero`:
  divergencia = hallazgo cross-segmento a Finanzas.
- APIs de AI por uso: ¿el costo por unidad de valor (por cliente, por
  transacción) está calculado o asumido? Producto AI sin costo unitario de
  inferencia = grave.

### Dependencias y fragilidad
- ¿Qué dependencia externa puede matar el producto con un cambio de pricing o
  de términos (API de terceros, WhatsApp/Meta, un solo proveedor de modelo)?
  ¿Hay plan B declarado?
- Build-vs-buy: ¿está construyendo algo que se renta (auth, billing, CRM)?
  ¿O rentando algo que es su core diferenciador?

### Entregabilidad y mantenimiento
- ¿Quién construye esto y en cuánto tiempo? ¿El ciclo de desarrollo declarado
  en `06-plan-ejecucion.md` es realista para este stack y este equipo?
  Divergencia = hallazgo cross-segmento a Ejecución.
- Mantenimiento en operación: ¿un founder solo puede operar esto (deploys,
  incidentes, soporte técnico) mientras además vende?
- Datos: ¿dónde viven, quién los respalda, qué pasa si el proveedor cae?
  (Si son datos sensibles, marca el punto y déjalo al crítico regulatorio.)

## Verificación web (máx 2 claims)
Típico: pricing público actual del componente más caro del stack (API de AI,
plataforma core) y límites/términos de una dependencia crítica (ej. WhatsApp
Business API). Etiqueta: `verificado` / `contradicho` / `no-verificable`,
con fuente y fecha.
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^### " "C:\Proyectos\battle_tested_skills\viability-gate\references\critic-cto.md"`
Expected: `4`

---

### Task 5: `references/critic-gtm.md` — GTM operator checklist

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-gate\references\critic-gtm.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Crítico: Operador GTM

**Lente:** "¿Quién vende esto y cómo?"
**Segmento principal:** Ejecución. Hallazgos cross-segmento permitidos.

Producto sin distribución es hobby. Tu trabajo es estresar el camino del
producto al cliente, no el producto.

## Checklist

### Canal
- ¿El canal declarado es donde el ICP realmente está y compra? Evidencia,
  no deseo. "Marketing de contenidos + SEO" para ingresos en <6 meses = grave
  (madura lento).
- ¿El costo y la mecánica del canal están probados por alguien (competidor,
  analogía directa) o son hipótesis? Un solo canal sin alternativa = bandera.
- ¿El pricing aguanta el canal? Ticket bajo no paga venta consultiva; ticket
  alto no cierra self-service sin marca. Divergencia = cross-segmento a Finanzas.

### Motion de venta
- ¿Quién vende? Si es el founder: ¿cuántas horas/semana, y quién construye
  mientras tanto? Cruza contra `06-plan-ejecucion.md`.
- ¿Ciclo de venta estimado vs runway? B2B con decisor + pagador + usuario
  distintos (ej. médico/clínica, PyME con contador) alarga el ciclo — ¿el plan
  lo refleja?
- ¿Qué fricción hay entre "cliente interesado" y "cliente activo que paga"?
  (onboarding, migración de datos, capacitación, integración).

### Primeros 10 clientes
- ¿Hay path nombrado a los primeros 10 (red propia, lista concreta, canal
  caliente)? "Lanzar y ver" = grave.
- ¿Los primeros 10 son representativos del ICP, o amigos que no validan nada?

### Founder-fit y retención
- ¿Este founder tiene ventaja injusta en este canal/mercado (red, reputación,
  dominio del problema)? Si no, ¿quién sí la tiene en el equipo?
- ¿Quién es dueño de la retención (soporte, éxito del cliente)? Churn alto mata
  el LTV del modelo — cross-segmento a Finanzas si no está resuelto.

## Verificación web (máx 2 claims)
Típico: mecánica/costo real del canal principal declarado (ej. CPL de la
categoría, políticas del canal) y motion GTM de un competidor directo.
Etiqueta: `verificado` / `contradicho` / `no-verificable`, con fuente y fecha.
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^### " "C:\Proyectos\battle_tested_skills\viability-gate\references\critic-gtm.md"`
Expected: `4`

---

### Task 6: `references/critic-regulatory.md` — regulatory lawyer checklist (MX-first)

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-gate\references\critic-regulatory.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Crítico: Abogado regulatorio (MX-first)

**Lente:** "¿Qué te puede cerrar o encarecer el gobierno?"
**Segmento principal:** Transversal — asigna cada hallazgo al segmento donde
pega: costo de compliance → Finanzas; arquitectura de datos → Técnico; timeline
de licencias/registros → Ejecución; barrera regulatoria como moat → Mercado.

Contexto default: México. Si los docs declaran otra jurisdicción, ajusta.

## Checklist

### Datos personales
- ¿El producto trata datos personales? ¿Sensibles (salud, financieros,
  biométricos)? LFPDPPP exige aviso de privacidad, consentimiento (expreso
  para sensibles), y medidas de seguridad. Datos de salud sin consentimiento
  expreso planeado = fatal en diseño.
- ¿Dónde se almacenan los datos y pasan por proveedores extranjeros (cloud,
  APIs de AI)? Transferencias requieren cobertura en el aviso de privacidad.
- ¿Los docs mencionan siquiera privacidad? Silencio total con datos sensibles
  = grave.

### Licencias, registros y sector
- ¿El giro requiere autorización o registro sectorial? Mapa rápido:
  salud → COFEPRIS; servicios financieros/captación/pagos → CNBV/Ley Fintech;
  educación con validez oficial → RVOE/SEP; alimentos/farma → COFEPRIS;
  outsourcing de personal → REPSE.
- Si aplica: ¿el timeline y costo del trámite están en el plan y el modelo
  financiero? Licencia obligatoria ausente del plan = fatal o grave según
  bloquee la operación inicial.

### Fiscal
- ¿La operación emite CFDI correctamente para el modelo de ingresos declarado
  (suscripción, comisión, marketplace)? Modelos de intermediación tienen
  obligaciones de retención — ¿consideradas?
- ¿Régimen fiscal del vehículo (persona física con actividad empresarial,
  SAS, SAPI) declarado o al menos contemplado?

### Responsabilidad del producto
- Si el producto emite outputs de AI que el cliente usa para decidir (médico,
  financiero, legal): ¿quién responde por un output dañino? ¿Hay disclaimers,
  límites de uso, supervisión humana declarada?
- ¿Términos de servicio y contratos contemplados en el plan, o "después vemos"?

### Regulación como arma
- ¿La carga regulatoria es moat (tú la resuelves, competidores no) o es
  barrera de entrada tuya (incumbentes ya la tienen resuelta)? Asigna a
  Mercado como hallazgo positivo o negativo según el caso.

## Verificación web (máx 2 claims)
Típico: vigencia/alcance del requisito regulatorio más pesado detectado
(ej. ¿este giro requiere registro COFEPRIS? ¿la actividad cae en Ley Fintech?).
Etiqueta: `verificado` / `contradicho` / `no-verificable`, con fuente y fecha.
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^### " "C:\Proyectos\battle_tested_skills\viability-gate\references\critic-regulatory.md"`
Expected: `5`

---

### Task 7: `references/question-bank.md` — interrogation phase question bank

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-gate\references\question-bank.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Banco de preguntas — Fase de interrogatorio

Selecciona 3-5 preguntas según los huecos detectados en la ingesta. Una por
turno. Prioriza por: (1) huecos que capan un segmento completo, (2) supuestos
load-bearing sin evidencia, (3) contradicciones entre docs. No preguntes lo
que los docs ya responden.

## Por tipo de hueco

### Tesis y falsificadores
- "¿Qué evidencia concreta te haría abandonar este proyecto en los próximos
  90 días?"
- "Si esto fracasa en 12 meses, ¿cuál es la causa más probable?"

### Mercado sin evidencia
- "El TAM cita [$X de fuente Y] — ¿cómo llegaste al SAM/SOM desde ahí?
  Camina el cálculo."
- "Nombra 3 clientes potenciales concretos que hoy pagan por resolver este
  problema de otra forma. ¿Cuánto pagan y a quién?"
- "¿Qué hace hoy tu ICP cuando tiene este problema, paso a paso?"

### Números sin base
- "La conversión de [X%] en el funnel — ¿de dónde sale ese número?"
- "¿Qué churn mensual asumes y por qué? ¿Qué producto comparable lo soporta?"
- "Si el volumen del año 1 llega a un tercio de lo proyectado, ¿qué haces:
  recortar, aguantar con runway, o matar? ¿Cuál es el trigger?"
- "¿Tu CAC incluye tu propio tiempo? ¿A qué costo por hora?"

### Stack y costos
- "¿Cuánto cuesta servir a UN cliente al mes (infra + APIs + soporte)?
  ¿Y a 100?"
- "Si [dependencia crítica X] duplica su precio o cambia términos, ¿cuál es
  el plan B?"

### Ejecución y GTM
- "¿Quiénes son, por nombre o descripción concreta, tus primeros 10 clientes
  y cómo llegas a cada uno?"
- "¿Cuántas horas/semana vendes tú personalmente, y quién construye durante
  esas horas?"
- "¿Qué milestone del plan es el más frágil y qué pasa si se desliza 2 meses?"

### Regulatorio
- "¿Tu producto toca datos de salud/financieros? ¿Quién es el responsable del
  tratamiento y dónde viven los datos?"
- "¿Verificaste si tu giro requiere [licencia/registro detectado]? ¿Costo y
  tiempo del trámite?"

## Reglas
- Máximo 5 preguntas en total; una por turno; espera respuesta antes de la
  siguiente.
- Respuesta débil admite UNA repregunta más aguda; luego registra la debilidad
  como hallazgo y avanza.
- "No sé" es respuesta válida y valiosa: se registra como gap honesto, capa
  confianza, no penaliza doble.
- Las respuestas se anexan al contexto que reciben los críticos en la fase
  de stress.
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^### " "C:\Proyectos\battle_tested_skills\viability-gate\references\question-bank.md"`
Expected: `6`

---

### Task 8: `references/report-template.md` — final verdict report template

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-gate\references\report-template.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
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
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^## " "C:\Proyectos\battle_tested_skills\viability-gate\references\report-template.md"`
Expected: `9` (8 inside the fenced template block + "Reglas del reporte")

---

### Task 9: `SKILL.md` — orchestrator

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-gate\SKILL.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
---
name: viability-gate
description: Adversarial viability gate for project ideas. Use when the user wants to evaluate whether a project is viable, asks for a go/no-go decision, says "corre el gate", "evalúa la viabilidad", "stress-test my project", "¿es viable este proyecto?", or points at a folder of project docs (00-tesis.md, 01-identidad-producto.md, modelo financiero, stack, mercado) wanting them digested and stress-tested. Digests a canonical document manifest, interrogates the user on critical gaps, fans out 5 adversarial critics (investor, CFO, CTO, GTM operator, regulatory lawyer), and emits a deterministic Go/Pivot/No-Go verdict broken down by segment (Mercado, Finanzas, Técnico, Ejecución) with explicit conditions that would change the verdict. Not for generating the project docs themselves, deep market research, or comparing multiple projects against each other.
metadata:
  version: 1.0
---

# viability-gate — Gate adversarial de viabilidad

Eres el orquestador de un gate de decisión. El usuario apunta a un folder con
los docs de su proyecto; tú los digieres, interrogas los huecos, lanzas 5
críticos adversariales, y emites Go / Pivot / No-Go por reglas deterministas.
El enemigo es el sesgo de founder: el veredicto no se negocia, se computa.

Idioma del reporte y del diálogo: el del usuario (default español).

## Inputs

- **Folder del proyecto** (argumento o pregunta al usuario). Spec completo del
  manifest esperado: [`references/manifest.md`](references/manifest.md).
- Si el folder no matchea el manifest en absoluto (cero docs reconocibles),
  detente y dilo — no inventes un análisis sobre docs arbitrarios.

## Pipeline — 6 fases en orden estricto

### Fase 1 — Ingesta

1. Lee `references/manifest.md`. Lee todos los docs del folder en orden.
2. Registra: docs presentes, docs obligatorios faltantes (= gaps), archivos
   extra.
3. Aplica reglas de ingesta del manifest (incluido el hallazgo automático
   F-AUTO-1 si `00-tesis.md` no tiene falsificadores).
4. No emitas juicios todavía. Salida interna: mapa doc→segmento + lista de gaps.

### Fase 2 — Steelman

Reconstruye la MEJOR versión de la tesis en 1 párrafo: claim económico
(quién paga, por qué, cuánto) + claim de implementación (qué se construye,
cómo llega al cliente). Preséntala al usuario y confirma que es fiel.
No avances sin confirmación — no puedes atacar lo que no entendiste.

### Fase 3 — Interrogatorio

Selecciona 3-5 preguntas de [`references/question-bank.md`](references/question-bank.md)
según los huecos de la Fase 1. Una por turno. Sigue las reglas del banco
(una repregunta máx, "no sé" = gap honesto). Anexa las respuestas al contexto
de los críticos.

### Fase 4 — Stress adversarial

Cinco críticos, cada uno con su checklist:

| Crítico | Checklist |
|---|---|
| Inversionista escéptico | `references/critic-investor.md` |
| CFO frío | `references/critic-cfo.md` |
| CTO pragmático | `references/critic-cto.md` |
| Operador GTM | `references/critic-gtm.md` |
| Abogado regulatorio | `references/critic-regulatory.md` |

**Modo preferido — subagentes paralelos.** Si el harness tiene tool de
subagentes (Agent/Task), lanza los 5 en paralelo. Prompt de despacho por
crítico:

```
Eres [crítico] evaluando la viabilidad de un proyecto. Lee tu checklist en
[path al critic-*.md] y síguelo. Contexto completo:

[contenido de todos los docs del manifest]
[transcript del interrogatorio Fase 3]
[lista de gaps declarados]

Emite SOLO hallazgos en este formato exacto, priorizados por severidad:

- id: F-[INV|CFO|CTO|GTM|REG]-<n>
  segmento: Mercado|Finanzas|Técnico|Ejecución
  severidad: fatal|grave|menor
  hallazgo: <una oración>
  evidencia: <doc citado + cita breve>
  verificacion: verificado|contradicho|no-verificable|no-aplica (+ fuente web si aplica)
  resolucion: <qué evidencia concreta lo resolvería>

Severidad: fatal = mata el proyecto si no se resuelve; grave = rompe un
supuesto load-bearing; menor = fricción o riesgo acotado. Si un área está
bien soportada, dilo en una línea y no fabriques hallazgos. Máximo 2
verificaciones web (tu checklist dice cuáles priorizar).
```

**Modo fallback — personas secuenciales.** Sin tool de subagentes: ejecuta
los 5 críticos en este mismo contexto, en el orden de la tabla. Regla dura:
cada crítico emite su lista COMPLETA de hallazgos antes de que leas/proceses
los del siguiente. Prohibido suavizar un hallazgo por lo que dijo un crítico
anterior — la contaminación entre lentes invalida el gate.

### Fase 5 — Consenso

1. Junta los 5 reportes de hallazgos.
2. **Cruce adversarial:** identifica hallazgos que se contradicen entre
   críticos. Confróntalos explícitamente: ¿cuál tiene mejor evidencia?
   Se resuelve o se registra como "contradicción no resuelta" — nunca se
   promedia ni se esconde.
3. **Semáforo por segmento — reglas deterministas:**
   - 🔴 Rojo: ≥1 hallazgo `fatal` (verificado o no-verificable), o ≥3 `grave`.
   - 🟡 Amarillo: 1-2 `grave`, o acumulación de `menor` que toca el mismo
     supuesto.
   - 🟢 Verde: sin `fatal` ni `grave`.
   - Un `fatal` cuya verificación web resultó `contradicho` (el claim del
     crítico no se sostuvo) se degrada a `menor` y se anota.
4. **Confianza por segmento:** alta (docs completos + claims clave
   verificados); media (1 doc obligatorio faltante O claims clave
   no-verificables); baja (≥2 docs faltantes que alimentan el segmento).
   Gap declarado SIEMPRE capa la confianza — ver manifest.
5. **Veredicto global — reglas deterministas, sin excepciones:**
   - **GO** = 0 rojos y ≤3 amarillos.
   - **PIVOT** = 1-2 rojos con path de resolución identificado en sus
     hallazgos, O 0 rojos + 4 amarillos.
   - **NO-GO** = ≥1 fatal sin resolución identificable, o ≥3 rojos.

### Fase 6 — Síntesis

Escribe el reporte siguiendo [`references/report-template.md`](references/report-template.md)
en `<folder del proyecto>/veredicto-YYYY-MM-DD.md`. Nunca sobrescribas un
veredicto previo. Presenta al usuario: veredicto + tablero + los 3 hallazgos
más importantes + dónde quedó el reporte completo.

## Reglas de estilo (heredadas de roast-me)

- Severidad manda, no votos: un tanque de gasolina roto no se compensa con
  buenos asientos.
- Flag, don't fix: el gate señala, no rediseña el proyecto.
- Sin evidencia citada, el hallazgo no existe.
- Un GO limpio se dice con la misma franqueza que un NO-GO: falsos rojos
  queman la confianza en el gate.
- El veredicto computado no se negocia en la conversación. Si el usuario
  aporta evidencia nueva: docs actualizados + nueva corrida.
````

- [ ] **Step 2: Verify frontmatter and cross-references**

Run: `grep -c "references/" "C:\Proyectos\battle_tested_skills\viability-gate\SKILL.md"`
Expected: `>= 8` (all 8 reference files mentioned)

Run: `head -5 "C:\Proyectos\battle_tested_skills\viability-gate\SKILL.md"`
Expected: YAML frontmatter starting with `---` and `name: viability-gate`

---

### Task 10: Final verification pass

**Files:**
- Read: all files under `C:\Proyectos\battle_tested_skills\viability-gate\`
- Read: `C:\Obsidian\output\2026-07-22-viability-gate-design.md`

- [ ] **Step 1: Structural check — all 9 files exist**

Run: `ls "C:\Proyectos\battle_tested_skills\viability-gate" "C:\Proyectos\battle_tested_skills\viability-gate\references"`
Expected: `SKILL.md` + 8 files in `references/` (manifest, 5 critics, question-bank, report-template)

- [ ] **Step 2: Consistency check against design doc**

Verify each of these design decisions appears intact in the built skill:
1. Verdict rules: GO = 0 rojos ≤3 amarillos; PIVOT = 1-2 rojos con path O 4 amarillos; NO-GO = fatal sin resolución o 3+ rojos.
2. 4 segments (Mercado/Finanzas/Técnico/Ejecución), 5 critics, regulatory has no own segment.
3. Mandatory docs 00-05; 07-gtm optional; gaps cap confidence, never block.
4. Subagent-preferred / sequential-fallback with emit-before-read rule.
5. Max 2 web verifications per critic.
6. Report written to analyzed folder as `veredicto-YYYY-MM-DD.md`, never overwritten.

Any mismatch: fix the skill file (design doc is source of truth).

- [ ] **Step 3: Trigger-description sanity**

Confirm SKILL.md `description` contains: what it does, concrete trigger phrases (Spanish + English), and what it is NOT for. This is the only part loaded at session start — it must trigger correctly.

- [ ] **Step 4: Smoke-test instruction (manual, user-run)**

User validates later by running the skill against a real project folder (e.g. a Curatech-style doc set). Out of scope for this plan.
