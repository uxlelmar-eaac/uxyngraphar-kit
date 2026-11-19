// Quitar un proyecto del panel (1.5.21): «Solo desvincular» (sale de la lista y de sus grupos; la carpeta no se toca)
// o «Quitar todo» (además retira lo que puso uxyngraphar). Antes de confirmar se ve la lista exacta de archivos y
// sistemas; lo que la persona modificó se respalda y lo que no creó uxyngraphar no se toca.

import { obtener, enviar } from "../api.js";
import { h, avisar, dialogo, insignia } from "../ui.js";

const grupo = (titulo, filas, clase = "") => (filas.length
  ? h("div", { class: `quitar-grupo ${clase}`.trim() }, h("h4", { texto: `${titulo} (${filas.length})` }),
    h("ul", { class: "quitar-lista" }, filas.map((f) => (typeof f === "string" ? h("li", { texto: f }) : f))))
  : null);

function listaPlan(p) {
  return h("div", { class: "pila" },
    grupo("Sistemas que se quitan", p.sistemas.map((s) => h("li", {}, `${s.id} ${s.version || ""} `,
      s.modificados.length ? insignia(`${s.modificados.length} archivo(s) modificados por ti`, "nota") : null))),
    grupo("Se borran", p.borrar),
    grupo("Se editan (solo lo de uxyngraphar)", p.editar),
    grupo("Se copian antes a un respaldo (los modificaste tú)", p.respaldar, "aviso"),
    grupo("Se quedan donde están", [...p.ajenos.map((a) => `${a} (no lo creó uxyngraphar)`), ...p.conservar]));
}

function textoGrupos(p) {
  if (!p.grupos.length) return null;
  const quedan = p.grupos.filter((g) => !p.grupos_que_desaparecen.includes(g));
  return h("p", { class: "tenue", texto: [
    quedan.length ? `Sale de ${quedan.length === 1 ? "el grupo" : "los grupos"} ${quedan.map((g) => `«${g}»`).join(", ")}.` : "",
    p.grupos_que_desaparecen.length ? `${p.grupos_que_desaparecen.map((g) => `«${g}»`).join(", ")} se ${p.grupos_que_desaparecen.length === 1 ? "borra" : "borran"} porque se ${p.grupos_que_desaparecen.length === 1 ? "queda" : "quedan"} con un solo proyecto.` : "",
  ].filter(Boolean).join(" ") });
}

function resumen(r) {
  const lineas = [...r.hechos];
  if (r.respaldo) lineas.push(`Copia de lo que habías modificado: ${r.respaldo}`);
  for (const c of r.conservados || []) lineas.push(`Conservado: ${c}`);
  for (const g of r.grupos_borrados || []) lineas.push(`Grupo «${g}» borrado (se quedaba con un solo proyecto)`);
  for (const g of r.grupos_actualizados || []) lineas.push(`Sale del grupo «${g}»`);
  for (const x of r.restos || []) lineas.push(`Queda por revisar: ${x}`);
  return lineas;
}

/** Abre el diálogo y hace lo elegido. Devuelve el resultado del servidor o null si se cancela. */
export async function quitarProyecto({ ruta, nombre }) {
  const p = await obtener("/api/proyectos/plan-quitar", { ruta });
  const solo = h("input", { type: "radio", name: "quitar-modo", value: "desvincular", checked: true });
  const todo = h("input", { type: "radio", name: "quitar-modo", value: "todo", disabled: !p.existe });
  const detalle = h("div", { class: "pila", hidden: true }, listaPlan(p));
  todo.addEventListener("change", () => { detalle.hidden = !todo.checked; });
  solo.addEventListener("change", () => { detalle.hidden = !todo.checked; });
  const nada = !p.sistemas.length && !p.borrar.length && !p.editar.length;
  const elegido = await dialogo({
    titulo: `Quitar ${nombre || p.nombre}`,
    contenido: h("div", { class: "pila" },
      !p.existe ? h("div", { class: "banda aviso", texto: "La carpeta ya no existe: solo se puede quitar de la lista." }) : null,
      h("div", { class: "quitar-opciones", role: "radiogroup", "aria-label": "Qué quitar" },
        h("label", { class: "quitar-opcion" }, solo, h("span", {}, h("b", { texto: "Solo desvincular" }),
          h("div", { class: "tenue", texto: "Deja de aparecer en el panel. No se toca nada de la carpeta del proyecto." }))),
        h("label", { class: "quitar-opcion peligro" }, todo, h("span", {}, h("b", { texto: "Quitar todo" }),
          h("div", { class: "tenue", texto: nada && p.existe
            ? "No tiene nada de uxyngraphar: equivale a desvincular."
            : "Retira todo lo que uxyngraphar puso en el proyecto (sistemas, instrucciones, protecciones, conexiones) y luego lo desvincula. Tu código no se toca." })))),
      textoGrupos(p),
      detalle),
    acciones: [{ texto: "Continuar", clase: "primario", accion: () => (todo.checked ? "todo" : "desvincular") }],
  });
  if (!elegido) return null;
  if (elegido === "todo") {
    const entiendo = h("input", { type: "checkbox" });
    const ok = await dialogo({
      titulo: `¿Quitar todo lo de uxyngraphar de ${p.nombre}?`,
      contenido: h("div", { class: "pila" },
        h("p", { texto: `Se quitan ${p.sistemas.length} sistema(s), se borran ${p.borrar.length} elemento(s) y se editan ${p.editar.length}.`
          + (p.respaldar.length ? ` Antes se copian ${p.respaldar.length} archivo(s) que modificaste a un respaldo en tu carpeta de uxyngraphar.` : "")
          + " Tu código y lo que no creó uxyngraphar se quedan como están. Hay copia de seguridad del cambio en la carpeta de uxyngraphar." }),
        h("label", { class: "casilla" }, entiendo, h("span", { texto: "Entiendo que se quitan estos archivos del proyecto" }))),
      acciones: [{ texto: "Quitar todo", clase: "peligro lleno", accion: () => {
        if (!entiendo.checked) { avisar("Marca la casilla para confirmar.", "mal"); return false; }
        return true;
      } }],
    });
    if (!ok) return null;
  }
  const r = await enviar("/api/proyectos/quitar", { ruta: p.ruta, ...(elegido === "todo" ? { todo: true, confirmar: true } : {}) });
  const lineas = resumen(r);
  if (elegido === "todo" || (r.grupos_borrados || []).length) {
    await dialogo({ titulo: elegido === "todo" ? `${p.nombre}: uxyngraphar quitado` : `${p.nombre}: quitado de la lista`,
      contenido: h("ul", { class: "lista" }, lineas.map((l) => h("li", { texto: l }))), acciones: [{ texto: "Entendido", clase: "primario" }], cancelar: null });
  } else {
    avisar(`${p.nombre}: quitado de la lista${(r.grupos_actualizados || []).length ? ` y de ${r.grupos_actualizados.length} grupo(s)` : ""}`);
  }
  return r;
}
