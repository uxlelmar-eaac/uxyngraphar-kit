// Pantalla «Creador de sistemas»: dos trabajos distintos, nunca mezclados.
//   crear  · sin sistema abierto → hero «Crea un sistema» (+ lista opcional); sin chat del agente
//   editar · sistema abierto → editor + un chat del Asistente; lista opcional
// Qué zonas están visibles se recuerda en este navegador (si el navegador lo permite).

import { catalogo } from "../api.js";
import { h, vaciar, boton, cabecera, insignia, icono } from "../ui.js";
import { editorSistema, crearSistema, FAMILIAS } from "./creador-editor.js";
import { chatAgente, tarjetaCreador } from "./creador.js";
import { inicioConAgente } from "./creador-inicio.js";

const CLAVE = "uxyn-creador-zonas-v2";
export const ZONAS = [
  ["lista", "Mis sistemas"],
  ["sistema", "Sistema"],
  ["agente", "Agente"],
];

/** Defaults distintos por modo: en crear no hay chat; en editar priorizamos editor + agente. */
export function leerZonas(modo = "editar") {
  const defecto = modo === "crear"
    ? { lista: true, sistema: true, agente: false }
    : { lista: false, sistema: true, agente: true };
  try {
    const guardado = JSON.parse(localStorage.getItem(CLAVE) || "{}");
    const zonas = { ...defecto, ...guardado };
    if (modo === "crear") zonas.agente = false;   // nunca chat al crear
    return Object.values(zonas).some(Boolean) ? zonas : defecto;
  } catch {
    return defecto;
  }
}

function guardarZonas(zonas) {
  try { localStorage.setItem(CLAVE, JSON.stringify(zonas)); } catch { /* sin almacenamiento: solo dura esta visita */ }
}

