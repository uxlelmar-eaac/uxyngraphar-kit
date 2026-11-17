// Creador local (ADR 0013): chat del agente en la pantalla «Creador de sistemas» (modelos de este equipo o la clave de tu cuenta) y
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
    h("option", { value: "agente|", texto: "Asistente del Creador (tu cuenta)" }),
    h("option", { value: "servidor|", texto: "Solo chat con mi clave de IA (cuenta)" }));
  try {
    for (const m of await obtener("/api/creador/modelos")) {
      sel.append(h("option", { value: `${m.proveedor}|${m.modelo}`, texto: `${m.modelo} (${m.proveedor === "ollama" ? "Ollama" : "LM Studio"}, en este equipo)` }));
    }
  } catch { /* sin modelos locales: solo la cuenta */ }
  try {
    const cuenta = await obtener("/api/cuenta");
    if (cuenta?.tipo !== "sesion" && sel.options.length > 2) sel.selectedIndex = 2;   // sin cuenta: un modelo de este equipo
  } catch { /* sin datos de cuenta */ }
  const elegido = () => { const [proveedor, modelo] = sel.value.split("|"); return { proveedor, modelo }; };
  return { sel, elegido };
}

/** Propuesta del agente: diferencias por archivo, casillas y aceptar o rechazar. Al aceptar se trae a este equipo. */
function tarjetaPropuesta(slug, p, alDecidir) {
  const pendientes = (p.archivos || []).filter((a) => a.estado === "pendiente");
  const casillas = pendientes.map((a) => h("input", { type: "checkbox", checked: true, value: a.ruta, "aria-label": `Aceptar ${a.ruta}` }));
  const zona = h("div", { class: "pila" });
  async function decidir(aceptarMarcados) {
    const marcados = casillas.filter((c) => c.checked).map((c) => c.value);
    const aceptar = aceptarMarcados ? marcados : [];
    const rechazar = aceptarMarcados ? pendientes.map((a) => a.ruta).filter((r) => !marcados.includes(r)) : pendientes.map((a) => a.ruta);
    const r = await enviar("/api/agente/decidir", { slug, propuesta: p.id, aceptar, rechazar });
    if (r.conflicto) {
      vaciar(zona, conflicto(r, (c) => sincronizarBorrador("bajar", slug, zona, alDecidir, c)));
      return;
    }
    avisar(aceptar.length ? `Cambios aceptados y traídos a este equipo (${aceptar.length})` : "Propuesta rechazada");
    vaciar(zona, h("p", { class: "tenue", texto: aceptar.length ? "Aceptada." : "Rechazada." }));
    if (alDecidir) await alDecidir();
  }
  return h("div", { class: "propuesta pila" },
    h("div", { class: "fila separada" }, h("b", { texto: p.titulo }), insignia(pendientes.length ? "por revisar" : (p.estado || "").toLowerCase(), pendientes.length ? "nota" : "")),
    p.resumen ? h("p", { class: "tenue", texto: p.resumen }) : null,
    pendientes.map((a, i) => h("details", {},
      h("summary", {}, casillas[i], ` ${a.ruta}${a.despues === null ? " (borrar)" : a.antes === null ? " (nuevo)" : ""}`),
      vistaDiferencias(a.antes || "", a.despues || ""))),
    pendientes.length ? h("div", { class: "fila" },
      boton("Aceptar lo marcado", () => decidir(true), { clase: "pequeno primario", icono: "check" }),
      boton("Rechazar todo", () => decidir(false), { clase: "pequeno" })) : null,
    zona);
}

/**
 * Chat del agente. `contexto()` devuelve el sistema abierto ({ id, rutaActual, textarea, recargar }) o null.
 * Con «Asistente del Creador» habla con el agente del servidor (herramientas y propuestas); con las otras opciones es
 * un chat simple con la clave de la cuenta o un modelo de este equipo. Nada se guarda sin que la persona lo acepte.
 */
