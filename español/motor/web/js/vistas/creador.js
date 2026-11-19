// Creador local (ADR 0013): chat de uxyn en «Creador de sistemas» y sincronización con borradores web.
// Nada se escribe sin que la persona lo acepte. Las sugerencias viven en «Por revisar», no perdidas en el chat.

import { obtener, enviar } from "../api.js";
import { h, vaciar, boton, avisar, insignia } from "../ui.js";
import { anotar } from "../registro.js";
import { cajaAgente, PREFIJO_CREAR } from "./creador-inicio.js";
import { ayudaSinIA, mensajeAgente, nuevoIdProgreso, trabajando } from "./agente-chat.js";

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

/** Lo que escribió la persona, sin la instrucción fija de «crear» (igual que la web). */
function textoMostrado(texto) {
  const limpio = String(texto || "").trim();
  return limpio.startsWith(PREFIJO_CREAR) ? limpio.slice(PREFIJO_CREAR.length).trim() || limpio : limpio;
}

async function selectorIA() {
  const sel = h("select", { "aria-label": "Qué IA usar" },
    h("option", { value: "agente|", texto: "uxyn (tu cuenta)" }),
    h("option", { value: "servidor|", texto: "Solo chat con mi clave o suscripción de la web (cuenta)" }));
  try {
    for (const m of await obtener("/api/creador/modelos")) {
      sel.append(h("option", m.suscripcion
        ? { value: `${m.proveedor}|`, "data-suscripcion": "1", texto: `${m.nombre} (tu suscripción, en este equipo${m.riesgo === "bajo" ? "" : " · lee el aviso en Conexiones"})` }
        : { value: `${m.proveedor}|${m.modelo}`, texto: `${m.modelo} (${m.proveedor === "ollama" ? "Ollama" : "LM Studio"}, en este equipo)` }));
    }
  } catch { /* sin modelos locales: solo la cuenta */ }
  try {
    const cuenta = await obtener("/api/cuenta");
    if (cuenta?.tipo !== "sesion" && sel.options.length > 2 && !sel.options[2].dataset.suscripcion) sel.selectedIndex = 2;
  } catch { /* sin datos de cuenta */ }
  const elegido = () => { const [proveedor, modelo] = sel.value.split("|"); return { proveedor, modelo }; };
  return { sel, elegido };
}

/** Propuestas aún abiertas (estado PENDING y al menos un archivo pendiente). */
export function filtrarPropuestasPendientes(todas) {
  return (todas || []).filter((x) => {
    const estado = String(x.estado || "").toUpperCase();
    if (estado && estado !== "PENDING" && estado !== "PENDIENTE") return false;
    return (x.archivos || []).some((a) => String(a.estado || "").toLowerCase() === "pendiente");
  });
}

const SITUACION = {
  ya_aplicado: ["ya aplicado", "bien", "El sistema ya tiene este contenido: basta con descartarlo."],
  desfasado: ["cambió después", "mal", "Este archivo cambió después de la sugerencia: si la aceptas, se pierden esos cambios."],
};

/** Archivos pendientes de una propuesta. */
const pendientesDe = (p) => (p.archivos || []).filter((a) => String(a.estado || "").toLowerCase() === "pendiente");

/** Banda que explica qué archivos chocan y deja elegir, en vez de un error sin salida. */
function avisoDesfasada(r, { aceptar, rechazar, alElegir }) {
  const rutas = r.rutas || [];
  const resto = aceptar.filter((x) => !rutas.includes(x));
  return h("div", { class: "pila banda aviso", role: "alert" },
    h("b", { texto: "Algunos archivos cambiaron después de esta sugerencia" }),
    h("p", { texto: `${rutas.join(", ")}: si la aceptas igualmente, esos cambios posteriores se sustituyen por los de la sugerencia.` }),
    h("div", { class: "fila" },
      boton("Aceptar igualmente (sobrescribe)", () => alElegir({ aceptar, rechazar, forzar: true }), { clase: "pequeno peligro" }),
      resto.length ? boton(`Aceptar solo ${resto.length === 1 ? "el que no choca" : `los ${resto.length} que no chocan`}`,
        () => alElegir({ aceptar: resto, rechazar: [...rechazar, ...rutas] }), { clase: "pequeno primario" }) : null,
      boton("Descartar los que chocan", () => alElegir({ aceptar: resto, rechazar: [...rechazar, ...rutas] }), { clase: "pequeno" }),
      boton("Cancelar", () => alElegir(null), { clase: "pequeno fantasma" })));
}

