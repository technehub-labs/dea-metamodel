CR-CM-000 — Terminology Alignment

Purpose

Establish semantic boundaries between:

* Enterprise Concept Framework;
* OpenDEA Concepts Model;
* OpenDEA Foundational Metamodel;
* Catalogs;
* Profiles.

Primary decision

Reserve:

Domain
Stage

for the Enterprise Concept Framework.

Introduce:

Concept Area
Concept Profile
Concept Classification
ECF Context

for the Concepts Model.

Acceptance criteria

1. No Concepts Model artifact uses Domain as a generic thematic grouping.
2. Every use of Domain is explicitly either:
    * ECF Domain, or
    * namespace-qualified.
3. Concepts may belong to multiple Concept Areas.
4. Concepts may have zero or more ECF Contexts.
5. Concept Area and ECF Domain are modeled as different concepts.
6. No automatic one-to-one mapping is assumed between them.
7. The terminology registry is introduced before the first canonical Concepts Model.