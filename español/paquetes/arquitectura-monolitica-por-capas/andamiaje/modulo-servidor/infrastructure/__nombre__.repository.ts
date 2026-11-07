import type { {{Nombre}} } from '../domain/{{nombre}}.entity';

export interface {{Nombre}}Repository {
  findById(id: string): Promise<{{Nombre}} | null>;
}
