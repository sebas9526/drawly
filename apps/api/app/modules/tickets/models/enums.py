from enum import Enum


class TicketStatus(str, Enum):
    """Ticket lifecycle states. Wire/DB values are lowercase to match the
    existing @drawly/api-client contract; Python members stay UPPERCASE so the
    domain never passes loose strings around.

    Lifecycle (docs/02-architecture/DOMAIN_MODEL.md):
        AVAILABLE -> RESERVED -> PAID -> WINNER
        RESERVED  -> AVAILABLE (reservation cancelled)
    """

    AVAILABLE = "available"
    RESERVED = "reserved"
    PAID = "paid"
    CANCELLED = "cancelled"
    WINNER = "winner"
