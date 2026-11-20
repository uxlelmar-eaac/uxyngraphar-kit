// Lógica pura de las anotaciones de la revisión de archivos (sin DOM), la misma que la web
// (uxyngraphar-frontend, creator/annotations.ts): ubicar una cita en el texto, partir el texto en tramos con sus
// marcas y armar el pedido para uxyn.

/** Dónde está hoy la anotación en `texto`: sus posiciones si siguen valiendo, o la cita buscada; null si ya no está. */
export function ubicar(texto, a) {
  const cita = String(a?.cita || "");
  if (!cita) return null;
  if (Number.isInteger(a.inicio) && texto.slice(a.inicio, a.fin) === cita) return [a.inicio, a.fin];
  const i = texto.indexOf(cita);
  return i < 0 ? null : [i, i + cita.length];
}

/**
 * Tramos del texto con las anotaciones ubicadas: [{texto, anotacion|null}]. Si dos se solapan, gana la primera y la
 * otra no se pinta (sigue en la lista lateral).
 */
export function tramos(texto, anotaciones) {
  const ubicadas = (anotaciones || [])
    .map((a) => ({ a, r: ubicar(texto, a) }))
    .filter((x) => x.r)
    .sort((x, y) => x.r[0] - y.r[0]);
  const salida = [];
  let pos = 0;
  for (const { a, r: [ini, fin] } of ubicadas) {
    if (ini < pos) continue;
    if (ini > pos) salida.push({ texto: texto.slice(pos, ini), anotacion: null });
    salida.push({ texto: texto.slice(ini, fin), anotacion: a });
    pos = fin;
  }
  if (pos < texto.length || !salida.length) salida.push({ texto: texto.slice(pos), anotacion: null });
  return salida;
}

/** El mensaje que recibe uxyn con las notas y los resaltados abiertos ("" si no hay). Igual que anotaciones.py. */
export function pedidoParaUxyn(anotaciones) {
  const abiertas = (anotaciones || []).filter((a) => (a.estado || "abierta") === "abierta");
  if (!abiertas.length) return "";
  const lineas = abiertas.map((a) => {
    let cita = String(a.cita || "").split(/\s+/).filter(Boolean).join(" ");
    if (cita.length > 300) cita = `${cita.slice(0, 297)}…`;
    return a.tipo === "nota"
      ? `- ${a.archivo}: «${cita}» → nota: ${a.nota}`
      : `- ${a.archivo}: «${cita}» (resaltado: revisa y mejora este fragmento)`;
  });
  return "Revisa mis notas y resaltados de este sistema y úsalos como guía para mejorarlo. Para cada uno, cambia "
    + "lo que pide la nota o mejora el fragmento resaltado, y añade lo que haga falta en otros archivos para que "
    + "el sistema sea coherente. Déjalo todo en «Por revisar».\n\n" + lineas.join("\n");
}
