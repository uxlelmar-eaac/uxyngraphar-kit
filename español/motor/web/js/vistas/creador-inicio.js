// Crear un sistema con el agente (igual que en el Creador web): la persona cuenta su idea y/o adjunta archivos de
// texto; el agente crea el borrador y deja el contenido como propuestas. El panel lo trae a este equipo.

import { enviar } from "../api.js";
import { h, vaciar, boton, avisar, icono } from "../ui.js";
import { anotar } from "../registro.js";
import { mensajeAgente, nuevoIdProgreso, trabajando } from "./agente-chat.js";

export const MAX_ADJUNTOS = 80;
export const MAX_CARACTERES_ADJUNTO = 100_000;
export const MAX_CARACTERES_ADJUNTOS = 200_000;

const CARPETAS_BASURA = new Set([".git", ".hg", ".svn", "node_modules", "__MACOSX", "__pycache__", ".venv", "venv",
  ".idea", ".vscode", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".next", ".cache"]);
const ARCHIVOS_BASURA = /(?:^|\/)(?:\.DS_Store|Thumbs\.db|desktop\.ini|\._[^/]*|[^/]*~|[^/]*\.(?:swp|pyc|pyo))$/i;

/** ¿Se ignora esta ruta? (.git, node_modules, basura del sistema operativo). Igual que en la web y el servidor. */
export function esBasura(ruta) {
  return String(ruta).split("/").some((p) => CARPETAS_BASURA.has(p)) || ARCHIVOS_BASURA.test(ruta);
}

export const PREFIJO_CREAR = "Quiero crear un sistema de gobernanza para agentes de IA. Créalo ahora (borrador y archivos núcleo completos como propuesta) a partir de esta idea y de los archivos adjuntos, si hay:";
export const DESDE_ARCHIVOS = "Crea el sistema de gobernanza a partir de los archivos adjuntos.";
export const EJEMPLOS = [
  ["Revisión de código", "Gobernanza de revisión de código con IA: pruebas obligatorias, explicar riesgos, rechazar secretos y nunca tocar producción."],
  ["Soporte con IA", "Agente de atención al cliente: tono amable, qué puede prometer, cuándo escalar a una persona y qué datos no puede pedir."],
  ["Publicación de contenido", "Agente que prepara publicaciones: quién aprueba, tono de marca, fuentes permitidas y qué no se publica nunca."],
];

const estricto = new TextDecoder("utf-8", { fatal: true });

function comoTexto(datos) {
  try {
    const texto = estricto.decode(datos);
    return texto.includes("\u0000") ? null : texto;
  } catch {
    return null;
  }
}

/** Orden de interés para el agente: documentos, configuración, código, el resto (igual que en la web). */
export function prioridad(ruta) {
  const nombre = (String(ruta).split("/").pop() || "").toLowerCase();
  if (/^(readme|sistema|agents?|claude|contributing)(\.|$)/.test(nombre)) return 0;
  if (/\.(md|mdx|txt|rst|adoc)$/.test(nombre)) return 1;
  if (/\.(json|ya?ml|toml|ini|cfg)$/.test(nombre)) return 2;
  if (/\.(ts|tsx|js|jsx|mjs|py|go|rs|java|kt|swift|rb|php|cs|c|cpp|h|vue|svelte|sql|sh|css|scss|html)$/.test(nombre)) return 3;
  return 4;
}

async function inflar(datos) {
  if (typeof DecompressionStream === "undefined") throw new Error("este navegador no puede abrir zips");
  const flujo = new Blob([datos]).stream().pipeThrough(new DecompressionStream("deflate-raw"));
  return new Uint8Array(await new Response(flujo).arrayBuffer());
}

