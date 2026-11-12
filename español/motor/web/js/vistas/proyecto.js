// Un proyecto: sus sistemas (instalar, actualizar, reparar, quitar) y las pestañas de memorias, flujo, salud y opciones.

import { obtener, enviar, catalogo, nombreDe } from "../api.js";
import { h, vaciar, boton, insignia, confirmar, avisar, dialogo, pestanas, vacio } from "../ui.js";
import { pestanaFlujo, pestanaSalud, pestanaOpciones } from "./proyecto-pestanas.js";
import { pestanaMemorias } from "./proyecto-memorias.js";

export async function vista(params, nav) {
  const ruta = params.ruta;
  if (!ruta) { nav.ir("proyectos"); return h("div"); }
  const estado = await obtener("/api/repo/estado", { repo: ruta });
  const ctx = { ruta, estado, ...nav };
  const cuerpo = h("div");
  const elegir = (id) => {
    const pintores = { sistemas: pestanaSistemas, memorias: pestanaMemorias, flujo: pestanaFlujo, salud: pestanaSalud, opciones: pestanaOpciones };
    vaciar(cuerpo, h("div", { class: "cargando" }, "Cargando…"));
    Promise.resolve(pintores[id](ctx)).then((n) => vaciar(cuerpo, n)).catch((e) => vaciar(cuerpo, h("div", { class: "banda mal", texto: e.message })));
  };
  const cabeza = h("div", { class: "cabecera" }, h("div", {},
    h("div", { class: "migas" }, h("a", { href: "#/proyectos", texto: "Mis proyectos" }), " / ", nombreDe(ruta)),
    h("h1", { texto: estado.nombre }), h("p", {}, h("code", { texto: estado.ruta }))));
  const noRegistrado = !estado.registrado ? h("div", { class: "banda acento", style: "margin-bottom:16px" }, "Este proyecto no está en tu lista.",
    h("span", { class: "espacio" }), boton("Añadirlo a mis proyectos", async () => { await enviar("/api/proyectos/agregar", { rutas: [estado.ruta] }); avisar("Añadido"); nav.recargar(); }, { clase: "primario pequeno" })) : null;
  const inicial = params.pestana || "sistemas";
  elegir(inicial);
  return h("div", {}, cabeza, noRegistrado,
    pestanas([["sistemas", "Sistemas"], ["memorias", estado.memorias_propuestas ? `Memorias (${estado.memorias_propuestas})` : "Memorias"], ["flujo", "Flujo del asistente"], ["salud", "Revisión"], ["opciones", "Más opciones"]], elegir, inicial), cuerpo);
}

