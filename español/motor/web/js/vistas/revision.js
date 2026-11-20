// Revisión de archivos: un sistema a pantalla completa para leerlo y analizarlo. Árbol de carpetas a la izquierda,
// el archivo en el centro y tus notas y resaltados a la derecha. Al seleccionar texto aparece un menú con tres
// herramientas: Mejorar (la IA reescribe ese fragmento ahí mismo y tú lo aceptas), Añadir nota y Resaltar. Las notas
// y los resaltados quedan guardados y uxyn los usa como guía cuando se lo pides. Igual que la web
// (uxyngraphar-frontend, creator/components/SystemReviewPage.tsx).

import { obtener, enviar } from "../api.js";
import { h, vaciar, boton, avisar, icono, insignia } from "../ui.js";
import { arbolDeRutas } from "./editor-archivos.js";
import { CAPAS, QUE_ES, capaDe, contarCapas, contarEstructura } from "./estructura-sistema.js";
import { tramos, ubicar, pedidoParaUxyn } from "./anotaciones-texto.js";
import { selectorIA, vistaDiferencias } from "./creador.js";

const ES_TEXTO = /\.(md|json|py|txt|ya?ml|toml|csv|sh)$/i;
const plural = (n, uno, varios) => `${n} ${n === 1 ? uno : varios}`;

/** Posición en el texto del archivo de un punto (nodo, desplazamiento) dentro del documento pintado. */
function posicionEn(doc, nodo, desplazamiento) {
  const recorrido = document.createTreeWalker(doc, NodeFilter.SHOW_TEXT);
  let total = 0;
  for (let t = recorrido.nextNode(); t; t = recorrido.nextNode()) {
    if (t === nodo) return total + desplazamiento;
    total += t.textContent.length;
  }
  // El punto cae en un elemento (no en un texto): cuenta el texto que hay antes de él.
  const r = document.createRange();
  r.selectNodeContents(doc);
  r.setEnd(nodo, desplazamiento);
  return r.toString().length;
}

