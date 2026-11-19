// Taller de sistemas (ADR 0015): el objeto es el sistema; uxyn es secundario.
// Layout: origen · ciclo · salida · archivos/editor · uxyn en columna estrecha.

import { catalogo, obtener, enviar } from "../api.js";
import { h, vaciar, boton, cabecera, insignia, icono, avisar, avisarConAccion, dialogo, menu } from "../ui.js";
import { eliminarSistemas } from "./mis-sistemas.js";
import { anotar } from "../registro.js";
import {
  editorSistema, crearSistema,
  descargarZipSistema, instalarEnProyecto, publicarEnMercado,
} from "./creador-editor.js";
import { chatAgente, sincronizarBorrador, panelSugerencias, filtrarPropuestasPendientes } from "./creador.js";
import { inicioConAgente } from "./creador-inicio.js";
import {
  armarPromptCompletar, resolverEstado, leerOrigen, guardarOrigen, moverOrigen, resumenOrigen,
  desdePendientes,
} from "./creador-estado.js";

const CLAVE = "uxyn-taller-zonas-v1";
const CLAVE_ARCHIVADOS = "uxyn-taller-mostrar-archivados";
export const ZONAS = [
  ["lista", "Lista"],
  ["sistema", "Sistema"],
  ["agente", "uxyn"],
];

/** Archivos + sistema por defecto; uxyn como cajón (apagado al abrir). */
export function leerZonas() {
  const defecto = { lista: true, sistema: true, agente: false };
  try {
    const guardado = JSON.parse(localStorage.getItem(CLAVE) || "{}");
    const zonas = { ...defecto, ...guardado, sistema: true };
    return Object.values(zonas).some(Boolean) ? zonas : defecto;
  } catch {
    return defecto;
  }
}

function guardarZonas(zonas) {
  try { localStorage.setItem(CLAVE, JSON.stringify(zonas)); } catch { /* sin almacenamiento */ }
}

function franjaOrigen(origen, { alVer } = {}) {
  if (origen.vacio) {
    return h("section", { class: "taller-origen vacio", "aria-label": "Origen" },
      h("span", { class: "taller-origen-etiqueta", texto: "Origen" }),
      h("p", { class: "tenue", texto: origen.resumen }));
  }
  return h("section", { class: "taller-origen", "aria-label": "Origen" },
    h("div", { class: "taller-origen-main" },
      h("span", { class: "taller-origen-etiqueta", texto: "Origen" }),
      h("p", { class: "taller-origen-resumen", texto: origen.resumen })),
    boton("Ver contexto", () => alVer && alVer(), { clase: "pequeno fantasma" }));
}

function carrilCiclo(ciclo, estado) {
  return h("section", { class: "taller-ciclo", "aria-label": "Ciclo del sistema" },
    h("ol", { class: "ciclo-pasos" }, ciclo.pasos.map((p) => h("li", {
      class: `ciclo-paso${p.activo ? " activo" : ""}${p.hecho ? " hecho" : ""}`,
      "aria-current": p.activo ? "step" : null,
    }, p.etiqueta))),
    h("div", { class: "ciclo-tecnico" },
      insignia(estado.etiqueta, estado.id === "listo" ? "bien" : estado.id === "por_revisar" || estado.id === "falta_nucleo" ? "nota" : ""),
      h("p", { class: "tenue", texto: estado.detalle }),
      ciclo.siguienteCiclo ? h("p", { class: "tenue", texto: `Siguiente en el ciclo: ${ciclo.siguienteCiclo}` }) : null));
}

function insigniasDonde({ enEquipo, enProyecto, publicado, enWeb }) {
  const nodos = [];
  if (enWeb) nodos.push(insignia("web", "acento"));
  if (enEquipo) nodos.push(insignia("equipo", "bien"));
  if ((enProyecto || []).length) nodos.push(insignia("instalado", "bien"));
  if (publicado) nodos.push(insignia("mercado", "acento"));
  return nodos.length ? h("span", { class: "fila insignias-donde" }, nodos) : null;
}

