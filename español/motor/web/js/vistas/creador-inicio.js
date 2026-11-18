// Crear un sistema con el agente (igual que en el Creador web): la persona cuenta su idea y/o adjunta archivos de
// texto; el agente crea el borrador y deja el contenido como propuestas. El panel lo trae a este equipo.

import { enviar } from "../api.js";
import { h, vaciar, boton, avisar, icono } from "../ui.js";

export const MAX_ADJUNTOS = 30;
export const MAX_CARACTERES_ADJUNTO = 100_000;
export const MAX_CARACTERES_ADJUNTOS = 200_000;

const CARPETAS_BASURA = new Set([".git", ".hg", ".svn", "node_modules", "__MACOSX", "__pycache__", ".venv", "venv",
  ".idea", ".vscode", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".next", ".cache"]);
const ARCHIVOS_BASURA = /(?:^|\/)(?:\.DS_Store|Thumbs\.db|desktop\.ini|\._[^/]*|[^/]*~|[^/]*\.(?:swp|pyc|pyo))$/i;

/** ¿Se ignora esta ruta? (.git, node_modules, basura del sistema operativo). Igual que en la web y el servidor. */
export function esBasura(ruta) {
  return String(ruta).split("/").some((p) => CARPETAS_BASURA.has(p)) || ARCHIVOS_BASURA.test(ruta);
}

export const PREFIJO_CREAR = "Quiero crear un sistema de gobernanza nuevo. Créalo ahora (borrador y archivos núcleo completos como propuesta) a partir de esta idea y de los archivos adjuntos, si hay:";
export const DESDE_ARCHIVOS = "Crea el sistema a partir de los archivos adjuntos.";
export const EJEMPLOS = [
  "Revisión de código para un equipo pequeño: pruebas obligatorias y nada de tocar producción.",
  "Atención al cliente por correo: tono amable, qué puede prometer y cuándo pasar a una persona.",
  "Publicación de contenido en redes: aprobaciones, marca y qué no se publica nunca.",
];

const estricto = new TextDecoder("utf-8", { fatal: true });

/** Lee archivos elegidos como adjuntos de texto. Devuelve { añadidos, rechazados } sin pasarse de los límites. */
export async function leerAdjuntos(archivos, actuales = []) {
  const añadidos = [];
  const rechazados = [];
  let total = actuales.reduce((n, a) => n + a.contenido.length, 0);
  const nombres = new Set(actuales.map((a) => a.nombre));
  for (const archivo of archivos) {
    const nombre = archivo.webkitRelativePath || archivo.name;
    if (esBasura(nombre) || nombres.has(nombre)) continue;
    if (actuales.length + añadidos.length >= MAX_ADJUNTOS || archivo.size > MAX_CARACTERES_ADJUNTO * 4) { rechazados.push(nombre); continue; }
    let contenido;
    try {
      contenido = estricto.decode(new Uint8Array(await archivo.arrayBuffer()));
    } catch { rechazados.push(nombre); continue; }
    if (contenido.includes("\u0000") || contenido.length > MAX_CARACTERES_ADJUNTO || total + contenido.length > MAX_CARACTERES_ADJUNTOS) {
      rechazados.push(nombre);
      continue;
    }
    total += contenido.length;
    nombres.add(nombre);
    añadidos.push({ nombre, contenido });
  }
  return { añadidos, rechazados };
}

/** Botones «Adjuntar archivos/carpeta», arrastrar y soltar y la lista de adjuntos. `valor()` devuelve los adjuntos. */
export function selectorAdjuntos({ compacto = false } = {}) {
  let adjuntos = [];
  const lista = h("ul", { class: "chips", "aria-label": "Archivos adjuntos" });
  const nota = h("p", { class: "tenue", role: "status" });
  const archivos = h("input", { type: "file", multiple: true, hidden: true });
  const carpeta = h("input", { type: "file", multiple: true, hidden: true, webkitdirectory: "" });
  const zona = h("div", { class: "adjuntos" });

  function pintar() {
    vaciar(lista, adjuntos.map((a) => h("li", { class: "chip" },
      h("code", { texto: a.nombre }),
      h("button", { type: "button", class: "chip-quitar", "aria-label": `Quitar ${a.nombre}`, title: "Quitar",
        onclick: () => { adjuntos = adjuntos.filter((x) => x !== a); pintar(); } }, icono("cerrar")))));
    lista.hidden = !adjuntos.length;
  }
  async function añadir(lista) {
    const { añadidos, rechazados } = await leerAdjuntos(Array.from(lista || []), adjuntos);
    adjuntos = [...adjuntos, ...añadidos];
    nota.textContent = rechazados.length ? `No se adjuntaron (no son texto o superan el límite): ${rechazados.slice(0, 5).join(", ")}${rechazados.length > 5 ? "…" : ""}` : "";
    pintar();
  }
  for (const entrada of [archivos, carpeta]) entrada.addEventListener("change", async () => { await añadir(entrada.files); entrada.value = ""; });
  zona.addEventListener("dragover", (e) => { e.preventDefault(); zona.classList.add("encima"); });
  zona.addEventListener("dragleave", () => zona.classList.remove("encima"));
  zona.addEventListener("drop", (e) => { e.preventDefault(); zona.classList.remove("encima"); añadir(e.dataTransfer.files); });
  pintar();
  zona.append(
    h("div", { class: "fila" },
      boton("Adjuntar archivos", () => archivos.click(), { clase: "pequeno", icono: "subir" }),
      boton("Adjuntar carpeta", () => carpeta.click(), { clase: "pequeno", icono: "carpeta" }),
      compacto ? null : h("span", { class: "tenue", texto: "o arrastra aquí documentos de texto, notas o código." })),
    archivos, carpeta, lista, nota);
  return { nodo: zona, valor: () => adjuntos, vaciar: () => { adjuntos = []; nota.textContent = ""; pintar(); } };
}

