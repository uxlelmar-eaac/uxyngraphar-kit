// Piezas de interfaz: crear elementos sin inyectar HTML, avisos, diálogos, estados de carga y vacío, iconos.

export function h(etiqueta, props, ...hijos) {
  const el = document.createElement(etiqueta);
  for (const [clave, valor] of Object.entries(props || {})) {
    if (valor === null || valor === undefined || valor === false) continue;
    if (clave.startsWith("on") && typeof valor === "function") el.addEventListener(clave.slice(2), valor);
    else if (clave === "class") el.className = valor;
    else if (clave === "texto") el.textContent = valor;
    else if (clave === "style") el.style.cssText = valor;   // CSSOM: lo permite la CSP, un atributo style no
    else if (clave in el && typeof valor !== "string") el[clave] = valor;
    else el.setAttribute(clave, valor === true ? "" : valor);
  }
  agregar(el, hijos);
  return el;
}

function agregar(el, hijos) {
  for (const hijo of hijos.flat(Infinity)) {
    if (hijo === null || hijo === undefined || hijo === false) continue;
    el.append(hijo instanceof Node ? hijo : document.createTextNode(String(hijo)));
  }
}

export function vaciar(el, ...hijos) { el.replaceChildren(); agregar(el, hijos); return el; }

const TRAZOS = {
  inicio: "M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z",
  proyectos: "M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
  flujos: "M5 5h5v5H5zM14 14h5v5h-5zM7.5 10v4a2 2 0 0 0 2 2H14M14 7.5h3a2 2 0 0 1 2 2V14",
  catalogo: "M4 5h7v6H4zM13 5h7v6h-7zM4 13h7v6H4zM13 13h7v6h-7z",
  herramienta: "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19 12l2-1-1-3-2 .3-1.4-1.4.3-2-3-1-1 2h-2l-1-2-3 1 .3 2L5.7 7.3 3.7 7l-1 3 2 1v2l-2 1 1 3 2-.3 1.4 1.4-.3 2 3 1 1-2h2l1 2 3-1-.3-2 1.4-1.4 2 .3 1-3-2-1z",
  mas: "M12 5v14M5 12h14",
  carpeta: "M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
  buscar: "M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM21 21l-5-5",
  flecha: "M5 12h14M13 6l6 6-6 6",
  descargar: "M12 4v12M6 10l6 6 6-6M4 20h16",
  subir: "M12 20V8M6 14l6-6 6 6M4 4h16",
  check: "M5 12l5 5 9-10",
  deshacer: "M9 14L4 9l5-5M4 9h10a6 6 0 0 1 0 12h-3",
  arriba: "M12 19V5M5 12l7-7 7 7",
  siguiente: "M9 6l6 6-6 6",
  editar: "M4 20h4L19 9l-4-4L4 16zM13 7l4 4",
};

export function icono(nombre) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "2");
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  svg.setAttribute("aria-hidden", "true");
  const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
  p.setAttribute("d", TRAZOS[nombre] || "");
  svg.append(p);
  return svg;
}

export function boton(texto, accion, { clase = "", icono: nombreIcono, titulo } = {}) {
  const b = h("button", { type: "button", class: `boton ${clase}`.trim(), title: titulo }, nombreIcono ? icono(nombreIcono) : null, texto);
  b.addEventListener("click", () => ocupado(b, accion));
  return b;
}

export async function ocupado(b, accion) {
  if (!accion || b.disabled) return;
  const antes = [...b.childNodes];
  b.disabled = true;
  b.replaceChildren(h("span", { class: "giro", "aria-hidden": "true" }), " Un momento…");
  try {
    await accion();
  } catch (e) {
    avisar(e.message || String(e), "mal");
  } finally {
    if (b.isConnected) { b.disabled = false; b.replaceChildren(...antes); }
  }
}

export function avisar(texto, tipo = "") {
  const a = h("div", { class: `aviso ${tipo}`, texto });
  document.getElementById("avisos").append(a);
  setTimeout(() => a.remove(), tipo === "mal" ? 8000 : 4500);
}

export const insignia = (texto, tipo = "") => h("span", { class: `insignia ${tipo}`, texto });
export const cargando = (texto = "Cargando…") => h("div", { class: "cargando" }, h("span", { class: "giro" }), texto);
export const vacio = (titulo, texto, ...acciones) => h("div", { class: "vacio" }, h("h3", { texto: titulo }), h("p", { texto }), h("div", { class: "fila", style: "justify-content:center" }, acciones));

