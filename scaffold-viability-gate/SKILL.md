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
