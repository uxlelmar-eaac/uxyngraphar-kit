// Importar un sistema sin perder nada (1.5.26): zona para soltar un .zip, archivos sueltos o una carpeta entera,
// vista previa de cómo se adapta al esqueleto completo y el resumen final (qué se colocó, qué puso la base, qué se
// conservó tal cual). El servidor del panel hace el trabajo: POST /api/catalogo/importar.

import { enviar } from "../api.js";
import { h, vaciar, boton, icono, avisar, dialogo } from "../ui.js";

const MAX_BYTES = 20 * 1024 * 1024;

const aBase64 = (archivo) => new Promise((resolver, rechazar) => {
  const lector = new FileReader();
  lector.onload = () => resolver(String(lector.result).split(",", 2)[1] || "");
  lector.onerror = () => rechazar(lector.error || new Error(`No se pudo leer ${archivo.name}`));
  lector.readAsDataURL(archivo);
});

/** Archivos de un «drop», entrando en las carpetas: [{archivo, ruta}]. */
async function archivosDelDrop(dt) {
  const salida = [];
  const entradas = [...(dt.items || [])].map((i) => i.webkitGetAsEntry?.()).filter(Boolean);
  if (!entradas.length) return [...(dt.files || [])].map((archivo) => ({ archivo, ruta: archivo.name }));
  const leerEntrada = async (e, prefijo) => {
    if (e.isFile) {
      const archivo = await new Promise((ok, mal) => e.file(ok, mal));
      salida.push({ archivo, ruta: `${prefijo}${e.name}` });
    } else if (e.isDirectory) {
      const lector = e.createReader();
      let lote;
      do {
        lote = await new Promise((ok, mal) => lector.readEntries(ok, mal));
        for (const hijo of lote) await leerEntrada(hijo, `${prefijo}${e.name}/`);
      } while (lote.length);
    }
  };
  for (const e of entradas) await leerEntrada(e, "");
  return salida;
}

/** Cuerpo del pedido para el servidor a partir de lo elegido: un .zip solo, o la lista de archivos. */
export async function cuerpoImportacion(elegidos) {
  const total = elegidos.reduce((s, x) => s + x.archivo.size, 0);
  if (!elegidos.length) throw new Error("Elige o suelta un .zip, archivos o una carpeta.");
  if (total > MAX_BYTES) throw new Error("Es demasiado grande: hasta 20 MB.");
  if (elegidos.length === 1 && /\.zip$/i.test(elegidos[0].archivo.name)) {
    return { zip: await aBase64(elegidos[0].archivo), nombre: elegidos[0].archivo.name };
  }
  const archivos = [];
  for (const x of elegidos) archivos.push({ ruta: x.ruta, datos: await aBase64(x.archivo) });
  const raiz = elegidos[0].ruta.includes("/") ? elegidos[0].ruta.split("/")[0] : "";
  return { archivos, nombre: raiz };
}

/** Lista de una sección del resumen. */
function seccion(titulo, items, { clase = "", vacio = "", pintar }) {
  return h("details", { class: `resumen-import-seccion ${clase}`.trim(), open: items.length > 0 && items.length <= 12 },
    h("summary", {}, h("span", { class: "resumen-import-titulo", texto: titulo }), h("span", { class: "insignia", texto: String(items.length) })),
    items.length ? h("ul", { class: "resumen-import-lista" }, items.map(pintar)) : h("p", { class: "tenue", texto: vacio }));
}

const flecha = (x) => h("li", {}, h("code", { texto: x.de }), x.de !== x.a ? [" → ", h("code", { texto: x.a })] : null,
  x.motivo ? h("span", { class: "tenue", texto: ` · ${x.motivo}` }) : null);

/** El resumen de una importación (o de su vista previa). */
export function resumenImportacion(r) {
  const pendientes = (r.errores || []).length;
  return h("div", { class: "resumen-import pila" },
    h("div", { class: "resumen-import-cifras" },
      h("div", { class: "cifra-mini" }, h("b", { texto: String((r.mapeados || []).length + (r.fusionados || []).length) }), h("span", { texto: "colocados o fusionados" })),
      h("div", { class: "cifra-mini" }, h("b", { texto: String((r.conservados || []).length) }), h("span", { texto: "conservados tal cual" })),
      h("div", { class: "cifra-mini" }, h("b", { texto: String((r.de_la_base || []).length) }), h("span", { texto: "añadidos desde la base" })),
      h("div", { class: "cifra-mini" }, h("b", { texto: String(r.total_importados ?? "") }), h("span", { texto: "archivos tuyos, ninguno descartado" }))),
    seccion("Colocados en su sitio", r.mapeados || [], { vacio: "Nada que mover: tus rutas ya encajan.", pintar: flecha }),
    seccion("Fusionados (tus valores mandan)", r.fusionados || [], { vacio: "No hubo configuraciones que fusionar.", pintar: flecha }),
    seccion("Conservados tal cual", r.conservados || [], { vacio: "—", pintar: flecha }),
    seccion("Añadidos desde la base", r.de_la_base || [], { clase: "base", vacio: "Tus archivos ya cubrían todo el esqueleto.", pintar: (x) => h("li", {}, h("code", { texto: x })) }),
    (r.renombrados || []).length ? seccion("Nombres saneados (ASCII sin espacios)", r.renombrados, { pintar: flecha }) : null,
    (r.ignorados || []).length ? seccion("Ignorados (basura del sistema operativo)", r.ignorados, { pintar: (x) => h("li", {}, h("code", { texto: x })) }) : null,
    (r.avisos || []).length ? h("ul", { class: "banda aviso resumen-import-avisos" }, r.avisos.map((a) => h("li", { texto: a }))) : null,
    pendientes ? h("p", { class: "tenue", texto: `Quedan ${pendientes} cosa(s) por completar (huecos {{…}} de la base, sobre todo). El editor te lleva a cada una.` }) : null);
}

