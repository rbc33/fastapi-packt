class FastShipError(Exception):
    """Base class for all FastShip exceptions."""

class EntityNotFound(FastShipError):
    """Entity is not found in the database."""

class ClientNotAuthorized(FastShipError):
    """Client is not authorized to perform the action."""

class BadCredentials(FastShipError):
    """Invalid email or password provided."""

class InvalidToken(FastShipError):
    """Invalid or expired token provided."""

class DeliveryPartnerNotAvailable(FastShipError):
    """Delivery partner not found."""

class BadRequest(FastShipError):
    """Bad request no data provided to update"""