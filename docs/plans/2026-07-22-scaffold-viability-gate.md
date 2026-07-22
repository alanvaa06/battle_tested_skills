# scaffold-viability-gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `scaffold-viability-gate` skill — runs in any folder and lays down the canonical viability-gate manifest structure (skeleton docs 00-07) so per-doc skills can develop the analysis and `viability-gate` can then run.

**Architecture:** SKILL.md orchestrator + `templates/` copy-out (same pattern as the existing `scaffold` skill). Audit-first idempotent: existing docs are never overwritten, only missing ones are copied, with `{{PROYECTO}}` token substitution. Templates are deliberately thin skeletons — section headers restating the manifest contract plus one HTML comment each; content intelligence belongs to future generator skills.

**Tech Stack:** Markdown only. Verification is structural (files exist, headers present, token count) plus consistency against `viability-gate/references/manifest.md` (source of truth for section headers).

**Note:** Repo `C:\Proyectos\battle_tested_skills` is a git repository (main). Commit after each task.

---

### Task 1: Templates 00-03 (tesis, identidad, cliente, mercado)

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates\00-tesis.md`
- Create: `C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates\01-identidad-producto.md`
- Create: `C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates\02-cliente-ideal.md`
- Create: `C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates\03-mercado.md`

- [ ] **Step 1: Write `templates/00-tesis.md`**

```markdown
# {{PROYECTO}} — Tesis

## La apuesta

<!-- ≤10 líneas: quién paga, por qué, cuánto, y qué se construye. -->

## Falsificadores

<!-- Condiciones concretas que matarían esta tesis. Sin esta sección llena,
el gate registra automáticamente "tesis no falsificable" (F-AUTO-1). -->
```

- [ ] **Step 2: Write `templates/01-identidad-producto.md`**

```markdown
# {{PROYECTO}} — Identidad de producto

## Problema

<!-- El dolor concreto y quién lo sufre. -->

## Propuesta de valor

<!-- Qué obtiene el cliente y por qué lo prefiere sobre su alternativa actual. -->

## Diferenciación

<!-- Qué defiende la posición: datos, canal, switching costs, regulación, marca. -->

## Por qué ahora

<!-- Qué cambió (tecnología, regulación, comportamiento) que lo hace posible hoy. -->
```

- [ ] **Step 3: Write `templates/02-cliente-ideal.md`**

```markdown
# {{PROYECTO}} — Cliente ideal

## ICP

<!-- Perfil concreto: giro, tamaño, rol del decisor y del pagador. -->

## Job-to-be-done

<!-- Qué tarea contrata el cliente a este producto para resolver. -->

## Disposición a pagar

<!-- Evidencia de gasto actual en resolver este problema, no deseo declarado. -->

## Cómo lo alcanzo

<!-- Dónde está el ICP y por qué canal se llega a él. -->
```

- [ ] **Step 4: Write `templates/03-mercado.md`**

```markdown
# {{PROYECTO}} — Mercado

## TAM / SAM / SOM

<!-- Con fuentes citadas. SOM: camina el cálculo bottom-up. -->

## Competidores

<!-- Nombres concretos. "No hay competencia" no existe. -->

## Alternativas actuales del cliente

<!-- Qué usa hoy el ICP para resolver esto (Excel, WhatsApp, contador, nada). -->
```

- [ ] **Step 5: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add scaffold-viability-gate && git commit -m "feat(scaffold-viability-gate): templates 00-03"
```

---

### Task 2: Templates 04-07 (finanzas, stack, ejecución, gtm)

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates\04-modelo-financiero.md`
- Create: `C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates\05-stack-arquitectura.md`
- Create: `C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates\06-plan-ejecucion.md`
- Create: `C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates\07-gtm.md`

- [ ] **Step 1: Write `templates/04-modelo-financiero.md`**

```markdown
# {{PROYECTO}} — Modelo financiero

<!-- Alternativa aceptada por el gate: un 04-modelo-financiero.xlsx en este
mismo folder sustituye a este .md. -->

## Pricing

<!-- Precio y su base: valor capturado, benchmark de competidor, o test real. -->

## Volumen proyectado

<!-- Descompuesto: prospectos × conversión × retención, con base de cada tasa. -->

## Unit economics

<!-- CAC (todo incluido), LTV (churn explícito), margen bruto. -->

## Costos de operación

<!-- Fijos y variables: subscripciones, infra, APIs, contador, herramientas. -->

## Breakeven y runway

<!-- Cuándo cruza cero y con qué caja se llega ahí. -->
```

- [ ] **Step 2: Write `templates/05-stack-arquitectura.md`**

```markdown
# {{PROYECTO}} — Stack y arquitectura

## Stack

<!-- Componentes y por qué cada uno. -->

## Subscripciones y costos de infra/APIs

<!-- Costo mensual al volumen proyectado y a 10×. -->

## Build vs buy

<!-- Qué se construye, qué se renta, y por qué. -->

## Límites de escala

<!-- Qué se rompe primero al crecer y qué dependencia externa es frágil. -->
```

- [ ] **Step 3: Write `templates/06-plan-ejecucion.md`**

```markdown
# {{PROYECTO}} — Plan de ejecución

## Scope del MVP

<!-- Qué entra y, más importante, qué NO entra. -->

## Ciclo de desarrollo y milestones

<!-- Fechas o ventanas, y cuál milestone es el más frágil. -->

## Quién construye / quién vende

