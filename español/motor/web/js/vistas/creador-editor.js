// Editor del Taller: archivos + formulario + piezas. Las salidas (zip, sync, instalar, publicar)
// viven en la barra de salida del taller; aquí quedan los retoques de versión.

import { obtener, enviar, catalogo, nombreDe } from "../api.js";
import { h, vaciar, boton, avisar, dialogo, pestanas, confirmar, pedirDatos, insignia, elegirVarios } from "../ui.js";
import { inicioConAgente } from "./creador-inicio.js";
import { construirZip, descargarBlob } from "./sistema-zip.js";

export const PIEZAS = {
  proceso: "Proceso por fases", skills: "Habilidades del agente", componentes: "Componentes", herramientas: "Herramientas",
  andamiaje: "Estructura de carpetas", plantillas: "Plantillas", referencia: "Referencia", ejemplos: "Ejemplos",
  pruebas: "Pruebas", cambios: "Historial de cambios",
};
export const FAMILIAS = { proceso: "Proceso", codigo: "Código", arquitectura: "Arquitectura", documentacion: "Documentación",
  seguridad: "Seguridad", producto: "Producto", plataforma: "Plataforma" };

function bytesLegibles(n) {
  if (n < 1024) return `${n} bytes`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KiB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MiB`;
}

/** Descarga el sistema local como .zip (archivos de texto del catálogo). */
export async function descargarZipSistema(id) {
  const lista = await obtener("/api/catalogo/archivos", { id });
  const files = [];
  for (const rel of lista) {
    const { contenido } = await obtener("/api/catalogo/archivo", { id, rel });
    files.push({ path: `${id}/${rel}`, data: new TextEncoder().encode(contenido) });
  }
  if (!files.length) throw new Error("Este sistema no tiene archivos para empaquetar.");
  descargarBlob(construirZip(files), `${id}.zip`);
  avisar(`Descargado ${id}.zip`);
}

/** Diálogo: elige proyectos registrados e instala el sistema (`/api/catalogo/instalar-en`). */
export async function instalarEnProyecto(id, titulo) {
  const lista = (await obtener("/api/proyectos")).filter((p) => p.existe);
  if (!lista.length) {
    avisar("Primero añade algún proyecto en «Proyectos».", "mal");
    return null;
  }
  const opciones = lista.map((p) => ({
    valor: p.ruta,
    titulo: p.nombre,
    detalle: (p.sistemas || []).includes(id) ? "ya lo tiene" : (p.grupo || ""),
  }));
  const eleccion = elegirVarios(opciones);
  const repos = await dialogo({
    titulo: `Instalar «${titulo || id}»`,
    contenido: h("div", { class: "pila" },
      h("p", { class: "tenue", texto: "Marca los proyectos donde quieres instalarlo." }),
      eleccion.nodo),
    acciones: [{
      texto: "Instalar",
      clase: "primario",
      accion: () => eleccion.valores().length ? eleccion.valores() : (avisar("Marca al menos un proyecto", "mal"), false),
    }],
  });
  if (!repos) return null;
  const resultados = await enviar("/api/catalogo/instalar-en", { ids: [id], repos });
  const zona = h("ul", { class: "lista" });
  vaciar(zona, resultados.map((r) => h("li", {},
    h("b", { class: "espacio", texto: nombreDe(r.ruta) }),
    r.error ? h("span", { class: "insignia mal", texto: r.error })
      : insignia(r.instalados.length ? "instalado" : "ya lo tenía", "bien"))));
  await dialogo({ titulo: "Resultado", contenido: zona, cancelar: "Cerrar", acciones: [] });
  return resultados;
}

/** Proyectos donde está instalado este id. */
export async function proyectosConSistema(id) {
  const lista = await obtener("/api/proyectos").catch(() => []);
  return lista.filter((p) => p.existe && (p.sistemas || []).includes(id)).map((p) => p.nombre || nombreDe(p.ruta));
}

/** Publica el sistema en el Mercado (versión inmutable). Distinto de «Guardar borrador en la web». */
export async function publicarEnMercado(id, zona, { alPublicar = null } = {}) {
  const cuenta = await obtener("/api/cuenta");
  const usuario = (cuenta.usuario || "").replace(/^@/, "");
  if (!usuario || cuenta.tipo === "ninguna") {
    avisar("Inicia sesión en «Cuenta» antes de publicar en el Mercado.", "mal");
    return;
  }
  const previa = await enviar("/api/catalogo/publicar", { id, simular: true });
  const editor = (previa.editor || "").replace(/^@/, "");
  const distinto = editor !== usuario;
  const marca = distinto ? h("input", { type: "checkbox" }) : null;
  const destino = zona || document.createElement("div");

  async function confirmarYSubir() {
    if (distinto && !marca?.checked) {
      avisar(`Marca «Usar @${usuario} como editor» antes de publicar.`, "mal");
      return;
    }
    const r = await enviar("/api/catalogo/publicar", { id, simular: false, alinear_editor: !!marca?.checked });
    vaciar(destino);
    avisar(`Publicado ${r.editor}/${r.id}@${r.version}`);
    if (alPublicar) await alPublicar(r);
  }

  vaciar(destino,
    h("div", { class: "banda" },
      h("b", { texto: "Publicar en el Mercado" }),
      h("p", { texto: `${previa.editor || editor}/${previa.id}@${previa.version}` }),
      h("p", { class: "tenue", texto: `${bytesLegibles(previa.tamano || 0)} · sha256 ${previa.sha256 || "?"}` }),
      h("p", { texto: distinto
        ? `El sistema declara editor «${editor}» y tu sesión es @${usuario}. Marca la casilla para alinearlo antes de publicar.`
        : `Se publicará con tu cuenta @${usuario}. Esta versión queda fija: para cambiarla luego publicarás una versión nueva.` }),
      distinto ? h("label", { class: "casilla" }, marca, h("span", { texto: `Usar @${usuario} como editor` })) : null,
      h("div", { class: "fila" },
        boton("Cancelar", () => vaciar(destino), { clase: "pequeno fantasma" }),
        boton("Publicar", confirmarYSubir, { clase: "pequeno primario" }))));
}

const leerJSON = (texto) => { try { return JSON.parse(texto); } catch { return null; } };

/** Formulario de lo básico de sistema.json: título, qué resuelve, tipo, problemas y lo que queda fuera. */
async function formularioBasico(id, alGuardar) {
  const original = (await obtener("/api/catalogo/archivo", { id, rel: "sistema.json" })).contenido;
  const datos = leerJSON(original);
  if (!datos) return h("div", { class: "banda aviso", texto: "sistema.json no es JSON válido: corrígelo en «Archivos»." });
  const titulo = h("input", { type: "text", value: datos.titulo || "", "aria-label": "Título" });
  const descripcion = h("textarea", { rows: 2, class: "breve", "aria-label": "Qué resuelve", texto: datos.descripcion || "" });
  const familia = h("select", { "aria-label": "Tipo" }, Object.entries(FAMILIAS).map(([v, t]) => h("option", { value: v, texto: t, selected: v === datos.familia })));
  const lineas = (lista, campo) => (lista || []).map((x) => x[campo] || "").join("\n");
  const problemas = h("textarea", { rows: 3, class: "breve", "aria-label": "Problemas que resuelve", texto: lineas(datos.alcance?.problemas, "descripcion") });
  const fuera = h("textarea", { rows: 2, class: "breve", "aria-label": "Lo que no resuelve", texto: lineas(datos.alcance?.fuera_de_alcance, "tema") });
  const activacion = h("input", { type: "text", value: (datos.activacion || []).join(", "), "aria-label": "Palabras que lo activan" });
  const slug = (t, i) => (t.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || `problema-${i + 1}`);
  const separar = (t) => t.value.split("\n").map((x) => x.trim()).filter(Boolean);

  async function guardar() {
    const actual = leerJSON((await obtener("/api/catalogo/archivo", { id, rel: "sistema.json" })).contenido) || datos;
    actual.titulo = titulo.value.trim();
    actual.descripcion = descripcion.value.trim();
    actual.familia = familia.value;
    actual.activacion = activacion.value.split(",").map((x) => x.trim()).filter(Boolean);
    actual.alcance = actual.alcance || {};
    const previos = actual.alcance.problemas || [];
    actual.alcance.problemas = separar(problemas).map((d, i) => ({ ...(previos[i] || {}), id: previos[i]?.id || slug(d, i), descripcion: d }));
    const previosFuera = actual.alcance.fuera_de_alcance || [];
    actual.alcance.fuera_de_alcance = separar(fuera).map((t, i) => ({ derivar_a: null, ...(previosFuera[i] || {}), tema: t }));
    const r = await enviar("/api/catalogo/archivo", { id, rel: "sistema.json", contenido: JSON.stringify(actual, null, 2) + "\n" });
    avisar(r.errores.length ? "Guardado, pero aún falta algo (mira «Lo que falta»)" : "Guardado", r.errores.length ? "mal" : "");
    await alGuardar();
  }

  return h("div", { class: "pila" },
    h("label", { class: "campo" }, "Título", titulo),
    h("label", { class: "campo" }, "Qué resuelve, en una frase", descripcion),
    h("label", { class: "campo" }, "Tipo", familia),
    h("label", { class: "campo" }, "Problemas que resuelve (uno por línea)", problemas),
    h("label", { class: "campo" }, "Lo que no resuelve (uno por línea)", fuera),
    h("label", { class: "campo" }, "Palabras que lo activan (separadas por comas)", activacion),
    h("div", { class: "fila" }, boton("Guardar", guardar, { clase: "primario pequeno", icono: "check" })));
}

/**
 * Editor de un sistema del catálogo local. Archivos visibles por defecto.
 * Devuelve { nodo, rutaActual, textarea, recargar, abrirPestana, panelPublicar }.
 */
export async function editorSistema(id, { alCambiar = async () => {}, pestanaInicial = "archivos" } = {}) {
  const archivos = h("select", { "aria-label": "Archivo del sistema" });
  const contenido = h("textarea", { "aria-label": "Contenido del archivo", spellcheck: "false", class: "editor-texto" });
  const errores = h("div", { class: "tenue" });
  const piezas = h("div", { class: "piezas" });
  const basico = h("div", { class: "pila" });
  const sincronia = h("div", { class: "pila salida-panel", "aria-label": "Publicar en el Mercado" });
  const version = h("span", {});
  const sinGuardar = h("span", { class: "insignia nota", texto: "sin guardar", hidden: true });
  let elegirPestana = () => {};
  // Lo que hay en disco del archivo abierto: si el texto difiere, hay cambios sin guardar y no se pisan al recargar.
  let enDisco = null;
  let rutaAbierta = "";
  const sucio = () => enDisco !== null && contenido.value !== enDisco;
  const marcarSucio = () => { sinGuardar.hidden = !sucio(); };
  contenido.addEventListener("input", marcarSucio);

  async function pintarPiezas() {
    const c = await obtener("/api/catalogo/completitud", { id });
    const presentes = new Set(c.piezas || []);
    const recomendadas = new Set(c.faltan_recomendadas || []);
    vaciar(piezas, Object.entries(PIEZAS).map(([p, nombre]) => {
      const casilla = h("input", { type: "checkbox", checked: presentes.has(p) });
      casilla.addEventListener("change", async () => {
        const accion = casilla.checked ? "agregar" : "quitar";
        if (accion === "quitar" && !(await confirmar({ titulo: `Quitar «${nombre}»`, texto: "Se borran los archivos de esta pieza en el sistema.", si: "Quitar", peligro: true }))) {
          casilla.checked = true;
          return;
        }
        try {
          const r = await enviar("/api/catalogo/pieza", { id, accion, pieza: p });
          avisar(`${nombre}: ${accion === "agregar" ? "añadida" : "quitada"}` + (r.length ? `. Pendiente: ${r.join("; ")}` : ""), r.length ? "mal" : "");
        } catch (e) { casilla.checked = !casilla.checked; throw e; }
        await recargar();
      });
      return h("label", { class: "pieza" + (presentes.has(p) ? " activa" : "") }, casilla, h("span", { texto: nombre }),
        recomendadas.has(p) ? insignia("recomendada", "nota") : null);
    }));
  }
  async function cargarArchivos(elegido) {
    const lista = await obtener("/api/catalogo/archivos", { id });
    const preferidos = ["sistema.json", "README.md", "SISTEMA.md"];
    // Un archivo nuevo aún sin guardar no está en disco: se conserva mientras tenga cambios.
    const conservarNuevo = elegido && !lista.includes(elegido) && sucio() && rutaAbierta === elegido;
    const inicial = elegido && (lista.includes(elegido) || conservarNuevo)
      ? elegido
      : (preferidos.find((p) => lista.includes(p)) || lista[0] || "");
    const rutas = conservarNuevo ? [...lista, elegido] : lista;
    vaciar(archivos, rutas.map((a) => h("option", { value: a, texto: a, selected: a === inicial })));
    if (inicial) archivos.value = inicial;
    await abrir({ recargando: true });
  }
  async function abrir({ recargando = false } = {}) {
    if (!archivos.value) {
      contenido.value = "";
      enDisco = null;
      rutaAbierta = "";
      marcarSucio();
      return;
    }
    const rel = archivos.value;
    if (recargando && rel === rutaAbierta && sucio()) {
      // uxyn u otra acción recargó el sistema: no se pierden los cambios sin guardar de la persona.
      let actual = null;
      try { actual = (await obtener("/api/catalogo/archivo", { id, rel })).contenido; } catch { /* archivo nuevo */ }
      if (actual !== null && actual !== enDisco) {
        errores.textContent = `${rel} cambió mientras lo editabas. Tus cambios siguen aquí; al guardar sustituyes la versión nueva.`;
        enDisco = actual;
      }
      marcarSucio();
      return;
    }
    if (!recargando && rutaAbierta && rel !== rutaAbierta && sucio()) {
      const seguir = await confirmar({
        titulo: "Cambios sin guardar",
        texto: `Tienes cambios sin guardar en ${rutaAbierta}. Si cambias de archivo, se pierden.`,
        si: "Descartar y cambiar",
        peligro: true,
      });
      if (!seguir) {
        if (![...archivos.options].some((o) => o.value === rutaAbierta)) archivos.append(h("option", { value: rutaAbierta, texto: rutaAbierta }));
        archivos.value = rutaAbierta;
        return;
      }
    }
    let texto = "";
    try {
      texto = (await obtener("/api/catalogo/archivo", { id, rel })).contenido;
    } catch (e) {
      if (rel !== rutaAbierta || !recargando) throw e;
    }
    contenido.value = texto;
    enDisco = texto;
    rutaAbierta = rel;
    errores.textContent = "";
    marcarSucio();
  }
  async function guardarArchivo() {
    if (!archivos.value) return avisar("Elige o crea un archivo primero.", "mal");
    const r = await enviar("/api/catalogo/archivo", { id, rel: archivos.value, contenido: contenido.value });
    enDisco = contenido.value;
    rutaAbierta = archivos.value;
    marcarSucio();
    errores.textContent = r.errores.join("; ");
    avisar(r.errores.length ? "Guardado, pero aún falta algo" : "Guardado", r.errores.length ? "mal" : "");
    if (archivos.value === "sistema.json") vaciar(basico, await formularioBasico(id, recargar));
    await alCambiar();
  }
  async function nuevoArchivo() {
    const r = await pedirDatos({ titulo: "Archivo nuevo", explicacion: "Ruta dentro del sistema, por ejemplo ejemplos/caso.md", campos: [{ nombre: "rel", etiqueta: "Ruta" }], si: "Crear" });
    const rel = String(r?.rel || "").trim().replace(/^\/+/, "");
    if (!rel) return;
    if ([...archivos.options].some((o) => o.value === rel)) {
      archivos.value = rel;
      await abrir();
      return;
    }
    if (sucio() && !(await confirmar({ titulo: "Cambios sin guardar", texto: `Tienes cambios sin guardar en ${rutaAbierta}. Si creas otro archivo, se pierden.`, si: "Descartar y crear", peligro: true }))) return;
    // Igual que la web: el archivo se crea al momento (un .md con su título) para que no se pierda.
    const inicial = rel.endsWith(".md") ? `# ${rel.split("/").pop().replace(/\.md$/, "")}\n` : "";
    const g = await enviar("/api/catalogo/archivo", { id, rel, contenido: inicial });
    enDisco = null;
    await cargarArchivos(rel);
    errores.textContent = (g.errores || []).join("; ");
    contenido.focus();
    await alCambiar();
  }
  async function subirVersion(nivel) {
    const v = await enviar("/api/catalogo/version", { id, nivel });
    version.textContent = v;
    avisar(`Versión ${v}. Actualiza tus proyectos para recibirla.`);
    await alCambiar();
  }
  async function recargar({ notificar = true } = {}) {
    const meta = (await catalogo(true)).find((m) => m.id === id);
    version.textContent = meta?.version || "";
    vaciar(basico, await formularioBasico(id, recargar));
    await Promise.all([pintarPiezas(), cargarArchivos(archivos.value)]);
    // Evita tormenta de pintados al montar el editor (lista + franjas en cascada).
    if (notificar) await alCambiar();
  }

  /** Selecciona el siguiente marcador {{…}} desde el cursor (vuelve al principio al llegar al final), como en la web. */
  function saltarAMarcador() {
    const texto = contenido.value;
    const patron = /\{\{[^{}]*\}\}/g;
    patron.lastIndex = contenido.selectionEnd || 0;
    let m = patron.exec(texto);
    if (!m) { patron.lastIndex = 0; m = patron.exec(texto); }
    if (!m) return avisar("Este archivo no tiene huecos {{…}} por rellenar.");
    contenido.focus();
    contenido.setSelectionRange(m.index, m.index + m[0].length);
  }

  async function abrirArchivo(rel) {
    elegirPestana("archivos");
    if (rel && [...archivos.options].some((o) => o.value === rel)) {
      archivos.value = rel;
      await abrir();
      contenido.focus();
    }
  }

  archivos.addEventListener("change", () => abrir().catch((e) => avisar(e.message || String(e), "mal")));
  contenido.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
      e.preventDefault();
      guardarArchivo().catch((err) => avisar(err.message || String(err), "mal"));
    }
  });
  window.addEventListener("beforeunload", (e) => { if (contenido.isConnected && sucio()) { e.preventDefault(); e.returnValue = ""; } });
  const secciones = {
    archivos: h("div", { class: "pila" },
      h("div", { class: "fila" }, h("div", { class: "espacio" }, archivos), sinGuardar, boton("Archivo nuevo", nuevoArchivo, { clase: "pequeno", icono: "mas" })),
      contenido, errores,
      h("div", { class: "fila" },
        boton("Guardar archivo", guardarArchivo, { clase: "primario pequeno", icono: "check" }),
        boton("Siguiente hueco", () => saltarAMarcador(), { clase: "pequeno fantasma", titulo: "Selecciona el siguiente {{…}} por rellenar" }),
        h("span", { class: "tenue", texto: "Ctrl+S guarda" }))),
    basico: h("div", { class: "pila" }, basico),
    piezas: h("div", { class: "pila" }, h("p", { class: "tenue", texto: "Activa las partes que necesita tu sistema. Las marcadas como recomendadas suelen hacer falta." }), piezas),
    version: h("div", { class: "pila" },
      h("div", { class: "fila" }, h("span", {}, "Versión local ", h("b", {}, version)), h("span", { class: "espacio" }),
        boton("Arreglo pequeño", () => subirVersion("parche"), { clase: "pequeno", titulo: "+ parche" }),
        boton("Mejora", () => subirVersion("menor"), { clase: "pequeno", titulo: "+ menor" }),
        boton("Cambio grande", () => subirVersion("mayor"), { clase: "pequeno", titulo: "+ mayor" })),
      h("p", { class: "tenue", texto: "Publicar y sincronizar están en la barra de salida del taller." })),
  };
  const barra = pestanas(
    [["archivos", "Archivos"], ["basico", "Lo básico"], ["piezas", "Piezas"], ["version", "Versión"]],
    (s) => {
      for (const [k, nodo] of Object.entries(secciones)) nodo.hidden = k !== s;
    },
    pestanaInicial,
  );
  elegirPestana = (s) => {
    for (const [k, nodo] of Object.entries(secciones)) nodo.hidden = k !== s;
    [...barra.querySelectorAll("[role=tab]")].forEach((b, i) => {
      const ids = ["archivos", "basico", "piezas", "version"];
      b.setAttribute("aria-selected", String(ids[i] === s));
    });
  };
  for (const [k, nodo] of Object.entries(secciones)) nodo.hidden = k !== pestanaInicial;

  await recargar({ notificar: false });
  const nodo = h("div", { class: "pila editor-taller" },
    h("div", { class: "tarjeta" }, barra, ...Object.values(secciones)));
  return {
    nodo,
    rutaActual: () => archivos.value,
    textarea: contenido,
    recargar,
    abrirPestana: elegirPestana,
    abrirArchivo,
    panelPublicar: sincronia,
    mostrarPublicar: () => publicarEnMercado(id, sincronia),
  };
}

