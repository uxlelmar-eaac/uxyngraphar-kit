// Bienvenida tras instalar o actualizar: lo que hizo el instalador, comando en la terminal, accesos directos y primeros pasos.

import { obtener, enviar } from "../api.js";
import { h, cabecera, boton, avisar } from "../ui.js";
import { agregarProyectos } from "../explorador.js";
import { tarjetaAccesos } from "./herramienta.js";

export async function vista(_params, { ir }) {
  const b = await obtener("/api/bienvenida");
  const titulo = b.anterior ? `uxyngraphar se actualizó a ${b.version}` : b.version ? `uxyngraphar ${b.version} está listo` : "uxyngraphar está listo";
  const path = b.path_pendiente && !b.en_path ? h("div", { class: "tarjeta pila" },
    h("h2", { texto: "¿Usar uxyngraphar también desde la terminal?" }),
    h("p", { class: "tenue", texto: "Añade el comando uxyngraphar a tu terminal para abrir este panel escribiendo una sola palabra. Es opcional: los accesos directos ya lo abren." }),
    h("div", {}, boton("Sí, añadir el comando", async () => avisar(await enviar("/api/herramienta/path")), { clase: "primario" }))) : null;

  return h("div", { class: "pila" },
    cabecera(titulo, b.anterior ? `Antes tenías la versión ${b.anterior}. Tus proyectos siguen como estaban.` : "Unos ajustes rápidos y empiezas."),
    path,
    await tarjetaAccesos({ titulo: "Accesos directos", explicacion: "Para abrir el panel sin terminal. Elige dónde quieres tenerlo.", marcarPorDefecto: !b.accesos_preguntados }),
    h("div", { class: "tarjeta pila" }, h("h2", { texto: "Primeros pasos" }),
      h("p", { class: "tenue", texto: "Añade las carpetas de tus proyectos (o una carpeta que contenga varios) y elige los sistemas que quieras usar." }),
      h("div", { class: "fila" },
        boton("Añadir mis proyectos", async () => { if ((await agregarProyectos()).length) ir("proyectos"); }, { clase: "primario", icono: "mas" }),
        boton("Ir al inicio", () => ir("inicio")))),
    (b.pasos || []).length ? h("details", {}, h("summary", { texto: "Ver lo que hizo el instalador" }), h("pre", { texto: b.pasos.join("\n") })) : null);
}
