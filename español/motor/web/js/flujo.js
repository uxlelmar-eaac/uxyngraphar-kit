// Flujo del asistente: diagrama para verlo y editor para cambiarlo sin escribir ids ni JSON.

import { h, vaciar } from "./ui.js";

export const MODOS = {
  manual: { titulo: "Solo cuando lo pida", texto: "El asistente usa un sistema únicamente si lo nombras en tu pedido." },
  leer_por_defecto: { titulo: "Tenerlos presentes", texto: "Lee estos sistemas en cada pedido, pero solo aplica los que nombres." },
  trabajar_con: { titulo: "Sistema base", texto: "Aplica siempre un sistema base en cada pedido, además de los que nombres." },
  secuencia: { titulo: "Pasos en orden", texto: "Recorre estos sistemas uno tras otro, en el orden que elijas." },
};

export const FLUJO_VACIO = { formato: 1, modo: "manual", leer_por_defecto: [], trabajar_con: null, secuencia: [], conflictos: "preguntar" };

const titulo = (sistemas, id) => (sistemas.find((p) => p.id === id) || {}).titulo || id;
const nodo = (texto, clase = "", detalle = "") => h("div", { class: `nodo ${clase}` }, texto, detalle ? h("small", { texto: detalle }) : null);
const flecha = () => h("span", { class: "flecha", "aria-hidden": "true", texto: "→" });

export function diagrama(flujo, sistemas) {
  const f = { ...FLUJO_VACIO, ...(flujo || {}) };
  const partes = [nodo("Tu pedido", "extremo")];
  if (f.modo === "manual") partes.push(flecha(), nodo("Sistemas que nombres", "", "solo si los pides"));
  if (f.modo === "leer_por_defecto") partes.push(flecha(), nodo(`Tiene presentes ${f.leer_por_defecto.length}`, "", f.leer_por_defecto.map((id) => titulo(sistemas, id)).join(", ")), flecha(), nodo("Aplica los que nombres"));
  if (f.modo === "trabajar_con") partes.push(flecha(), nodo(titulo(sistemas, f.trabajar_con), "base", "sistema base, siempre"), flecha(), nodo("+ los que nombres"));
  if (f.modo === "secuencia") f.secuencia.forEach((id, i) => partes.push(flecha(), nodo(`${i + 1}. ${titulo(sistemas, id)}`, i === 0 ? "base" : "")));
  partes.push(flecha(), nodo("Resultado", "extremo"));
  return h("div", { class: "diagrama", role: "img", "aria-label": `Flujo: ${MODOS[f.modo]?.titulo || f.modo}` }, partes);
}

