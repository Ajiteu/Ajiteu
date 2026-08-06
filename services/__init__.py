"""서비스 레이어 공통 예외."""


class ServiceError(Exception):
    """비즈니스 로직 오류 (API가 HTTP 상태 코드로 변환)."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status
