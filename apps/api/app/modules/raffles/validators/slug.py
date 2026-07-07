import re
import unicodedata

_NON_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """Deterministic lowercase kebab-case slug. No business rules, just formatting."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    lowered = normalized.lower().strip()
    return _NON_SLUG.sub("-", lowered).strip("-")
