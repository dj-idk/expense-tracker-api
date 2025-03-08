from fastapi import HTTPException


class BadRequest(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)


class Unauthorized(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class Forbidden(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


class NotFound(HTTPException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(status_code=404, detail=detail)


class MethodNotAllowed(HTTPException):
    def __init__(self, detail: str = "Method not allowed"):
        super().__init__(status_code=405, detail=detail)


class Conflict(HTTPException):
    def __init__(self, detail: str = "Conflict detected"):
        super().__init__(status_code=409, detail=detail)


class UnprocessableEntity(HTTPException):
    def __init__(self, detail: str = "Unprocessable entity"):
        super().__init__(status_code=422, detail=detail)


class TooManyRequests(HTTPException):
    def __init__(self, detail: str = "Too many requests"):
        super().__init__(status_code=429, detail=detail)


class InternalServerError(HTTPException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=500, detail=detail)


class ServiceUnavailable(HTTPException):
    def __init__(self, detail: str = "Service unavailable"):
        super().__init__(status_code=503, detail=detail)
