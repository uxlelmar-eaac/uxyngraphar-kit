// Puesto de trabajo asistido: carril de estado + Editor (izq) + uxyn (der).
// Crear y editar viven en la misma pantalla. Lista = cajón opcional.

import { catalogo, obtener } from "../api.js";
import { h, vaciar, boton, cabecera, insignia, icono, avisar } from "../ui.js";
import { editorSistema, crearSistema, FAMILIAS } from "./creador-editor.js";
import { chatAgente, tarjetaCreador, panelSugerencias } from "./creador.js";
import { inicioConAgente } from "./creador-inicio.js";
import { resolverEstado } from "./creador-estado.js";

const CLAVE = "uxyn-creador-zonas-v4";
export const ZONAS = [
  ["lista", "Lista"],
  ["sistema", "Editor"],
  ["agente", "uxyn"],
];

/** Siempre Editor + uxyn; Lista opcional. */
export function leerZonas() {
  const defecto = { lista: false, sistema: true, agente: true };
  try {
    const guardado = JSON.parse(localStorage.getItem(CLAVE) || "{}");
    const zonas = { ...defecto, ...guardado, sistema: true, agente: true };
    return Object.values(zonas).some(Boolean) ? zonas : defecto;
  } catch {
    return defecto;
  }
}

function guardarZonas(zonas) {
  try { localStorage.setItem(CLAVE, JSON.stringify(zonas)); } catch { /* sin almacenamiento */ }
}

function carrilEstado(estado, { alAccion, ocupado } = {}) {
  const nodo = h("section", {
    class: "carril-estado",
    "data-estado": estado.id,
    "aria-label": "Estado del sistema",
  },
    h("div", { class: "carril-estado-main" },
      insignia(estado.etiqueta, estado.id === "listo" ? "bien" : estado.id === "por_revisar" || estado.id === "falta_nucleo" ? "nota" : ""),
      h("p", { class: "carril-detalle", texto: estado.detalle }),
      estado.revisar ? h("p", { class: "tenue", texto: estado.revisar }) : null),
    (() => {
      if (!estado.cta || estado.accion === "ninguna") return null;
      const b = boton(estado.cta, () => alAccion && alAccion(estado), { clase: "pequeno primario" });
      if (ocupado) b.disabled = true;
      return b;
    })());
  return nodo;
}