/** Una sugerencia pendiente: ver cambios, corregir, abrir en el editor, aceptar o rechazar (nunca deja atascado). */
function tarjetaPropuesta(slug, p, alDecidir, { alAbrirEnEditor } = {}) {
  const pendientes = pendientesDe(p);
  const casillas = pendientes.map((a) => h("input", {
    type: "checkbox", checked: a.situacion !== "ya_aplicado", value: a.ruta, "aria-label": `Aceptar ${a.ruta}`,
  }));
  const zona = h("div", { class: "pila" });
  async function enviarDecision({ aceptar, rechazar, forzar = false }) {
    const r = await enviar("/api/agente/decidir", { slug, propuesta: p.id, aceptar, rechazar, ...(forzar ? { forzar: true } : {}) });
    if (r.desfasada) {
      vaciar(zona, avisoDesfasada(r, {
        aceptar, rechazar,
        alElegir: (eleccion) => {
          if (!eleccion) return vaciar(zona);
          return enviarDecision(eleccion).catch((e) => avisar(e.message || String(e), "mal"));
        },
      }));
      return;
    }
    if (r.conflicto) {
      vaciar(zona, conflicto(r, (c) => sincronizarBorrador("bajar", slug, zona, alDecidir, c)));
      return;
    }
    avisar(aceptar.length ? `Cambios aceptados (${aceptar.length})${rechazar.length ? `, descartados ${rechazar.length}` : ""}` : "Sugerencia descartada");
    if (alDecidir) await alDecidir();
  }
  async function decidir(aceptarMarcados) {
    const marcados = casillas.filter((c) => c.checked).map((c) => c.value);
    const todas = pendientes.map((a) => a.ruta);
    const aceptar = aceptarMarcados ? marcados : [];
    const rechazar = aceptarMarcados ? todas.filter((r) => !marcados.includes(r)) : todas;
    await enviarDecision({ aceptar, rechazar });
  }
  function editarArchivo(a) {
    if (a.despues === null) return;
    const area = h("textarea", { class: "codigo", rows: 12, "aria-label": `Corregir ${a.ruta}` });
    area.value = a.despues || "";
    vaciar(zona,
      h("p", { class: "tenue", texto: `Corrige ${a.ruta} y guarda. Luego acepta la sugerencia.` }),
      area,
      h("div", { class: "fila" },
        boton("Guardar corrección", async () => {
          await enviar("/api/agente/corregir", { slug, propuesta: p.id, ruta: a.ruta, contenido: area.value });
          a.despues = area.value;
          avisar("Corrección guardada.");
          vaciar(zona);
        }, { clase: "pequeno primario" }),
        boton("Cancelar", () => vaciar(zona), { clase: "pequeno" })));
  }
  return h("article", { class: "propuesta pila", "aria-label": p.titulo || "Sugerencia" },
    h("div", { class: "fila separada" },
      h("b", { texto: p.titulo || "Sugerencia" }),
      insignia(pendientes.length ? "por revisar" : (p.estado || "").toLowerCase(), pendientes.length ? "nota" : "")),
    p.resumen ? h("p", { class: "tenue", texto: p.resumen }) : null,
    pendientes.map((a, i) => {
      const s = SITUACION[a.situacion];
      return h("details", { open: pendientes.length === 1 },
        h("summary", {}, casillas[i], ` ${a.ruta}${a.despues === null ? " (borrar)" : a.antes === null ? " (nuevo)" : ""} `,
          s ? insignia(s[0], s[1]) : null),
        s ? h("p", { class: "tenue", texto: s[2] }) : null,
        vistaDiferencias(a.antes || "", a.despues || ""),
        h("div", { class: "fila" },
          a.despues !== null ? boton("Corregir", () => editarArchivo(a), { clase: "pequeno" }) : null,
          alAbrirEnEditor ? boton("Abrir en el editor", () => alAbrirEnEditor(a, p), { clase: "pequeno", icono: "editar" }) : null));
    }),
    pendientes.length ? h("div", { class: "fila" },
      boton("Aceptar marcados", () => decidir(true), { clase: "pequeno primario", icono: "check" }),
      boton("Descartar sugerencia", () => decidir(false), { clase: "pequeno" })) : null,
    zona);
}

