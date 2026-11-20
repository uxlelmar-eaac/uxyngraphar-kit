// Estructura de un sistema: qué es cada pieza (archivos del núcleo y carpetas del esqueleto) y cuántas carpetas y
// archivos tiene. La usa la revisión de archivos. Igual que la web (uxyngraphar-frontend, creator/systemStructure.ts).

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
