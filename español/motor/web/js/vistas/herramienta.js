// Herramienta y ajustes: versión, actualizar uxyngraphar y los sistemas de todos los proyectos, versiones guardadas,
// accesos directos y desinstalar.

import { obtener, enviar, esperarServidor, nombreDe } from "../api.js";
import { h, vaciar, cabecera, boton, insignia, avisar, confirmar, dialogo } from "../ui.js";

const TRAS_ACTUALIZAR = "uxyn-tras-actualizar";

export async function vista() {
  const info = await obtener("/api/herramienta");
  const estadoVersion = h("div", { class: "pila" }, h("div", { class: "cargando" }, "Buscando versiones nuevas…"));
  const registro = h("pre", { hidden: true, "aria-live": "polite" });

  async function comprobar(forzar) {
    const u = await obtener("/api/herramienta/ultima", forzar ? { forzar: 1 } : {});
    if (u.hay_nueva) {
      vaciar(estadoVersion, h("div", { class: "banda acento" }, h("b", { texto: `Hay una versión nueva: ${u.ultima}` }), h("span", { class: "espacio" }),
        boton(`Actualizar a ${u.ultima}`, () => actualizar(""), { clase: "primario", icono: "descargar" })));
    } else if (u.error) {
      vaciar(estadoVersion, h("div", { class: "banda aviso" }, "No pude consultar si hay versiones nuevas (¿sin internet?).", h("span", { class: "espacio" }),
        boton("Reintentar", () => comprobar(true), { clase: "pequeno" })));
    } else {
      vaciar(estadoVersion, h("div", { class: "banda bien" }, `Tienes la última versión (${u.actual}).`, h("span", { class: "espacio" }),
        boton("Buscar de nuevo", () => comprobar(true), { clase: "pequeno" })));
    }
  }

  async function seguir(progreso) {
    registro.hidden = false;
    let p = progreso;
    while (p.estado === "en_curso") {
      registro.textContent = p.lineas.join("\n");
      registro.scrollTop = registro.scrollHeight;
      await new Promise((r) => setTimeout(r, 1000));
      p = await obtener("/api/herramienta/progreso");
    }
    registro.textContent = p.lineas.join("\n");
    if (p.estado === "error") throw new Error("La actualización no se completó. Revisa el registro de abajo.");
    if (!p.reiniciar) { avisar("Ya tenías esa versión activa."); return; }
    vaciar(estadoVersion, h("div", { class: "cargando" }, h("span", { class: "giro" }), `Reiniciando el panel con la versión ${p.version}…`));
    sessionStorage.setItem(TRAS_ACTUALIZAR, p.version);
    await enviar("/api/reiniciar");
    if (await esperarServidor()) location.reload();
    else throw new Error("El panel no volvió a arrancar. Ábrelo de nuevo con el acceso directo o el comando uxyngraphar.");
  }

  const actualizar = async (version) => seguir(await enviar("/api/herramienta/actualizar", { version }));
  const usar = (v) => async () => {
    if (!(await confirmar({ titulo: `Usar la versión ${v}`, texto: "El panel se reiniciará con esa versión. Tus proyectos no cambian hasta que actualices sus sistemas.", si: "Cambiar de versión" }))) return;
    await seguir(await enviar("/api/herramienta/usar", { version: v }));
  };

  const recienActualizado = sessionStorage.getItem(TRAS_ACTUALIZAR);
  sessionStorage.removeItem(TRAS_ACTUALIZAR);
  if (info.instalada) comprobar(false).catch(() => {});
  else vaciar(estadoVersion, h("div", { class: "banda aviso" }, "Estás usando la copia del repositorio: se actualiza con git, no desde aquí."));

  return h("div", {},
    cabecera("Herramienta y ajustes", "Mantén uxyngraphar al día y decide cómo se abre en este equipo."),
    recienActualizado ? h("div", { class: "banda bien", style: "margin-bottom:16px" }, h("b", { texto: `uxyngraphar se actualizó a ${recienActualizado}.` }),
      " Los sistemas de tus proyectos pueden tener mejoras.", h("span", { class: "espacio" }), boton("Actualizar todos mis proyectos", actualizarProyectos, { clase: "primario" })) : null,
    h("div", { class: "tarjeta pila" }, h("div", { class: "fila separada" }, h("h2", { texto: "Versión" }), insignia(info.version, "acento")), estadoVersion, registro),
    h("div", { class: "tarjeta pila" }, h("h2", { texto: "Sistemas de mis proyectos" }),
      h("p", { class: "tenue", texto: "Actualiza (o repara) de una vez los sistemas de todos tus proyectos con la versión del catálogo que tienes ahora." }),
      h("div", {}, boton("Actualizar todos mis proyectos", actualizarProyectos, { icono: "descargar" }))),
    info.instalada && info.anterior && info.anterior !== info.activa ? h("div", { class: "tarjeta pila" }, h("h2", { texto: "¿Algo no va bien tras actualizar?" }),
      h("p", { class: "tenue", texto: `Vuelve a la versión que tenías antes (${info.anterior}). Tus datos se respaldan y la versión se comprueba antes de activarla; si algo falla, todo queda como estaba.` }),
      h("div", {}, boton(`Volver a la versión anterior (${info.anterior})`, volverAnterior, { icono: "deshacer" }))) : null,
    info.guardadas.length > 1 ? h("div", { class: "tarjeta pila" }, h("h2", { texto: "Versiones guardadas" }),
      h("p", { class: "tenue", texto: "Si algo falla tras actualizar, puedes volver a una versión anterior." }),
      h("ul", { class: "lista" }, info.guardadas.map((v) => h("li", {}, h("span", { class: "espacio", texto: v }),
        v === info.activa ? insignia("activa", "bien") : boton("Usar esta", usar(v), { clase: "pequeno" }))))) : null,
    h("div", { class: "tarjeta pila" }, h("h2", { texto: "Reparar" }),
      h("p", { class: "tenue", texto: "Revisa la herramienta (versión activa, archivos dañados, comando, PATH, accesos directos) y, si quieres, tus proyectos (cambios cortados, sistemas alterados, flujo inválido). No cambia de versión ni toca tu trabajo." }),
      h("div", { class: "fila" }, boton("Reparar la herramienta", () => reparar(false)), boton("Reparar herramienta y proyectos", () => reparar(true)))),
    await tarjetaAccesos(),
    await tarjetaHistorial(),
    h("div", { class: "tarjeta pila" }, h("h2", { texto: "Carpeta de uxyngraphar" }), h("p", {}, h("code", { texto: info.carpeta })),
      h("p", { class: "tenue", texto: "Aquí se guardan la herramienta, tu lista de proyectos, tus flujos guardados y los respaldos." })),
    h("div", { class: "tarjeta pila", style: "border-color:var(--mal)" }, h("h2", { texto: "Desinstalar" }),
      h("p", { class: "tenue", texto: "Eliges qué quitar: todo, solo la herramienta (núcleo y panel), uxyngraphar de tus proyectos o solo los accesos directos. Antes de borrar nada verás la lista exacta." }),
      h("div", {}, boton("Desinstalar…", desinstalar, { clase: "peligro" }))));

  async function volverAnterior() {
    if (!(await confirmar({ titulo: `Volver a la versión ${info.anterior}`, texto: "El panel se reiniciará con esa versión. Tus proyectos no cambian.", si: "Volver" }))) return;
    await seguir(await enviar("/api/herramienta/anterior"));
  }

  async function reparar(conProyectos) {
    const r = await enviar("/api/herramienta/reparar", { proyectos: conProyectos });
    const filas = [...r.hechos.map((x) => ["bien", x]), ...r.problemas.map((x) => ["mal", x]),
      ...(r.proyectos || []).map((p) => [p.error ? "mal" : "bien", `${nombreDe(p.ruta)}: ${p.error || p.hechos.join("; ") || "sano"}`])];
    await dialogo({ titulo: "Reparación", cancelar: "Cerrar", contenido: filas.length
      ? h("ul", { class: "lista" }, filas.map(([tipo, texto]) => h("li", {}, insignia(tipo === "bien" ? "ok" : "problema", tipo), h("span", { texto }))))
      : h("p", { texto: "Todo estaba bien: no hubo nada que reparar." }) });
  }

  async function desinstalar() {
    const alcances = [
      ["herramienta", "Solo la herramienta (núcleo y panel)", "Quita el comando, el panel, el PATH, los accesos directos, tu lista de proyectos y tus flujos guardados. Tus proyectos no se tocan."],
      ["proyectos", "uxyngraphar de mis proyectos", "Quita uxyngraphar de los proyectos que elijas. La herramienta se queda."],
      ["todo", "Todo", "La herramienta y uxyngraphar de todos tus proyectos registrados."],
      ["accesos", "Solo los accesos directos", "Quita los accesos del menú, el escritorio y la barra. Nada más."],
    ];
    const radios = alcances.map(([valor], i) => h("input", { type: "radio", name: "alcance", value: valor, checked: i === 0 }));
    const lista = await obtener("/api/proyectos").catch(() => []);
    const marcas = lista.map((p) => h("input", { type: "checkbox", value: p.ruta, checked: true }));
    const proyectosZona = h("div", { class: "pila", hidden: true }, h("b", { texto: "Proyectos" }),
      lista.length ? h("ul", { class: "lista desplazable" }, lista.map((p, i) => h("li", {}, h("label", { class: "casilla", style: "flex:1" }, marcas[i],
        h("span", {}, h("b", { texto: p.nombre }), h("div", { class: "tenue", texto: p.ruta }))))))
        : h("p", { class: "tenue", texto: "No tienes proyectos en tu lista." }));
    const trabajo = h("input", { type: "checkbox" });
    const trabajoZona = h("label", { class: "casilla", hidden: true }, trabajo, h("span", { texto: "Borrar también el trabajo guardado de cada proyecto (uxyngraphar/trabajo)" }));
    const elegido = () => radios.find((r) => r.checked).value;
    const refrescar = () => {
      proyectosZona.hidden = elegido() !== "proyectos";
      trabajoZona.hidden = !["todo", "proyectos"].includes(elegido());
    };
    radios.forEach((r) => r.addEventListener("change", refrescar));
    const contenido = h("div", { class: "pila" },
      h("ul", { class: "lista" }, alcances.map(([, titulo, texto], i) => h("li", {}, h("label", { class: "casilla", style: "flex:1" }, radios[i],
        h("span", {}, h("b", { texto: titulo }), h("div", { class: "tenue", texto })))))),
      proyectosZona, trabajoZona);
    const pedido = await dialogo({ titulo: "Desinstalar", contenido, acciones: [{ texto: "Ver lo que se quitará", clase: "primario", accion: () => ({
      alcance: elegido(), rutas: elegido() === "proyectos" ? marcas.filter((m) => m.checked).map((m) => m.value) : [], con_trabajo: trabajo.checked }) }] });
    if (!pedido) return;
    if (pedido.alcance === "proyectos" && !pedido.rutas.length) return avisar("No elegiste ningún proyecto.", "mal");
    const plan = await enviar("/api/herramienta/desinstalar", { ...pedido, simular: true });
    const seguro = await dialogo({ titulo: "Esto es lo que se quitará", contenido: h("pre", { texto: plan.texto, style: "max-height:50vh;overflow:auto" }),
      acciones: [{ texto: "Desinstalar", clase: "peligro lleno" }] });
    if (!seguro) return;
    const informe = await enviar("/api/herramienta/desinstalar", pedido);
    if (["todo", "herramienta"].includes(pedido.alcance)) {
      document.querySelector("#desconectado h2").textContent = informe.pendiente.length ? "Desinstalación con avisos" : "uxyngraphar se desinstaló";
      document.querySelector("#desconectado p").textContent = informe.texto;
      document.getElementById("desconectado").hidden = false;
      return;
    }
    await dialogo({ titulo: "Desinstalación terminada", cancelar: "Cerrar", contenido: h("pre", { texto: informe.texto, style: "max-height:50vh;overflow:auto" }) });
    location.reload();
  }
}

