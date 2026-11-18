// Editor del Creador de sistemas: datos básicos con un formulario, piezas como interruptores, lista de lo que falta,
// archivos y versión. Vive en la zona central de la pantalla «Creador de sistemas» (antes era el «modo avanzado»).

import { obtener, enviar, catalogo } from "../api.js";
import { h, vaciar, boton, avisar, dialogo, pestanas, confirmar, pedirDatos, insignia } from "../ui.js";
import { sincronizarBorrador } from "./creador.js";
import { inicioConAgente } from "./creador-inicio.js";

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

/** Publica el sistema en el Mercado (versión inmutable). Distinto de «Subir al Creador web» (borrador). */
export async function publicarEnMercado(id, zona) {
  const cuenta = await obtener("/api/cuenta");
  const usuario = (cuenta.usuario || "").replace(/^@/, "");
  if (!usuario || cuenta.tipo === "ninguna") {
    avisar("Inicia sesión en «Herramienta y ajustes» antes de publicar en el Mercado.", "mal");
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
 * Editor de un sistema del catálogo local, como nodo (no diálogo). `alCambiar` se llama tras guardar algo que cambia
 * la lista (título, piezas, versión). Devuelve { nodo, rutaActual, textarea, recargar } para que el chat lo use.
 */
export async function editorSistema(id, { alCambiar = async () => {} } = {}) {
  const archivos = h("select", { "aria-label": "Archivo del sistema" });
  const contenido = h("textarea", { "aria-label": "Contenido del archivo", spellcheck: "false", class: "editor-texto" });
  const errores = h("div", { class: "tenue" });
  const falta = h("div", { class: "pila" });
  const piezas = h("div", { class: "piezas" });
  const basico = h("div", { class: "pila" });
  const sincronia = h("div", { class: "pila" });
  const version = h("span", {});
  let barra = null;

  async function pintarFalta() {
    const p = await obtener("/api/catalogo/pendientes", { id });
    const marcas = p.marcadores || [];
    const total = (p.errores || []).length + marcas.length;
    if (p.listo) {
      vaciar(falta, h("div", { class: "banda bien", texto: "Listo: no falta nada." }));
      return;
    }
    vaciar(falta,
      p.siguiente ? h("p", {}, h("b", { texto: "Siguiente paso: " }), p.siguiente) : null,
      h("details", {}, h("summary", { texto: `Ver todo lo que falta (${total})` }),
        h("ul", { class: "lista" },
          marcas.map((m) => h("li", {}, h("button", { type: "button", class: "enlace", texto: `Rellenar ${m.archivo}, línea ${m.linea}`,
            onclick: async () => { barra.querySelectorAll("button")[2].click(); archivos.value = m.archivo; await abrir(); contenido.focus(); } }))),
          (p.errores || []).filter((e) => !/marcadores sin rellenar/.test(e)).map((e) => h("li", { texto: e })))));
  }
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
    vaciar(archivos, lista.map((a) => h("option", { value: a, texto: a, selected: a === elegido })));
    await abrir();
  }
  async function abrir() {
    if (!archivos.value) return;
    contenido.value = (await obtener("/api/catalogo/archivo", { id, rel: archivos.value })).contenido;
    errores.textContent = "";
  }
  async function guardarArchivo() {
    const r = await enviar("/api/catalogo/archivo", { id, rel: archivos.value, contenido: contenido.value });
    errores.textContent = r.errores.join("; ");
    avisar(r.errores.length ? "Guardado, pero aún falta algo (mira «Lo que falta»)" : "Guardado", r.errores.length ? "mal" : "");
    await pintarFalta();
    if (archivos.value === "sistema.json") vaciar(basico, await formularioBasico(id, recargar));
  }
  async function nuevoArchivo() {
    const r = await pedirDatos({ titulo: "Archivo nuevo", explicacion: "Ruta dentro del sistema, por ejemplo ejemplos/caso.md", campos: [{ nombre: "rel", etiqueta: "Ruta" }], si: "Crear" });
    if (!r?.rel) return;
    archivos.append(h("option", { value: r.rel, texto: r.rel, selected: true }));
    contenido.value = "";
  }
  async function subirVersion(nivel) {
    const v = await enviar("/api/catalogo/version", { id, nivel });
    version.textContent = v;
    avisar(`Versión ${v}. Actualiza tus proyectos para recibirla.`);
    await alCambiar();
  }
  async function recargar() {
    const meta = (await catalogo(true)).find((m) => m.id === id);
    version.textContent = meta?.version || "";
    vaciar(basico, await formularioBasico(id, recargar));
    await Promise.all([pintarFalta(), pintarPiezas(), cargarArchivos(archivos.value)]);
    await alCambiar();
  }

  archivos.addEventListener("change", abrir);
  const secciones = {
    basico: h("div", { class: "pila" }, basico),
    piezas: h("div", { class: "pila" }, h("p", { class: "tenue", texto: "Activa las partes que necesita tu sistema. Las marcadas como recomendadas suelen hacer falta." }), piezas),
    archivos: h("div", { class: "pila" },
      h("div", { class: "fila" }, h("div", { class: "espacio" }, archivos), boton("Archivo nuevo", nuevoArchivo, { clase: "pequeno", icono: "mas" })),
      contenido, errores,
      h("div", { class: "fila" }, boton("Guardar archivo", guardarArchivo, { clase: "primario pequeno", icono: "check" }))),
    publicar: h("div", { class: "pila" },
      h("div", { class: "fila" }, h("span", {}, "Versión ", h("b", {}, version)), h("span", { class: "espacio" }),
        boton("Arreglo pequeño", () => subirVersion("parche"), { clase: "pequeno", titulo: "+ parche" }),
        boton("Mejora", () => subirVersion("menor"), { clase: "pequeno", titulo: "+ menor" }),
        boton("Cambio grande", () => subirVersion("mayor"), { clase: "pequeno", titulo: "+ mayor" })),
      h("div", { class: "fila" },
        boton("Guardar borrador en la web", () => sincronizarBorrador("subir", id, sincronia), { clase: "pequeno", icono: "subir" }),
        boton("Publicar en el Mercado", () => publicarEnMercado(id, sincronia), { clase: "pequeno primario" })),
      h("p", { class: "tenue", texto: "El borrador en la web se puede seguir editando. Publicar en el Mercado deja una versión fija que otras personas pueden instalar." }),
      sincronia),
  };
  barra = pestanas([["basico", "Lo básico"], ["piezas", "Piezas"], ["archivos", "Archivos"], ["publicar", "Versión y publicar"]],
    (s) => { for (const [k, nodo] of Object.entries(secciones)) nodo.hidden = k !== s; }, "basico");
  for (const [k, nodo] of Object.entries(secciones)) nodo.hidden = k !== "basico";

  await recargar();
  const nodo = h("div", { class: "pila" },
    h("div", { class: "tarjeta pila" }, h("h3", { texto: "Lo que falta" }), falta),
    h("div", { class: "tarjeta" }, barra, ...Object.values(secciones)));
  return { nodo, rutaActual: () => archivos.value, textarea: contenido, recargar };
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
  // El agente primero: es la forma principal de crear un sistema (igual que en el Creador web).
  let creado = null;
  const conAgente = inicioConAgente({ conBoton: false, alCrear: (idNuevo, r) => { creado = { id: idNuevo, conversacion: r.conversacion }; } });
  let modo = "agente";
  esqueleto.hidden = true;
  const barra = pestanas([["agente", "Con el agente"], ["esqueleto", "Paso a paso"], ["spec", "Desde especificación"]], (m) => {
    modo = m;
    conAgente.nodo.hidden = m !== "agente";
    esqueleto.hidden = m !== "esqueleto";
    desdeSpec.hidden = m !== "spec";
  }, "agente");
  return dialogo({ titulo: "Crear sistema", contenido: h("div", { class: "pila" }, barra, conAgente.nodo, esqueleto, desdeSpec), acciones: [{ texto: "Crear", clase: "primario", accion: async () => {
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