/** Lee un .zip en el navegador: { archivos: [{ ruta, datos }], ignorados } sin descomprimir .git ni node_modules. */
export async function leerZip(blob) {
  const b = new Uint8Array(await blob.arrayBuffer());
  const v = new DataView(b.buffer, b.byteOffset, b.byteLength);
  let fin = -1;
  for (let i = b.length - 22; i >= Math.max(0, b.length - 65557); i--) {
    if (v.getUint32(i, true) === 0x06054b50) { fin = i; break; }
  }
  if (fin < 0) throw new Error("no es un .zip válido");
  const total = v.getUint16(fin + 10, true);
  let p = v.getUint32(fin + 16, true);
  if (total === 0xffff || p === 0xffffffff || total > 50000) throw new Error("el .zip es demasiado grande");
  const archivos = [];
  let ignorados = 0;
  for (let n = 0; n < total; n++) {
    if (p + 46 > b.length || v.getUint32(p, true) !== 0x02014b50) throw new Error("el .zip está dañado");
    const banderas = v.getUint16(p + 8, true);
    const metodo = v.getUint16(p + 10, true);
    const comprimido = v.getUint32(p + 20, true);
    const largoNombre = v.getUint16(p + 28, true);
    const extra = v.getUint16(p + 30, true);
    const comentario = v.getUint16(p + 32, true);
    const local = v.getUint32(p + 42, true);
    const ruta = new TextDecoder(banderas & 0x0800 ? "utf-8" : "latin1").decode(b.subarray(p + 46, p + 46 + largoNombre));
    p += 46 + largoNombre + extra + comentario;
    if (ruta.endsWith("/")) continue;
    if (esBasura(ruta)) { ignorados++; continue; }
    if (banderas & 0x1 || (metodo !== 0 && metodo !== 8)) continue;
    const inicio = local + 30 + v.getUint16(local + 26, true) + v.getUint16(local + 28, true);
    const crudo = b.subarray(inicio, inicio + comprimido);
    archivos.push({ ruta, datos: metodo === 0 ? crudo : await inflar(crudo) });
  }
  return { archivos, ignorados };
}

/**
 * Lee archivos elegidos (sueltos, de una carpeta o dentro de un .zip) como adjuntos de texto, sin pasarse de los límites.
 * Devuelve { añadidos, rechazados: [{ nombre, motivo }], ignorados, zips: [{ nombre, tomados, total }] }.
 */
export async function leerAdjuntos(archivos, actuales = []) {
  const rechazados = [];
  const zips = [];
  let ignorados = 0;
  const candidatos = [];
  for (const archivo of archivos) {
    const nombre = archivo.webkitRelativePath || archivo.name;
    if (esBasura(nombre)) { ignorados++; continue; }
    if (/\.zip$/i.test(nombre)) {
      try {
        const z = await leerZip(archivo);
        ignorados += z.ignorados;
        zips.push({ nombre, tomados: 0, total: z.archivos.length });
        for (const a of z.archivos) candidatos.push({ nombre: `${nombre}/${a.ruta}`, datos: a.datos, zip: nombre });
      } catch {
        rechazados.push({ nombre, motivo: "zip" });
      }
      continue;
    }
    if (archivo.size > MAX_CARACTERES_ADJUNTO * 4) { rechazados.push({ nombre, motivo: "grande" }); continue; }
    candidatos.push({ nombre, datos: new Uint8Array(await archivo.arrayBuffer()), zip: null });
  }
  candidatos.sort((a, b) => Number(!!a.zip) - Number(!!b.zip) || prioridad(a.nombre) - prioridad(b.nombre) || a.datos.length - b.datos.length);
  const añadidos = [];
  const nombres = new Set(actuales.map((a) => a.nombre));
  let total = actuales.reduce((n, a) => n + a.contenido.length, 0);
  for (const c of candidatos) {
    if (nombres.has(c.nombre)) continue;
    const contenido = comoTexto(c.datos);
    if (contenido === null) { rechazados.push({ nombre: c.nombre, motivo: "binario" }); continue; }
    if (contenido.length > MAX_CARACTERES_ADJUNTO) { rechazados.push({ nombre: c.nombre, motivo: "grande" }); continue; }
    if (actuales.length + añadidos.length >= MAX_ADJUNTOS || total + contenido.length > MAX_CARACTERES_ADJUNTOS) {
      rechazados.push({ nombre: c.nombre, motivo: "limite" });
      continue;
    }
    total += contenido.length;
    nombres.add(c.nombre);
    añadidos.push({ nombre: c.nombre, contenido });
    if (c.zip) zips.find((z) => z.nombre === c.zip).tomados++;
  }
  return { añadidos, rechazados, ignorados, zips };
}

