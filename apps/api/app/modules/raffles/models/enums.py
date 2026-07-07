from enum import Enum


class RaffleStatus(str, Enum):
    """Raffle lifecycle. Wire/DB values are lowercase (existing project contract).

    Mirrors the lifecycle in docs/02-architecture/DOMAIN_MODEL.md
    (Draft -> Published -> Closed -> Archived).
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"
