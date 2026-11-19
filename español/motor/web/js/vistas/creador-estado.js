// Contrato de estados del Taller (misma semántica que la web / guidedState).
// Carril técnico: estado · qué falta · qué revisar · siguiente paso (una CTA).
// Ciclo de producto: Borrador → En equipo → En proyecto → Mercado.

export const NUCLEO = ["sistema.json", "README.md", "SISTEMA.md", "MEMORIAS.md", "LIMITES.md", "PERMISOS.md"];
const NUCLEO_SET = new Set(NUCLEO);

const ETIQUETAS = {
  sin_sistema: "Sin sistema",
  proponiendo: "uxyn trabajando",
  por_revisar: "Por revisar",
  falta_nucleo: "Falta el núcleo",
  ajustar: "Ajustar",
  listo: "Listo",
};

/** Pasos visibles del ciclo de vida (carril de producto). */
export const CICLO = [
  { id: "borrador", etiqueta: "Borrador" },
  { id: "equipo", etiqueta: "En equipo" },
  { id: "proyecto", etiqueta: "En proyecto" },
  { id: "mercado", etiqueta: "Mercado" },
];

const PROMPT_MARCADORES =
  "Completa los archivos núcleo (SISTEMA.md, LIMITES.md, PERMISOS.md, MEMORIAS.md, README.md y sistema.json): "
  + "sustituye todos los marcadores {{…}} y déjalo en «Por revisar». "
  + "En sistema.json, permisos.acciones.agente y solo_persona son listas de «scripts/….py [subcomando]» (o []); sin texto libre.";

const ORIGEN_IDEA_MAX = 160;

/**
 * Prompt para «Que uxyn complete»: si ya no hay marcadores pero sí errores
 * (p. ej. permisos.acciones), pide corregir esos errores concretos.
 * @param {{ errores?: string[], marcadores?: object[], siguiente?: string|null }} entrada
 */
/**
 * Misma regla en Inicio y Taller a partir de `/api/catalogo/pendientes`.
 * @param {{ listo?: boolean, errores?: string[], marcadores?: object[] }|null|undefined} p
 * @returns {{ errores: string[], marcadores: object[], siguiente: string|null, listo: boolean|null, valido: boolean|null }}
 */
export function desdePendientes(p) {
  if (!p) {
    return { errores: [], marcadores: [], siguiente: null, listo: null, valido: null };
  }
  const errores = p.errores || [];
  const marcadores = p.marcadores || [];
  const listo = !!p.listo;
  // Sin errores ni marcadores → válido; si los hay, coincide con listo (normalmente false).
  const valido = !errores.length && !marcadores.length ? true : listo;
  return {
    errores,
    marcadores,
    siguiente: p.siguiente || null,
    listo,
    valido,
  };
}

export function armarPromptCompletar(entrada = {}) {
  const errores = entrada.errores || [];
  const marcadores = entrada.marcadores || [];
  const siguiente = (entrada.siguiente || "").trim();
  const hayMarcadoresNucleo = marcadores.some((m) => NUCLEO_SET.has(m.archivo || m.file));
  if (hayMarcadoresNucleo || marcadores.length) return PROMPT_MARCADORES;
  if (errores.length) {
    const lista = errores.slice(0, 6).map((e) => `- ${e}`).join("\n");
    return (
      "Corrige estos errores de validación del núcleo y deja la propuesta en «Por revisar»:\n"
      + `${lista}\n\n`
      + "En sistema.json, permisos.acciones.agente y solo_persona son listas de «scripts/….py [subcomando]» (o []). "
      + "El texto libre va en LIMITES.md o en «Por qué» de PERMISOS.md."
    );
  }
  if (siguiente) {
    return (
      `Siguiente paso del validador: ${siguiente}. `
      + "Propón los cambios en los archivos que falten y déjalos en «Por revisar». "
      + "Si tocas permisos.acciones, usa solo «scripts/….py [subcomando]» o []."
    );
  }
  return PROMPT_MARCADORES;
}

function huecoNucleo({ errores = [], marcadores = [] }) {
  const m = marcadores.find((x) => NUCLEO_SET.has(x.archivo || x.file));
  if (m) return { archivo: m.archivo || m.file, texto: m.texto || m.text || m.marcador || m.marker };
  const err = errores.find((e) => NUCLEO.some((f) => String(e).includes(f))
    || /marcador|núcleo|nucleo|SISTEMA|LIMITES|PERMISOS|MEMORIAS|README|sistema\.json/i.test(String(e)));
  if (err) return { archivo: null, texto: String(err) };
  if (marcadores.length) {
    const x = marcadores[0];
    return { archivo: x.archivo || x.file, texto: x.texto || x.text || x.marcador || x.marker };
  }
  if (errores.length) return { archivo: null, texto: String(errores[0]) };
  return null;
}

