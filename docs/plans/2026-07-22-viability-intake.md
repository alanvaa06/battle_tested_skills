# viability-intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `viability-intake` skill — structured founder interview that fills the manifest docs that live only in the founder's head (00, 01, 02, 06, 07) plus seeded hypotheses in 04/05, leaving 03-mercado untouched for research.

**Architecture:** SKILL.md orchestrator + `references/interview-guide.md` (question blocks per doc section with sufficiency criteria). State lives in the docs themselves: a section whose body is only the template's HTML comment is pending; filled sections are never rewritten. Each doc is written when its block completes, so an interrupted interview loses nothing.

**Tech Stack:** Markdown only. Verification is structural plus consistency with `scaffold-viability-gate/templates/` headers (the contract) and the design doc at `C:\Obsidian\output\2026-07-22-viability-intake-design.md`.

**Note:** Repo `C:\Proyectos\battle_tested_skills` is git (main). Commit at the end of each task.

---

### Task 1: `references/interview-guide.md`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-intake\references\interview-guide.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Guía de entrevista — viability-intake

Una pregunta por turno. Repregunta única si la respuesta no cumple el criterio
de suficiencia; después se registra tal cual (la debilidad es señal para el
gate, no problema tuyo). "No sé" → escribir en la sección:
`> Gap declarado: <tema> — sin respuesta del founder.`

Cero preguntas adversariales: extraer, no atacar. Si una pregunta parece
roast, pertenece al question-bank del gate, no aquí. No sugieras respuestas
al founder; no rellenes con conocimiento propio.

Orden de bloques: 00 → 01 → 02 → 06 → 07 → hipótesis (04/05).

## Bloque 00 — Tesis

### La apuesta
- "Cuéntame la apuesta en una frase: ¿quién paga, cuánto, y a cambio de qué?"
- "¿Qué se construye exactamente para capturar ese pago?"
- Suficiencia: cliente identificable + monto o rango + mecanismo de cobro.

### Falsificadores (obligatorio — el gate castiga su ausencia con F-AUTO-1)
- "¿Qué evidencia concreta, en los próximos 90 días, te haría abandonar esto?"
- "¿Qué número (ventas, conversión, churn, costo) marcaría fracaso, y en qué
  plazo?"
- Suficiencia: ≥2 condiciones, cada una con métrica y plazo.

## Bloque 01 — Identidad de producto

### Problema
- "¿Cuál es el dolor concreto y quién lo sufre? Dame un caso real que hayas
  visto tú."
- Suficiencia: rol/persona + situación concreta observada.

### Propuesta de valor
- "¿Qué obtiene el cliente, medido en qué: tiempo, dinero, riesgo evitado?"
- Suficiencia: beneficio en unidad medible, no adjetivos.

### Diferenciación
- "¿Qué tienes tú que un competidor con más dinero no replica en 6 meses?"
- Suficiencia: activo nombrado (datos, canal, relación, licencia, dominio).

### Por qué ahora
- "¿Qué cambió recientemente — tecnología, regulación, comportamiento — que
  hace esto viable hoy y no hace 3 años?"
- Suficiencia: cambio específico y fechable; "AI existe" no basta.

## Bloque 02 — Cliente ideal

### ICP
- "Describe al comprador: giro, tamaño, quién decide y quién paga."
- Suficiencia: los cuatro campos presentes.

### Job-to-be-done
- "¿Qué tarea le contrata el cliente al producto, y cómo la resuelve hoy?"
- Suficiencia: tarea + método actual (aunque sea 'nada').

### Disposición a pagar
- "¿Cuánto gasta hoy el ICP en resolver esto — dinero u horas? ¿Cómo lo
  sabes?"
- Suficiencia: cifra + origen del dato (entrevista, experiencia propia,
  observación; se registra el origen tal cual).

### Cómo lo alcanzo
- "¿Dónde se junta tu ICP (físico o digital) y cómo entras tú ahí?"
- Suficiencia: lugar/canal concreto + mecanismo de entrada.

## Bloque 06 — Plan de ejecución

### Scope del MVP
- "¿Qué hace la v1? Ahora lo difícil: ¿qué NO hace aunque duela dejarlo
  fuera?"
