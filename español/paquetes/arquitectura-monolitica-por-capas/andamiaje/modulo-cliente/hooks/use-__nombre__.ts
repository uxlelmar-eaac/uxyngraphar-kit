import { fetch{{Nombre}} } from '../api/{{nombre}}.api';
import { to{{Nombre}}View } from '../reception/{{nombre}}.reception';
import { {{nombreCamel}}QueryKeys } from '../model/{{nombre}}.query-keys';
import type { {{Nombre}}View } from '../types/{{nombre}}.types';

// Orquesta api + reception. Conecta aquí la librería de estado remoto del proyecto.
export async function load{{Nombre}}(baseUrl: string, id: string): Promise<{ key: readonly string[]; view: {{Nombre}}View }> {
  return { key: {{nombreCamel}}QueryKeys.detail(id), view: to{{Nombre}}View(await fetch{{Nombre}}(baseUrl, id)) };
}
