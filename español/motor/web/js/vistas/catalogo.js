// Mercado: catálogo remoto de sistemas. Los borradores y el catálogo local se trabajan en el Taller (ADR 0015).

import { obtener, enviar, nombreDe } from "../api.js";
import { h, vaciar, cabecera, boton, insignia, avisar, dialogo, elegirVarios } from "../ui.js";

const FAMILIAS = { proceso: "Proceso", codigo: "Código", arquitectura: "Arquitectura", documentacion: "Documentación",
  seguridad: "Seguridad", producto: "Producto", plataforma: "Plataforma" };

export async function vista(params, { ir }) {
  if (params.editar) setTimeout(() => ir("creador", { id: params.editar }));

  return h("div", {},
    cabecera("Mercado", "Sistemas publicados que puedes traer e instalar. Para crear o editar, usa el Taller.",
      boton("Ir al taller", () => ir("creador"), { icono: "creador" })),
    servidor(ir),
    flujosDelMercado(),
    h("p", { class: "tenue", style: "margin-top:24px", texto: "Los sistemas ya en este equipo aparecen en el Taller, con insignias web / equipo / instalado." }));
}

// Búsqueda en el servidor (GET /api/sistemas/buscar): sin red muestra el último índice guardado y el aviso.
function servidor(ir) {
  const caja = h("input", { type: "search", placeholder: "Buscar en el Mercado (ej.: secretos, commits, accesibilidad)", "aria-label": "Buscar en el Mercado" });
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
    lista.replaceChildren(...r.sistemas.map((s) => remota(s, r.locales || {}, ir)));
  };
  let espera;
  caja.addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(buscar, 300); });
  setTimeout(buscar);
  return h("div", { class: "pila" }, caja, estado, lista);
}

function remota(s, locales, ir) {
  const ultima = ((s.versiones || [])[0] || {}).version || s.version || "";
  const ref = `${s.editor}/${s.id}`;
  return h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("h3", { texto: s.titulo || s.id }), insignia(FAMILIAS[s.familia] || s.familia || "")),
    h("div", { class: "tenue", texto: s.descripcion || "" }),
    h("div", { class: "fila" }, insignia(ref), ultima ? insignia(`versión ${ultima}`, "acento") : null,
      Number.isFinite(s.estrellas) ? insignia(`★ ${s.estrellas}`) : null,
      s.valoracion ? insignia(`${s.valoracion}/5 · ${s.valoraciones} reseña(s)`) : null,
      s.implementado === true ? insignia("Implementado ✓", "bien") : s.implementado === false ? insignia("por debajo de «implementado»", "aviso") : null,
      (s.traido || []).length ? insignia("en este equipo", "bien") : null, locales[s.id] ? insignia(`local ${locales[s.id]}`) : null),
    h("div", { class: "acciones" },
      boton("Traer", async () => {
        await enviar("/api/sistemas/traer", { ref: ultima ? `${ref}@${ultima}` : ref });
        avisar(`«${s.titulo || s.id}» guardado en este equipo`, "bien");
        if (ir) ir("creador", { id: s.id });
      }, { clase: "pequeno" }),
      boton("Instalar en proyectos", () => instalarEn([{ id: s.id, titulo: s.titulo || s.id }]), { clase: "primario pequeno" })));
}

async function instalarEn(sistemas) {
  const lista = (await obtener("/api/proyectos")).filter((p) => p.existe);
  if (!lista.length) return avisar("Primero añade algún proyecto en «Proyectos».", "mal");
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

// Flujos publicados (servidor >= 1.1.0): secuencias de sistemas publicados que otros comparten, con estrellas y comentarios.
function flujosDelMercado() {
  const lista = h("div", { class: "rejilla" });
  const estado = h("p", { class: "tenue", texto: "Cargando flujos…" });
  setTimeout(async () => {
    let r;
    try { r = await obtener("/api/flujos/mercado"); } catch (e) { estado.textContent = String(e.message || e); return; }
    const flujos = r.flujos || [];
    estado.textContent = flujos.length ? `${flujos.length} flujos publicados` : (r.error ? `Sin flujos del Mercado (${r.error}).` : "Aún no hay flujos publicados.");
    lista.replaceChildren(...flujos.map((f) => h("div", { class: "tarjeta tarjeta-item" },
      h("h3", { texto: f.nombre || f.slug }),
      h("div", { class: "tenue", texto: f.descripcion || "" }),
      h("div", { class: "fila" }, insignia(`${f.editor}/${f.slug}`), insignia(`★ ${f.estrellas || 0}`), insignia(`${f.comentarios || 0} comentario(s)`),
        insignia(`${(f.sistemas || []).length} sistemas`, "acento")),
      h("div", { class: "acciones" }, boton("Traer a mis flujos", async () => {
        const g = await enviar("/api/flujos/traer", { ref: `${f.editor}/${f.slug}` });
        avisar(`Flujo guardado como «${g.id}» con sus sistemas`, "bien");
      }, { clase: "pequeno" })))));
  });
  return h("div", { class: "pila", style: "margin-top:24px" }, h("h2", { texto: "Flujos del Mercado" }), estado, lista);
}
