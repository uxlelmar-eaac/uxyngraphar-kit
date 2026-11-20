// Taller de sistemas (ADR 0015, rediseño 1.5.29): el sistema se construye en una ruta guiada de cinco pasos.
//   Sin sistema abierto: «¿cómo empiezas?» (uxyn, tu material o desde cero) y tus sistemas para continuar.
//   Con sistema abierto: cabecera · ruta (Propósito → Reglas → Flujo y piezas → Probar → Entregar) · «ahora toca» ·
//   el trabajo del paso (guía + formulario o editor) · uxyn al lado. Una sola acción principal visible en cada momento.

import { catalogo, obtener, enviar } from "../api.js";
import { h, vaciar, boton, insignia, icono, avisar, avisarConAccion, dialogo, menu } from "../ui.js";
import { eliminarSistemas } from "./mis-sistemas.js";
import { visorBorradorWeb } from "./editor-archivos.js";
import { anotar } from "../registro.js";
import {
  editorSistema, crearSistema,
  descargarZipSistema, instalarEnProyecto, publicarEnMercado,
} from "./creador-editor.js";
import { chatAgente, sincronizarBorrador, panelSugerencias, filtrarPropuestasPendientes } from "./creador.js";
import { inicioConAgente } from "./creador-inicio.js";
import { describirMarcador, leerOrigen, guardarOrigen, moverOrigen, desdePendientes } from "./creador-estado.js";

const CLAVE = "uxyn-taller-zonas-v2";
const CLAVE_ARCHIVADOS = "uxyn-taller-mostrar-archivados";
export const ZONAS = [
  ["sistema", "Sistema"],
  ["agente", "uxyn"],
];

/** uxyn abierto por defecto al lado del sistema (se puede plegar y se recuerda). */
export function leerZonas() {
  const defecto = { sistema: true, agente: true };
  try {
    const guardado = JSON.parse(localStorage.getItem(CLAVE) || "{}");
    return { ...defecto, ...guardado, sistema: true };
  } catch {
    return defecto;
  }
}

function guardarZonas(zonas) {
  try { localStorage.setItem(CLAVE, JSON.stringify(zonas)); } catch { /* sin almacenamiento */ }
}

// ── La ruta de un sistema de gobernanza ─────────────────────────────────────────────────────────────────────────
const ARCHIVOS_PROPOSITO = ["sistema.json", "README.md"];
const ARCHIVOS_REGLAS = ["SISTEMA.md", "LIMITES.md", "PERMISOS.md", "MEMORIAS.md"];
const REGLA_PERMISOS = "En sistema.json, permisos.acciones.agente y solo_persona son listas de «scripts/….py [subcomando]» (o []); sin texto libre.";

/** Para qué sirve cada archivo, en una línea (lo que se ve en la guía de cada paso). */
export const ROL_ARCHIVO = {
  "sistema.json": "El manifiesto: título, qué resuelve, alcance, permisos y palabras que lo activan.",
  "README.md": "La presentación para quien lo instala: qué hace y cómo se usa.",
  "SISTEMA.md": "Qué garantiza, cuándo se usa, qué necesita y qué deja.",
  "LIMITES.md": "Las reglas duras, comprobables, y cuándo el agente debe parar y preguntar.",
  "PERMISOS.md": "Qué hace el agente solo y qué queda siempre para la persona.",
  "MEMORIAS.md": "Qué debe recordar entre conversaciones y qué no hace falta guardar.",
};

export const PASOS = [
  {
    id: "proposito", titulo: "Propósito", lema: "Qué resuelve y qué deja fuera",
    guia: "Todo sistema de gobernanza empieza por su razón de ser: el problema concreto que resuelve, lo que queda fuera "
      + "y cuándo debe activarse. Rellénalo en el formulario; el resto del sistema se apoya en esto.",
    pedido: "Completa el propósito del sistema: en sistema.json, título, descripción, alcance.problemas, fuera_de_alcance y "
      + "activación; y el README.md. Sustituye los marcadores {{…}} de esos archivos y déjalo en «Por revisar».",
  },
  {
    id: "reglas", titulo: "Reglas", lema: "Límites, permisos y memoria",
    guia: "El corazón del sistema: lo que el agente nunca hace, lo que solo decide la persona y lo que hay que recordar. "
      + "Escribe reglas concretas y comprobables («no aprueba un PR sin pruebas»), no buenas intenciones.",
    pedido: "Completa las reglas del sistema (SISTEMA.md, LIMITES.md, PERMISOS.md y MEMORIAS.md): reglas duras y "
      + `comprobables, cuándo parar y preguntar, y qué queda solo para la persona. Sustituye los marcadores {{…}}. ${REGLA_PERMISOS} `
      + "Déjalo en «Por revisar».",
  },
  {
    id: "piezas", titulo: "Flujo y piezas", lema: "Proceso, prompts, skills y plantillas",
    guia: "Cómo trabaja el agente con estas reglas: las fases del proceso, los prompts, las skills y las plantillas. "
      + "Activa solo las piezas que necesitas y rellena sus huecos.",
    pedido: "Completa el flujo y las piezas del sistema (proceso/, prompts/, skills/, plantillas, referencia, ejemplos y "
      + "pruebas) de forma coherente con SISTEMA.md y LIMITES.md. Sustituye los marcadores {{…}} y déjalo en «Por revisar».",
  },
  {
    id: "probar", titulo: "Probar", lema: "Valida y ponlo a prueba",
    guia: "Antes de usarlo de verdad: el validador comprueba que no falte nada y el simulador actúa como el agente que "
      + "seguirá el sistema. Pídele algo que debería rechazar y mira si lo rechaza.",
    pedido: "Revisa el sistema completo y dime, en lenguaje sencillo, qué le falta o qué mejorarías.",
  },
  {
    id: "entregar", titulo: "Entregar", lema: "Instálalo, guárdalo o publícalo",
    guia: "Lleva el sistema a donde trabajan tus agentes: instálalo en un proyecto, guárdalo en la web, descárgalo o "
      + "publícalo en el Mercado. Cada vez que lo mejores, sube su versión.",
    pedido: null,
  },
];
const PASO = Object.fromEntries(PASOS.map((p) => [p.id, p]));

/** ¿A qué paso pertenece un archivo? */
export function pasoDeArchivo(rel) {
  if (ARCHIVOS_PROPOSITO.includes(rel)) return "proposito";
  if (ARCHIVOS_REGLAS.includes(rel)) return "reglas";
  return "piezas";
}

/** El archivo al que se refiere un error del validador («LIMITES.md: …», «nomenclatura: README.md: …», «activacion: …»). */
export function archivoDeError(texto) {
  const t = String(texto).replace(/^nomenclatura:\s*/, "");
  const ruta = (t.match(/^([\w./<>-]+\.(?:json|md|py)):/) || [])[1];
  if (ruta) return ruta;
  if (/^(activaci[oó]n|t[ií]tulo|id\b|alcance|familia|permisos|descripci[oó]n|versi[oó]n|editor)/i.test(t)) return "sistema.json";
  return null;
}

