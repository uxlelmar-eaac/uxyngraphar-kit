# Configuración

Ajustes propios del sistema que no forman parte del manifiesto (`sistema.json`): parámetros, valores por defecto,
listas de referencia. El kit no los interpreta; los leen tus prompts, scripts o fases.

- `ajustes.json`: punto de partida. Cambia los valores o añade claves nuevas.

Si importas un sistema con su propia configuración (JSON, YAML, TOML…), se guarda aquí sin perder nada: los JSON
con el mismo nombre se fusionan y tus valores mandan.