/** Decide todas las propuestas a la vez: «aceptar», «rechazar» o «obsoletas» (descarta solo lo ya aplicado). */
export async function decidirTodas(slug, propuestas, modo) {
  let aceptados = 0;
  let descartados = 0;
  const chocan = [];
  // De la más antigua a la más reciente: lo último que propuso uxyn es lo que queda.
  for (const p of [...propuestas].sort((x, y) => Number(x.id) - Number(y.id))) {
    const pend = pendientesDe(p);
    const yaAplicados = pend.filter((a) => a.situacion === "ya_aplicado").map((a) => a.ruta);
    let aceptar = [];
    let rechazar = [];
    if (modo === "rechazar") rechazar = pend.map((a) => a.ruta);
    else if (modo === "obsoletas") rechazar = yaAplicados;
    else { rechazar = yaAplicados; aceptar = pend.map((a) => a.ruta).filter((r) => !yaAplicados.includes(r)); }
    if (!aceptar.length && !rechazar.length) continue;
    let r = await enviar("/api/agente/decidir", { slug, propuesta: p.id, aceptar, rechazar });
    if (r.desfasada) {
      // Los que chocan quedan pendientes (la persona decide en su tarjeta); lo demás se aplica.
      chocan.push(...(r.rutas || []));
      aceptar = aceptar.filter((x) => !(r.rutas || []).includes(x));
      if (!aceptar.length && !rechazar.length) continue;
      r = await enviar("/api/agente/decidir", { slug, propuesta: p.id, aceptar, rechazar });
      if (r.desfasada) { chocan.push(...aceptar); continue; }
    }
    aceptados += aceptar.length;
    descartados += rechazar.length;
  }
  return { aceptados, descartados, chocan: [...new Set(chocan)] };
}

/**
 * Bloque fijo «Por revisar»: aquí viven las sugerencias de uxyn (no en el hilo del chat). No bloquea nada: se puede
 * seguir editando y hablando con uxyn, plegarlo, y decidir una a una o todas a la vez.
 * Devuelve { nodo, refrescar }.
 */
