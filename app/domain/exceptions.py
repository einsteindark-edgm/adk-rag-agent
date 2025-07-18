"""Domain exceptions for shipment tracking system."""


class DomainError(Exception):
    """Base exception for domain errors."""
    pass


class ShipmentTrackingError(DomainError):
    """Base exception for shipment tracking errors."""
    pass


class ShipmentNotFoundError(ShipmentTrackingError):
    """Raised when a shipment is not found."""
    def __init__(self, ticket_id: str):
        self.ticket_id = ticket_id
        super().__init__(f"Shipment not found: {ticket_id}")


class InvalidTicketIDError(ShipmentTrackingError):
    """Raised when a ticket ID format is invalid."""
    def __init__(self, ticket_id: str):
        self.ticket_id = ticket_id
        super().__init__(f"Invalid ticket ID format: {ticket_id}")


class AnomalyNotFoundError(ShipmentTrackingError):
    """Raised when an anomaly is not found."""
    def __init__(self, anomaly_id: str):
        self.anomaly_id = anomaly_id
        super().__init__(f"Anomaly not found: {anomaly_id}")


class AnomalyProcessingError(ShipmentTrackingError):
    """Raised when there's an error processing anomaly data."""
    def __init__(self, message: str, anomaly_type: str = None):
        self.anomaly_type = anomaly_type
        super().__init__(message)