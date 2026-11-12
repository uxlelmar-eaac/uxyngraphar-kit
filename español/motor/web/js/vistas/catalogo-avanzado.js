// Modo avanzado del catálogo: crear sistemas, editar sus archivos, añadir o quitar piezas y subir la versión.

import { obtener, enviar, catalogo } from "../api.js";
import { h, vaciar, boton, avisar, dialogo, pestanas } from "../ui.js";
import { asistenteIA, sincronizarBorrador } from "./creador.js";

const PIEZAS = ["proceso", "skills", "componentes", "herramientas", "andamiaje", "plantillas", "referencia", "ejemplos", "pruebas", "cambios"];
const FAMILIAS = ["proceso", "codigo", "arquitectura", "documentacion", "seguridad", "producto", "plataforma"];

export async function editorAvanzado(id, recargar) {
  if (!id) id = await crear();
  if (!id) return;
  const archivos = h("select", { "aria-label": "Archivo del sistema" });
  const contenido = h("textarea", { "aria-label": "Contenido del archivo", spellcheck: "false" });
  const errores = h("div", { class: "tenue" });
  const completitud = h("div", { class: "tenue" });
  const pendientes = h("div", { class: "tenue" });
  const piezaSel = h("select", { "aria-label": "Pieza" }, PIEZAS.map((p) => h("option", { value: p, texto: p })));

  async function cargarArchivos(elegido) {
    const lista = await obtener("/api/catalogo/archivos", { id });
    vaciar(archivos, lista.map((a) => h("option", { value: a, texto: a, selected: a === elegido })));
    const c = await obtener("/api/catalogo/completitud", { id });
    completitud.textContent = `Piezas: ${c.piezas.join(", ") || "solo núcleo"}` + (c.faltan_recomendadas.length ? ` · recomendadas que faltan: ${c.faltan_recomendadas.join(", ")}` : "");
    await revisarPendientes();
    await abrir();
  }
  async function revisarPendientes() {
    const p = await obtener("/api/catalogo/pendientes", { id });
    const marcas = p.marcadores.map((m) => `${m.archivo}:${m.linea}`);
    vaciar(pendientes,
      h("div", { texto: p.listo ? "Sin pendientes." : `Pendientes: ${p.errores.length} errores, ${marcas.length} marcadores por rellenar` + (marcas.length ? ` (${marcas.slice(0, 4).join(", ")}${marcas.length > 4 ? "…" : ""})` : "") }),
      h("div", {}, h("b", { texto: "Siguiente: " }), p.siguiente));
  }
  async function abrir() {
    if (!archivos.value) return;
    contenido.value = (await obtener("/api/catalogo/archivo", { id, rel: archivos.value })).contenido;
    errores.textContent = "";
  }
  async function guardar() {
    const r = await enviar("/api/catalogo/archivo", { id, rel: archivos.value, contenido: contenido.value });
    errores.textContent = r.errores.join("; ");
    avisar(r.errores.length ? "Guardado, pero el sistema aún no valida" : "Guardado", r.errores.length ? "mal" : "");
    await revisarPendientes();
  }
  async function nuevoArchivo() {
    const rel = prompt("Ruta del archivo nuevo dentro del sistema (ej.: ejemplos/caso.md)");
    if (!rel) return;
    archivos.append(h("option", { value: rel, texto: rel, selected: true }));
    contenido.value = "";
  }
  async function pieza(accion) {
    const nombre = piezaSel.value;
    if (accion === "quitar" && !confirm(`¿Quitar la pieza ${nombre}? Se borran sus archivos del catálogo.`)) return;
    const r = await enviar("/api/catalogo/pieza", { id, accion, pieza: nombre });
    avisar(`Pieza ${nombre} ${accion === "agregar" ? "agregada" : "quitada"}` + (r.length ? `; pendiente: ${r.join("; ")}` : ""), r.length ? "mal" : "");
    await cargarArchivos(archivos.value);
  }
  async function version(nivel) {
    const v = await enviar("/api/catalogo/version", { id, nivel });
    avisar(`${id} → ${v}. Actualiza los proyectos para recibirla.`);
  }

  archivos.addEventListener("change", abrir);
  await cargarArchivos();
  const sincronia = h("div", { class: "pila" });
  const ia = await asistenteIA(id, () => archivos.value, contenido);
  const cuerpo = h("div", { class: "pila" },
    h("p", { class: "tenue", texto: "Estás editando el catálogo de esta instalación. Los cambios llegan a los proyectos al actualizar sus sistemas." }),
    h("div", { class: "fila" }, h("div", { class: "espacio" }, archivos), boton("Nuevo archivo", nuevoArchivo, { clase: "pequeno" })),
    completitud,
    pendientes,
    h("div", { class: "fila" }, piezaSel, boton("Agregar pieza", () => pieza("agregar"), { clase: "pequeno" }), boton("Quitar pieza", () => pieza("quitar"), { clase: "pequeno peligro" }),
      h("span", { class: "espacio" }), boton("+ parche", () => version("parche"), { clase: "pequeno" }), boton("+ menor", () => version("menor"), { clase: "pequeno" }),
      boton("+ mayor", () => version("mayor"), { clase: "pequeno" })),
    contenido, errores, ia,
    h("div", { class: "fila" }, boton("Subir al Creador web", () => sincronizarBorrador("subir", id, sincronia), { clase: "pequeno" }),
      h("span", { class: "tenue", texto: "Necesita sesión iniciada. Si también cambió en la web, verás las diferencias antes de elegir." })),
    sincronia);
  const d = document.getElementById("dialogo");
  d.style.width = "min(1100px, 96vw)";
  await dialogo({ titulo: `Editar ${id}`, contenido: cuerpo, cancelar: "Cerrar", acciones: [{ texto: "Guardar archivo", clase: "primario", accion: async () => { await guardar(); return false; } }] });
  d.style.width = "";
  await catalogo(true);
  recargar();
}

