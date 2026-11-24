// Conexiones: tus agentes de IA y la IA del Creador. Conectar un agente a un proyecto le da las instrucciones de
// uxyngraphar y registra uxyngraphar como servidor MCP (solo lectura) para que consulte tus sistemas por sí mismo.

import { obtener, enviar, nombreDe } from "../api.js";
import { h, vaciar, cabecera, boton, insignia, avisar, dialogo, elegirVarios, confirmar } from "../ui.js";

export async function vista(params, { recargar }) {
  const [datos, lista, cuenta, subs] = await Promise.all([
    obtener("/api/conexiones"),
    obtener("/api/proyectos"),
    obtener("/api/cuenta").catch(() => null),
    obtener("/api/ia/suscripciones").catch(() => null),
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

  function abrirUrl(url) {
    if (url) window.open(url, "_blank", "noopener,noreferrer");
  }

  async function iniciarSesionCli(s) {
    let estado;
    try {
      estado = await enviar("/api/ia/suscripciones/iniciar", { proveedor: s.proveedor });
    } catch (e) {
      avisar(e?.message || `No se pudo iniciar sesión en ${s.nombre}`, "mal");
      return;
    }
    const contenedor = h("div", { class: "pila" });
    let vivo = true;
    let temporizador = null;

    function pintar(est) {
      const nodos = [];
      if (est.estado === "listo") {
        nodos.push(h("div", { class: "banda acento", style: "display:block" },
          h("strong", { texto: "Sesión iniciada. " }), `Ya puedes elegir ${s.nombre} en «Creador de sistemas».`));
      } else if (est.estado === "error") {
        nodos.push(h("div", { class: "banda aviso", style: "display:block" },
          h("strong", { texto: "No se completó el inicio de sesión: " }),
          est.error || `prueba a ejecutar «${s.iniciar_sesion}» en una terminal.`));
      } else {
        nodos.push(h("p", { class: "tenue", texto: est.url
          ? "Se abrió la página del proveedor en tu navegador. Completa el inicio de sesión allí y vuelve aquí."
          : `Esperando enlace de inicio de sesión de ${s.nombre}…` }));
      }
      if (est.codigo) {
        nodos.push(h("div", { class: "banda acento fila separada" },
          h("span", {}, "Código: ", h("strong", { style: "font-size:1.15em;letter-spacing:0.08em", texto: est.codigo })),
          boton("Copiar código", async () => { await navigator.clipboard.writeText(est.codigo); avisar("Código copiado"); }, { clase: "pequeno" })));
      }
      if (est.url) {
        nodos.push(h("div", { class: "acciones" },
          boton("Abrir página de inicio de sesión", () => abrirUrl(est.url), { clase: "primario pequeno" }),
          boton("Copiar enlace", async () => { await navigator.clipboard.writeText(est.url); avisar("Enlace copiado"); }, { clase: "pequeno" })));
      }
      if (est.salida?.length) {
        nodos.push(h("pre", { class: "informe", texto: est.salida.join("\n") }));
      }
      vaciar(contenedor, nodos);
    }

    pintar(estado);
    if (estado.estado === "listo") avisar(`${s.nombre}: sesión iniciada`, "bien");

    const sondear = async () => {
      if (!vivo || estado.estado !== "en_curso") return;
      try {
        estado = await obtener(`/api/ia/suscripciones/estado?id=${encodeURIComponent(estado.id)}`);
        if (!vivo) return;
        pintar(estado);
        if (estado.estado === "listo") {
          avisar(`${s.nombre}: sesión iniciada`, "bien");
          return;
        }
        if (estado.estado === "en_curso") temporizador = setTimeout(sondear, 1200);
      } catch {
        if (vivo) temporizador = setTimeout(sondear, 2000);
      }
    };
    if (estado.estado === "en_curso") temporizador = setTimeout(sondear, 1000);

    await dialogo({
      titulo: `Iniciar sesión en ${s.nombre}`,
      contenido: contenedor,
      cancelar: "Cerrar",
      acciones: s.url_claves ? [{ texto: "Abrir página de claves", clase: "pequeno", accion: () => { abrirUrl(s.url_claves); return false; } }] : [],
    });
    vivo = false;
    if (temporizador) clearTimeout(temporizador);
    if (estado.estado === "en_curso") {
      enviar("/api/ia/suscripciones/cancelar", { id: estado.id }).catch(() => {});
    }
  }

  // Suscripciones en este equipo (ADR 0014): la CLI oficial de cada proveedor responde con tu sesión.
  const tarjetaSuscripcion = (s) => h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("h3", { texto: s.nombre }),
      h("div", { class: "fila" },
        insignia(`riesgo ${s.riesgo}`, s.riesgo === "bajo" ? "bien" : "nota"),
        s.instalada ? insignia("en este equipo", "bien") : insignia("no instalada"))),
    h("p", { class: "tenue", texto: s.planes }),
    h("div", { class: s.riesgo === "bajo" ? "banda acento" : "banda aviso", style: "display:block" },
      h("strong", { texto: s.riesgo === "bajo" ? "Cómo funciona: " : "Antes de usar tu suscripción: " }), s.aviso),
    h("p", { class: "tenue", texto: `Comando de sesión: ${s.iniciar_sesion}` }),
    h("div", { class: "acciones" },
      s.instalada
        ? boton("Iniciar sesión", () => iniciarSesionCli(s), { clase: "primario pequeno" })
        : (s.url_instalar ? boton("Instalar CLI", () => abrirUrl(s.url_instalar), { clase: "primario pequeno" }) : null),
      s.url_claves ? boton("Abrir clave en la web", () => abrirUrl(s.url_claves), { clase: "pequeno" }) : null,
      boton("Copiar comando", async () => { await navigator.clipboard.writeText(s.iniciar_sesion.split("  ")[0]); avisar("Copiado"); }, { clase: "pequeno fantasma" })));

  const tarjetaWeb = (w) => h("div", { class: "tarjeta tarjeta-item" },
    h("div", { class: "fila separada" }, h("h3", { texto: w.nombre }),
      insignia(`riesgo ${w.riesgo}`, w.riesgo === "bajo" ? "bien" : "nota")),
    h("p", { class: "tenue", texto: w.planes }),
    h("div", { class: w.riesgo === "bajo" ? "banda acento" : "banda aviso", style: "display:block" },
      h("strong", { texto: "Cómo funciona: " }), w.aviso),
    h("div", { class: "acciones" },
      boton("Abrir clave en la web", () => abrirUrl(w.url_claves), { clase: "primario pequeno" }),
      subs?.url_cuenta_ia ? boton("Pegar en mi cuenta", () => abrirUrl(subs.url_cuenta_ia), { clase: "pequeno" }) : null));

  const seccionSuscripciones = subs ? h("div", { class: "pila" },
    h("h2", { texto: "Tus suscripciones de IA" }),
    h("p", { class: "tenue", texto: "Inicia sesión con un botón en las CLI instaladas en tu equipo, o abre directamente la página web del proveedor para obtener tu clave y pegarla en tu cuenta." }),
    h("div", { class: "rejilla" }, subs.disponibles.map(tarjetaSuscripcion)),
    subs.web?.length ? h("h3", { texto: "Planes y suscripciones por clave en la web" }) : null,
    subs.web?.length ? h("div", { class: "rejilla" }, subs.web.map(tarjetaWeb)) : null,
    subs.no_permitidas.map((n) => h("div", { class: "banda aviso", style: "display:block" },
      h("strong", { texto: `${n.nombre}: no disponible. ` }), n.motivo)),
    h("p", { class: "tenue", texto: `Términos revisados el ${subs.revisado}.` })) : null;

  const detectados = datos.agentes.filter((a) => a.detectado);
  const otros = datos.agentes.filter((a) => !a.detectado);
  const manual = JSON.stringify({ mcpServers: { uxyngraphar: datos.mcp_manual } }, null, 2);

  return h("div", {},
    cabecera("Conexiones", "Conecta tus agentes de IA con tus proyectos para que sigan tus sistemas de gobernanza."),
    h("div", { class: "tarjeta pila" },
      h("div", { class: "fila separada" }, h("h2", { texto: "uxyn" }),
        cuenta?.tipo === "sesion" ? insignia("conectado", "bien") : insignia("sin cuenta", "nota")),
      h("p", { class: "tenue", texto: cuenta?.tipo === "sesion"
        ? `Usa tu cuenta ${cuenta.usuario || ""}: tu clave de IA o la IA incluida. uxyn está en «Creador de sistemas».`
        : "Inicia sesión en «Cuenta» para usar uxyn, el agente del Creador. Sin cuenta, el chat puede usar Ollama, LM Studio o tus suscripciones de este equipo." })),
    seccionSuscripciones,
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