export function panelSugerencias(slug, { alCambiar, alAbrirEnEditor, soloWeb = false } = {}) {
  const nodo = h("section", { class: "sugerencias-panel", "aria-label": "Por revisar", hidden: true });
  let plegado = false;
  async function refrescar() {
    if (!slug) {
      nodo.hidden = true;
      vaciar(nodo);
      return [];
    }
    let todas = [];
    try {
      todas = await obtener("/api/agente/propuestas", { slug });
    } catch {
      nodo.hidden = true;
      return [];
    }
    const pendientes = filtrarPropuestasPendientes(todas);
    if (!pendientes.length) {
      nodo.hidden = true;
      vaciar(nodo);
      return [];
    }
    nodo.hidden = false;
    const archivos = pendientes.flatMap(pendientesDe);
    const obsoletas = archivos.filter((a) => a.situacion === "ya_aplicado").length;
    const tras = async () => { await refrescar(); if (alCambiar) await alCambiar(); };
    async function enBloque(modo) {
      const r = await decidirTodas(slug, pendientes, modo);
      avisar([r.aceptados ? `aceptados ${r.aceptados}` : "", r.descartados ? `descartados ${r.descartados}` : "",
        r.chocan.length ? `${r.chocan.length} cambiaron después y siguen por revisar (${r.chocan.join(", ")})` : ""]
        .filter(Boolean).join(" · ") || "Nada que cambiar", r.chocan.length ? "mal" : "");
      await tras();
    }
    const lista = h("div", { class: "pila", hidden: plegado },
      ...pendientes.map((p) => tarjetaPropuesta(slug, p, tras, { alAbrirEnEditor })));
    const plegar = h("button", { type: "button", class: "boton pequeno fantasma", "aria-expanded": String(!plegado), texto: plegado ? "Mostrar" : "Ocultar" });
    plegar.addEventListener("click", () => {
      plegado = !plegado;
      lista.hidden = plegado;
      plegar.textContent = plegado ? "Mostrar" : "Ocultar";
      plegar.setAttribute("aria-expanded", String(!plegado));
    });
    vaciar(nodo,
      h("div", { class: "sugerencias-cabecera" },
        h("h3", { texto: "Por revisar" }),
        insignia(String(pendientes.length), "nota"),
        h("span", { class: "espacio" }),
        plegar),
      h("p", { class: "tenue", texto: "uxyn dejó cambios. Puedes aceptarlos, corregirlos o descartarlos cuando quieras: mientras tanto sigues pudiendo editar tus archivos y hablar con uxyn." }),
      soloWeb ? h("p", { class: "tenue", texto: "Este sistema está solo en la web: lo que aceptes se aplica allí y se trae a este equipo." }) : null,
      h("div", { class: "fila" },
        boton("Aceptar todo", () => enBloque("aceptar"), { clase: "pequeno primario", icono: "check" }),
        boton("Descartar todo", () => enBloque("rechazar"), { clase: "pequeno" }),
        obsoletas ? boton(`Descartar lo ya aplicado (${obsoletas})`, () => enBloque("obsoletas"), { clase: "pequeno" }) : null),
      lista);
    return pendientes;
  }
  return { nodo, refrescar };
}

/**
 * Chat de uxyn (sistema abierto). Modos: uxyn | Simulador.
 * Las sugerencias van al panel «Por revisar» (`sugerencias`), no al hilo.
 */
