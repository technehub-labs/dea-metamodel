"""CR-8 §7 identity helpers for the runtime."""
from __future__ import annotations

import re

CANONICAL_ID = re.compile(r"^[a-z][a-z0-9-]*(\.[a-z0-9-]+)*$")


def is_canonical_id(value: str) -> bool:
    """True when ``value`` satisfies the CR-8 §7 stable-identity pattern.

    Names are not identities: ``Customer Service`` is a name;
    ``cap.customer-service`` is an identity.
    """
    return bool(CANONICAL_ID.match(value or ""))