export async function actualizarProyectos() {
  const resultados = await enviar("/api/herramienta/proyectos");
  if (!resultados.length) return avisar("No tienes proyectos en tu lista.");
  await dialogo({ titulo: "Proyectos actualizados", cancelar: "Cerrar", contenido: h("ul", { class: "lista" }, resultados.map((r) => h("li", {},
    h("b", { class: "espacio", texto: nombreDe(r.ruta) }),
    r.error ? h("span", { class: "insignia mal", texto: r.error }) : insignia(r.actualizados.length ? `${r.actualizados.length} actualizado(s)` : "ya estaba al día", "bien")))) });
}

export async function tarjetaAccesos({ titulo = "Accesos directos", explicacion = "Abre el panel sin usar la terminal, desde el menú, el escritorio o la barra de tareas.", marcarPorDefecto = false } = {}) {
  const datos = await obtener("/api/accesos");
  const zona = h("div", { class: "tarjeta pila" });
  const pintar = (d) => {
    const ninguno = !d.disponibles.some((a) => a.creado);
    const casillas = d.disponibles.map((a) => h("input", { type: "checkbox", value: a.tipo, disabled: !a.posible,
      checked: a.creado || (marcarPorDefecto && ninguno && a.posible && a.tipo === "menu") }));
    vaciar(zona, h("h2", { texto: titulo }), h("p", { class: "tenue", texto: explicacion }),
      !d.lanzador ? h("div", { class: "banda aviso", texto: "Los accesos directos necesitan la herramienta instalada con el comando de instalación de una línea." }) : null,
      h("ul", { class: "lista" }, d.disponibles.map((a, i) => h("li", { style: "flex-direction:column;align-items:stretch" },
        h("label", { class: "casilla" }, casillas[i], h("span", {}, h("b", { texto: a.etiqueta }), a.creado ? " " : null, a.creado ? insignia("creado", "bien") : null)),
        a.nota ? h("div", { class: "tenue", texto: a.nota }) : null))),
      h("div", {}, boton("Guardar accesos directos", async () => {
        const r = await enviar("/api/accesos", { tipos: casillas.filter((c) => c.checked && !c.disabled).map((c) => c.value) });
        (r.avisos || []).forEach((a) => avisar(a));
        avisar("Accesos directos actualizados");
        pintar(r);
      }, { clase: "primario" })));
  };
  pintar(datos);
  return zona;
}


// Historial: las últimas acciones que cambiaron algo (registros/acciones.jsonl), desde la CLI o desde el panel.
async function tarjetaHistorial() {
  const acciones = await obtener("/api/historial", { limite: 30 }).catch(() => []);
  const fila = (a) => h("li", {}, insignia(a.resultado === "ok" ? "ok" : "error", a.resultado === "ok" ? "bien" : "mal"),
    h("span", { class: "espacio", texto: `${a.fecha.replace("T", " ")} · ${a.accion}${a.proyecto ? " · " + nombreDe(a.proyecto) : ""}${a.ids?.length ? " · " + a.ids.join(", ") : ""}${a.error ? " · " + a.error : ""}` }),
    h("span", { class: "tenue", texto: a.origen }));
  return h("div", { class: "tarjeta pila" }, h("h2", { texto: "Historial" }),
    h("p", { class: "tenue", texto: "Las últimas acciones que cambiaron algo en tus proyectos o en la herramienta, desde el panel o desde la terminal." }),
    acciones.length ? h("ul", { class: "lista desplazable" }, acciones.map(fila)) : h("p", { class: "tenue", texto: "Aún no hay acciones registradas." }));
}
