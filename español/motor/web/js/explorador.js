// Explorador de carpetas servido por el panel (el navegador no puede leer rutas del equipo por sí mismo).

import { obtener, enviar, nombreDe } from "./api.js";
import { h, vaciar, dialogo, insignia, cargando, avisar, icono, elegirVarios } from "./ui.js";

function botonIcono(nombre, titulo, accion) {
  return h("button", { type: "button", class: "boton pequeno", title: titulo, "aria-label": titulo, onclick: accion }, icono(nombre));
}

// Segmentos clicables de la ruta; en Windows el primero es la unidad («C:\»).
function migas(ruta, abrir) {
  const sep = ruta.includes("\\") ? "\\" : "/";
  const partes = ruta.split(sep).filter(Boolean);
  const raiz = sep === "/" ? "/" : partes.shift() + "\\";
  const nodos = [h("button", { type: "button", class: "miga", onclick: () => abrir(raiz) }, sep === "/" ? "/" : raiz)];
  let acumulada = raiz;
  partes.forEach((p, i) => {
    acumulada += (i === 0 || acumulada.endsWith(sep) ? "" : sep) + p;
    const destino = acumulada;
    if (i > 0 || sep !== "/") nodos.push(h("span", { class: "miga-sep", "aria-hidden": "true" }, "›"));
    const ultima = i === partes.length - 1;
    nodos.push(h("button", { type: "button", class: "miga" + (ultima ? " actual" : ""), "aria-current": ultima ? "location" : null,
      onclick: ultima ? null : () => abrir(destino) }, p));
  });
  return nodos;
}

// Abre el explorador y resuelve con la ruta elegida (o null).
export function elegirCarpeta({ titulo = "Elige la carpeta del proyecto", si = "Usar esta carpeta", inicial } = {}) {
  let actual = null;
  const barraMigas = h("nav", { class: "migas-ruta", "aria-label": "Ruta actual" });
  const subir = botonIcono("arriba", "Subir a la carpeta superior", () => actual?.padre && abrir(actual.padre));
  const casa = botonIcono("inicio", "Ir a mi carpeta personal", () => actual && abrir(actual.inicio));
  const lista = h("ul", { class: "explorador-lista", role: "list" });
  const resumen = h("div", { class: "explorador-resumen" });
  const escribir = h("input", { type: "text", class: "explorador-escribir", placeholder: "/ruta/a/tu/proyecto", "aria-label": "Ruta de la carpeta", hidden: true });
  const filtro = h("input", { type: "search", class: "explorador-filtro", placeholder: "Filtrar…", "aria-label": "Filtrar carpetas" });
  const editar = botonIcono("editar", "Escribir la ruta a mano", () => editando(escribir.hidden));

  function editando(si) {
    escribir.hidden = !si;
    barraMigas.hidden = si;
    editar.setAttribute("aria-pressed", String(si));
    if (si) { escribir.value = actual?.ruta || ""; escribir.focus(); escribir.select(); }
  }

  function pintarLista() {
    const t = filtro.value.trim().toLowerCase();
    const visibles = actual.carpetas.filter((c) => !t || c.nombre.toLowerCase().includes(t));
    if (!visibles.length) {
      vaciar(lista, h("li", { class: "explorador-vacio" }, actual.carpetas.length ? "Ninguna carpeta coincide con el filtro." : "Esta carpeta no tiene subcarpetas."));
      return;
    }
    vaciar(lista, visibles.map((c) => h("li", {},
      h("button", { type: "button", class: "explorador-fila", title: c.ruta, onclick: () => abrir(c.ruta) },
        icono("carpeta"), h("span", { class: "explorador-nombre", texto: c.nombre }),
        c.uxyngraphar ? insignia("uxyngraphar", "acento") : null, c.repo ? insignia("git", "bien") : null,
        h("span", { class: "explorador-chevron" }, icono("siguiente"))))));
  }

  async function abrir(destino) {
    vaciar(lista, h("li", { class: "explorador-vacio" }, cargando()));
    try {
      actual = await obtener("/api/proyectos/carpetas", destino ? { ruta: destino } : {});
    } catch (e) {
      avisar(e.message, "mal");
      if (!actual) vaciar(lista);
      else pintarLista();
      return;
    }
    editando(false);
    filtro.value = "";
    subir.disabled = !actual.padre;
    casa.disabled = actual.ruta === actual.inicio;
    vaciar(barraMigas, migas(actual.ruta, abrir));
    barraMigas.scrollLeft = barraMigas.scrollWidth;
    const nombre = actual.ruta.split(/[\\/]/).filter(Boolean).pop() || actual.ruta;
    vaciar(resumen, icono("carpeta"), h("div", { class: "espacio" },
      h("div", {}, "Se añadirá ", h("b", { texto: nombre })),
      h("div", { class: "tenue", texto: actual.repo
        ? "Es un repositorio git: se añadirá como proyecto."
        : "No es un repositorio git: buscaré los proyectos que contenga." })),
    actual.repo ? insignia("git", "bien") : null);
    pintarLista();
  }

  escribir.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && escribir.value.trim()) { e.preventDefault(); abrir(escribir.value.trim()); }
    if (e.key === "Escape") { e.preventDefault(); editando(false); editar.focus(); }
  });
  filtro.addEventListener("input", () => actual && pintarLista());
  filtro.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    lista.querySelector(".explorador-fila")?.click();
  });

  const contenido = h("div", { class: "pila explorador" },
    h("div", { class: "explorador-barra" }, subir, casa, barraMigas, escribir, editar, filtro),
    lista,
    resumen);
  abrir(inicial);
  return dialogo({ titulo, contenido, acciones: [{ texto: si, clase: "primario", accion: () => {
    const escrita = escribir.value.trim();
    return (!escribir.hidden && escrita && escrita !== actual?.ruta ? escrita : actual?.ruta) || false;
  } }] });
}

