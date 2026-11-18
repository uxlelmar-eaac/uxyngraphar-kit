// Contrato de estados del Creador asistido (misma semántica que la web).
// Carril: estado · qué falta · qué revisar · siguiente paso (una CTA).

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
 * @param {{ tieneSistema: boolean, proponiendo?: boolean, propuestas?: number,
 *   valido?: boolean|null, listo?: boolean|null, alDia?: boolean|null,
 *   errores?: string[], marcadores?: object[], siguiente?: string|null }} entrada
 */
export function resolverEstado(entrada) {
  if (!entrada.tieneSistema) {
    return {
      id: "sin_sistema",
      etiqueta: ETIQUETAS.sin_sistema,
      detalle: "Cuenta tu idea o adjunta archivos/zip. uxyn arma el núcleo; tú aceptas los cambios.",
      revisar: null,
      cta: "Crear con uxyn",
      accion: "crear",
      archivo: null,
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
    };
  }
  if (entrada.valido === true && entrada.listo === true && entrada.alDia !== false) {
    return {
      id: "listo",
      etiqueta: ETIQUETAS.listo,
      detalle: entrada.siguiente || "El sistema cumple lo mínimo. Puedes publicar o seguir afinando con uxyn.",
      revisar: null,
      cta: "Publicar",
      accion: "publicar",
      archivo: null,
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
  };
}
