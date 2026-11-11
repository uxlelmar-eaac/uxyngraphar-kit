// Pestañas de un proyecto: flujo del asistente, revisión y más opciones.

import { obtener, enviar } from "../api.js";
import { h, vaciar, boton, insignia, confirmar, avisar, pedirDatos } from "../ui.js";
import { editorFlujo } from "../flujo.js";

export function pestanaFlujo({ ruta, estado, ir, recargar }) {
  const sistemas = estado.sistemas.map((p) => ({ id: p.id, titulo: p.titulo || p.id, descripcion: p.descripcion }));
  let cambiado = false;
  const guardarBtn = boton("Guardar cambios", guardar, { clase: "primario" });
  const editor = editorFlujo(estado.flujo, sistemas, () => { cambiado = true; });

  async function guardar() {
    await enviar("/api/repo/flujo", { repo: ruta, flujo: editor.valor() });
    cambiado = false;
    avisar("Flujo guardado. El asistente lo usará desde su próximo pedido.");
  }

  async function comoPlantilla() {
    const datos = await pedirDatos({ titulo: "Guardar como flujo reutilizable", explicacion: "Guarda estos sistemas y esta forma de trabajar para aplicarlos en otros proyectos con un clic.",
      campos: [{ nombre: "nombre", etiqueta: "Nombre", ayuda: "Ej.: API con revisión humana", obligatorio: true }, { nombre: "descripcion", etiqueta: "Descripción (opcional)" }] });
    if (!datos) return;
    if (cambiado) await guardar();
    await enviar("/api/flujos/desde-proyecto", { repo: ruta, ...datos });
    avisar("Flujo guardado en tu biblioteca");
  }

  return h("div", { class: "pila" },
    h("p", { class: "tenue", texto: "Decide cómo usa el asistente de IA los sistemas de este proyecto. Solo tú lo cambias; el asistente lo lee en cada pedido." }),
    h("div", { class: "tarjeta" }, editor.nodo),
    h("div", { class: "fila" }, guardarBtn, boton("Guardar como flujo reutilizable", comoPlantilla, { icono: "flujos" }),
      h("span", { class: "espacio" }), boton("Ver mis flujos guardados", () => ir("flujos"), { clase: "fantasma" })),
    !estado.sistemas.length ? h("p", { class: "tenue" }, "Consejo: instala sistemas en la pestaña «Sistemas» para poder usarlos en el flujo.",
      " ", h("a", { href: "#", onclick: (e) => { e.preventDefault(); recargar(); }, texto: "Recargar" })) : null);
}

export function pestanaSalud({ ruta, estado }) {
  const salida = h("div", { class: "pila" });
  async function revisar() {
    const resultados = await enviar("/api/repo/verificar", { repo: ruta });
    if (!resultados.length) return vaciar(salida, h("p", { class: "tenue", texto: "Los sistemas instalados no tienen comprobaciones." }));
    const fallos = resultados.filter((r) => r.codigo);
    vaciar(salida,
      h("div", { class: `banda ${fallos.length ? "mal" : "bien"}` }, fallos.length ? `${fallos.length} comprobación(es) encontraron problemas.` : "Todo en orden: todas las comprobaciones pasaron."),
      h("ul", { class: "lista" }, resultados.map((r) => h("li", { style: "flex-direction:column;align-items:stretch" },
        h("div", { class: "fila separada" }, h("b", { texto: (estado.sistemas.find((p) => p.id === r.sistema) || {}).titulo || r.sistema }),
          r.codigo ? insignia("con problemas", "mal") : insignia("bien", "bien")),
        h("details", {}, h("summary", { texto: "Ver detalles" }), h("div", { class: "tenue", texto: r.verificacion }), h("pre", { texto: r.salida || "(sin mensajes)" }))))));
  }
  const integridad = estado.sistemas.filter((p) => !p.integro);
  const automatico = h("div", { class: "pila" });
  const TEXTOS = { workflow: ["En cada push y PR (GitHub Actions)", ".github/workflows/uxyngraphar-verificar.yml"],
    precommit: ["Antes de cada commit (gancho pre-commit, solo en este equipo)", ".git/hooks/pre-commit"] };
  async function pintarAutomatico(actual) {
    const e = actual || await obtener("/api/repo/integracion", { repo: ruta });
    vaciar(automatico, Object.entries(TEXTOS).map(([tipo, [titulo, archivo]]) => h("div", { class: "fila separada" },
      h("span", {}, h("b", { texto: titulo }), h("div", { class: "tenue", texto: archivo })),
      estado.registrado ? boton(e[tipo] ? "Quitar" : "Añadir", async () => {
        pintarAutomatico(await enviar("/api/repo/integracion", { repo: ruta, tipo, accion: e[tipo] ? "quitar" : "agregar" }));
        avisar(e[tipo] ? "Quitado" : "Añadido");
      }, { clase: "pequeno" }) : insignia(e[tipo] ? "puesto" : "no", e[tipo] ? "bien" : ""))));
  }
  pintarAutomatico().catch(() => {});
  return h("div", { class: "pila" },
    h("p", { class: "tenue", texto: "Comprueba que los sistemas están intactos y que el proyecto cumple sus reglas." }),
    integridad.length ? h("div", { class: "banda mal" }, `${integridad.length} sistema(s) fueron modificados a mano. Repáralos desde la pestaña «Sistemas».`) : null,
    h("div", {}, boton("Revisar ahora", revisar, { clase: "primario", icono: "check" })), salida,
    h("div", { class: "tarjeta pila" }, h("h3", { texto: "Comprobar automáticamente (opcional)" }),
      h("p", { class: "tenue", texto: "uxyngraphar no ejecuta nada por su cuenta. Si quieres, añade aquí una comprobación automática; se quita igual de fácil y también al quitar uxyngraphar del proyecto." }),
      automatico));
}

