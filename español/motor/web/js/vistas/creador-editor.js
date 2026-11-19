// Editor del Taller: archivos + formulario + piezas. Las salidas (zip, sync, instalar, publicar)
// viven en la barra de salida del taller; aquí quedan los retoques de versión.

import { obtener, enviar, catalogo, nombreDe } from "../api.js";
import { h, vaciar, boton, avisar, dialogo, pestanas, confirmar, pedirDatos, insignia, elegirVarios } from "../ui.js";
import { inicioConAgente } from "./creador-inicio.js";
import { construirZip, descargarBlob } from "./sistema-zip.js";
import { explorador } from "./editor-archivos.js";

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
  const sinTildes = (t) => t.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  // Ids de problemas: como mucho 40 caracteres, cortando entre palabras (no «…-revision-a»).
  const slug = (t, i) => {
    let s = sinTildes(t).replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    if (s.length > 40) {
      const corte = s.slice(0, 41);
      s = corte.includes("-") ? corte.replace(/-[^-]*$/, "") : s.slice(0, 40);
    }
    return s || `problema-${i + 1}`;
  };
  // Frases de activación: minúsculas ASCII sin tildes ni signos (como pide la nomenclatura).
  const frase = (t) => sinTildes(t).replace(/[^a-z0-9 -]+/g, " ").replace(/\s+/g, " ")
    .replace(/ ?-[ -]*/g, "-").replace(/^[ -]+|[ -]+$/g, "");
  const separar = (t) => t.value.split("\n").map((x) => x.trim()).filter(Boolean);

  async function guardar() {
    const actual = leerJSON((await obtener("/api/catalogo/archivo", { id, rel: "sistema.json" })).contenido) || datos;
    actual.titulo = titulo.value.trim();
    actual.descripcion = descripcion.value.trim();
    actual.familia = familia.value;
    actual.activacion = [...new Set(activacion.value.split(",").map(frase).filter(Boolean))];
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
  const piezas = h("div", { class: "piezas" });
  const basico = h("div", { class: "pila" });
  const sincronia = h("div", { class: "pila salida-panel", "aria-label": "Publicar en el Mercado" });
  const version = h("span", {});
  let elegirPestana = () => {};

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
  const archivos = await explorador(id, {
    alGuardado: async (rel) => {
      if (rel === "sistema.json") vaciar(basico, await formularioBasico(id, recargar));
      await alCambiar();
    },
    alCambiarArchivos: async () => { await pintarPiezas(); await alCambiar(); },
  });
  async function subirVersion(nivel) {
    const v = await enviar("/api/catalogo/version", { id, nivel });
    version.textContent = v;
    avisar(`Versión ${v}. Actualiza tus proyectos para recibirla.`);
    await alCambiar();
  }
  let primera = true;
  async function recargar({ notificar = true } = {}) {
    const meta = (await catalogo(true)).find((m) => m.id === id);
    version.textContent = meta?.version || "";
    vaciar(basico, await formularioBasico(id, recargar));
    // El explorador ya cargó al crearse: la primera vez no hace falta volver a leer los archivos.
    await Promise.all([pintarPiezas(), primera ? null : archivos.recargar()]);
    primera = false;
    // Evita tormenta de pintados al montar el editor (lista + franjas en cascada).
    if (notificar) await alCambiar();
  }
  async function abrirArchivo(rel, opciones) {
    elegirPestana("archivos");
    if (rel) await archivos.abrirArchivo(rel, opciones);
  }
  function abrirDiferencias(...args) {
    elegirPestana("archivos");
    archivos.abrirDiferencias(...args);
  }

  const secciones = {
    archivos: h("div", { class: "pila" }, archivos.nodo),
    basico: h("div", { class: "pila" }, basico),
    piezas: h("div", { class: "pila" }, h("p", { class: "tenue", texto: "Activa las partes que necesita tu sistema. Las marcadas como recomendadas suelen hacer falta." }), piezas),
    version: h("div", { class: "pila" },
      h("div", { class: "fila" }, h("span", {}, "Versión local ", h("b", {}, version)), h("span", { class: "espacio" }),
        boton("Arreglo pequeño", () => subirVersion("parche"), { clase: "pequeno", titulo: "+ parche" }),
        boton("Mejora", () => subirVersion("menor"), { clase: "pequeno", titulo: "+ menor" }),
        boton("Cambio grande", () => subirVersion("mayor"), { clase: "pequeno", titulo: "+ mayor" })),
      h("p", { class: "tenue", texto: "Publicar y sincronizar están en la barra de salida del taller." })),
  };
  const ids = ["archivos", "basico", "piezas", "version"];
  const barra = pestanas(
    [["archivos", "Archivos"], ["basico", "Lo básico"], ["piezas", "Piezas"], ["version", "Versión"]],
    (s) => {
      for (const [k, nodo] of Object.entries(secciones)) nodo.hidden = k !== s;
    },
    pestanaInicial,
  );
  elegirPestana = (s) => {
    for (const [k, nodo] of Object.entries(secciones)) nodo.hidden = k !== s;
    [...barra.querySelectorAll("[role=tab]")].forEach((b, i) => b.setAttribute("aria-selected", String(ids[i] === s)));
  };
  for (const [k, nodo] of Object.entries(secciones)) nodo.hidden = k !== pestanaInicial;

  await recargar({ notificar: false });
  const nodo = h("div", { class: "pila editor-taller" },
    h("div", { class: "tarjeta" }, barra, ...Object.values(secciones)));
  return {
    nodo,
    rutaActual: () => archivos.rutaActual(),
    textarea: archivos.area,
    recargar,
    abrirPestana: elegirPestana,
    abrirArchivo,
    abrirDiferencias,
    haySinGuardar: archivos.haySinGuardar,
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
