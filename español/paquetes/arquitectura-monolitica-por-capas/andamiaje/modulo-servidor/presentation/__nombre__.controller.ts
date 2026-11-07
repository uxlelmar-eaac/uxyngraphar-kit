import type { {{Nombre}}Dto } from '../contracts/{{nombre}}.dto';
import type { Get{{Nombre}}UseCase } from '../application/{{nombre}}.usecase';

export class {{Nombre}}Controller {
  constructor(private readonly getUseCase: Get{{Nombre}}UseCase) {}

  get(id: string): Promise<{{Nombre}}Dto | null> {
    return this.getUseCase.execute(id);
  }
}