// Editor. `sistemas`: [{id, titulo, descripcion}] que el flujo puede usar. Devuelve { nodo, valor() }.
export function editorFlujo(flujoInicial, sistemas, alCambiar = () => {}) {
  const f = { ...FLUJO_VACIO, ...(flujoInicial || {}) };
  f.leer_por_defecto = [...f.leer_por_defecto];
  f.secuencia = [...f.secuencia];
  const raiz = h("div", { class: "pila" });
  const nombreGrupo = "modo-" + Math.random().toString(36).slice(2);

  function valor() {
    return { formato: 1, conflictos: "preguntar", modo: f.modo,
      leer_por_defecto: f.modo === "leer_por_defecto" ? f.leer_por_defecto : [],
      trabajar_con: f.modo === "trabajar_con" ? f.trabajar_con : null,
      secuencia: f.modo === "secuencia" ? f.secuencia : [] };
  }

  function cambiar() { pintar(); alCambiar(valor()); }

  function selectorModo() {
    return h("div", { class: "modos", role: "radiogroup", "aria-label": "Cómo trabaja el asistente" },
      Object.entries(MODOS).map(([id, m]) => h("label", { class: "modo" },
        h("input", { type: "radio", name: nombreGrupo, value: id, checked: f.modo === id, onchange: () => { f.modo = id; cambiar(); } }),
        h("b", { texto: m.titulo }), h("div", { class: "tenue", texto: m.texto }))));
  }

  function detalle() {
    if (!sistemas.length && f.modo !== "manual") return h("p", { class: "banda aviso", texto: "Primero instala algún sistema en este proyecto." });
    if (f.modo === "leer_por_defecto") {
      return h("div", { class: "pila" }, h("h3", { texto: "¿Qué sistemas debe tener presentes?" }),
        h("ul", { class: "lista" }, sistemas.map((p) => h("li", {}, h("label", { class: "casilla", style: "flex:1" },
          h("input", { type: "checkbox", checked: f.leer_por_defecto.includes(p.id), onchange: (e) => {
            f.leer_por_defecto = e.target.checked ? [...f.leer_por_defecto, p.id] : f.leer_por_defecto.filter((x) => x !== p.id);
            cambiar();
          } }), h("span", {}, h("b", { texto: p.titulo }), h("div", { class: "tenue", texto: p.descripcion || "" })))))));
    }
    if (f.modo === "trabajar_con") {
      return h("label", { class: "campo" }, "Sistema base (se aplica en cada pedido)",
        h("select", { onchange: (e) => { f.trabajar_con = e.target.value || null; cambiar(); } },
          h("option", { value: "", texto: "— Elige un sistema —" }),
          sistemas.map((p) => h("option", { value: p.id, selected: f.trabajar_con === p.id, texto: p.titulo }))));
    }
    if (f.modo === "secuencia") return editorPasos();
    return null;
  }

  function editorPasos() {
    const lista = h("ol", { class: "pasos" });
    let arrastrado = null;
    f.secuencia.forEach((id, i) => {
      const mover = (d) => { const j = i + d; [f.secuencia[i], f.secuencia[j]] = [f.secuencia[j], f.secuencia[i]]; cambiar(); };
      const li = h("li", { draggable: true },
        h("span", { class: "asa", title: "Arrastra para reordenar", "aria-hidden": "true", texto: "⠿" }),
        h("span", { class: "numero", texto: String(i + 1) }), h("span", { class: "espacio", texto: titulo(sistemas, id) }),
        h("button", { type: "button", class: "boton pequeno fantasma", disabled: i === 0, "aria-label": "Subir paso", onclick: () => mover(-1) }, "↑"),
        h("button", { type: "button", class: "boton pequeno fantasma", disabled: i === f.secuencia.length - 1, "aria-label": "Bajar paso", onclick: () => mover(1) }, "↓"),
        h("button", { type: "button", class: "boton pequeno peligro", "aria-label": "Quitar paso", onclick: () => { f.secuencia.splice(i, 1); cambiar(); } }, "Quitar"));
      li.addEventListener("dragstart", () => { arrastrado = i; li.classList.add("arrastrando"); });
      li.addEventListener("dragend", () => li.classList.remove("arrastrando"));
      li.addEventListener("dragover", (e) => e.preventDefault());
      li.addEventListener("drop", (e) => {
        e.preventDefault();
        if (arrastrado === null || arrastrado === i) return;
        const [movido] = f.secuencia.splice(arrastrado, 1);
        f.secuencia.splice(i, 0, movido);
        cambiar();
      });
      lista.append(li);
    });
    const libres = sistemas.filter((p) => !f.secuencia.includes(p.id));
    const elegir = h("select", { "aria-label": "Sistema para el siguiente paso" }, libres.map((p) => h("option", { value: p.id, texto: p.titulo })));
    return h("div", { class: "pila" }, h("h3", { texto: "Pasos (arrastra o usa las flechas para ordenarlos)" }),
      f.secuencia.length ? lista : h("p", { class: "tenue", texto: "Aún no hay pasos." }),
      libres.length ? h("div", { class: "fila" }, h("div", { class: "espacio" }, elegir),
        h("button", { type: "button", class: "boton", onclick: () => { f.secuencia.push(elegir.value); cambiar(); } }, "Añadir paso")) : null);
  }

  function pintar() {
    vaciar(raiz, h("h3", { texto: "Así trabajará el asistente" }), diagrama(valor(), sistemas),
      h("h3", { texto: "¿Cómo quieres que trabaje?", style: "margin-top:8px" }), selectorModo(), detalle());
  }

  pintar();
  return { nodo: raiz, valor };
}