/**
 * «Crea un sistema con el agente». `alCrear(id, respuesta)` se llama cuando el agente ha creado el sistema y el panel
 * lo ha traído. Si el agente pregunta algo, la conversación sigue aquí. Con `conBoton: false` lo dispara `crear()`.
 */
export function inicioConAgente({ alCrear, conBoton = true } = {}) {
  let conversacion = null;
  const respuestas = h("div", { class: "pila conversacion", role: "log", "aria-live": "polite", hidden: true });
  const idea = h("textarea", { rows: 5, "aria-label": "Tu idea", maxlength: 6000,
    placeholder: "Por ejemplo: «Quiero que mis agentes revisen los pull requests de mi equipo: que no aprueben sin pruebas, que expliquen los riesgos y que nunca toquen producción»." });
  const etiqueta = h("span", { texto: "Tu idea" });
  const ejemplos = h("div", { class: "fila", role: "group", "aria-label": "Ideas de ejemplo" },
    EJEMPLOS.map((t) => h("button", { type: "button", class: "ejemplo", texto: t, onclick: () => { idea.value = t; idea.focus(); } })));
  const adjuntos = selectorAdjuntos();
  const espera = h("span", { class: "tenue", hidden: true, texto: "El agente está creando tu sistema. Puede tardar un minuto." });

  async function crear() {
    const texto = idea.value.trim();
    const archivos = adjuntos.valor();
    if (texto.length < 10 && !archivos.length) {
      avisar("Cuenta tu idea (al menos una frase) o adjunta archivos", "mal");
      return false;
    }
    const mensaje = texto || DESDE_ARCHIVOS;
    espera.hidden = false;
    try {
      const r = await enviar("/api/agente/turno", { mensaje: conversacion ? mensaje : `${PREFIJO_CREAR}\n\n${mensaje}`, conversacion, adjuntos: archivos });
      conversacion = r.conversacion;
      if (r.borrador) {
        if (r.error_al_traer || r.conflicto_al_traer) avisar(`El sistema se creó en tu cuenta, pero no se pudo traer a este equipo: ${r.error_al_traer || "cambió aquí también"}`, "mal");
        else avisar("Sistema creado. Revisa las propuestas del agente.");
        if (alCrear) await alCrear(r.traido || r.borrador, r);
        return r.traido || r.borrador;
      }
      respuestas.hidden = false;
      respuestas.append(h("div", { class: "mensaje tuyo", texto: mensaje }), h("div", { class: "mensaje ia", texto: r.respuesta }));
      respuestas.scrollTop = respuestas.scrollHeight;
      idea.value = "";
      adjuntos.vaciar();
      etiqueta.textContent = "Tu respuesta";
      ejemplos.hidden = true;
      return false;
    } finally {
      espera.hidden = true;
    }
  }
  idea.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); botonCrear?.click(); } });
  const botonCrear = conBoton ? boton("Crear con el agente", crear, { clase: "primario", icono: "creador" }) : null;
  const nodo = h("div", { class: "pila inicio-agente" },
    h("h3", {}, icono("creador"), " Crea un sistema con el agente"),
    h("p", { class: "tenue", texto: "Cuenta qué quieres gobernar o adjunta lo que ya tengas (documentos, notas, código, procesos). El agente crea el sistema completo y te deja todo como propuestas para que lo revises." }),
    respuestas,
    h("label", { class: "campo" }, etiqueta, idea),
    ejemplos,
    adjuntos.nodo,
    h("div", { class: "fila" }, botonCrear, espera));
  return { nodo, crear };
}