/**
 * Estado de cada paso a partir de `/api/catalogo/pendientes` (+ propuestas y dónde está).
 * Devuelve { pasos: {id → {hecho, huecos, problemas, archivos: Map(rel → {huecos, linea, texto})}}, recomendado }.
 */
export function resolverPasos({ pendientes = null, propuestas = 0, enProyecto = [], publicado = false } = {}) {
  const p = desdePendientes(pendientes);
  const porPaso = Object.fromEntries(PASOS.map((x) => [x.id, { hecho: false, huecos: 0, problemas: [], archivos: new Map() }]));
  for (const m of p.marcadores) {
    const rel = m.archivo || m.file || "";
    const paso = porPaso[pasoDeArchivo(rel)];
    paso.huecos += 1;
    const previo = paso.archivos.get(rel);
    if (previo) previo.huecos += 1;
    else paso.archivos.set(rel, { huecos: 1, linea: m.linea || m.line || null, texto: describirMarcador(m) });
  }
  for (const e of p.errores) {
    const texto = String(e);
    if (/marcadores sin rellenar/.test(texto)) continue;   // ya contados como huecos
    const rel = archivoDeError(texto);
    const destino = rel ? porPaso[pasoDeArchivo(rel)] : porPaso.probar;
    destino.problemas.push({ rel: rel || null, texto });
    if (rel && !destino.archivos.has(rel)) destino.archivos.set(rel, { huecos: 0, linea: null, texto });
  }
  for (const id of ["proposito", "reglas", "piezas"]) {
    porPaso[id].hecho = pendientes != null && !porPaso[id].huecos && !porPaso[id].problemas.length;
  }
  porPaso.probar.hecho = pendientes != null && p.listo === true && !p.errores.length && !propuestas;
  porPaso.entregar.hecho = (enProyecto || []).length > 0 || !!publicado;
  const recomendado = ["proposito", "reglas", "piezas", "probar"].find((id) => !porPaso[id].hecho) || "entregar";
  return { pasos: porPaso, recomendado, siguiente: p.siguiente };
}

function textoEstadoPaso(id, e) {
  if (e.hecho) return id === "entregar" ? "Entregado" : "Listo";
  if (id === "probar") return e.problemas.length ? `${e.problemas.length} por corregir` : "Por validar";
  if (id === "entregar") return "Cuando quieras";
  const n = e.huecos + e.problemas.length;
  return n === 1 ? "1 hueco" : `${n} huecos`;
}

function insigniasDonde({ enEquipo, enProyecto, publicado, enWeb }) {
  const nodos = [];
  if (enEquipo) nodos.push(insignia("en este equipo", "bien"));
  if (enWeb) nodos.push(insignia("en la web", "acento"));
  if ((enProyecto || []).length) nodos.push(insignia(`instalado en ${enProyecto.length === 1 ? enProyecto[0] : `${enProyecto.length} proyectos`}`, "bien"));
  if (publicado) nodos.push(insignia("en el Mercado", "acento"));
  return nodos.length ? h("span", { class: "fila insignias-donde" }, nodos) : null;
}