// Flujo completo «añadir proyectos»: elegir carpeta; si no es un repo, ofrecer los repos que contiene.
export async function agregarProyectos() {
  const carpeta = await elegirCarpeta({ titulo: "Añadir un proyecto", si: "Añadir esta carpeta" });
  if (!carpeta) return [];
  const info = await obtener("/api/proyectos/carpetas", { ruta: carpeta });
  if (info.repo) {
    const hechas = await enviar("/api/proyectos/agregar", { rutas: [info.ruta] });
    avisar("Proyecto añadido");
    return hechas;
  }
  const hallados = await obtener("/api/proyectos/buscar", { ruta: carpeta });
  const nuevos = hallados.filter((p) => !p.registrado);
  if (!nuevos.length) {
    const r = await dialogo({ titulo: "No encontré proyectos ahí", contenido: h("p", { texto: hallados.length
      ? "Todos los proyectos de esa carpeta ya están en tu lista." : "Esa carpeta no es un repositorio git ni contiene ninguno. ¿La añado de todas formas?" }),
      acciones: hallados.length ? [] : [{ texto: "Añadirla igualmente", clase: "primario" }], cancelar: hallados.length ? "Entendido" : "Cancelar" });
    if (!r) return [];
    // una carpeta que no es repositorio ni tiene uxyngraphar: el servidor pide confirmarla con su nombre
    return enviar("/api/proyectos/agregar", { rutas: [info.ruta], confirmar: nombreDe(info.ruta) });
  }
  const opciones = nuevos.map((p) => ({ valor: p.ruta, titulo: p.nombre, detalle: p.ruta + (p.uxyngraphar ? " · ya usa uxyngraphar" : "") }));
  const eleccion = elegirVarios(opciones, opciones.map((o) => o.valor));
  const rutas = await dialogo({ titulo: `Encontré ${nuevos.length} proyecto(s)`, contenido: h("div", { class: "pila" },
    h("p", { texto: "Marca los que quieres gestionar desde el panel." }), eleccion.nodo),
    acciones: [{ texto: "Añadir seleccionados", clase: "primario", accion: () => eleccion.valores() }] });
  if (!rutas || !rutas.length) return [];
  const hechas = await enviar("/api/proyectos/agregar", { rutas });
  avisar(`${hechas.length} proyecto(s) añadido(s)`);
  return hechas;
}
