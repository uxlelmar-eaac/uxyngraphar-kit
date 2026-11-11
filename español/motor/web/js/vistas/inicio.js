// Inicio: cómo están tus proyectos de un vistazo y accesos a lo más habitual.

import { obtener, enviar } from "../api.js";
import { h, cabecera, boton, insignia, avisar } from "../ui.js";
import { agregarProyectos } from "../explorador.js";
import { tarjetaProyecto } from "./proyectos.js";

export async function vista(_params, { ir }) {
  const [lista, guardados, herramienta] = await Promise.all([obtener("/api/proyectos"), obtener("/api/flujos"), obtener("/api/herramienta")]);
  const conActualizacion = lista.filter((p) => p.actualizables > 0);
  const alterados = lista.filter((p) => p.alterados > 0);
  const atencion = [...new Set([...alterados, ...conActualizacion])];
  // Avisos proactivos (M-28): versión nueva, cambios a medias, actualizaciones, FLUJO.json inválido…
  const nueva = h("div", { class: "pila" });
  const BOTON = { actualizar: ["Ver cómo actualizar", (a) => ir("herramienta")],
    reparar: ["Reparar", async () => { await enviar("/api/herramienta/reparar", { proyectos: true }); avisar("Reparación hecha"); ir("inicio"); }],
    abrir: ["Abrir", (a) => ir("proyecto", { ruta: a.ruta })] };
  obtener("/api/avisos").then((avisos) => {
    nueva.replaceChildren(...avisos.map((a) => h("div", { class: `banda ${a.tipo === "interrumpida" || a.tipo === "flujo" ? "mal" : "acento"}` },
      h("b", { texto: a.mensaje }), h("span", { class: "espacio" }),
      BOTON[a.accion] ? boton(BOTON[a.accion][0], () => BOTON[a.accion][1](a), { clase: "primario pequeno" }) : null)));
  }).catch(() => {});

  const cifra = (valor, texto, tipo) => h("div", { class: "tarjeta" }, h("div", { class: "cifra", texto: String(valor) }), h("div", { class: "tenue" }, texto),
    tipo ? h("div", { style: "margin-top:6px" }, tipo) : null);

  return h("div", {},
    cabecera("Hola", "Desde aquí gestionas los sistemas de gobernanza de todos tus proyectos."),
    nueva,
    h("div", { class: "rejilla-cifras", style: "margin-top:16px" },
      cifra(lista.length, "proyectos en tu lista"),
      cifra(conActualizacion.length, "con actualizaciones", conActualizacion.length ? insignia("actualizar", "aviso") : insignia("todo al día", "bien")),
      cifra(alterados.length, "con sistemas alterados", alterados.length ? insignia("reparar", "mal") : null),
      cifra(guardados.length, "flujos guardados"),
    ),
    h("div", { class: "seccion" }, h("h2", { texto: "¿Qué quieres hacer?" }),
      h("div", { class: "rejilla" },
        boton("Añadir un proyecto", async () => { if ((await agregarProyectos()).length) ir("proyectos"); }, { clase: "grande", icono: "mas" }),
        boton("Usar un flujo guardado", () => ir("flujos"), { clase: "grande", icono: "flujos" }),
        boton("Explorar sistemas", () => ir("catalogo"), { clase: "grande", icono: "catalogo" }),
        boton("Actualizar uxyngraphar", () => ir("herramienta"), { clase: "grande", icono: "descargar" }),
      )),
    atencion.length ? h("div", { class: "seccion" }, h("h2", { texto: "Necesitan tu atención" }),
      h("div", { class: "rejilla" }, atencion.map((p) => tarjetaProyecto(p, ir)))) : null,
    !lista.length ? h("div", { class: "seccion tarjeta" }, h("h2", { texto: "Empieza por añadir tus proyectos" }),
      h("p", { class: "tenue", texto: "Elige la carpeta de un proyecto (o una carpeta que contenga varios) y el panel los encontrará." }),
      boton("Añadir proyectos", async () => { if ((await agregarProyectos()).length) ir("proyectos"); }, { clase: "primario", icono: "mas" })) : null,
    h("p", { class: "tenue", style: "margin-top:28px", texto: `uxyngraphar ${herramienta.version}` + (herramienta.instalada ? "" : " · copia del repositorio") }),
  );
}
