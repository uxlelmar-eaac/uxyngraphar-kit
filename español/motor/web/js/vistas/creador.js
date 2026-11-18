// Creador local (ADR 0013): chat de uxyn en «Creador de sistemas» y sincronización con borradores web.
// Nada se escribe sin que la persona lo acepte. Las sugerencias viven en «Por revisar», no perdidas en el chat.

import { obtener, enviar } from "../api.js";
import { h, vaciar, boton, avisar, insignia } from "../ui.js";
import { anotar } from "../registro.js";
import { cajaAgente } from "./creador-inicio.js";
import { mensajeAgente, nuevoIdProgreso, trabajando } from "./agente-chat.js";

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

/** Una sugerencia pendiente: ver cambios, corregir, aceptar o rechazar. */
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
    avisar(aceptar.length ? `Cambios aceptados (${aceptar.length})` : "Sugerencia rechazada");
    if (alDecidir) await alDecidir();
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
    pendientes.map((a, i) => h("details", { open: pendientes.length === 1 },
      h("summary", {}, casillas[i], ` ${a.ruta}${a.despues === null ? " (borrar)" : a.antes === null ? " (nuevo)" : ""}`),
      vistaDiferencias(a.antes || "", a.despues || ""),
      a.despues !== null ? h("div", { class: "fila" }, boton("Corregir", () => editarArchivo(a), { clase: "pequeno" })) : null)),
    pendientes.length ? h("div", { class: "fila" },
      boton("Aceptar", () => decidir(true), { clase: "pequeno primario", icono: "check" }),
      boton("Rechazar", () => decidir(false), { clase: "pequeno" })) : null,
    zona);
}

/**
 * Bloque fijo «Por revisar»: aquí viven las sugerencias de uxyn (no en el hilo del chat).
 * Devuelve { nodo, refrescar }.
 */
export function panelSugerencias(slug, { alCambiar } = {}) {
  const nodo = h("section", { class: "sugerencias-panel", "aria-label": "Por revisar", hidden: true });
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
    const pendientes = (todas || []).filter((x) => (x.archivos || []).some((a) => a.estado === "pendiente"));
    if (!pendientes.length) {
      nodo.hidden = true;
      vaciar(nodo);
      return [];
    }
    nodo.hidden = false;
    vaciar(nodo,
      h("div", { class: "sugerencias-cabecera" },
        h("h3", { texto: "Por revisar" }),
        insignia(String(pendientes.length), "nota")),
      h("p", { class: "tenue", texto: "uxyn dejó cambios. Acéptalos, corrígelos o recházalos antes de seguir." }),
      ...pendientes.map((p) => tarjetaPropuesta(slug, p, async () => {
        await refrescar();
        if (alCambiar) await alCambiar();
      })));
    try { nodo.scrollIntoView({ behavior: "smooth", block: "nearest" }); } catch { /* sin scroll */ }
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
  const mensajes = [];
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
        extra: [h("div", { class: "fila" }, boton("Reintentar", async () => { fallo.remove(); await pedirTurno(cuerpo); }, { clase: "pequeno", icono: "deshacer" }))],
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

  async function mejorar() {
    const c = abierto();
    if (conAgente()) {
      await turnoAgente(`Mejora el archivo ${c.rutaActual()}${pregunta.value.trim() ? `: ${pregunta.value.trim()}` : " (claridad, precisión y lo que falte)"}.`);
      pregunta.value = "";
      return;
    }
    const r = await enviar("/api/creador/mejorar", { id: c.id, rel: c.rutaActual(), contenido: c.textarea.value, instruccion: pregunta.value.trim(), ...elegido() });
    pregunta.value = "";
    vaciar(propuestaLocal, h("div", { class: "fila separada" }, h("b", { texto: `Propuesta para ${r.rel}` }), insignia(r.modelo)),
      vistaDiferencias(c.textarea.value, r.propuesta),
      h("div", { class: "fila" },
        boton("Aceptar", () => { c.textarea.value = r.propuesta; vaciar(propuestaLocal); avisar("En el editor: revisa y pulsa «Guardar archivo»"); }, { clase: "pequeno primario" }),
        boton("Descartar", () => vaciar(propuestaLocal), { clase: "pequeno" })));
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
    if (!contexto()) {
      avisar("Abre o crea un sistema para hablar con uxyn.", "mal");
      return;
    }
    if (conAgente() && !enSimulador()) {
      pregunta.value = "";
      return turnoAgente(texto);
    }
    const c = abierto();
    mensajes.push({ role: "user", content: texto });
    decir("tuyo", texto);
    pregunta.value = "";
    try {
      const datos = (modo === "asistente" && elegido().proveedor === "agente")
        ? { proveedor: "servidor", modelo: "" }
        : elegido();
      const r = await enviar("/api/creador/chat", { id: c.id, mensajes, simulador: enSimulador(), ...datos });
      mensajes.push({ role: "assistant", content: r.texto });
      decir("ia", r.texto);
    } catch (e) {
      mensajes.pop();
      throw e;
    }
  }
  if (conversacionInicial) {
    try {
      const previa = await obtener("/api/agente/conversacion", { id: conversacionInicial });
      vaciar(hilo);
      for (const m of previa.mensajes || []) {
        if (m.rol === "user") decir("tuyo", m.texto);
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
  const barraHistorial = h("div", { class: "fila atajos-chat" },
    selConversacion,
    boton("Nueva", () => { conversacion = null; vaciar(hilo, h("div", { class: "mensaje ia", texto: saludoAsistente })); }, { clase: "pequeno" }));

  async function cargarHistorial(id) {
    const previa = await obtener("/api/agente/conversacion", { id });
    conversacion = previa.id || id;
    vaciar(hilo);
    for (const m of previa.mensajes || []) {
      if (m.rol === "user") decir("tuyo", m.texto);
      else hilo.append(mensajeAgente(m.texto, { acciones: m.acciones, fecha: m.fecha }));
    }
    hilo.scrollTop = hilo.scrollHeight;
    await refrescarSugerencias();
  }

  async function refrescarLista() {
    const slug = slugDe();
    let lista = [];
    try {
      lista = await obtener("/api/agente/conversaciones", slug ? { slug } : {});
    } catch { /* sin listado */ }
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
      conversacion = null;
      vaciar(hilo, h("div", { class: "mensaje ia", texto: saludoAsistente }));
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
