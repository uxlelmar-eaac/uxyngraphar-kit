// Flujos guardados: plantillas de «qué sistemas y cómo trabaja el asistente» para reutilizar en cualquier proyecto.
// Pensado para quien no programa: cómo funciona en tres pasos, plantillas para empezar, buscador, filtros por forma de
// trabajar, un asistente de creación por pasos y una vista previa de qué cambiará en cada proyecto antes de aplicar.

import { obtener, enviar, catalogo, nombreDe } from "../api.js";
import { h, vaciar, cabecera, boton, insignia, confirmar, avisar, dialogo, descargarJSON, ocupado } from "../ui.js";
import { diagrama, editorFlujo, resumen, iconoFlujo, MODOS, FLUJO_VACIO } from "../flujo.js";

const FAMILIAS = { proceso: "Proceso", codigo: "Código", arquitectura: "Arquitectura", documentacion: "Documentación",
  seguridad: "Seguridad", producto: "Producto", plataforma: "Plataforma" };

const TRAZOS = {
  aplicar: "M5 12h14M13 6l6 6-6 6",
  editar: "M4 20h4L19 9l-4-4L4 16zM13 7l4 4",
  duplicar: "M8 8h11v11H8zM5 16V5h11",
  exportar: "M12 4v12M6 10l6 6 6-6M4 20h16",
  borrar: "M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13",
  proyecto: "M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
  sistemas: "M12 3l8 4.5v9L12 21l-8-4.5v-9zM12 12l8-4.5M12 12v9M12 12L4 7.5",
  como: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 8v4l3 2",
};
const ico = (nombre) => {
  const svg = iconoFlujo("flecha");
  svg.querySelector("path").setAttribute("d", TRAZOS[nombre]);
  return svg;
};

// Lo que el usuario eligió en la barra sobrevive a «recargar» (que vuelve a pintar la vista entera).
const estado = { texto: "", modo: "", orden: leerPreferencia("orden", "nombre") };

function leerPreferencia(clave, defecto) {
  try { return localStorage.getItem(`uxyn-flujos-${clave}`) || defecto; } catch { return defecto; }
}
function guardarPreferencia(clave, valor) {
  try { localStorage.setItem(`uxyn-flujos-${clave}`, valor); } catch { /* sin almacenamiento: solo dura esta visita */ }
}

// Botón de solo icono con texto accesible y aviso al pasar el ratón.
function botonIcono(nombre, texto, accion, clase = "") {
  const b = h("button", { type: "button", class: `boton pequeno icono-solo ${clase}`.trim(), title: texto, "aria-label": texto }, ico(nombre));
  b.addEventListener("click", () => ocupado(b, accion));
  return b;
}

const sistemasTexto = (n) => `${n} sistema${n === 1 ? "" : "s"}`;
const proyectosTexto = (n) => `${n} proyecto${n === 1 ? "" : "s"}`;

