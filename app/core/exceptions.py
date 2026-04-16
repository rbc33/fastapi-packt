from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse


class FastShipError(Exception):
    """Base class for all FastShip exceptions."""
    status_code: int = status.HTTP_400_BAD_REQUEST

class EntityNotFound(FastShipError):
    """Entity is not found in the database."""
    status_code = status.HTTP_404_NOT_FOUND

class ClientNotAuthorized(FastShipError):
    """Client is not authorized to perform the action."""
    status_code = status.HTTP_401_UNAUTHORIZED

class BadCredentials(FastShipError):
    """Invalid email or password provided."""
    status_code = status.HTTP_401_UNAUTHORIZED

class InvalidToken(FastShipError):
    """Invalid or expired token provided."""
    status_code = status.HTTP_401_UNAUTHORIZED

class DeliveryPartnerNotAvailable(FastShipError):
    """Delivery partner not found."""
    status_code = status.HTTP_406_NOT_ACCEPTABLE

class NothingToUpdate(FastShipError):
    """Bad request no data provided to update."""
    status_code = status.HTTP_400_BAD_REQUEST

class EmailNotVerified(FastShipError):
    """Email is not verified."""
    status_code = status.HTTP_401_UNAUTHORIZED


def _get_handler(status:int, detail:str):
    def handler(request: Request, exception: Exception) -> JSONResponse:
        from rich import panel, print

        print(panel.Panel(f"Handled: {exception.__class__.__name__}"))
        
        return JSONResponse(
            status_code=status,
            content={"detail": detail},
        )
    return handler

def add_exception_handlers(app: FastAPI):
    for exception_class in FastShipError.__subclasses__():
        app.add_exception_handler(
            exception_class,
            _get_handler(exception_class.status_code, exception_class.__doc__),
        )
    @app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    def internal_server_error_handler(request, exception):
        return JSONResponse(
            content= {"detail": "Something went wrong..."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={
                "X-Error": f"{exception}"
            }
        )
