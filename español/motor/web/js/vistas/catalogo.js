// Catálogo: buscar sistemas de gobernanza en el servidor, traerlos e instalarlos en varios proyectos a la vez.
// Debajo, el catálogo local (solo para quien escribe sistemas: el instalador llega vacío).

import { obtener, enviar, catalogo, nombreDe } from "../api.js";
import { h, vaciar, cabecera, boton, insignia, avisar, dialogo, elegirVarios } from "../ui.js";
import { editorAvanzado } from "./catalogo-avanzado.js";

const FAMILIAS = { proceso: "Proceso", codigo: "Código", arquitectura: "Arquitectura", documentacion: "Documentación",
  seguridad: "Seguridad", producto: "Producto", plataforma: "Plataforma" };

export async function vista(params, { modoAvanzado, recargar }) {
  const cat = await catalogo(true);
  const filtro = h("input", { type: "search", placeholder: "¿Qué problema quieres resolver? (ej.: secretos, accesibilidad, commits)", "aria-label": "Buscar en el catálogo" });
  const familias = [...new Set(cat.map((m) => m.familia).filter(Boolean))].sort();
  const familia = h("select", { "aria-label": "Filtrar por tipo" }, h("option", { value: "", texto: "Todos los tipos" }),
    familias.map((f) => h("option", { value: f, texto: FAMILIAS[f] || f })));
  const rejilla = h("div", { class: "rejilla" });

  const texto = (m) => [m.titulo, m.descripcion, ...((m.alcance || {}).problemas || []).map((p) => p.descripcion), ...(m.activacion || [])].join(" ").toLowerCase();
  const pintar = () => {
    const t = filtro.value.trim().toLowerCase();
    const visibles = cat.filter((m) => (!familia.value || m.familia === familia.value) && (!t || texto(m).includes(t)));
    rejilla.replaceChildren(...visibles.map((m) => tarjeta(m)));
    if (!visibles.length) rejilla.append(h("p", { class: "tenue", texto: "No hay sistemas que coincidan." }));
  };

  const tarjeta = (m) => h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("h3", { texto: m.titulo }), insignia(FAMILIAS[m.familia] || m.familia || "")),
    h("div", { class: "tenue", texto: m.descripcion }),
    (m.errores || []).length ? h("div", { class: "banda mal", texto: "Este sistema tiene errores y no se puede instalar." }) : null,
    h("div", { class: "acciones" },
      boton("Ver detalles", () => detalles(m), { clase: "pequeno" }),
      (m.errores || []).length ? null : boton("Instalar en proyectos", () => instalarEn([m]), { clase: "primario pequeno" }),
      modoAvanzado() ? boton("Editar", () => editorAvanzado(m.id, recargar), { clase: "pequeno fantasma" }) : null));

  filtro.addEventListener("input", pintar);
  familia.addEventListener("change", pintar);
  pintar();
  if (params.editar && modoAvanzado()) setTimeout(() => editorAvanzado(params.editar, recargar));

  return h("div", {},
    cabecera("Sistemas de gobernanza", "Cada sistema resuelve un conjunto concreto de problemas en tus proyectos. Búscalos en el servidor e instálalos.",
      modoAvanzado() ? boton("Crear sistema", () => editorAvanzado(null, recargar), { icono: "mas" }) : null),
    servidor(),
    cat.length ? h("div", {},
      h("h2", { texto: `Catálogo local (${cat.length})` }),
      h("p", { class: "tenue", texto: "Sistemas con fuente en este equipo. Si uno está también en el servidor, se instala la versión más alta." }),
      h("div", { class: "fila", style: "margin-bottom:16px" }, h("div", { class: "espacio", style: "min-width:260px" }, filtro), h("div", {}, familia)),
      rejilla) : null);
}

// Búsqueda en el servidor (GET /api/sistemas/buscar): sin red muestra el último índice guardado y el aviso.
function servidor() {
  const caja = h("input", { type: "search", placeholder: "Buscar en el servidor (ej.: secretos, commits, accesibilidad)", "aria-label": "Buscar en el servidor" });
  const estado = h("p", { class: "tenue" });
  const lista = h("div", { class: "rejilla" });
  let turno = 0;
  const buscar = async () => {
    const mio = ++turno;
    estado.textContent = "Buscando…";
    let r;
    try { r = await obtener(`/api/sistemas/buscar?q=${encodeURIComponent(caja.value.trim())}`); }
    catch (e) { if (mio === turno) estado.textContent = String(e.message || e); return; }
    if (mio !== turno) return;
    estado.textContent = r.error ? `Sin conexión con el servidor (${r.error}).${r.sistemas.length ? " Se muestra el último índice guardado." : ""}`
      : `${r.sistemas.length} sistemas en ${r.servidor}`;
    lista.replaceChildren(...r.sistemas.map((s) => remota(s, r.locales || {})));
  };
  let espera;
  caja.addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(buscar, 300); });
  setTimeout(buscar);
  return h("div", { class: "tarjeta", style: "margin-bottom:24px" }, h("h2", { texto: "En el servidor" }), caja, estado, lista);
}