export async function chatAgente(contexto) {
  const { sel, elegido } = await selectorIA();
  const mensajes = [];
  let conversacion = null;
  const hilo = h("div", { class: "pila conversacion", role: "log", "aria-live": "polite" },
    h("div", { class: "mensaje ia", texto: "Hola, soy el Asistente del Creador. Puedo revisar tu sistema, rellenar lo que falta o crear uno nuevo contigo. Todo lo que cambie te lo dejo como propuesta para que lo aceptes. ¿Por dónde empezamos?" }));
  const propuesta = h("div", { class: "pila" });
  const pregunta = h("textarea", { "aria-label": "Mensaje para el agente", rows: 3, class: "breve", placeholder: "Escribe aquí (Ctrl+Enter para enviar)" });
  const simulador = h("input", { type: "checkbox" });
  const conAgente = () => elegido().proveedor === "agente";
  const abierto = () => {
    const c = contexto();
    if (!c) throw new Error("Abre o crea un sistema para que el agente pueda trabajar con él.");
    return c;
  };
  const decir = (quien, texto, ...extra) => {
    hilo.append(h("div", { class: `mensaje ${quien}` }, h("div", { texto }), ...extra));
    hilo.scrollTop = hilo.scrollHeight;
  };

  async function turnoAgente(texto) {
    const c = contexto();
    decir("tuyo", texto);
    const r = await enviar("/api/agente/turno", { mensaje: texto, conversacion, id: c?.id || null });
    if (r.conflicto) {
      decir("ia", "Tu sistema cambió en la web y en este equipo. Elige qué versión conservar y vuelve a enviar el mensaje.");
      vaciar(propuesta, conflicto(r, (cual) => sincronizarBorrador("subir", r.slug, propuesta, null, cual)));
      return;
    }
    conversacion = r.conversacion;
    const hechas = (r.acciones || []).map((a) => h("li", { class: a.ok ? "" : "tenue", texto: `${a.ok ? "✓" : "✗"} ${a.resumen}` }));
    decir("ia", r.respuesta, hechas.length ? h("ul", { class: "acciones-agente" }, hechas) : null);
    const slug = r.borrador || c?.id;
    if (r.propuestas?.length && slug) {
      const todas = await obtener("/api/agente/propuestas", { slug });
      for (const p of todas.filter((x) => r.propuestas.includes(x.id))) {
        hilo.append(tarjetaPropuesta(slug, p, async () => { if (contexto()?.recargar) await contexto().recargar(); }));
      }
      hilo.scrollTop = hilo.scrollHeight;
    }
  }

  async function mejorar() {
    const c = abierto();
    if (conAgente()) {
      await turnoAgente(`Mejora el archivo ${c.rutaActual()}${pregunta.value.trim() ? `: ${pregunta.value.trim()}` : " (claridad, precisión y lo que falte)"}.`);
      pregunta.value = "";
      return;
    }
    const r = await enviar("/api/creador/mejorar", { id: c.id, rel: c.rutaActual(), contenido: c.textarea.value, instruccion: pregunta.value.trim(), ...elegido() });
    pregunta.value = "";
    vaciar(propuesta, h("div", { class: "fila separada" }, h("b", { texto: `Propuesta para ${r.rel}` }), insignia(r.modelo)),
      vistaDiferencias(c.textarea.value, r.propuesta),
      h("div", { class: "fila" },
        boton("Aceptar", () => { c.textarea.value = r.propuesta; vaciar(propuesta); avisar("Propuesta en el editor: revisa y pulsa «Guardar archivo»"); }, { clase: "pequeno primario" }),
        boton("Descartar", () => vaciar(propuesta), { clase: "pequeno" })));
  }
  async function revisar() {
    const c = abierto();
    if (conAgente()) return turnoAgente("Revisa el sistema completo y dime, en lenguaje sencillo, qué le falta o qué mejorarías.");
    const r = await enviar("/api/creador/revisar", { id: c.id, ...elegido() });
    decir("ia", r.texto);
  }
  async function hablar() {
    const texto = pregunta.value.trim();
    if (!texto) return;
    if (conAgente() && !simulador.checked) {
      pregunta.value = "";
      return turnoAgente(texto);
    }
    const c = abierto();
    mensajes.push({ role: "user", content: texto });
    decir("tuyo", texto);
    pregunta.value = "";
    try {
      const datos = conAgente() ? { proveedor: "servidor", modelo: "" } : elegido();
      const r = await enviar("/api/creador/chat", { id: c.id, mensajes, simulador: simulador.checked, ...datos });
      mensajes.push({ role: "assistant", content: r.texto });
      decir("ia", r.texto);
    } catch (e) {
      mensajes.pop();
      throw e;
    }
  }
  const enviarBoton = boton("Enviar", hablar, { clase: "pequeno primario" });
  pregunta.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); enviarBoton.click(); } });
  return h("div", { class: "chat-agente" },
    h("div", { class: "fila" }, h("label", { class: "campo espacio" }, "Con quién hablas", sel)),
    h("div", { class: "fila" },
      boton("Revisar el sistema", revisar, { clase: "pequeno" }),
      boton("Mejorar el archivo abierto", mejorar, { clase: "pequeno", titulo: "Usa lo que escribas abajo como instrucción" })),
    hilo,
    propuesta,
    h("label", { class: "casilla" }, simulador, "Simulador: habla con el agente que usará este sistema"),
    pregunta,
    h("div", { class: "fila" }, enviarBoton));
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

/** Tarjeta «Borradores en la web»: borradores de la cuenta y bajar/subir con control de conflictos. */
export async function tarjetaCreador({ alTraer } = {}) {
  const zona = h("div", { class: "tarjeta pila" });
  const detalle = h("div", { class: "pila" });

  async function pintar() {
    const cuenta = await obtener("/api/cuenta");
    const titulo = h("h3", { texto: "Borradores en la web" });
    if (!cuenta || cuenta.tipo !== "sesion") {
      vaciar(zona, titulo, h("p", { class: "tenue", texto: "Inicia sesión en «Herramienta y ajustes» para traer a este equipo los borradores que creas en la web (y subir los tuyos)." }));
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
      h("p", { class: "tenue", texto: "Traer copia el borrador a este equipo para editarlo aquí. Guardar en la web lleva tus cambios. Si cambió en los dos sitios te enseñamos las diferencias." }),
      filas.length ? h("ul", { class: "lista" }, filas.map((f) => h("li", { class: "fila separada" },
        h("span", {}, h("b", { texto: f.titulo || f.slug }), h("span", { class: "tenue", texto: ` ${f.slug} · revisión ${f.revision}` })),
        h("span", { class: "fila" },
          f.en_equipo ? insignia(f.revision_equipo === f.revision ? "al día" : "en este equipo", "bien") : null,
          boton("Traer", () => sincronizarBorrador("bajar", f.slug, detalle, async (r) => { await pintar(); if (alTraer) await alTraer(r, f.slug); }), { clase: "pequeno" }),
          f.en_equipo ? boton("Guardar en la web", () => sincronizarBorrador("subir", f.slug, detalle, pintar), { clase: "pequeno" }) : null))))
        : h("p", { class: "tenue", texto: "No tienes borradores en el Creador web todavía." }),
      detalle);
  }

  await pintar().catch((e) => vaciar(zona, h("h3", { texto: "Borradores en la web" }), h("div", { class: "banda aviso", texto: String(e.message || e) })));
  return zona;
}
