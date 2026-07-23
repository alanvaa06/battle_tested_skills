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
