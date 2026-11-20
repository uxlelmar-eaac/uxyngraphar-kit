// Mis sistemas: TODOS tus sistemas (la misma lista que el Taller: catálogo local, borradores web, papelera y
// archivados, de GET /api/mis-sistemas), en carpetas que tú ordenas (arrastrando o con «Mover a…»), con sus
// herramientas: abrir en el Taller, instalar, descargar, duplicar, cambiar el nombre y eliminar (a la papelera).
//
// Las carpetas solo ordenan esta vista (.organizacion.json en la carpeta del catálogo): no mueven nada en el disco, la
// CLI sigue encontrando cada sistema y nada de esto toca el servidor (un borrador web o lo publicado siguen igual).

import { obtener, enviar } from "../api.js";
import { h, vaciar, cabecera, boton, insignia, vacio, confirmar, avisar, avisarConAccion, dialogo, icono, menu } from "../ui.js";
import { descargarZipSistema, instalarEnProyecto, FAMILIAS } from "./creador-editor.js";

const PREFERENCIAS = "uxyn-mis-sistemas";
const RAIZ = "_raiz";
const TODOS = "_todos";
const PAPELERA = "_papelera";

const sinTildes = (t) => String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
export const slugDe = (titulo) => sinTildes(titulo).toLowerCase().replace(/[^a-z]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40).replace(/-+$/, "");
const porTitulo = (a, b) => a.titulo.localeCompare(b.titulo, "es", { sensitivity: "base" });

function leerPreferencias() {
  try { return JSON.parse(localStorage.getItem(PREFERENCIAS)) || {}; } catch { return {}; }
}
function guardarPreferencias(p) {
  try { localStorage.setItem(PREFERENCIAS, JSON.stringify(p)); } catch { /* sin almacenamiento: no se recuerda */ }
}

const botonIcono = (nombre, etiqueta, accion) => {
  const b = h("button", { type: "button", class: "boton fantasma pequeno solo-icono", "aria-label": etiqueta, title: etiqueta, "aria-haspopup": "menu" }, icono(nombre));
  b.addEventListener("click", (e) => { e.stopPropagation(); accion(b); });
  return b;
};

/**
 * Diálogo «Eliminar» (a la papelera) con avisos de proyectos y borradores web, y «Deshacer» en el aviso. Lo usan Mis
 * sistemas y el Taller. `sistemas`: [{id, titulo}]. Devuelve lo eliminado o null si se cancela.
 */
export async function eliminarSistemas(sistemas, { instaladoEn = () => [], web = [], alCambiar = async () => {} } = {}) {
  if (!sistemas.length) return null;
  const filas = sistemas.map((s) => {
    const donde = instaladoEn(s.id);
    const b = (web || []).find((x) => x.slug === s.id);
    return h("li", {}, h("div", {}, h("b", { texto: s.titulo }), " ", h("code", { texto: s.id })),
      donde.length ? h("div", { class: "aviso-linea", texto: `Instalado en ${donde.join(", ")}: esos proyectos lo conservan.` }) : null,
      b ? h("div", { class: "aviso-linea", texto: `Tiene borrador en la web${b.version_publicada || b.publicado ? " y está publicado en el Mercado" : ""}: allí sigue igual.` }) : null);
  });
  const ok = await dialogo({ titulo: sistemas.length === 1 ? `¿Eliminar «${sistemas[0].titulo}»?` : `¿Eliminar ${sistemas.length} sistemas?`,
    contenido: h("div", { class: "pila" }, h("ul", { class: "lista eliminar-lista" }, filas),
      h("p", { texto: "Se mueve a la papelera de este equipo y puedes recuperarlo. No se borra nada del servidor: tu borrador web y lo publicado siguen igual." })),
    acciones: [{ texto: "Mover a la papelera", clase: "peligro lleno", accion: () => true }] });
  if (!ok) return null;
  const hechos = await enviar("/api/mis-sistemas/eliminar", { ids: sistemas.map((s) => s.id) });
  await alCambiar();
  avisarConAccion(hechos.length === 1 ? `«${hechos[0].titulo}» está en la papelera` : `${hechos.length} sistemas en la papelera`, "Deshacer", async () => {
    for (const x of hechos) await enviar("/api/mis-sistemas/restaurar", { entrada: x.entrada });
    await alCambiar();
    avisar(hechos.length === 1 ? `«${hechos[0].titulo}» restaurado` : `${hechos.length} sistemas restaurados`);
  });
  return hechos;
}

