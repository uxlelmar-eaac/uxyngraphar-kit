// Estructura de un sistema: su árbol de carpetas y archivos, con qué es cada pieza y una vista previa de solo lectura.
// La usan «Mis sistemas» (panel al elegir un sistema) y el Taller. Igual que en la web (uxyngraphar-frontend,
// creator/components/SystemStructure.tsx): mismas descripciones de carpetas y la misma forma de contar.

import { obtener } from "../api.js";
import { h, vaciar, boton, icono } from "../ui.js";
import { markdownANodos } from "../editor-codigo.js";
import { arbolDeRutas } from "./editor-archivos.js";

/** Qué es cada pieza conocida de un sistema de gobernanza (archivos del núcleo y carpetas del esqueleto). */
export const QUE_ES = {
  "sistema.json": "Manifiesto: título, alcance, permisos y cuándo se activa",
  "README.md": "Presentación para quien lo instala",
  "SISTEMA.md": "Qué garantiza, cuándo se usa y qué deja",
  "LIMITES.md": "Reglas duras y cuándo parar a preguntar",
  "PERMISOS.md": "Qué hace el agente solo y qué decide la persona",
  "MEMORIAS.md": "Qué recordar entre conversaciones",
  "HERRAMIENTAS.md": "Herramientas y scripts que puede usar",
  "CHANGELOG.md": "Historial de versiones",
  proceso: "Fases del trabajo, en orden",
  skills: "Habilidades que el agente puede invocar",
  prompts: "Instrucciones reutilizables",
  config: "Ajustes que la persona puede cambiar",
  plantillas: "Documentos que el agente rellena",
  referencia: "Material de consulta",
  ejemplos: "Casos resueltos de muestra",
  pruebas: "Comprobaciones del sistema",
  scripts: "Scripts que el sistema ejecuta",
};

/** Cuántas carpetas y archivos tiene una lista de rutas. */
export function contarEstructura(rutas) {
  const carpetas = new Set();
  for (const r of rutas) {
    const partes = r.split("/");
    for (let i = 1; i < partes.length; i++) carpetas.add(partes.slice(0, i).join("/"));
  }
  return { carpetas: carpetas.size, archivos: rutas.length };
}

const plural = (n, uno, varios) => `${n} ${n === 1 ? uno : varios}`;

/**
 * Árbol navegable + vista previa. `id`: sistema del catálogo local. `alAbrir(rel)`: abre ese archivo en el Taller.
 * Devuelve el nodo (carga en segundo plano).
 */
export function estructuraSistema(id, { alAbrir = null } = {}) {
  const plegadas = new Set();
  let rutas = [];
  let elegido = null;
  const resumen = h("p", { class: "tenue estructura-resumen", texto: "Cargando archivos…" });
  const arbol = h("ul", { class: "estructura-arbol", role: "tree", "aria-label": "Carpetas y archivos del sistema" });
  const previa = h("div", { class: "estructura-previa", "aria-live": "polite" },
    h("p", { class: "tenue", texto: "Elige un archivo para verlo aquí." }));

  function fila({ rel, nombre, carpeta, nivel, cuantos }) {
    const plegada = carpeta && plegadas.has(rel);
    const que = QUE_ES[rel] || null;
    const b = h("button", {
      type: "button", class: `estructura-nodo ${carpeta ? "es-carpeta" : "es-archivo"}${elegido === rel ? " activo" : ""}`,
      style: `--nivel:${nivel}`, "aria-expanded": carpeta ? String(!plegada) : null, "aria-current": elegido === rel ? "true" : null,
      title: que || rel,
      onclick: () => {
        if (carpeta) { if (plegada) plegadas.delete(rel); else plegadas.add(rel); pintar(); }
        else void verArchivo(rel);
      },
    },
    h("span", { class: "estructura-flecha", "aria-hidden": "true", texto: carpeta ? (plegada ? "▸" : "▾") : "" }),
    icono(carpeta ? "carpeta" : "lista"),
    h("span", { class: "estructura-nombre", texto: carpeta ? `${nombre}/` : nombre }),
    carpeta ? h("span", { class: "contador", texto: String(cuantos) }) : null,
    que ? h("span", { class: "estructura-que", texto: que }) : null);
    return h("li", { role: "treeitem" }, b);
  }

  function pintar() {
    const items = [];
    const total = (nodo) => nodo.archivos.length + [...nodo.carpetas.values()].reduce((s, c) => s + total(c), 0);
    const recorrer = (nodo, prefijo, nivel) => {
      // Primero los archivos de la raíz (el núcleo), después las carpetas: así se lee como el esqueleto.
      for (const rel of [...nodo.archivos].sort((a, b) => a.localeCompare(b))) {
        items.push(fila({ rel, nombre: rel.split("/").pop(), carpeta: false, nivel }));
      }
      for (const nombre of [...nodo.carpetas.keys()].sort((a, b) => a.localeCompare(b))) {
        const rel = prefijo ? `${prefijo}/${nombre}` : nombre;
        const hijo = nodo.carpetas.get(nombre);
        items.push(fila({ rel, nombre, carpeta: true, nivel, cuantos: total(hijo) }));
        if (!plegadas.has(rel)) recorrer(hijo, rel, nivel + 1);
      }
    };
    recorrer(arbolDeRutas(rutas), "", 0);
    vaciar(arbol, items.length ? items : h("li", { class: "tenue", texto: "Sin archivos." }));
  }

  async function verArchivo(rel) {
    elegido = rel;
    pintar();
    vaciar(previa, h("p", { class: "tenue", texto: `Cargando ${rel}…` }));
    try {
      const r = await obtener("/api/catalogo/archivo", { id, rel });
      const texto = String(r?.contenido ?? "");
      vaciar(previa,
        h("div", { class: "fila separada estructura-previa-cabeza" },
          h("code", { texto: rel }),
          alAbrir ? boton("Abrir en el Taller", () => alAbrir(rel), { clase: "pequeno", icono: "editar" }) : null),
        rel.endsWith(".md") ? markdownANodos(texto) : h("pre", { class: "estructura-codigo", texto }));
    } catch (e) {
      vaciar(previa, h("div", { class: "banda mal", texto: `No se pudo abrir ${rel}: ${e.message || e}` }));
    }
  }

  const nodo = h("div", { class: "estructura" },
    h("div", { class: "estructura-lado" }, resumen, arbol),
    previa);

  void (async () => {
    try {
      rutas = (await obtener("/api/catalogo/archivos", { id })) || [];
      const { carpetas, archivos } = contarEstructura(rutas);
      resumen.textContent = `${plural(carpetas, "carpeta", "carpetas")} · ${plural(archivos, "archivo", "archivos")}`;
      pintar();
      const primero = ["README.md", "SISTEMA.md", "sistema.json"].find((r) => rutas.includes(r)) || rutas[0];
      if (primero) await verArchivo(primero);
    } catch (e) {
      resumen.textContent = `No se pudieron leer los archivos: ${e.message || e}`;
    }
  })();
  return nodo;
}
