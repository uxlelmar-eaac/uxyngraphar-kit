// Conexiones: tus agentes de IA y la IA del Creador. Conectar un agente a un proyecto le da las instrucciones de
// uxyngraphar y registra uxyngraphar como servidor MCP (solo lectura) para que consulte tus sistemas por sí mismo.

import { obtener, enviar, nombreDe } from "../api.js";
import { h, vaciar, cabecera, boton, insignia, avisar, dialogo, elegirVarios, confirmar } from "../ui.js";

export async function vista(params, { recargar }) {
  const [datos, lista, cuenta] = await Promise.all([
    obtener("/api/conexiones"),
    obtener("/api/proyectos"),
    obtener("/api/cuenta").catch(() => null),
  ]);
  const existentes = lista.filter((p) => p.existe);

  async function elegir(agente, accion) {
    const opciones = (accion === "desconectar" ? lista.filter((p) => agente.proyectos.includes(p.ruta)) : existentes)
      .map((p) => ({ valor: p.ruta, titulo: p.nombre || nombreDe(p.ruta), detalle: p.ruta }));
    const marcados = accion === "desconectar" ? agente.proyectos : opciones.map((o) => o.valor).filter((r) => !agente.proyectos.includes(r));
    if (!opciones.length) {
      avisar(accion === "conectar" ? "Añade antes un proyecto en «Mis proyectos» e instala algún sistema." : "No está conectado a ningún proyecto.", "mal");
      return;
    }
    const sel = elegirVarios(opciones, marcados);
    const elegidos = await dialogo({
      titulo: `${accion === "conectar" ? "Conectar" : "Desconectar"} ${agente.nombre}`,
      contenido: h("div", { class: "pila" },
        h("p", { class: "tenue", texto: accion === "conectar"
          ? `En cada proyecto se añaden las instrucciones de uxyngraphar a ${agente.instrucciones}` + (agente.mcp ? " y se registra uxyngraphar como servidor MCP para este agente." : ".")
          : "Se quita la entrada de uxyngraphar de su configuración. Tus sistemas y tu trabajo no se tocan." }),
        sel.nodo),
      acciones: [{ texto: accion === "conectar" ? "Conectar" : "Desconectar", clase: accion === "conectar" ? "primario" : "peligro", accion: () => sel.valores() }],
    });
    if (!elegidos?.length) return;
    await enviar(`/api/conexiones/${accion}`, { agente: agente.id, proyectos: elegidos });
    avisar(`${agente.nombre}: ${accion === "conectar" ? "conectado" : "desconectado"} (${elegidos.length})`);
    recargar();
  }

  const tarjetaAgente = (a) => h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("h3", { texto: a.nombre }),
      a.detectado ? insignia("en este equipo", "bien") : insignia("no detectado")),
    h("p", { class: "tenue", texto: a.proyectos.length
      ? `Conectado en: ${a.proyectos.map(nombreDe).join(", ")}`
      : "Aún no está conectado a ningún proyecto." }),
    h("ul", { class: "detalles-conexion" },
      h("li", { texto: `Instrucciones: ${a.instrucciones}` }),
      h("li", { texto: a.mcp ? "Consulta tus sistemas con MCP: sí" : "MCP: configúralo a mano (abajo)" })),
    h("div", { class: "acciones" },
      boton("Conectar", () => elegir(a, "conectar"), { clase: "primario pequeno", icono: "mas" }),
      a.proyectos.length ? boton("Desconectar", () => elegir(a, "desconectar"), { clase: "pequeno" }) : null));

  const detectados = datos.agentes.filter((a) => a.detectado);
  const otros = datos.agentes.filter((a) => !a.detectado);
  const manual = JSON.stringify({ mcpServers: { uxyngraphar: datos.mcp_manual } }, null, 2);

  return h("div", {},
    cabecera("Conexiones", "Conecta tus agentes de IA con tus proyectos para que sigan tus sistemas de gobernanza."),
    h("div", { class: "tarjeta pila" },
      h("div", { class: "fila separada" }, h("h2", { texto: "Asistente del Creador" }),
        cuenta?.tipo === "sesion" ? insignia("conectado", "bien") : insignia("sin cuenta", "nota")),
      h("p", { class: "tenue", texto: cuenta?.tipo === "sesion"
        ? `Usa tu cuenta ${cuenta.usuario || ""}: tu clave de IA o la IA incluida. Lo encuentras en «Creador de sistemas».`
        : "Inicia sesión en «Herramienta y ajustes» para usar el agente del Creador. Sin cuenta, el chat puede usar Ollama o LM Studio en este equipo." })),
    h("h2", { texto: "Tus agentes" }),
    detectados.length ? h("div", { class: "rejilla" }, detectados.map(tarjetaAgente))
      : h("p", { class: "tenue", texto: "No encontré agentes instalados en este equipo. Puedes conectarlos igualmente:" }),
    otros.length ? h("details", { class: "tarjeta" }, h("summary", { texto: `Otros agentes (${otros.length})` }),
      h("div", { class: "rejilla", style: "margin-top:12px" }, otros.map(tarjetaAgente))) : null,
    h("details", { class: "tarjeta" }, h("summary", { texto: "Configurar MCP a mano (cualquier agente)" }),
      h("p", { class: "tenue", texto: "Si tu agente admite servidores MCP, añade esta entrada a su configuración. Es de solo lectura: buscar sistemas, ver los del proyecto y leerlos." }),
      h("pre", { class: "informe", texto: manual }),
      boton("Copiar", async () => { await navigator.clipboard.writeText(manual); avisar("Copiado"); }, { clase: "pequeno" })));
}
