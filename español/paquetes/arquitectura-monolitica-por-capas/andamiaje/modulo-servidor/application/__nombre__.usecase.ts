import type { {{Nombre}}Dto } from '../contracts/{{nombre}}.dto';
import type { {{Nombre}}Repository } from '../infrastructure/{{nombre}}.repository';

export class Get{{Nombre}}UseCase {
  constructor(private readonly repository: {{Nombre}}Repository) {}

  async execute(id: string): Promise<{{Nombre}}Dto | null> {
    const found = await this.repository.findById(id);
    return found ? { id: found.id } : null;
  }
}