/** Resumen en lenguaje llano de lo que se tomó y lo que se dejó fuera (el mismo texto que en la web). */
export function describirAdjuntos(r) {
  const partes = r.zips.map((z) => z.tomados === z.total
    ? `De ${z.nombre} se tomaron sus ${z.tomados} archivos de texto.`
    : `De ${z.nombre} se tomaron ${z.tomados} de ${z.total} archivos (primero documentos y configuración).`);
  const cuenta = (m) => r.rechazados.filter((x) => x.motivo === m).length;
  const binarios = cuenta("binario");
  const grandes = cuenta("grande");
  const limite = cuenta("limite");
  const malos = r.rechazados.filter((x) => x.motivo === "zip").map((x) => x.nombre);
  if (binarios) partes.push(`${binarios} no ${binarios === 1 ? "es" : "son"} de texto (imágenes u otros) y se omiten.`);
  if (grandes) partes.push(`${grandes} ${grandes === 1 ? "es demasiado grande" : "son demasiado grandes"} (más de 100 mil caracteres).`);
  if (limite) partes.push(`${limite} no caben: el agente recibe como máximo ${MAX_ADJUNTOS} archivos y 200 mil caracteres.`);
  if (r.ignorados) partes.push(`Se ignoraron ${r.ignorados} de .git, node_modules y similares.`);
  if (malos.length) partes.push(`No se pudo abrir: ${malos.join(", ")}.`);
  return partes.join(" ");
}

