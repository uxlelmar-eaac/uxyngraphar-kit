export const {{nombreCamel}}QueryKeys = {
  all: ['{{nombre}}'] as const,
  detail: (id: string) => ['{{nombre}}', id] as const,
};