/** Diálogo para crear un sistema: con lo mínimo (esqueleto) o desde una especificación. Devuelve el id creado. */
/** Diálogo «Crear sistema». Devuelve el id creado, o { id, conversacion } si lo creó el agente; null si se cancela. */
export async function crearSistema() {
  const id = h("input", { type: "text", placeholder: "por ejemplo: revision-de-seguridad", "aria-label": "Identificador" });
  const titulo = h("input", { type: "text", "aria-label": "Título" });
  const descripcion = h("input", { type: "text", "aria-label": "Qué resuelve" });
  const familia = h("select", { "aria-label": "Tipo" }, Object.entries(FAMILIAS).map(([v, t]) => h("option", { value: v, texto: t })));
  const casillas = Object.keys(PIEZAS).map((p) => h("input", { type: "checkbox", value: p, checked: p === "plantillas" || p === "cambios" }));
  const esqueleto = h("div", { class: "pila" },
    h("label", { class: "campo" }, "Título", titulo),
    h("label", { class: "campo" }, "Identificador (minúsculas y guiones)", id),
    h("label", { class: "campo" }, "Qué resuelve", descripcion), h("label", { class: "campo" }, "Tipo", familia),
    h("div", {}, h("b", { texto: "Piezas" }), h("div", { class: "fila" }, Object.values(PIEZAS).map((nombre, i) => h("label", { class: "casilla" }, casillas[i], nombre)))),
    h("p", { class: "tenue", texto: "Después, «Lo que falta» te lleva a cada cosa por rellenar. También puedes pedírselo al agente." }));
  titulo.addEventListener("input", () => {
    if (id.dataset.tocado) return;
    id.value = titulo.value.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  });
  id.addEventListener("input", () => { id.dataset.tocado = "1"; });
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
    h("p", { class: "tenue", texto: "Sistema completo desde una especificación (formato en motor/GENERADOR.md). Solo se crea si no tiene errores." }),
    spec, h("div", { class: "fila" }, boton("Comprobar", async () => mostrar(await enviar("/api/catalogo/generar", { spec: leerSpec(), aplicar: false })), { clase: "pequeno" })),
    resultado);
  // Formas alternativas al hero «Crea un sistema con el agente» (pantalla principal).
  let creado = null;
  const conAgente = inicioConAgente({ conBoton: false, cabecera: false, alCrear: (idNuevo, r) => { creado = { id: idNuevo, conversacion: r.conversacion }; } });
  let modo = "esqueleto";
  conAgente.nodo.hidden = true;
  esqueleto.hidden = false;
  const barra = pestanas([["esqueleto", "Paso a paso"], ["agente", "Con uxyn"], ["spec", "Desde especificación"]], (m) => {
    modo = m;
    conAgente.nodo.hidden = m !== "agente";
    esqueleto.hidden = m !== "esqueleto";
    desdeSpec.hidden = m !== "spec";
  }, "esqueleto");
  return dialogo({ titulo: "Nueva plantilla", contenido: h("div", { class: "pila" },
    h("p", { class: "tenue", texto: "Plantilla a mano, con uxyn, o desde una especificación JSON." }),
    barra, esqueleto, conAgente.nodo, desdeSpec), acciones: [{ texto: "Crear", clase: "primario", accion: async () => {
    if (modo === "agente") {
      const r = await conAgente.crear();
      return r && creado ? creado : false;   // si el agente pregunta algo, el diálogo sigue abierto para responder
    }
    if (modo === "spec") {
      const r = await enviar("/api/catalogo/generar", { spec: leerSpec(), aplicar: true });
      mostrar(r);
      if (!r.aplicado) { avisar("No se creó: revisa los errores", "mal"); return false; }
      avisar("Sistema creado");
      return r.id;
    }
    await enviar("/api/catalogo/crear", { id: id.value.trim(), titulo: titulo.value.trim(), descripcion: descripcion.value.trim(), familia: familia.value,
      piezas: casillas.filter((c) => c.checked).map((c) => c.value) });
    avisar("Sistema creado");
    return id.value.trim();
  } }] });
}
