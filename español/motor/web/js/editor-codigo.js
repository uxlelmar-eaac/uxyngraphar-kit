// Editor de código ligero, sin dependencias externas (cumple la CSP «default-src 'self'»): un <textarea> real (deshacer,
// pegar, selección, lectores de pantalla y móviles funcionan como siempre) sobre una capa con resaltado de sintaxis y
// números de línea. Lenguajes: Markdown, JSON, Python, YAML y shell. Incluye buscar y reemplazar, marcas de error por
// línea y una vista previa de Markdown que construye nodos (sin HTML inyectado).

import { h, icono } from "./ui.js";

const MARCADOR = [/\{\{[^{}\n]*\}\}/y, "t-marcador"];
const CADENA_DOBLE = /"(?:[^"\\\n]|\\.)*"?/y;
const CADENA_SIMPLE = /'(?:[^'\\\n]|\\.)*'?/y;
const NUMERO = [/-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b/y, "t-numero"];
const COMENTARIO_ALMOHADILLA = [/#.*/y, "t-comentario", (linea, i) => i === 0 || /\s/.test(linea[i - 1])];

const REGLAS = {
  json: [
    [/"(?:[^"\\\n]|\\.)*"(?=\s*:)/y, "t-propiedad"], [CADENA_DOBLE, "t-cadena"], NUMERO,
    [/\b(?:true|false|null)\b/y, "t-clave"], MARCADOR,
  ],
  py: [
    [/#.*/y, "t-comentario"], [/[rRbBfFuU]{0,2}(?:"(?:[^"\\\n]|\\.)*"?|'(?:[^'\\\n]|\\.)*'?)/y, "t-cadena"],
    [/@[\w.]+/y, "t-variable"],
    [/\b(?:def|class|return|if|elif|else|for|while|import|from|as|with|try|except|finally|raise|in|is|not|and|or|None|True|False|lambda|yield|pass|break|continue|global|nonlocal|async|await|assert|del|match|case)\b/y, "t-clave"],
    [/\b(?:self|cls|print|len|range|str|int|dict|list|set|tuple|open|isinstance|super)\b/y, "t-variable"], NUMERO,
  ],
  yaml: [
    COMENTARIO_ALMOHADILLA, [/[\w.-]+(?=\s*:(?:\s|$))/y, "t-propiedad"], [CADENA_DOBLE, "t-cadena"], [CADENA_SIMPLE, "t-cadena"],
    [/\b(?:true|false|null|yes|no|on|off)\b/y, "t-clave"], [/^\s*-(?=\s)/y, "t-lista"], NUMERO, MARCADOR,
  ],
  sh: [
    COMENTARIO_ALMOHADILLA, [CADENA_DOBLE, "t-cadena"], [CADENA_SIMPLE, "t-cadena"], [/\$\{[^}\n]*\}?|\$[\w@*#?$!-]/y, "t-variable"],
    [/\b(?:if|then|else|elif|fi|for|in|do|done|case|esac|while|until|function|return|export|local|readonly|set|unset|exit|echo|cd|source|shift|trap)\b/y, "t-clave"],
    NUMERO,
  ],
  md: [
    [/`[^`\n]+`/y, "t-codigo"], [/\*\*[^*\n]+\*\*|__[^_\n]+__/y, "t-negrita"], [/\[[^\]\n]*\]\([^)\n]*\)/y, "t-enlace"],
    MARCADOR, [/(?<![\w*])\*[^*\s][^*\n]*\*(?!\w)/y, "t-cursiva"],
  ],
};

/** Lenguaje por la extensión del archivo (texto plano si no se conoce). */
export function lenguajeDe(ruta) {
  const ext = String(ruta || "").toLowerCase().split(".").pop();
  return { md: "md", markdown: "md", json: "json", py: "py", yml: "yaml", yaml: "yaml", sh: "sh", bash: "sh" }[ext] || "texto";
}

export const NOMBRE_LENGUAJE = { md: "Markdown", json: "JSON", py: "Python", yaml: "YAML", sh: "Shell", texto: "Texto" };

function trozos(linea, reglas) {
  const salida = [];
  let i = 0;
  let plano = "";
  while (i < linea.length) {
    let hecho = false;
    for (const [re, clase, condicion] of reglas) {
      if (condicion && !condicion(linea, i)) continue;
      re.lastIndex = i;
      const m = re.exec(linea);
      if (m && m[0].length) {
        if (plano) { salida.push(["", plano]); plano = ""; }
        salida.push([clase, m[0]]);
        i += m[0].length;
        hecho = true;
        break;
      }
    }
    if (!hecho) {
      // Avanza hasta el siguiente carácter que pueda empezar algo (rápido en líneas largas sin tokens).
      plano += linea[i];
      i += 1;
    }
  }
  if (plano) salida.push(["", plano]);
  return salida;
}

/** Tokens por línea: [[clase, texto], …] por cada línea. Con estado entre líneas (bloques ``` y cadenas """). */
export function tokenizar(texto, lenguaje) {
  const lineas = String(texto ?? "").split("\n");
  const reglas = REGLAS[lenguaje];
  if (!reglas) return lineas.map((l) => (l ? [["", l]] : []));
  let enBloque = false;
  let triple = "";
  return lineas.map((l) => {
    if (lenguaje === "md") {
      if (/^\s*(```|~~~)/.test(l)) { enBloque = !enBloque; return [["t-codigo", l]]; }
      if (enBloque) return [["t-codigo", l]];
      const titulo = /^#{1,6}\s/.exec(l);
      if (titulo) return [["t-titulo", l]];
      if (/^\s*>/.test(l)) return [["t-cita", l]];
      if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(l)) return [["t-comentario", l]];
      const lista = /^\s*(?:[-*+]|\d+[.)])\s/.exec(l);
      if (lista) return [["t-lista", lista[0]], ...trozos(l.slice(lista[0].length), reglas)];
      if (/^\s*\|/.test(l)) return trozos(l, reglas).flatMap(([c, t]) => (c ? [[c, t]] : t.split(/(\|)/).filter(Boolean).map((x) => [x === "|" ? "t-comentario" : "", x])));
      return trozos(l, reglas);
    }
    if (lenguaje === "py") {
      if (triple) {
        const fin = l.indexOf(triple);
        if (fin < 0) return [["t-cadena", l]];
        triple = "";
        return [["t-cadena", l.slice(0, fin + 3)], ...trozos(l.slice(fin + 3), reglas)];
      }
      const m = /("""|''')/.exec(l);
      if (m && !l.slice(0, m.index).includes("#")) {
        const resto = l.slice(m.index + 3);
        if (!resto.includes(m[1])) {
          triple = m[1];
          return [...trozos(l.slice(0, m.index), reglas), ["t-cadena", l.slice(m.index)]];
        }
      }
    }
    return trozos(l, reglas);
  });
}

/** Nodos con el resaltado (spans), listos para la capa bajo el textarea. */
export function resaltar(texto, lenguaje) {
  const frag = document.createDocumentFragment();
  tokenizar(texto, lenguaje).forEach((linea, n) => {
    if (n) frag.append("\n");
    for (const [clase, t] of linea) frag.append(clase ? h("span", { class: clase, texto: t }) : t);
  });
  frag.append("\n");   // el último salto evita que la capa se quede una línea corta al final
  return frag;
}

// Vista previa de Markdown ---------------------------------------------------------------------------------------

function enLinea(texto) {
  const salida = [];
  const re = /(`[^`]+`)|(\*\*[^*]+\*\*|__[^_]+__)|(\*[^*\s][^*]*\*|_[^_\s][^_]*_)|(\[[^\]]*\]\([^)\s]*\))|(\{\{[^{}]*\}\})/g;
  let ultimo = 0;
  for (let m = re.exec(texto); m; m = re.exec(texto)) {
    if (m.index > ultimo) salida.push(texto.slice(ultimo, m.index));
    const t = m[0];
    if (m[1]) salida.push(h("code", { texto: t.slice(1, -1) }));
    else if (m[2]) salida.push(h("strong", {}, enLinea(t.slice(2, -2))));
    else if (m[3]) salida.push(h("em", {}, enLinea(t.slice(1, -1))));
    else if (m[4]) {
      const [, etiqueta, url] = /^\[([^\]]*)\]\(([^)\s]*)\)$/.exec(t);
      salida.push(/^https?:\/\//i.test(url)
        ? h("a", { href: url, target: "_blank", rel: "noopener noreferrer" }, enLinea(etiqueta))
        : h("span", { class: "enlace-local", title: url }, enLinea(etiqueta)));
    } else salida.push(h("mark", { class: "marcador", texto: t }));
    ultimo = m.index + t.length;
  }
  if (ultimo < texto.length) salida.push(texto.slice(ultimo));
  return salida;
}

/** Markdown → nodos DOM (subconjunto: títulos, párrafos, listas, citas, código, tablas, separadores). */
export function markdownANodos(texto) {
  // Los comentarios HTML (como los marcadores de entrada de uxyngraphar) no se ven en la vista previa.
  const lineas = String(texto ?? "").replace(/\r/g, "").replace(/<!--[\s\S]*?-->/g, "").split("\n");
  const raiz = h("div", { class: "vista-md" });
  let i = 0;
  while (i < lineas.length) {
    const l = lineas[i];
    if (!l.trim()) { i++; continue; }
    const valla = /^\s*(```|~~~)(.*)$/.exec(l);
    if (valla) {
      const cuerpo = [];
      for (i++; i < lineas.length && !lineas[i].trim().startsWith(valla[1]); i++) cuerpo.push(lineas[i]);
      i++;
      raiz.append(h("pre", {}, h("code", { texto: cuerpo.join("\n") })));
      continue;
    }
    const titulo = /^(#{1,6})\s+(.*)$/.exec(l);
    if (titulo) { raiz.append(h(`h${titulo[1].length}`, {}, enLinea(titulo[2]))); i++; continue; }
    if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(l)) { raiz.append(h("hr", {})); i++; continue; }
    if (/^\s*>/.test(l)) {
      const cita = [];
      for (; i < lineas.length && /^\s*>/.test(lineas[i]); i++) cita.push(lineas[i].replace(/^\s*>\s?/, ""));
      raiz.append(h("blockquote", {}, markdownANodos(cita.join("\n")).childNodes.length ? [...markdownANodos(cita.join("\n")).childNodes] : null));
      continue;
    }
    if (/^\s*\|/.test(l)) {
      const filas = [];
      for (; i < lineas.length && /^\s*\|/.test(lineas[i]); i++) filas.push(lineas[i]);
      const celdas = (f) => f.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      const separador = filas.length > 1 && /^[\s|:-]+$/.test(filas[1]);
      const cabeza = separador ? celdas(filas[0]) : null;
      const cuerpo = (separador ? filas.slice(2) : filas).map(celdas);
      raiz.append(h("table", {},
        cabeza ? h("thead", {}, h("tr", {}, cabeza.map((c) => h("th", {}, enLinea(c))))) : null,
        h("tbody", {}, cuerpo.map((f) => h("tr", {}, f.map((c) => h("td", {}, enLinea(c))))))));
      continue;
    }
    const item = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/.exec(l);
    if (item) {
      const ordenada = /\d/.test(item[2]);
      const lista = h(ordenada ? "ol" : "ul", {});
      for (; i < lineas.length; i++) {
        const m = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/.exec(lineas[i]);
        if (!m) {
          if (lineas[i].trim() && /^\s{2,}/.test(lineas[i]) && lista.lastChild) { lista.lastChild.append(" ", ...enLinea(lineas[i].trim())); continue; }
          break;
        }
        const tarea = /^\[([ xX])\]\s+(.*)$/.exec(m[3]);
        lista.append(h("li", { class: m[1].length >= 2 ? "anidado" : null },
          tarea ? h("input", { type: "checkbox", checked: tarea[1] !== " ", disabled: true }) : null,
          tarea ? " " : null, enLinea(tarea ? tarea[2] : m[3])));
      }
      raiz.append(lista);
      continue;
    }
    const parrafo = [];
    for (; i < lineas.length && lineas[i].trim() && !/^(#{1,6}\s|\s*(```|~~~)|\s*>|\s*\||\s*([-*+]|\d+[.)])\s)/.test(lineas[i]); i++) parrafo.push(lineas[i].trim());
    if (!parrafo.length) { parrafo.push(l.trim()); i++; }
    raiz.append(h("p", {}, enLinea(parrafo.join(" "))));
  }
  return raiz;
}

// Editor ------------------------------------------------------------------------------------------------------------

/**
 * Crea el editor. Devuelve { nodo, area, fijar(texto, lenguaje), valor(), irALinea(n), marcar(lineas), buscar(),
 * enfocar(), estado() }. `alCambiar` se llama en cada cambio; `alGuardar` con Ctrl+S; `alCursor` al moverse.
 */
export function crearEditor({ alCambiar = () => {}, alGuardar = () => {}, alCursor = () => {}, etiqueta = "Contenido del archivo" } = {}) {
  const area = h("textarea", { class: "ec-texto", spellcheck: "false", autocapitalize: "off", autocomplete: "off", "aria-label": etiqueta, wrap: "off" });
  const capa = h("pre", { class: "ec-capa", "aria-hidden": "true" });
  const numeros = h("div", { class: "ec-numeros", "aria-hidden": "true" });
  const zonaTexto = h("div", { class: "ec-zona" }, capa, area);
  let lenguaje = "texto";
  let marcas = new Map();
  let pendiente = 0;
  let lineasPintadas = -1;
  let escapado = false;

  function pintarNumeros() {
    const n = area.value.split("\n").length;
    if (n === lineasPintadas && !marcas.size && !numeros.querySelector(".error")) return;
    lineasPintadas = n;
    const frag = document.createDocumentFragment();
    for (let i = 1; i <= n; i++) {
      const msg = marcas.get(i);
      frag.append(h("div", msg ? { class: "error", title: msg } : {}, String(i)));
    }
    numeros.replaceChildren(frag);
  }
  function pintar() {
    pendiente = 0;
    capa.replaceChildren(resaltar(area.value, lenguaje));
    pintarNumeros();
    sincronizar();
  }
  const programar = () => { if (!pendiente) pendiente = requestAnimationFrame(pintar); };
  function sincronizar() {
    capa.scrollTop = area.scrollTop;
    capa.scrollLeft = area.scrollLeft;
    numeros.scrollTop = area.scrollTop;
  }
  function posicion() {
    const antes = area.value.slice(0, area.selectionStart);
    const linea = antes.split("\n").length;
    return { linea, columna: area.selectionStart - antes.lastIndexOf("\n"), lineas: area.value.split("\n").length };
  }
  area.addEventListener("input", () => { programar(); alCambiar(area.value); alCursor(posicion()); });
  area.addEventListener("scroll", sincronizar);
  for (const ev of ["keyup", "click", "select"]) area.addEventListener(ev, () => alCursor(posicion()));
  area.addEventListener("keydown", (e) => {
    const mod = e.ctrlKey || e.metaKey;
    if (mod && e.key.toLowerCase() === "s") { e.preventDefault(); alGuardar(); return; }
    if (mod && (e.key.toLowerCase() === "f" || e.key.toLowerCase() === "h")) { e.preventDefault(); abrirBuscar(e.key.toLowerCase() === "h"); return; }
    if (e.key === "Escape") { escapado = true; cerrarBuscar(); return; }
    if (e.key === "Tab" && !escapado && !e.altKey && !mod) {
      // Tab sangra (dos espacios); Esc y luego Tab sale del editor (accesible con teclado).
      e.preventDefault();
      const { selectionStart: a, selectionEnd: b, value: v } = area;
      const inicio = v.lastIndexOf("\n", a - 1) + 1;
      if (a !== b && v.slice(a, b).includes("\n") || e.shiftKey) {
        const fin = b;
        const bloque = v.slice(inicio, fin);
        const nuevo = e.shiftKey ? bloque.replace(/^ {1,2}/gm, "") : bloque.replace(/^/gm, "  ");
        area.setRangeText(nuevo, inicio, fin, "select");
      } else {
        area.setRangeText("  ", a, b, "end");
      }
      area.dispatchEvent(new Event("input"));
      return;
    }
    escapado = false;
    if (e.key === "Enter" && !mod && !e.shiftKey && !e.altKey) {
      // Mantiene la sangría (y la viñeta de las listas de Markdown).
      const { selectionStart: a, value: v } = area;
      const linea = v.slice(v.lastIndexOf("\n", a - 1) + 1, a);
      const sangria = /^\s*/.exec(linea)[0];
      const vineta = lenguaje === "md" ? /^\s*([-*+]\s(?:\[[ xX]\]\s)?)/.exec(linea) : null;
      if (vineta && linea.trim() === vineta[1].trim()) return;   // viñeta vacía: Enter normal (termina la lista)
      if (sangria || vineta) {
        e.preventDefault();
        area.setRangeText(`\n${sangria}${vineta ? vineta[1].replace(/\[[xX]\]/, "[ ]").trimStart() : ""}`, a, area.selectionEnd, "end");
        area.dispatchEvent(new Event("input"));
      }
    }
  });

  // Buscar y reemplazar ------------------------------------------------------------------------------------------
  const qBuscar = h("input", { type: "search", placeholder: "Buscar", "aria-label": "Buscar en el archivo" });
  const qReemplazar = h("input", { type: "text", placeholder: "Reemplazar por", "aria-label": "Reemplazar por" });
  const mayus = h("input", { type: "checkbox", "aria-label": "Distinguir mayúsculas" });
  const contador = h("span", { class: "tenue ec-contador", "aria-live": "polite" });
  const filaReemplazar = h("div", { class: "fila ec-fila-reemplazar", hidden: true });
  const mini = (texto, accion, titulo) => {
    const b = h("button", { type: "button", class: "boton pequeno fantasma", title: titulo || texto, texto });
    b.addEventListener("click", accion);
    return b;
  };
  const barra = h("div", { class: "ec-buscar", hidden: true, role: "search" },
    h("div", { class: "fila" }, qBuscar, h("label", { class: "fila tenue", title: "Distinguir mayúsculas" }, mayus, "Aa"), contador,
      mini("↑", () => saltar(-1), "Anterior (Mayús+Enter)"), mini("↓", () => saltar(1), "Siguiente (Enter)"),
      mini("Reemplazar…", () => { filaReemplazar.hidden = !filaReemplazar.hidden; if (!filaReemplazar.hidden) qReemplazar.focus(); }),
      mini("×", () => { cerrarBuscar(); area.focus(); }, "Cerrar (Esc)")),
    filaReemplazar);
  filaReemplazar.append(qReemplazar, mini("Reemplazar", () => reemplazar(false)), mini("Reemplazar todo", () => reemplazar(true)));
  const normal = (t) => (mayus.checked ? t : t.toLowerCase());
  function coincidencias() {
    const q = qBuscar.value;
    if (!q) return [];
    const texto = normal(area.value);
    const aguja = normal(q);
    const salida = [];
    for (let i = texto.indexOf(aguja); i >= 0; i = texto.indexOf(aguja, i + Math.max(1, aguja.length))) salida.push(i);
    return salida;
  }
  function contar(actual = -1) {
    const n = coincidencias().length;
    contador.textContent = qBuscar.value ? (n ? `${actual >= 0 ? `${actual + 1} de ` : ""}${n}` : "sin resultados") : "";
  }
  function seleccionar(inicio, fin) {
    area.focus({ preventScroll: true });
    area.setSelectionRange(inicio, fin);
    const linea = area.value.slice(0, inicio).split("\n").length;
    const alto = parseFloat(getComputedStyle(area).lineHeight) || 20;
    area.scrollTop = Math.max(0, (linea - 1) * alto - area.clientHeight / 2);
    sincronizar();
  }
  function saltar(dir) {
    const lista = coincidencias();
    if (!lista.length) return contar();
    const desde = dir > 0 ? area.selectionEnd : area.selectionStart - 1;
    let k = dir > 0 ? lista.findIndex((i) => i >= desde) : lista.findLastIndex((i) => i <= desde - 0);
    if (k < 0) k = dir > 0 ? 0 : lista.length - 1;
    seleccionar(lista[k], lista[k] + qBuscar.value.length);
    contar(k);
    qBuscar.focus();
  }
  function reemplazar(todo) {
    const q = qBuscar.value;
    if (!q) return;
    if (todo) {
      const lista = coincidencias();
      if (!lista.length) return contar();
      for (const i of [...lista].reverse()) area.setRangeText(qReemplazar.value, i, i + q.length, "preserve");
      area.dispatchEvent(new Event("input"));
      contador.textContent = `${lista.length} reemplazado(s)`;
      return;
    }
    const sel = area.value.slice(area.selectionStart, area.selectionEnd);
    if (normal(sel) === normal(q)) {
      area.setRangeText(qReemplazar.value, area.selectionStart, area.selectionEnd, "end");
      area.dispatchEvent(new Event("input"));
    }
    saltar(1);
  }
  qBuscar.addEventListener("input", () => contar());
  mayus.addEventListener("change", () => contar());
  qBuscar.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); saltar(e.shiftKey ? -1 : 1); }
    if (e.key === "Escape") { e.preventDefault(); cerrarBuscar(); area.focus(); }
  });
  qReemplazar.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); reemplazar(false); }
    if (e.key === "Escape") { e.preventDefault(); cerrarBuscar(); area.focus(); }
  });
  function abrirBuscar(conReemplazo = false) {
    barra.hidden = false;
    filaReemplazar.hidden = !conReemplazo && filaReemplazar.hidden;
    const sel = area.value.slice(area.selectionStart, area.selectionEnd);
    if (sel && !sel.includes("\n")) qBuscar.value = sel;
    qBuscar.focus();
    qBuscar.select();
    contar();
  }
  function cerrarBuscar() { barra.hidden = true; }

  const nodo = h("div", { class: "ec" }, barra, h("div", { class: "ec-cuerpo" }, numeros, zonaTexto));
  return {
    nodo,
    area,
    fijar(texto, lang = lenguaje) {
      lenguaje = lang;
      nodo.dataset.lenguaje = lang;
      area.value = texto ?? "";
      area.scrollTop = 0;
      area.scrollLeft = 0;
      lineasPintadas = -1;
      pintar();
    },
    repintar: pintar,
    valor: () => area.value,
    lenguaje: () => lenguaje,
    irALinea(n, columna = 1) {
      const lineas = area.value.split("\n");
      const k = Math.min(Math.max(1, n), lineas.length);
      const inicio = lineas.slice(0, k - 1).reduce((s, l) => s + l.length + 1, 0) + Math.max(0, columna - 1);
      seleccionar(inicio, inicio + Math.max(0, (lineas[k - 1] || "").length - Math.max(0, columna - 1)));
    },
    marcar(mapa) { marcas = new Map(Object.entries(mapa || {}).map(([k, v]) => [Number(k), v])); lineasPintadas = -1; pintarNumeros(); },
    buscar: abrirBuscar,
    enfocar: () => area.focus(),
    estado: () => ({ seleccion: [area.selectionStart, area.selectionEnd], scroll: [area.scrollTop, area.scrollLeft] }),
    restaurar(e) {
      if (!e) return;
      area.setSelectionRange(...e.seleccion);
      [area.scrollTop, area.scrollLeft] = e.scroll;
      sincronizar();
    },
    posicion,
  };
}

/** Vista de diferencias en dos columnas de números (antes | después), de solo lectura. */
export function vistaDiferenciasCodigo(lineas) {
  let a = 0;
  let b = 0;
  return h("div", { class: "ec-diff", role: "table", "aria-label": "Diferencias" },
    lineas.map((l) => {
      if (l.tipo !== "nueva") a++;
      if (l.tipo !== "quitada") b++;
      return h("div", { class: `ec-diff-fila dif-${l.tipo}`, role: "row" },
        h("span", { class: "ec-diff-n", texto: l.tipo === "nueva" ? "" : String(a) }),
        h("span", { class: "ec-diff-n", texto: l.tipo === "quitada" ? "" : String(b) }),
        h("span", { class: "ec-diff-signo", texto: l.tipo === "nueva" ? "+" : l.tipo === "quitada" ? "−" : " " }),
        h("span", { class: "ec-diff-texto", texto: l.texto || " " }));
    }));
}

/** Divisor arrastrable: cambia la variable CSS `variable` de `contenedor` (en px) y la recuerda en localStorage. */
export function divisor(contenedor, variable, clave, { minimo = 140, maximo = 640, inicial = 240, invertir = false } = {}) {
  const asa = h("div", { class: "ec-divisor", role: "separator", tabindex: "0", "aria-orientation": "vertical", title: "Arrastra para cambiar el ancho" }, icono("asa"));
  let ancho = inicial;
  try { ancho = Number(localStorage.getItem(clave)) || inicial; } catch { /* */ }
  const aplicar = (px) => {
    ancho = Math.round(Math.min(maximo, Math.max(minimo, px)));
    contenedor.style.setProperty(variable, `${ancho}px`);
    asa.setAttribute("aria-valuenow", String(ancho));
    try { localStorage.setItem(clave, String(ancho)); } catch { /* */ }
  };
  aplicar(ancho);
  asa.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    asa.setPointerCapture(e.pointerId);
    const x0 = e.clientX;
    const a0 = ancho;
    const mover = (ev) => aplicar(a0 + (invertir ? x0 - ev.clientX : ev.clientX - x0));
    const soltar = () => { asa.removeEventListener("pointermove", mover); asa.removeEventListener("pointerup", soltar); };
    asa.addEventListener("pointermove", mover);
    asa.addEventListener("pointerup", soltar);
  });
  asa.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") { e.preventDefault(); aplicar(ancho + (invertir ? 20 : -20)); }
    if (e.key === "ArrowRight") { e.preventDefault(); aplicar(ancho + (invertir ? -20 : 20)); }
  });
  return asa;
}