export async function vista(_params, { ir, recargar }) {
  const [guardados, cat] = await Promise.all([obtener("/api/flujos"), catalogo()]);
  const titulos = cat.filter((m) => !(m.errores || []).length)
    .map((m) => ({ id: m.id, titulo: m.titulo, descripcion: m.descripcion, familia: m.familia }));
  const nombreSistema = (id) => (titulos.find((t) => t.id === id) || {}).titulo || id;

  const nuevo = async (opciones) => { if (await editar(null, titulos, opciones)) recargar(); };

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

  const acciones = [
    boton("Importar", importar, { icono: "subir", titulo: "Añadir un flujo desde un archivo .json que te pasaron" }),
    boton("Desde un proyecto", async () => { if (await desdeProyecto()) recargar(); }, { icono: "proyectos", titulo: "Copiar los sistemas y la forma de trabajar de un proyecto que ya tienes" }),
    boton("Nuevo flujo", () => nuevo(), { clase: "primario", icono: "mas" }),
  ];
  const cab = cabecera("Flujos guardados", "Guarda una combinación de sistemas y una forma de trabajar, y aplícala a cualquier proyecto con un clic.", ...acciones);

  if (!guardados.length) {
    return h("div", { class: "vista-flujos" }, cab, comoFunciona(),
      h("section", { class: "seccion" }, h("h2", { texto: "Empieza con una plantilla" }),
        h("p", { class: "tenue", texto: "Elige cómo quieres que trabaje el asistente. Después solo tienes que marcar los sistemas." }),
        plantillas(nuevo)),
      h("div", { class: "banda acento otras-formas" }, iconoFlujo("pedido"),
        h("span", { class: "espacio", texto: "¿Ya tienes un proyecto configurado? Conviértelo en flujo y reutilízalo en los demás." }),
        boton("Usar un proyecto", async () => { if (await desdeProyecto()) recargar(); }, { clase: "pequeno" }),
        boton("Ver mis proyectos", () => ir("proyectos"), { clase: "pequeno fantasma" })));
  }

  // Barra de herramientas: buscar, filtrar por forma de trabajar y ordenar.
  const buscador = h("input", { type: "search", value: estado.texto, placeholder: "Buscar por nombre, descripción o sistema…", "aria-label": "Buscar flujos" });
  const cuenta = (modo) => guardados.filter((g) => !modo || (g.flujo?.modo || "manual") === modo).length;
  const chips = h("div", { class: "chips-filtro", role: "radiogroup", "aria-label": "Filtrar por forma de trabajar" });
  const pintarChips = () => vaciar(chips, [["", "Todos", null], ...Object.entries(MODOS).map(([id, m]) => [id, m.titulo, m.icono])]
    .filter(([id]) => !id || cuenta(id))
    .map(([id, texto, icono]) => h("button", { type: "button", class: "chip", role: "radio", "aria-checked": String(estado.modo === id),
      onclick: () => { estado.modo = id; pintarChips(); pintar(); } }, icono ? iconoFlujo(icono) : null, texto, h("span", { class: "chip-cuenta", texto: String(cuenta(id)) }))));
  const orden = h("select", { "aria-label": "Ordenar flujos" },
    [["nombre", "Nombre (A-Z)"], ["recientes", "Cambiados hace poco"], ["sistemas", "Más sistemas"]]
      .map(([v, t]) => h("option", { value: v, texto: t, selected: estado.orden === v })));
  const rejilla = h("div", { class: "rejilla rejilla-flujos" });
  const contador = h("span", { class: "tenue" });

  const texto = (g) => [g.nombre, g.descripcion, ...g.sistemas.map(nombreSistema), MODOS[g.flujo?.modo]?.titulo].join(" ").toLowerCase();
  function pintar() {
    const t = estado.texto.trim().toLowerCase();
    const visibles = guardados.filter((g) => (!estado.modo || (g.flujo?.modo || "manual") === estado.modo) && (!t || texto(g).includes(t)));
    const ordenar = { nombre: () => 0, recientes: (a, b) => String(b.actualizado || "").localeCompare(String(a.actualizado || "")),
      sistemas: (a, b) => b.sistemas.length - a.sistemas.length }[estado.orden] || (() => 0);
    visibles.sort(ordenar);
    contador.textContent = visibles.length === guardados.length ? `${guardados.length} flujo${guardados.length === 1 ? "" : "s"}`
      : `${visibles.length} de ${guardados.length}`;
    vaciar(rejilla, visibles.length ? visibles.map((g) => tarjeta(g)) : h("div", { class: "vacio" },
      h("h3", { texto: "Ningún flujo coincide" }), h("p", { texto: "Prueba con otra palabra o quita el filtro." }),
      boton("Quitar filtros", () => { estado.texto = ""; estado.modo = ""; buscador.value = ""; pintarChips(); pintar(); }, { clase: "pequeno" })));
  }
  buscador.addEventListener("input", () => { estado.texto = buscador.value; pintar(); });
  orden.addEventListener("change", () => { estado.orden = orden.value; guardarPreferencia("orden", orden.value); pintar(); });

  const tarjeta = (g) => {
    const modo = MODOS[g.flujo?.modo] || MODOS.manual;
    const visibles = g.sistemas.slice(0, 4);
    return h("article", { class: `tarjeta tarjeta-flujo tono-${modo.tono}` },
      h("div", { class: "tarjeta-flujo-cinta" }, iconoFlujo(modo.icono), h("span", { texto: modo.titulo })),
      h("div", { class: "tarjeta-flujo-cuerpo" },
        h("h3", { texto: g.nombre }),
        g.descripcion ? h("p", { class: "tenue", texto: g.descripcion }) : null,
        h("p", { class: "resumen-flujo", texto: resumen(g.flujo, titulos) }),
        diagrama(g.flujo, titulos, { compacto: true }),
        h("div", { class: "fila etiquetas-sistemas" }, visibles.map((id) => insignia(nombreSistema(id))),
          g.sistemas.length > visibles.length ? insignia(`+${g.sistemas.length - visibles.length} más`, "acento") : null,
          !g.sistemas.length ? h("span", { class: "tenue", texto: "Sin sistemas" }) : null),
        h("div", { class: "tenue meta-flujo" }, sistemasTexto(g.sistemas.length), g.actualizado ? ` · cambiado el ${fecha(g.actualizado)}` : "")),
      h("div", { class: "acciones tarjeta-flujo-pie" },
        boton("Aplicar a proyectos", () => aplicar(g, titulos), { clase: "primario pequeno", icono: "flecha" }),
        h("span", { class: "espacio" }),
        botonIcono("editar", "Editar", async () => { if (await editar(g, titulos)) recargar(); }),
        botonIcono("duplicar", "Duplicar", async () => { await enviar("/api/flujos/duplicar", { id: g.id }); avisar("Duplicado"); recargar(); }),
        botonIcono("exportar", "Exportar a un archivo para compartirlo", async () => descargarJSON(`${g.id}.uxyngraphar-flujo.json`, await obtener("/api/flujos/exportar", { id: g.id }))),
        botonIcono("borrar", "Borrar", async () => {
          if (!(await confirmar({ titulo: `Borrar «${g.nombre}»`, texto: "Se borra de tu biblioteca. Los proyectos donde ya lo aplicaste no cambian.", si: "Borrar", peligro: true }))) return;
          await enviar("/api/flujos/borrar", { id: g.id });
          avisar("Borrado");
          recargar();
        }, "peligro")));
  };

  pintarChips();
  pintar();
  const ayuda = h("details", { class: "como-funciona-plegable", open: leerPreferencia("ayuda", "abierta") === "abierta" },
    h("summary", { texto: "¿Cómo funcionan los flujos? · Plantillas para empezar" }), comoFunciona(), plantillas(nuevo));
  ayuda.addEventListener("toggle", () => guardarPreferencia("ayuda", ayuda.open ? "abierta" : "cerrada"));
  return h("div", { class: "vista-flujos" }, cab, ayuda,
    h("div", { class: "barra-flujos" }, h("div", { class: "espacio buscador-flujos" }, buscador), orden),
    h("div", { class: "fila separada" }, chips, contador),
    rejilla);
}

