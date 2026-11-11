// Pestaña «Memorias» de un proyecto: lo que el asistente y la persona acuerdan recordar, por sistema.
// El asistente solo propone; aquí la persona aprueba, archiva o crea memorias vigentes.

import { obtener, enviar } from "../api.js";
import { h, boton, insignia, avisar, pedirDatos, vacio } from "../ui.js";

const ESTADOS = { propuesta: ["propuesta", "aviso"], vigente: ["vigente", "bien"], archivada: ["archivada", ""] };

function slug(texto) {
  return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60) || "memoria";
}

export async function pestanaMemorias({ ruta, estado, recargar }) {
  const sistemas = await obtener("/api/repo/memorias", { repo: ruta });
  if (!sistemas.length) return vacio("Sin sistemas instalados", "Instala sistemas para que el asistente y tú podáis guardar memorias del proyecto.");
  const pendientes = sistemas.reduce((n, s) => n + s.propuestas, 0);

  const accion = (rutaApi, s, m, texto) => async () => {
    await enviar(rutaApi, { repo: ruta, sistema: s.id, id: m.id });
    avisar(texto);
    recargar();
  };
  const nueva = (s) => async () => {
    const datos = await pedirDatos({ titulo: `Nueva memoria · ${s.titulo}`,
      explicacion: "Nace vigente: el asistente la aplicará cada vez que use este sistema.",
      campos: [{ nombre: "titulo", etiqueta: "Qué hay que recordar (título)", obligatorio: true },
        { nombre: "texto", etiqueta: "Detalle (opcional)" }, { nombre: "motivo", etiqueta: "Por qué importa (opcional)" },
        { nombre: "valida_hasta", etiqueta: "Válida hasta (AAAA-MM-DD, opcional)" }], si: "Guardar memoria" });
    if (!datos) return;
    await enviar("/api/repo/memorias/nueva", { repo: ruta, sistema: s.id, slug: slug(datos.titulo), ...datos });
    avisar("Memoria guardada");
    recargar();
  };

  const fila = (s, m) => {
    const [texto, tono] = ESTADOS[m.status] || [m.status || "sin status", "mal"];
    return h("li", { style: "flex-direction:column;align-items:stretch" },
      h("div", { class: "fila separada" }, h("span", {}, h("b", { texto: m.titulo }),
        h("div", { class: "tenue", texto: `${m.id} · ${m.autor === "agente" ? "propuesta por el asistente" : "de la persona"}${m.fecha ? ` · ${m.fecha}` : ""}` })),
      h("span", { class: "fila" }, m.caducada ? insignia("caducada", "mal") : null, insignia(texto, tono))),
      h("details", {}, h("summary", { texto: "Ver" }), h("pre", { texto: m.contenido })),
      estado.registrado && m.status !== "archivada" ? h("div", { class: "acciones" },
        m.status === "propuesta" ? boton("Aprobar", accion("/api/repo/memorias/aprobar", s, m, "Memoria aprobada"), { clase: "primario pequeno" }) : null,
        boton("Archivar", accion("/api/repo/memorias/archivar", s, m, "Memoria archivada"), { clase: "pequeno" })) : null);
  };

  return h("div", { class: "pila" },
    h("p", { class: "tenue", texto: "Lo que el asistente y tú acordáis recordar de este proyecto. El asistente lee las vigentes al usar cada sistema y solo puede proponer nuevas; tú decides." }),
    pendientes ? h("div", { class: "banda aviso" }, `${pendientes} memoria(s) propuesta(s) por el asistente esperan tu decisión.`) : null,
    sistemas.map((s) => h("div", { class: "tarjeta pila" },
      h("div", { class: "fila separada" }, h("h3", { texto: s.titulo }),
        estado.registrado ? boton("Nueva memoria", nueva(s), { clase: "pequeno" }) : null),
      s.memorias.length ? h("ul", { class: "lista" }, s.memorias.map((m) => fila(s, m)))
        : h("p", { class: "tenue", texto: "Sin memorias todavía." }))));
}
