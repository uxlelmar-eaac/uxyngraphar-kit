---
name: documentar-area
description: Crea el contexto ARE de un área funcional en su propia carpeta, con propósito, las cuatro líneas de fronteras, dependencias, mapa de lectura y código ancla.
resuelve: [fronteras-de-area-difusas, cambios-sin-area-identificada, dependencias-hacia-areas-sin-documentar]
---

# Documentar área

## Cuándo usarla

- Nace un área funcional nueva.
- Un área existente no tiene contexto (aparece en `depends_on` de otra o el pedido la toca).

## Pasos

1. Elige el nombre del área en kebab-case (será su carpeta y lo que citen las demás en `depends_on`): `payments`.
2. Crea el contexto en su carpeta:
   `python3 $P/scripts/comun/fichas.py nueva area --slug payments --en payments --titulo "Área: pagos"`
3. Frontmatter: `depends_on` con nombres de carpetas de áreas; `owners` vacío salvo que la persona los dé. Si el área aún no tiene código, `python3 $P/scripts/comun/fichas.py estado <id> planned`.
4. «Propósito»: dos a cuatro líneas.
5. «Fronteras»: las cuatro líneas (Posee, No posee, Escribe en datos, Habla con externos). En «No posee», lo que suele confundirse con esta área y de quién es.
6. «Mapa de lectura»: este contexto y como mucho cuatro pasos más (raíz del módulo, caso de uso principal, espejo o ficha de API clave).
7. «Código ancla»: carpetas o archivos reales. «Flujos críticos»: los recorridos que no se pueden romper.

## Resultado

- `uxyngraphar/trabajo/mapa-de-modulos/<area>/ARE-<fecha>-<area>.md` con fronteras completas y dependencias hacia áreas existentes.