/** Agrupa los adjuntos para enseñarlos: los de un mismo .zip o carpeta van juntos. [{ clave, archivos }] */
export function agruparAdjuntos(adjuntos) {
  const grupos = new Map();
  for (const a of adjuntos) {
    const zip = a.nombre.match(/^(.*?\.zip)\//i);
    const clave = zip ? zip[1] : a.nombre.includes("/") ? `${a.nombre.split("/")[0]}/` : a.nombre;
    if (!grupos.has(clave)) grupos.set(clave, []);
    grupos.get(clave).push(a);
  }
  return [...grupos].map(([clave, archivos]) => ({ clave, archivos }));
}

/**
 * Caja para escribirle al agente (igual que en la web): texto, archivos adjuntos (sueltos, una carpeta o un .zip,
 * también arrastrándolos) y el botón principal a la derecha. Ctrl+Enter pulsa ese botón.
 * Devuelve { nodo, textarea, adjuntos(), vaciar(), ponerAccion(boton) }.
 */
export function cajaAgente({ etiqueta, placeholder = "", filas = 4, textarea, ocultarEtiqueta = true } = {}) {
  let adjuntos = [];
  let accion = null;
  const area = textarea || h("textarea", { rows: filas, maxlength: 6000 });
  area.classList.add("caja-agente-texto");
  if (placeholder) area.placeholder = placeholder;
  area.setAttribute("aria-label", etiqueta);
  const titulo = h("span", { class: ocultarEtiqueta ? "solo-lector" : "caja-agente-etiqueta", texto: etiqueta });
  const lista = h("ul", { class: "chips", "aria-label": "Archivos adjuntos", hidden: true });
  const meta = h("span", { class: "caja-agente-meta", texto: "También puedes arrastrar archivos aquí" });
  const nota = h("p", { class: "caja-agente-nota", role: "status", hidden: true });
  const archivos = h("input", { type: "file", multiple: true, hidden: true });
  const carpeta = h("input", { type: "file", multiple: true, hidden: true, webkitdirectory: "" });
  const hueco = h("span", { class: "caja-agente-accion" });
  const caja = h("div", { class: "caja-agente" });

  function pintar() {
    vaciar(lista, agruparAdjuntos(adjuntos).map((g) => h("li", { class: "chip", title: g.archivos.map((a) => a.nombre).join("\n") },
      h("span", { class: "chip-nombre", texto: g.archivos.length > 1 || g.clave !== g.archivos[0].nombre ? `${g.clave} · ${g.archivos.length} ${g.archivos.length === 1 ? "archivo" : "archivos"}` : g.clave }),
      h("button", { type: "button", class: "chip-quitar", "aria-label": `Quitar ${g.clave}`, title: "Quitar",
        onclick: () => { adjuntos = adjuntos.filter((x) => !g.archivos.includes(x)); pintar(); } }, icono("cerrar")))),
    agruparAdjuntos(adjuntos).length > 1 ? h("li", {}, h("button", { type: "button", class: "enlace", texto: "Quitar todos", onclick: () => { adjuntos = []; nota.hidden = true; pintar(); } })) : null);
    lista.hidden = !adjuntos.length;
    const caracteres = adjuntos.reduce((n, a) => n + a.contenido.length, 0);
    meta.textContent = adjuntos.length
      ? `${adjuntos.length} ${adjuntos.length === 1 ? "archivo" : "archivos"} · ${Math.ceil(caracteres / 1000)} de 200 mil caracteres`
      : "También puedes arrastrar archivos aquí";
  }
  async function añadir(elegidos) {
    const lista = Array.from(elegidos || []);
    if (!lista.length) return;
    meta.textContent = "Leyendo archivos…";
    try {
      const r = await leerAdjuntos(lista, adjuntos);
      adjuntos = [...adjuntos, ...r.añadidos];
      const texto = describirAdjuntos(r);
      nota.textContent = texto;
      nota.hidden = !texto;
    } catch (e) {
      nota.textContent = `No se pudieron leer los archivos: ${e.message || e}`;
      nota.hidden = false;
    }
    pintar();
  }
  for (const entrada of [archivos, carpeta]) entrada.addEventListener("change", async () => { await añadir(entrada.files); entrada.value = ""; });
  caja.addEventListener("dragover", (e) => { e.preventDefault(); caja.classList.add("encima"); });
  caja.addEventListener("dragleave", () => caja.classList.remove("encima"));
  caja.addEventListener("drop", (e) => { e.preventDefault(); caja.classList.remove("encima"); añadir(e.dataTransfer.files); });
  area.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && accion) { e.preventDefault(); accion.click(); } });
  const pastilla = (texto, icon, titulo, alPulsar) => h("button", { type: "button", class: "pastilla", title: titulo, onclick: alPulsar }, icono(icon), h("span", { texto }));
  caja.append(area, lista,
    h("div", { class: "caja-agente-barra" },
      pastilla("Archivos o .zip", "subir", "Documentos, notas, código o un .zip (se toman sus archivos de texto)", () => archivos.click()),
      pastilla("Carpeta", "carpeta", "Una carpeta entera (se ignoran .git y node_modules)", () => carpeta.click()),
      meta, h("span", { class: "espacio" }), hueco),
    archivos, carpeta);
  pintar();
  return {
    nodo: h("div", { class: "pila caja-agente-envoltorio" }, h("label", { class: "pila" }, titulo), caja, nota),
    textarea: area,
    adjuntos: () => adjuntos,
    vaciar: () => { adjuntos = []; nota.hidden = true; pintar(); },
    ponerAccion: (b) => { accion = b; vaciar(hueco, b); },
    ponerEtiqueta: (t) => { titulo.textContent = t; area.setAttribute("aria-label", t); },
  };
}

/**
 * «Crea un sistema con el agente». `alCrear(id, respuesta)` se llama cuando el agente ha creado el sistema y el panel
 * lo ha traído. Si el agente pregunta algo, la conversación sigue aquí. Con `conBoton: false` lo dispara `crear()`.
 */
