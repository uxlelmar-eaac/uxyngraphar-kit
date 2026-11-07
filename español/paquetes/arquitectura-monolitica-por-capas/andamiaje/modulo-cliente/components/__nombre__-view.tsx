import type { {{Nombre}}View as {{Nombre}}ViewModel } from '../types/{{nombre}}.types';

// UI sin lógica de red: recibe la vista ya adaptada por el hook.
export function {{Nombre}}View({ view }: { view: {{Nombre}}ViewModel }) {
  return <div>{view.label}</div>;
}