- Suficiencia: lista de dentro + lista de fuera, ambas no vacías.

### Ciclo de desarrollo y milestones
- "Dame los milestones con ventana de fecha. ¿Cuál es el más frágil y por
  qué?"
- Suficiencia: ≥3 milestones fechados + frágil identificado.

### Quién construye / quién vende
- "Horas por semana de cada quién: construir y vender. Si eres tú en ambos,
  ¿cómo se reparte la semana?"
- Suficiencia: números, no roles abstractos.

## Bloque 07 — Go-to-market

### Canales
- "¿Canal principal y canal alternativo? ¿Qué evidencia hay de que el ICP
  compra ahí?"
- Suficiencia: 2 canales; evidencia o hipótesis declarada como tal.

### Motion de venta
- "¿Self-service, venta directa, o partner? ¿Ciclo de venta estimado en
  semanas?"
- Suficiencia: motion + estimado numérico.

### Primeros 10 clientes
- "Nombra —o describe con precisión— a los primeros 10 y el camino a cada
  uno."
- Suficiencia: ≥5 identificables individualmente (nombre, empresa, o
  descripción inequívoca).

## Bloque hipótesis — siembra en 04 y 05

Formular explícitamente como hipótesis de trabajo, no compromiso. Escribir
SOLO si la sección destino está vacía (solo comentario del template).

### Pricing tentativo → `04-modelo-financiero.md` sección `## Pricing`
- "Como hipótesis de trabajo: ¿modelo de cobro (suscripción, uso, comisión) y
  precio tentativo? ¿En qué lo anclas?"
- Escribir con marcador: `<!-- hipótesis intake, pendiente de validar -->`

### Stack tentativo → `05-stack-arquitectura.md` sección `## Stack`
- "¿Stack tentativo? ¿Qué parte ya dominas y cuál sería nueva para ti?"
- Escribir con marcador: `<!-- hipótesis intake, pendiente de validar -->`
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^### " "C:\Proyectos\battle_tested_skills\viability-intake\references\interview-guide.md"`
Expected: `18` (16 doc sections + 2 hypothesis sections)

Run: `grep -c "Suficiencia:" "C:\Proyectos\battle_tested_skills\viability-intake\references\interview-guide.md"`
Expected: `16`

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-intake && git commit -m "feat(viability-intake): interview guide"
```

---

### Task 2: `SKILL.md`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-intake\SKILL.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
---
name: viability-intake
description: Structured founder interview that fills the viability manifest docs that only live in the founder's head — 00-tesis (with falsifiers), 01-identidad-producto, 02-cliente-ideal, 06-plan-ejecucion, 07-gtm — plus tentative pricing/stack hypotheses seeded into 04/05. Use when the user says "entrevístame para el gate", "llena los docs de viabilidad", "viability intake", "intake de [proyecto]", or has just scaffolded a viability folder and wants to develop the docs. Resumable: only interviews empty sections, never rewrites filled ones. Faithful capture, not adversarial — stress-testing is viability-gate's job. Never touches 03-mercado (research territory). Not for running the gate or doing market research.
metadata:
  version: 1.0
---

# viability-intake — Entrevista de founder

Extraes lo que vive en la cabeza del founder y lo escribes en los docs del
manifest. Captura fiel: sin roast, sin juicios, sin sugerir respuestas. El
stress adversarial es trabajo de `viability-gate` — si los docs llegan
pre-negociados, el gate pierde señal.

Guía de preguntas y criterios: [`references/interview-guide.md`](references/interview-guide.md).
Idioma: el del usuario (default español).

## Docs que te tocan

| Doc | Alcance |
|---|---|
| `00-tesis.md` | Completo (falsificadores obligatorios) |
| `01-identidad-producto.md` | Completo |
| `02-cliente-ideal.md` | Completo |
| `06-plan-ejecucion.md` | Completo |
| `07-gtm.md` | Completo |
| `04-modelo-financiero.md` | SOLO sección `## Pricing`, como hipótesis marcada |
| `05-stack-arquitectura.md` | SOLO sección `## Stack`, como hipótesis marcada |
| `03-mercado.md` | JAMÁS — territorio de research |

## Pasos

