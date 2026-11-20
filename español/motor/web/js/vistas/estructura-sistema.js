// Estructura de un sistema: qué es cada pieza (archivos del núcleo y carpetas del esqueleto), cuántas carpetas y
// archivos tiene y a qué capa de uxyngraphar pertenece cada ruta. La usa la revisión de archivos. Igual que la web
// (uxyngraphar-frontend, creator/systemStructure.ts).

/** Qué es cada pieza conocida de un sistema de gobernanza (archivos del núcleo y carpetas del esqueleto). */
export const QUE_ES = {
  "sistema.json": "Manifiesto: título, alcance, permisos y cuándo se activa",
  "README.md": "Presentación para quien lo instala",
  "SISTEMA.md": "Qué garantiza, cuándo se usa y qué deja",
  "LIMITES.md": "Reglas duras y cuándo parar a preguntar",
  "PERMISOS.md": "Qué hace el agente solo y qué decide la persona",
  "MEMORIAS.md": "Qué recordar entre conversaciones",
  "HERRAMIENTAS.md": "Herramientas y scripts que puede usar",
  "CHANGELOG.md": "Historial de versiones",
  proceso: "Fases del trabajo, en orden",
  skills: "Habilidades que el agente puede invocar",
  prompts: "Instrucciones reutilizables",
  config: "Ajustes que la persona puede cambiar",
  plantillas: "Documentos que el agente rellena",
  referencia: "Material de consulta",
  ejemplos: "Casos resueltos de muestra",
  pruebas: "Comprobaciones del sistema",
  scripts: "Scripts que el sistema ejecuta",
};

/** Cuántas carpetas y archivos tiene una lista de rutas. */
export function contarEstructura(rutas) {
  const carpetas = new Set();
  for (const r of rutas) {
    const partes = r.split("/");
    for (let i = 1; i < partes.length; i++) carpetas.add(partes.slice(0, i).join("/"));
  }
  return { carpetas: carpetas.size, archivos: rutas.length };
}

// ── Capas de uxyngraphar ───────────────────────────────────────────────────────────────────────────────────────
// Qué parte de un sistema pone el marco de uxyngraphar y qué es propio del sistema. Las mismas listas que
// `_base/scripts/comun/uxyn_base.py` (NUCLEO, INTEGRIDAD y PIEZAS) y que la web (creator/systemStructure.ts).

/** Archivos del núcleo: todo sistema los tiene (más la huella de integridad). */
export const NUCLEO = ["sistema.json", "README.md", "SISTEMA.md", "MEMORIAS.md", "LIMITES.md", "PERMISOS.md", "INTEGRIDAD.json"];
/** Rutas de las piezas estándar (opcionales, de forma fija). */
export const PIEZAS = ["proceso", "skills", "COMPONENTES.md", "HERRAMIENTAS.md", "andamiaje", "plantillas", "referencia",
  "ejemplos", "pruebas", "CHANGELOG.md"];
/** Scripts comunes que el generador copia igual en todos los sistemas. */
export const COMUN = "scripts/comun";

export const CAPAS = {
  nucleo: { nombre: "Núcleo", que: "Lo que todo sistema de uxyngraphar tiene: manifiesto, presentación, alcance, memorias, límites y permisos" },
  estandar: { nombre: "Estándar", que: "Piezas estándar de uxyngraphar (proceso, skills, plantillas…): forma fija, contenido de este sistema" },
  comun: { nombre: "Común", que: "Scripts comunes del motor de uxyngraphar, iguales en todos los sistemas: no se editan a mano" },
  propio: { nombre: "Propio", que: "Extensiones y archivos propios de este sistema" },
};

/** A qué capa pertenece una ruta (archivo o carpeta): «nucleo», «estandar», «comun» o «propio». */
export function capaDe(rel) {
  const ruta = String(rel || "").replace(/\/+$/, "");
  if (NUCLEO.includes(ruta)) return "nucleo";
  if (ruta === "scripts" || ruta === COMUN || ruta.startsWith(`${COMUN}/`)) return "comun";
  const primera = ruta.split("/")[0];
  if (PIEZAS.includes(primera)) return "estandar";
  return "propio";
}

/** Cuántos archivos hay de cada capa. */
export function contarCapas(rutas) {
  const n = { nucleo: 0, estandar: 0, comun: 0, propio: 0 };
  for (const r of rutas) n[capaDe(r)] += 1;
  return n;
}
