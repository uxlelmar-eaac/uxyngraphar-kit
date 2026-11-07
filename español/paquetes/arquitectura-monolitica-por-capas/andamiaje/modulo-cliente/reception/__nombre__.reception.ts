import type { {{Nombre}}Response, {{Nombre}}View } from '../types/{{nombre}}.types';

export function to{{Nombre}}View(response: {{Nombre}}Response): {{Nombre}}View {
  return { id: response.id, label: response.id };
}
