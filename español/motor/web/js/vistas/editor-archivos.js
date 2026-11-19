// Archivos de un sistema como en un editor de código: árbol con carpetas (crear, renombrar, borrar), pestañas,
// resaltado, números de línea, buscar y reemplazar, Ctrl+S, avisos de cambios sin guardar, vista previa de Markdown,
// divisores arrastrables, errores de validación por archivo y línea y las sugerencias de uxyn abiertas como diferencias.

import { obtener, enviar } from "../api.js";
import { h, vaciar, boton, avisar, confirmar, pedirDatos, icono, menu } from "../ui.js";
import { crearEditor, lenguajeDe, NOMBRE_LENGUAJE, markdownANodos, vistaDiferenciasCodigo, divisor } from "../editor-codigo.js";
import { diferenciasLineas } from "./creador.js";

const PREFERIDOS = ["SISTEMA.md", "README.md", "sistema.json"];
const RE_ARCHIVO_LINEA = /([\w./-]+\.(?:md|json|py|ya?ml|sh|txt))(?::(\d+))?/;

/** Árbol {carpetas: Map(nombre → árbol), archivos: [rel]} a partir de rutas «a/b/c.md». */
export function arbolDeRutas(rutas, extras = []) {
  const raiz = { carpetas: new Map(), archivos: [] };
  const carpetaDe = (partes) => {
    let nodo = raiz;
    for (const p of partes) {
      if (!nodo.carpetas.has(p)) nodo.carpetas.set(p, { carpetas: new Map(), archivos: [] });
      nodo = nodo.carpetas.get(p);
    }
    return nodo;
  };
  for (const c of extras) carpetaDe(c.split("/").filter(Boolean));
  for (const r of rutas) {
    const partes = r.split("/");
    carpetaDe(partes.slice(0, -1)).archivos.push(r);
  }
  return raiz;
}

/** Errores de validación agrupados por archivo: Map(rel → [{linea, texto}]) + los generales. */
export function erroresPorArchivo(pendientes, rutas) {
  const mapa = new Map();
  const generales = [];
  const poner = (rel, linea, texto) => { if (!mapa.has(rel)) mapa.set(rel, []); mapa.get(rel).push({ linea, texto }); };
  for (const m of pendientes?.marcadores || []) poner(m.archivo, m.linea, `Hueco por rellenar ${m.marcador}`);
  for (const e of pendientes?.errores || []) {
    if (/marcadores sin rellenar/.test(e)) continue;   // ya están por línea
    const m = RE_ARCHIVO_LINEA.exec(e);
    const rel = m && rutas.find((r) => r === m[1] || r.endsWith(`/${m[1]}`));
    if (rel) poner(rel, m[2] ? Number(m[2]) : null, e);
    else generales.push(e);
  }
  return { mapa, generales };
}

