# Guía de entrevista — viability-intake

Una pregunta por turno. Repregunta única si la respuesta no cumple el criterio
de suficiencia; después se registra tal cual (la debilidad es señal para el
gate, no problema tuyo). "No sé" → escribir en la sección:
`> Gap declarado: <tema> — sin respuesta del founder.`

Cero preguntas adversariales: extraer, no atacar. Si una pregunta parece
roast, pertenece al question-bank del gate, no aquí. No sugieras respuestas
al founder; no rellenes con conocimiento propio.

Orden de bloques: 00 → 01 → 02 → 06 → 07 → hipótesis (04/05).

## Cosecha de recursos (si hay recursos extra)

- Por sección pendiente, busca en los recursos una respuesta candidata que
  cumpla el criterio de suficiencia de esa sección. Si no lo cumple, la
  sección se pregunta normal — no bajes el estándar por tener fuente.
- Presenta candidatos por doc, en bloque: `sección → contenido propuesto →
  fuente`. El founder confirma, corrige o rechaza cada uno.
- Jerarquía de evidencia: código de prototipo (lo que EXISTE) > docs de
  research previo > notas sueltas > memoria del founder.
- Nunca mezcles cosecha con invención: si el recurso no lo dice, no es
  candidato.

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