export async function vista(params, { ir }) {
  let datos = await obtener("/api/mis-sistemas");
  let proyectos = [];
  let borradores = null;   // null: sin consultar; [] sin sesión o sin borradores
  const pref = { orden: "manual", plegadas: [], ...leerPreferencias() };
  let actual = params.carpeta || pref.carpeta || TODOS;
  const filtros = { texto: "", familia: "", archivo: "" };
  const elegidos = new Set();
  let arrastre = null;   // { tipo: "sistema" | "carpeta", valor }: dataTransfer no se puede leer durante dragover

  obtener("/api/proyectos").then((l) => { proyectos = l || []; pintar(); }).catch(() => {});

  const carpeta = (id) => datos.carpetas.find((c) => c.id === id);
  const hijas = (padre) => datos.carpetas.filter((c) => (c.padre || null) === padre);
  const ruta = (id) => {
    const partes = [];
    for (let c = carpeta(id); c; c = carpeta(c.padre)) partes.unshift(c.nombre);
    return partes;
  };
  const ancestros = (id) => {
    const salida = [];
    for (let c = carpeta(id); c; c = carpeta(c.padre)) salida.unshift(c);
    return salida;
  };
  const descendientes = (id) => {
    const salida = new Set();
    const pendientes = [id];
    while (pendientes.length) for (const c of hijas(pendientes.pop())) if (!salida.has(c.id)) { salida.add(c.id); pendientes.push(c.id); }
    return salida;
  };
  const instaladoEn = (id) => {
    const lista = proyectos.filter((p) => p.existe && (p.sistemas || []).includes(id)).map((p) => p.nombre);
    return lista.length ? lista : (datos.sistemas.find((s) => s.id === id)?.instalado || []);
  };
  const nombreCarpeta = (id) => (id ? `«${ruta(id).join(" / ")}»` : "«Sin carpeta»");

  async function recargar(nuevos) {
    datos = nuevos && nuevos.sistemas ? nuevos : await obtener("/api/mis-sistemas");
    if (actual !== TODOS && actual !== RAIZ && actual !== PAPELERA && !carpeta(actual)) actual = TODOS;
    for (const id of [...elegidos]) if (!datos.sistemas.some((s) => s.id === id)) elegidos.delete(id);
    pintar();
  }
  const cambiar = async (rutaApi, cuerpo, aviso) => {
    await enviar(rutaApi, cuerpo);
    await recargar();
    if (aviso) avisar(aviso);
  };
  const mover = (ids, destino, antes = null) => {
    const cambia = ids.some((id) => (datos.sistemas.find((s) => s.id === id)?.carpeta || null) !== (destino || null));
    return cambiar("/api/mis-sistemas/mover", { ids, carpeta: destino || null, antes },
      cambia ? `${ids.length === 1 ? ids[0] : `${ids.length} sistemas`} → ${nombreCarpeta(destino)}` : "");
  };
  const moverCarpeta = (id, padre) => cambiar("/api/mis-sistemas/carpeta", { accion: "mover", id, padre: padre || null },
    `Carpeta movida a ${padre ? nombreCarpeta(padre) : "la raíz"}`);

  // Arrastrar y soltar ----------------------------------------------------------------------------------------------
  function arrastrable(el, tipo, valor) {
    el.draggable = true;
    el.addEventListener("dragstart", (e) => {
      e.stopPropagation();
      arrastre = { tipo, valor: tipo === "sistema" && elegidos.has(valor) && elegidos.size > 1 ? [...elegidos] : valor };
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", String(valor));
      el.classList.add("arrastrando");
      zona.classList.add(`arrastrando-${tipo}`);
    });
    el.addEventListener("dragend", () => {
      arrastre = null;
      el.classList.remove("arrastrando");
      zona.classList.remove("arrastrando-sistema", "arrastrando-carpeta");
      for (const d of document.querySelectorAll(".destino")) d.classList.remove("destino");
    });
  }
  function soltable(el, acepta, alSoltar) {
    el.addEventListener("dragover", (e) => {
      if (!arrastre || !acepta(arrastre)) return;
      e.preventDefault();
      e.stopPropagation();
      e.dataTransfer.dropEffect = "move";
      for (const d of document.querySelectorAll(".destino")) if (d !== el) d.classList.remove("destino");
      el.classList.add("destino");
    });
    el.addEventListener("dragleave", (e) => { if (!el.contains(e.relatedTarget)) el.classList.remove("destino"); });
    el.addEventListener("drop", (e) => {
      if (!arrastre || !acepta(arrastre)) return;
      e.preventDefault();
      e.stopPropagation();
      el.classList.remove("destino");
      const a = arrastre;
      arrastre = null;
      Promise.resolve(alSoltar(a)).catch((err) => avisar(err.message || String(err), "mal"));
    });
  }
  const idsDe = (a) => (Array.isArray(a.valor) ? a.valor : [a.valor]);
  const aceptaEnCarpeta = (destino) => (a) => (a.tipo === "sistema")
    || (a.tipo === "carpeta" && a.valor !== destino && !descendientes(a.valor).has(destino) && (carpeta(a.valor)?.padre || null) !== destino);
  const soltarEnCarpeta = (destino) => (a) => (a.tipo === "sistema" ? mover(idsDe(a), destino) : moverCarpeta(a.valor, destino));

  // Diálogos --------------------------------------------------------------------------------------------------------
  function opcionesDestino(seleccionado, excluir = new Set()) {
    const opciones = [h("option", { value: "", texto: "Sin carpeta (raíz)", selected: !seleccionado })];
    const recorrer = (padre, nivel) => {
      for (const c of hijas(padre)) {
        if (excluir.has(c.id)) continue;
        opciones.push(h("option", { value: c.id, selected: c.id === seleccionado, texto: `${"\u00a0\u00a0".repeat(nivel)}${c.nombre}` }));
        recorrer(c.id, nivel + 1);
      }
    };
    recorrer(null, 1);
    return opciones;
  }

  async function nuevaCarpeta(padre = null) {
    const nombre = h("input", { type: "text", maxlength: "40", placeholder: "Por ejemplo: Pruebas, Clientes, Archivados", "aria-label": "Nombre de la carpeta" });
    const dentro = h("select", { "aria-label": "Dentro de" }, opcionesDestino(padre));
    const id = await dialogo({ titulo: "Nueva carpeta", contenido: h("div", { class: "pila" },
      h("p", { class: "tenue", texto: "Las carpetas solo ordenan esta vista: no mueven nada en tu disco ni cambian ningún sistema." }),
      h("label", { class: "campo" }, "Nombre", nombre), h("label", { class: "campo" }, "Dentro de", dentro)),
    acciones: [{ texto: "Crear carpeta", clase: "primario", accion: async () => {
      if (!nombre.value.trim()) { avisar("Escribe un nombre para la carpeta", "mal"); return false; }
      const org = await enviar("/api/mis-sistemas/carpeta", { accion: "crear", nombre: nombre.value, padre: dentro.value || null });
      const nueva = org.carpetas.find((c) => (c.padre || null) === (dentro.value || null) && c.nombre.toLowerCase() === nombre.value.trim().replace(/\s+/g, " ").toLowerCase());
      return nueva?.id || true;
    } }] });
    if (id) { await recargar(); avisar("Carpeta creada"); }
    return id;
  }

  async function renombrarCarpeta(c) {
    const nombre = h("input", { type: "text", maxlength: "40", value: c.nombre, "aria-label": "Nombre de la carpeta" });
    const ok = await dialogo({ titulo: `Cambiar el nombre de «${c.nombre}»`, contenido: h("label", { class: "campo" }, "Nombre", nombre),
      acciones: [{ texto: "Guardar", clase: "primario", accion: async () => {
        if (!nombre.value.trim()) { avisar("Escribe un nombre para la carpeta", "mal"); return false; }
        await enviar("/api/mis-sistemas/carpeta", { accion: "renombrar", id: c.id, nombre: nombre.value });
        return true;
      } }] });
    if (ok) await recargar();
  }

  async function moverCarpetaDialogo(c) {
    const dentro = h("select", { "aria-label": "Mover dentro de" }, opcionesDestino(c.padre, new Set([c.id, ...descendientes(c.id)])));
    const destino = await dialogo({ titulo: `Mover la carpeta «${c.nombre}»`, contenido: h("label", { class: "campo" }, "Dentro de", dentro),
      acciones: [{ texto: "Mover", clase: "primario", accion: () => ({ padre: dentro.value || null }) }] });
    if (destino) await moverCarpeta(c.id, destino.padre);
  }

  async function borrarCarpeta(c) {
    const subcarpetas = descendientes(c.id);
    const todas = new Set([c.id, ...subcarpetas]);
    const dentro = datos.sistemas.filter((s) => todas.has(s.carpeta));
    if (dentro.length || subcarpetas.size) {
      const ok = await confirmar({ titulo: `¿Borrar la carpeta «${c.nombre}»?`, peligro: true, si: "Borrar la carpeta",
        texto: `Tiene ${dentro.length} sistema(s)${subcarpetas.size ? ` y ${subcarpetas.size} subcarpeta(s)` : ""}. Los sistemas pasan a «Sin carpeta»: no se borra ninguno.` });
      if (!ok) return;
    }
    await cambiar("/api/mis-sistemas/carpeta", { accion: "borrar", id: c.id, confirmar: true }, `Carpeta «${c.nombre}» borrada`);
  }

  async function moverDialogo(ids) {
    const una = ids.length === 1 ? datos.sistemas.find((s) => s.id === ids[0]) : null;
    const dentro = h("select", { "aria-label": "Mover a" }, opcionesDestino(una?.carpeta || null));
    const nueva = h("input", { type: "text", maxlength: "40", placeholder: "Nombre de la carpeta nueva (opcional)", "aria-label": "O crea una carpeta nueva" });
    const destino = await dialogo({ titulo: una ? `Mover «${una.titulo}»` : `Mover ${ids.length} sistemas`,
      contenido: h("div", { class: "pila" }, h("label", { class: "campo" }, "Carpeta", dentro),
        h("label", { class: "campo" }, "O crea una carpeta nueva (dentro de la elegida)", nueva)),
      acciones: [{ texto: "Mover", clase: "primario", accion: async () => {
        if (!nueva.value.trim()) return { carpeta: dentro.value || null };
        const org = await enviar("/api/mis-sistemas/carpeta", { accion: "crear", nombre: nueva.value, padre: dentro.value || null });
        const nombre = nueva.value.trim().replace(/\s+/g, " ").toLowerCase();
        return { carpeta: org.carpetas.find((c) => (c.padre || null) === (dentro.value || null) && c.nombre.toLowerCase() === nombre)?.id || null };
      } }] });
    if (destino) await mover(ids, destino.carpeta);
  }

  async function consultarBorradores() {
    if (borradores) return borradores;
    try {
      const cuenta = await obtener("/api/cuenta");
      borradores = cuenta?.tipo === "sesion" ? await obtener("/api/creador/borradores") : [];
    } catch { borradores = []; }
    return borradores;
  }

  async function eliminar(ids) {
    // Solo se elimina (a la papelera) lo que está en este equipo: un borrador web o algo ya en la papelera no.
    const sistemas = ids.map((id) => datos.sistemas.find((s) => s.id === id)).filter((s) => s && s.estado === "local");
    if (!sistemas.length) { avisar("Solo se pueden eliminar sistemas que están en este equipo.", "mal"); return; }
    const hechos = await eliminarSistemas(sistemas, { instaladoEn, web: await consultarBorradores(), alCambiar: recargar });
    if (hechos) for (const id of ids) elegidos.delete(id);
  }
  async function archivar(ids, si) {
    await enviar("/api/mis-sistemas/archivar", { ids, archivar: si });
    await recargar();
    avisarConAccion(si ? `${ids.length === 1 ? `«${ids[0]}»` : `${ids.length} sistemas`} archivado(s): ya no salen en el Taller` : "De vuelta en el Taller",
      "Deshacer", async () => { await enviar("/api/mis-sistemas/archivar", { ids, archivar: !si }); await recargar(); });
  }

  function campoIdDesdeTitulo(tituloInicial, idInicial) {
    const titulo = h("input", { type: "text", value: tituloInicial, placeholder: "Por ejemplo: Revisión de diseño", "aria-label": "Título" });
    const id = h("input", { type: "text", value: idInicial, spellcheck: false, "aria-label": "Id", class: "mono" });
    let tocado = false;
    id.addEventListener("input", () => { tocado = true; });
    titulo.addEventListener("input", () => { if (!tocado) id.value = slugDe(titulo.value); });
    return { titulo, id };
  }

  async function duplicar(s) {
    const c = campoIdDesdeTitulo("", "");
    const r = await dialogo({ titulo: `Duplicar «${s.titulo}»`, contenido: h("div", { class: "pila" },
      h("p", { class: "tenue", texto: "La copia tiene otro id y prefijos de fichas nuevos; queda justo detrás del original, en su misma carpeta." }),
      h("label", { class: "campo" }, "Título de la copia", c.titulo),
      h("label", { class: "campo" }, "Id (se escribe solo a partir del título)", c.id),
      h("p", { class: "tenue", texto: "El título son las palabras del id con tildes y mayúscula inicial (de 2 a 5 palabras, sin números)." })),
    acciones: [{ texto: "Duplicar", clase: "primario", accion: () => enviar("/api/mis-sistemas/duplicar", { id: s.id, nuevo_id: c.id.value.trim(), titulo: c.titulo.value.trim() }) }] });
    if (!r) return;
    await recargar();
    avisar(`Copia creada: ${r.id}${r.frases_quitadas?.length ? ` (sin las frases «${r.frases_quitadas.join("», «")}», que chocarían)` : ""}`);
  }

  async function renombrar(s) {
    const c = campoIdDesdeTitulo(s.titulo, s.id);
    const donde = instaladoEn(s.id);
    const r = await dialogo({ titulo: `Cambiar el nombre de «${s.titulo}»`, contenido: h("div", { class: "pila" },
      h("label", { class: "campo" }, "Título", c.titulo),
      h("label", { class: "campo" }, "Id", c.id),
      h("p", { class: "tenue", texto: "El título son las palabras del id: con el mismo id solo cambian tildes y mayúsculas. Para otro nombre cambia también el id." }),
      h("div", { class: "banda aviso", texto: "Al cambiar el id se crea el sistema con el id nuevo (mismos prefijos y frases) y el anterior va a la papelera, recuperable. "
        + (donde.length ? `Los proyectos donde está instalado (${donde.join(", ")}) siguen con el id anterior hasta que instales el nuevo. ` : "")
        + "Un borrador web o lo publicado no cambian de nombre." })),
    acciones: [{ texto: "Guardar", clase: "primario", accion: () => enviar("/api/mis-sistemas/renombrar", { id: s.id, titulo: c.titulo.value.trim(), nuevo_id: c.id.value.trim() }) }] });
    if (!r) return;
    await recargar();
    if (r.anterior) {
      avisarConAccion(`Ahora es ${r.id}; el anterior está en la papelera`, "Deshacer", async () => {
        await enviar("/api/mis-sistemas/eliminar", { ids: [r.id] });
        await enviar("/api/mis-sistemas/restaurar", { entrada: r.anterior.entrada });
        await recargar();
        avisar(`De vuelta como ${r.anterior.id}`);
      });
    } else avisar("Título cambiado");
  }

  // Traer a este equipo un borrador que solo está en la web (para editarlo) y restaurar uno de la papelera.
  async function traer(s) {
    const r = await enviar("/api/creador/bajar", { slug: s.id });
    if (r?.conflicto) { ir("creador", { id: s.id }); return; }
    await recargar();
    avisarConAccion(`«${s.titulo}» está ahora en este equipo`, "Abrir en el Taller", () => ir("creador", { id: s.id }));
  }
  async function restaurar(s) {
    await enviar("/api/mis-sistemas/restaurar", { entrada: s.entrada });
    await recargar();
    avisar(`«${s.titulo}» restaurado de la papelera`);
  }
  const accionPrincipal = (s) => (s.estado === "web"
    ? boton("Traer para editar", () => traer(s).catch((e) => avisar(e.message, "mal")), { clase: "primario pequeno", icono: "descargar" })
    : s.estado === "papelera"
      ? boton("Restaurar", () => restaurar(s).catch((e) => avisar(e.message, "mal")), { clase: "primario pequeno", icono: "deshacer" })
      : boton("Abrir en el Taller", () => ir("creador", { id: s.id }), { clase: "primario pequeno" }));

  const opcionesSistema = (s) => s.estado !== "local" ? [
    s.estado === "web"
      ? { texto: "Traer para editar", icono: "descargar", accion: () => traer(s).catch((e) => avisar(e.message, "mal")) }
      : { texto: "Restaurar de la papelera", icono: "deshacer", accion: () => restaurar(s).catch((e) => avisar(e.message, "mal")) },
    { texto: "Ver en el Taller", icono: "creador", accion: () => ir("creador", { id: s.id }) },
    "-",
    { texto: "Mover a…", icono: "carpeta", accion: () => moverDialogo([s.id]) },
    s.archivado
      ? { texto: "Volver al Taller", icono: "deshacer", accion: () => archivar([s.id], false).catch((e) => avisar(e.message, "mal")) }
      : { texto: "Archivar (ocultar del Taller)", icono: "lista", accion: () => archivar([s.id], true).catch((e) => avisar(e.message, "mal")) },
  ] : [
    { texto: "Abrir en el Taller", icono: "creador", accion: () => ir("creador", { id: s.id }) },
    { texto: "Revisar archivos", icono: "lista", accion: () => ir("revision", { id: s.id }) },
    { texto: "Instalar en un proyecto…", icono: "proyectos", accion: async () => { await instalarEnProyecto(s.id, s.titulo); proyectos = await obtener("/api/proyectos").catch(() => proyectos); pintar(); } },
    { texto: "Descargar como zip", icono: "descargar", accion: () => descargarZipSistema(s.id).catch((e) => avisar(e.message, "mal")) },
    "-",
    { texto: "Mover a…", icono: "carpeta", accion: () => moverDialogo([s.id]) },
    { texto: "Duplicar…", icono: "copiar", accion: () => duplicar(s).catch((e) => avisar(e.message, "mal")) },
    { texto: "Cambiar el nombre…", icono: "editar", accion: () => renombrar(s).catch((e) => avisar(e.message, "mal")) },
    s.archivado
      ? { texto: "Volver al Taller", icono: "deshacer", accion: () => archivar([s.id], false).catch((e) => avisar(e.message, "mal")) }
      : { texto: "Archivar (ocultar del Taller)", icono: "lista", accion: () => archivar([s.id], true).catch((e) => avisar(e.message, "mal")) },
    "-",
    { texto: "Eliminar…", icono: "basura", peligro: true, accion: () => eliminar([s.id]).catch((e) => avisar(e.message, "mal")) },
  ];
  const opcionesCarpeta = (c) => [
    { texto: "Nueva subcarpeta…", icono: "mas", accion: () => nuevaCarpeta(c.id) },
    { texto: "Cambiar el nombre…", icono: "editar", accion: () => renombrarCarpeta(c).catch((e) => avisar(e.message, "mal")) },
    { texto: "Mover a…", icono: "carpeta", accion: () => moverCarpetaDialogo(c).catch((e) => avisar(e.message, "mal")) },
    "-",
    { texto: "Borrar la carpeta…", icono: "basura", peligro: true, accion: () => borrarCarpeta(c).catch((e) => avisar(e.message, "mal")) },
  ];

  // Árbol de carpetas -----------------------------------------------------------------------------------------------
  const arbol = h("nav", { class: "arbol-carpetas", "aria-label": "Carpetas de Mis sistemas" });
  const cuantos = (id) => datos.sistemas.filter((s) => (s.carpeta || null) === id).length;
  function nodo({ id, nombre, icon, contador, soltar, extra, nivel = 0, carpetaObj = null, plegable = false }) {
    const plegada = carpetaObj && pref.plegadas.includes(carpetaObj.id);
    const fila = h("div", { class: `nodo-carpeta ${actual === id ? "activo" : ""}`, style: `--nivel:${nivel}`, "data-carpeta": id },
      plegable ? h("button", { type: "button", class: "nodo-plegar", "aria-label": plegada ? `Abrir ${nombre}` : `Plegar ${nombre}`, "aria-expanded": String(!plegada),
        onclick: () => { pref.plegadas = plegada ? pref.plegadas.filter((x) => x !== carpetaObj.id) : [...pref.plegadas, carpetaObj.id]; guardarPreferencias(pref); pintar(); } },
      h("span", { class: `chevron ${plegada ? "plegado" : ""}` }, icono("abajo"))) : h("span", { class: "nodo-hueco" }),
      h("button", { type: "button", class: "nodo-ir", "aria-current": actual === id ? "true" : null, onclick: () => elegir(id) },
        icono(icon), h("span", { class: "nodo-nombre", texto: nombre }), contador !== undefined ? h("span", { class: "contador", texto: String(contador) }) : null),
      extra || null);
    if (soltar) soltable(fila, soltar.acepta, soltar.alSoltar);
    if (carpetaObj) arrastrable(fila, "carpeta", carpetaObj.id);
    return fila;
  }
  function pintarArbol() {
    const filas = [
      nodo({ id: TODOS, nombre: "Todos", icon: "lista", contador: datos.sistemas.length }),
      nodo({ id: RAIZ, nombre: "Sin carpeta", icon: "proyectos", contador: cuantos(null), soltar: { acepta: aceptaEnCarpeta(null), alSoltar: soltarEnCarpeta(null) } }),
    ];
    const recorrer = (padre, nivel) => {
      for (const c of hijas(padre)) {
        const tieneHijas = hijas(c.id).length > 0;
        filas.push(nodo({ id: c.id, nombre: c.nombre, icon: "carpeta", contador: cuantos(c.id), nivel, carpetaObj: c, plegable: tieneHijas,
          soltar: { acepta: aceptaEnCarpeta(c.id), alSoltar: soltarEnCarpeta(c.id) },
          extra: botonIcono("puntos", `Opciones de la carpeta ${c.nombre}`, (b) => menu(b, opcionesCarpeta(c))) }));
        if (tieneHijas && !pref.plegadas.includes(c.id)) recorrer(c.id, nivel + 1);
      }
    };
    recorrer(null, 1);
    filas.push(h("hr", {}), nodo({ id: PAPELERA, nombre: "Papelera", icon: "basura", contador: datos.papelera }));
    vaciar(arbol, h("div", { class: "arbol-cabeza" }, h("b", { texto: "Carpetas" }),
      botonIcono("mas", "Nueva carpeta", () => nuevaCarpeta(carpeta(actual) ? actual : null))), filas);
  }
  function elegir(id) {
    actual = id;
    pref.carpeta = id;
    guardarPreferencias(pref);
    elegidos.clear();
    pintar();
  }

  // Tarjetas --------------------------------------------------------------------------------------------------------
  function estado(s) {
    if (s.estado === "web") return insignia("solo en la web", "acento");
    if (s.estado === "papelera") return insignia("en la papelera", "mal");
    if (s.errores.length) return insignia(`${s.errores.length} pendiente(s) de validar`, "aviso");
    return insignia("valida", "bien");
  }
  function tarjeta(s, enOrdenManual) {
    const donde = instaladoEn(s.id);
    const marca = h("input", { type: "checkbox", checked: elegidos.has(s.id), "aria-label": `Elegir ${s.titulo}` });
    marca.addEventListener("change", () => { if (marca.checked) elegidos.add(s.id); else elegidos.delete(s.id); pintarSeleccion(); el.classList.toggle("elegido", marca.checked); });
    const el = h("article", { class: `tarjeta tarjeta-item sistema-mio ${elegidos.has(s.id) ? "elegido" : ""}`, "data-id": s.id },
      h("div", { class: "proyecto-cabeza" },
        h("label", { class: "elegir-sistema" }, marca),
        h("span", { class: "asa", title: "Arrastra a una carpeta o entre sistemas para ordenar", "aria-hidden": "true" }, icono("asa")),
        h("div", { class: "proyecto-titulo" }, h("h3", { texto: s.titulo }), h("code", { class: "tenue", texto: s.id })),
        botonIcono("puntos", `Opciones de ${s.titulo}`, (b) => menu(b, opcionesSistema(s)))),
      h("div", { class: "proyecto-estado" }, estado(s),
        s.estado === "local" ? insignia("local", "bien") : null,
        s.web && s.estado !== "web" ? insignia("web", "acento") : null,
        s.publicado ? insignia("mercado", "acento") : null,
        s.estado === "local" && s.implementado === true ? insignia("Implementado ✓", "bien") : null,
        s.estado === "local" && s.implementado === false && !s.errores.length ? insignia("esqueleto: falta contenido", "aviso") : null,
        s.archivado ? insignia("archivado", "nota") : null,
        s.familia ? insignia(FAMILIAS[s.familia] || s.familia) : null,
        s.version ? h("span", { class: "tenue", texto: `v${s.version}` }) : null),
      s.descripcion ? h("p", { class: "tenue descripcion-corta", texto: s.descripcion }) : null,
      h("div", { class: "tenue detalle-sistema" },
        actual === TODOS || filtros.texto ? h("span", {}, icono("carpeta"), s.carpeta ? ruta(s.carpeta).join(" / ") : "Sin carpeta") : null,
        donde.length ? h("span", { title: donde.join(", ") }, icono("proyectos"), `Instalado en ${donde.length} proyecto(s)`) : null),
      h("div", { class: "acciones" },
        accionPrincipal(s),
        s.estado === "local" ? boton("Revisar archivos", () => ir("revision", { id: s.id }), { clase: "pequeno", icono: "lista", titulo: "A pantalla completa: lee sus archivos, mejora fragmentos con IA y deja notas y resaltados" }) : null,
        boton("Mover a…", () => moverDialogo([s.id]), { clase: "pequeno", icono: "carpeta" })));
    el.dataset.estado = s.estado || "local";
    el.addEventListener("dblclick", (e) => { if (!e.target.closest("button, input, label")) ir("creador", { id: s.id }); });
    arrastrable(el, "sistema", s.id);
    if (enOrdenManual) {
      soltable(el, (a) => a.tipo === "sistema" && !idsDe(a).includes(s.id), (a) => mover(idsDe(a), s.carpeta || null, s.id));
    }
    return el;
  }

  // Barra de herramientas -------------------------------------------------------------------------------------------
  const buscar = h("input", { type: "search", placeholder: "Buscar por título o id…", "aria-label": "Buscar sistema" });
  buscar.addEventListener("input", () => { filtros.texto = buscar.value.trim().toLowerCase(); pintar(); });
  const familia = h("select", { "aria-label": "Filtrar por familia" }, h("option", { value: "", texto: "Todas las familias" }),
    Object.entries(FAMILIAS).map(([v, t]) => h("option", { value: v, texto: t })));
  familia.addEventListener("change", () => { filtros.familia = familia.value; pintar(); });
  const orden = h("select", { "aria-label": "Ordenar" },
    [["manual", "Orden: el mío (arrastrando)"], ["titulo", "Orden: por título"], ["estado", "Orden: primero lo pendiente"], ["familia", "Orden: por familia"]]
      .map(([v, t]) => h("option", { value: v, selected: v === pref.orden, texto: t })));
  orden.addEventListener("change", () => { pref.orden = orden.value; guardarPreferencias(pref); pintar(); });
  const archivo = h("select", { "aria-label": "Filtrar por archivados" },
    [["", "Todos (también archivados)"], ["taller", "Solo los del Taller"], ["archivados", "Solo archivados"], ["local", "Solo en este equipo"], ["web", "Solo en la web"], ["papelera", "En la papelera"]].map(([v, t]) => h("option", { value: v, texto: t })));
  archivo.addEventListener("change", () => { filtros.archivo = archivo.value; pintar(); });
  const herramientas = h("div", { class: "herramientas-proyectos" }, buscar, familia, archivo, orden,
    boton("Nueva carpeta", () => nuevaCarpeta(carpeta(actual) ? actual : null), { clase: "pequeno", icono: "carpeta" }));

  const barraSeleccion = h("div", { class: "barra-seleccion", hidden: true });
  function pintarSeleccion() {
    barraSeleccion.hidden = !elegidos.size;
    if (!elegidos.size) return;
    vaciar(barraSeleccion, h("b", { texto: `${elegidos.size} elegido(s)` }),
      boton("Mover a…", () => moverDialogo([...elegidos]), { clase: "pequeno", icono: "carpeta" }),
      boton("Archivar", () => archivar([...elegidos], true), { clase: "pequeno", icono: "lista", titulo: "Ocultarlos del Taller sin borrar nada" }),
      boton("Eliminar…", () => eliminar([...elegidos]), { clase: "pequeno peligro", icono: "basura" }),
      boton("Quitar la selección", () => { elegidos.clear(); pintar(); }, { clase: "fantasma pequeno" }));
  }

  const pasa = (s) => (!filtros.familia || s.familia === filtros.familia)
    && (!filtros.archivo
      || (filtros.archivo === "archivados" && s.archivado)
      || (filtros.archivo === "taller" && !s.archivado && s.estado !== "papelera")
      || (["local", "web", "papelera"].includes(filtros.archivo) && s.estado === filtros.archivo))
    && (!filtros.texto || `${s.titulo} ${sinTildes(s.titulo)} ${s.id} ${s.descripcion}`.toLowerCase().includes(filtros.texto));
  function ordenar(lista) {
    if (pref.orden === "titulo") return [...lista].sort(porTitulo);
    if (pref.orden === "estado") return [...lista].sort((a, b) => b.errores.length - a.errores.length || porTitulo(a, b));
    if (pref.orden === "familia") return [...lista].sort((a, b) => a.familia.localeCompare(b.familia) || porTitulo(a, b));
    return lista;   // el servidor ya los da en tu orden
  }

  // Papelera --------------------------------------------------------------------------------------------------------
  async function pintarPapelera(cuerpo) {
    vaciar(cuerpo, h("p", { class: "tenue", texto: "Cargando la papelera…" }));
    const entradas = await obtener("/api/mis-sistemas/papelera");
    if (!entradas.length) {
      vaciar(cuerpo, vacio("La papelera está vacía", "Lo que elimines de «Mis sistemas» llega aquí y se puede restaurar."));
      return;
    }
    const restaurar = async (e) => {
      const r = await enviar("/api/mis-sistemas/restaurar", { entrada: e.entrada });
      await recargar();
      avisar(`«${r.titulo}» restaurado${r.carpeta ? ` en «${r.carpeta}»` : ""}`);
    };
    const borrar = async (e) => {
      const ok = await confirmar({ titulo: `¿Borrar para siempre «${e.titulo}»?`, peligro: true, si: "Borrar para siempre",
        texto: `${e.id} ${e.version} se borra de este equipo y no se puede recuperar. No se toca nada del servidor.` });
      if (!ok) return;
      await enviar("/api/mis-sistemas/vaciar", { entrada: e.entrada, confirmar: true });
      await recargar();
      avisar("Borrado para siempre");
    };
    const vaciarTodo = async () => {
      const ok = await confirmar({ titulo: "¿Vaciar la papelera?", peligro: true, si: "Vaciar la papelera",
        texto: `Se borran para siempre ${entradas.length} sistema(s) de este equipo. No se toca nada del servidor.` });
      if (!ok) return;
      await enviar("/api/mis-sistemas/vaciar", { confirmar: true });
      await recargar();
      avisar("Papelera vacía");
    };
    vaciar(cuerpo, h("div", { class: "fila separada" }, h("p", { class: "tenue", texto: "Restaura un sistema para devolverlo al catálogo (y a su carpeta, si aún existe)." }),
      boton("Vaciar la papelera", vaciarTodo, { clase: "peligro pequeno", icono: "basura" })),
    h("ul", { class: "lista papelera" }, entradas.map((e) => h("li", { class: "fila separada", "data-entrada": e.entrada },
      h("div", {}, h("b", { texto: e.titulo }), " ", h("code", { class: "tenue", texto: `${e.id} ${e.version}` }),
        h("div", { class: "tenue", texto: `Eliminado el ${String(e.eliminado || "").slice(0, 16).replace("T", " a las ")}${e.nombre_carpeta ? ` · estaba en «${e.nombre_carpeta}»` : ""}` }),
        e.choca ? h("div", { class: "aviso-linea", texto: "Ya hay otro sistema con este id: cámbiale el nombre o elimínalo antes de restaurar." }) : null),
      h("div", { class: "fila" }, boton("Restaurar", () => restaurar(e), { clase: "primario pequeno", icono: "deshacer" }),
        boton("Borrar para siempre", () => borrar(e), { clase: "fantasma pequeno peligro" }))))));
  }

  // Pintado ---------------------------------------------------------------------------------------------------------
  const contenido = h("div", { class: "mis-sistemas-contenido" });
  const zona = h("div", { class: "mis-sistemas" }, arbol, contenido);
  function pintar() {
    pintarArbol();
    if (actual === PAPELERA) {
      const cuerpo = h("div", { class: "pila" });
      vaciar(contenido, h("h2", {}, icono("basura"), " Papelera"), cuerpo);
      pintarPapelera(cuerpo).catch((e) => vaciar(cuerpo, h("div", { class: "banda mal", texto: e.message })));
      return;
    }
    const filtrando = Boolean(filtros.texto || filtros.familia || filtros.archivo);
    const enCarpeta = actual === RAIZ ? null : actual;
    const lista = ordenar(datos.sistemas.filter((s) => pasa(s) && (filtrando || actual === TODOS || (s.carpeta || null) === enCarpeta)));
    const manual = pref.orden === "manual" && !filtrando && actual !== TODOS;
    const titulo = actual === TODOS ? "Todos tus sistemas" : actual === RAIZ ? "Sin carpeta" : ruta(actual).join(" / ");
    const subcarpetas = actual === TODOS || filtrando ? [] : hijas(enCarpeta);
    const migas = carpeta(actual) ? h("div", { class: "migas tenue" },
      h("button", { type: "button", class: "enlace", texto: "Mis sistemas", onclick: () => elegir(TODOS) }),
      ancestros(actual).map((c, i, todos) => [" / ", i === todos.length - 1 ? h("b", { texto: c.nombre })
        : h("button", { type: "button", class: "enlace", texto: c.nombre, onclick: () => elegir(c.id) })])) : null;
    const cuerpo = lista.length || subcarpetas.length ? h("div", { class: "rejilla" },
      subcarpetas.map((c) => {
        const t = h("button", { type: "button", class: "tarjeta carpeta-tarjeta", onclick: () => elegir(c.id) },
          icono("carpeta"), h("span", { class: "nodo-nombre", texto: c.nombre }), h("span", { class: "contador", texto: String(cuantos(c.id)) }));
        soltable(t, aceptaEnCarpeta(c.id), soltarEnCarpeta(c.id));
        return t;
      }),
      lista.map((s) => tarjeta(s, manual)))
      : (datos.sistemas.length ? h("div", { class: "soltar-aqui", texto: filtrando ? "Ningún sistema coincide con la búsqueda." : "Carpeta vacía: arrastra sistemas aquí o usa «Mover a…»." })
        : vacio("Aún no tienes sistemas", "Crea tu primer sistema en el Taller y aparecerá aquí.", boton("Ir al Taller", () => ir("creador"), { clase: "primario" })));
    if (!lista.length && datos.sistemas.length && !filtrando && actual !== TODOS) soltable(cuerpo, aceptaEnCarpeta(enCarpeta), soltarEnCarpeta(enCarpeta));
    vaciar(contenido, migas, h("div", { class: "fila separada" }, h("h2", { texto: titulo }),
      h("span", { class: "tenue", texto: filtrando ? `${lista.length} de ${datos.sistemas.length}` : `${lista.length} sistema(s)` })),
    herramientas, barraSeleccion, cuerpo,
    manual && lista.length > 1 ? h("p", { class: "tenue pista", texto: "Arrastra un sistema sobre otro para ordenarlos, o sobre una carpeta para moverlo. En el móvil, usa «Mover a…»." }) : null);
    pintarSeleccion();
  }

  pintar();
  return h("div", {}, cabecera("Mis sistemas", "Todo lo que desarrollas: en tu equipo, solo en la web, archivado o instalado. Es la misma lista que el Taller. Las carpetas solo ordenan esta vista: no mueven nada en el disco ni tocan el servidor.",
    boton("Crear sistema", () => ir("creador"), { clase: "primario", icono: "mas" })), zona);
}
