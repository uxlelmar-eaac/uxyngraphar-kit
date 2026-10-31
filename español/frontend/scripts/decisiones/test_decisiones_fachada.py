#!/usr/bin/env python3
"""Regresión — superficie pública del tooling tras la división R-19.

Fija que la fachada `common.py` siga re-exportando todo lo que consumen el
resto de módulos y que `applier` mantenga su API pública. Evita que una
división futura rompa imports en silencio.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from applier import apply_decision_to_file, apply_session, session_suffix
from common import (
    DEFAULT_OPTIONS,
    ESTADOS,
    MOVE_ACTIONS,
    STATUS_MAP,
    DecisionItem,
    DecisionOption,
    date_from_fm,
    estado_dest_rel,
    estado_from_path,
    extract_context,
    extract_title,
    find_group_id,
    find_section_root,
    has_decision_section,
    infer_tipo,
    is_pending_tipo,
    is_stale_item,
    iter_decision_blocks,
    load_json,
    parse_simple_yaml,
    rebuild_content,
    resolve_docs_roots,
    save_json,
    serialize_frontmatter,
    session_id_now,
    session_paths,
    should_skip_file,
    split_frontmatter,
    split_frontmatter_parts,
    update_frontmatter_raw,
    utc_now_iso,
    validate_group_id,
)


class TestFachadaR19(unittest.TestCase):
    def test_common_reexporta_utilidades(self) -> None:
        for fn in (
            parse_simple_yaml,
            split_frontmatter,
            split_frontmatter_parts,
            update_frontmatter_raw,
            rebuild_content,
            serialize_frontmatter,
            iter_decision_blocks,
            find_group_id,
            validate_group_id,
            has_decision_section,
            extract_title,
            extract_context,
            find_section_root,
            date_from_fm,
            estado_dest_rel,
            estado_from_path,
            utc_now_iso,
            session_id_now,
            resolve_docs_roots,
            session_paths,
            should_skip_file,
            infer_tipo,
            is_pending_tipo,
            is_stale_item,
            load_json,
            save_json,
        ):
            self.assertTrue(callable(fn))

    def test_common_reexporta_datos(self) -> None:
        self.assertIn("mejora", DEFAULT_OPTIONS)
        self.assertIn("01-pendientes", ESTADOS)
        self.assertIn(("mejora", "aprobar"), MOVE_ACTIONS)
        self.assertIn("mejora", STATUS_MAP)
        self.assertTrue(callable(DecisionItem))
        self.assertTrue(callable(DecisionOption))

    def test_applier_expone_api_publica(self) -> None:
        self.assertTrue(callable(apply_decision_to_file))
        self.assertTrue(callable(apply_session))
        self.assertTrue(callable(session_suffix))

    def test_modulos_extraidos_importables(self) -> None:
        import common_bloques  # noqa: F401
        import common_constantes  # noqa: F401
        import common_frontmatter  # noqa: F401
        import applier_promocion  # noqa: F401
        import applier_rutas  # noqa: F401
        import session_acciones  # noqa: F401


if __name__ == "__main__":
    unittest.main()