export function inicioConAgente({ alCrear, alAntesDeCrear = null, alDespuesDeCrear = null, conBoton = true, cabecera = true } = {}) {
  let conversacion = null;
  const respuestas = h("div", { class: "pila conversacion", role: "log", "aria-live": "polite", hidden: true });
  const caja = cajaAgente({ etiqueta: "Tu idea", placeholder: "¿Qué quieres que sigan tus agentes? Por ejemplo: «Que revisen los pull requests de mi equipo, que no aprueben sin pruebas y que nunca toquen producción»." });
  const idea = caja.textarea;
  const ejemplos = h("div", { class: "fila ejemplos", role: "group", "aria-label": "Prueba con" },
    h("span", { class: "tenue", texto: "Prueba con:" }),
    EJEMPLOS.map(([corto, texto]) => h("button", { type: "button", class: "ejemplo", texto: corto, title: texto, onclick: () => { idea.value = texto; idea.focus(); } })));
  const zonaEspera = h("div", {});
  let fallo = null;

  async function crear() {
    const texto = idea.value.trim();
    const archivos = caja.adjuntos();
    if (texto.length < 10 && !archivos.length) {
      avisar("Cuenta tu idea (al menos una frase) o adjunta archivos", "mal");
      return false;
    }
    if (alAntesDeCrear) await alAntesDeCrear({ idea: texto, adjuntos: archivos.map((a) => a.nombre) });
    const mensaje = texto || DESDE_ARCHIVOS;
    if (fallo) { fallo.remove(); fallo = null; }
    anotar({
      nivel: "info", origen: "agente", titulo: conversacion ? "Turno uxyn (seguir creación)" : "Turno uxyn (crear sistema)",
      datos: { adjuntos: archivos.length, charsIdea: mensaje.length, conversacion },
    });
    const espera = trabajando({ pista: "uxyn está creando tu sistema. Suele tardar menos de un minuto." });
    const progreso = nuevoIdProgreso();
    zonaEspera.append(espera.nodo);
    espera.seguir(progreso);
    try {
      let r;
      try {
        r = await enviar("/api/agente/turno", { mensaje: conversacion ? mensaje : `${PREFIJO_CREAR}\n\n${mensaje}`, conversacion, adjuntos: archivos, progreso });
      } catch (e) {
        anotar({ nivel: "error", origen: "agente", titulo: "Turno uxyn falló al crear", detalle: e.message || String(e) });
        // El texto y los adjuntos siguen en la caja: «Reintentar» repite el mismo envío.
        fallo = mensajeAgente(e.message || String(e), { error: true, extra: [h("div", { class: "fila" }, boton("Reintentar", crear, { clase: "pequeno", icono: "deshacer" }))] });
        zonaEspera.after(fallo);
        return false;
      }
      conversacion = r.conversacion;
      if (r.borrador) {
        if (r.error_al_traer || r.conflicto_al_traer) {
          anotar({
            nivel: "error", origen: "creador",
            titulo: `Borrador «${r.borrador}» en la cuenta, pero no en este equipo`,
            detalle: r.error_al_traer || "conflicto al traer",
            datos: { borrador: r.borrador, traido: r.traido, conversacion: r.conversacion },
          });
          avisar(`El sistema se creó en tu cuenta, pero no se pudo traer a este equipo: ${r.error_al_traer || "cambió aquí también"}`, "mal");
        } else {
          anotar({
            nivel: "info", origen: "creador",
            titulo: `Sistema traído al catálogo local: ${r.traido || r.borrador}`,
            datos: { borrador: r.borrador, traido: r.traido, conversacion: r.conversacion, propuestas: r.propuestas },
          });
          avisar("Sistema creado. Revisa «Por revisar» para aceptar o corregir.");
        }
        if (alCrear) await alCrear(r.traido || r.borrador, r);
        return r.traido || r.borrador;
      }
      anotar({
        nivel: "aviso", origen: "agente", titulo: "uxyn respondió sin crear borrador aún",
        datos: { conversacion: r.conversacion, propuestas: r.propuestas },
      });
      respuestas.hidden = false;
      respuestas.append(h("div", { class: "mensaje tuyo", texto: mensaje }), mensajeAgente(r.respuesta, { acciones: r.acciones }));
      respuestas.scrollTop = respuestas.scrollHeight;
      idea.value = "";
      caja.vaciar();
      caja.ponerEtiqueta("Tu respuesta");
      ejemplos.hidden = true;
      return false;
    } finally {
      espera.parar();
      if (alDespuesDeCrear) await alDespuesDeCrear();
    }
  }
  if (conBoton) caja.ponerAccion(boton("Crear con uxyn", crear, { clase: "primario", icono: "flecha" }));
  const nodo = h("div", { class: "pila inicio-agente" },
    cabecera ? h("div", { class: "inicio-agente-cabecera" },
      h("span", { class: "inicio-agente-insignia", "aria-hidden": "true" }, icono("creador")),
      h("div", {}, h("h3", { texto: "Empezar con uxyn" }),
        h("p", { class: "tenue", texto: "Idea o zip → archivos del sistema. Tú aceptas en «Por revisar»." }))) : null,
    respuestas, zonaEspera, caja.nodo, ejemplos);
  return { nodo, crear };
}
