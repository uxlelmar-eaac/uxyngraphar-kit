// Flujos guardados: plantillas de «qué sistemas y cómo trabaja el asistente» para reutilizar en cualquier proyecto.

import { obtener, enviar, catalogo, nombreDe } from "../api.js";
import { h, vaciar, cabecera, boton, insignia, vacio, confirmar, avisar, dialogo, elegirVarios, descargarJSON } from "../ui.js";
import { diagrama, editorFlujo, MODOS, FLUJO_VACIO } from "../flujo.js";

export async function vista(_params, { ir, recargar }) {
  const [guardados, cat] = await Promise.all([obtener("/api/flujos"), catalogo()]);
  const titulos = cat.map((m) => ({ id: m.id, titulo: m.titulo, descripcion: m.descripcion }));

  const importar = () => new Promise((resolver) => {
    const entrada = h("input", { type: "file", accept: ".json,application/json", hidden: true });
    entrada.addEventListener("change", async () => {
      try {
        const datos = JSON.parse(await entrada.files[0].text());
        await enviar("/api/flujos/importar", { datos });
        avisar("Flujo importado");
        recargar();
      } catch (e) {
        avisar(e instanceof SyntaxError ? "Ese archivo no es un flujo guardado válido." : e.message, "mal");
      }
      entrada.remove();
      resolver();
    });
    document.body.append(entrada);
    entrada.click();
  });

  const tarjeta = (g) => h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("h3", { texto: g.nombre }), insignia(MODOS[g.flujo?.modo]?.titulo || "", "acento")),
    g.descripcion ? h("div", { class: "tenue", texto: g.descripcion }) : null,
    h("div", { class: "fila" }, g.sistemas.map((id) => insignia((titulos.find((t) => t.id === id) || {}).titulo || id))),
    diagrama(g.flujo, titulos),
    h("div", { class: "acciones" },
      boton("Aplicar a proyectos", () => aplicar(g), { clase: "primario pequeno" }),
      boton("Editar", async () => { if (await editar(g, titulos)) recargar(); }, { clase: "pequeno" }),
      boton("Duplicar", async () => { await enviar("/api/flujos/duplicar", { id: g.id }); avisar("Duplicado"); recargar(); }, { clase: "pequeno" }),
      boton("Exportar", async () => descargarJSON(`${g.id}.uxyngraphar-flujo.json`, await obtener("/api/flujos/exportar", { id: g.id })), { clase: "pequeno", icono: "descargar" }),
      boton("Borrar", async () => {
        if (!(await confirmar({ titulo: `Borrar «${g.nombre}»`, texto: "Se borra de tu biblioteca. Los proyectos donde ya lo aplicaste no cambian.", si: "Borrar", peligro: true }))) return;
        await enviar("/api/flujos/borrar", { id: g.id });
        avisar("Borrado");
        recargar();
      }, { clase: "pequeno peligro" })));

  return h("div", {},
    cabecera("Flujos guardados", "Guarda una combinación de sistemas y una forma de trabajar, y aplícala a cualquier proyecto con un clic.",
      boton("Importar", importar, { icono: "subir" }),
      boton("Nuevo flujo", async () => { if (await editar(null, titulos)) recargar(); }, { clase: "primario", icono: "mas" })),
    guardados.length ? h("div", { class: "rejilla" }, guardados.map(tarjeta))
      : vacio("Aún no tienes flujos guardados", "Crea uno aquí o, desde un proyecto que ya tengas configurado, usa «Guardar como flujo reutilizable».",
        boton("Crear mi primer flujo", async () => { if (await editar(null, titulos)) recargar(); }, { clase: "primario", icono: "mas" }), boton("Ver mis proyectos", () => ir("proyectos"))));
}

