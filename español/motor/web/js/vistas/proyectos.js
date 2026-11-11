// Mis proyectos: la lista de proyectos que gestiona el panel, con su estado.

import { obtener, enviar } from "../api.js";
import { h, cabecera, boton, insignia, vacio, confirmar, avisar, dialogo, elegirVarios, pedirDatos } from "../ui.js";
import { agregarProyectos } from "../explorador.js";
import { MODOS } from "../flujo.js";

export function estadoProyecto(p) {
  if (!p.existe) return insignia("carpeta no encontrada", "mal");
  if (p.alterados) return insignia(`${p.alterados} alterado(s)`, "mal");
  if (p.actualizables) return insignia(`${p.actualizables} actualización(es)`, "aviso");
  if (!p.sistemas.length) return insignia("sin sistemas");
  return insignia("al día", "bien");
}

export function tarjetaProyecto(p, ir, alQuitar) {
  const abrir = () => ir("proyecto", { ruta: p.ruta });
  return h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("div", {}, h("h3", { texto: p.nombre }), h("div", { class: "tenue", texto: p.grupo })), estadoProyecto(p)),
    h("div", { class: "tenue" }, p.sistemas.length ? `${p.sistemas.length} sistema(s)` : "Sin sistemas instalados",
      p.modo ? ` · ${MODOS[p.modo]?.titulo || p.modo}` : ""),
    h("div", { class: "acciones" }, p.existe ? boton("Abrir", abrir, { clase: "primario pequeno" }) : null,
      alQuitar ? boton("Quitar de la lista", alQuitar, { clase: "fantasma pequeno" }) : null));
}

export async function vista(_params, { ir, recargar }) {
  const lista = await obtener("/api/proyectos");
  const filtro = h("input", { type: "search", placeholder: "Buscar por nombre…", "aria-label": "Buscar proyecto" });
  const rejilla = h("div", { class: "rejilla" });

  const quitar = (p) => async () => {
    const r = await confirmar({ titulo: `Quitar ${p.nombre} de la lista`, texto: "Solo deja de aparecer en el panel. No se borra nada de la carpeta del proyecto.", si: "Quitar de la lista" });
    if (!r) return;
    await enviar("/api/proyectos/quitar", { ruta: p.ruta });
    avisar("Quitado de la lista");
    recargar();
  };

  function pintar() {
    const texto = filtro.value.trim().toLowerCase();
    const visibles = lista.filter((p) => !texto || (p.nombre + " " + p.grupo).toLowerCase().includes(texto));
    rejilla.replaceChildren(...visibles.map((p) => tarjetaProyecto(p, ir, quitar(p))));
  }
  filtro.addEventListener("input", pintar);
  pintar();

  const agregar = async () => { if ((await agregarProyectos()).length) recargar(); };
  const grupos = lista.length > 1 ? await seccionGrupos(lista, recargar) : null;
  return h("div", {},
    cabecera("Mis proyectos", "Los proyectos que gestionas desde el panel. Ábrelos para instalar sistemas o cambiar su flujo.",
      boton("Añadir proyectos", agregar, { clase: "primario", icono: "mas" })),
    grupos,
    lista.length ? h("div", { class: "pila" }, filtro, rejilla)
      : vacio("Aún no hay proyectos", "Añade la carpeta de un proyecto, o una carpeta que contenga varios, y aparecerán aquí.",
        boton("Añadir proyectos", agregar, { clase: "primario", icono: "mas" })));
}


// Grupos (M-18): varios repos que forman un sistema y se actualizan o verifican juntos, con su matriz repo × sistema.
async function seccionGrupos(lista, recargar) {
  const grupos = await obtener("/api/grupos").catch(() => ({}));
  const nuevo = async () => {
    const datos = await pedirDatos({ titulo: "Nuevo grupo", explicacion: "Por ejemplo «uxyngraphar» para backend, frontend y landing.",
      campos: [{ nombre: "nombre", etiqueta: "Nombre (minúsculas y guiones)" }], si: "Siguiente" });
    if (!datos) return;
    const opciones = lista.filter((p) => p.existe).map((p) => ({ valor: p.ruta, titulo: p.nombre, detalle: p.ruta }));
    const eleccion = elegirVarios(opciones, []);
    const rutas = await dialogo({ titulo: `Proyectos de «${datos.nombre}»`, contenido: eleccion.nodo,
      acciones: [{ texto: "Crear grupo", clase: "primario", accion: () => eleccion.valores() }] });
    if (!rutas) return;
    await enviar("/api/grupos/guardar", { nombre: datos.nombre, rutas });
    avisar("Grupo creado");
    recargar();
  };
  const informe = (titulo, filas, texto) => dialogo({ titulo, cancelar: "Cerrar", contenido: h("ul", { class: "lista" },
    filas.map((f) => h("li", {}, insignia(f.error || f.codigo ? "revisar" : "bien", f.error || f.codigo ? "mal" : "bien"),
      h("span", { texto: `${f.nombre}: ${f.error || texto(f)}` })))) });
  const tarjeta = (nombre) => {
    const tabla = h("div", { class: "desplazable" });
    const verMatriz = async () => {
      const m = await obtener("/api/grupos/matriz", { nombre });
      tabla.replaceChildren(h("table", { class: "matriz" },
        h("thead", {}, h("tr", {}, h("th", { texto: "Sistema" }), ...m.repos.map((r) => h("th", { texto: r.nombre })))),
        h("tbody", {}, ...m.sistemas.map((pid) => h("tr", {}, h("td", { texto: pid }), ...m.repos.map((r) => {
          const c = r.sistemas[pid];
          return h("td", {}, c ? insignia(c.version, !c.integro ? "mal" : c.actualizable ? "aviso" : "bien") : "—");
        }))))));
    };
    return h("div", { class: "tarjeta pila" },
      h("div", { class: "fila separada" }, h("h3", { texto: nombre }), h("span", { class: "tenue", texto: grupos[nombre].map((r) => r.split(/[\\/]/).pop()).join(" · ") })),
      h("div", { class: "fila" },
        boton("Actualizar grupo", async () => informe("Actualizar grupo", await enviar("/api/grupos/actualizar", { nombre }),
          (f) => (f.actualizados || []).join(", ") || "al día"), { clase: "primario pequeno" }),
        boton("Verificar grupo", async () => informe("Verificar grupo", await enviar("/api/grupos/verificar", { nombre }),
          (f) => `${f.codigo ? "con problemas" : "bien"}${f.contratos && f.contratos !== "no instalado" ? ` · contratos ${f.contratos}` : ""}`), { clase: "pequeno" }),
        boton("Ver matriz", verMatriz, { clase: "pequeno" }),
        boton("Borrar grupo", async () => { if (await confirmar({ titulo: `Borrar el grupo «${nombre}»`, texto: "Solo se olvida el grupo; los proyectos siguen en tu lista.", si: "Borrar" })) { await enviar("/api/grupos/borrar", { nombre }); recargar(); } }, { clase: "fantasma pequeno" })),
      tabla);
  };
  return h("div", { class: "seccion pila" }, h("div", { class: "fila separada" }, h("h2", { texto: "Grupos" }), boton("Nuevo grupo", nuevo, { clase: "pequeno", icono: "mas" })),
    Object.keys(grupos).length ? h("div", { class: "pila" }, Object.keys(grupos).map(tarjeta))
      : h("p", { class: "tenue", texto: "Agrupa los repos de un mismo sistema para actualizarlos y verificarlos juntos." }));
}