/**
 * Normaliza el origen (idea + adjuntos) para la franja del taller.
 * @param {{ idea?: string, adjuntos?: string[]| { nombre?: string }[] }} entrada
 * @returns {{ idea: string|null, adjuntos: string[], vacio: boolean, resumen: string }}
 */
export function resumenOrigen(entrada = {}) {
  const ideaBruta = String(entrada.idea || "").trim();
  const idea = ideaBruta
    ? (ideaBruta.length > ORIGEN_IDEA_MAX ? `${ideaBruta.slice(0, ORIGEN_IDEA_MAX - 1)}…` : ideaBruta)
    : null;
  const adjuntos = (entrada.adjuntos || [])
    .map((a) => (typeof a === "string" ? a : (a?.nombre || "")).trim())
    .filter(Boolean);
  const vacio = !idea && !adjuntos.length;
  let resumen = "Sin origen aún: empieza con una idea, un zip o archivos.";
  if (!vacio) {
    const partes = [];
    if (idea) partes.push(idea);
    if (adjuntos.length) {
      const nombres = adjuntos.slice(0, 4).join(", ") + (adjuntos.length > 4 ? "…" : "");
      partes.push(adjuntos.length === 1 ? `1 adjunto (${nombres})` : `${adjuntos.length} adjuntos (${nombres})`);
    }
    resumen = partes.join(" · ");
  }
  return { idea, adjuntos, vacio, resumen };
}

/**
 * Resuelve en qué paso del ciclo de producto está el sistema.
 * @param {{ tieneSistema?: boolean, enEquipo?: boolean, enProyecto?: string[], publicado?: boolean }} entrada
 * @returns {{ id: string, etiqueta: string, pasos: { id: string, etiqueta: string, activo: boolean, hecho: boolean }[], siguienteCiclo: string|null }}
 */
export function resolverCiclo(entrada = {}) {
  const enProyecto = Array.isArray(entrada.enProyecto) ? entrada.enProyecto.filter(Boolean) : [];
  const enEquipo = !!entrada.enEquipo || enProyecto.length > 0;
  const publicado = !!entrada.publicado;
  let id = "borrador";
  if (publicado) id = "mercado";
  else if (enProyecto.length) id = "proyecto";
  else if (enEquipo) id = "equipo";
  else if (entrada.tieneSistema) id = "borrador";

  const orden = CICLO.map((p) => p.id);
  const idx = orden.indexOf(id);
  const pasos = CICLO.map((p, i) => ({
    ...p,
    activo: p.id === id,
    hecho: i < idx,
  }));

  const siguienteCiclo = id === "borrador" ? "Guárdalo en este equipo o tráelo desde la web."
    : id === "equipo" ? "Instálalo en un proyecto registrado."
      : id === "proyecto" ? "Cuando esté listo, publícalo en el Mercado."
        : null;

  return { id, etiqueta: CICLO.find((p) => p.id === id)?.etiqueta || "Borrador", pasos, siguienteCiclo, enEquipo, enProyecto, publicado };
}

/**
 * @param {{ tieneSistema: boolean, proponiendo?: boolean, propuestas?: number,
 *   valido?: boolean|null, listo?: boolean|null, alDia?: boolean|null,
 *   errores?: string[], marcadores?: object[], siguiente?: string|null,
 *   enEquipo?: boolean, enProyecto?: string[], publicado?: boolean,
 *   origen?: { idea?: string, adjuntos?: string[]|object[] } }} entrada
 */