async function crear() {
  const id = h("input", { type: "text", placeholder: "objeto-de-gobierno (ver NOMENCLATURA.md)", "aria-label": "Identificador" });
  const titulo = h("input", { type: "text", "aria-label": "Título" });
  const descripcion = h("input", { type: "text", "aria-label": "Qué gobierna" });
  const familia = h("select", { "aria-label": "Familia" }, FAMILIAS.map((f) => h("option", { value: f, texto: f })));
  const casillas = PIEZAS.map((p) => h("input", { type: "checkbox", value: p, checked: p === "plantillas" || p === "cambios" }));
  const esqueleto = h("div", { class: "pila" },
    h("label", { class: "campo" }, "Identificador", id), h("label", { class: "campo" }, "Título", titulo),
    h("label", { class: "campo" }, "Qué gobierna", descripcion), h("label", { class: "campo" }, "Familia", familia),
    h("div", {}, h("b", { texto: "Piezas" }), h("div", { class: "fila" }, PIEZAS.map((p, i) => h("label", { class: "casilla" }, casillas[i], p)))),
    h("p", { class: "tenue", texto: "El núcleo (sistema.json, README.md, SISTEMA.md) siempre se crea. Rellena sus marcadores {{…}}: hasta entonces el sistema no valida. «Pendientes» del editor dice dónde están." }));
  const spec = h("textarea", { "aria-label": "Especificación JSON", spellcheck: "false", rows: 18 });
  const resultado = h("div", { class: "tenue" });
  spec.value = JSON.stringify(await obtener("/api/catalogo/plantilla-spec", {}), null, 2);
  const leerSpec = () => {
    try { return JSON.parse(spec.value); } catch (e) { throw new Error(`La especificación no es JSON válido: ${e.message}`); }
  };
  const mostrar = (r) => vaciar(resultado,
    r.errores.length ? h("ul", {}, r.errores.map((e) => h("li", { texto: `error: ${e}` }))) : h("div", { texto: `Sin errores: crearía ${r.archivos.length} archivos.` }),
    r.avisos.length ? h("ul", {}, r.avisos.map((a) => h("li", { texto: `aviso: ${a}` }))) : null);
  const desdeSpec = h("div", { class: "pila", hidden: true },
    h("p", { class: "tenue", texto: "Sistema completo desde una especificación (formato en motor/GENERADOR.md). Solo se crea si valida sin errores." }),
    spec, h("div", { class: "fila" }, boton("Comprobar", async () => mostrar(await enviar("/api/catalogo/generar", { spec: leerSpec(), aplicar: false })), { clase: "pequeno" })),
    resultado);
  let modo = "esqueleto";
  const barra = pestanas([["esqueleto", "Esqueleto"], ["spec", "Desde especificación"]], (m) => {
    modo = m;
    esqueleto.hidden = m !== "esqueleto";
    desdeSpec.hidden = m !== "spec";
  }, "esqueleto");
  const contenido = h("div", { class: "pila" }, barra, esqueleto, desdeSpec);
  return dialogo({ titulo: "Crear sistema", contenido, acciones: [{ texto: "Crear", clase: "primario", accion: async () => {
    if (modo === "spec") {
      const r = await enviar("/api/catalogo/generar", { spec: leerSpec(), aplicar: true });
      mostrar(r);
      if (!r.aplicado) { avisar("No se creó: revisa los errores", "mal"); return false; }
      avisar("Sistema creado desde la especificación");
      return r.id;
    }
    await enviar("/api/catalogo/crear", { id: id.value.trim(), titulo: titulo.value.trim(), descripcion: descripcion.value.trim(), familia: familia.value,
      piezas: casillas.filter((c) => c.checked).map((c) => c.value) });
    avisar("Sistema creado");
    return id.value.trim();
  } }] });
}