<!-- Horas por semana de cada quién; si es la misma persona, dilo. -->
```

- [ ] **Step 4: Write `templates/07-gtm.md`**

```markdown
# {{PROYECTO}} — Go-to-market

<!-- Doc opcional para el gate: si no existe, GTM se estresa desde
02-cliente-ideal.md y 06-plan-ejecucion.md. -->

## Canales

<!-- Canal principal + alternativa, con evidencia de que el ICP compra ahí. -->

## Motion de venta

<!-- Self-service, venta directa, partner. Ciclo de venta estimado. -->

## Primeros 10 clientes

<!-- Path nombrado: red propia, lista concreta, canal caliente. -->
```

- [ ] **Step 5: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add scaffold-viability-gate && git commit -m "feat(scaffold-viability-gate): templates 04-07"
```

---

### Task 3: SKILL.md orchestrator

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\scaffold-viability-gate\SKILL.md`

- [ ] **Step 1: Write `SKILL.md`**

````markdown
---
name: scaffold-viability-gate
description: Lays down the canonical viability-gate manifest structure (skeleton docs 00-tesis through 07-gtm) in the current folder so the project's viability analysis can be developed doc by doc and then stress-tested with the viability-gate skill. Use when the user says "scaffold viability", "prepara la estructura del gate", "inicializa el manifest de viabilidad", or starts a new project folder that will be evaluated with viability-gate. Idempotent: never overwrites existing docs, only creates missing ones. Not for running the gate itself or generating doc content.
disable-model-invocation: true
metadata:
  version: 1.0
---

# Scaffold Viability Gate — estructura del manifest

Prepara un folder para el pipeline de viabilidad:

```
scaffold-viability-gate → [desarrollo de docs] → viability-gate → veredicto
```

Los templates son esqueletos a propósito: headers del contrato del manifest +
un comentario por sección. La inteligencia de contenido vive en las skills
generadoras (futuras) y en los checklists de los críticos del gate — no aquí.

Templates viven en `./templates/` junto a este SKILL.md (resolver relativo al
directorio de la skill). Son fuente: NO modificarlos; copiar de ellos.

## Pasos

1. **Resolver target y nombre.**
   - Target = cwd, salvo que el usuario nombre un subfolder en la invocación
     (crearlo si no existe).
   - Nombre del proyecto: tomarlo de la invocación o del nombre del folder;
     si ninguno es claro, preguntar UNA vez.

2. **Audit (leer antes de escribir).** Listar cuáles de los 8 docs del
   manifest ya existen en el target:
   `00-tesis.md`, `01-identidad-producto.md`, `02-cliente-ideal.md`,
   `03-mercado.md`, `04-modelo-financiero.md` (o `.xlsx`),
   `05-stack-arquitectura.md`, `06-plan-ejecucion.md`, `07-gtm.md`.

3. **Copiar solo faltantes.** Para cada doc ausente: copiar su template
   sustituyendo `{{PROYECTO}}` por el nombre del proyecto. Docs existentes
   NUNCA se tocan — ni para "mejorarlos". Si `04-modelo-financiero.xlsx`
   existe, no crear el `.md`.

4. **Reportar.** Tabla `doc | presente/creado`. Cerrar con próximos pasos:
   - Desarrollar cada doc (a mano o con skills dedicadas cuando existan —
     p.ej. modelo financiero, deep research para `03-mercado.md`).
   - `07-gtm.md` es opcional para el gate: puede borrarse sin penalización.
   - Al terminar los docs: correr `viability-gate` apuntando a este folder.

## Reglas

- Idempotente: correr sobre un folder ya scaffoldeado = no-op reportado, cero
  cambios.
- No generar contenido de análisis, no llenar secciones, no opinar sobre el
  proyecto — eso es trabajo de las skills generadoras y del gate.
- Fuente de verdad de los headers: `viability-gate/references/manifest.md`
  ("contenido mínimo"). Si el manifest cambió y estos templates no, señalar
  el drift al usuario en vez de improvisar.
````

- [ ] **Step 2: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add scaffold-viability-gate && git commit -m "feat(scaffold-viability-gate): SKILL.md orchestrator"
```

---

### Task 4: Verification + install

- [ ] **Step 1: Structural check**

Run: `ls "C:\Proyectos\battle_tested_skills\scaffold-viability-gate" "C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates"`
Expected: `SKILL.md` + `templates/` with exactly 8 files (00-07).

Run: `grep -rc "{{PROYECTO}}" "C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates" | grep -c ":0$"`
Expected: `0` (every template contains the token at least once).

- [ ] **Step 2: Consistency vs manifest**

Compare each template's `## ` headers against the "contenido mínimo" column of `viability-gate/references/manifest.md`. Every minimum-content item must map to a header. Mismatch: fix the template (manifest is source of truth).

- [ ] **Step 3: Falsifier guard present**

Run: `grep -c "## Falsificadores" "C:\Proyectos\battle_tested_skills\scaffold-viability-gate\templates\00-tesis.md"`
Expected: `1`

- [ ] **Step 4: Install globally via junction (same pattern as viability-gate)**

PowerShell: `New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\scaffold-viability-gate" -Target "C:\Proyectos\battle_tested_skills\scaffold-viability-gate"`
Expected: junction created; skill discoverable.

- [ ] **Step 5: Smoke test in scratchpad**

Create an empty folder in the session scratchpad, follow the SKILL.md steps against it with project name "demo": expect 8 files created, `{{PROYECTO}}` replaced by "demo", second run reports 8 × `presente` and changes nothing. Delete the demo folder afterwards.
