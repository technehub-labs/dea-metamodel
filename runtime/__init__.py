"""OpenDEA Runtime — CR-9 reference implementation.

CR-9.1 (Runtime Foundation) delivers the vendor-independent graph abstraction
(CR-9D), the canonical model loader (CR-9BT.2/.3) and entity/relationship
APIs with registry-backed write validation. Later milestones (CR-9.2…CR-9.10)
layer provenance graphs, reasoning, temporal/event runtime, integration,
assessment, decision, agentic runtime, explorer and conformance releases on
top of this surface. See runtime/README.md and docs/runtime-architecture.md.
"""

__version__ = "0.3.0"  # CR-9.1 + CR-10 Phase 1 + CR-11 Phase 1
__opendea_spec__ = "1.0.0"  # CR-8 specification this runtime consumes