export function resolverEstado(entrada) {
  const origen = resumenOrigen(entrada.origen || {});
  const ciclo = resolverCiclo({
    tieneSistema: !!entrada.tieneSistema,
    enEquipo: entrada.enEquipo,
    enProyecto: entrada.enProyecto,
    publicado: entrada.publicado,
  });
  const base = {
    enEquipo: ciclo.enEquipo,
    enProyecto: ciclo.enProyecto,
    publicado: ciclo.publicado,
    origen,
    ciclo,
  };

  if (!entrada.tieneSistema) {
    return {
      id: "sin_sistema",
      etiqueta: ETIQUETAS.sin_sistema,
      detalle: "Cuenta tu idea o adjunta archivos/zip. uxyn arma el núcleo; tú aceptas los cambios.",
      revisar: null,
      cta: "Crear con uxyn",
      accion: "crear",
      archivo: null,
      ...base,
    };
  }
  if (entrada.proponiendo) {
    return {
      id: "proponiendo",
      etiqueta: ETIQUETAS.proponiendo,
      detalle: "Creando o ajustando el sistema a partir de tu idea y el núcleo.",
      revisar: null,
      cta: null,
      accion: "ninguna",
      archivo: null,
      ...base,
    };
  }
  const n = entrada.propuestas || 0;
  if (n > 0) {
    return {
      id: "por_revisar",
      etiqueta: ETIQUETAS.por_revisar,
      detalle: n === 1 ? "Hay 1 sugerencia de uxyn esperando tu decisión." : `Hay ${n} sugerencias de uxyn esperando tu decisión.`,
      revisar: "Revisa, corrige si hace falta, y acepta o rechaza en «Por revisar».",
      cta: n === 1 ? "Revisar cambios" : `Revisar ${n} cambios`,
      accion: "revisar",
      archivo: null,
      ...base,
    };
  }
  const hueco = huecoNucleo(entrada);
  const hayNucleo = (entrada.errores || []).length
    || (entrada.marcadores || []).some((m) => NUCLEO_SET.has(m.archivo || m.file))
    || entrada.valido === false;
  if (hayNucleo || (hueco && entrada.valido !== true)) {
    return {
      id: "falta_nucleo",
      etiqueta: ETIQUETAS.falta_nucleo,
      detalle: hueco?.texto || entrada.siguiente || "Quedan huecos o errores en los archivos núcleo.",
      revisar: hueco?.archivo ? `Abrir ${hueco.archivo} o pedir a uxyn que complete.` : "Pide a uxyn que complete lo que falta.",
      cta: "Que uxyn complete",
      accion: "completar",
      archivo: hueco?.archivo || null,
      ...base,
    };
  }
  if (entrada.valido === true && entrada.listo === true && entrada.alDia !== false) {
    return {
      id: "listo",
      etiqueta: ETIQUETAS.listo,
      detalle: entrada.siguiente || "El sistema cumple lo mínimo. Puedes publicar o seguir afinando con uxyn.",
      revisar: null,
      cta: "Abrir salida",
      accion: "abrir_salida",
      archivo: null,
      ...base,
    };
  }
  if (entrada.alDia === false || entrada.valido == null) {
    return {
      id: "ajustar",
      etiqueta: "Validar",
      detalle: entrada.alDia === false ? "Hay cambios desde la última validación." : "Aún no has validado este borrador.",
      revisar: null,
      cta: "Validar",
      accion: "validar",
      archivo: null,
      ...base,
    };
  }
  return {
    id: "ajustar",
    etiqueta: ETIQUETAS.ajustar,
    detalle: entrada.siguiente || "El mínimo está; afina con uxyn o el editor.",
    revisar: null,
    cta: "Que uxyn complete",
    accion: "completar",
    archivo: null,
    ...base,
  };
}

/** Clave de sessionStorage para recordar idea/adjuntos de un sistema. */
export function claveOrigen(id) {
  return `uxyn-taller-origen:${id || "_nuevo"}`;
}

export function guardarOrigen(id, origen) {
  try {
    sessionStorage.setItem(claveOrigen(id), JSON.stringify({
      idea: String(origen?.idea || "").slice(0, 4000),
      adjuntos: (origen?.adjuntos || []).map((a) => (typeof a === "string" ? a : a?.nombre || "")).filter(Boolean).slice(0, 40),
      nombre: String(origen?.nombre || "").slice(0, 120),
    }));
  } catch { /* sin almacenamiento */ }
}

export function leerOrigen(id) {
  try {
    const bruto = sessionStorage.getItem(claveOrigen(id));
    if (!bruto) return { idea: "", adjuntos: [], nombre: "" };
    const d = JSON.parse(bruto);
    return { idea: d.idea || "", adjuntos: d.adjuntos || [], nombre: d.nombre || "" };
  } catch {
    return { idea: "", adjuntos: [], nombre: "" };
  }
}

export function moverOrigen(desde, hacia) {
  if (!hacia || desde === hacia) return;
  const o = leerOrigen(desde);
  if (!o.idea && !(o.adjuntos || []).length) return;
  guardarOrigen(hacia, o);
  try { sessionStorage.removeItem(claveOrigen(desde)); } catch { /* */ }
}