export async function vista(params, { ir }) {
  const id = String(params.id || "");
  if (!id) throw new Error("Falta el sistema que revisar.");
  const cat = await obtener("/api/catalogo").catch(() => []);
  const meta = (cat || []).find((m) => m.id === id) || { id, titulo: id };
  let rutas = await obtener("/api/catalogo/archivos", { id });
  let anotaciones = await obtener("/api/anotaciones", { id }).catch(() => []);
  const plegadas = new Set();
  let actual = params.archivo && rutas.includes(params.archivo) ? params.archivo
    : (["README.md", "SISTEMA.md", "sistema.json"].find((r) => rutas.includes(r)) || rutas[0] || null);
  let texto = "";
  let filtro = "abiertas";
  const { sel: selIA, elegido } = await selectorIA();
  selIA.classList.add("revision-ia");

  // ── Zonas ──────────────────────────────────────────────────────────────────────────────────────────────────
  const arbol = h("ul", { class: "estructura-arbol", "aria-label": "Carpetas y archivos del sistema" });
  const cabezaDoc = h("div", { class: "revision-doc-cabeza" });
  const doc = h("div", { class: "revision-doc", "aria-label": "Contenido del archivo", tabindex: "0" });
  const lado = h("div", { class: "revision-notas-lista" });
  const pestanas = h("div", { class: "segmentado", role: "group", "aria-label": "Qué anotaciones ver" });
  const contador = h("span", { class: "insignia" });
  const menuSel = h("div", { class: "revision-menu", role: "toolbar", "aria-label": "Herramientas para el texto elegido", hidden: true });
  const panelFlotante = h("div", { class: "revision-flotante", hidden: true });
  const botonUxyn = boton("Pedir a uxyn que use mis notas", pedirAUxyn, { clase: "primario pequeno", icono: "chat",
    titulo: "Abre el Taller y uxyn mejora el sistema guiándose por tus notas y resaltados abiertos" });

  // ── Árbol (con la capa de uxyngraphar de cada ruta) ────────────────────────────────────────────────────────
  const titulo = (rel) => `${CAPAS[capaDe(rel)].nombre} · ${QUE_ES[rel] || rel}`;
  function leyenda() {
    const n = contarCapas(rutas);
    return h("ul", { class: "capas-leyenda", "aria-label": "Capas del sistema" },
      ...Object.entries(CAPAS).filter(([c]) => n[c]).map(([c, { nombre, que }]) =>
        h("li", { class: `capa-${c}`, title: que }, h("span", { class: "capa-punto", "aria-hidden": "true" }),
          h("span", { texto: nombre }), h("span", { class: "tenue", texto: String(n[c]) }))));
  }

  // ── Árbol ──────────────────────────────────────────────────────────────────────────────────────────────────
  function pintarArbol() {
    const items = [];
    const total = (n) => n.archivos.length + [...n.carpetas.values()].reduce((s, c) => s + total(c), 0);
    const notasDe = (rel) => anotaciones.filter((a) => a.estado === "abierta" && (a.archivo === rel || a.archivo.startsWith(`${rel}/`))).length;
    const recorrer = (nodo, prefijo, nivel) => {
      for (const rel of [...nodo.archivos].sort((a, b) => a.localeCompare(b))) {
        const n = notasDe(rel);
        items.push(h("li", {}, h("button", {
          type: "button", class: `estructura-nodo es-archivo capa-${capaDe(rel)}${rel === actual ? " activo" : ""}`, style: `--nivel:${nivel}`,
          "aria-current": rel === actual ? "true" : null, title: titulo(rel), onclick: () => abrir(rel),
        }, h("span", { class: "estructura-flecha" }), icono("lista"), h("span", { class: "estructura-nombre", texto: rel.split("/").pop() }),
        n ? h("span", { class: "contador contador-notas", texto: String(n), title: plural(n, "anotación abierta", "anotaciones abiertas") }) : null)));
      }
      for (const nombre of [...nodo.carpetas.keys()].sort((a, b) => a.localeCompare(b))) {
        const rel = prefijo ? `${prefijo}/${nombre}` : nombre;
        const hijo = nodo.carpetas.get(nombre);
        const plegada = plegadas.has(rel);
        items.push(h("li", {}, h("button", {
          type: "button", class: `estructura-nodo es-carpeta capa-${capaDe(rel)}`, style: `--nivel:${nivel}`, "aria-expanded": String(!plegada),
          title: titulo(rel), onclick: () => { if (plegada) plegadas.delete(rel); else plegadas.add(rel); pintarArbol(); },
        }, h("span", { class: "estructura-flecha", texto: plegada ? "▸" : "▾" }), icono("carpeta"),
        h("span", { class: "estructura-nombre", texto: `${nombre}/` }), h("span", { class: "contador", texto: String(total(hijo)) }))));
        if (!plegada) recorrer(hijo, rel, nivel + 1);
      }
    };
    recorrer(arbolDeRutas(rutas), "", 0);
    vaciar(arbol, items);
  }

  // ── Documento ──────────────────────────────────────────────────────────────────────────────────────────────
  async function abrir(rel) {
    actual = rel;
    cerrarMenus();
    try { history.replaceState(null, "", `#/revision?${new URLSearchParams({ id, archivo: rel })}`); } catch { /* */ }
    pintarArbol();
    const capa = capaDe(rel);
    vaciar(cabezaDoc, h("span", { class: `capa-insignia capa-${capa}`, title: CAPAS[capa].que, texto: CAPAS[capa].nombre }),
      h("code", { texto: rel }), QUE_ES[rel] ? h("span", { class: "tenue", texto: QUE_ES[rel] }) : null);
    if (!ES_TEXTO.test(rel)) {
      texto = "";
      vaciar(doc, h("p", { class: "tenue", texto: "Este archivo no es de texto: ábrelo en el Taller para verlo." }));
      return;
    }
    vaciar(doc, h("p", { class: "tenue", texto: "Cargando…" }));
    texto = String((await obtener("/api/catalogo/archivo", { id, rel }))?.contenido ?? "");
    pintarDoc();
    doc.scrollTop = 0;
  }

  function pintarDoc() {
    const delArchivo = anotaciones.filter((a) => a.archivo === actual && a.estado === "abierta");
    vaciar(doc, texto ? tramos(texto, delArchivo).map((t) => (t.anotacion
      ? h("mark", { class: `marca marca-${t.anotacion.tipo}`, "data-anotacion": t.anotacion.id,
        title: t.anotacion.tipo === "nota" ? `Nota: ${t.anotacion.nota}` : "Resaltado",
        onclick: () => enfocarNota(t.anotacion.id) }, t.texto)
      : document.createTextNode(t.texto)))
      : h("p", { class: "tenue", texto: "Archivo vacío." }));
  }

  // ── Selección y menú flotante ──────────────────────────────────────────────────────────────────────────────
  let eleccion = null;   // {inicio, fin, cita}
  function cerrarMenus() {
    menuSel.hidden = true;
    panelFlotante.hidden = true;
    eleccion = null;
  }
  function colocar(nodo, rect) {
    const caja = pagina.getBoundingClientRect();
    nodo.style.top = `${Math.max(rect.top - caja.top - 46, 4)}px`;
    nodo.style.left = `${Math.min(Math.max(rect.left - caja.left, 4), caja.width - 360)}px`;
  }
  function alSoltar() {
    const s = window.getSelection();
    if (!s || s.isCollapsed || !s.rangeCount || !texto) { if (panelFlotante.hidden) menuSel.hidden = true; return; }
    const r = s.getRangeAt(0);
    if (!doc.contains(r.startContainer) || !doc.contains(r.endContainer)) return;
    const inicio = posicionEn(doc, r.startContainer, r.startOffset);
    const fin = posicionEn(doc, r.endContainer, r.endOffset);
    const cita = texto.slice(inicio, fin);
    if (!cita.trim()) return;
    eleccion = { inicio, fin, cita };
    panelFlotante.hidden = true;
    menuSel.hidden = false;
    colocar(menuSel, r.getBoundingClientRect());
    menuSel.querySelector("button")?.focus({ preventScroll: true });
  }
  doc.addEventListener("mouseup", () => setTimeout(alSoltar, 0));
  doc.addEventListener("keyup", (e) => { if (e.shiftKey) alSoltar(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && pagina.isConnected) cerrarMenus(); });

  async function crearAnotacion(tipo, nota = "") {
    if (!eleccion) return;
    const a = await enviar("/api/anotaciones/crear", { id, archivo: actual, tipo, cita: eleccion.cita, inicio: eleccion.inicio, fin: eleccion.fin, nota });
    anotaciones.push(a);
    window.getSelection()?.removeAllRanges();
    cerrarMenus();
    pintarTodo();
    avisar(tipo === "nota" ? "Nota guardada" : "Resaltado guardado");
  }

  function abrirFlotante(...hijos) {
    const rect = menuSel.getBoundingClientRect();
    menuSel.hidden = true;
    vaciar(panelFlotante, h("div", { class: "revision-flotante-cita", texto: `«${eleccion.cita.length > 180 ? `${eleccion.cita.slice(0, 177)}…` : eleccion.cita}»` }), ...hijos);
    panelFlotante.hidden = false;
    colocar(panelFlotante, { top: rect.top + 46, left: rect.left });
    panelFlotante.querySelector("textarea, input")?.focus();
  }

  function herramientaNota() {
    const area = h("textarea", { rows: 3, class: "breve", "aria-label": "Tu nota", placeholder: "Qué quieres que cambie o qué falta aquí…" });
    abrirFlotante(area, h("div", { class: "fila" },
      boton("Guardar nota", async () => {
        if (!area.value.trim()) { avisar("Escribe la nota primero", "mal"); return; }
        await crearAnotacion("nota", area.value);
      }, { clase: "primario pequeno" }),
      boton("Cancelar", cerrarMenus, { clase: "fantasma pequeno" })));
  }

  function herramientaMejorar() {
    const pedido = h("input", { type: "text", "aria-label": "Qué mejorar (opcional)", placeholder: "Qué mejorar (opcional): más concreto, añade un ejemplo…" });
    const zona = h("div", { class: "pila" });
    const elegida = { ...eleccion };
    abrirFlotante(pedido, zona, h("div", { class: "fila" },
      boton("Mejorar con IA", async () => {
        vaciar(zona, h("p", { class: "tenue", texto: "La IA está reescribiendo el fragmento…" }));
        const r = await enviar("/api/creador/mejorar-fragmento", { id, rel: actual, fragmento: elegida.cita, instruccion: pedido.value.trim(), ...elegido() });
        vaciar(zona, h("div", { class: "fila separada" }, h("b", { texto: "Propuesta" }), r.modelo ? insignia(r.modelo) : null),
          vistaDiferencias(elegida.cita, r.propuesta),
          h("div", { class: "fila" },
            boton("Aplicar en el archivo", async () => {
              const [ini, fin] = ubicar(texto, elegida) || [];
              if (ini === undefined) { avisar("El fragmento cambió mientras tanto: vuelve a seleccionarlo.", "mal"); return; }
              const nuevo = texto.slice(0, ini) + r.propuesta + texto.slice(fin);
              const g = await enviar("/api/catalogo/archivo", { id, rel: actual, contenido: nuevo });
              texto = nuevo;
              cerrarMenus();
              pintarDoc();
              avisar(g?.errores?.length ? `Aplicado. El validador avisa: ${g.errores[0]}` : "Fragmento mejorado y guardado");
            }, { clase: "primario pequeno", icono: "check" }),
            boton("Descartar", cerrarMenus, { clase: "fantasma pequeno" })));
      }, { clase: "primario pequeno", icono: "creador" }),
      boton("Cancelar", cerrarMenus, { clase: "fantasma pequeno" })));
  }

  vaciar(menuSel,
    boton("Mejorar", herramientaMejorar, { clase: "pequeno", icono: "creador", titulo: "La IA reescribe este fragmento y tú decides si lo aplicas" }),
    boton("Añadir nota", herramientaNota, { clase: "pequeno", icono: "editar", titulo: "Deja una nota para ti y para uxyn" }),
    boton("Resaltar", () => crearAnotacion("resaltado"), { clase: "pequeno", icono: "etiqueta", titulo: "Marca este fragmento para revisarlo" }));

  // ── Lista de anotaciones ───────────────────────────────────────────────────────────────────────────────────
  function enfocarNota(aid) {
    const el = lado.querySelector(`[data-anotacion="${aid}"]`);
    if (!el) return;
    el.scrollIntoView({ block: "nearest", behavior: "smooth" });
    el.classList.add("destacada");
    setTimeout(() => el.classList.remove("destacada"), 1200);
  }
  async function irA(a) {
    if (a.archivo !== actual) await abrir(a.archivo);
    const marca = doc.querySelector(`[data-anotacion="${a.id}"]`);
    if (marca) {
      marca.scrollIntoView({ block: "center", behavior: "smooth" });
      marca.classList.add("destacada");
      setTimeout(() => marca.classList.remove("destacada"), 1200);
    } else avisar("Ese fragmento ya no está en el archivo (cambió después de anotarlo).", "mal");
  }
  async function cambiarEstado(a, estado) {
    Object.assign(a, await enviar("/api/anotaciones/cambiar", { id, anotacion: a.id, estado }));
    pintarTodo();
  }
  async function borrarNota(a) {
    await enviar("/api/anotaciones/borrar", { id, anotacion: a.id });
    anotaciones = anotaciones.filter((x) => x.id !== a.id);
    pintarTodo();
  }
  function pintarLado() {
    const abiertas = anotaciones.filter((a) => a.estado === "abierta");
    const lista = anotaciones.filter((a) => (filtro === "abiertas" ? a.estado === "abierta" : a.estado === "resuelta"));
    contador.textContent = plural(abiertas.length, "abierta", "abiertas");
    botonUxyn.disabled = !abiertas.length;
    vaciar(pestanas, [["abiertas", `Abiertas (${abiertas.length})`], ["resueltas", `Resueltas (${anotaciones.length - abiertas.length})`]].map(([v, t]) =>
      h("button", { type: "button", class: "segmento", "aria-pressed": String(filtro === v), onclick: () => { filtro = v; pintarLado(); } }, t)));
    if (!lista.length) {
      vaciar(lado, h("p", { class: "tenue revision-vacio", texto: filtro === "abiertas"
        ? "Selecciona texto del archivo para mejorarlo, añadir una nota o resaltarlo. Tus notas y resaltados aparecen aquí y uxyn los usa como guía."
        : "Aún no has resuelto ninguna." }));
      return;
    }
    vaciar(lado, lista.map((a) => {
      const perdida = a.archivo === actual && texto && !ubicar(texto, a);
      return h("article", { class: `revision-nota revision-nota-${a.tipo}`, "data-anotacion": a.id },
        h("div", { class: "fila separada" },
          h("span", { class: "revision-nota-tipo" }, icono(a.tipo === "nota" ? "editar" : "etiqueta"), a.tipo === "nota" ? "Nota" : "Resaltado"),
          h("button", { type: "button", class: "enlace revision-nota-archivo", texto: a.archivo, onclick: () => irA(a) })),
        h("button", { type: "button", class: "revision-nota-cita", onclick: () => irA(a), texto: `«${a.cita.length > 160 ? `${a.cita.slice(0, 157)}…` : a.cita}»` }),
        a.nota ? h("p", { class: "revision-nota-texto", texto: a.nota }) : null,
        perdida ? h("p", { class: "aviso-linea", texto: "El texto cambió: ya no se encuentra en el archivo." }) : null,
        h("div", { class: "fila" },
          a.estado === "abierta"
            ? boton("Resolver", () => cambiarEstado(a, "resuelta"), { clase: "pequeno", icono: "check" })
            : boton("Reabrir", () => cambiarEstado(a, "abierta"), { clase: "pequeno", icono: "deshacer" }),
          boton("Borrar", () => borrarNota(a), { clase: "fantasma pequeno", icono: "basura" })));
    }));
  }

  function pintarTodo() {
    pintarArbol();
    pintarDoc();
    pintarLado();
  }

  // ── uxyn ───────────────────────────────────────────────────────────────────────────────────────────────────
  async function pedirAUxyn() {
    if (!pedidoParaUxyn(anotaciones)) { avisar("No tienes notas ni resaltados abiertos.", "mal"); return; }
    ir("creador", { id, pedir: "notas" });
  }

  // ── Página ─────────────────────────────────────────────────────────────────────────────────────────────────
  const { carpetas, archivos } = contarEstructura(rutas);
  const pagina = h("div", { class: "revision" },
    h("header", { class: "revision-cabeza" },
      h("div", { class: "revision-titulo" },
        h("a", { class: "volver-taller tenue", href: "#/mis-sistemas", texto: "← Mis sistemas" }),
        h("h1", { texto: meta.titulo || id }),
        h("span", { class: "tenue", texto: `${id} · ${plural(carpetas, "carpeta", "carpetas")} · ${plural(archivos, "archivo", "archivos")}` })),
      h("div", { class: "fila revision-acciones" },
        h("div", { class: "chat-pie" }, h("label", { class: "ia-selector" }, h("span", { texto: "IA" }), selIA)),
        botonUxyn,
        boton("Abrir en el Taller", () => ir("creador", actual ? { id, archivo: actual } : { id }), { clase: "pequeno", icono: "editar" }))),
    h("div", { class: "revision-cuerpo" },
      h("nav", { class: "revision-arbol", "aria-label": "Archivos" }, leyenda(), arbol),
      h("section", { class: "revision-centro", "aria-label": "Archivo" }, cabezaDoc, doc,
        h("p", { class: "tenue revision-pista", texto: "Selecciona texto para Mejorar, Añadir nota o Resaltar." })),
      h("aside", { class: "revision-notas", "aria-label": "Notas y resaltados" },
        h("div", { class: "fila separada" }, h("h2", { texto: "Notas y resaltados" }), contador),
        pestanas, lado)),
    menuSel, panelFlotante);

  pagina.addEventListener("mousedown", (e) => {
    if (!menuSel.contains(e.target) && !panelFlotante.contains(e.target) && !doc.contains(e.target)) cerrarMenus();
  });

  pintarLado();
  if (actual) await abrir(actual);
  else vaciar(doc, h("p", { class: "tenue", texto: "Este sistema no tiene archivos." }));
  return pagina;
}