function remota(s, locales) {
  const ultima = ((s.versiones || [])[0] || {}).version || s.version || "";
  const ref = `${s.editor}/${s.id}`;
  return h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("h3", { texto: s.titulo || s.id }), insignia(FAMILIAS[s.familia] || s.familia || "")),
    h("div", { class: "tenue", texto: s.descripcion || "" }),
    h("div", { class: "fila" }, insignia(ref), ultima ? insignia(`versión ${ultima}`, "acento") : null,
      (s.traido || []).length ? insignia("en este equipo", "bien") : null, locales[s.id] ? insignia(`local ${locales[s.id]}`) : null),
    h("div", { class: "acciones" },
      boton("Traer", async () => { await enviar("/api/sistemas/traer", { ref: ultima ? `${ref}@${ultima}` : ref }); avisar(`«${s.titulo || s.id}» guardado en este equipo`, "bien"); },
        { clase: "pequeno" }),
      boton("Instalar en proyectos", () => instalarEn([{ id: s.id, titulo: s.titulo || s.id }]), { clase: "primario pequeno" })));
}

function detalles(m) {
  const alcance = m.alcance || {};
  return dialogo({ titulo: m.titulo, cancelar: "Cerrar", contenido: h("div", { class: "pila" },
    h("p", { texto: m.descripcion }),
    h("div", { class: "fila" }, insignia(`versión ${m.version}`), insignia(FAMILIAS[m.familia] || m.familia || "", "acento")),
    h("h3", { texto: "Problemas que resuelve" }),
    h("ul", {}, (alcance.problemas || []).map((p) => h("li", { texto: p.descripcion }))),
    (alcance.fuera_de_alcance || []).length ? h("details", {}, h("summary", { texto: "Lo que no cubre" }),
      h("ul", {}, alcance.fuera_de_alcance.map((f) => h("li", { texto: f.tema + (f.derivar_a ? ` (lo cubre: ${f.derivar_a})` : "") })))) : null,
    h("h3", { texto: "Cómo pedírselo al asistente" }),
    h("p", { class: "tenue" }, "Escribe en tu pedido: ", h("code", { texto: `usa el sistema ${(m.activacion || [m.id])[0]}` })),
    (m.avisos || []).length ? h("details", {}, h("summary", { texto: "Avisos del catálogo" }), h("ul", {}, m.avisos.map((a) => h("li", { texto: a })))) : null),
    acciones: (m.errores || []).length ? [] : [{ texto: "Instalar en proyectos", clase: "primario", accion: () => { setTimeout(() => instalarEn([m])); return true; } }] });
}

async function instalarEn(sistemas) {
  const lista = (await obtener("/api/proyectos")).filter((p) => p.existe);
  if (!lista.length) return avisar("Primero añade algún proyecto en «Mis proyectos».", "mal");
  const ids = sistemas.map((p) => p.id);
  const opciones = lista.map((p) => ({ valor: p.ruta, titulo: p.nombre, detalle: ids.every((i) => p.sistemas.includes(i)) ? "ya lo tiene" : p.grupo }));
  const eleccion = elegirVarios(opciones);
  const repos = await dialogo({ titulo: `Instalar «${sistemas.map((p) => p.titulo).join(", ")}»`,
    contenido: h("div", { class: "pila" }, h("p", { class: "tenue", texto: "Marca los proyectos donde quieres instalarlo." }), eleccion.nodo),
    acciones: [{ texto: "Instalar", clase: "primario", accion: () => eleccion.valores().length ? eleccion.valores() : (avisar("Marca al menos un proyecto", "mal"), false) }] });
  if (!repos) return;
  const resultados = await enviar("/api/catalogo/instalar-en", { ids, repos });
  const zona = h("ul", { class: "lista" });
  vaciar(zona, resultados.map((r) => h("li", {}, h("b", { class: "espacio", texto: nombreDe(r.ruta) }),
    r.error ? h("span", { class: "insignia mal", texto: r.error }) : insignia(r.instalados.length ? "instalado" : "ya lo tenía", "bien"))));
  await dialogo({ titulo: "Resultado", contenido: zona, cancelar: "Cerrar" });
}
