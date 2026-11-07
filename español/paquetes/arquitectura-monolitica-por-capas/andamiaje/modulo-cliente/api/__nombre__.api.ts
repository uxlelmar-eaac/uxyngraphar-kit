import type { {{Nombre}}Response } from '../types/{{nombre}}.types';

export async function fetch{{Nombre}}(baseUrl: string, id: string): Promise<{{Nombre}}Response> {
  const response = await fetch(`${baseUrl}/{{nombre}}/${id}`);
  if (!response.ok) throw new Error(`{{nombre}}: ${response.status}`);
  return response.json();
}