1. **Target y prerequisito.** Target = cwd o folder nombrado. Si faltan los
   esqueletos de tus docs: ofrece correr `scaffold-viability-gate` y detente
   hasta que exista la estructura. No crees esqueletos tú.

2. **Audit por sección.** Una sección está PENDIENTE si su cuerpo es solo el
   comentario HTML del template, o está vacío. Cualquier otro contenido =
   respondida, se salta. Reporta el mapa de pendientes antes de empezar.
   Si todo está lleno: dilo y termina — no-op.

3. **Entrevista.** Bloques en orden `00 → 01 → 02 → 06 → 07`, solo secciones
   pendientes. Reglas duras:
   - UNA pregunta por turno. Espera respuesta.
   - Respuesta que no cumple el criterio de suficiencia de la guía: UNA
     repregunta de concreción (¿quién, cuánto, cuándo?). Después registra
     tal cual — la debilidad es señal para el gate.
   - "No sé" → escribe `> Gap declarado: <tema> — sin respuesta del founder.`
   - Registra las palabras del founder (limpias de muletillas), no tu
     paráfrasis interpretada. Números y nombres van verbatim.

4. **Escritura por doc.** Al cerrar el bloque de un doc, escríbelo:
   - Reemplaza los comentarios HTML por el contenido.
   - Conserva los headers EXACTOS del template — son el contrato con el gate.
   - Secciones ya llenas NUNCA se reescriben. Re-entrevistar una sección =
     el usuario la borra a mano y re-corre la skill.

5. **Hipótesis (al final).** Si las secciones destino están vacías: escribe
   pricing tentativo en `04 ## Pricing` y stack tentativo en `05 ## Stack`,
   cada una con `<!-- hipótesis intake, pendiente de validar -->`. Si tienen
   contenido, no las toques.

6. **Cierre.** Tabla `doc | completo / parcial / gaps declarados` + próximos
   pasos: research para `03-mercado.md`, modelo financiero para `04`, y al
   terminar todo: correr `viability-gate`.
````

- [ ] **Step 2: Verify frontmatter and cross-reference**

Run: `head -3 "C:\Proyectos\battle_tested_skills\viability-intake\SKILL.md"`
Expected: frontmatter with `name: viability-intake`

Run: `grep -c "interview-guide.md" "C:\Proyectos\battle_tested_skills\viability-intake\SKILL.md"`
Expected: `>= 1`

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-intake && git commit -m "feat(viability-intake): SKILL.md orchestrator"
```

---

### Task 3: Verification + install

- [ ] **Step 1: Structural check**

Run: `ls "C:\Proyectos\battle_tested_skills\viability-intake" "C:\Proyectos\battle_tested_skills\viability-intake\references"`
Expected: `SKILL.md`, `references/` with `interview-guide.md`.

- [ ] **Step 2: Contract check vs scaffold templates**

Every section header the guide interviews for must exist verbatim in `scaffold-viability-gate/templates/`: La apuesta, Falsificadores (00); Problema, Propuesta de valor, Diferenciación, Por qué ahora (01); ICP, Job-to-be-done, Disposición a pagar, Cómo lo alcanzo (02); Scope del MVP, Ciclo de desarrollo y milestones, Quién construye / quién vende (06); Canales, Motion de venta, Primeros 10 clientes (07); Pricing (04); Stack (05). Mismatch = fix the guide (templates are the contract).

- [ ] **Step 3: Design-doc consistency**

Check against `C:\Obsidian\output\2026-07-22-viability-intake-design.md`: no adversarial questions in the guide; 03-mercado never mentioned as writable; hypotheses only into empty sections; docs-as-state audit rule present in SKILL.md.

- [ ] **Step 4: Install globally via junction**

PowerShell: `New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\viability-intake" -Target "C:\Proyectos\battle_tested_skills\viability-intake"`
Expected: junction created.

- [ ] **Step 5: Smoke test (structural only — interview is interactive)**

In scratchpad: scaffold a demo folder (copy templates with token replaced), then verify the audit rule mechanically: every section body in the fresh skeletons consists only of an HTML comment → all sections classify as PENDIENTE; add one line of real text under `## ICP` in `02-cliente-ideal.md` → that section classifies as respondida. Delete demo folder. The full interactive flow is validated later by dogfooding on a real project.
