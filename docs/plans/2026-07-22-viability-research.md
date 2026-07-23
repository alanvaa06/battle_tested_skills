# viability-research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `viability-research` skill — derives a research plan from the founder docs (00/01/02), gets human approval, runs verified deep research through an engine cascade, and writes `03-mercado.md` with dual TAM, cited competitors, alternatives, and a local reality check.

**Architecture:** SKILL.md orchestrator + `references/research-protocol.md` (dual TAM method, Porter-lite, reality-check checklist, source rules). Engine cascade by detection: `/deep-research` (Claude Code CLI builtin) → own fan-out with Agent tool → sequential WebSearch/WebFetch (Cowork's main path). Verification lives in the skill, not only the delegated engine.

**Tech Stack:** Markdown only. Verification: structural checks + header contract vs `scaffold-viability-gate/templates/03-mercado.md` + design doc at `C:\Obsidian\output\2026-07-22-viability-research-design.md`.

**Note:** Repo is git (main). Commit per task.

---

### Task 1: `references/research-protocol.md`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-research\references\research-protocol.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
# Protocolo de research — viability-research

## Método TAM dual (obligatorio, base CFA industry analysis)

**Top-down:** mercado total citado (fuente con metodología identificable) →
segmento relevante al ICP → share alcanzable. Cadena explícita:
`mercado macro × recorte de segmento × share alcanzable`, cada factor con
fuente o supuesto declarado.

**Bottom-up:** `# clientes alcanzables en el canal declarado (02/07) ×
pricing hipótesis (04)`. Si no hay pricing hipótesis en `04`, usar el rango
de pricing de competidores encontrado y declararlo.

**Reconciliación:** divergencia >3× entre vías = NO promediar. Declararla en
el doc con hipótesis de la causa (mismo umbral que usa el crítico
inversionista del gate — el doc llega pre-reconciliado o con la divergencia
explícita).

## Porter-lite — scan competitivo en 5 preguntas

1. **Entrada:** ¿qué tan barato es entrar a este mercado? ¿Quién entró en los
   últimos 24 meses?
2. **Proveedores:** ¿dependencia de plataforma o insumo concentrado (Meta/
   WhatsApp, un API, un distribuidor)?
3. **Compradores:** ¿ICP concentrado o fragmentado? ¿Costo de switching real?
4. **Sustitutos:** ¿qué usa hoy el ICP — status quo, Excel, WhatsApp, un
   humano, nada? (Esto alimenta la sección Alternativas.)
5. **Rivalidad:** competidores directos NOMBRADOS + pricing público +
   posicionamiento de cada uno.

## Checklist reality-check local

- **Pago:** método dominante del ICP (tarjeta/SPEI/OXXO/efectivo/anticipo) y
  qué implica para cobrar de forma recurrente.
- **Canal:** dónde descubre y compra software/servicios el ICP realmente
  (no dónde debería).
- **Regulación:** del giro del CLIENTE y del producto — ¿fricción (trámite,
  licencia, costo) o moat (quien la resuelve gana)? Nombrar el instrumento
  concreto (ley, NOM, registro).
- **Infra local:** conectividad, dispositivos, WhatsApp-first, madurez
  digital del ICP.

## Reglas de fuentes

- Toda cifra lleva fuente + fecha visible: `(Fuente, año — metodología si
  aplica)` o link.
- Cifra load-bearing (TAM, pricing de competidor, tamaño de segmento):
  **2 fuentes independientes o etiqueta `no-verificable`**.
- Independencia: dos fuentes citando el mismo reporte original = UNA fuente.
- Jerarquía: dato oficial (INEGI, censos, regulador) > reporte con
  metodología > consultora sin metodología > blog/nota de prensa.
- Antigüedad: preferir <24 meses; dato más viejo se usa con su año visible.
- Etiquetas de verificación (taxonomía compartida con el gate):
  `verificado` / `contradicho` / `no-verificable`.
- Adversarial contra FUENTES (¿quién lo dice, cómo lo midió, quién lo
  contradice?), nunca contra el founder.

## Escritura de `03-mercado.md`

Headers exactos del template del scaffold + una sección nueva al final:

```
## TAM / SAM / SOM        ← dual: top-down + bottom-up + reconciliación
## Competidores           ← Porter-lite, nombres + pricing citado
## Alternativas actuales del cliente   ← sustitutos/status quo del ICP
## Reality check local    ← checklist de arriba, solo hallazgos con evidencia
```

Al final del doc, una línea de trazabilidad:
`> Research corrido con motor: [deep-research | fan-out subagentes |
secuencial] — YYYY-MM-DD.`
````

- [ ] **Step 2: Verify structure**

Run: `grep -c "^## " "C:\Proyectos\battle_tested_skills\viability-research\references\research-protocol.md"`
Expected: `5` (TAM dual, Porter-lite, reality-check, fuentes, escritura)

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-research && git commit -m "feat(viability-research): research protocol"
```

---

### Task 2: `SKILL.md`

**Files:**
- Create: `C:\Proyectos\battle_tested_skills\viability-research\SKILL.md`

- [ ] **Step 1: Write the file with this exact content**

````markdown
---
name: viability-research
description: Verified market deep-research generator for the viability pipeline — derives a research plan from the founder docs (00-tesis, 01-identidad, 02-cliente-ideal), gets human approval, runs it through the best available engine (/deep-research skill, subagent fan-out, or sequential web search), and writes 03-mercado.md with dual top-down/bottom-up TAM, named competitors with cited pricing, customer alternatives, and a local reality check (payments, channel, regulation). Use when the user says "investiga el mercado", "corre el research de mercado", "llena 03-mercado", "viability research", or has completed intake and needs the market doc. Every load-bearing number needs 2 independent sources or gets tagged no-verificable. Only writes 03-mercado.md. Not for stress-testing (gate's job), founder interviews (intake's job), or generic industry reports.
metadata:
  version: 1.0
---

# viability-research — Research de mercado verificado

Llenas `03-mercado.md` con evidencia citada, no con prosa plausible. Reglas
de método: [`references/research-protocol.md`](references/research-protocol.md).
Adversarial contra fuentes, nunca contra el founder. Idioma: el del usuario
(default español).

## Contrato

- **Lees:** `00-tesis.md`, `01-identidad-producto.md`, `02-cliente-ideal.md`,
  `07-gtm.md` (si existe) y la hipótesis de pricing de `04-modelo-financiero.md`.
- **Escribes:** SOLO `03-mercado.md`. Si el research contradice la hipótesis
  de pricing de `04`, lo señalas en el cierre — no editas `04`.

## Pasos

1. **Prerequisito.** `00/01/02` deben tener contenido real (intake corrido).
   Vacíos → detente y sugiere `viability-intake`. `03-mercado.md` ya con
   contenido → no-op, salvo que el usuario pida re-corrida explícita (entonces
   el doc anterior se renombra a `03-mercado-YYYY-MM-DD.bak.md`, nunca se
   pisa).

2. **Plan de research.** Deriva 5-8 preguntas concretas desde tesis + ICP.
   Cubre siempre: TAM top-down, SOM bottom-up, competidores directos +
   pricing, alternativas/status quo del ICP, fricciones locales (pago/canal),
   regulación del giro. Preguntas específicas al proyecto, no genéricas.

3. **Checkpoint humano.** Presenta el plan (las preguntas + qué motor vas a
   usar) y ESPERA aprobación o ajuste antes de ejecutar. No quemes tokens de
   research sin el OK.

4. **Motor — cascada por detección:**
   - ¿Skill `/deep-research` disponible en el harness? → delégale el plan
     completo como argumento y recibe el reporte citado.
   - Si no, ¿hay tool de subagentes (Agent/Task)? → fan-out propio: 1
     subagente por pregunta + 1 verificador que cruza las cifras load-bearing
     contra segundas fuentes.
   - Si no → secuencial con WebSearch/WebFetch, pregunta por pregunta,
     verificación cruzada incluida.
   - El motor usado se declara en la línea de trazabilidad del doc.

5. **Verificación.** Aplica las reglas de fuentes del protocol a TODO número
   que sostenga una conclusión: 2 fuentes independientes o `no-verificable`.
   Etiquetas: `verificado / contradicho / no-verificable`.

6. **Escritura.** `03-mercado.md` con los headers exactos del template +
   `## Reality check local` al final (ver protocol). Toda cifra con fuente y
   fecha. TAM dual con reconciliación o divergencia declarada.

7. **Cierre.** Presenta: hallazgos clave (3-5), contradicciones con docs
   existentes (ej. pricing hipótesis de `04` vs pricing real de competidores),
   cifras que quedaron `no-verificable`, y próximo paso: modelo financiero
   (`04`) → gate.

## Reglas duras

- Sin fuente citada, la cifra no entra al doc.
- No rellenes con conocimiento propio del modelo sin marcarlo: dato sin
  búsqueda = `(conocimiento base del modelo, verificar)` — úsalo solo como
  último recurso.
- El plan aprobado es el alcance: no expandas el research sin avisar.
- Headers del template son contrato con el gate — no los renombres.
````

- [ ] **Step 2: Verify frontmatter and cross-reference**

Run: `head -3 "C:\Proyectos\battle_tested_skills\viability-research\SKILL.md"`
Expected: frontmatter with `name: viability-research`

Run: `grep -c "research-protocol.md" "C:\Proyectos\battle_tested_skills\viability-research\SKILL.md"`
Expected: `>= 1`

- [ ] **Step 3: Commit**

```bash
cd /c/Proyectos/battle_tested_skills && git add viability-research && git commit -m "feat(viability-research): SKILL.md orchestrator"
```

---

### Task 3: Verification + install

- [ ] **Step 1: Structural check**

Run: `ls "C:\Proyectos\battle_tested_skills\viability-research" "C:\Proyectos\battle_tested_skills\viability-research\references"`
Expected: `SKILL.md` + `references/research-protocol.md`.

- [ ] **Step 2: Header contract check**

The three template headers referenced in the protocol's escritura section must match `scaffold-viability-gate/templates/03-mercado.md` verbatim: `TAM / SAM / SOM`, `Competidores`, `Alternativas actuales del cliente`. `Reality check local` is new (additive — allowed). Mismatch = fix protocol.

- [ ] **Step 3: Design-doc consistency**

Check against `C:\Obsidian\output\2026-07-22-viability-research-design.md`: engine cascade order (deep-research → subagents → sequential); human checkpoint BEFORE engine; dual TAM with >3× divergence rule; 2-source rule; only writes 03; pricing contradiction reported not edited; traceability line present.

- [ ] **Step 4: Install globally via junction**

PowerShell: `New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\viability-research" -Target "C:\Proyectos\battle_tested_skills\viability-research"`
Expected: junction created.

- [ ] **Step 5: Full-pipeline dogfood note (user-run, out of scope)**

Real validation = run scaffold → intake → research on a live project folder. The engine cascade's Cowork path (no deep-research, no Agent tool) is validated the first time the skill runs inside Cowork.
