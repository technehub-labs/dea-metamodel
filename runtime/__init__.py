"""OpenDEA Runtime — CR-9 reference implementation.

CR-9.1 (Runtime Foundation) delivers the vendor-independent graph abstraction
(CR-9D), the canonical model loader (CR-9BT.2/.3) and entity/relationship
APIs with registry-backed write validation. CR-9.2 adds the canonical
provenance graph (CR-9O/P/T/BC). Later milestones (CR-9.3…CR-9.10) layer
reasoning, temporal/event runtime, integration, assessment, decision, agentic
runtime, explorer and conformance releases on top of this surface. See
runtime/README.md and docs/runtime-architecture.md.
"""

__version__ = "0.9.0"  # CR-9.1–9.4 + CR-10 Phases 1–3 + CR-11 Phases 1–2
__opendea_spec__ = "1.0.0"  # CR-8 specification this runtime consumes