export async function explorador(id, { alGuardado = async () => {}, alCambiarArchivos = async () => {} } = {}) {
  let rutas = [];
  const virtuales = new Set();
  const claveArbol = `uxyn-editor-plegadas-${id}`;
  let plegadas = new Set();
  try { plegadas = new Set(JSON.parse(localStorage.getItem(claveArbol) || "[]")); } catch { /* */ }
  const pestanas = [];
  let activa = null;
  let errores = { mapa: new Map(), generales: [] };
  let modoPrevia = "editor";
  try { modoPrevia = localStorage.getItem("uxyn-editor-previa") || "editor"; } catch { /* */ }

  const estado = h("div", { class: "ide-estado", "aria-live": "polite" });
  const editor = crearEditor({
    alCambiar: (v) => {
      if (activa?.tipo !== "archivo") return;
      activa.texto = v;
      marcarSucias();
      programarPrevia();
    },
    alGuardar: () => guardar().catch((e) => avisar(e.message || String(e), "mal")),
    alCursor: () => pintarEstado(),
  });
  const zonaDiff = h("div", { class: "ide-diff", hidden: true });
  const vacio = h("div", { class: "ide-vacio tenue", texto: "Elige un archivo en el árbol (o crea uno) para verlo aquí." });
  const previa = h("div", { class: "ide-previa", "aria-label": "Vista previa", hidden: true });
  const arbol = h("ul", { class: "ide-arbol-lista", role: "tree", "aria-label": "Archivos del sistema" });
  const barraPestanas = h("div", { class: "ide-pestanas", role: "tablist", "aria-label": "Archivos abiertos" });
  const problemas = h("details", { class: "ide-problemas" });
  const selPrevia = h("select", { "aria-label": "Vista previa de Markdown", class: "ide-sel-previa" },
    [["editor", "Solo editor"], ["dividido", "Editor y vista previa"], ["previa", "Solo vista previa"]].map(([v, t]) => h("option", { value: v, texto: t, selected: v === modoPrevia })));
  const trabajo = h("div", { class: "ide-trabajo" }, editor.nodo, zonaDiff, vacio);
  const divPrevia = divisor(trabajo, "--ancho-previa", "uxyn-editor-ancho-previa", { minimo: 200, maximo: 900, inicial: 420, invertir: true });
  divPrevia.classList.add("ide-div-previa");
  // El divisor de la vista previa mide desde la derecha: arrastrar a la izquierda la ensancha.
  trabajo.append(divPrevia, previa);

  const sucia = (p) => p.tipo === "archivo" && p.enDisco !== null && p.texto !== p.enDisco;
  const haySinGuardar = () => pestanas.some(sucia);

  // Árbol --------------------------------------------------------------------------------------------------------
  async function cargarLista() {
    rutas = await obtener("/api/catalogo/archivos", { id });
    for (const v of [...virtuales]) if (rutas.some((r) => r.startsWith(`${v}/`))) virtuales.delete(v);
  }
  function guardarPlegadas() { try { localStorage.setItem(claveArbol, JSON.stringify([...plegadas])); } catch { /* */ } }
  function fila({ rel, nombre, carpeta, nivel }) {
    const errs = carpeta ? [...errores.mapa.keys()].filter((r) => r.startsWith(`${rel}/`)).length : (errores.mapa.get(rel) || []).length;
    const abierta = !carpeta && pestanas.some((p) => p.tipo === "archivo" && p.rel === rel);
    const el = h("li", { role: "treeitem", class: `ide-nodo ${carpeta ? "es-carpeta" : "es-archivo"}${activa?.rel === rel && activa?.tipo === "archivo" ? " activo" : ""}`,
      "data-rel": rel, "aria-expanded": carpeta ? String(!plegadas.has(rel)) : null },
    h("div", { class: "ide-nodo-fila", style: `--nivel:${nivel}` },
      h("button", { type: "button", class: "ide-nodo-nombre", title: rel,
        onclick: () => {
          if (carpeta) { if (plegadas.has(rel)) plegadas.delete(rel); else plegadas.add(rel); guardarPlegadas(); pintarArbol(); }
          else abrirArchivo(rel).catch((e) => avisar(e.message || String(e), "mal"));
        } },
      carpeta ? h("span", { class: "ide-flecha", texto: plegadas.has(rel) ? "▸" : "▾" }) : h("span", { class: "ide-flecha" }),
      icono(carpeta ? "carpeta" : "lista"), h("span", { class: "ide-nodo-texto", texto: nombre }),
      abierta && pestanas.some((p) => p.rel === rel && sucia(p)) ? h("span", { class: "punto-sucio", title: "Sin guardar", texto: "●" }) : null,
      errs ? h("span", { class: "ide-err", title: `${errs} aviso(s) de validación`, texto: String(errs) }) : null),
    h("button", { type: "button", class: "boton fantasma pequeno solo-icono ide-nodo-menu", "aria-haspopup": "menu", title: `Opciones de ${nombre}`, "aria-label": `Opciones de ${nombre}`,
      onclick: (e) => { e.stopPropagation(); menu(e.currentTarget, carpeta ? opcionesCarpeta(rel) : opcionesArchivo(rel)); } }, icono("puntos"))));
    return el;
  }
  function pintarArbol() {
    const items = [];
    const recorrer = (nodo, prefijo, nivel) => {
      for (const nombre of [...nodo.carpetas.keys()].sort((a, b) => a.localeCompare(b))) {
        const rel = prefijo ? `${prefijo}/${nombre}` : nombre;
        items.push(fila({ rel, nombre, carpeta: true, nivel }));
        if (!plegadas.has(rel)) recorrer(nodo.carpetas.get(nombre), rel, nivel + 1);
      }
      const orden = (r) => { const i = PREFERIDOS.indexOf(r); return i < 0 ? 99 : i; };
      for (const rel of [...nodo.archivos].sort((a, b) => orden(a) - orden(b) || a.localeCompare(b))) {
        items.push(fila({ rel, nombre: rel.split("/").pop(), carpeta: false, nivel }));
      }
    };
    recorrer(arbolDeRutas(rutas, [...virtuales]), "", 0);
    vaciar(arbol, items.length ? items : h("li", { class: "tenue", texto: "Sin archivos." }));
  }
  const opcionesArchivo = (rel) => [
    { texto: "Abrir", icono: "editar", accion: () => abrirArchivo(rel) },
    { texto: "Renombrar o mover…", icono: "editar", accion: () => renombrar(rel, false).catch((e) => avisar(e.message, "mal")) },
    { texto: "Copiar la ruta", icono: "copiar", accion: () => navigator.clipboard?.writeText(rel).then(() => avisar("Ruta copiada")) },
    "-",
    { texto: "Borrar…", icono: "basura", peligro: true, accion: () => borrar(rel, false).catch((e) => avisar(e.message, "mal")) },
  ];
  const opcionesCarpeta = (rel) => [
    { texto: "Archivo nuevo aquí…", icono: "mas", accion: () => nuevoArchivo(rel).catch((e) => avisar(e.message, "mal")) },
    { texto: "Carpeta nueva aquí…", icono: "carpeta", accion: () => nuevaCarpeta(rel).catch((e) => avisar(e.message, "mal")) },
    { texto: "Renombrar o mover…", icono: "editar", accion: () => renombrar(rel, true).catch((e) => avisar(e.message, "mal")) },
    "-",
    { texto: "Borrar la carpeta…", icono: "basura", peligro: true, accion: () => borrar(rel, true).catch((e) => avisar(e.message, "mal")) },
  ];
  const limpiar = (r) => String(r || "").trim().replace(/^\/+|\/+$/g, "");

  async function nuevoArchivo(carpeta = "") {
    const r = await pedirDatos({ titulo: "Archivo nuevo", explicacion: "Sin espacios ni tildes; puedes usar carpetas: ejemplos/caso.md",
      campos: [{ nombre: "rel", etiqueta: "Ruta", valor: carpeta ? `${carpeta}/` : "" }], si: "Crear" });
    const rel = limpiar(r?.rel);
    if (!rel || rel.endsWith("/")) return;
    if (rutas.includes(rel)) return abrirArchivo(rel);
    const inicial = rel.endsWith(".md") ? `# ${rel.split("/").pop().replace(/\.md$/, "")}\n` : rel.endsWith(".json") ? "{}\n" : "";
    await enviar("/api/catalogo/archivo", { id, rel, contenido: inicial });
    await cargarLista();
    await abrirArchivo(rel);
    await refrescarErrores();
    await alCambiarArchivos();
  }
  async function nuevaCarpeta(padre = "") {
    const r = await pedirDatos({ titulo: "Carpeta nueva", explicacion: "Aparece en el árbol al momento; se guarda en el disco cuando crees un archivo dentro.",
      campos: [{ nombre: "nombre", etiqueta: "Nombre", valor: padre ? `${padre}/` : "" }], si: "Crear" });
    const rel = limpiar(r?.nombre);
    if (!rel) return;
    if (!/^[\w./-]+$/.test(rel)) throw new Error("Nombre de carpeta: letras sin tildes, números, guiones y barras.");
    virtuales.add(rel);
    plegadas.delete(rel);
    pintarArbol();
  }
  async function renombrar(rel, carpeta) {
    if (carpeta && virtuales.has(rel) && !rutas.some((r) => r.startsWith(`${rel}/`))) {
      const r = await pedirDatos({ titulo: "Renombrar carpeta", campos: [{ nombre: "a", etiqueta: "Nombre nuevo", valor: rel }], si: "Renombrar" });
      const a = limpiar(r?.a);
      if (a && a !== rel) { virtuales.delete(rel); virtuales.add(a); pintarArbol(); }
      return;
    }
    const afectadas = pestanas.filter((p) => p.tipo === "archivo" && (p.rel === rel || p.rel.startsWith(`${rel}/`)));
    if (afectadas.some(sucia)) throw new Error("Guarda o descarta antes los cambios de los archivos que vas a mover.");
    const r = await pedirDatos({ titulo: carpeta ? "Renombrar o mover la carpeta" : "Renombrar o mover el archivo",
      explicacion: "Escribe la ruta nueva dentro del sistema.", campos: [{ nombre: "a", etiqueta: "Ruta nueva", valor: rel }], si: "Renombrar" });
    const a = limpiar(r?.a);
    if (!a || a === rel) return;
    const hecho = await enviar("/api/catalogo/archivo/renombrar", { id, de: rel, a });
    for (const p of afectadas) { p.rel = a + p.rel.slice(rel.length); p.clave = `archivo:${p.rel}`; p.lenguaje = lenguajeDe(p.rel); }
    await cargarLista();
    mostrarActiva();
    pintarPestanas();
    await refrescarErrores(hecho.errores);
    avisar(`${rel} → ${a}`);
    await alCambiarArchivos();
  }
  async function borrar(rel, carpeta) {
    if (carpeta && virtuales.has(rel) && !rutas.some((r) => r.startsWith(`${rel}/`))) { virtuales.delete(rel); pintarArbol(); return; }
    const dentro = carpeta ? rutas.filter((r) => r.startsWith(`${rel}/`)) : [rel];
    const ok = await confirmar({ titulo: carpeta ? `¿Borrar la carpeta ${rel}?` : `¿Borrar ${rel}?`, peligro: true, si: "Borrar",
      texto: carpeta ? `Se borran ${dentro.length} archivo(s): ${dentro.slice(0, 6).join(", ")}${dentro.length > 6 ? "…" : ""}.` : "Se borra del sistema en este equipo." });
    if (!ok) return;
    const hecho = await enviar("/api/catalogo/archivo/borrar", { id, rel, ...(carpeta ? { carpeta: true } : {}) });
    for (const p of [...pestanas]) if (p.tipo === "archivo" && dentro.includes(p.rel)) quitarPestana(p);
    await cargarLista();
    pintarPestanas();
    await refrescarErrores(hecho.errores);
    mostrarActiva();
    avisar(carpeta ? `Carpeta ${rel} borrada` : `${rel} borrado`);
    await alCambiarArchivos();
  }

  // Pestañas -----------------------------------------------------------------------------------------------------
  function guardarEstadoActiva() {
    if (activa?.tipo === "archivo") { activa.texto = editor.valor(); activa.vista = editor.estado(); }
  }
  async function abrirArchivo(rel, { linea = null } = {}) {
    let p = pestanas.find((x) => x.tipo === "archivo" && x.rel === rel);
    if (!p) {
      const contenido = (await obtener("/api/catalogo/archivo", { id, rel })).contenido;
      p = { clave: `archivo:${rel}`, tipo: "archivo", rel, texto: contenido, enDisco: contenido, lenguaje: lenguajeDe(rel), vista: null, nota: "" };
      pestanas.push(p);
    }
    activar(p);
    if (linea) editor.irALinea(linea);
    return p;
  }
  function abrirDiferencias(rel, antes, despues, titulo = "Sugerencia") {
    const clave = `diff:${rel}:${titulo}`;
    let p = pestanas.find((x) => x.clave === clave);
    if (!p) { p = { clave, tipo: "diff", rel, antes, despues, titulo }; pestanas.push(p); }
    else Object.assign(p, { antes, despues });
    activar(p);
  }
  function activar(p) {
    if (activa !== p) guardarEstadoActiva();
    activa = p;
    mostrarActiva();
    pintarPestanas();
    pintarArbol();
  }
  function mostrarActiva() {
    const p = activa && pestanas.includes(activa) ? activa : null;
    if (!p) activa = null;
    vacio.hidden = Boolean(p);
    editor.nodo.hidden = p?.tipo !== "archivo";
    zonaDiff.hidden = p?.tipo !== "diff";
    selPrevia.hidden = !(p?.tipo === "archivo" && p.lenguaje === "md");
    if (p?.tipo === "archivo") {
      editor.fijar(p.texto, p.lenguaje);
      editor.restaurar(p.vista);
      const marcas = {};
      for (const e of errores.mapa.get(p.rel) || []) if (e.linea) marcas[e.linea] = (marcas[e.linea] ? `${marcas[e.linea]}\n` : "") + e.texto;
      editor.marcar(marcas);
    }
    if (p?.tipo === "diff") pintarDiff(p);
    aplicarPrevia();
    pintarEstado();
  }
  function pintarDiff(p) {
    vaciar(zonaDiff,
      h("div", { class: "fila separada ide-diff-cabeza" },
        h("div", {}, h("b", { texto: `${p.titulo} · ${p.rel}` }), h("div", { class: "tenue", texto: "Izquierda: antes · derecha: lo que propone uxyn. Decide en «Por revisar»." })),
        h("div", { class: "fila" },
          p.despues !== null && p.despues !== undefined ? boton("Llevar la propuesta al editor", async () => {
            const f = rutas.includes(p.rel) ? await abrirArchivo(p.rel) : null;
            if (!f) {
              await enviar("/api/catalogo/archivo", { id, rel: p.rel, contenido: "" });
              await cargarLista();
              await abrirArchivo(p.rel);
            }
            const objetivo = pestanas.find((x) => x.tipo === "archivo" && x.rel === p.rel);
            objetivo.texto = p.despues;
            if (objetivo.enDisco === "" && !f) objetivo.enDisco = "";
            mostrarActiva();
            marcarSucias();
            avisar("La propuesta está en el editor sin guardar: revísala y pulsa Ctrl+S para guardarla.");
          }, { clase: "pequeno", icono: "editar" }) : null,
          rutas.includes(p.rel) ? boton("Abrir el archivo", () => abrirArchivo(p.rel), { clase: "pequeno" }) : null)),
      vistaDiferenciasCodigo(diferenciasLineas(p.antes || "", p.despues || "")));
  }
  function quitarPestana(p) {
    const i = pestanas.indexOf(p);
    if (i < 0) return;
    pestanas.splice(i, 1);
    if (activa === p) activa = pestanas[Math.min(i, pestanas.length - 1)] || null;
  }
  async function cerrar(p) {
    if (activa === p) guardarEstadoActiva();
    if (sucia(p) && !(await confirmar({ titulo: "Cambios sin guardar", texto: `${p.rel} tiene cambios sin guardar. Si cierras la pestaña, se pierden.`, si: "Cerrar sin guardar", peligro: true }))) return;
    quitarPestana(p);
    mostrarActiva();
    pintarPestanas();
    pintarArbol();
  }
  function pintarPestanas() {
    vaciar(barraPestanas, pestanas.map((p) => {
      const t = h("div", { class: `ide-pestana${p === activa ? " activa" : ""}${sucia(p) ? " sucia" : ""}${p.tipo === "diff" ? " es-diff" : ""}`, "data-clave": p.clave },
        h("button", { type: "button", role: "tab", "aria-selected": String(p === activa), class: "ide-pestana-nombre", title: p.tipo === "diff" ? `${p.titulo}: ${p.rel}` : p.rel,
          onclick: () => activar(p) },
        p.tipo === "diff" ? "± " : "", p.rel.split("/").pop(), h("span", { class: "punto-sucio", "aria-label": "sin guardar", texto: sucia(p) ? " ●" : "" })),
        h("button", { type: "button", class: "ide-pestana-cerrar", "aria-label": `Cerrar ${p.rel}`, title: "Cerrar", texto: "×",
          onclick: () => cerrar(p).catch((e) => avisar(e.message, "mal")) }));
      t.addEventListener("auxclick", (e) => { if (e.button === 1) cerrar(p); });
      return t;
    }));
    botonGuardarTodo.hidden = pestanas.filter(sucia).length < 2;
    barraPestanas.querySelector(".ide-pestana.activa")?.scrollIntoView({ block: "nearest", inline: "nearest" });
  }
  function marcarSucias() {
    for (const el of barraPestanas.querySelectorAll(".ide-pestana")) {
      const p = pestanas.find((x) => x.clave === el.dataset.clave);
      if (!p) continue;
      el.classList.toggle("sucia", sucia(p));
      const punto = el.querySelector(".punto-sucio");
      if (punto) punto.textContent = sucia(p) ? " ●" : "";
    }
    botonGuardarTodo.hidden = pestanas.filter(sucia).length < 2;
    const nodo = activa?.tipo === "archivo" ? arbol.querySelector(`[data-rel="${CSS.escape(activa.rel)}"] .ide-nodo-nombre`) : null;
    if (nodo) {
      const punto = nodo.querySelector(".punto-sucio");
      if (sucia(activa) && !punto) nodo.append(h("span", { class: "punto-sucio", title: "Sin guardar", texto: "●" }));
      if (!sucia(activa) && punto) punto.remove();
    }
    pintarEstado();
  }
  function pintarEstado() {
    if (activa?.tipo !== "archivo") { vaciar(estado, activa ? h("span", { texto: `Diferencias · ${activa.rel}` }) : null); return; }
    const pos = editor.posicion();
    vaciar(estado,
      h("span", { texto: activa.rel }),
      h("span", { texto: `Línea ${pos.linea}, columna ${pos.columna} · ${pos.lineas} líneas` }),
      h("span", { texto: NOMBRE_LENGUAJE[activa.lenguaje] || "Texto" }),
      sucia(activa) ? h("span", { class: "insignia nota", texto: "sin guardar" }) : h("span", { class: "tenue", texto: "guardado" }),
      activa.nota ? h("span", { class: "aviso-linea", texto: activa.nota }) : null);
  }

  // Vista previa -------------------------------------------------------------------------------------------------
  let temporizadorPrevia = 0;
  function programarPrevia() { clearTimeout(temporizadorPrevia); temporizadorPrevia = setTimeout(pintarPrevia, 180); }
  function pintarPrevia() { if (!previa.hidden && activa?.tipo === "archivo") vaciar(previa, markdownANodos(editor.valor())); }
  function aplicarPrevia() {
    const md = activa?.tipo === "archivo" && activa.lenguaje === "md";
    const modo = md ? modoPrevia : "editor";
    trabajo.dataset.previa = modo;
    previa.hidden = modo === "editor";
    divPrevia.hidden = modo !== "dividido";
    if (modo === "previa") editor.nodo.hidden = true;
    pintarPrevia();
  }
  selPrevia.addEventListener("change", () => {
    modoPrevia = selPrevia.value;
    try { localStorage.setItem("uxyn-editor-previa", modoPrevia); } catch { /* */ }
    mostrarActiva();
  });

  // Guardar, errores y recarga -----------------------------------------------------------------------------------
  async function refrescarErrores(validacion) {
    let p = null;
    try { p = await obtener("/api/catalogo/pendientes", { id }); } catch { p = { errores: validacion || [], marcadores: [] }; }
    errores = erroresPorArchivo(p, rutas);
    const total = [...errores.mapa.values()].reduce((s, l) => s + l.length, 0) + errores.generales.length;
    vaciar(problemas,
      h("summary", {}, total ? `Problemas (${total})` : "Sin problemas de validación"),
      h("ul", { class: "lista ide-problemas-lista" },
        [...errores.mapa.entries()].flatMap(([rel, lista]) => lista.map((e) => h("li", {},
          h("button", { type: "button", class: "enlace", texto: `${rel}${e.linea ? `:${e.linea}` : ""}`,
            onclick: () => abrirArchivo(rel, { linea: e.linea }).catch((x) => avisar(x.message, "mal")) }), " ", e.texto))),
        errores.generales.map((e) => h("li", { texto: e }))));
    problemas.hidden = false;
    if (activa?.tipo === "archivo") {
      const marcas = {};
      for (const e of errores.mapa.get(activa.rel) || []) if (e.linea) marcas[e.linea] = (marcas[e.linea] ? `${marcas[e.linea]}\n` : "") + e.texto;
      editor.marcar(marcas);
    }
    pintarArbol();
  }
  async function guardar(p = activa) {
    if (!p || p.tipo !== "archivo") return avisar("Abre un archivo para guardarlo.", "mal");
    if (p === activa) p.texto = editor.valor();
    const r = await enviar("/api/catalogo/archivo", { id, rel: p.rel, contenido: p.texto });
    const noGuardado = (r.errores || []).some((e) => String(e).startsWith("no guardado"));
    if (!noGuardado) { p.enDisco = p.texto; p.nota = ""; }
    marcarSucias();
    pintarPestanas();
    await refrescarErrores(r.errores);
    avisar(noGuardado ? r.errores.join("; ") : (r.errores || []).length ? `${p.rel} guardado; al sistema aún le falta algo (mira «Problemas»)` : `${p.rel} guardado`,
      noGuardado || (r.errores || []).length ? "mal" : "");
    await alGuardado(p.rel);
  }
  async function guardarTodo() {
    for (const p of pestanas.filter(sucia)) await guardar(p);
  }
  async function recargar() {
    guardarEstadoActiva();
    await cargarLista();
    for (const p of [...pestanas]) {
      if (p.tipo !== "archivo") continue;
      if (!rutas.includes(p.rel)) { if (!sucia(p)) quitarPestana(p); else p.nota = "Este archivo ya no está en el disco: al guardar se vuelve a crear."; continue; }
      let actual = null;
      try { actual = (await obtener("/api/catalogo/archivo", { id, rel: p.rel })).contenido; } catch { /* */ }
      if (actual === null || actual === p.enDisco) continue;
      if (sucia(p)) p.nota = `${p.rel} cambió mientras lo editabas. Tus cambios siguen aquí; al guardar sustituyes la versión nueva.`;
      else p.texto = actual;
      p.enDisco = actual;
    }
    mostrarActiva();
    pintarPestanas();
    await refrescarErrores();
  }

  /** Selecciona el siguiente marcador {{…}} desde el cursor, como en la web. */
  function saltarAMarcador() {
    if (activa?.tipo !== "archivo") return avisar("Abre un archivo primero.");
    const area = editor.area;
    const patron = /\{\{[^{}]*\}\}/g;
    patron.lastIndex = area.selectionEnd || 0;
    let m = patron.exec(area.value);
    if (!m) { patron.lastIndex = 0; m = patron.exec(area.value); }
    if (!m) return avisar("Este archivo no tiene huecos {{…}} por rellenar.");
    area.focus();
    area.setSelectionRange(m.index, m.index + m[0].length);
  }

  // Montaje ------------------------------------------------------------------------------------------------------
  const botonGuardarTodo = boton("Guardar todo", () => guardarTodo(), { clase: "pequeno", icono: "check" });
  botonGuardarTodo.hidden = true;
  const ide = h("div", { class: "ide" });
  const ampliar = h("button", { type: "button", class: "boton pequeno fantasma ide-ampliar", "aria-pressed": "false", title: "Usar toda la ventana para editar", texto: "Ampliar" });
  ampliar.addEventListener("click", () => {
    const si = !ide.classList.contains("ampliado");
    ide.classList.toggle("ampliado", si);
    ampliar.textContent = si ? "Reducir" : "Ampliar";
    ampliar.setAttribute("aria-pressed", String(si));
    if (activa?.tipo === "archivo") editor.enfocar();
  });
  const verArbol = boton("Archivos", () => ide.classList.toggle("con-arbol"), { clase: "pequeno ide-ver-arbol", icono: "lista" });
  const lateral = h("aside", { class: "ide-arbol", "aria-label": "Árbol de archivos" },
    h("div", { class: "ide-arbol-cabeza" }, h("b", { texto: "Archivos" }),
      h("div", { class: "fila" },
        h("button", { type: "button", class: "boton fantasma pequeno solo-icono", title: "Archivo nuevo", "aria-label": "Archivo nuevo", onclick: () => nuevoArchivo().catch((e) => avisar(e.message, "mal")) }, icono("mas")),
        h("button", { type: "button", class: "boton fantasma pequeno solo-icono", title: "Carpeta nueva", "aria-label": "Carpeta nueva", onclick: () => nuevaCarpeta().catch((e) => avisar(e.message, "mal")) }, icono("carpeta")))),
    arbol);
  arbol.addEventListener("click", (e) => { if (e.target.closest(".es-archivo .ide-nodo-nombre")) ide.classList.remove("con-arbol"); });
  const principal = h("section", { class: "ide-principal" },
    barraPestanas,
    h("div", { class: "ide-herramientas fila" },
      verArbol,
      boton("Guardar", () => guardar(), { clase: "primario pequeno", icono: "check", titulo: "Ctrl+S" }),
      botonGuardarTodo,
      boton("Buscar", () => { if (activa?.tipo === "archivo") editor.buscar(); }, { clase: "pequeno fantasma", titulo: "Ctrl+F · reemplazar: Ctrl+H" }),
      boton("Siguiente hueco", () => saltarAMarcador(), { clase: "pequeno fantasma", titulo: "Selecciona el siguiente {{…}} por rellenar" }),
      h("span", { class: "espacio" }),
      selPrevia,
      ampliar),
    trabajo, estado, problemas);
  const divArbol = divisor(ide, "--ancho-arbol", "uxyn-editor-ancho-arbol", { minimo: 150, maximo: 480, inicial: 190 });
  ide.append(lateral, divArbol, principal);

  window.addEventListener("beforeunload", (e) => { if (ide.isConnected && haySinGuardar()) { e.preventDefault(); e.returnValue = ""; } });

  await cargarLista();
  const inicial = PREFERIDOS.find((p) => rutas.includes(p)) || rutas[0];
  await refrescarErrores();
  if (inicial) await abrirArchivo(inicial);
  else mostrarActiva();

  return {
    nodo: ide,
    area: editor.area,
    editor,
    rutaActual: () => (activa ? activa.rel : ""),
    abrirArchivo: (rel, opciones) => abrirArchivo(rel, opciones),
    abrirDiferencias,
    recargar,
    haySinGuardar,
    guardar,
  };
}