async function aplicar(g) {
  const lista = (await obtener("/api/proyectos")).filter((p) => p.existe);
  if (!lista.length) return avisar("Primero añade algún proyecto en «Mis proyectos».", "mal");
  const eleccion = elegirVarios(lista.map((p) => ({ valor: p.ruta, titulo: p.nombre, detalle: `${p.grupo} · ${p.sistemas.length} sistema(s)` })));
  const repos = await dialogo({ titulo: `Aplicar «${g.nombre}»`, contenido: h("div", { class: "pila" },
    h("p", { class: "tenue", texto: "En cada proyecto se instalan los sistemas que falten y se cambia el flujo del asistente. Los sistemas que ya tenga no se tocan." }), eleccion.nodo),
    acciones: [{ texto: "Aplicar", clase: "primario", accion: () => eleccion.valores().length ? eleccion.valores() : (avisar("Marca al menos un proyecto", "mal"), false) }] });
  if (!repos) return;
  const resultados = await enviar("/api/flujos/aplicar", { id: g.id, repos });
  const fallos = resultados.filter((r) => r.error);
  await dialogo({ titulo: fallos.length ? "Aplicado con algunos problemas" : "Flujo aplicado", cancelar: "Cerrar",
    contenido: h("ul", { class: "lista" }, resultados.map((r) => h("li", {}, h("b", { class: "espacio", texto: nombreDe(r.ruta) }),
      r.error ? h("span", { class: "insignia mal", texto: r.error }) : insignia(r.instalados.length ? `${r.instalados.length} sistema(s) instalados` : "listo", "bien")))) });
}

// Crear (g = null) o editar un flujo guardado. Resuelve con el id guardado o null.
async function editar(g, titulos) {
  const datos = g ? structuredClone(g) : { nombre: "", descripcion: "", sistemas: [], flujo: { ...FLUJO_VACIO } };
  const nombre = h("input", { type: "text", value: datos.nombre, placeholder: "Ej.: Frontend con accesibilidad", "aria-label": "Nombre" });
  const descripcion = h("input", { type: "text", value: datos.descripcion || "", "aria-label": "Descripción" });
  const elegidos = new Set(datos.sistemas);
  let flujo = datos.flujo;
  const zonaEditor = h("div");
  let editor;
  const pintarEditor = () => {
    const disponibles = titulos.filter((t) => elegidos.has(t.id));
    const limpio = { ...flujo, leer_por_defecto: (flujo.leer_por_defecto || []).filter((x) => elegidos.has(x)),
      secuencia: (flujo.secuencia || []).filter((x) => elegidos.has(x)), trabajar_con: elegidos.has(flujo.trabajar_con) ? flujo.trabajar_con : null };
    editor = editorFlujo(limpio, disponibles, (v) => { flujo = v; });
    flujo = editor.valor();
    vaciar(zonaEditor, editor.nodo);
  };
  const filtro = h("input", { type: "search", placeholder: "Buscar sistemas…", "aria-label": "Buscar sistemas" });
  const lista = h("ul", { class: "lista desplazable" });
  const pintarLista = () => {
    const t = filtro.value.trim().toLowerCase();
    vaciar(lista, titulos.filter((p) => !t || (p.titulo + " " + p.descripcion).toLowerCase().includes(t)).map((p) => h("li", {},
      h("label", { class: "casilla", style: "flex:1" }, h("input", { type: "checkbox", checked: elegidos.has(p.id), onchange: (e) => {
        e.target.checked ? elegidos.add(p.id) : elegidos.delete(p.id);
        pintarEditor();
      } }), h("span", {}, h("b", { texto: p.titulo }), h("div", { class: "tenue", texto: p.descripcion }))))));
  };
  filtro.addEventListener("input", pintarLista);
  pintarLista();
  pintarEditor();
  const contenido = h("div", { class: "pila" },
    h("label", { class: "campo" }, "Nombre", nombre), h("label", { class: "campo" }, "Descripción (opcional)", descripcion),
    h("h3", { texto: "1. Sistemas que incluye" }), filtro, lista,
    h("h3", { texto: "2. Cómo trabaja el asistente" }), zonaEditor);
  return dialogo({ titulo: g ? `Editar «${g.nombre}»` : "Nuevo flujo guardado", contenido, acciones: [{ texto: "Guardar flujo", clase: "primario", accion: async () => {
    if (!nombre.value.trim()) { avisar("Ponle un nombre al flujo", "mal"); return false; }
    return enviar("/api/flujos/guardar", { flujo: { id: g?.id, nombre: nombre.value.trim(), descripcion: descripcion.value.trim(), sistemas: [...elegidos], flujo: editor.valor() } });
  } }] });
}