export function pestanaOpciones({ ruta, estado, ir, recargar }) {
  const quitarLista = async () => {
    const r = await confirmar({ titulo: "Quitar de mi lista", texto: "El proyecto deja de aparecer en el panel. No se borra nada de su carpeta.", si: "Quitar de la lista" });
    if (!r) return;
    await enviar("/api/proyectos/quitar", { ruta });
    avisar("Quitado de la lista");
    ir("proyectos");
  };
  const desinstalar = async () => {
    const r = await confirmar({ titulo: "Quitar uxyngraphar de este proyecto",
      texto: "Se quitan todos los sistemas, el flujo del asistente y las instrucciones que uxyngraphar añadió a AGENTES.md. El trabajo guardado (carpeta uxyngraphar/trabajo) se conserva, salvo que marques la casilla.",
      si: "Quitar uxyngraphar", peligro: true, casilla: "Borrar también todo el trabajo guardado" });
    if (!r) return;
    const hecho = await enviar("/api/repo/desinstalar", { repo: ruta, con_trabajo: r.casilla, confirmar: estado.nombre });
    avisar("uxyngraphar quitado del proyecto");
    recargar();
  };
  const deshacer = async () => {
    const lista = await obtener("/api/repo/respaldos", { repo: ruta });
    if (!lista.length) { avisar("No hay cambios que deshacer en este proyecto"); return; }
    const [ultimo] = lista;
    const r = await confirmar({ titulo: "Deshacer el último cambio",
      texto: `El proyecto vuelve a como estaba antes de «${ultimo.motivo}» (${ultimo.fecha.replace("T", " ")}). Tu trabajo en uxyngraphar/trabajo no se toca. Si te arrepientes, vuelve a pulsar «Deshacer»: también se puede deshacer.`,
      si: "Deshacer" });
    if (!r) return;
    await enviar("/api/repo/deshacer", { repo: ruta, respaldo: ultimo.nombre, confirmar: estado.nombre });
    avisar("Cambio deshecho");
    recargar();
  };
  const desinstalarBtn = boton("Quitar uxyngraphar…", desinstalar, { clase: "peligro" });
  desinstalarBtn.disabled = !estado.sistemas.length;
  return h("div", { class: "pila" },
    h("div", { class: "tarjeta" }, h("h3", { texto: "Carpeta del proyecto" }), h("p", {}, h("code", { texto: estado.ruta })),
      boton("Copiar ruta", async () => { await navigator.clipboard.writeText(estado.ruta); avisar("Ruta copiada"); }, { clase: "pequeno" })),
    estado.registrado ? h("div", { class: "tarjeta" }, h("h3", { texto: "Quitar de mi lista" }),
      h("p", { class: "tenue", texto: "Deja de mostrarlo en el panel sin tocar sus archivos." }), boton("Quitar de mi lista", quitarLista)) : null,
    estado.registrado ? h("div", { class: "tarjeta" }, h("h3", { texto: "Deshacer el último cambio" }),
      h("p", { class: "tenue", texto: "Vuelve a como estaba antes de la última instalación, actualización o retirada de sistemas. No toca tu trabajo." }),
      boton("Deshacer…", deshacer)) : null,
    h("div", { class: "tarjeta" }, h("h3", { texto: "Quitar uxyngraphar de este proyecto" }),
      h("p", { class: "tenue", texto: "Desinstala todos los sistemas y deja el proyecto como si nunca hubiera usado uxyngraphar (puedes conservar el trabajo)." }),
      desinstalarBtn));
}