function plantillaNuevo({ proponiendo, idea, nombreInput }) {
  return h("div", { class: "plantilla-nuevo", "aria-label": "Nuevo sistema" },
    h("h2", { texto: "Nuevo sistema" }),
    h("p", { class: "tenue", texto: proponiendo
      ? "uxyn está armando el núcleo. Mientras tanto puedes nombrar el sistema y ver el esqueleto."
      : "Cuenta tu idea o adjunta un zip a la derecha. Aquí verás archivos, origen y salida en cuanto exista el borrador." }),
    h("label", { class: "campo" }, "Nombre", nombreInput),
    h("div", { class: "esqueleto-archivos", "aria-label": "Primeras piezas" },
      ["sistema.json", "README.md", "SISTEMA.md", "LIMITES.md", "PERMISOS.md", "MEMORIAS.md"].map((f) =>
        h("div", { class: "esqueleto-archivo", texto: f }))),
    idea ? h("p", { class: "tenue", texto: `Idea: ${resumenOrigen({ idea }).idea}` }) : null);
}

export async function vista(params, { ir, recargar }) {
  const idAbierto = params.id || "";
  const zonas = leerZonas();
  let abierto = null;
  let propuestasPendientes = 0;
  let proponiendo = false;
  let chatApi = null;
  let enWeb = false;
  let publicadoSesion = false;
  let chatMontado = false;
  let sugerenciasApi = null;
  let pagina = null;
  const cache = { cat: null, borradores: null, proyectos: null, sesion: null };
  const zonaSalidaDetalle = h("div", { class: "taller-salida-detalle" });

  const marco = h("div", { class: "taller-puesto" });
  const zonaOrigen = h("div", { class: "taller-franja-origen" });
  const zonaCiclo = h("div", { class: "taller-franja-ciclo" });
  const zonaSalida = h("div", { class: "taller-salida", "aria-label": "Salida" });
  const cuerpo = h("div", { class: "taller", "data-modo": idAbierto ? "editar" : "crear" });
  const zonaLista = h("section", { class: "zona zona-lista", "aria-label": "Sistemas del taller" });
  const zonaSistema = h("section", { class: "zona zona-sistema", "aria-label": "Sistema" });
  const zonaAgente = h("section", { class: "zona zona-agente", "aria-label": "uxyn" });
  const nodos = { lista: zonaLista, sistema: zonaSistema, agente: zonaAgente };
  const huecoSugerencias = h("div", { class: "taller-por-revisar" });
  // Tras el primer tick el nodo ya está en el DOM; si el usuario navega, isConnected pasa a false.
  const vivo = () => Boolean(pagina && pagina.isConnected);

  const interruptorLista = h("button", {
    type: "button", class: "boton pequeno conmutador",
    "aria-pressed": String(zonas.lista), "aria-controls": "zona-lista",
    title: "Mostrar u ocultar la lista",
  }, "Lista");
  const interruptorAgente = h("button", {
    type: "button", class: "boton pequeno conmutador",
    "aria-pressed": String(zonas.agente), "aria-controls": "zona-agente",
    title: "Mostrar u ocultar uxyn",
  }, "uxyn");
  interruptorLista.addEventListener("click", () => { zonas.lista = !zonas.lista; guardarZonas(zonas); aplicar(); });
  interruptorAgente.addEventListener("click", async () => {
    zonas.agente = !zonas.agente;
    guardarZonas(zonas);
    aplicar();
    if (zonas.agente && !chatMontado) await montarChat();
  });

  function aplicar() {
    zonas.sistema = true;
    for (const [clave] of ZONAS) {
      nodos[clave].id = `zona-${clave}`;
      nodos[clave].hidden = !zonas[clave];
    }
    interruptorLista.setAttribute("aria-pressed", String(zonas.lista));
    interruptorAgente.setAttribute("aria-pressed", String(zonas.agente));
    cuerpo.dataset.zonas = ZONAS.filter(([k]) => zonas[k]).map(([k]) => k).join(" ");
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
    enWeb = web;
    return { enEquipo: local, enProyecto, publicado, enWeb: web };
  }

  async function datosEstado() {
    const origen = leerOrigen(idAbierto || "_nuevo");
    if (!idAbierto) {
      return resolverEstado({ tieneSistema: false, proponiendo, origen });
    }
    const donde = await dondeEsta(idAbierto);
    let pendientes = desdePendientes(null);
    try {
      pendientes = desdePendientes(await obtener("/api/catalogo/pendientes", { id: idAbierto }));
    } catch { /* sin validador local */ }
    try {
      const todas = (await conSesion()) ? await obtener("/api/agente/propuestas", { slug: idAbierto }) : [];
      propuestasPendientes = filtrarPropuestasPendientes(todas).length;
    } catch {
      propuestasPendientes = 0;
    }
    return resolverEstado({
      tieneSistema: true,
      proponiendo,
      propuestas: propuestasPendientes,
      errores: pendientes.errores,
      marcadores: pendientes.marcadores,
      siguiente: pendientes.siguiente,
      listo: pendientes.listo,
      valido: pendientes.valido,
      // El catálogo local no expone al_dia; no fingimos «Validar» por desfase.
      alDia: true,
      enEquipo: donde.enEquipo,
      enProyecto: donde.enProyecto,
      publicado: donde.publicado,
      origen,
    });
  }

  function enfocarSalidaPublicar() {
    zonaSalidaDetalle.hidden = false;
    zonaSalida.scrollIntoView({ behavior: "smooth", block: "nearest" });
    if (idAbierto) {
      vaciar(zonaSalidaDetalle);
      // Solo cuenta como publicado cuando la publicación termina de verdad (no al abrir el aviso).
      publicarEnMercado(idAbierto, zonaSalidaDetalle, {
        alPublicar: async () => {
          publicadoSesion = true;
          await pintarFranjas();
          await pintarLista();
        },
      }).catch((e) => avisar(e.message || String(e), "mal"));
    }
  }

  async function pintarFranjas() {
    const estado = await datosEstado();
    vaciar(zonaOrigen, franjaOrigen(estado.origen, {
      alVer: async () => {
        const o = leerOrigen(idAbierto || "_nuevo");
        await dialogo({
          titulo: "Contexto de origen",
          cancelar: "Cerrar",
          contenido: h("div", { class: "pila" },
            o.idea ? h("div", {}, h("b", { texto: "Idea" }), h("p", { texto: o.idea })) : h("p", { class: "tenue", texto: "Sin idea guardada." }),
            (o.adjuntos || []).length
              ? h("div", {}, h("b", { texto: "Adjuntos" }), h("ul", {}, o.adjuntos.map((n) => h("li", { texto: n }))))
              : h("p", { class: "tenue", texto: "Sin adjuntos." })),
          acciones: [],
        });
      },
    }));

    vaciar(zonaCiclo, carrilCiclo(estado.ciclo, estado), (() => {
      if (!estado.cta || estado.accion === "ninguna") return null;
      const b = boton(estado.cta, async () => {
        if (estado.accion === "crear") {
          zonas.agente = true;
          guardarZonas(zonas);
          aplicar();
          if (!chatMontado) await montarChat();
          zonaAgente.querySelector("textarea")?.focus();
          return;
        }
        if (estado.accion === "revisar") {
          const panel = huecoSugerencias.querySelector(".sugerencias-panel");
          if (panel) {
            panel.hidden = false;
            try { panel.scrollIntoView({ behavior: "smooth", block: "nearest" }); } catch { /* */ }
          }
          return;
        }
        if (estado.accion === "validar") {
          cache.cat = null;
          if (abierto?.recargar) await abierto.recargar({ notificar: false });
          await pintarFranjas();
          await pintarLista();
          avisar("Validación actualizada");
          return;
        }
        if (estado.accion === "completar") {
          if (estado.archivo && abierto?.abrirArchivo) {
            try { await abierto.abrirArchivo(estado.archivo); } catch { /* */ }
          }
          zonas.agente = true;
          guardarZonas(zonas);
          aplicar();
          if (!chatMontado) await montarChat();
          if (chatApi?.pedirCompletar) await chatApi.pedirCompletar();
          else avisar("Escribe a uxyn: «Completa el núcleo».", "mal");
          return;
        }
        if (estado.accion === "abrir_salida") {
          zonaSalida.scrollIntoView({ behavior: "smooth", block: "nearest" });
          try { zonaSalida.focus(); } catch { /* */ }
        }
      }, { clase: "pequeno primario" });
      if (proponiendo) b.disabled = true;
      return h("div", { class: "fila", style: "margin-top:8px" }, b);
    })());

    await pintarSalida();
  }

  async function pintarSalida() {
    const id = idAbierto;
    const donde = id ? await dondeEsta(id) : { enEquipo: false, enProyecto: [], publicado: false, enWeb: false };
    const syncBtns = [];
    const idDeSync = (r) => r?.slug || r?.id || id;
    const traer = async () => {
      if (!id) return avisar("Abre un sistema primero.", "mal");
      cache.cat = null;
      await sincronizarBorrador("bajar", id, zonaSalidaDetalle, async (r) => {
        await catLocal(true);
        await pintarLista();
        await pintarFranjas();
        abrir(idDeSync(r));
      });
    };
    const subir = async () => {
      if (!id) return avisar("Abre un sistema primero.", "mal");
      cache.borradores = null;
      await sincronizarBorrador("subir", id, zonaSalidaDetalle, async () => {
        await pintarLista();
        await pintarFranjas();
      });
    };
    if (donde.enWeb) {
      syncBtns.push(boton("Traer", traer, { clase: "pequeno", icono: "descargar", titulo: "Bajar el borrador de la web a este equipo" }));
    }
    if (donde.enEquipo || !donde.enWeb) {
      syncBtns.push(boton(donde.enWeb ? "Subir" : "Guardar en la web", subir, {
        clase: "pequeno", icono: "subir", titulo: "Subir el borrador de este equipo a la web",
      }));
    }
    const acciones = h("div", { class: "fila taller-salida-acciones" },
      boton("Descargar .zip", async () => {
        if (!id) return avisar("Abre un sistema primero.", "mal");
        await descargarZipSistema(id);
      }, { clase: "pequeno", icono: "descargar", titulo: "Empaqueta los archivos del sistema" }),
      ...syncBtns,
      boton("Instalar en proyecto", async () => {
        if (!id) return avisar("Abre un sistema primero.", "mal");
        const meta = (await catalogo(true)).find((m) => m.id === id);
        await instalarEnProyecto(id, meta?.titulo || id);
        cache.proyectos = null;   // la franja y la salida tienen que ver el proyecto recién instalado
        await pintarLista();
        await pintarFranjas();
      }, { clase: "pequeno" }),
      boton("Publicar", () => {
        if (!id) return avisar("Abre un sistema primero.", "mal");
        enfocarSalidaPublicar();
      }, { clase: "pequeno primario" }));
    if (!id) [...acciones.querySelectorAll("button")].forEach((b) => { b.disabled = true; });

    vaciar(zonaSalida,
      h("div", { class: "fila separada taller-salida-barra" },
        h("div", { class: "fila" },
          h("span", { class: "taller-salida-etiqueta", texto: "Salida" }),
          insigniasDonde(donde)),
        acciones),
      zonaSalidaDetalle);
  }

  async function pintarLista() {
    const cat = await catLocal(true);
    const borradores = await listaBorradores(true);
    const proyectos = await listaProyectos(true);
    const instalados = new Map();
    for (const p of proyectos) {
      for (const sid of p.sistemas || []) {
        if (!instalados.has(sid)) instalados.set(sid, []);
        instalados.get(sid).push(p.nombre);
      }
    }
    const porId = new Map();
    for (const m of cat) {
      porId.set(m.id, {
        id: m.id,
        titulo: m.titulo || m.id,
        local: true,
        web: false,
        instalado: instalados.get(m.id) || [],
        familia: m.familia,
        version: m.version,
        errores: m.errores || [],
      });
    }
    for (const b of borradores || []) {
      const prev = porId.get(b.slug) || {
        id: b.slug, titulo: b.titulo || b.slug, local: !!b.en_equipo, web: true,
        instalado: instalados.get(b.slug) || [], familia: "", version: "", errores: [],
        publicado: !!(b.version_publicada || b.publicado),
      };
      prev.web = true;
      prev.local = prev.local || !!b.en_equipo;
      prev.titulo = prev.titulo || b.titulo || b.slug;
      if (b.version_publicada || b.publicado) prev.publicado = true;
      porId.set(b.slug, prev);
    }
    let archivados = [];
    try { archivados = await obtener("/api/mis-sistemas/archivados"); } catch { /* sin archivados */ }
    for (const m of porId.values()) m.archivado = archivados.includes(m.id);
    const items = [...porId.values()].sort((a, b) => (a.titulo || "").localeCompare(b.titulo || "", "es"));
    let mostrarArchivados = false;
    try { mostrarArchivados = localStorage.getItem(CLAVE_ARCHIVADOS) === "1"; } catch { /* */ }

    const filtro = h("input", { type: "search", placeholder: "Buscar…", "aria-label": "Buscar sistema" });
    const lista = h("ul", { class: "lista lista-sistemas" });
    const conArchivados = h("input", { type: "checkbox", checked: mostrarArchivados });
    const cuantosArchivados = items.filter((m) => m.archivado).length;
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
    const opciones = (m) => [
      { texto: "Abrir", icono: "editar", accion: () => abrir(m.id) },
      m.archivado
        ? { texto: "Volver al Taller", icono: "deshacer", accion: () => archivar(m, false).catch((e) => avisar(e.message, "mal")) }
        : { texto: m.local ? "Archivar (ocultar del Taller)" : "Olvidar en el Taller (solo aquí)", icono: "lista",
          accion: () => archivar(m, true).catch((e) => avisar(e.message, "mal")) },
      m.local ? "-" : null,
      m.local ? { texto: "Eliminar…", icono: "basura", peligro: true, accion: async () => {
        const hechos = await eliminarSistemas([{ id: m.id, titulo: m.titulo }], {
          instaladoEn: () => m.instalado, web: m.web ? [{ slug: m.id, publicado: m.publicado }] : [],
          alCambiar: async () => { cache.cat = null; await pintarLista(); await pintarFranjas(); if (m.id === idAbierto) await pintarSistema(); },
        }).catch((e) => { avisar(e.message, "mal"); return null; });
        return hechos;
      } } : null,
    ];
    const pintar = () => {
      const t = filtro.value.trim().toLowerCase();
      const visibles = items.filter((m) => (!t || `${m.titulo} ${m.id}`.toLowerCase().includes(t))
        && (mostrarArchivados || !m.archivado || m.id === idAbierto));
      vaciar(lista, visibles.map((m) => h("li", { class: "elemento-con-menu" + (m.archivado ? " archivado" : "") },
        h("a", {
          href: `#/creador?id=${encodeURIComponent(m.id)}`,
          class: "elemento-sistema" + (m.id === idAbierto ? " activo" : ""),
          "aria-current": m.id === idAbierto ? "page" : null,
        },
          h("b", { texto: m.titulo || m.id }),
          h("span", { class: "tenue", texto: m.id }),
          h("span", { class: "fila" },
            m.web ? insignia("web", "acento") : null,
            m.local ? insignia("equipo", "bien") : null,
            m.instalado.length ? insignia("instalado", "bien") : null,
            m.publicado ? insignia("mercado", "acento") : null,
            m.archivado ? insignia("archivado", "nota") : null,
            (m.errores || []).length ? insignia("le falta algo", "nota") : null)),
        (() => {
          const b = h("button", { type: "button", class: "boton fantasma pequeno solo-icono menu-sistema", "aria-haspopup": "menu", title: `Opciones de ${m.titulo}`, "aria-label": `Opciones de ${m.titulo}` }, icono("puntos"));
          b.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); menu(b, opciones(m)); });
          return b;
        })())));
      if (!visibles.length) {
        lista.append(h("li", { class: "tenue", texto: items.length ? (t ? "Nada coincide." : "Todos tus sistemas están archivados.") : "Aún no hay sistemas en el taller." }));
      }
    };
    filtro.addEventListener("input", pintar);
    pintar();
    vaciar(zonaLista,
      h("div", { class: "fila separada" },
        h("h2", { texto: "Taller" }),
        boton("Nuevo", () => abrir(""), { clase: "pequeno", icono: "mas", titulo: "Nuevo sistema" })),
      filtro, lista,
      cuantosArchivados ? h("label", { class: "fila tenue mostrar-archivados" }, conArchivados, ` Mostrar archivados (${cuantosArchivados})`) : null,
      boton("Plantilla sin uxyn", async () => {
        const r = await crearSistema();
        if (!r) return;
        if (typeof r === "string") abrir(r);
        else abrir(r.id, r.conversacion);
      }, { clase: "pequeno fantasma" }));
  }

  async function pintarSistema() {
    if (!idAbierto) {
      const nombreInput = h("input", { type: "text", placeholder: "por ejemplo: revisión de seguridad", "aria-label": "Nombre del sistema" });
      const origen = leerOrigen("_nuevo");
      vaciar(zonaSistema,
        plantillaNuevo({ proponiendo, idea: origen.idea, nombreInput }),
        huecoSugerencias);
      nombreInput.addEventListener("change", () => {
        const o = leerOrigen("_nuevo");
        guardarOrigen("_nuevo", { ...o, nombre: nombreInput.value.trim() });
      });
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
          await pintarLista();
          abrir(r?.slug || r?.id || idAbierto);
        });
      };
      vaciar(zonaSistema,
        h("div", { class: "tarjeta pila solo-web" },
          h("h2", { texto: donde.enWeb ? `«${idAbierto}» está en la web, no en este equipo` : `«${idAbierto}» no está en este equipo` }),
          h("p", { texto: donde.enWeb
            ? "Para ver y editar sus archivos aquí, tráelo: se copia a tu catálogo local y la web no cambia. Mientras tanto puedes revisar lo que dejó uxyn abajo y pedirle mejoras."
            : "No está en tu catálogo local." }),
          h("div", { class: "fila" },
            donde.enWeb ? boton("Traer de la web para editar", traer, { clase: "primario", icono: "descargar" }) : null,
            enPapelera ? boton("Restaurar de la papelera", async () => {
              await enviar("/api/mis-sistemas/restaurar", { entrada: enPapelera.entrada });
              cache.cat = null;
              await catLocal(true);
              await pintarLista();
              avisar(`«${idAbierto}» restaurado de la papelera`);
              abrir(idAbierto);
            }, { clase: donde.enWeb ? "" : "primario", icono: "deshacer" }) : null,
            boton("Mejorar con uxyn", async () => {
              zonas.agente = true;
              guardarZonas(zonas);
              aplicar();
              if (!chatMontado) await montarChat();
            }, { icono: "chat" }),
            boton("Nuevo sistema", () => abrir(""), { clase: "fantasma" })),
          enPapelera ? h("p", { class: "tenue", texto: `Lo eliminaste de este equipo el ${String(enPapelera.eliminado || "").slice(0, 16).replace("T", " a las ")}; sigue en la papelera.` }) : null),
        huecoSugerencias);
      return;
    }
    abierto = await editorSistema(idAbierto, {
      alCambiar: async () => {
        cache.cat = null;
        await pintarLista();
        await pintarFranjas();
      },
    });
    if (pagina && !pagina.isConnected) return;
    vaciar(zonaSistema,
      h("div", { class: "fila separada" },
        h("div", {},
          h("h2", { texto: meta.titulo || meta.id }),
          h("code", { class: "tenue", texto: meta.id }),
          insigniasDonde(await dondeEsta(idAbierto))),
        boton("Nuevo", () => abrir(""), { clase: "pequeno", titulo: "Nuevo sistema" })),
      huecoSugerencias,
      abierto.nodo);
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
        await pintarLista();
        await pintarFranjas();
      },
    });
    vaciar(huecoSugerencias, sugerenciasApi.nodo);
    await sugerenciasApi.refrescar();
  }

  async function montarChat() {
    if (chatMontado || !vivo()) return;
    chatMontado = true;
    if (!idAbierto) {
      const inicio = inicioConAgente({
        cabecera: true,
        alAntesDeCrear: async ({ idea, adjuntos }) => {
          guardarOrigen("_nuevo", { idea, adjuntos });
          proponiendo = true;
          await pintarFranjas();
          await pintarSistema();
        },
        alDespuesDeCrear: async () => {
          proponiendo = false;
          await pintarFranjas();
        },
        alCrear: async (id, r) => {
          moverOrigen("_nuevo", id);
          cache.cat = null;
          await catLocal(true);
          abrir(id, r.conversacion);
        },
      });
      vaciar(zonaAgente,
        h("h2", {}, icono("chat"), " uxyn"),
        h("p", { class: "tenue", texto: "Propone el núcleo. Tú ves archivos y aceptas en «Por revisar»." }),
        inicio.nodo);
      return;
    }

    if (!sugerenciasApi) await montarSugerencias();
    const chat = await chatAgente(
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
          await pintarFranjas();
        },
        alTerminarTurno: async () => {
          proponiendo = false;
          await pintarFranjas();
          if (abierto?.recargar) await abierto.recargar();
        },
      });

    chatApi = {
      pedirCompletar: async () => {
        const area = zonaAgente.querySelector("textarea");
        if (!area) {
          zonas.agente = true;
          guardarZonas(zonas);
          aplicar();
          if (!chatMontado) await montarChat();
          return;
        }
        let errores = [];
        let marcadores = [];
        let siguiente = null;
        try {
          const p = await obtener("/api/catalogo/pendientes", { id: idAbierto });
          errores = p.errores || [];
          marcadores = p.marcadores || [];
          siguiente = p.siguiente || null;
        } catch { /* */ }
        area.value = armarPromptCompletar({ errores, marcadores, siguiente });
        area.dispatchEvent(new Event("input"));
        const enviarBtn = [...zonaAgente.querySelectorAll("button")].find((b) => /Enviar/i.test(b.textContent || ""));
        enviarBtn?.click();
      },
    };

    vaciar(zonaAgente,
      h("h2", {}, icono("chat"), " uxyn"),
      h("p", { class: "tenue", texto: "Propone cambios; tú decides en «Por revisar»." }),
      chat);
  }

  async function pintarAgente() {
    if (!idAbierto) {
      // Al crear, uxyn es el camino principal: montarlo aunque el cajón empiece cerrado
      // solo si el usuario lo abre, o si ya estaba abierto.
      vaciar(zonaAgente,
        h("h2", {}, icono("chat"), " uxyn"),
        h("p", { class: "tenue", texto: "Abre uxyn (arriba) o pulsa «Crear con uxyn»." }));
      if (zonas.agente) await montarChat();
      return;
    }
    await montarSugerencias();
    if (zonas.agente) await montarChat();
    else {
      vaciar(zonaAgente,
        h("h2", {}, icono("chat"), " uxyn"),
        h("p", { class: "tenue", texto: "Cajón cerrado. Ábrelo para hablar con uxyn." }));
      chatMontado = false;
      chatApi = {
        pedirCompletar: async () => {
          zonas.agente = true;
          guardarZonas(zonas);
          aplicar();
          await montarChat();
        },
      };
    }
  }

  aplicar();
  cuerpo.append(zonaLista, zonaSistema, zonaAgente);
  marco.append(zonaOrigen, zonaCiclo, zonaSalida, cuerpo);
  const sigueCargando = (zona) => zona.childElementCount === 1 && zona.firstElementChild?.dataset.cargando === "1";
  vaciar(zonaLista, h("p", { class: "tenue", "data-cargando": "1", texto: "Cargando sistemas…" }));
  vaciar(zonaSistema, h("p", { class: "tenue", "data-cargando": "1", texto: idAbierto ? "Cargando sistema…" : "Preparando…" }));
  vaciar(zonaOrigen, h("p", { class: "tenue", "data-cargando": "1", texto: "…" }));
  vaciar(zonaCiclo, h("p", { class: "tenue", "data-cargando": "1", texto: "…" }));
  vaciar(zonaSalida, h("p", { class: "tenue", "data-cargando": "1", texto: "…" }));

  pagina = h("div", { class: "taller-pagina" },
    cabecera("Taller", "Sistemas de gobernanza: archivos, origen, ciclo y salida. uxyn propone; tú decides.",
      h("div", { class: "fila", role: "group", "aria-label": "Zonas" }, interruptorLista, interruptorAgente)),
    marco);

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
      await Promise.all([pintarLista(), pintarSistema(), pintarFranjas()]);
      if (!vivo()) return;
      await pintarAgente();
      if (!vivo()) return;
      await pintarFranjas();
    } catch (e) {
      if (!vivo()) return;
      const mensaje = e.message || String(e);
      avisar(mensaje, "mal");
      // Ninguna zona se queda en «Cargando…» para siempre: si la carga falló, lo dice y deja reintentar.
      for (const zona of [zonaLista, zonaSistema, zonaOrigen, zonaCiclo, zonaSalida]) {
        if (!sigueCargando(zona)) continue;
        vaciar(zona, h("div", { class: "banda mal", role: "alert" },
          h("span", { texto: `No se pudo cargar: ${mensaje} ` }),
          h("button", { type: "button", class: "secundario", texto: "Reintentar", onclick: () => recargar?.() })));
      }
    }
  })();

  return pagina;
}
