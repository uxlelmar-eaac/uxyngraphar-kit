// Bus de logs del panel: un solo historial para el cajón del Creador y la sección «Logs».
// Sin tokens ni secretos; cuerpos resumidos y truncados.

const CLAVE = "uxyn-panel-logs";
const MAX = 500;
const SECRETOS = /^(token|codigo|password|clave|secret|authorization|cookie|sesion|session|api[_-]?key)$/i;
const OMITIR_RUTAS = new Set(["/api/latido", "/api/agente/progreso", "/api/registros"]);

let entradas = [];
const oyentes = new Set();
let seq = 0;

try {
  const crudo = sessionStorage.getItem(CLAVE);
  if (crudo) {
    const lista = JSON.parse(crudo);
    if (Array.isArray(lista)) {
      entradas = lista.slice(0, MAX);
      seq = entradas.reduce((n, e) => Math.max(n, Number(e.id) || 0), 0);
    }
  }
} catch { /* sin almacenamiento */ }

function persistir() {
  try { sessionStorage.setItem(CLAVE, JSON.stringify(entradas.slice(0, 200))); } catch { /* */ }
}

function avisarOyentes() {
  for (const fn of oyentes) {
    try { fn(entradas); } catch { /* oyente roto */ }
  }
}

/** Resume un valor para el log (sin secretos ni textos enormes). */
export function resumir(valor, profundidad = 0) {
  if (valor == null) return valor;
  if (typeof valor === "string") return valor.length > 240 ? `${valor.slice(0, 240)}…[${valor.length}]` : valor;
  if (typeof valor !== "object") return valor;
  if (profundidad > 3) return "[…]";
  if (Array.isArray(valor)) {
    if (valor.length && valor[0] && typeof valor[0] === "object" && ("nombre" in valor[0] || "name" in valor[0])) {
      return valor.slice(0, 20).map((a) => ({
        nombre: a.nombre || a.name,
        chars: typeof a.contenido === "string" ? a.contenido.length : (typeof a.content === "string" ? a.content.length : undefined),
      }));
    }
    return valor.slice(0, 30).map((x) => resumir(x, profundidad + 1));
  }
  const out = {};
  for (const [k, v] of Object.entries(valor)) {
    if (SECRETOS.test(k)) { out[k] = "[oculto]"; continue; }
    if (k === "contenido" || k === "content" || k === "despues" || k === "antes") {
      out[k] = typeof v === "string" ? `[texto ${v.length} chars]` : resumir(v, profundidad + 1);
      continue;
    }
    out[k] = resumir(v, profundidad + 1);
  }
  return out;
}

/**
 * @param {{ nivel?: string, origen?: string, titulo: string, detalle?: string, ruta?: string, ms?: number, ok?: boolean, datos?: unknown }} entrada
 */
export function anotar(entrada) {
  const item = {
    id: ++seq,
    t: new Date().toISOString(),
    nivel: entrada.nivel || "info",
    origen: entrada.origen || "sistema",
    titulo: String(entrada.titulo || ""),
    detalle: entrada.detalle != null ? String(entrada.detalle) : undefined,
    ruta: entrada.ruta,
    ms: entrada.ms,
    ok: entrada.ok,
    datos: entrada.datos !== undefined ? resumir(entrada.datos) : undefined,
  };
  entradas = [item, ...entradas].slice(0, MAX);
  persistir();
  avisarOyentes();
  return item;
}

export function listar({ nivel, origen } = {}) {
  return entradas.filter((e) => (!nivel || e.nivel === nivel) && (!origen || e.origen === origen));
}

export function vaciar() {
  entradas = [];
  persistir();
  avisarOyentes();
}

export function suscribir(fn) {
  oyentes.add(fn);
  return () => oyentes.delete(fn);
}

export function exportarTexto(filtro = {}) {
  return listar(filtro).map((e) => {
    const partes = [`[${e.t}] ${e.nivel.toUpperCase()} ${e.origen} ${e.titulo}`];
    if (e.ruta) partes.push(`  ruta: ${e.ruta}`);
    if (e.ms != null) partes.push(`  ms: ${e.ms}`);
    if (e.ok === false) partes.push("  ok: false");
    if (e.detalle) partes.push(`  ${e.detalle}`);
    if (e.datos !== undefined) {
      try { partes.push(`  datos: ${JSON.stringify(e.datos)}`); } catch { partes.push("  datos: [no serializable]"); }
    }
    return partes.join("\n");
  }).join("\n\n");
}

export function contadorErrores() {
  return entradas.filter((e) => e.nivel === "error").length;
}

export function debeOmitirRuta(ruta) {
  const base = String(ruta || "").split("?")[0];
  return OMITIR_RUTAS.has(base);
}

/** Mezcla eventos del servidor (GET /api/registros) sin duplicar por id de servidor. */
export function incorporarServidor(lista) {
  if (!Array.isArray(lista) || !lista.length) return;
  const vistos = new Set(entradas.filter((e) => e.sid).map((e) => e.sid));
  const nuevos = [];
  for (const e of lista) {
    const sid = e.id != null ? `s${e.id}` : null;
    if (sid && vistos.has(sid)) continue;
    nuevos.push({
      id: ++seq,
      sid,
      t: e.t || new Date().toISOString(),
      nivel: e.nivel || (e.ok === false ? "error" : "info"),
      origen: e.origen || "panel",
      titulo: e.titulo || `${e.metodo || ""} ${e.ruta || ""}`.trim() || "evento panel",
      detalle: e.detalle,
      ruta: e.ruta,
      ms: e.ms,
      ok: e.ok,
      datos: e.datos !== undefined ? resumir(e.datos) : undefined,
    });
  }
  if (!nuevos.length) return;
  entradas = [...nuevos, ...entradas].slice(0, MAX);
  persistir();
  avisarOyentes();
}