const fecha = (texto) => {
  const [d] = String(texto).split(" ");
  const [a, m, dia] = d.split("-");
  return a && m && dia ? `${Number(dia)}/${Number(m)}/${a}` : texto;
};

function comoFunciona() {
  const paso = (n, icono, titulo, texto) => h("li", { class: "paso-explicado" },
    h("span", { class: "paso-explicado-icono" }, ico(icono), h("span", { class: "paso-explicado-n", texto: String(n) })),
    h("b", { texto: titulo }), h("span", { class: "tenue", texto }));
  return h("ol", { class: "como-funciona", "aria-label": "Cómo funciona un flujo" },
    paso(1, "sistemas", "Elige sistemas", "Las normas y procesos que quieres que siga el asistente."),
    paso(2, "como", "Decide cómo trabaja", "Solo cuando lo pidas, siempre, o paso a paso en orden."),
    paso(3, "aplicar", "Aplícalo a tus proyectos", "Con un clic, en uno o en muchos proyectos a la vez."));
}

function plantillas(nuevo) {
  return h("div", { class: "plantillas" }, Object.entries(MODOS).map(([id, m]) => h("button", { type: "button", class: `plantilla tono-${m.tono}`,
    onclick: () => nuevo({ modo: id, paso: 1 }) },
    h("span", { class: "plantilla-icono" }, iconoFlujo(m.icono)),
    h("b", { texto: m.titulo }), h("span", { class: "tenue", texto: m.texto }),
    h("span", { class: "plantilla-ir" }, "Usar esta forma", iconoFlujo("flecha")))));
}