export function cabecera(titulo, descripcion, ...acciones) {
  return h("div", { class: "cabecera" }, h("div", {}, h("h1", { texto: titulo }), descripcion ? h("p", { texto: descripcion }) : null),
    h("div", { class: "fila" }, acciones));
}

// Diálogo genérico. `acciones`: [{ texto, clase, accion }]; si `accion` devuelve algo distinto de false, se cierra
// y la promesa se resuelve con ese valor. Cerrar o cancelar resuelve con null.
export function dialogo({ titulo, contenido, acciones = [], cancelar = "Cancelar" }) {
  const d = document.getElementById("dialogo");
  return new Promise((resolver) => {
    const terminar = (valor) => { d.close(); resolver(valor); };
    const botones = acciones.map((a) => {
      const b = h("button", { type: "button", class: `boton ${a.clase || ""}` }, a.texto);
      b.addEventListener("click", () => ocupado(b, async () => {
        const r = a.accion ? await a.accion() : true;
        if (r !== false) terminar(r === undefined ? true : r);
      }));
      return b;
    });
    vaciar(d, h("div", { class: "dialogo-cuerpo" }, h("h2", { texto: titulo }), contenido),
      h("div", { class: "dialogo-pie" }, cancelar ? h("button", { type: "button", class: "boton fantasma", onclick: () => terminar(null) }, cancelar) : null, botones));
    d.onclose = () => { if (!d.open) resolver(null); };   // un «close» tardío del diálogo anterior llega con este ya abierto
    d.showModal();
    (d.querySelector("input:not([hidden]), select, textarea") || botones[botones.length - 1])?.focus();
  });
}

export async function confirmar({ titulo, texto, si = "Sí, continuar", peligro = false, casilla }) {
  const marca = casilla ? h("input", { type: "checkbox" }) : null;
  const contenido = h("div", { class: "pila" }, h("p", { texto }), casilla ? h("label", { class: "casilla" }, marca, h("span", { texto: casilla })) : null);
  const r = await dialogo({ titulo, contenido, acciones: [{ texto: si, clase: peligro ? "peligro lleno" : "primario", accion: () => ({ casilla: !!marca?.checked }) }] });
  return r || null;
}

export async function pedirDatos({ titulo, explicacion, campos, si = "Guardar" }) {
  const entradas = campos.map((c) => h("input", { type: "text", value: c.valor || "", placeholder: c.ayuda || "", "aria-label": c.etiqueta }));
  const contenido = h("div", { class: "pila" }, explicacion ? h("p", { class: "tenue", texto: explicacion }) : null,
    campos.map((c, i) => h("label", { class: "campo" }, c.etiqueta, entradas[i])));
  return dialogo({ titulo, contenido, acciones: [{ texto: si, clase: "primario", accion: () => {
    const valores = Object.fromEntries(campos.map((c, i) => [c.nombre, entradas[i].value.trim()]));
    const falta = campos.find((c) => c.obligatorio && !valores[c.nombre]);
    if (falta) { avisar(`Falta: ${falta.etiqueta}`, "mal"); return false; }
    return valores;
  } }] });
}

export function elegirVarios(opciones, marcados = []) {
  const casillas = opciones.map((o) => h("input", { type: "checkbox", value: o.valor, checked: marcados.includes(o.valor) }));
  const lista = h("ul", { class: "lista desplazable" }, opciones.map((o, i) => h("li", {},
    h("label", { class: "casilla", style: "flex:1" }, casillas[i], h("span", {}, h("b", { texto: o.titulo }), o.detalle ? h("div", { class: "tenue", texto: o.detalle }) : null)))));
  return { nodo: lista, valores: () => casillas.filter((c) => c.checked).map((c) => c.value) };
}

export function descargarJSON(nombre, datos) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(datos, null, 2)], { type: "application/json" }));
  const a = h("a", { href: url, download: nombre });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function pestanas(nombres, alCambiar, inicial) {
  const barra = h("div", { class: "pestanas", role: "tablist" });
  const botones = nombres.map(([id, texto]) => h("button", { type: "button", role: "tab", "aria-selected": String(id === inicial), onclick: () => elegir(id) }, texto));
  function elegir(id) {
    botones.forEach((b, i) => b.setAttribute("aria-selected", String(nombres[i][0] === id)));
    alCambiar(id);
  }
  barra.append(...botones);
  return barra;
}
