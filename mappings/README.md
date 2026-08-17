# External mappings (CR-8 §44-§46)

OpenDEA never depends on external standards; mappings are informative bridges and the
OpenDEA semantic identity remains authoritative. Where semantics differ, we document the
difference rather than pretend equivalence.

| Mapping | Status | Notes |
|---|---|---|
| [ArchiMate](./archimate/mapping.yaml) | v1.0.0 | §45 matrix with documented divergences |
| DMN | evaluated (§46) | OpenDEA Decision ≈ DMN Decision + decision logic, but OpenDEA Decision is broader: authority, governance, enterprise context, architecture impact, change, accountability. A DMN profile is a future extension candidate. |
| BPMN | candidate | OpenDEA BusinessProcess/Workflow ↔ BPMN process/collaboration; not yet mapped. |
| RDF/OWL | adopted as derived serialization | `ttl/dea-metamodel-ontology.ttl` is generated from the normative source (§2/§21). SHACL evaluation for graph-level validation is a roadmap item (§26). |
| JSON Schema / JSON-LD | JSON Schema adopted | JSON-LD context candidate under `schema/contexts/`. |
| Dublin Core / PROV | alignment notes | metadata fields map to dcterms; provenance (§39) aligns with PROV-O wasDerivedFrom/wasAttributedTo. |