// Aplicar: elegir proyectos viendo antes qué cambiará en cada uno.
async function aplicar(g, titulos) {
  const lista = (await obtener("/api/proyectos")).filter((p) => p.existe);
  if (!lista.length) return avisar("Primero añade algún proyecto en «Mis proyectos».", "mal");
  const marcados = new Set();
  const nuevoModo = MODOS[g.flujo?.modo]?.titulo || g.flujo?.modo;
  const filtro = h("input", { type: "search", placeholder: "Buscar proyecto…", "aria-label": "Buscar proyecto" });
  const filas = h("ul", { class: "lista desplazable lista-aplicar" });
  const resumenSeleccion = h("div", { class: "banda acento resumen-aplicar", role: "status" });
  const faltan = (p) => g.sistemas.filter((id) => !(p.sistemas || []).includes(id));

  const pintarResumen = () => {
    const elegidos = lista.filter((p) => marcados.has(p.ruta));
    const instalar = elegidos.reduce((n, p) => n + faltan(p).length, 0);
    resumenSeleccion.textContent = elegidos.length
      ? `${proyectosTexto(elegidos.length)} marcado${elegidos.length === 1 ? "" : "s"}. Se instalarán ${instalar} sistema${instalar === 1 ? "" : "s"} en total y el asistente pasará a «${nuevoModo}».`
      : "Marca los proyectos donde quieres usar este flujo.";
  };
  const pintar = () => {
    const t = filtro.value.trim().toLowerCase();
    vaciar(filas, lista.filter((p) => !t || `${p.nombre} ${p.grupo}`.toLowerCase().includes(t)).map((p) => {
      const nuevos = faltan(p);
      const cambiaModo = p.modo !== (g.flujo?.modo || "manual");
      return h("li", {}, h("label", { class: "casilla", style: "flex:1" },
        h("input", { type: "checkbox", checked: marcados.has(p.ruta), onchange: (e) => { e.target.checked ? marcados.add(p.ruta) : marcados.delete(p.ruta); pintarResumen(); } }),
        h("span", { class: "espacio" }, h("b", { texto: p.nombre }), h("div", { class: "tenue", texto: `${p.grupo} · ${sistemasTexto((p.sistemas || []).length)} · ahora: ${MODOS[p.modo]?.titulo || "sin flujo"}` }))),
        h("span", { class: "fila", style: "gap:6px;justify-content:flex-end" },
          nuevos.length ? insignia(`+${nuevos.length} por instalar`, "aviso") : insignia("tiene todos", "bien"),
          cambiaModo ? insignia("cambia la forma", "acento") : null));
    }));
  };
  const todos = (si) => { lista.forEach((p) => si ? marcados.add(p.ruta) : marcados.delete(p.ruta)); pintar(); pintarResumen(); };
  filtro.addEventListener("input", pintar);
  pintar();
  pintarResumen();

  const repos = await dialogo({ titulo: `Aplicar «${g.nombre}»`, contenido: h("div", { class: "pila" },
    diagrama(g.flujo, titulos),
    h("p", { class: "tenue", texto: "En cada proyecto se instalan los sistemas que falten y se cambia la forma de trabajar del asistente. Los sistemas que ya tenga no se tocan." }),
    h("div", { class: "fila" }, h("div", { class: "espacio" }, filtro),
      h("button", { type: "button", class: "boton pequeno", onclick: () => todos(true) }, "Marcar todos"),
      h("button", { type: "button", class: "boton pequeno fantasma", onclick: () => todos(false) }, "Ninguno")),
    filas, resumenSeleccion),
    acciones: [{ texto: "Aplicar", clase: "primario", accion: () => marcados.size ? [...marcados] : (avisar("Marca al menos un proyecto", "mal"), false) }] });
  if (!repos) return;
  const resultados = await enviar("/api/flujos/aplicar", { id: g.id, repos });
  const fallos = resultados.filter((r) => r.error);
  await dialogo({ titulo: fallos.length ? "Aplicado con algunos problemas" : "Flujo aplicado", cancelar: "Cerrar",
    contenido: h("div", { class: "pila" },
      h("div", { class: `banda ${fallos.length ? "aviso" : "bien"}`, texto: fallos.length
        ? `Listo en ${resultados.length - fallos.length} de ${resultados.length}. Revisa los que muestran un problema.`
        : `Listo en ${proyectosTexto(resultados.length)}. El asistente lo usará desde su próximo pedido.` }),
      h("ul", { class: "lista" }, resultados.map((r) => h("li", {}, h("b", { class: "espacio", texto: nombreDe(r.ruta) }),
        r.error ? h("span", { class: "insignia mal", texto: r.error }) : insignia(r.instalados.length ? `${sistemasTexto(r.instalados.length)} instalado${r.instalados.length === 1 ? "" : "s"}` : "listo", "bien"))))) });
}

