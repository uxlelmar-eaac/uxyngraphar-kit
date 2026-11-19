// Mis proyectos: la lista de proyectos que gestiona el panel, ordenada en carpetas y con etiquetas (todo se arrastra),
// y los grupos, que juntan repos de un mismo sistema para actualizarlos y verificarlos a la vez.
//
// Carpetas y etiquetas solo ordenan esta lista (organizacion.json); los grupos actúan sobre los proyectos (grupos.json).
// Por eso conviven: una carpeta «Clientes» puede tener varios proyectos sueltos, y un grupo «tienda» junta el backend y
// el frontend de un sistema estén en la carpeta que estén. Desde una carpeta se puede crear un grupo con sus proyectos.

import { obtener, enviar } from "../api.js";
import { h, vaciar, cabecera, boton, insignia, vacio, confirmar, avisar, dialogo, elegirVarios, pedirDatos, icono, menu } from "../ui.js";
import { agregarProyectos } from "../explorador.js";
import { MODOS } from "../flujo.js";
import { quitarProyecto } from "./quitar-proyecto.js";

export const COLORES = [["oro", "Oro"], ["naranja", "Naranja"], ["verde", "Verde"], ["rojo", "Rojo"], ["arena", "Arena"], ["gris", "Gris"]];
const SIN_CARPETA = "_sin";
const PREFERENCIAS = "uxyn-proyectos";
const ORG_VACIA = { carpetas: [], etiquetas: [], proyectos: {}, orden: [] };

export function estadoProyecto(p) {
  if (!p.existe) return insignia("carpeta no encontrada", "mal");
  if (p.alterados) return insignia(`${p.alterados} alterado(s)`, "mal");
  if (p.actualizables) return insignia(`${p.actualizables} actualización(es)`, "aviso");
  if (!p.sistemas.length) return insignia("sin sistemas");
  return insignia("al día", "bien");
}

const detalleSistemas = (p) => [p.sistemas.length ? `${p.sistemas.length} sistema(s)` : "Sin sistemas instalados",
  p.modo ? ` · ${MODOS[p.modo]?.titulo || p.modo}` : ""];

// Tarjeta sencilla (la usa Inicio para los proyectos que piden atención).
export function tarjetaProyecto(p, ir, alQuitar) {
  const abrir = () => ir("proyecto", { ruta: p.ruta });
  return h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("div", {}, h("h3", { texto: p.nombre }), h("div", { class: "tenue", texto: p.grupo })), estadoProyecto(p)),
    h("div", { class: "tenue" }, detalleSistemas(p)),
    h("div", { class: "acciones" }, p.existe ? boton("Abrir", abrir, { clase: "primario pequeno" }) : null,
      alQuitar ? boton("Quitar de la lista", alQuitar, { clase: "fantasma pequeno" }) : null));
}

const atencion = (p) => !p.existe || p.alterados > 0 || p.actualizables > 0;
const gravedad = (p) => (!p.existe || p.alterados ? 0 : p.actualizables ? 1 : !p.sistemas.length ? 2 : 3);
const porNombre = (a, b) => a.nombre.localeCompare(b.nombre, "es", { sensitivity: "base" });
const aSlug = (texto) => String(texto || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
  .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40);

function leerPreferencias() {
  try { return JSON.parse(localStorage.getItem(PREFERENCIAS)) || {}; } catch { return {}; }
}
function guardarPreferencias(p) {
  try { localStorage.setItem(PREFERENCIAS, JSON.stringify(p)); } catch { /* sin almacenamiento: no se recuerda */ }
}

function selectorColor(actual) {
  const radios = COLORES.map(([valor, texto]) => h("input", { type: "radio", name: "color", value: valor, checked: valor === actual, "aria-label": texto }));
  return {
    nodo: h("div", { class: "colores", role: "radiogroup", "aria-label": "Color" },
      COLORES.map(([valor, texto], i) => h("label", { class: `muestra color-${valor}`, title: texto }, radios[i]))),
    valor: () => radios.find((r) => r.checked)?.value || actual,
  };
}

const botonIcono = (nombre, etiqueta, accion) => {
  const b = h("button", { type: "button", class: "boton fantasma pequeno solo-icono", "aria-label": etiqueta, title: etiqueta, "aria-haspopup": "menu" }, icono(nombre));
  b.addEventListener("click", () => accion(b));
  return b;
};

