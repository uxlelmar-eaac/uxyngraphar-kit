# Estructura del repo kit

```text
uxyngraphar-kit/
├── README.md                    ← portada corta: apunta a este manual
├── LICENSE · LICENCIA.md · LICENSING.md · SECURITY.md   ← lo que GitHub espera en la raíz
├── .github/workflows/publicar.yml   ← pruebas en cada cambio y release al etiquetar vX.Y.Z
└── español/                     ← única versión del sistema por ahora
    ├── documentacion/           ← este manual: TODA la documentación del kit (no se instala)
    ├── README.md · INDICE.md · AGENTES.md   ← punteros cortos a este manual / a cada pack
    ├── uxyngraphar.py           ← la herramienta «uxyngraphar»
    ├── instalar.py · actualizar.py   ← instalar y actualizar desde un clon
    ├── instalador/              ← asistente y panel (web local + consola) e instalador de una línea (arranque*.py)
    ├── backend/ · frontend/     ← los packs que se copian a uxyngraphar/ de cada proyecto
    └── _compartido/             ← fuente de lo idéntico en ambos packs + construir-packs.py + publicar.py
```

**No ensuciar:** no metas este manual dentro de `backend/`, `frontend/` ni `_compartido/base/`; cada pack lleva su propia documentación operativa (`uxyngraphar/10-guias/…`) porque viaja al proyecto.

Mantener los packs y publicar versiones: [mantener-kit.md](mantener-kit.md).
