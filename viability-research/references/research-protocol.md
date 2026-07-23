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
