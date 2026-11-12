// Creador local (ADR 0013): IA en el editor del catálogo (modelos de este equipo o la clave de tu cuenta) y
// sincronización con los borradores del Creador web. Nada se escribe sin que la persona lo acepte.

import { obtener, enviar } from "../api.js";
import { h, vaciar, boton, avisar, insignia } from "../ui.js";

const MAX_LINEAS_LCS = 1500;

/** Diferencias por líneas (LCS): [{tipo: "igual"|"quitada"|"nueva", texto}]. */
export function diferenciasLineas(antes, despues) {
  const a = String(antes || "").split("\n");
  const b = String(despues || "").split("\n");
  if (a.length > MAX_LINEAS_LCS || b.length > MAX_LINEAS_LCS) {
    return [...a.map((texto) => ({ tipo: "quitada", texto })), ...b.map((texto) => ({ tipo: "nueva", texto }))];
  }
  const t = Array.from({ length: a.length + 1 }, () => new Uint16Array(b.length + 1));
  for (let i = a.length - 1; i >= 0; i--) {
    for (let j = b.length - 1; j >= 0; j--) {
      t[i][j] = a[i] === b[j] ? t[i + 1][j + 1] + 1 : Math.max(t[i + 1][j], t[i][j + 1]);
    }
  }
  const salida = [];
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) { salida.push({ tipo: "igual", texto: a[i] }); i++; j++; }
    else if (t[i + 1][j] >= t[i][j + 1]) salida.push({ tipo: "quitada", texto: a[i++] });
    else salida.push({ tipo: "nueva", texto: b[j++] });
  }
  while (i < a.length) salida.push({ tipo: "quitada", texto: a[i++] });
  while (j < b.length) salida.push({ tipo: "nueva", texto: b[j++] });
  return salida;
}

export function vistaDiferencias(antes, despues) {
  const lineas = diferenciasLineas(antes, despues);
  return h("pre", { class: "diferencias", "aria-label": "Diferencias" },
    lineas.map((l) => h("div", { class: `dif-${l.tipo}`, texto: `${l.tipo === "nueva" ? "+ " : l.tipo === "quitada" ? "− " : "  "}${l.texto}` })));
}

async function selectorIA() {
  const sel = h("select", { "aria-label": "Qué IA usar" },
    h("option", { value: "servidor|", texto: "Mi clave de IA (cuenta)" }));
  try {
    for (const m of await obtener("/api/creador/modelos")) {
      sel.append(h("option", { value: `${m.proveedor}|${m.modelo}`, texto: `${m.modelo} (${m.proveedor === "ollama" ? "Ollama" : "LM Studio"}, en este equipo)` }));
    }
  } catch { /* sin modelos locales: solo la cuenta */ }
  const elegido = () => { const [proveedor, modelo] = sel.value.split("|"); return { proveedor, modelo }; };
  return { sel, elegido };
}

/** Panel de IA del editor: mejorar el archivo abierto (con diferencias), revisar el sistema, chat y simulador. */
export async function asistenteIA(id, rutaActual, textarea) {
  const { sel, elegido } = await selectorIA();
  const instruccion = h("input", { type: "text", "aria-label": "Qué mejorar", placeholder: "Qué mejorar (opcional): más claro, añade ejemplos…" });
  const resultado = h("div", { class: "pila" });
  const mensajes = [];
  const conversacion = h("div", { class: "pila conversacion" });
  const pregunta = h("textarea", { "aria-label": "Mensaje", rows: 2, placeholder: "Pregunta sobre el sistema o, en el simulador, habla con el agente" });
  const simulador = h("input", { type: "checkbox", "aria-label": "Simulador" });

  async function mejorar() {
    const r = await enviar("/api/creador/mejorar", { id, rel: rutaActual(), contenido: textarea.value, instruccion: instruccion.value, ...elegido() });
    const aceptar = boton("Aceptar propuesta", () => {
      textarea.value = r.propuesta;
      vaciar(resultado);
      avisar("Propuesta en el editor: revisa y pulsa «Guardar archivo»");
    }, { clase: "pequeno primario" });
    vaciar(resultado, h("div", { class: "fila separada" }, h("b", { texto: `Propuesta para ${r.rel}` }), insignia(r.modelo)),
      vistaDiferencias(textarea.value, r.propuesta),
      h("div", { class: "fila" }, aceptar, boton("Descartar", () => vaciar(resultado), { clase: "pequeno" })));
  }
  async function revisar() {
    const r = await enviar("/api/creador/revisar", { id, ...elegido() });
    vaciar(resultado, h("b", { texto: "Revisión del sistema" }), h("pre", { class: "informe", texto: r.texto }),
      boton("Cerrar", () => vaciar(resultado), { clase: "pequeno" }));
  }
  async function hablar() {
    const texto = pregunta.value.trim();
    if (!texto) return;
    mensajes.push({ role: "user", content: texto });
    conversacion.append(h("div", { class: "mensaje tuyo", texto }));
    pregunta.value = "";
    try {
      const r = await enviar("/api/creador/chat", { id, mensajes, simulador: simulador.checked, ...elegido() });
      mensajes.push({ role: "assistant", content: r.texto });
      conversacion.append(h("div", { class: "mensaje ia", texto: r.texto }));
    } catch (e) {
      mensajes.pop();
      throw e;
    }
  }
  return h("details", { class: "tarjeta pila" },
    h("summary", { texto: "Asistente de IA" }),
    h("p", { class: "tenue", texto: "Usa la clave de IA de tu cuenta (Cuenta › Claves de IA en la web) o un modelo de este equipo (Ollama, LM Studio). Las propuestas no se guardan solas." }),
    h("div", { class: "fila" }, sel, instruccion),
    h("div", { class: "fila" }, boton("Mejorar este archivo", mejorar, { clase: "pequeno" }),
      boton("Revisar el sistema", revisar, { clase: "pequeno" })),
    resultado,
    conversacion,
    h("div", { class: "fila" }, h("label", { class: "casilla" }, simulador, "Simulador (habla con el agente que usa este sistema)")),
    h("div", { class: "fila" }, h("div", { class: "espacio" }, pregunta), boton("Enviar", hablar, { clase: "pequeno" })));
}

