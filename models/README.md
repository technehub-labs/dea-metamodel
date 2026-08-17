# OpenDEA Models — golden & negative suites (CR-8 §30-§33)

`golden/` — canonical valid models. Every file MUST pass `tools/opendea_validate.py`.
They double as the reference scenarios (§31): traditional (Core), transformation
(lifecycle), DMM (assessment), agent (agentic), governed agent (governance),
multi-agent (orchestration).

`invalid/` — deliberately invalid models. The validator MUST fail each for the
expected reason (recorded in the file header and asserted in
`tests/conformance/test_014_specification_rules.py`). This makes the specification
a testable contract (§33): two independent implementations must reach the same
conclusion (§69 Definition of Done).

| File | Expected | Rule |
|---|---|---|
| missing-id.yaml | FAIL | DEA-E004 envelope |
| invalid-type.yaml | FAIL | DEA-E001 |
| invalid-relationship.yaml | FAIL | DEA-E002 |
| invalid-endpoint.yaml | FAIL | DEA-E006 |
| cardinality-error.yaml | FAIL | DEA-E003 (A001) |
| unauthorized-agent.yaml | FAIL | DEA-E009 (G006) |
| missing-owner.yaml | FAIL | DEA-E008 (G007) |
| invalid-lifecycle.yaml | FAIL | DEA-E004 vocabulary |
