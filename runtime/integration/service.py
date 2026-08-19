"""CR-9.5 integration service."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional

from ..api import RuntimeService
from ..graph import InMemoryGraphStore, GraphStore
from ..interoperability import (ExternalIdentifier, InteropError,
                                InteropRegistry)
from ..interoperability.identity import ConflictValue


@dataclass(frozen=True)
class IntegrationReport:
    """The outcome of one integration run."""

    source: str
    import_mode: str
    imported: int = 0
    skipped: int = 0
    failed: int = 0
    errors: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "importMode": self.import_mode,
            "imported": self.imported,
            "skipped": self.skipped,
            "failed": self.failed,
            "errors": self.errors,
        }


def _validate_target_type(target_type: str) -> str:
    """CR-9K: an imported element's type must exist in the canonical registry."""
    from ..api.service import Registry
    if target_type not in Registry.entities():
        raise InteropError(
            f"integration target type {target_type!r} is not a canonical "
            "OpenDEA concept (CR-9K)")
    return target_type


class IntegrationService:
    """CR-9J/O/P — runtime integration of external sources into a GraphStore."""

    def __init__(self, registry: InteropRegistry,
                 service: Optional[RuntimeService] = None):
        self.registry = registry
        self.service = service or RuntimeService(InMemoryGraphStore())

    def run_full_import(self, source: str, records: Iterable[Mapping[str, Any]],
                        source_tag: str = "") -> IntegrationReport:
        """CR-9P: full import mode — every record is materialised."""
        return self._run_import(source, records, import_mode="FULL",
                               source_tag=source_tag)

    def run_incremental_import(self, source: str,
                               records: Iterable[Mapping[str, Any]],
                               source_tag: str = "") -> IntegrationReport:
        """CR-9P: incremental import mode — already-present entities are skipped."""
        return self._run_import(source, records, import_mode="INCREMENTAL",
                               source_tag=source_tag)

    def run(self, source: str, records: Iterable[Mapping[str, Any]],
            import_mode: str = "FULL", source_tag: str = "") -> IntegrationReport:
        return self._run_import(source, records, import_mode=import_mode,
                               source_tag=source_tag)

    def _run_import(self, source: str, records: Iterable[Mapping[str, Any]],
                    import_mode: str, source_tag: str) -> IntegrationReport:
        if source not in self.registry.systems:
            raise InteropError(f"unknown integration source {source!r}")
        imported = skipped = failed = 0
        errors: List[str] = []
        for record in records:
            try:
                materialised = self._materialize(
                    source, record, source_tag,
                    skip_existing=(import_mode != "FULL"))
            except InteropError as exc:
                failed += 1
                errors.append(str(exc))
                continue
            if materialised:
                imported += 1
            else:
                skipped += 1
        return IntegrationReport(
            source=source, import_mode=import_mode,
            imported=imported, skipped=skipped, failed=failed,
            errors=errors)

    def _materialize(self, source: str, record: Mapping[str, Any],
                     source_tag: str, skip_existing: bool) -> bool:
        entity_id = record.get("id")
        target_type = record.get("type")
        if not entity_id or not target_type:
            raise InteropError(
                "integration records require id and type (CR-9K)")
        target_type = _validate_target_type(target_type)
        already = self.service.store.has_entity(entity_id)
        if skip_existing and already:
            return False

        existing_properties = (
            self.service.store.get_entity(entity_id).properties
            if already else {})
        properties = self._build_properties(source, record, source_tag)
        if already:
            self.service.update_entity(
                entity_id, name=record.get("name"), properties=properties)
        else:
            self.service.create_entity(
                entity_id, target_type, record.get("name", entity_id),
                lifecycle_status=record.get("lifecycle_status"),
                properties=properties,
                source={"sourceSystem": source,
                        "sourceTag": source_tag or source})

        external_id = record.get("external_id")
        if external_id:
            self.registry.link_external_identifier(ExternalIdentifier(
                system=source, identifier=str(external_id), entity=entity_id,
                identifier_type="primary"))

        for prop_name in ("lifecycle_state", "classification"):
            if prop_name in record and already:
                existing = existing_properties.get(prop_name)
                if existing is not None and existing != record[prop_name]:
                    self.registry.record_conflict(
                        entity_id, prop_name,
                        [ConflictValue(source=source, value=existing,
                                       observed_at=existing_properties.get("sourceTag", "")),
                         ConflictValue(source=source, value=record[prop_name],
                                       observed_at=source_tag or source)])
        return True

    def _build_properties(self, source: str, record: Mapping[str, Any],
                          source_tag: str) -> Dict[str, Any]:
        props: Dict[str, Any] = {"sourceSystem": source}
        if source_tag:
            props["sourceTag"] = source_tag
        external_id = record.get("external_id")
        if external_id:
            props["sourceRecord"] = str(external_id)
        for prop_name in ("lifecycle_state", "classification"):
            if prop_name in record:
                props[prop_name] = record[prop_name]
        for key, value in record.get("properties", {}).items():
            props[key] = value
        return props

    def _record_property_conflict_if_changed(self, source: str, entity_id: str,
                                            property_name: str,
                                            incoming_value: Any) -> None:
        """CR-9L: disagreement between sources is preserved as a conflict."""
        node = self.service.store.get_entity(entity_id)
        existing = node.properties.get(property_name)
        if existing is None or existing == incoming_value:
            return
        self.registry.record_conflict(
            entity_id, property_name,
            [ConflictValue(source=source, value=existing,
                           observed_at=node.properties.get("sourceTag", "")),
             ConflictValue(source=source, value=incoming_value,
                           observed_at=node.properties.get("sourceTag", ""))])
