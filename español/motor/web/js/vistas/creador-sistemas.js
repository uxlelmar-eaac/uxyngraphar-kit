// Pantalla «Creador de sistemas»: tres zonas que se pueden ocultar para centrarse en lo que importa en cada momento.
//   izquierda  · Mis sistemas (catálogo local + borradores de la web)
//   centro     · el sistema abierto (lo básico, piezas, archivos, versión y publicar)
//   derecha    · el chat con el agente del Creador
// Qué zonas están visibles se recuerda en este navegador (si el navegador lo permite).

import { catalogo } from "../api.js";
import { h, vaciar, boton, cabecera, insignia, vacio, icono } from "../ui.js";
import { editorSistema, crearSistema, FAMILIAS } from "./creador-editor.js";
import { chatAgente, tarjetaCreador } from "./creador.js";
import { inicioConAgente } from "./creador-inicio.js";

const CLAVE = "uxyn-creador-zonas";
export const ZONAS = [
  ["lista", "Mis sistemas"],
  ["sistema", "Sistema"],
  ["agente", "Agente"],
];

export function leerZonas() {
  const defecto = { lista: true, sistema: true, agente: true };
  try {
    const guardado = JSON.parse(localStorage.getItem(CLAVE) || "{}");
    const zonas = { ...defecto, ...guardado };
    return Object.values(zonas).some(Boolean) ? zonas : defecto;
  } catch {
    return defecto;
  }
}

function guardarZonas(zonas) {
  try { localStorage.setItem(CLAVE, JSON.stringify(zonas)); } catch { /* sin almacenamiento: solo dura esta visita */ }
}

export async function vista(params, { ir }) {
  const zonas = leerZonas();
  const idAbierto = params.id || "";
  let abierto = null;

  const marco = h("div", { class: "creador" });
  const zonaLista = h("section", { class: "zona zona-lista", "aria-label": "Mis sistemas" });
  const zonaSistema = h("section", { class: "zona zona-sistema", "aria-label": "Sistema abierto" });
  const zonaAgente = h("section", { class: "zona zona-agente", "aria-label": "Agente del Creador" });
  const nodos = { lista: zonaLista, sistema: zonaSistema, agente: zonaAgente };

  const interruptores = ZONAS.map(([clave, nombre]) => {
    const b = h("button", { type: "button", class: "boton pequeno conmutador", "aria-pressed": String(zonas[clave]), "aria-controls": `zona-${clave}`,
      title: `Mostrar u ocultar «${nombre}»` }, nombre);
    b.addEventListener("click", () => {
      const visibles = ZONAS.filter(([k]) => zonas[k]).length;
      if (zonas[clave] && visibles === 1) return;   // siempre queda al menos una zona
      zonas[clave] = !zonas[clave];
      guardarZonas(zonas);
      aplicar();
    });
    return b;
  });
  function aplicar() {
    for (const [clave] of ZONAS) {
      nodos[clave].id = `zona-${clave}`;
      nodos[clave].hidden = !zonas[clave];
    }
    interruptores.forEach((b, i) => b.setAttribute("aria-pressed", String(zonas[ZONAS[i][0]])));
    marco.dataset.zonas = ZONAS.filter(([k]) => zonas[k]).map(([k]) => k).join(" ");
  }

  const abrir = (id, conversacion) => ir("creador", id ? { id, ...(conversacion ? { conversacion } : {}) } : null);
  async function nuevo() {
    const r = await crearSistema();
    if (!r) return;
    if (typeof r === "string") abrir(r);
    else abrir(r.id, r.conversacion);
  }

  // Izquierda: lista de sistemas locales con buscador y borradores de la web.
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
    vaciar(zonaLista,
      h("div", { class: "fila separada" }, h("h2", { texto: "Mis sistemas" }), boton("Crear", nuevo, { clase: "pequeno primario", icono: "mas" })),
      filtro, lista,
      await tarjetaCreador({ alTraer: async (r, slug) => abrir(r?.id || slug) }));
  }

  // Centro: el sistema abierto.
  async function pintarSistema() {
    if (!idAbierto) {
      const inicio = inicioConAgente({ alCrear: (id, r) => abrir(id, r.conversacion) });
      vaciar(zonaSistema, h("div", { class: "tarjeta pila" }, inicio.nodo),
        h("p", { class: "tenue" }, "Un sistema reúne lo que tus agentes deben saber y seguir para resolver un tipo de problema. También puedes abrir uno desde «Mis sistemas» o ",
          boton("crearlo paso a paso", nuevo, { clase: "pequeno", icono: "mas" })));
      return;
    }
    const meta = (await catalogo()).find((m) => m.id === idAbierto);
    if (!meta) {
      vaciar(zonaSistema, h("div", { class: "banda mal", texto: `No encuentro «${idAbierto}» en este equipo.` }));
      return;
    }
    abierto = await editorSistema(idAbierto, { alCambiar: () => pintarLista() });
    vaciar(zonaSistema, h("div", { class: "fila separada" }, h("h2", { texto: meta.titulo || meta.id }), h("code", { class: "tenue", texto: meta.id })), abierto.nodo);
  }

  // Derecha: chat con el agente.
  async function pintarAgente() {
    vaciar(zonaAgente, h("h2", {}, icono("chat"), " Agente"),
      await chatAgente(() => (abierto ? { id: idAbierto, rutaActual: abierto.rutaActual, textarea: abierto.textarea, recargar: abierto.recargar } : null),
        { conversacionInicial: Number(params.conversacion) || null, slugInicial: idAbierto || null }));
  }

  aplicar();
  marco.append(zonaLista, zonaSistema, zonaAgente);
  await Promise.all([pintarLista(), pintarSistema()]);
  await pintarAgente();
  return h("div", {},
    cabecera("Creador de sistemas", "Crea y mejora tus sistemas de gobernanza a mano o conversando con el agente.",
      h("div", { class: "fila", role: "group", "aria-label": "Zonas visibles" }, interruptores)),
    marco);
}