export async function vista(params, { ir }) {
  const idAbierto = params.id || "";
  const modo = idAbierto ? "editar" : "crear";
  const zonas = leerZonas(modo);
  let abierto = null;

  const marco = h("div", { class: "creador", "data-modo": modo });
  const zonaLista = h("section", { class: "zona zona-lista", "aria-label": "Mis sistemas" });
  const zonaSistema = h("section", { class: "zona zona-sistema", "aria-label": modo === "crear" ? "Crear sistema" : "Sistema abierto" });
  const zonaAgente = h("section", { class: "zona zona-agente", "aria-label": "Agente del Creador" });
  const nodos = { lista: zonaLista, sistema: zonaSistema, agente: zonaAgente };

  // En crear solo se conmutan lista y sistema; en editar las tres.
  const clavesToggle = modo === "crear" ? ZONAS.filter(([k]) => k !== "agente") : ZONAS;
  const interruptores = clavesToggle.map(([clave, nombre]) => {
    const b = h("button", { type: "button", class: "boton pequeno conmutador", "aria-pressed": String(zonas[clave]), "aria-controls": `zona-${clave}`,
      title: `Mostrar u ocultar «${nombre}»` }, nombre);
    b.addEventListener("click", () => {
      const visibles = ZONAS.filter(([k]) => zonas[k]).length;
      if (zonas[clave] && visibles === 1) return;
      if (modo === "crear" && clave === "agente") return;
      zonas[clave] = !zonas[clave];
      if (modo === "crear") zonas.agente = false;
      guardarZonas(zonas);
      aplicar();
    });
    return b;
  });
  function aplicar() {
    if (modo === "crear") zonas.agente = false;
    for (const [clave] of ZONAS) {
      nodos[clave].id = `zona-${clave}`;
      nodos[clave].hidden = !zonas[clave];
    }
    interruptores.forEach((b, i) => b.setAttribute("aria-pressed", String(zonas[clavesToggle[i][0]])));
    marco.dataset.zonas = ZONAS.filter(([k]) => zonas[k]).map(([k]) => k).join(" ");
    marco.dataset.modo = modo;
  }

  const abrir = (id, conversacion) => ir("creador", id ? { id, ...(conversacion ? { conversacion } : {}) } : null);
  async function nuevo() {
    const r = await crearSistema();
    if (!r) return;
    if (typeof r === "string") abrir(r);
    else abrir(r.id, r.conversacion);
  }

  async function pintarLista() {
    const cat = await catalogo(true);
    const filtro = h("input", { type: "search", placeholder: "Buscar", "aria-label": "Buscar en mis sistemas" });
    const lista = h("ul", { class: "lista lista-sistemas" });
    const pintar = () => {
      const t = filtro.value.trim().toLowerCase();
      const visibles = cat.filter((m) => !t || `${m.titulo} ${m.id} ${m.descripcion}`.toLowerCase().includes(t));
      vaciar(lista, visibles.map((m) => h("li", {},
        h("a", { href: `#/creador?id=${encodeURIComponent(m.id)}`, class: "elemento-sistema" + (m.id === idAbierto ? " activo" : ""),
          "aria-current": m.id === idAbierto ? "page" : null },
          h("b", { texto: m.titulo || m.id }),
          h("span", { class: "tenue", texto: `${FAMILIAS[m.familia] || m.familia || ""} · ${m.version || ""}` }),
          (m.errores || []).length ? insignia("le falta algo", "nota") : null))));
      if (!visibles.length) lista.append(h("li", { class: "tenue", texto: cat.length ? "Nada coincide." : "Aún no tienes sistemas." }));
    };
    filtro.addEventListener("input", pintar);
    pintar();
    const cabLista = modo === "crear"
      ? h("div", { class: "fila separada" }, h("h2", { texto: "Abrir uno existente" }), boton("Paso a paso", nuevo, { clase: "pequeno", icono: "mas", titulo: "Crear sin el agente" }))
      : h("div", { class: "fila separada" },
          h("h2", { texto: "Mis sistemas" }),
          h("div", { class: "fila" },
            boton("Nuevo", () => abrir(""), { clase: "pequeno", icono: "mas", titulo: "Volver a crear un sistema" }),
            boton("Paso a paso", nuevo, { clase: "pequeno", titulo: "Crear sin el agente" })));
    vaciar(zonaLista, cabLista, filtro, lista,
      await tarjetaCreador({ alTraer: async (r, slug) => abrir(r?.id || slug) }));
  }

  async function pintarSistema() {
    if (!idAbierto) {
      const inicio = inicioConAgente({ alCrear: (id, r) => abrir(id, r.conversacion) });
      vaciar(zonaSistema,
        h("div", { class: "tarjeta pila inicio" }, inicio.nodo),
        h("p", { class: "tenue inicio-ayuda" },
          "Un sistema reúne lo que tus agentes deben saber y seguir. El botón primario es ",
          h("b", { texto: "Crear" }),
          ". Después revisarás las propuestas del agente. También puedes ",
          boton("crearlo paso a paso", nuevo, { clase: "pequeno" }),
          " o abrir uno desde la lista."));
      return;
    }
    const meta = (await catalogo()).find((m) => m.id === idAbierto);
    if (!meta) {
      vaciar(zonaSistema, h("div", { class: "banda mal", texto: `No encuentro «${idAbierto}» en este equipo.` }),
        h("p", {}, boton("Volver a crear", () => abrir(""), { clase: "pequeno" })));
      return;
    }
    abierto = await editorSistema(idAbierto, { alCambiar: () => pintarLista() });
    vaciar(zonaSistema,
      h("div", { class: "fila separada" },
        h("div", {}, h("h2", { texto: meta.titulo || meta.id }), h("code", { class: "tenue", texto: meta.id })),
        boton("Crear otro", () => abrir(""), { clase: "pequeno", titulo: "Volver a la pantalla de crear" })),
      abierto.nodo);
  }

  async function pintarAgente() {
    if (modo === "crear") {
      vaciar(zonaAgente);   // no se muestra; evita un segundo chat frente a «Crear»
      return;
    }
    vaciar(zonaAgente,
      h("h2", {}, icono("chat"), " Asistente"),
      h("p", { class: "tenue", texto: "Revisa, rellena o mejora el sistema abierto. Los cambios llegan como propuestas: tú decides." }),
      await chatAgente(() => (abierto ? { id: idAbierto, rutaActual: abierto.rutaActual, textarea: abierto.textarea, recargar: abierto.recargar } : null),
        { conversacionInicial: Number(params.conversacion) || null, slugInicial: idAbierto || null }));
  }

  aplicar();
  marco.append(zonaLista, zonaSistema, zonaAgente);
  await Promise.all([pintarLista(), pintarSistema()]);
  await pintarAgente();
  const sub = modo === "crear"
    ? "Cuenta tu idea o sube archivos. El agente arma el sistema y tú decides qué aceptar."
    : "Edita a mano o pide cambios al asistente. Nada se guarda sin que lo aceptes.";
  return h("div", {},
    cabecera(modo === "crear" ? "Crear un sistema" : "Creador de sistemas", sub,
      h("div", { class: "fila", role: "group", "aria-label": "Zonas visibles" }, interruptores)),
    marco);
}