export async function vista(params, { ir, recargar }) {
  const idAbierto = params.id || "";
  const zonas = leerZonas();
  let abierto = null;
  let propuestasPendientes = 0;
  let proponiendo = false;
  let chatApi = null;
  let chatNodo = null;
  let publicadoSesion = false;
  let chatMontado = false;
  let sugerenciasApi = null;
  let pagina = null;
  let pasoActual = PASO[params.paso] ? params.paso : null;
  let estadoPasos = null;
  let editorVisibleEnProposito = false;
  const cache = { cat: null, borradores: null, proyectos: null, sesion: null, mios: null };
  const zonaSalidaDetalle = h("div", { class: "taller-salida-detalle" });

  const zonaLista = h("section", { class: "taller-mis-sistemas", "aria-label": "Tus sistemas" });
  const zonaCabecera = h("div", { class: "taller-cabecera-sistema" });
  const zonaRuta = h("nav", { class: "taller-ruta", "aria-label": "Pasos del sistema", hidden: true });
  const zonaAhora = h("div", { class: "taller-ahora", role: "status" });
  const zonaGuia = h("div", { class: "taller-guia-hueco" });
  const zonaTrabajo = h("div", { class: "taller-trabajo" });
  const zonaSistema = h("section", { class: "zona-sistema", "aria-label": "Sistema" });
  const zonaAgente = h("aside", { class: "zona zona-agente", "aria-label": "uxyn", id: "zona-agente" });
  const huecoSugerencias = h("div", { class: "taller-por-revisar" });
  const cuerpo = h("div", { class: "taller", "data-modo": idAbierto ? "editar" : "crear" });
  // Tras el primer tick el nodo ya está en el DOM; si el usuario navega, isConnected pasa a false.
  const vivo = () => Boolean(pagina && pagina.isConnected);

  const interruptorAgente = h("button", {
    type: "button", class: "boton pequeno conmutador",
    "aria-pressed": String(zonas.agente), "aria-controls": "zona-agente",
    title: "Mostrar u ocultar uxyn",
  }, icono("chat"), "uxyn");
  interruptorAgente.addEventListener("click", async () => {
    zonas.agente = !zonas.agente;
    guardarZonas(zonas);
    aplicar();
    if (zonas.agente && !chatMontado) await montarChat();
  });

  function aplicar() {
    zonas.sistema = true;
    const conAgente = Boolean(idAbierto) && zonas.agente;
    zonaAgente.hidden = !conAgente;
    interruptorAgente.setAttribute("aria-pressed", String(zonas.agente));
    cuerpo.dataset.zonas = conAgente ? "sistema agente" : "sistema";
    cuerpo.dataset.modo = idAbierto ? "editar" : "crear";
  }

  const abrir = (id, conversacion) => ir("creador", id ? { id, ...(conversacion ? { conversacion } : {}) } : null);

  async function catLocal(forzar = false) {
    if (!cache.cat || forzar) cache.cat = await catalogo(true);
    return cache.cat;
  }
  /** ¿Hay sesión de la cuenta? Sin ella, los borradores web y uxyn no responden: no se les pregunta. */
  async function conSesion() {
    if (cache.sesion === null) {
      try { cache.sesion = (await obtener("/api/cuenta"))?.tipo === "sesion"; }
      catch { cache.sesion = false; }
    }
    return cache.sesion;
  }
  async function listaBorradores(forzar = false) {
    if (!cache.borradores || forzar) {
      if (!(await conSesion())) cache.borradores = [];
      else {
        try { cache.borradores = await obtener("/api/creador/borradores"); }
        catch { cache.borradores = []; }
      }
    }
    return cache.borradores || [];
  }
  async function listaProyectos(forzar = false) {
    if (!cache.proyectos || forzar) {
      cache.proyectos = await obtener("/api/proyectos").catch(() => []);
    }
    return cache.proyectos || [];
  }

  async function dondeEsta(id) {
    if (!id) return { enEquipo: false, enProyecto: [], publicado: false, enWeb: false };
    const local = (await catLocal()).some((m) => m.id === id);
    const proyectos = await listaProyectos();
    const enProyecto = proyectos
      .filter((p) => p.existe && (p.sistemas || []).includes(id))
      .map((p) => p.nombre);
    let web = false;
    let publicado = publicadoSesion;
    try {
      const borradores = await listaBorradores();
      const b = (borradores || []).find((x) => x.slug === id);
      web = !!b;
      if (b && (b.version_publicada || b.publicado)) publicado = true;
    } catch { /* sin sesión */ }
    return { enEquipo: local, enProyecto, publicado, enWeb: web };
  }

  async function datosPasos() {
    const donde = await dondeEsta(idAbierto);
    let pendientes = null;
    try { pendientes = await obtener("/api/catalogo/pendientes", { id: idAbierto }); } catch { /* sin validador local */ }
    try {
      const todas = (await conSesion()) ? await obtener("/api/agente/propuestas", { slug: idAbierto }) : [];
      propuestasPendientes = filtrarPropuestasPendientes(todas).length;
    } catch {
      propuestasPendientes = 0;
    }
    return { donde, ...resolverPasos({ pendientes, propuestas: propuestasPendientes, enProyecto: donde.enProyecto, publicado: donde.publicado }) };
  }

  // ── uxyn ──────────────────────────────────────────────────────────────────────────────────────────────────────
  async function abrirUxyn() {
    if (!zonas.agente) {
      zonas.agente = true;
      guardarZonas(zonas);
      aplicar();
    }
    if (!chatMontado) await montarChat();
  }
  /** Escribe un pedido en el chat de uxyn y lo envía (los cambios llegan a «Por revisar»). */
  async function pedirAUxyn(texto) {
    await abrirUxyn();
    chatNodo?.ponerModo?.("asistente");
    const area = zonaAgente.querySelector("textarea");
    if (!area) return avisar("Abre uxyn para pedírselo.", "mal");
    area.value = texto;
    area.dispatchEvent(new Event("input"));
    const enviarBtn = [...zonaAgente.querySelectorAll("button")].find((b) => /^Enviar$/i.test((b.textContent || "").trim()));
    if (enviarBtn) enviarBtn.click();
    else area.focus();
  }
  async function abrirSimulador() {
    await abrirUxyn();
    chatNodo?.ponerModo?.("simulador");
    zonaAgente.querySelector("textarea")?.focus();
  }
  function irAPorRevisar() {
    const panel = huecoSugerencias.querySelector(".sugerencias-panel");
    if (!panel) return;
    panel.hidden = false;
    try { panel.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* */ }
  }

  // ── Ruta, «ahora toca» y guía del paso ────────────────────────────────────────────────────────────────────────
  async function elegirPaso(id, { desdeArchivo = false } = {}) {
    if (!PASO[id]) return;
    const cambia = id !== pasoActual;
    pasoActual = id;
    if (id === "proposito" && desdeArchivo) editorVisibleEnProposito = true;
    try {
      const q = new URLSearchParams({ id: idAbierto, paso: id });
      history.replaceState(null, "", `#/creador?${q}`);
    } catch { /* */ }
    pintarRuta();
    pintarAhora();
    pintarGuia();
    if (cambia || desdeArchivo) await pintarTrabajo({ abrirPrimero: !desdeArchivo });
    if (cambia && !desdeArchivo) {
      try { zonaRuta.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* */ }
    }
  }

  function pintarRuta() {
    if (!estadoPasos) return;
    vaciar(zonaRuta, h("ol", { class: "ruta-pasos" }, PASOS.map((p, i) => {
      const e = estadoPasos.pasos[p.id];
      const activo = p.id === pasoActual;
      return h("li", {},
        h("button", {
          type: "button",
          class: `ruta-paso${activo ? " activo" : ""}${e.hecho ? " hecho" : ""}${p.id === estadoPasos.recomendado && !activo ? " recomendado" : ""}`,
          "aria-current": activo ? "step" : null,
          onclick: () => elegirPaso(p.id),
        },
          h("span", { class: "ruta-numero", "aria-hidden": "true" }, e.hecho ? icono("check") : String(i + 1)),
          h("span", { class: "ruta-texto" },
            h("b", { texto: p.titulo }),
            h("span", { class: "ruta-estado", texto: textoEstadoPaso(p.id, e) }))));
    })));
  }

  function pintarAhora() {
    if (!estadoPasos) return;
    const { pasos, recomendado } = estadoPasos;
    let tono = "";
    let titulo;
    let detalle;
    const acciones = [];
    if (proponiendo) {
      tono = "trabajando";
      titulo = "uxyn está trabajando";
      detalle = "Cuando termine, sus cambios aparecen en «Por revisar». Puedes seguir editando mientras tanto.";
    } else if (propuestasPendientes > 0) {
      tono = "revisar";
      titulo = propuestasPendientes === 1 ? "uxyn dejó 1 cambio por revisar" : `uxyn dejó ${propuestasPendientes} cambios por revisar`;
      detalle = "Míralos, corrígelos si hace falta y acéptalos o descártalos. Nada se aplica sin ti.";
      acciones.push(boton("Revisar cambios", irAPorRevisar, { clase: "primario", icono: "check" }));
    } else if (recomendado === "entregar") {
      tono = "listo";
      titulo = pasos.entregar.hecho ? "Tu sistema está en uso" : "Tu sistema está listo";
      detalle = pasos.entregar.hecho
        ? "Sigue afinándolo con uxyn; cuando lo mejores, sube la versión y actualiza tus proyectos."
        : "Valida sin errores. Instálalo en un proyecto, guárdalo en la web o publícalo.";
      if (pasoActual !== "entregar") acciones.push(boton("Ir a Entregar", () => elegirPaso("entregar"), { clase: "primario", icono: "flecha" }));
    } else {
      const paso = PASO[recomendado];
      const e = pasos[recomendado];
      const primero = [...e.archivos.entries()][0];
      titulo = `Paso ${PASOS.indexOf(paso) + 1} · ${paso.titulo}`;
      detalle = recomendado === "probar"
        ? (e.problemas[0]?.texto || "Todo está relleno: valida el sistema y pruébalo con el simulador.")
        : (primero ? primero[1].texto : paso.lema);
      if (pasoActual !== recomendado) {
        acciones.push(boton(`Ir a ${paso.titulo}`, () => elegirPaso(recomendado), { clase: "primario", icono: "flecha" }));
      } else if (primero && recomendado !== "probar") {
        // La guía de abajo ya ofrece «Que uxyn complete este paso»: aquí, ir directo al primer hueco.
        acciones.push(boton("Ir al primer hueco", () => abierto?.abrirArchivo(primero[0], primero[1].linea ? { linea: primero[1].linea } : undefined)
          .catch((x) => avisar(x.message || String(x), "mal")), { clase: "primario", icono: "editar" }));
      } else if (recomendado === "probar") {
        acciones.push(boton("Abrir el simulador", abrirSimulador, { clase: "primario", icono: "chat" }));
      }
    }
    vaciar(zonaAhora,
      h("div", { class: `ahora${tono ? ` ahora-${tono}` : ""}` },
        h("div", { class: "ahora-texto" },
          h("span", { class: "ahora-etiqueta", texto: "Ahora" }),
          h("b", { texto: titulo }),
          h("span", { class: "tenue", texto: detalle })),
        acciones.length ? h("div", { class: "fila ahora-acciones" }, acciones) : null));
    for (const b of zonaAhora.querySelectorAll("button")) if (proponiendo) b.disabled = true;
  }

  /** Lista de archivos de un paso con su estado y un botón para ir al primer hueco. */
  function listaArchivosPaso(id) {
    const e = estadoPasos.pasos[id];
    const fijos = id === "proposito" ? ARCHIVOS_PROPOSITO : id === "reglas" ? ARCHIVOS_REGLAS : [];
    const rutas = [...new Set([...fijos, ...e.archivos.keys()])];
    if (!rutas.length) {
      return h("p", { class: "guia-vacia tenue" }, icono("check"), " Todos los archivos de este paso están completos.");
    }
    return h("ul", { class: "guia-archivos" }, rutas.map((rel) => {
      const info = e.archivos.get(rel);
      const n = info ? info.huecos || 1 : 0;
      return h("li", { class: `guia-archivo${n ? "" : " completo"}` },
        h("span", { class: "guia-archivo-marca", "aria-hidden": "true" }, n ? String(n) : icono("check")),
        h("span", { class: "guia-archivo-texto" },
          h("code", { texto: rel }),
          h("span", { class: "tenue", texto: info?.texto && n ? info.texto : (ROL_ARCHIVO[rel] || "Completo.") })),
        boton(n ? "Rellenar" : "Abrir", () => abierto?.abrirArchivo(rel, info?.linea ? { linea: info.linea } : undefined)
          .catch((x) => avisar(x.message || String(x), "mal")), { clase: `pequeno${n ? "" : " fantasma"}` }));
    }));
  }

  function pintarGuia() {
    if (!estadoPasos || !abierto) return;
    const paso = PASO[pasoActual];
    const e = estadoPasos.pasos[pasoActual];
    const idx = PASOS.indexOf(paso);
    const siguiente = PASOS[idx + 1];
    const extra = [];
    if (pasoActual === "proposito" || pasoActual === "reglas" || pasoActual === "piezas") extra.push(listaArchivosPaso(pasoActual));
    const acciones = [];
    if (paso.pedido && pasoActual !== "probar" && !e.hecho) {
      acciones.push(boton("Que uxyn complete este paso", () => pedirAUxyn(paso.pedido), { clase: "pequeno", icono: "creador" }));
    }
    if (siguiente) acciones.push(boton(`Siguiente: ${siguiente.titulo}`, () => elegirPaso(siguiente.id), { clase: `pequeno${e.hecho ? " primario" : ""}`, icono: "flecha" }));
    vaciar(zonaGuia,
      h("section", { class: "tarjeta guia-paso", "aria-label": `Paso ${idx + 1}: ${paso.titulo}` },
        h("div", { class: "guia-cabecera" },
          h("span", { class: "guia-numero", texto: `Paso ${idx + 1} de ${PASOS.length}` }),
          h("h2", { texto: paso.titulo }),
          e.hecho ? insignia(textoEstadoPaso(pasoActual, e), "bien") : null),
        h("p", { class: "guia-texto", texto: paso.guia }),
        ...extra,
        acciones.length ? h("div", { class: "fila guia-acciones" }, acciones) : null));
  }

  // ── El trabajo de cada paso ──────────────────────────────────────────────────────────────────────────────────
  function tarjetaTrabajo(titulo, ...hijos) {
    return h("section", { class: "tarjeta trabajo-bloque" }, titulo ? h("h3", { texto: titulo }) : null, ...hijos);
  }

  function trabajoProbar() {
    const e = estadoPasos.pasos;
    const problemas = PASOS.flatMap((p) => estadoPasos.pasos[p.id].problemas);
    const huecos = ["proposito", "reglas", "piezas"].reduce((n, id) => n + e[id].huecos, 0);
    const validacion = h("div", { class: "pila" },
      !huecos && !problemas.length && e.probar.hecho
        ? h("div", { class: "banda bien" }, icono("check"), " El sistema valida: no le falta nada obligatorio.")
        : h("div", { class: "pila" },
          huecos ? h("p", { texto: `Quedan ${huecos} ${huecos === 1 ? "hueco" : "huecos"} por rellenar en los pasos anteriores.` }) : null,
          problemas.length ? h("ul", { class: "lista-problemas" }, problemas.map((p) => h("li", {},
            p.rel ? h("button", { type: "button", class: "enlace", texto: p.rel,
              onclick: () => abierto?.abrirArchivo(p.rel).catch((x) => avisar(x.message, "mal")) }) : null,
            p.rel ? " " : null, h("span", { texto: p.rel ? p.texto.slice(p.rel.length + 1).trim() : p.texto })))) : null,
          estadoPasos.siguiente ? h("p", { class: "tenue", texto: `Siguiente paso del validador: ${estadoPasos.siguiente}` }) : null),
      h("div", { class: "fila" },
        boton("Validar de nuevo", async () => {
          cache.cat = null;
          await pintarFranjas();
          pintarTrabajo();
          avisar("Validación actualizada");
        }, { clase: "pequeno", icono: "check" }),
        problemas.length || huecos ? boton("Que uxyn lo corrija", () => pedirAUxyn(PASOS[1].pedido.replace("Completa las reglas del sistema", "Corrige lo que falta para que el sistema valide, empezando por las reglas")), { clase: "pequeno", icono: "creador" }) : null));
    return [
      tarjetaTrabajo("Validación", validacion),
      tarjetaTrabajo("Simulador",
        h("p", { class: "tenue", texto: "uxyn hace de agente que sigue tu sistema. Pídele algo que debería rechazar (por ejemplo, saltarse una regla de LIMITES.md) y comprueba que se niega y explica por qué." }),
        h("div", { class: "fila" },
          boton("Abrir el simulador", abrirSimulador, { clase: "pequeno primario", icono: "chat" }),
          boton("Pedir una revisión a uxyn", () => pedirAUxyn(PASO.probar.pedido), { clase: "pequeno" }))),
    ];
  }

  async function trabajoEntregar() {
    const donde = await dondeEsta(idAbierto);
    const id = idAbierto;
    const idDeSync = (r) => r?.slug || r?.id || id;
    const traer = async () => {
      cache.cat = null;
      await sincronizarBorrador("bajar", id, zonaSalidaDetalle, async (r) => {
        await catLocal(true);
        await pintarFranjas();
        abrir(idDeSync(r));
      });
    };
    const subir = async () => {
      cache.borradores = null;
      await sincronizarBorrador("subir", id, zonaSalidaDetalle, async () => {
        await pintarFranjas();
        pintarTrabajo();
      });
    };
    const opcion = (ic, titulo, texto, accion, clase = "") => h("div", { class: `salida-opcion${clase ? ` ${clase}` : ""}` },
      h("span", { class: "salida-opcion-icono", "aria-hidden": "true" }, icono(ic)),
      h("div", { class: "salida-opcion-texto" }, h("b", { texto: titulo }), h("span", { class: "tenue", texto })),
      accion);
    const enProyecto = donde.enProyecto || [];
    const opciones = h("div", { class: "salida-opciones", "aria-label": "Salida" },
      opcion("proyectos", "Instalar en un proyecto",
        enProyecto.length ? `Ya está en ${enProyecto.join(", ")}. Puedes añadirlo a otros.` : "Tus agentes lo siguen en ese repositorio desde ya.",
        boton("Instalar en proyecto", async () => {
          const meta = (await catalogo(true)).find((m) => m.id === id);
          await instalarEnProyecto(id, meta?.titulo || id);
          cache.proyectos = null;   // la franja y la salida tienen que ver el proyecto recién instalado
          await pintarFranjas();
          pintarTrabajo();
        }, { clase: "pequeno primario" }), "principal"),
      opcion("subir", donde.enWeb ? "Sincronizar con la web" : "Guardar en la web",
        donde.enWeb ? "Sube los cambios de este equipo o trae los de la web." : "Una copia en tu cuenta para seguir desde otro equipo o con uxyn en la web.",
        h("div", { class: "fila" },
          donde.enEquipo || !donde.enWeb ? boton(donde.enWeb ? "Subir" : "Guardar en la web", subir, { clase: "pequeno", icono: "subir" }) : null,
          donde.enWeb ? boton("Traer", traer, { clase: "pequeno", icono: "descargar" }) : null)),
      opcion("descargar", "Descargar .zip", "Todos los archivos del sistema en un zip, para compartirlo o guardarlo.",
        boton("Descargar .zip", () => descargarZipSistema(id), { clase: "pequeno", icono: "descargar" })),
      opcion("catalogo", "Publicar en el Mercado",
        donde.publicado ? "Ya hay una versión publicada. Sube la versión antes de publicar otra." : "Una versión fija que cualquiera puede instalar.",
        boton("Publicar", () => {
          vaciar(zonaSalidaDetalle);
          // Solo cuenta como publicado cuando la publicación termina de verdad (no al abrir el aviso).
          publicarEnMercado(id, zonaSalidaDetalle, {
            alPublicar: async () => { publicadoSesion = true; await pintarFranjas(); pintarTrabajo(); },
          }).catch((e) => avisar(e.message || String(e), "mal"));
        }, { clase: "pequeno" })));
    const version = h("div", { class: "fila version-fila" },
      h("span", {}, "Versión ", h("b", { texto: abierto?.version?.textContent || "" })),
      h("span", { class: "espacio" }),
      boton("Arreglo pequeño", () => abierto.subirVersion("parche").then(() => pintarTrabajo()), { clase: "pequeno", titulo: "+ parche" }),
      boton("Mejora", () => abierto.subirVersion("menor").then(() => pintarTrabajo()), { clase: "pequeno", titulo: "+ menor" }),
      boton("Cambio grande", () => abierto.subirVersion("mayor").then(() => pintarTrabajo()), { clase: "pequeno", titulo: "+ mayor" }));
    const avisoNoListo = estadoPasos.recomendado !== "entregar"
      ? h("div", { class: "banda aviso" }, `Aún le falta algo (${PASO[estadoPasos.recomendado].titulo}). Puedes descargarlo o guardarlo, pero instálalo o publícalo cuando esté listo.`)
      : null;
    return [
      avisoNoListo,
      tarjetaTrabajo(null, opciones, zonaSalidaDetalle),
      tarjetaTrabajo("Versión", version,
        h("p", { class: "tenue", texto: "Sube la versión al terminar una mejora: los proyectos donde está instalado podrán actualizarse." })),
    ];
  }

  async function pintarTrabajo({ abrirPrimero = false } = {}) {
    if (!abierto || !estadoPasos) return;
    const s = abierto.secciones;
    const conEditor = pasoActual === "reglas" || pasoActual === "piezas" || (pasoActual === "proposito" && editorVisibleEnProposito);
    const bloques = [];
    if (pasoActual === "proposito") {
      bloques.push(tarjetaTrabajo("Lo básico", s.basico,
        editorVisibleEnProposito ? null : h("div", { class: "fila" },
          boton("Editar los archivos a mano", () => { editorVisibleEnProposito = true; pintarTrabajo({ abrirPrimero: true }); }, { clase: "pequeno fantasma", icono: "editar" }))));
    }
    if (pasoActual === "piezas") {
      bloques.push(h("details", { class: "tarjeta trabajo-bloque piezas-plegable" },
        h("summary", {}, h("b", { texto: "Elegir piezas" }), h("span", { class: "tenue", texto: " · activa solo las partes que necesita tu sistema" })),
        s.piezas));
    }
    if (pasoActual === "probar") bloques.push(...trabajoProbar());
    if (pasoActual === "entregar") bloques.push(...(await trabajoEntregar()));
    if (conEditor) {
      s.archivos.hidden = false;
      bloques.push(h("section", { class: "trabajo-editor", "aria-label": "Archivos del sistema" }, s.archivos));
    }
    for (const nodo of [s.basico, s.piezas]) nodo.hidden = false;
    vaciar(zonaTrabajo, ...bloques.filter(Boolean));
    // Al entrar en un paso con editor, se abre el primer archivo de ese paso (en su primer hueco).
    if (conEditor && abrirPrimero) {
      const actual = abierto.rutaActual?.();
      if (!actual || pasoDeArchivo(actual) !== pasoActual) {
        const e = estadoPasos.pasos[pasoActual];
        const [rel, info] = [...e.archivos.entries()][0]
          || [(pasoActual === "reglas" ? ARCHIVOS_REGLAS[0] : pasoActual === "proposito" ? ARCHIVOS_PROPOSITO[0] : null), null];
        if (rel) await abierto.abrirArchivo(rel, info?.linea ? { linea: info.linea } : undefined).catch(() => {});
      }
    }
  }

  // Nombre histórico: repinta cabecera, ruta, «ahora» y guía tras cualquier cambio (no el editor, para no perder el foco).
  async function pintarFranjas() {
    if (!idAbierto || !abierto) return;
    estadoPasos = await datosPasos();
    if (!pasoActual) pasoActual = estadoPasos.recomendado;
    pintarCabecera(estadoPasos.donde);
    pintarRuta();
    pintarAhora();
    pintarGuia();
  }

  function pintarCabecera(donde) {
    const meta = (cache.cat || []).find((m) => m.id === idAbierto) || {};
    const origen = leerOrigen(idAbierto);
    const conOrigen = origen.idea || (origen.adjuntos || []).length;
    const cambiar = h("button", { type: "button", class: "boton pequeno", "aria-haspopup": "menu", title: "Abrir otro sistema" },
      icono("carpeta"), "Sistemas", icono("abajo"));
    cambiar.addEventListener("click", async (ev) => {
      ev.stopPropagation();
      const mios = cache.mios || await obtener("/api/mis-sistemas").catch(() => ({ sistemas: [] }));
      const otros = (mios.sistemas || []).filter((s) => s.local && !s.archivado && s.estado !== "papelera" && s.id !== idAbierto)
        .sort((a, b) => (a.titulo || "").localeCompare(b.titulo || "", "es")).slice(0, 12);
      menu(cambiar, [
        { texto: "Nuevo sistema", icono: "mas", accion: () => abrir("") },
        otros.length ? "-" : null,
        ...otros.map((s) => ({ texto: s.titulo || s.id, icono: "editar", accion: () => abrir(s.id) })),
        "-",
        { texto: "Todos mis sistemas", icono: "lista", accion: () => abrir("") },
      ].filter(Boolean));
    });
    vaciar(zonaCabecera,
      h("div", { class: "cabecera-sistema-titulo" },
        h("a", { class: "volver-taller tenue", href: "#/creador", texto: "← Taller" }),
        h("h1", { texto: meta.titulo || idAbierto }),
        h("div", { class: "fila cabecera-sistema-meta" },
          h("code", { class: "tenue", texto: idAbierto }),
          meta.version ? h("span", { class: "tenue", texto: `v${meta.version}` }) : null,
          insigniasDonde(donde),
          conOrigen ? h("button", { type: "button", class: "enlace", texto: "Idea de origen", onclick: verOrigen }) : null)),
      h("div", { class: "fila cabecera-sistema-acciones" }, cambiar, interruptorAgente));
  }

  async function verOrigen() {
    const o = leerOrigen(idAbierto || "_nuevo");
    await dialogo({
      titulo: "Idea de origen",
      cancelar: "Cerrar",
      contenido: h("div", { class: "pila" },
        o.idea ? h("div", {}, h("b", { texto: "Idea" }), h("p", { texto: o.idea })) : h("p", { class: "tenue", texto: "Sin idea guardada." }),
        (o.adjuntos || []).length
          ? h("div", {}, h("b", { texto: "Adjuntos" }), h("ul", {}, o.adjuntos.map((n) => h("li", { texto: n }))))
          : h("p", { class: "tenue", texto: "Sin adjuntos." })),
      acciones: [],
    });
  }

  // ── Tus sistemas (pantalla de inicio del Taller) ─────────────────────────────────────────────────────────────
  async function pintarLista() {
    // La MISMA lista que «Mis sistemas» (GET /api/mis-sistemas): catálogo local, borradores web, papelera y archivados.
    await catLocal(true);
    const mios = await obtener("/api/mis-sistemas");
    cache.mios = mios;
    if (idAbierto) return;
    const items = (mios.sistemas || []).map((s) => ({ ...s, instalado: s.instalado || [], errores: s.errores || [] }))
      .sort((a, b) => (a.titulo || "").localeCompare(b.titulo || "", "es"));
    const oculto = (m) => m.archivado || m.estado === "papelera";
    let mostrarArchivados = false;
    try { mostrarArchivados = localStorage.getItem(CLAVE_ARCHIVADOS) === "1"; } catch { /* */ }

    const filtro = h("input", { type: "search", placeholder: "Buscar…", "aria-label": "Buscar sistema" });
    const lista = h("ul", { class: "lista-sistemas-taller" });
    const conArchivados = h("input", { type: "checkbox", checked: mostrarArchivados });
    const cuantosArchivados = items.filter(oculto).length;
    conArchivados.addEventListener("change", () => {
      mostrarArchivados = conArchivados.checked;
      try { localStorage.setItem(CLAVE_ARCHIVADOS, mostrarArchivados ? "1" : "0"); } catch { /* */ }
      pintar();
    });
    const archivar = async (m, si) => {
      await enviar("/api/mis-sistemas/archivar", { ids: [m.id], archivar: si });
      await pintarLista();
      const deshacer = async () => { await enviar("/api/mis-sistemas/archivar", { ids: [m.id], archivar: !si }); await pintarLista(); };
      avisarConAccion(si ? `«${m.titulo}» archivado: ya no sale en el Taller (no se borró nada)` : `«${m.titulo}» de vuelta en el Taller`, "Deshacer", deshacer);
    };
    const restaurarDePapelera = async (m) => {
      await enviar("/api/mis-sistemas/restaurar", { entrada: m.entrada });
      cache.cat = null;
      avisar(`«${m.titulo}» restaurado de la papelera`);
      await pintarLista();
    };
    const opciones = (m) => [
      { texto: m.estado === "web" ? "Abrir (traer para editar)" : "Abrir", icono: "editar", accion: () => abrir(m.id) },
      m.estado === "papelera" ? { texto: "Restaurar de la papelera", icono: "deshacer", accion: () => restaurarDePapelera(m).catch((e) => avisar(e.message, "mal")) } : null,
      m.archivado
        ? { texto: "Volver al Taller", icono: "deshacer", accion: () => archivar(m, false).catch((e) => avisar(e.message, "mal")) }
        : { texto: m.local ? "Archivar (ocultar del Taller)" : "Olvidar en el Taller (solo aquí)", icono: "lista",
          accion: () => archivar(m, true).catch((e) => avisar(e.message, "mal")) },
      m.local ? "-" : null,
      m.local ? { texto: "Eliminar…", icono: "basura", peligro: true, accion: async () => {
        const hechos = await eliminarSistemas([{ id: m.id, titulo: m.titulo }], {
          instaladoEn: () => m.instalado, web: m.web ? [{ slug: m.id, publicado: m.publicado }] : [],
          alCambiar: async () => { cache.cat = null; await pintarLista(); },
        }).catch((e) => { avisar(e.message, "mal"); return null; });
        return hechos;
      } } : null,
    ];
    const estadoDe = (m) => {
      if (m.estado === "papelera") return insignia("en la papelera", "mal");
      if (m.estado === "web") return insignia("solo en la web", "acento");
      if ((m.errores || []).length) return insignia("a medias", "nota");
      if (m.publicado) return insignia("en el Mercado", "acento");
      if (m.instalado.length) return insignia("en uso", "bien");
      return insignia("listo para entregar", "bien");
    };
    const pintar = () => {
      const t = filtro.value.trim().toLowerCase();
      const visibles = items.filter((m) => (!t || `${m.titulo} ${m.id}`.toLowerCase().includes(t))
        && (mostrarArchivados || !oculto(m)));
      vaciar(lista, visibles.map((m) => h("li", { class: "tarjeta-sistema" + (m.archivado ? " archivado" : "") },
        h("a", { href: `#/creador?id=${encodeURIComponent(m.id)}`, class: "tarjeta-sistema-enlace" },
          h("b", { texto: m.titulo || m.id }),
          h("span", { class: "tenue", texto: m.id }),
          h("span", { class: "fila" },
            estadoDe(m),
            m.local && m.web ? insignia("web", "acento") : null,
            m.archivado ? insignia("archivado", "nota") : null),
          h("span", { class: "tarjeta-sistema-seguir", texto: m.estado === "web" ? "Traer y seguir →" : "Seguir →" })),
        (() => {
          const b = h("button", { type: "button", class: "boton fantasma pequeno solo-icono menu-sistema", "aria-haspopup": "menu", title: `Opciones de ${m.titulo}`, "aria-label": `Opciones de ${m.titulo}` }, icono("puntos"));
          b.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); menu(b, opciones(m)); });
          return b;
        })())));
      if (!visibles.length) {
        lista.append(h("li", { class: "tenue", texto: items.length ? (t ? "Nada coincide." : "Todos tus sistemas están archivados o en la papelera.") : "Aún no tienes sistemas: empieza arriba." }));
      }
    };
    filtro.addEventListener("input", pintar);
    pintar();
    vaciar(zonaLista,
      h("div", { class: "fila separada taller-mis-sistemas-cabecera" },
        h("h2", { texto: "Continúa con un sistema" }),
        items.length > 4 ? filtro : null),
      lista,
      h("div", { class: "fila separada" },
        cuantosArchivados ? h("label", { class: "fila tenue mostrar-archivados" }, conArchivados, ` Mostrar archivados y papelera (${cuantosArchivados})`) : h("span", {}),
        h("a", { class: "tenue enlace-mis-sistemas", href: "#/mis-sistemas", texto: "Organizar en Mis sistemas →" })));
  }

  async function nuevoConAsistente(modo = "esqueleto") {
    const r = await crearSistema(modo);
    if (!r) return;
    cache.cat = null;
    if (typeof r === "string") abrir(r);
    else abrir(r.id, r.conversacion);
  }

  /** Pantalla de inicio: la ruta en un vistazo y tres formas de empezar. */
  function pintarInicio() {
    const inicio = inicioConAgente({
      cabecera: false,
      alAntesDeCrear: async ({ idea, adjuntos }) => {
        guardarOrigen("_nuevo", { idea, adjuntos });
        proponiendo = true;
      },
      alDespuesDeCrear: async () => { proponiendo = false; },
      alCrear: async (id, r) => {
        moverOrigen("_nuevo", id);
        cache.cat = null;
        await catLocal(true);
        abrir(id, r.conversacion);
      },
    });
    const alternativa = (ic, titulo, texto, accion) => h("button", { type: "button", class: "empezar-alternativa", onclick: accion },
      h("span", { class: "empezar-icono", "aria-hidden": "true" }, icono(ic)),
      h("span", { class: "empezar-alternativa-texto" }, h("b", { texto: titulo }), h("span", { class: "tenue", texto })));
    vaciar(zonaSistema,
      h("section", { class: "taller-empezar", "aria-label": "Nuevo sistema" },
        h("div", { class: "tarjeta empezar-uxyn" },
          h("div", { class: "empezar-cabecera" },
            h("span", { class: "empezar-icono", "aria-hidden": "true" }, icono("creador")),
            h("div", {},
              h("h2", { texto: "Cuéntale a uxyn qué deben seguir tus agentes" }),
              h("p", { class: "tenue", texto: "Describe la idea o adjunta tu material. uxyn arma el sistema completo y te deja cada cambio para que lo aceptes." }))),
          inicio.nodo),
        h("div", { class: "empezar-otras" },
          h("span", { class: "empezar-o tenue", texto: "o empieza tú" }),
          alternativa("subirArchivo", "Subir tu material", "Un .zip, archivos o una carpeta con tus reglas actuales. No se pierde nada.", () => nuevoConAsistente("importar")),
          alternativa("mas", "Empezar desde cero", "Pones nombre y tipo; sale el esqueleto completo para rellenar paso a paso.", () => nuevoConAsistente("esqueleto")),
          h("button", { type: "button", class: "enlace tenue empezar-spec", texto: "¿Ya tienes la especificación JSON del generador?", onclick: () => nuevoConAsistente("spec") }))),
      h("section", { class: "taller-ruta-resumen", "aria-label": "Cómo se construye un sistema" },
        h("h2", { texto: "Así se construye un sistema" }),
        h("ol", { class: "ruta-resumen" }, PASOS.map((p, i) => h("li", {},
          h("span", { class: "ruta-numero", "aria-hidden": "true", texto: String(i + 1) }),
          h("span", { class: "ruta-texto" }, h("b", { texto: p.titulo }), h("span", { class: "tenue", texto: p.lema })))))),
      zonaLista);
  }

  async function pintarSistema() {
    if (!idAbierto) {
      pintarInicio();
      return;
    }
    let meta = (await catLocal()).find((m) => m.id === idAbierto);
    if (!meta) {
      await new Promise((r) => setTimeout(r, 400));
      meta = (await catLocal(true)).find((m) => m.id === idAbierto);
    }
    if (!meta) {
      anotar({
        nivel: "aviso", origen: "creador",
        titulo: `«${idAbierto}» no está en el catálogo local`,
        datos: { id: idAbierto },
      });
      abierto = null;
      const donde = await dondeEsta(idAbierto);
      let enPapelera = null;
      try { enPapelera = (await obtener("/api/mis-sistemas/papelera")).find((e) => e.id === idAbierto && !e.choca) || null; } catch { /* */ }
      const traer = async () => {
        await sincronizarBorrador("bajar", idAbierto, zonaSalidaDetalle, async (r) => {
          cache.cat = null;
          await catLocal(true);
          abrir(r?.slug || r?.id || idAbierto);
        });
      };
      vaciar(zonaCabecera,
        h("div", { class: "cabecera-sistema-titulo" },
          h("a", { class: "volver-taller tenue", href: "#/creador", texto: "← Taller" }),
          h("h1", { texto: idAbierto })),
        h("div", { class: "fila cabecera-sistema-acciones" }, interruptorAgente));
      vaciar(zonaSistema,
        h("div", { class: "tarjeta pila solo-web" },
          h("h2", { texto: donde.enWeb ? `«${idAbierto}» está en la web, no en este equipo` : `«${idAbierto}» no está en este equipo` }),
          h("p", { texto: donde.enWeb
            ? "Abajo ves TODOS sus archivos tal como están en la web. Para editarlos aquí, tráelo: se copia a tu catálogo local y la web no cambia."
            : "No está en tu catálogo local." }),
          h("div", { class: "fila" },
            donde.enWeb ? boton("Traer de la web para editar", traer, { clase: "primario", icono: "descargar" }) : null,
            enPapelera ? boton("Restaurar de la papelera", async () => {
              await enviar("/api/mis-sistemas/restaurar", { entrada: enPapelera.entrada });
              cache.cat = null;
              await catLocal(true);
              avisar(`«${idAbierto}» restaurado de la papelera`);
              abrir(idAbierto);
            }, { clase: donde.enWeb ? "" : "primario", icono: "deshacer" }) : null,
            boton("Mejorar con uxyn", abrirUxyn, { icono: "chat" }),
            boton("Nuevo sistema", () => abrir(""), { clase: "fantasma" })),
          enPapelera ? h("p", { class: "tenue", texto: `Lo eliminaste de este equipo el ${String(enPapelera.eliminado || "").slice(0, 16).replace("T", " a las ")}; sigue en la papelera.` }) : null,
          zonaSalidaDetalle),
        huecoSugerencias,
        donde.enWeb ? await visorBorradorWeb(idAbierto, { alTraer: traer }) : null);
      return;
    }
    abierto = await editorSistema(idAbierto, {
      alCambiar: async () => {
        cache.cat = null;
        await catLocal(true);
        await pintarFranjas();
      },
      // Abrir un archivo (desde la guía, «Por revisar» o el editor) lleva al paso que lo trabaja.
      alPedirSeccion: async (seccion, rel) => {
        if (seccion !== "archivos") return;
        const paso = rel ? pasoDeArchivo(rel) : (pasoActual === "proposito" || pasoActual === "reglas" ? pasoActual : "piezas");
        const enEditor = pasoActual === "reglas" || pasoActual === "piezas" || (pasoActual === "proposito" && editorVisibleEnProposito);
        if (paso !== pasoActual || !enEditor) await elegirPaso(paso, { desdeArchivo: true });
        await new Promise((r) => requestAnimationFrame(r));
        zonaTrabajo.querySelector(".trabajo-editor")?.scrollIntoView({ behavior: "smooth", block: "start" });
      },
    });
    if (pagina && !pagina.isConnected) return;
    zonaRuta.hidden = false;
    vaciar(zonaSistema, zonaAhora, huecoSugerencias, zonaGuia, zonaTrabajo);
    // «Abrir en el Taller» desde la estructura de Mis sistemas: entra en el paso de ese archivo y lo abre.
    const pedido = typeof params.archivo === "string" && params.archivo ? params.archivo : null;
    if (pedido) {
      pasoActual = pasoDeArchivo(pedido);
      if (pasoActual === "proposito") editorVisibleEnProposito = true;
    }
    await pintarFranjas();
    await pintarTrabajo({ abrirPrimero: !pedido });
    if (pedido) await abierto.abrirArchivo(pedido).catch(() => {});
  }

  async function montarSugerencias() {
    if (!idAbierto) {
      vaciar(huecoSugerencias);
      sugerenciasApi = null;
      return;
    }
    const local = (await catLocal()).some((m) => m.id === idAbierto);
    sugerenciasApi = panelSugerencias(idAbierto, {
      soloWeb: !local,
      alAbrirEnEditor: local ? (a, p) => abierto?.abrirDiferencias?.(a.ruta, a.antes || "", a.despues || "", `Sugerencia #${p.id}`) : null,
      alCambiar: async () => {
        cache.cat = null;
        if (!local && (await catLocal(true)).some((m) => m.id === idAbierto)) {
          // Al aceptar, el borrador se trae a este equipo: ya se puede editar.
          await pintarSistema();
          await montarSugerencias();
        } else if (abierto?.recargar) await abierto.recargar();
        await pintarFranjas();
      },
    });
    vaciar(huecoSugerencias, sugerenciasApi.nodo);
    await sugerenciasApi.refrescar();
  }

  async function montarChat() {
    if (chatMontado || !vivo() || !idAbierto) return;
    chatMontado = true;
    if (!sugerenciasApi) await montarSugerencias();
    chatNodo = await chatAgente(
      () => (abierto ? { id: idAbierto, rutaActual: abierto.rutaActual, textarea: abierto.textarea, recargar: abierto.recargar } : null),
      {
        conversacionInicial: Number(params.conversacion) || null,
        slugInicial: idAbierto || null,
        sugerencias: sugerenciasApi,
        alProponer: async () => {
          proponiendo = false;
          await pintarFranjas();
        },
        alEmpezarTurno: async () => {
          proponiendo = true;
          pintarAhora();
        },
        alTerminarTurno: async () => {
          proponiendo = false;
          if (abierto?.recargar) await abierto.recargar({ notificar: false });
          await pintarFranjas();
        },
      });
    chatApi = { pedir: pedirAUxyn };
    const plegar = boton("", () => interruptorAgente.click(), { clase: "pequeno fantasma solo-icono", icono: "cerrar", titulo: "Ocultar uxyn" });
    plegar.setAttribute("aria-label", "Ocultar uxyn");
    vaciar(zonaAgente,
      h("div", { class: "fila separada zona-agente-cabecera" }, h("h2", {}, icono("chat"), " uxyn"), plegar),
      chatNodo);
  }

  async function pintarAgente() {
    if (!idAbierto) return;
    await montarSugerencias();
    if (zonas.agente) await montarChat();
    else {
      chatMontado = false;
      chatApi = { pedir: pedirAUxyn };
    }
  }

  aplicar();
  cuerpo.append(zonaSistema, zonaAgente);
  const sigueCargando = (zona) => zona.childElementCount === 1 && zona.firstElementChild?.dataset.cargando === "1";
  vaciar(zonaLista, h("p", { class: "tenue", "data-cargando": "1", texto: "Cargando sistemas…" }));
  vaciar(zonaSistema, h("p", { class: "tenue", "data-cargando": "1", texto: idAbierto ? "Cargando sistema…" : "Preparando…" }));
  vaciar(zonaAgente, h("p", { class: "tenue", texto: "uxyn" }));

  pagina = h("div", { class: "taller-pagina" },
    idAbierto
      ? h("div", { class: "taller-arriba" }, zonaCabecera, zonaRuta)
      : h("header", { class: "cabecera taller-cabecera-inicio" },
        h("div", {},
          h("h1", { texto: "Taller" }),
          h("p", { texto: "Crea y mejora sistemas de gobernanza para tus agentes de IA, paso a paso." }))),
    cuerpo);

  anotar({
    nivel: "info", origen: "creador",
    titulo: idAbierto ? `Taller abierto: ${idAbierto}` : "Taller abierto (nuevo sistema)",
    datos: { id: idAbierto || null, conversacion: params.conversacion || null },
  });

  // Rellena en segundo plano: la UI deja de mostrar el «Cargando…» global al instante.
  void (async () => {
    await new Promise((r) => queueMicrotask(r));
    if (!vivo()) return;
    try {
      if (!idAbierto) pintarInicio();
      await Promise.all([pintarLista(), idAbierto ? pintarSistema() : null]);
      if (!vivo()) return;
      await pintarAgente();
    } catch (e) {
      if (!vivo()) return;
      const mensaje = e.message || String(e);
      avisar(mensaje, "mal");
      // Ninguna zona se queda en «Cargando…» para siempre: si la carga falló, lo dice y deja reintentar.
      for (const zona of [zonaLista, zonaSistema]) {
        if (!sigueCargando(zona)) continue;
        vaciar(zona, h("div", { class: "banda mal", role: "alert" },
          h("span", { texto: `No se pudo cargar: ${mensaje} ` }),
          h("button", { type: "button", class: "secundario", texto: "Reintentar", onclick: () => recargar?.() })));
      }
    }
  })();

  return pagina;
}