export async function vista(params, { ir }) {
  const idAbierto = params.id || "";
  const zonas = leerZonas();
  let abierto = null;
  let propuestasPendientes = 0;
  let proponiendo = false;
  let chatApi = null; // { pedirCompletar, pedirRevisar } si el chat lo expone

  const marco = h("div", { class: "creador-puesto" });
  const zonaCarril = h("div", { class: "creador-carril" });
  const cuerpo = h("div", { class: "creador", "data-modo": idAbierto ? "editar" : "crear" });
  const zonaLista = h("section", { class: "zona zona-lista", "aria-label": "Lista de sistemas" });
  const zonaSistema = h("section", { class: "zona zona-sistema", "aria-label": "Editor" });
  const zonaAgente = h("section", { class: "zona zona-agente", "aria-label": "uxyn" });
  const nodos = { lista: zonaLista, sistema: zonaSistema, agente: zonaAgente };

  const interruptores = ZONAS.map(([clave, nombre]) => {
    const fijo = clave === "sistema" || clave === "agente";
    const b = h("button", {
      type: "button",
      class: "boton pequeno conmutador",
      "aria-pressed": String(zonas[clave]),
      "aria-controls": `zona-${clave}`,
      title: fijo ? `«${nombre}» siempre visible en el puesto asistido` : `Mostrar u ocultar «${nombre}»`,
      disabled: fijo || null,
    }, nombre);
    if (!fijo) {
      b.addEventListener("click", () => {
        zonas[clave] = !zonas[clave];
        guardarZonas(zonas);
        aplicar();
      });
    }
    return b;
  });

  function aplicar() {
    zonas.sistema = true;
    zonas.agente = true;
    for (const [clave] of ZONAS) {
      nodos[clave].id = `zona-${clave}`;
      nodos[clave].hidden = !zonas[clave];
    }
    interruptores.forEach((b, i) => b.setAttribute("aria-pressed", String(zonas[ZONAS[i][0]])));
    cuerpo.dataset.zonas = ZONAS.filter(([k]) => zonas[k]).map(([k]) => k).join(" ");
    cuerpo.dataset.modo = idAbierto ? "editar" : "crear";
  }

  const abrir = (id, conversacion) => ir("creador", id ? { id, ...(conversacion ? { conversacion } : {}) } : null);

  async function datosEstado() {
    if (!idAbierto) {
      return resolverEstado({ tieneSistema: false, proponiendo });
    }
    let errores = [];
    let marcadores = [];
    let siguiente = null;
    let listo = null;
    let valido = null;
    try {
      const p = await obtener("/api/catalogo/pendientes", { id: idAbierto });
      errores = p.errores || [];
      marcadores = p.marcadores || [];
      siguiente = p.siguiente || null;
      listo = !!p.listo;
      valido = listo || !(errores.length || marcadores.length) ? listo : false;
      if (!errores.length && !marcadores.length) valido = true;
    } catch { /* sin validador local */ }
    try {
      const todas = await obtener("/api/agente/propuestas", { slug: idAbierto });
      propuestasPendientes = (todas || []).filter((x) => (x.archivos || []).some((a) => a.estado === "pendiente")).length;
    } catch {
      propuestasPendientes = 0;
    }
    return resolverEstado({
      tieneSistema: true,
      proponiendo,
      propuestas: propuestasPendientes,
      errores,
      marcadores,
      siguiente,
      listo,
      valido,
      alDia: true,
    });
  }

  async function pintarCarril() {
    const estado = await datosEstado();
    vaciar(zonaCarril, carrilEstado(estado, {
      ocupado: proponiendo,
      alAccion: async (e) => {
        if (e.accion === "crear") {
          zonaAgente.querySelector("textarea")?.focus();
          return;
        }
        if (e.accion === "revisar") {
          const panel = zonaAgente.querySelector(".sugerencias-panel");
          if (panel) {
            panel.hidden = false;
            try { panel.scrollIntoView({ behavior: "smooth", block: "nearest" }); } catch { /* */ }
          }
          return;
        }
        if (e.accion === "completar" || e.accion === "validar") {
          if (chatApi?.pedirCompletar) await chatApi.pedirCompletar();
          else avisar("Escribe a uxyn a la derecha: «Completa el núcleo».", "mal");
          return;
        }
        if (e.accion === "publicar") {
          avisar("Usa «Versión y publicar» en el editor cuando el carril diga Listo.");
        }
      },
    }));
  }

  async function pintarLista() {
    const cat = await catalogo(true);
    const filtro = h("input", { type: "search", placeholder: "Buscar…", "aria-label": "Buscar sistema" });
    const lista = h("ul", { class: "lista lista-sistemas" });
    const pintar = () => {
      const t = filtro.value.trim().toLowerCase();
      const visibles = cat.filter((m) => !t || `${m.titulo} ${m.id} ${m.descripcion}`.toLowerCase().includes(t));
      vaciar(lista, visibles.map((m) => h("li", {},
        h("a", { href: `#/creador?id=${encodeURIComponent(m.id)}`, class: "elemento-sistema" + (m.id === idAbierto ? " activo" : ""),
          "aria-current": m.id === idAbierto ? "page" : null },
          h("b", { texto: m.titulo || m.id }),
          h("span", { class: "tenue", texto: `${FAMILIAS[m.familia] || m.familia || ""} · ${m.version || ""}` }),
          (m.errores || []).length ? insignia("le falta algo", "nota") : null))));
      if (!visibles.length) lista.append(h("li", { class: "tenue", texto: cat.length ? "Nada coincide." : "Aún no hay sistemas aquí." }));
    };
    filtro.addEventListener("input", pintar);
    pintar();
    vaciar(zonaLista,
      h("div", { class: "fila separada" },
        h("h2", { texto: "Lista" }),
        boton("Nuevo", () => abrir(""), { clase: "pequeno", icono: "mas", titulo: "Crear otro con uxyn" })),
      filtro, lista,
      await tarjetaCreador({ alTraer: async (r, slug) => abrir(r?.id || slug) }),
      h("details", { class: "creador-extra" },
        h("summary", { texto: "Avanzado: crear sin uxyn" }),
        h("p", { class: "tenue", texto: "Plantilla paso a paso (sin agente)." }),
        boton("Paso a paso", async () => {
          const r = await crearSistema();
          if (!r) return;
          if (typeof r === "string") abrir(r);
          else abrir(r.id, r.conversacion);
        }, { clase: "pequeno" })));
  }

  async function pintarSistema() {
    if (!idAbierto) {
      vaciar(zonaSistema,
        h("div", { class: "pila editor-vacio" },
          h("h2", { texto: "Editor" }),
          h("p", { class: "tenue", texto: "Aquí verás los archivos núcleo cuando uxyn cree el sistema. Mientras, escribe la idea a la derecha." }),
          h("div", { class: "banda aviso", texto: "1. Idea o archivos → 2. uxyn propone → 3. Aceptas en «Por revisar»." })));
      return;
    }
    const meta = (await catalogo()).find((m) => m.id === idAbierto);
    if (!meta) {
      vaciar(zonaSistema, h("div", { class: "banda mal", texto: `No encuentro «${idAbierto}» en este equipo.` }),
        h("p", {}, boton("Crear con uxyn", () => abrir(""), { clase: "pequeno" })));
      return;
    }
    abierto = await editorSistema(idAbierto, {
      alCambiar: async () => {
        await pintarLista();
        await pintarCarril();
      },
    });
    vaciar(zonaSistema,
      h("div", { class: "fila separada" },
        h("div", {}, h("h2", { texto: meta.titulo || meta.id }), h("code", { class: "tenue", texto: meta.id })),
        boton("Crear otro", () => abrir(""), { clase: "pequeno", titulo: "Volver a crear con uxyn" })),
      abierto.nodo);
  }

  async function pintarAgente() {
    if (!idAbierto) {
      const inicio = inicioConAgente({
        alCrear: async (id, r) => {
          proponiendo = false;
          await pintarCarril();
          abrir(id, r.conversacion);
        },
      });
      // Envolver create para marcar proponiendo
      const crearOrig = inicio.crear;
      inicio.crear = async () => {
        proponiendo = true;
        await pintarCarril();
        try {
          return await crearOrig();
        } finally {
          proponiendo = false;
          await pintarCarril();
        }
      };
      vaciar(zonaAgente,
        h("h2", {}, icono("chat"), " uxyn"),
        h("p", { class: "tenue", texto: "Cuenta la idea o sube archivos/zip. uxyn arma el núcleo del sistema." }),
        inicio.nodo);
      return;
    }

    const sugerencias = panelSugerencias(idAbierto, {
      alCambiar: async () => {
        if (abierto?.recargar) await abierto.recargar();
        await pintarLista();
        await pintarCarril();
      },
    });

    const chat = await chatAgente(
      () => (abierto ? { id: idAbierto, rutaActual: abierto.rutaActual, textarea: abierto.textarea, recargar: abierto.recargar } : null),
      {
        conversacionInicial: Number(params.conversacion) || null,
        slugInicial: idAbierto || null,
        sugerencias,
        alProponer: async () => {
          proponiendo = false;
          await pintarCarril();
        },
        alEmpezarTurno: async () => {
          proponiendo = true;
          await pintarCarril();
        },
        alTerminarTurno: async () => {
          proponiendo = false;
          await pintarCarril();
          if (abierto?.recargar) await abierto.recargar();
        },
      });

    chatApi = {
      pedirCompletar: async () => {
        const area = zonaAgente.querySelector("textarea");
        if (area) {
          area.value = "Completa los archivos núcleo (SISTEMA.md, LIMITES.md, PERMISOS.md, MEMORIAS.md, README.md y sistema.json): sustituye todos los marcadores {{…}} y déjalo en «Por revisar».";
          area.dispatchEvent(new Event("input"));
          const enviarBtn = [...zonaAgente.querySelectorAll("button")].find((b) => /Enviar/i.test(b.textContent || ""));
          enviarBtn?.click();
        }
      },
    };

    vaciar(zonaAgente,
      h("h2", {}, icono("chat"), " uxyn"),
      h("p", { class: "tenue", texto: "Pide completar o mejorar. Los cambios salen en «Por revisar» (arriba). Mira el carril de estado." }),
      sugerencias.nodo,
      chat);
  }

  aplicar();
  cuerpo.append(zonaLista, zonaSistema, zonaAgente);
  marco.append(zonaCarril, cuerpo);
  await Promise.all([pintarLista(), pintarSistema(), pintarCarril()]);
  await pintarAgente();
  await pintarCarril();

  return h("div", {},
    cabecera("Creador de sistemas",
      idAbierto
        ? "Editor a la izquierda · uxyn a la derecha · el carril dice el siguiente paso."
        : "Cuenta la idea a uxyn. El editor se llenará cuando exista el sistema.",
      h("div", { class: "fila", role: "group", "aria-label": "Zonas visibles" }, interruptores)),
    marco);
}