function conflicto(r, alElegir) {
  return h("div", { class: "pila" },
    h("div", { class: "banda aviso", texto: `«${r.slug}» cambió en la web (revisión ${r.revision_web}) y en este equipo. Elige qué versión conservar.` }),
    r.diferencias.map((d) => h("details", {}, h("summary", { texto: `${d.ruta} (${d.cambio})` }), h("pre", { class: "diferencias", texto: d.diff }))),
    h("div", { class: "fila" }, boton("Conservar la de la web", () => alElegir("web"), { clase: "pequeno" }),
      boton("Conservar la de este equipo", () => alElegir("local"), { clase: "pequeno" })));
}

/** Sube o baja un borrador; ante un conflicto pinta las diferencias en `zona` y deja elegir. */
export async function sincronizarBorrador(accion, slug, zona, alTerminar, conservar) {
  const r = await enviar(`/api/creador/${accion}`, { slug, ...(conservar ? { conservar } : {}) });
  if (r.conflicto) {
    vaciar(zona, conflicto(r, (c) => sincronizarBorrador(accion, slug, zona, alTerminar, c)));
    return;
  }
  vaciar(zona);
  avisar(accion === "subir" ? `«${slug}» subido al Creador web` : r.accion === "al_dia" ? `«${slug}» ya estaba al día` : `«${slug}» está en tu catálogo local`);
  if (alTerminar) await alTerminar(r);
}

/** Tarjeta «Creador web»: borradores de la cuenta y bajar/subir con control de conflictos. */
export async function tarjetaCreador() {
  const zona = h("div", { class: "tarjeta pila" });
  const detalle = h("div", { class: "pila" });

  async function pintar() {
    const cuenta = await obtener("/api/cuenta");
    const titulo = h("h2", { texto: "Creador web" });
    if (!cuenta || cuenta.tipo !== "sesion") {
      vaciar(zona, titulo, h("p", { class: "tenue", texto: "Inicia sesión arriba para traer a este equipo los borradores que creas en la web (y subir los tuyos)." }));
      return;
    }
    let filas = [];
    try {
      filas = await obtener("/api/creador/borradores");
    } catch (e) {
      vaciar(zona, titulo, h("div", { class: "banda aviso", texto: `No se pudo consultar: ${e.message || e}` }));
      return;
    }
    vaciar(zona, titulo,
      h("p", { class: "tenue", texto: "Bajar trae el borrador al catálogo local (Catálogo › modo avanzado para editarlo). Subir lleva tus cambios a la web. Si cambió en los dos sitios te enseñamos las diferencias." }),
      filas.length ? h("ul", { class: "lista" }, filas.map((f) => h("li", { class: "fila separada" },
        h("span", {}, h("b", { texto: f.titulo || f.slug }), h("span", { class: "tenue", texto: ` ${f.slug} · revisión ${f.revision}` })),
        h("span", { class: "fila" },
          f.en_equipo ? insignia(f.revision_equipo === f.revision ? "al día" : "en este equipo", "bien") : null,
          boton("Bajar", () => sincronizarBorrador("bajar", f.slug, detalle, pintar), { clase: "pequeno" }),
          f.en_equipo ? boton("Subir", () => sincronizarBorrador("subir", f.slug, detalle, pintar), { clase: "pequeno" }) : null))))
        : h("p", { class: "tenue", texto: "No tienes borradores en el Creador web todavía." }),
      detalle);
  }

  await pintar().catch((e) => vaciar(zona, h("h2", { texto: "Creador web" }), h("div", { class: "banda aviso", texto: String(e.message || e) })));
  return zona;
}