export async function chatAgente(contexto, {
  conversacionInicial = null,
  slugInicial = null,
  sugerencias = null,
  alEmpezarTurno = null,
  alTerminarTurno = null,
  alProponer = null,
} = {}) {
  const { sel, elegido } = await selectorIA();
  // Historial del chat simple (sin agente): uno por modo, para no mezclar el simulador con el asistente.
  const historiales = { asistente: [], simulador: [] };
  let conversacion = conversacionInicial;
  let modo = "asistente";
  let adjuntos = null;
  const saludoAsistente = "Hola, soy uxyn. A la izquierda tienes archivos y origen; arriba el ciclo del sistema. Si dejo cambios, salen en «Por revisar».";
  const saludoSimulador = "Simulador: actúo como el agente de IA que sigue este sistema. Pídeme algo que debería rechazar.";
  const hilo = h("div", { class: "pila conversacion", role: "log", "aria-live": "polite" },
    h("div", { class: "mensaje ia", texto: saludoAsistente }));
  const propuestaLocal = h("div", { class: "pila" });
  const pregunta = h("textarea", { "aria-label": "Mensaje para uxyn", rows: 3, class: "breve", placeholder: "Escribe aquí (Ctrl+Enter para enviar)" });
  const conAgente = () => modo === "asistente" && elegido().proveedor === "agente";
  const enSimulador = () => modo === "simulador";
  const abierto = () => {
    const c = contexto();
    if (!c) throw new Error("Abre o crea un sistema para que uxyn pueda trabajar con él.");
    return c;
  };
  const slugDe = () => slugInicial || contexto()?.id || null;
  const refrescarSugerencias = async () => (sugerencias ? sugerencias.refrescar() : []);
  const decir = (quien, texto, ...extra) => {
    const quienIa = enSimulador() ? "Simulador" : (conAgente() ? "uxyn" : "IA");
    hilo.append(quien === "ia"
      ? mensajeAgente(texto, { extra, quien: quienIa })
      : h("div", { class: `mensaje ${quien}` }, h("div", { texto }), ...extra));
    hilo.scrollTop = hilo.scrollHeight;
  };
  function pintarSaludo() {
    const primero = hilo.querySelector(".mensaje.ia");
    if (primero && hilo.children.length === 1) primero.textContent = enSimulador() ? saludoSimulador : saludoAsistente;
  }

  async function turnoAgente(texto) {
    const c = contexto();
    const archivos = adjuntos.adjuntos();
    decir("tuyo", texto, archivos.length ? h("div", { class: "tenue", texto: `Adjuntó: ${archivos.map((a) => a.nombre).slice(0, 5).join(", ")}${archivos.length > 5 ? "…" : ""}` }) : null);
    adjuntos.vaciar();
    await pedirTurno({ mensaje: texto, id: c?.id || null, adjuntos: archivos });
  }

  async function pedirTurno(cuerpo) {
    const c = contexto();
    if (alEmpezarTurno) await alEmpezarTurno();
    anotar({
      nivel: "info", origen: "agente", titulo: "Turno uxyn",
      datos: { id: c?.id || cuerpo.id, conversacion, chars: String(cuerpo.mensaje || "").length },
    });
    const progreso = nuevoIdProgreso();
    const espera = trabajando();
    hilo.append(espera.nodo);
    hilo.scrollTop = hilo.scrollHeight;
    espera.seguir(progreso);
    let r;
    try {
      r = await enviar("/api/agente/turno", { ...cuerpo, conversacion, progreso });
    } catch (e) {
      espera.parar();
      anotar({ nivel: "error", origen: "agente", titulo: "Turno uxyn falló", detalle: e.message || String(e) });
      if (alTerminarTurno) await alTerminarTurno();
      const fallo = mensajeAgente(e.message || String(e), {
        error: true,
        extra: [ayudaSinIA(e.message), h("div", { class: "fila" }, boton("Reintentar", async () => { fallo.remove(); await pedirTurno(cuerpo); }, { clase: "pequeno", icono: "deshacer" }))],
      });
      hilo.append(fallo);
      hilo.scrollTop = hilo.scrollHeight;
      return;
    }
    espera.parar();
    if (r.conflicto) {
      anotar({ nivel: "aviso", origen: "creador", titulo: "Conflicto web ↔ equipo", datos: { slug: r.slug } });
      if (alTerminarTurno) await alTerminarTurno();
      decir("ia", "Tu sistema cambió en la web y en este equipo. Elige qué versión conservar y vuelve a enviar el mensaje.");
      vaciar(propuestaLocal, conflicto(r, (cual) => sincronizarBorrador("subir", r.slug, propuestaLocal, null, cual)));
      return;
    }
    conversacion = r.conversacion;
    anotar({
      nivel: "info", origen: "agente", titulo: "Turno uxyn terminó",
      datos: { conversacion, propuestas: r.propuestas, borrador: r.borrador, traido: r.traido, acciones: (r.acciones || []).length },
    });
    hilo.append(mensajeAgente(r.respuesta, { acciones: r.acciones }));
    hilo.scrollTop = hilo.scrollHeight;
    if (typeof refrescarLista === "function") void refrescarLista();
    if (r.propuestas?.length) {
      const pendientes = await refrescarSugerencias();
      if (pendientes?.length) {
        anotar({ nivel: "aviso", origen: "creador", titulo: `${pendientes.length} sugerencia(s) en Por revisar` });
        decir("ia", `Hay ${pendientes.length === 1 ? "1 sugerencia" : `${pendientes.length} sugerencias`} en «Por revisar» (arriba). Acéptala o corrígela ahí.`);
      }
      if (alProponer) await alProponer(pendientes);
    } else {
      await refrescarSugerencias();
    }
    if (alTerminarTurno) await alTerminarTurno();
  }

  /** Si el error es «no hay IA», lo explica en el hilo con opciones concretas (y no solo un aviso fugaz). */
  function explicarSiFaltaIA(e) {
    const ayuda = ayudaSinIA(e?.message);
    if (!ayuda) return false;
    hilo.append(mensajeAgente(e.message, { error: true, extra: [ayuda] }));
    hilo.scrollTop = hilo.scrollHeight;
    return true;
  }

  async function mejorar() {
    const c = abierto();
    if (conAgente()) {
      await turnoAgente(`Mejora el archivo ${c.rutaActual()}${pregunta.value.trim() ? `: ${pregunta.value.trim()}` : " (claridad, precisión y lo que falte)"}.`);
      pregunta.value = "";
      return;
    }
    let r;
    try {
      r = await enviar("/api/creador/mejorar", { id: c.id, rel: c.rutaActual(), contenido: c.textarea.value, instruccion: pregunta.value.trim(), ...elegido() });
    } catch (e) {
      if (explicarSiFaltaIA(e)) return;
      throw e;
    }
    pregunta.value = "";
    vaciar(propuestaLocal, h("div", { class: "fila separada" }, h("b", { texto: `Propuesta para ${r.rel}` }), insignia(r.modelo)),
      vistaDiferencias(c.textarea.value, r.propuesta),
      h("div", { class: "fila" },
        boton("Aceptar", () => { c.textarea.value = r.propuesta; c.textarea.dispatchEvent(new Event("input")); vaciar(propuestaLocal); avisar("En el editor: revisa y pulsa «Guardar archivo»"); }, { clase: "pequeno primario" }),
        boton("Descartar", () => vaciar(propuestaLocal), { clase: "pequeno" })));
  }
  async function revisar() {
    const c = abierto();
    if (conAgente()) return turnoAgente("Revisa el sistema completo y dime, en lenguaje sencillo, qué le falta o qué mejorarías.");
    try {
      const r = await enviar("/api/creador/revisar", { id: c.id, ...elegido() });
      decir("ia", r.texto);
    } catch (e) {
      if (!explicarSiFaltaIA(e)) throw e;
    }
  }
  async function hablar() {
    const texto = pregunta.value.trim();
    if (!texto) return;
    if (!contexto()) {
      avisar("Abre o crea un sistema para hablar con uxyn.", "mal");
      return;
    }
    if (conAgente() && !enSimulador()) {
      pregunta.value = "";
      return turnoAgente(texto);
    }
    const c = abierto();
    const mensajes = historiales[modo];
    mensajes.push({ role: "user", content: texto });
    decir("tuyo", texto);
    pregunta.value = "";
    try {
      // «uxyn (tu cuenta)» no es un proveedor de chat: el simulador (y el chat simple) usan la IA de la cuenta.
      const datos = elegido().proveedor === "agente" ? { proveedor: "servidor", modelo: "" } : elegido();
      const r = await enviar("/api/creador/chat", { id: c.id, mensajes, simulador: enSimulador(), ...datos });
      mensajes.push({ role: "assistant", content: r.texto });
      decir("ia", r.texto);
    } catch (e) {
      mensajes.pop();
      pregunta.value = pregunta.value || texto;
      if (!explicarSiFaltaIA(e)) throw e;
    }
  }
  if (conversacionInicial) {
    try {
      const previa = await obtener("/api/agente/conversacion", { id: conversacionInicial });
      vaciar(hilo);
      for (const m of previa.mensajes || []) {
        if (m.rol === "user") decir("tuyo", textoMostrado(m.texto));
        else hilo.append(mensajeAgente(m.texto, { acciones: m.acciones, fecha: m.fecha }));
      }
      hilo.scrollTop = hilo.scrollHeight;
    } catch { /* sin la conversación anterior: se empieza una nueva */ }
  }
  await refrescarSugerencias();

  const btnAsistente = h("button", { type: "button", class: "boton pequeno conmutador", "aria-pressed": "true" }, "uxyn");
  const btnSimulador = h("button", { type: "button", class: "boton pequeno conmutador", "aria-pressed": "false" }, "Simulador");
  const atajos = h("div", { class: "fila atajos-chat" },
    boton("Revisar", revisar, { clase: "pequeno" }),
    boton("Mejorar archivo", mejorar, { clase: "pequeno", titulo: "Usa lo que escribas abajo como instrucción" }));
  const pistaModo = h("p", { class: "tenue pista-modo", texto: "Los cambios de uxyn salen en «Por revisar», arriba." });
  const enviarBoton = boton("Enviar", hablar, { clase: "pequeno primario" });
  const selConversacion = h("select", { "aria-label": "Conversación guardada", class: "breve" });
  const empezarDeNuevo = () => {
    conversacion = null;
    historiales[modo] = [];
    selConversacion.value = "";
    vaciar(hilo, h("div", { class: "mensaje ia", texto: enSimulador() ? saludoSimulador : saludoAsistente }));
  };
  const barraHistorial = h("div", { class: "fila atajos-chat" },
    selConversacion,
    boton("Nueva", empezarDeNuevo, { clase: "pequeno" }));

  async function cargarHistorial(id) {
    const previa = await obtener("/api/agente/conversacion", { id });
    conversacion = previa.id || id;
    vaciar(hilo);
    for (const m of previa.mensajes || []) {
      if (m.rol === "user") decir("tuyo", textoMostrado(m.texto));
      else hilo.append(mensajeAgente(m.texto, { acciones: m.acciones, fecha: m.fecha }));
    }
    hilo.scrollTop = hilo.scrollHeight;
    await refrescarSugerencias();
  }

  let reanudada = Boolean(conversacionInicial);
  async function refrescarLista() {
    const slug = slugDe();
    let lista = [];
    try {
      lista = await obtener("/api/agente/conversaciones", slug ? { slug } : {});
    } catch { /* sin listado */ }
    // Como en la web: sin conversación pedida, se reanuda la más reciente de este sistema.
    if (!reanudada && !conversacion && slug && lista.length && hilo.children.length <= 1) {
      reanudada = true;
      try { await cargarHistorial(lista[0].id); } catch { /* se empieza una nueva */ }
    }
    reanudada = true;
    vaciar(selConversacion, h("option", { value: "", texto: lista.length ? "Conversación nueva" : "Sin conversaciones" }));
    for (const c of lista) {
      selConversacion.append(h("option", {
        value: String(c.id),
        texto: `${c.titulo || ("#" + c.id)}${c.actualizada ? " · " + new Date(c.actualizada).toLocaleString("es", { dateStyle: "short", timeStyle: "short" }) : ""}`,
        selected: conversacion === c.id,
      }));
    }
    if (conversacion && ![...selConversacion.options].some((o) => o.value === String(conversacion))) {
      selConversacion.append(h("option", { value: String(conversacion), texto: `Conversación #${conversacion}`, selected: true }));
    }
  }

  selConversacion.addEventListener("change", async () => {
    const id = Number(selConversacion.value);
    if (!id) {
      empezarDeNuevo();
      return;
    }
    try {
      await cargarHistorial(id);
    } catch (e) {
      avisar(e.message || String(e), "mal");
    }
  });

  function aplicarModo(nuevo) {
    modo = nuevo;
    btnAsistente.setAttribute("aria-pressed", String(modo === "asistente"));
    btnSimulador.setAttribute("aria-pressed", String(modo === "simulador"));
    atajos.hidden = modo === "simulador";
    barraHistorial.hidden = modo === "simulador";
    pistaModo.textContent = modo === "simulador"
      ? "Prueba el sistema como lo seguiría un agente de IA."
      : "Los cambios de uxyn salen en «Por revisar», arriba.";
    pregunta.setAttribute("aria-label", modo === "simulador" ? "Mensaje para el simulador" : "Mensaje para uxyn");
    enviarBoton.textContent = "Enviar";
    pintarSaludo();
  }
  btnAsistente.addEventListener("click", () => aplicarModo("asistente"));
  btnSimulador.addEventListener("click", () => aplicarModo("simulador"));
  adjuntos = cajaAgente({ etiqueta: "Mensaje", textarea: pregunta });
  adjuntos.ponerAccion(enviarBoton);
  void refrescarLista();

  return h("div", { class: "chat-agente" },
    h("div", { class: "fila modos-chat", role: "group", "aria-label": "Modo del chat" }, btnAsistente, btnSimulador),
    pistaModo,
    barraHistorial,
    atajos,
    hilo,
    propuestaLocal,
    h("label", { class: "campo ia-selector" }, "Qué IA usar", sel),
    adjuntos.nodo);
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
  avisar(accion === "subir" ? `Borrador «${slug}» guardado en la web` : r.accion === "al_dia" ? `«${slug}» ya estaba al día` : `«${slug}» está en tu catálogo local`);
  if (alTerminar) await alTerminar(r);
}