// Crear un flujo copiando los sistemas y la forma de trabajar de un proyecto.
async function desdeProyecto() {
  const lista = (await obtener("/api/proyectos")).filter((p) => p.existe && (p.sistemas || []).length);
  if (!lista.length) { avisar("Ningún proyecto tiene sistemas instalados todavía. Instálalos desde «Mis proyectos» o el catálogo.", "mal"); return null; }
  let elegido = null;
  const nombre = h("input", { type: "text", placeholder: "Ej.: Como en mi tienda online", "aria-label": "Nombre del flujo" });
  const descripcion = h("input", { type: "text", "aria-label": "Descripción" });
  const grupo = "origen-" + Math.random().toString(36).slice(2);
  const opciones = h("div", { class: "fichas", role: "radiogroup", "aria-label": "Proyecto de origen" }, lista.map((p) => h("label", { class: "ficha-sistema ficha-radio" },
    h("input", { type: "radio", name: grupo, onchange: () => { elegido = p; if (!nombre.value.trim()) nombre.value = `Como en ${p.nombre}`; } }),
    h("span", { class: "ficha-texto" }, h("b", { texto: p.nombre }),
      h("small", { texto: `${sistemasTexto(p.sistemas.length)} · ${MODOS[p.modo]?.titulo || "sin flujo propio"}` })))));
  return dialogo({ titulo: "Crear un flujo desde un proyecto", contenido: h("div", { class: "pila" },
    h("p", { class: "tenue", texto: "Se copian los sistemas instalados y la forma de trabajar del proyecto que elijas. El proyecto no cambia." }),
    h("h3", { texto: "1. ¿De qué proyecto?" }), opciones,
    h("h3", { texto: "2. ¿Cómo lo llamamos?" }), h("label", { class: "campo" }, "Nombre", nombre), h("label", { class: "campo" }, "Descripción (opcional)", descripcion)),
  acciones: [{ texto: "Crear flujo", clase: "primario", accion: async () => {
    if (!elegido) { avisar("Elige un proyecto", "mal"); return false; }
    if (!nombre.value.trim()) { avisar("Ponle un nombre al flujo", "mal"); return false; }
    const id = await enviar("/api/flujos/desde-proyecto", { repo: elegido.ruta, nombre: nombre.value.trim(), descripcion: descripcion.value.trim() });
    avisar("Flujo creado");
    return id;
  } }] });
}

