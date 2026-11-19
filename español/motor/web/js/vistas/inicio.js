// Inicio: sistemas en curso + siguiente paso del ciclo (ADR 0015).

import { obtener, enviar, catalogo } from "../api.js";
import { h, cabecera, boton, insignia, avisar } from "../ui.js";
import { agregarProyectos } from "../explorador.js";
import { tarjetaProyecto } from "./proyectos.js";
import { resolverEstado, leerOrigen, desdePendientes } from "./creador-estado.js";
import { filtrarPropuestasPendientes } from "./creador.js";

async function tarjetaSistemaEnCurso(m, ir, proyectos, publicado = false) {
  const enProyecto = (proyectos || [])
    .filter((p) => p.existe && (p.sistemas || []).includes(m.id))
    .map((p) => p.nombre);
  let pendientes = desdePendientes(null);
  let propuestas = 0;
  try {
    pendientes = desdePendientes(await obtener("/api/catalogo/pendientes", { id: m.id }));
  } catch { /* */ }
  try {
    const todas = await obtener("/api/agente/propuestas", { slug: m.id });
    propuestas = filtrarPropuestasPendientes(todas).length;
  } catch { /* */ }
  const estado = resolverEstado({
    tieneSistema: true,
    propuestas,
    errores: pendientes.errores,
    marcadores: pendientes.marcadores,
    siguiente: pendientes.siguiente,
    listo: pendientes.listo,
    valido: pendientes.valido,
    alDia: true,
    enEquipo: true,
    enProyecto,
    publicado,
    origen: leerOrigen(m.id),
  });
  return h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" },
      h("div", {}, h("h3", { texto: m.titulo || m.id }), h("code", { class: "tenue", texto: m.id })),
      insignia(estado.ciclo.etiqueta)),
    h("p", { class: "tenue", texto: estado.detalle }),
    estado.ciclo.siguienteCiclo ? h("p", { class: "tenue", texto: estado.ciclo.siguienteCiclo }) : null,
    h("div", { class: "fila" },
      enProyecto.length ? insignia("instalado", "bien") : insignia("equipo", "bien"),
      publicado ? insignia("mercado", "acento") : null,
      (m.errores || []).length ? insignia("le falta algo", "nota") : null),
    h("div", { class: "acciones" },
      boton("Abrir en el taller", () => ir("creador", { id: m.id }), { clase: "primario pequeno" })));
}

export async function vista(_params, { ir }) {
  const [lista, cat, herramienta] = await Promise.all([
    obtener("/api/proyectos"),
    catalogo(true).catch(() => []),
    obtener("/api/herramienta"),
  ]);
  let borradores = [];
  try { borradores = await obtener("/api/creador/borradores"); } catch { /* sin sesión */ }

  const conActualizacion = lista.filter((p) => p.actualizables > 0);
  const alterados = lista.filter((p) => p.alterados > 0);
  const atencion = [...new Set([...alterados, ...conActualizacion])];

  const nueva = h("div", { class: "pila" });
  const BOTON = {
    actualizar: ["Ver cómo actualizar", () => ir("cuenta")],
    reparar: ["Reparar", async (a) => { await enviar("/api/herramienta/reparar", { proyectos: true }); avisar("Reparación hecha"); ir("inicio"); }],
    abrir: ["Abrir", (a) => ir("proyecto", { ruta: a.ruta })],
  };
  obtener("/api/avisos").then((avisos) => {
    nueva.replaceChildren(...avisos.map((a) => h("div", { class: `banda ${a.tipo === "interrumpida" || a.tipo === "flujo" ? "mal" : "acento"}` },
      h("b", { texto: a.mensaje }), h("span", { class: "espacio" }),
      BOTON[a.accion] ? boton(BOTON[a.accion][0], () => BOTON[a.accion][1](a), { clase: "primario pequeno" }) : null)));
  }).catch(() => {});

  const idsLocales = new Set(cat.map((m) => m.id));
  const publicadoDe = (slug) => {
    const b = (borradores || []).find((x) => x.slug === slug);
    return !!(b && (b.version_publicada || b.publicado));
  };
  const soloWeb = (borradores || []).filter((b) => !idsLocales.has(b.slug));
  const enCurso = [
    ...cat.slice(0, 8),
    ...soloWeb.slice(0, 4).map((b) => ({
      id: b.slug,
      titulo: b.titulo || b.slug,
      errores: [],
      soloWeb: true,
      publicado: !!(b.version_publicada || b.publicado),
    })),
  ];

  const rejillaSistemas = h("div", { class: "rejilla" });
  if (enCurso.length) {
    const tarjetas = await Promise.all(enCurso.map(async (m) => {
      if (m.soloWeb) {
        return h("div", { class: "tarjeta tarjeta-item" },
          h("div", { class: "fila separada" },
            h("h3", { texto: m.titulo }),
            h("span", { class: "fila" },
              insignia("web", "acento"),
              m.publicado ? insignia("mercado", "acento") : null)),
          h("p", { class: "tenue", texto: "Borrador en la web. Tráelo al equipo desde el taller." }),
          h("div", { class: "acciones" },
            boton("Abrir en el taller", () => ir("creador", { id: m.id }), { clase: "primario pequeno" })));
      }
      return tarjetaSistemaEnCurso(m, ir, lista, publicadoDe(m.id));
    }));
    rejillaSistemas.append(...tarjetas);
  }

  return h("div", {},
    cabecera("Inicio", "Sistemas en curso y el siguiente paso del ciclo. El objeto es el sistema de gobernanza; uxyn ayuda."),
    nueva,
    h("div", { class: "seccion" },
      h("div", { class: "fila separada" },
        h("h2", { texto: "Sistemas en curso" }),
        boton("Nuevo en el taller", () => ir("creador"), { clase: "pequeno", icono: "mas" })),
      enCurso.length
        ? rejillaSistemas
        : h("div", { class: "tarjeta" },
          h("p", { texto: "Aún no hay sistemas en este equipo." }),
          h("p", { class: "tenue", texto: "Empieza con una idea o un zip en el Taller: verás archivos, origen y salida desde el primer momento." }),
          boton("Ir al taller", () => ir("creador"), { clase: "primario", icono: "creador" }))),
    h("div", { class: "seccion" }, h("h2", { texto: "Atajos" }),
      h("div", { class: "rejilla" },
        boton("Taller", () => ir("creador"), { clase: "grande", icono: "creador" }),
        boton("Añadir un proyecto", async () => { if ((await agregarProyectos()).length) ir("proyectos"); }, { clase: "grande", icono: "mas" }),
        boton("Mercado", () => ir("catalogo"), { clase: "grande", icono: "catalogo" }),
        boton("Flujos guardados", () => ir("flujos"), { clase: "grande", icono: "flujos" }),
      )),
    atencion.length ? h("div", { class: "seccion" }, h("h2", { texto: "Proyectos que necesitan atención" }),
      h("div", { class: "rejilla" }, atencion.map((p) => tarjetaProyecto(p, ir)))) : null,
    !lista.length ? h("div", { class: "seccion tarjeta" }, h("h2", { texto: "Empieza por añadir tus proyectos" }),
      h("p", { class: "tenue", texto: "Elige la carpeta de un proyecto (o una carpeta que contenga varios) y el panel los encontrará." }),
      boton("Añadir proyectos", async () => { if ((await agregarProyectos()).length) ir("proyectos"); }, { clase: "primario", icono: "mas" })) : null,
    h("p", { class: "tenue", style: "margin-top:28px", texto: `uxyngraphar ${herramienta.version}` + (herramienta.instalada ? "" : " · copia del repositorio") }),
  );
}
