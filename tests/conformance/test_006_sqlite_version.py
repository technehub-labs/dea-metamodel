"""Test 006 (CR-1.9): SQLite schema version equals the generated schema version."""
import re
import sqlite3

from conftest import BASE


def test_sqlite_schema_version(canonical_version):
    sql = (BASE / "sqlite" / "schema.sql").read_text()
    m = re.search(r"INSERT OR REPLACE INTO metamodel_meta.*?'metamodel_version',\s*'([^']+)'",
                  sql, re.S)
    assert m, "sqlite/schema.sql has no metamodel_meta version row"
    assert m.group(1) == canonical_version, \
        f"sqlite projection {m.group(1)} != canonical {canonical_version}"


def test_sqlite_schema_applies():
    sql = (BASE / "sqlite" / "schema.sql").read_text()
    con = sqlite3.connect(":memory:")
    con.executescript(sql)
    row = con.execute("SELECT value FROM metamodel_meta WHERE key='metamodel_version'").fetchone()
    con.close()
    assert row, "metamodel_meta not populated after schema apply"
