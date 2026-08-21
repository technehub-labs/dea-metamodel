# External mappings (CR-8 §44-§46)

OpenDEA never depends on external standards; mappings are informative bridges and the
OpenDEA semantic identity remains authoritative. Where semantics differ, we document the
difference rather than pretend equivalence.

| Mapping | Status | Notes |
|---|---|---|
| [ArchiMate](./archimate/mapping.yaml) | v1.0.0 → CR-11X | §45 matrix + relationship mapping + confidence/lossiness (CR-11X). |
| [BPMN](./bpmn/mapping.yaml) | v1.0.0 / CR-11Y | Process / Task / Gateway / Event mapping into OpenDEA's process vocabulary. |
| [DMN](./dmn/mapping.yaml) | v1.0.0 / CR-11Z | Decision + DecisionRecord + DecisionCriterion mapping; FEEL preserved literally. |
| [DMM](./dmm/mapping.yaml) | v1.0.0 / Phase 5 | DMM assessment bands map to OpenDEA maturity v2 (Emergent → Self-Optimising). |
| RDF/OWL | adopted as derived serialization | `ttl/dea-metamodel-ontology.ttl` is generated from the normative source (§2/§21). SHACL evaluation for graph-level validation is a roadmap item (§26). |
| JSON Schema / JSON-LD | JSON Schema adopted | JSON-LD context candidate under `schema/contexts/`. |
| Dublin Core / PROV | alignment notes | metadata fields map to dcterms; provenance (§39) aligns with PROV-O wasDerivedFrom/wasAttributedTo. |
