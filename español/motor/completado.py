"""`uxyngraphar completado bash|zsh|fish|powershell`: imprime el script de autocompletado de la CLI (M-26) con los
comandos y los ids del catálogo de esta versión. Se activa añadiendo su salida al perfil de la shell (ver README)."""

from __future__ import annotations

SHELLS = ("bash", "zsh", "fish", "powershell")
CON_IDS = ("instalar", "actualizar", "quitar", "validar", "indice-sistema", "version", "pieza", "construir", "andamiar")


def comandos() -> list[str]:
    import cli
    import uxyngraphar
    sub = cli.analizador()._subparsers._group_actions[0].choices   # noqa: SLF001 - argparse no expone los subcomandos
    publicos = [c for c in uxyngraphar.HERRAMIENTA if not c.startswith("_")]
    return sorted({*sub, *publicos, "ayuda"})


def ids() -> list[str]:
    import fuentes
    return fuentes.ids_conocidos()


def script(shell: str) -> str:
    if shell not in SHELLS:
        raise ValueError(f"shell: una de {', '.join(SHELLS)}")
    cmds, sistemas, con_ids = " ".join(comandos()), " ".join(ids()), " ".join(CON_IDS)
    if shell in ("bash", "zsh"):
        previo = "autoload -U +X bashcompinit && bashcompinit\n" if shell == "zsh" else ""
        return f"""# uxyngraphar: autocompletado ({shell}). Generado por «uxyngraphar completado {shell}».
{previo}_uxyngraphar() {{
  local actual="${{COMP_WORDS[COMP_CWORD]}}"
  if [ "$COMP_CWORD" -eq 1 ]; then
    COMPREPLY=($(compgen -W "{cmds}" -- "$actual"))
  elif [[ " {con_ids} " == *" ${{COMP_WORDS[1]}} "* && "$actual" != -* ]]; then
    COMPREPLY=($(compgen -W "{sistemas}" -- "$actual"))
  fi
}}
complete -o default -F _uxyngraphar uxyngraphar
"""
    if shell == "fish":
        return (f"# uxyngraphar: autocompletado (fish). Generado por «uxyngraphar completado fish».\n"
                f"complete -c uxyngraphar -f -n '__fish_use_subcommand' -a '{cmds}'\n"
                f"complete -c uxyngraphar -f -n '__fish_seen_subcommand_from {con_ids}' -a '{sistemas}'\n")
    lista = ", ".join(f"'{c}'" for c in comandos())
    ids_ps = ", ".join(f"'{i}'" for i in ids())
    con_ids_ps = ", ".join(f"'{c}'" for c in CON_IDS)
    return f"""# uxyngraphar: autocompletado (PowerShell). Generado por «uxyngraphar completado powershell».
Register-ArgumentCompleter -Native -CommandName uxyngraphar -ScriptBlock {{
  param($palabra, $linea, $cursor)
  $partes = $linea.ToString().Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
  $opciones = if ($partes.Count -le 1 -or ($partes.Count -eq 2 -and $palabra)) {{ @({lista}) }}
              elseif (@({con_ids_ps}) -contains $partes[1]) {{ @({ids_ps}) }} else {{ @() }}
  $opciones | Where-Object {{ $_ -like "$palabra*" }} | ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
}}
"""
