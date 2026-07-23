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