// Crear (g = null) o editar un flujo guardado, en cuatro pasos. Resuelve con el id guardado o null.
async function editar(g, titulos, { modo = null, paso = 0 } = {}) {
  const datos = g ? structuredClone(g) : { nombre: "", descripcion: "", sistemas: [], flujo: { ...FLUJO_VACIO, ...(modo ? { modo } : {}) } };
  const nombre = h("input", { type: "text", value: datos.nombre, placeholder: "Ej.: Frontend con accesibilidad", "aria-label": "Nombre" });
  const descripcion = h("input", { type: "text", value: datos.descripcion || "", placeholder: "Ej.: Para webs públicas que deben ser accesibles", "aria-label": "Descripción" });
  if (!g && modo) nombre.value = `Mi flujo · ${MODOS[modo].titulo.toLowerCase()}`;
  const elegidos = new Set(datos.sistemas);
  let flujo = datos.flujo;
  let editor;

  // Paso 2: sistemas como fichas que se marcan con un clic, con buscador y filtro por tipo.
  const familias = [...new Set(titulos.map((t) => t.familia).filter(Boolean))].sort();
  let familia = "";
  let soloElegidos = false;
  const filtro = h("input", { type: "search", placeholder: "Buscar sistemas (ej.: seguridad, commits, accesibilidad)…", "aria-label": "Buscar sistemas" });
  const chipsFamilia = h("div", { class: "chips-filtro" });
  const fichas = h("div", { class: "fichas fichas-sistemas" });
  const cuentaElegidos = h("span", { class: "insignia acento" });
  const pintarChips = () => vaciar(chipsFamilia,
    [["", "Todos"], ...familias.map((f) => [f, FAMILIAS[f] || f])].map(([id, texto]) => h("button", { type: "button", class: "chip", "aria-pressed": String(!soloElegidos && familia === id),
      onclick: () => { familia = id; soloElegidos = false; pintarChips(); pintarFichas(); } }, texto)),
    h("button", { type: "button", class: "chip", "aria-pressed": String(soloElegidos), onclick: () => { soloElegidos = !soloElegidos; pintarChips(); pintarFichas(); } }, "Solo los elegidos"));
  const pintarFichas = () => {
    const t = filtro.value.trim().toLowerCase();
    const visibles = titulos.filter((p) => (!soloElegidos || elegidos.has(p.id)) && (soloElegidos || !familia || p.familia === familia)
      && (!t || `${p.titulo} ${p.descripcion}`.toLowerCase().includes(t)));
    cuentaElegidos.textContent = `${elegidos.size} elegido${elegidos.size === 1 ? "" : "s"}`;
    vaciar(fichas, visibles.length ? visibles.map((p) => h("button", { type: "button", class: "ficha-sistema", role: "checkbox", "aria-checked": String(elegidos.has(p.id)),
      onclick: () => { elegidos.has(p.id) ? elegidos.delete(p.id) : elegidos.add(p.id); pintarFichas(); } },
      h("span", { class: "ficha-marca", "aria-hidden": "true" }, elegidos.has(p.id) ? iconoFlujo("resultado") : null),
      h("span", { class: "ficha-texto" }, h("b", { texto: p.titulo }), p.descripcion ? h("small", { texto: p.descripcion }) : null,
        p.familia ? h("span", { class: "ficha-familia", texto: FAMILIAS[p.familia] || p.familia }) : null)))
      : h("p", { class: "tenue", texto: soloElegidos ? "Aún no has elegido ningún sistema." : "No hay sistemas que coincidan." }));
  };
  filtro.addEventListener("input", pintarFichas);

  // Paso 3: la forma de trabajar, con solo los sistemas elegidos.
  const zonaEditor = h("div");
  const pintarEditor = () => {
    const disponibles = titulos.filter((t) => elegidos.has(t.id));
    const limpio = { ...flujo, leer_por_defecto: (flujo.leer_por_defecto || []).filter((x) => elegidos.has(x)),
      secuencia: (flujo.secuencia || []).filter((x) => elegidos.has(x)), trabajar_con: elegidos.has(flujo.trabajar_con) ? flujo.trabajar_con : null };
    editor = editorFlujo(limpio, disponibles, (v) => { flujo = v; });
    flujo = editor.valor();
    vaciar(zonaEditor, editor.nodo);
  };

  // Paso 4: repaso de todo antes de guardar.
  const zonaRepaso = h("div", { class: "pila" });
  const pintarRepaso = () => vaciar(zonaRepaso,
    h("div", { class: "repaso" },
      h("div", {}, h("small", { class: "tenue", texto: "Nombre" }), h("b", { texto: nombre.value.trim() || "(sin nombre)" })),
      descripcion.value.trim() ? h("div", {}, h("small", { class: "tenue", texto: "Descripción" }), h("span", { texto: descripcion.value.trim() })) : null,
      h("div", {}, h("small", { class: "tenue", texto: "Sistemas" }), h("div", { class: "fila" },
        elegidos.size ? [...elegidos].map((id) => insignia((titulos.find((t) => t.id === id) || {}).titulo || id)) : h("span", { class: "tenue", texto: "Ninguno" })))),
    diagrama(editor.valor(), titulos), h("p", { class: "resumen-flujo", texto: resumen(editor.valor(), titulos) }),
    !nombre.value.trim() ? h("div", { class: "banda aviso", texto: "Falta el nombre: vuelve al paso 1." }) : null);

  const PASOS = [
    ["Nombre", h("div", { class: "pila" }, h("p", { class: "tenue", texto: "Un nombre corto que te ayude a reconocerlo después." }),
      h("label", { class: "campo" }, "Nombre", nombre), h("label", { class: "campo" }, "Descripción (opcional)", descripcion))],
    ["Sistemas", h("div", { class: "pila" }, h("div", { class: "fila separada" }, h("p", { class: "tenue", style: "margin:0", texto: "Marca las normas y procesos que incluye este flujo." }), cuentaElegidos),
      filtro, chipsFamilia, fichas)],
    ["Cómo trabaja", zonaEditor],
    ["Repasar", zonaRepaso],
  ];
  let actual = 0;
  let contenido = null;
  const indicador = h("ol", { class: "pasos-asistente", "aria-label": "Pasos" });
  const paneles = PASOS.map(([, contenido]) => h("div", { class: "panel-paso" }, contenido));
  const atras = h("button", { type: "button", class: "boton fantasma" }, "Atrás");
  const siguiente = h("button", { type: "button", class: "boton" }, "Siguiente", iconoFlujo("flecha"));
  const ir = (i) => {
    actual = Math.max(0, Math.min(PASOS.length - 1, i));
    if (actual === 2) pintarEditor();
    if (actual === 3) pintarRepaso();
    paneles.forEach((p, j) => { p.hidden = j !== actual; });
    vaciar(indicador, PASOS.map(([texto], j) => h("li", {}, h("button", { type: "button", class: "paso-asistente",
      "aria-current": j === actual ? "step" : null, "data-estado": j < actual ? "hecho" : j === actual ? "actual" : "pendiente", onclick: () => ir(j) },
    h("span", { class: "paso-asistente-n" }, j < actual ? iconoFlujo("resultado") : String(j + 1)), texto))));
    atras.hidden = actual === 0;
    siguiente.hidden = actual === PASOS.length - 1;
    contenido?.closest(".dialogo-cuerpo")?.scrollTo(0, 0);
    paneles[actual].querySelector("input:not([type=checkbox]):not([type=radio])")?.focus();
  };
  atras.addEventListener("click", () => ir(actual - 1));
  siguiente.addEventListener("click", () => ir(actual + 1));
  pintarChips();
  pintarFichas();
  pintarEditor();
  ir(paso);

  contenido = h("div", { class: "pila asistente-flujo" }, indicador, paneles, h("div", { class: "fila asistente-nav" }, atras, h("span", { class: "espacio" }), siguiente));
  const caja = document.getElementById("dialogo");
  caja.classList.add("dialogo-ancho");
  try {
    return await dialogo({ titulo: g ? `Editar «${g.nombre}»` : "Nuevo flujo guardado", contenido, acciones: [{ texto: "Guardar flujo", clase: "primario", accion: async () => {
      if (!nombre.value.trim()) { avisar("Ponle un nombre al flujo", "mal"); ir(0); return false; }
      const id = await enviar("/api/flujos/guardar", { flujo: { id: g?.id, nombre: nombre.value.trim(), descripcion: descripcion.value.trim(), sistemas: [...elegidos], flujo: editor.valor() } });
      avisar(g ? "Cambios guardados" : "Flujo guardado");
      return id;
    } }] });
  } finally {
    caja.classList.remove("dialogo-ancho");
  }
}