async function pestanaSistemas(ctx) {
  const { ruta, estado, recargar } = ctx;
  const cat = await catalogo();
  const instalados = new Set(estado.sistemas.map((p) => p.id));
  const pendientes = estado.sistemas.filter((p) => p.actualizable || !p.integro);

  const actualizar = (ids) => async () => {
    const hechos = await enviar("/api/repo/actualizar", { repo: ruta, ids });
    avisar(hechos.length ? `Listo: ${hechos.length} sistema(s) actualizado(s)` : "Ya estaba todo al día");
    recargar();
  };
  const quitar = (p) => async () => {
    const r = await confirmar({ titulo: `Quitar «${p.titulo}»`, texto: "El sistema deja de aplicarse en este proyecto. Lo que ya se trabajó con él se conserva, salvo que marques la casilla.",
      si: "Quitar sistema", peligro: true, casilla: "Borrar también el trabajo guardado de este sistema" });
    if (!r) return;
    await enviar("/api/repo/quitar", { repo: ruta, id: p.id, con_trabajo: r.casilla, confirmar: estado.nombre });
    avisar(`Quitado: ${p.titulo}`);
    recargar();
  };

  // Reporte al autor (Fase 8): siempre con vista previa de lo que sale del equipo antes de enviarlo.
  const reportar = (p) => async () => {
    const nombre = p.titulo || p.id;
    const tipo = h("select", {}, h("option", { value: "problema", texto: "Algo no funciona" }),
      h("option", { value: "mejora", texto: "Falta algo o se puede mejorar" }), h("option", { value: "duda", texto: "No se entiende algo" }));
    const texto = h("textarea", { class: "corto", rows: "6", placeholder: "Qué hacías, qué esperabas y qué pasó. No pegues datos privados ni código." });
    const pedido = () => ({ ref: p.id, tipo: tipo.value, texto: texto.value, repo: ruta });
    const contenido = h("div", { class: "pila" },
      h("p", { class: "tenue", texto: `El autor de «${nombre}» lo verá en sus sugerencias y podrá mejorar el sistema. Antes de enviar verás exactamente qué sale de tu equipo.` }),
      h("label", { class: "campo" }, "Tipo", tipo), h("label", { class: "campo" }, "Qué quieres contar", texto));
    const previa = await dialogo({ titulo: `Reportar «${nombre}»`, contenido,
      acciones: [{ texto: "Ver qué se envía", clase: "primario", accion: () => enviar("/api/reportes/vista-previa", pedido()) }] });
    if (!previa) return;
    const r = await dialogo({ titulo: "Esto es lo que se envía", contenido: h("pre", { texto: previa.vista_previa }),
      acciones: [{ texto: "Enviar al autor", clase: "primario", accion: () => enviar("/api/reportes/enviar", pedido()) }] });
    if (r) avisar(r.repetido ? "Ya lo habías enviado hoy; no se duplicó." : "Enviado. El autor lo verá en sus sugerencias. Gracias.");
  };

  const tarjetaInstalado = (p) => h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("h3", { texto: p.titulo || p.id }),
      !p.integro ? insignia("alterado", "mal") : p.actualizable ? insignia(`Actualización disponible: ${p.catalogo}`, "aviso") : insignia("al día", "bien")),
    h("div", { class: "tenue", texto: p.descripcion }),
    h("div", { class: "tenue", texto: `Versión ${p.version}` }),
    h("div", { class: "acciones" },
      !p.integro ? boton("Reparar", actualizar([p.id]), { clase: "primario pequeno" }) : null,
      p.integro && p.actualizable ? boton("Actualizar", actualizar([p.id]), { clase: "primario pequeno" }) : null,
      boton("Reportar al autor", reportar(p), { clase: "pequeno", titulo: "Cuenta al autor qué falla o qué falta" }),
      boton("Quitar", quitar(p), { clase: "peligro pequeno" })));

  const elegidos = new Set();
  const filtro = h("input", { type: "search", placeholder: "Buscar sistemas…", "aria-label": "Buscar sistemas del catálogo" });
  const rejilla = h("div", { class: "rejilla" });
  const instalarBtn = boton("Instalar seleccionados", async () => {
    if (!elegidos.size) return avisar("Marca al menos un sistema", "mal");
    await enviar("/api/repo/instalar", { repo: ruta, ids: [...elegidos] });
    avisar(`Instalados ${elegidos.size} sistema(s)`);
    recargar();
  }, { clase: "primario" });
  const libres = cat.filter((m) => !instalados.has(m.id) && !(m.errores || []).length);
  const pintarLibres = () => {
    const t = filtro.value.trim().toLowerCase();
    rejilla.replaceChildren(...libres.filter((m) => !t || (m.titulo + " " + m.descripcion).toLowerCase().includes(t)).map((m) => {
      const tarjeta = h("div", { class: `tarjeta tarjeta-item elegible ${elegidos.has(m.id) ? "elegido" : ""}`, role: "checkbox", tabindex: "0", "aria-checked": String(elegidos.has(m.id)) },
        h("div", { class: "fila separada" }, h("h3", { texto: m.titulo }), insignia(m.familia || "")), h("div", { class: "tenue", texto: m.descripcion }));
      const alternar = () => { elegidos.has(m.id) ? elegidos.delete(m.id) : elegidos.add(m.id); instalarBtn.lastChild.textContent = elegidos.size ? ` Instalar ${elegidos.size} seleccionado(s)` : "Instalar seleccionados"; pintarLibres(); };
      tarjeta.addEventListener("click", alternar);
      tarjeta.addEventListener("keydown", (e) => { if (e.key === " " || e.key === "Enter") { e.preventDefault(); alternar(); } });
      return tarjeta;
    }));
  };
  filtro.addEventListener("input", pintarLibres);
  pintarLibres();

  return h("div", {},
    pendientes.length ? h("div", { class: "banda aviso", style: "margin-bottom:16px" }, `${pendientes.length} sistema(s) necesitan actualizarse o repararse.`,
      h("span", { class: "espacio" }), boton("Actualizar todo", actualizar([]), { clase: "primario pequeno" })) : null,
    h("div", { class: "fila separada" }, h("h2", { texto: "Instalados" }), boton("Aplicar un flujo guardado", () => aplicarGuardado(ctx), { icono: "flujos" })),
    estado.sistemas.length ? h("div", { class: "rejilla" }, estado.sistemas.map(tarjetaInstalado))
      : vacio("Este proyecto aún no tiene sistemas", "Elige abajo los que quieras o aplica un flujo guardado para instalar varios de una vez."),
    h("div", { class: "seccion" }, h("div", { class: "fila separada" }, h("h2", { texto: "Añadir sistemas" }), instalarBtn),
      libres.length ? h("div", { class: "pila" }, h("p", { class: "tenue", texto: "Toca las tarjetas para marcarlas y pulsa «Instalar»." }), filtro, rejilla)
        : h("p", { class: "tenue", texto: "Ya tienes instalados todos los sistemas del catálogo." })));
}

export async function aplicarGuardado({ ruta, recargar, ir }) {
  const guardados = await obtener("/api/flujos");
  if (!guardados.length) {
    const r = await dialogo({ titulo: "No tienes flujos guardados", contenido: h("p", { texto: "Guarda el flujo de un proyecto que te guste desde su pestaña «Flujo del asistente» y podrás reutilizarlo aquí." }),
      acciones: [{ texto: "Ir a flujos guardados", clase: "primario" }] });
    if (r) ir("flujos");
    return;
  }
  const radios = guardados.map((g, i) => h("input", { type: "radio", name: "guardado", value: g.id, checked: i === 0 }));
  const contenido = h("div", { class: "pila" }, h("p", { class: "tenue", texto: "Se instalan los sistemas que falten y se cambia el flujo del asistente de este proyecto." }),
    h("ul", { class: "lista desplazable" }, guardados.map((g, i) => h("li", {}, h("label", { class: "casilla", style: "flex:1" }, radios[i],
      h("span", {}, h("b", { texto: g.nombre }), h("div", { class: "tenue", texto: `${g.sistemas.length} sistema(s)` + (g.descripcion ? ` · ${g.descripcion}` : "") })))))));
  const id = await dialogo({ titulo: "Aplicar un flujo guardado", contenido, acciones: [{ texto: "Aplicar", clase: "primario", accion: () => radios.find((r) => r.checked)?.value || false }] });
  if (!id) return;
  const [r] = await enviar("/api/flujos/aplicar", { id, repos: [ruta] });
  if (r.error) throw new Error(r.error);
  avisar(r.instalados.length ? `Flujo aplicado; instalados: ${r.instalados.length}` : "Flujo aplicado");
  recargar();
}