/** Modo «Subir zip o archivos» del asistente de creación. Devuelve { nodo, crear() }. */
export function modoImportar() {
  let elegidos = [];
  let previa = null;
  const id = h("input", { type: "text", placeholder: "se toma de tu sistema.json o del nombre del zip", "aria-label": "Identificador (opcional)" });
  const lista = h("div", { class: "zona-soltar-lista tenue", "aria-live": "polite" });
  const resultado = h("div", { class: "resumen-import-previa" });
  const entradaArchivos = h("input", { type: "file", multiple: true, hidden: true, accept: "*/*" });
  const entradaCarpeta = h("input", { type: "file", multiple: true, hidden: true, webkitdirectory: "" });
  const pintarLista = () => {
    if (!elegidos.length) { vaciar(lista, "Nada elegido todavía."); return; }
    const total = elegidos.reduce((s, x) => s + x.archivo.size, 0);
    const muestra = elegidos.slice(0, 6).map((x) => x.ruta).join(", ");
    vaciar(lista, h("b", { texto: `${elegidos.length} archivo(s)` }), ` · ${(total / 1024).toFixed(0)} KB · ${muestra}${elegidos.length > 6 ? "…" : ""}`);
  };
  const poner = async (nuevos) => {
    elegidos = nuevos;
    previa = null;
    pintarLista();
    vaciar(resultado);
    if (elegidos.length) await comprobar().catch((e) => vaciar(resultado, h("p", { class: "banda mal", texto: e.message || String(e) })));
  };
  entradaArchivos.addEventListener("change", () => poner([...entradaArchivos.files].map((archivo) => ({ archivo, ruta: archivo.name }))));
  entradaCarpeta.addEventListener("change", () => poner([...entradaCarpeta.files].map((archivo) => ({ archivo, ruta: archivo.webkitRelativePath || archivo.name }))));
  const zona = h("div", { class: "zona-soltar", tabindex: "0", role: "button", "aria-label": "Suelta aquí un .zip, archivos o una carpeta, o pulsa para elegir archivos" },
    h("span", { class: "zona-soltar-icono", "aria-hidden": "true" }, icono("subirArchivo")),
    h("b", { texto: "Suelta aquí un .zip, archivos o una carpeta" }),
    h("span", { class: "tenue", texto: "Se adapta al esqueleto completo de un sistema de gobernanza. Nada de lo tuyo se descarta." }),
    h("div", { class: "fila vacio-acciones" },
      boton("Elegir archivos o .zip", () => entradaArchivos.click(), { clase: "pequeno", icono: "zip" }),
      boton("Elegir una carpeta", () => entradaCarpeta.click(), { clase: "pequeno", icono: "carpeta" })),
    entradaArchivos, entradaCarpeta);
  zona.addEventListener("keydown", (e) => { if ((e.key === "Enter" || e.key === " ") && e.target === zona) { e.preventDefault(); entradaArchivos.click(); } });
  zona.addEventListener("dragover", (e) => { e.preventDefault(); zona.classList.add("encima"); });
  zona.addEventListener("dragleave", () => zona.classList.remove("encima"));
  zona.addEventListener("drop", async (e) => {
    e.preventDefault();
    zona.classList.remove("encima");
    await poner(await archivosDelDrop(e.dataTransfer));
  });
  async function comprobar() {
    vaciar(resultado, h("div", { class: "cargando" }, h("div", { class: "giro" }), "Preparando la vista previa…"));
    const cuerpo = await cuerpoImportacion(elegidos);
    previa = await enviar("/api/catalogo/importar", { ...cuerpo, id: id.value.trim(), aplicar: false });
    if (!id.value.trim()) id.placeholder = previa.id;
    vaciar(resultado, h("p", {}, h("b", { texto: `Así quedará «${previa.id}»` }), h("span", { class: "tenue", texto: " (vista previa: aún no se ha creado nada)" })), resumenImportacion(previa));
  }
  const nodo = h("div", { class: "pila modo-importar" }, zona, lista,
    h("label", { class: "campo" }, "Identificador (opcional)", id), resultado);
  return {
    nodo,
    async crear() {
      const cuerpo = await cuerpoImportacion(elegidos);
      const r = await enviar("/api/catalogo/importar", { ...cuerpo, id: id.value.trim(), aplicar: true });
      setTimeout(() => dialogo({ titulo: `«${r.id}» creado: así se importó`, contenido: resumenImportacion(r), cancelar: "Cerrar" }), 60);
      avisar(`Sistema «${r.id}» creado con ${r.total_importados} archivo(s) tuyos`);
      return r.id;
    },
    hayAlgo: () => elegidos.length > 0,
  };
}