/** Borradores de la cuenta (sincronizar web ↔ equipo). Usado desde Cuenta si hace falta. */
export async function tarjetaCreador({ alTraer } = {}) {
  const zona = h("div", { class: "pila" });
  const detalle = h("div", { class: "pila" });

  async function pintar() {
    const cuenta = await obtener("/api/cuenta");
    if (!cuenta || cuenta.tipo !== "sesion") {
      vaciar(zona, h("p", { class: "tenue", texto: "Inicia sesión en «Cuenta» para sincronizar borradores con la web." }));
      return;
    }
    let filas = [];
    try {
      filas = await obtener("/api/creador/borradores");
    } catch (e) {
      vaciar(zona, h("div", { class: "banda aviso", texto: `No se pudo consultar: ${e.message || e}` }));
      return;
    }
    vaciar(zona,
      h("p", { class: "tenue", texto: "Trae un borrador de la web a este equipo, o guarda aquí cambios en la web. En el Taller también puedes usar la barra de salida." }),
      filas.length ? h("ul", { class: "lista" }, filas.map((f) => h("li", { class: "fila separada" },
        h("span", {}, h("b", { texto: f.titulo || f.slug }), h("span", { class: "tenue", texto: ` ${f.slug}` })),
        h("span", { class: "fila" },
          f.en_equipo ? insignia(f.revision_equipo === f.revision ? "al día" : "aquí", "bien") : null,
          boton("Traer", () => sincronizarBorrador("bajar", f.slug, detalle, async (r) => { await pintar(); if (alTraer) await alTraer(r, f.slug); }), { clase: "pequeno" }),
          f.en_equipo ? boton("Subir", () => sincronizarBorrador("subir", f.slug, detalle, pintar), { clase: "pequeno" }) : null))))
        : h("p", { class: "tenue", texto: "No hay borradores en la web." }),
      detalle);
  }

  await pintar().catch((e) => vaciar(zona, h("div", { class: "banda aviso", texto: String(e.message || e) })));
  return h("div", { class: "pila" }, h("h3", { texto: "Borradores en la web" }), zona);
}