export async function vista(_params, { ir, recargar }) {
  const [lista, orgGuardada, gruposGuardados] = await Promise.all([obtener("/api/proyectos"),
    obtener("/api/organizacion").catch(() => ORG_VACIA), obtener("/api/grupos").catch(() => ({}))]);
  let org = orgGuardada;
  let grupos = gruposGuardados;
  let arrastre = null;   // { tipo: "proyecto" | "etiqueta" | "carpeta", valor }: dataTransfer no se puede leer durante dragover
  const pref = { orden: "manual", vista: "tarjetas", plegadas: [], ...leerPreferencias() };
  const filtros = { texto: "", etiquetas: new Set(), estado: "todos" };

  const agregar = async () => { if ((await agregarProyectos()).length) recargar(); };
  if (!lista.length) {
    return h("div", {}, cabecera("Proyectos", "Los proyectos que gestionas desde el panel."),
      vacio("Aún no hay proyectos", "Añade la carpeta de un proyecto, o una carpeta que contenga varios, y aparecerán aquí.",
        boton("Añadir proyectos", agregar, { clase: "primario", icono: "mas" })));
  }

  const info = (p) => org.proyectos[p.ruta] || { carpeta: null, etiquetas: [] };
  const carpetaDe = (p) => (org.carpetas.some((c) => c.id === info(p).carpeta) ? info(p).carpeta : null);
  const colorEtiqueta = (nombre) => org.etiquetas.find((e) => e.nombre === nombre)?.color || "gris";
  const gruposDe = (p) => Object.keys(grupos).filter((n) => grupos[n].includes(p.ruta));

  async function cambiar(ruta, datos, aviso) {
    org = await enviar(ruta, datos);
    pintar();
    if (aviso) avisar(aviso);
  }
  const mover = (rutas, carpeta, antes) => {
    const destino = org.carpetas.find((c) => c.id === carpeta);
    const cambia = rutas.some((r) => (info({ ruta: r }).carpeta || null) !== (carpeta || null));
    return cambiar("/api/organizacion/mover", { rutas, carpeta: carpeta || null, antes: antes || null },
      cambia ? (destino ? `Movido a «${destino.nombre}»` : "Movido a «Sin carpeta»") : "");
  };
  const etiquetar = (rutas, etiqueta, poner = true) => cambiar("/api/organizacion/etiquetar", { rutas, etiqueta, poner },
    poner ? `Etiqueta «${etiqueta}» puesta` : "");

  // Arrastrar y soltar ----------------------------------------------------------------------------------------------
  function arrastrable(el, tipo, valor) {
    el.draggable = true;
    el.addEventListener("dragstart", (e) => {
      e.stopPropagation();
      arrastre = { tipo, valor };
      e.dataTransfer.effectAllowed = tipo === "etiqueta" ? "copy" : "move";
      e.dataTransfer.setData("text/plain", String(valor));
      el.classList.add("arrastrando");
      zona.classList.add(`arrastrando-${tipo}`);
    });
    el.addEventListener("dragend", () => {
      arrastre = null;
      el.classList.remove("arrastrando");
      zona.classList.remove("arrastrando-proyecto", "arrastrando-etiqueta", "arrastrando-carpeta");
      for (const d of document.querySelectorAll(".destino")) d.classList.remove("destino");
    });
  }
  function soltable(el, acepta, alSoltar) {
    const sobreSiMismo = (e) => arrastre?.tipo === "proyecto" && e.target.closest?.(".proyecto.arrastrando");
    el.addEventListener("dragover", (e) => {
      if (!arrastre || !acepta(arrastre) || sobreSiMismo(e)) return;
      e.preventDefault();
      e.stopPropagation();
      e.dataTransfer.dropEffect = arrastre.tipo === "etiqueta" ? "copy" : "move";
      for (const d of document.querySelectorAll(".destino")) if (d !== el) d.classList.remove("destino");
      el.classList.add("destino");
    });
    el.addEventListener("dragleave", (e) => { if (!el.contains(e.relatedTarget)) el.classList.remove("destino"); });
    el.addEventListener("drop", (e) => {
      if (!arrastre || !acepta(arrastre) || sobreSiMismo(e)) return;
      e.preventDefault();
      e.stopPropagation();
      el.classList.remove("destino");
      const a = arrastre;
      arrastre = null;
      Promise.resolve(alSoltar(a)).catch((err) => avisar(err.message || String(err), "mal"));
    });
  }

  // Diálogos --------------------------------------------------------------------------------------------------------
  function editarCarpeta(c) {
    const nombre = h("input", { type: "text", value: c?.nombre || "", placeholder: "Por ejemplo: Clientes, Personales, Archivados", "aria-label": "Nombre de la carpeta" });
    const color = selectorColor(c?.color || "oro");
    return dialogo({ titulo: c ? `Editar la carpeta «${c.nombre}»` : "Nueva carpeta",
      contenido: h("div", { class: "pila" },
        h("p", { class: "tenue", texto: "Las carpetas solo ordenan esta lista: no mueven ni cambian nada en tu disco." }),
        h("label", { class: "campo" }, "Nombre", nombre), h("div", { class: "pila" }, h("b", { texto: "Color" }), color.nodo)),
      acciones: [{ texto: c ? "Guardar" : "Crear carpeta", clase: "primario", accion: async () => {
        if (!nombre.value.trim()) { avisar("Escribe un nombre para la carpeta", "mal"); return false; }
        await cambiar("/api/organizacion/carpeta", c ? { accion: "cambiar", id: c.id, nombre: nombre.value, color: color.valor() }
          : { accion: "crear", nombre: nombre.value, color: color.valor() });
        return org.carpetas.find((x) => x.nombre.toLowerCase() === nombre.value.trim().toLowerCase())?.id || true;
      } }] });
  }

  function editarEtiquetaNueva(rutas = []) {
    const nombre = h("input", { type: "text", placeholder: "Por ejemplo: urgente, cliente, pausado", "aria-label": "Nombre de la etiqueta" });
    const color = selectorColor(COLORES[org.etiquetas.length % COLORES.length][0]);
    return dialogo({ titulo: "Nueva etiqueta", contenido: h("div", { class: "pila" },
      h("p", { class: "tenue", texto: "Un proyecto puede tener varias etiquetas. Después arrástrala sobre un proyecto para ponérsela." }),
      h("label", { class: "campo" }, "Nombre", nombre), h("div", { class: "pila" }, h("b", { texto: "Color" }), color.nodo)),
    acciones: [{ texto: "Crear etiqueta", clase: "primario", accion: async () => {
      if (!nombre.value.trim()) { avisar("Escribe un nombre para la etiqueta", "mal"); return false; }
      await cambiar("/api/organizacion/etiqueta", { accion: "crear", nombre: nombre.value, color: color.valor() });
      if (rutas.length) await etiquetar(rutas, nombre.value.trim());
      return true;
    } }] });
  }

  function gestionarEtiquetas() {
    const filas = org.etiquetas.map((e) => ({ e, nombre: h("input", { type: "text", value: e.nombre, "aria-label": `Nombre de ${e.nombre}` }),
      color: h("select", { "aria-label": `Color de ${e.nombre}` }, COLORES.map(([v, t]) => h("option", { value: v, selected: v === e.color, texto: t }))),
      borrar: h("input", { type: "checkbox", "aria-label": `Borrar ${e.nombre}` }) }));
    const usos = (n) => Object.values(org.proyectos).filter((p) => p.etiquetas.includes(n)).length;
    return dialogo({ titulo: "Etiquetas", contenido: h("div", { class: "pila" },
      h("p", { class: "tenue", texto: "Cambia el nombre o el color. Borrar una etiqueta la quita de todos los proyectos; los proyectos no se tocan." }),
      h("ul", { class: "lista desplazable" }, filas.map((f) => h("li", { class: "fila-etiqueta" },
        h("span", { class: `punto color-${f.e.color}` }), f.nombre, f.color,
        h("span", { class: "tenue", texto: `${usos(f.e.nombre)} proy.` }),
        h("label", { class: "casilla" }, f.borrar, h("span", { texto: "Borrar" })))))),
    acciones: [{ texto: "Guardar cambios", clase: "primario", accion: async () => {
      for (const f of filas) {
        if (f.borrar.checked) await cambiar("/api/organizacion/etiqueta", { accion: "borrar", nombre: f.e.nombre });
        else if (f.nombre.value.trim() !== f.e.nombre || f.color.value !== f.e.color) {
          await cambiar("/api/organizacion/etiqueta", { accion: "cambiar", nombre: f.e.nombre, nuevo: f.nombre.value, color: f.color.value });
        }
      }
      avisar("Etiquetas guardadas");
      return true;
    } }] });
  }

  function editarEtiquetasDe(p) {
    const actuales = info(p).etiquetas;
    const casillas = org.etiquetas.map((e) => h("input", { type: "checkbox", value: e.nombre, checked: actuales.includes(e.nombre) }));
    const nueva = h("input", { type: "text", placeholder: "Nueva etiqueta (opcional)", "aria-label": "Nueva etiqueta" });
    return dialogo({ titulo: `Etiquetas de ${p.nombre}`, contenido: h("div", { class: "pila" },
      org.etiquetas.length ? h("div", { class: "chips elegir-etiquetas" }, org.etiquetas.map((e, i) =>
        h("label", { class: `chip color-${e.color}` }, casillas[i], h("span", { class: "punto" }), e.nombre)))
        : h("p", { class: "tenue", texto: "Aún no tienes etiquetas: escribe una abajo para crearla." }),
      h("label", { class: "campo" }, "Crear y poner otra", nueva)),
    acciones: [{ texto: "Guardar", clase: "primario", accion: async () => {
      const elegidas = casillas.filter((c) => c.checked).map((c) => c.value);
      if (nueva.value.trim()) elegidas.push(nueva.value.trim());
      await cambiar("/api/organizacion/etiquetas", { ruta: p.ruta, etiquetas: elegidas }, "Etiquetas guardadas");
      return true;
    } }] });
  }

  function elegirCarpeta(p) {
    const opciones = [{ id: "", nombre: "Sin carpeta", color: "gris" }, ...org.carpetas];
    const actual = carpetaDe(p) || "";
    const radios = opciones.map((c) => h("input", { type: "radio", name: "carpeta-destino", value: c.id, checked: c.id === actual }));
    const nueva = h("input", { type: "text", placeholder: "…o escribe el nombre de una carpeta nueva", "aria-label": "Carpeta nueva" });
    return dialogo({ titulo: `Mover ${p.nombre}`, contenido: h("div", { class: "pila" },
      h("ul", { class: "lista desplazable" }, opciones.map((c, i) => h("li", {}, h("label", { class: "casilla carpeta-opcion" },
        radios[i], h("span", { class: `punto color-${c.color}` }), h("span", { texto: c.nombre }))))), nueva),
    acciones: [{ texto: "Mover", clase: "primario", accion: async () => {
      let destino = radios.find((r) => r.checked)?.value || "";
      if (nueva.value.trim()) {
        org = await enviar("/api/organizacion/carpeta", { accion: "crear", nombre: nueva.value.trim(), color: "oro" });
        destino = org.carpetas[org.carpetas.length - 1].id;
      }
      await mover([p.ruta], destino || null);
      return true;
    } }] });
  }

  async function anadirAGrupo(p) {
    const nombres = Object.keys(grupos).filter((n) => !grupos[n].includes(p.ruta));
    if (!nombres.length) { avisar("No hay otro grupo al que añadirlo. Crea uno en «Grupos», al final de la página."); return; }
    const radios = nombres.map((n, i) => h("input", { type: "radio", name: "grupo-destino", value: n, checked: i === 0 }));
    const nombre = await dialogo({ titulo: `Añadir ${p.nombre} a un grupo`, contenido: h("ul", { class: "lista" }, nombres.map((n, i) =>
      h("li", {}, h("label", { class: "casilla carpeta-opcion" }, radios[i], h("span", {}, h("b", { texto: n }),
        h("div", { class: "tenue", texto: grupos[n].map((r) => r.split(/[\\/]/).pop()).join(" · ") })))))),
    acciones: [{ texto: "Añadir", clase: "primario", accion: () => radios.find((r) => r.checked)?.value }] });
    if (nombre) await guardarGrupo(nombre, [...grupos[nombre], p.ruta], `Añadido al grupo «${nombre}»`);
  }

  async function guardarGrupo(nombre, rutas, aviso) {
    await enviar("/api/grupos/guardar", { nombre, rutas });
    grupos = await obtener("/api/grupos");
    pintar();
    pintarGrupos();
    if (aviso) avisar(aviso);
  }

  const quitar = async (p) => {
    const r = await quitarProyecto({ ruta: p.ruta, nombre: p.nombre });
    if (!r) return;
    grupos = await obtener("/api/grupos").catch(() => grupos);
    recargar();
  };

  const opcionesProyecto = (p) => [
    p.existe ? { texto: "Abrir", icono: "flecha", accion: () => ir("proyecto", { ruta: p.ruta }) } : null,
    { texto: "Mover a carpeta…", icono: "carpeta", accion: () => elegirCarpeta(p) },
    { texto: "Etiquetas…", icono: "etiqueta", accion: () => editarEtiquetasDe(p) },
    { texto: "Añadir a un grupo…", icono: "conexiones", accion: () => anadirAGrupo(p) },
    { texto: "Copiar la ruta", icono: "copiar", accion: async () => {
      try { await navigator.clipboard.writeText(p.ruta); avisar("Ruta copiada"); } catch { avisar(p.ruta); }
    } },
    "-",
    { texto: "Quitar…", icono: "cerrar", peligro: true, accion: () => quitar(p) },
  ];

  async function crearGrupoDeCarpeta(c, ps) {
    const datos = await pedirDatos({ titulo: `Crear un grupo con «${c.nombre}»`,
      explicacion: `Un grupo actualiza y verifica de una vez sus proyectos (${ps.map((p) => p.nombre).join(", ")}). La carpeta sigue igual.`,
      campos: [{ nombre: "nombre", etiqueta: "Nombre del grupo", valor: aSlug(c.nombre) }], si: "Crear grupo" });
    if (!datos) return;
    await guardarGrupo(aSlug(datos.nombre), ps.map((p) => p.ruta), "Grupo creado");
  }

  const opcionesCarpeta = (c, ps) => [
    { texto: "Cambiar nombre o color…", icono: "editar", accion: () => editarCarpeta(c) },
    ps.filter((p) => p.existe).length >= 2 ? { texto: "Crear un grupo con estos proyectos…", icono: "conexiones",
      accion: () => crearGrupoDeCarpeta(c, ps.filter((p) => p.existe)) } : null,
    "-",
    { texto: "Borrar la carpeta", icono: "basura", peligro: true, accion: async () => {
      const ok = await confirmar({ titulo: `Borrar la carpeta «${c.nombre}»`, si: "Borrar carpeta",
        texto: ps.length ? `Sus ${ps.length} proyecto(s) pasan a «Sin carpeta». No se borra nada de tu disco.` : "Está vacía. No se borra nada de tu disco." });
      if (ok) await cambiar("/api/organizacion/carpeta", { accion: "borrar", id: c.id }, "Carpeta borrada");
    } },
  ];

  // Piezas ----------------------------------------------------------------------------------------------------------
  function chipEtiqueta(nombre, quitarla) {
    return h("span", { class: `chip color-${colorEtiqueta(nombre)}` }, h("span", { class: "punto" }), nombre,
      quitarla ? h("button", { type: "button", class: "chip-quitar", "aria-label": `Quitar la etiqueta ${nombre}`, title: "Quitar etiqueta",
        onclick: (e) => { e.stopPropagation(); quitarla(); } }, icono("cerrar")) : null);
  }

  function tarjeta(p) {
    const i = info(p);
    const suyos = gruposDe(p);
    const abrir = () => ir("proyecto", { ruta: p.ruta });
    const el = h("article", { class: "tarjeta tarjeta-item proyecto", "aria-label": p.nombre },
      h("div", { class: "proyecto-cabeza" },
        h("span", { class: "asa", title: "Arrastra para moverlo", "aria-hidden": "true" }, icono("asa")),
        h("div", { class: "proyecto-titulo" }, h("h3", { texto: p.nombre }),
          h("div", { class: "tenue proyecto-ruta", title: p.ruta }, icono("carpeta"), h("span", { texto: p.grupo }))),
        botonIcono("puntos", `Opciones de ${p.nombre}`, (b) => menu(b, opcionesProyecto(p)))),
      h("div", { class: "proyecto-estado" }, estadoProyecto(p), p.sistemas.length || p.modo ? h("span", { class: "tenue proyecto-detalle" }, detalleSistemas(p)) : null),
      i.etiquetas.length || suyos.length ? h("div", { class: "chips" },
        i.etiquetas.map((t) => chipEtiqueta(t, () => etiquetar([p.ruta], t, false))),
        suyos.map((n) => h("span", { class: "insignia acento", title: "Grupo: se actualiza y verifica con otros proyectos" }, icono("conexiones"), n))) : null,
      p.error ? h("div", { class: "tenue", texto: `No se pudo leer del todo: ${p.error}` }) : null,
      h("div", { class: "acciones" }, p.existe ? boton("Abrir", abrir, { clase: "primario pequeno" })
        : boton("Quitar de la lista", () => quitar(p), { clase: "pequeno" })));
    if (p.existe) el.addEventListener("dblclick", (e) => { if (!e.target.closest("button")) abrir(); });
    arrastrable(el, "proyecto", p.ruta);
    soltable(el, (a) => (a.tipo === "proyecto" && a.valor !== p.ruta) || (a.tipo === "etiqueta" && !i.etiquetas.includes(a.valor)),
      (a) => (a.tipo === "etiqueta" ? etiquetar([p.ruta], a.valor)
        : mover([a.valor], carpetaDe(p), pref.orden === "manual" ? p.ruta : null)));
    return el;
  }

  function seccion(c, ps) {
    const clave = c?.id || SIN_CARPETA;
    const plegada = pref.plegadas.includes(clave) && !filtrando();
    const plegar = () => {
      pref.plegadas = plegada ? pref.plegadas.filter((x) => x !== clave) : [...pref.plegadas, clave];
      guardarPreferencias(pref);
      pintar();
    };
    const cuerpo = ps.length ? h("div", { class: "rejilla" }, ps.map(tarjeta))
      : h("div", { class: "soltar-aqui", texto: filtrando() ? "Ningún proyecto de esta carpeta coincide." : "Carpeta vacía: arrastra proyectos aquí." });
    const cab = h("div", { class: "carpeta-cabeza" },
      c ? h("span", { class: "asa", title: "Arrastra para ordenar las carpetas", "aria-hidden": "true" }, icono("asa")) : null,
      h("button", { type: "button", class: "carpeta-plegar", "aria-expanded": String(!plegada), onclick: plegar },
        h("span", { class: `chevron ${plegada ? "plegado" : ""}` }, icono("abajo")),
        h("span", { class: `punto grande color-${c?.color || "gris"}` }),
        h("span", { class: "carpeta-nombre", texto: c ? c.nombre : "Sin carpeta" }),
        h("span", { class: "contador", texto: String(ps.length) })),
      c ? botonIcono("puntos", `Opciones de la carpeta ${c.nombre}`, (b) => menu(b, opcionesCarpeta(c, ps))) : null);
    const el = h("section", { class: `carpeta color-${c?.color || "gris"} ${c ? "" : "sin-carpeta"}`, "aria-label": c ? `Carpeta ${c.nombre}` : "Sin carpeta" },
      cab, plegada ? null : cuerpo);
    if (c) arrastrable(cab, "carpeta", c.id);
    soltable(el, (a) => a.tipo === "proyecto" || (a.tipo === "carpeta" && c && a.valor !== c.id), (a) => {
      if (a.tipo === "proyecto") return mover([a.valor], c?.id || null);
      const ids = org.carpetas.map((x) => x.id).filter((x) => x !== a.valor);
      ids.splice(ids.indexOf(c.id), 0, a.valor);
      return cambiar("/api/organizacion/carpetas/ordenar", { ids });
    });
    return el;
  }

  // Barra de herramientas y filtros ---------------------------------------------------------------------------------
  const filtrando = () => Boolean(filtros.texto || filtros.etiquetas.size || filtros.estado !== "todos");
  function pasa(p) {
    const i = info(p);
    if (filtros.texto && !`${p.nombre} ${p.grupo} ${i.etiquetas.join(" ")} ${gruposDe(p).join(" ")}`.toLowerCase().includes(filtros.texto)) return false;
    for (const t of filtros.etiquetas) if (!i.etiquetas.includes(t)) return false;
    if (filtros.estado === "atencion") return atencion(p);
    if (filtros.estado === "al-dia") return !atencion(p) && p.sistemas.length > 0;
    if (filtros.estado === "sin-sistemas") return p.existe && !p.sistemas.length;
    return true;
  }
  function ordenar(ps) {
    if (pref.orden === "nombre") return [...ps].sort(porNombre);
    if (pref.orden === "estado") return [...ps].sort((a, b) => gravedad(a) - gravedad(b) || porNombre(a, b));
    const pos = new Map(org.orden.map((r, i) => [r, i]));
    return [...ps].sort((a, b) => (pos.get(a.ruta) ?? Infinity) - (pos.get(b.ruta) ?? Infinity) || porNombre(a, b));
  }

  const buscar = h("input", { type: "search", placeholder: "Buscar por nombre, carpeta del disco, etiqueta o grupo…", "aria-label": "Buscar proyecto" });
  buscar.addEventListener("input", () => { filtros.texto = buscar.value.trim().toLowerCase(); pintar(); });
  const estado = h("select", { "aria-label": "Filtrar por estado" },
    [["todos", "Todos los estados"], ["atencion", "Necesitan atención"], ["al-dia", "Al día"], ["sin-sistemas", "Sin sistemas"]]
      .map(([v, t]) => h("option", { value: v, texto: t })));
  estado.addEventListener("change", () => { filtros.estado = estado.value; pintar(); });
  const orden = h("select", { "aria-label": "Ordenar" },
    [["manual", "Orden: el mío (arrastrando)"], ["nombre", "Orden: por nombre"], ["estado", "Orden: primero lo que pide atención"]]
      .map(([v, t]) => h("option", { value: v, selected: v === pref.orden, texto: t })));
  orden.addEventListener("change", () => { pref.orden = orden.value; guardarPreferencias(pref); pintar(); });
  const vistas = [["tarjetas", "rejilla", "Ver como tarjetas"], ["lista", "lista", "Ver como lista"]].map(([v, ic, t]) => {
    const b = h("button", { type: "button", class: "boton pequeno solo-icono", "aria-label": t, title: t, "aria-pressed": String(pref.vista === v) }, icono(ic));
    b.addEventListener("click", () => {
      pref.vista = v;
      guardarPreferencias(pref);
      for (const x of vistas) x.setAttribute("aria-pressed", String(x === b));
      pintar();
    });
    return b;
  });
  const herramientas = h("div", { class: "herramientas-proyectos" }, buscar, estado, orden, h("div", { class: "conmutador-vista", role: "group", "aria-label": "Vista" }, vistas));

  const barraEtiquetas = h("div", { class: "barra-etiquetas" });
  function pintarEtiquetas() {
    const chips = org.etiquetas.map((e) => {
      const activa = filtros.etiquetas.has(e.nombre);
      // span con rol de botón: Firefox no deja arrastrar un <button>
      const b = h("span", { role: "button", tabindex: "0", class: `chip pulsable color-${e.color}`, "aria-pressed": String(activa),
        title: "Pulsa para filtrar · arrastra sobre un proyecto para ponérsela" }, h("span", { class: "punto" }), e.nombre);
      const alternar = () => {
        if (activa) filtros.etiquetas.delete(e.nombre); else filtros.etiquetas.add(e.nombre);
        pintar();
      };
      b.addEventListener("click", alternar);
      b.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); alternar(); } });
      arrastrable(b, "etiqueta", e.nombre);
      return b;
    });
    vaciar(barraEtiquetas, h("span", { class: "barra-titulo" }, icono("etiqueta"), "Etiquetas"), ...chips,
      h("button", { type: "button", class: "chip chip-nueva", onclick: () => editarEtiquetaNueva() }, icono("mas"), "Nueva etiqueta"),
      org.etiquetas.length ? h("button", { type: "button", class: "enlace tenue", onclick: () => gestionarEtiquetas(), texto: "Editar etiquetas" }) : null,
      org.etiquetas.length ? null : h("span", { class: "tenue", texto: "Ponles etiquetas como «cliente» o «urgente» para encontrarlos rápido." }));
  }

  const resumen = h("div", { class: "resumen-proyectos" });
  function pintarResumen(visibles) {
    const pendientes = lista.filter(atencion).length;
    vaciar(resumen,
      h("span", { class: "tenue", texto: filtrando() ? `Mostrando ${visibles} de ${lista.length} proyectos` : `${lista.length} proyecto(s)` }),
      pendientes && filtros.estado !== "atencion" ? h("button", { type: "button", class: "enlace", texto: `${pendientes} necesita(n) atención`,
        onclick: () => { filtros.estado = estado.value = "atencion"; pintar(); } }) : null,
      filtrando() ? h("button", { type: "button", class: "enlace", texto: "Quitar filtros", onclick: () => {
        filtros.texto = buscar.value = ""; filtros.estado = estado.value = "todos"; filtros.etiquetas.clear(); pintar();
      } }) : null,
      pref.orden === "manual" && !filtrando() ? h("span", { class: "tenue pista", texto: "Arrastra los proyectos entre carpetas o para ordenarlos. Doble clic abre un proyecto." }) : null);
  }

  const zona = h("div", { class: "organizador" });
  function pintar() {
    zona.classList.toggle("vista-lista", pref.vista === "lista");
    pintarEtiquetas();
    const visibles = ordenar(lista.filter(pasa));
    pintarResumen(visibles.length);
    const secciones = org.carpetas.map((c) => seccion(c, visibles.filter((p) => carpetaDe(p) === c.id)))
      .filter((s, i) => !filtrando() || visibles.some((p) => carpetaDe(p) === org.carpetas[i].id));
    const sueltos = visibles.filter((p) => !carpetaDe(p));
    if (sueltos.length || (org.carpetas.length && !filtrando())) secciones.push(seccion(null, sueltos));
    vaciar(zona, secciones, visibles.length ? null
      : h("div", { class: "vacio" }, h("h3", { texto: "Ningún proyecto coincide" }), h("p", { texto: "Prueba con otra búsqueda o quita los filtros." })));
  }
  pintar();

  // Grupos ----------------------------------------------------------------------------------------------------------
  const zonaGrupos = h("div", { class: "seccion pila" });
  function pintarGrupos() { vaciar(zonaGrupos, seccionGrupos()); }
  function seccionGrupos() {
    const existentes = lista.filter((p) => p.existe);
    const nuevo = async () => {
      const datos = await pedirDatos({ titulo: "Nuevo grupo", explicacion: "Por ejemplo «tienda» para su backend, frontend y landing.",
        campos: [{ nombre: "nombre", etiqueta: "Nombre del grupo" }], si: "Siguiente" });
      if (!datos?.nombre) return;
      const eleccion = elegirVarios(existentes.map((p) => ({ valor: p.ruta, titulo: p.nombre, detalle: p.ruta })), []);
      const rutas = await dialogo({ titulo: `Proyectos de «${aSlug(datos.nombre)}»`, contenido: eleccion.nodo,
        acciones: [{ texto: "Crear grupo", clase: "primario", accion: () => {
          const v = eleccion.valores();
          if (v.length < 2) { avisar("Elige al menos dos proyectos", "mal"); return false; }
          return v;
        } }] });
      if (rutas) await guardarGrupo(aSlug(datos.nombre), rutas, "Grupo creado");
    };
    const informe = (titulo, filas, texto) => dialogo({ titulo, cancelar: "Cerrar", contenido: h("ul", { class: "lista" },
      filas.map((f) => h("li", {}, insignia(f.error || f.codigo ? "revisar" : "bien", f.error || f.codigo ? "mal" : "bien"),
        h("span", { texto: `${f.nombre}: ${f.error || texto(f)}` })))) });
    const tarjetaGrupo = (nombre) => {
      const miembros = grupos[nombre];
      const tabla = h("div", { class: "desplazable" });
      const verMatriz = async () => {
        if (tabla.childNodes.length) { tabla.replaceChildren(); return; }
        const m = await obtener("/api/grupos/matriz", { nombre });
        tabla.replaceChildren(h("table", { class: "matriz" },
          h("thead", {}, h("tr", {}, h("th", { texto: "Sistema" }), ...m.repos.map((r) => h("th", { texto: r.nombre })))),
          h("tbody", {}, ...m.sistemas.map((pid) => h("tr", {}, h("td", { texto: pid }), ...m.repos.map((r) => {
            const c = r.sistemas[pid];
            return h("td", {}, c ? insignia(c.version, !c.integro ? "mal" : c.actualizable ? "aviso" : "bien") : "—");
          }))))));
      };
      const quitarMiembro = (ruta) => (miembros.length > 2 ? () => guardarGrupo(nombre, miembros.filter((r) => r !== ruta), "Quitado del grupo") : null);
      const el = h("div", { class: "tarjeta pila grupo" },
        h("div", { class: "fila separada" }, h("h3", { class: "fila" }, icono("conexiones"), nombre),
          h("div", { class: "chips" }, miembros.map((r) => {
            const quitarlo = quitarMiembro(r);
            return h("span", { class: "chip color-gris", title: r }, r.split(/[\\/]/).pop(),
              quitarlo ? h("button", { type: "button", class: "chip-quitar", "aria-label": `Quitar ${r.split(/[\\/]/).pop()} del grupo`, title: "Quitar del grupo", onclick: quitarlo }, icono("cerrar")) : null);
          }))),
        h("div", { class: "fila" },
          boton("Actualizar grupo", async () => informe("Actualizar grupo", await enviar("/api/grupos/actualizar", { nombre }),
            (f) => (f.actualizados || []).join(", ") || "al día"), { clase: "primario pequeno" }),
          boton("Verificar grupo", async () => informe("Verificar grupo", await enviar("/api/grupos/verificar", { nombre }),
            (f) => `${f.codigo ? "con problemas" : "bien"}${f.contratos && f.contratos !== "no instalado" ? ` · contratos ${f.contratos}` : ""}`), { clase: "pequeno" }),
          boton("Ver matriz", verMatriz, { clase: "pequeno" }),
          boton("Borrar grupo", async () => {
            if (await confirmar({ titulo: `Borrar el grupo «${nombre}»`, texto: "Solo se olvida el grupo; los proyectos siguen en tu lista y en sus carpetas.", si: "Borrar" })) {
              await enviar("/api/grupos/borrar", { nombre });
              grupos = await obtener("/api/grupos");
              pintar();
              pintarGrupos();
            }
          }, { clase: "fantasma pequeno" })),
        tabla);
      soltable(el, (a) => a.tipo === "proyecto" && !miembros.includes(a.valor),
        (a) => guardarGrupo(nombre, [...miembros, a.valor], `Añadido al grupo «${nombre}»`));
      return el;
    };
    return [h("div", { class: "fila separada" }, h("h2", { texto: "Grupos" }), boton("Nuevo grupo", nuevo, { clase: "pequeno", icono: "mas" })),
      h("p", { class: "tenue", texto: "Un grupo junta los repos de un mismo sistema (por ejemplo backend, frontend y landing) para actualizarlos y "
        + "verificarlos de una vez. Las carpetas y etiquetas solo ordenan tu lista; los grupos actúan sobre los proyectos. "
        + "Arrastra un proyecto sobre un grupo para añadirlo." }),
      Object.keys(grupos).length ? h("div", { class: "pila" }, Object.keys(grupos).map(tarjetaGrupo))
        : h("div", { class: "soltar-aqui", texto: "Aún no hay grupos." })];
  }
  if (lista.length > 1) pintarGrupos();

  const nuevaCarpeta = async () => { await editarCarpeta(null); };
  return h("div", { class: "mis-proyectos" },
    cabecera("Proyectos", "Ordénalos en carpetas y con etiquetas, arrastrando. Ábrelos para instalar sistemas o cambiar su flujo.",
      boton("Flujos guardados", () => ir("flujos"), { clase: "fantasma", icono: "flujos" }),
      boton("Nueva carpeta", nuevaCarpeta, { icono: "carpeta" }),
      boton("Añadir proyectos", agregar, { clase: "primario", icono: "mas" })),
    h("div", { class: "pila" }, herramientas, barraEtiquetas, resumen),
    zona,
    lista.length > 1 ? zonaGrupos : null);
}
