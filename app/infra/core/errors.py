class AppError(Exception):
    pass


class ExistsError(AppError):

    def __init__(self, resource: str, attribute: str, value: str) -> None:
        self.resource = resource
        self.attribute = attribute
        self.value = value
        message = f"{resource} with {attribute} <{value}> already exists."
        super().__init__(message)


class DoesNotExistError(AppError):

    def __init__(self, resource: str, attribute: str, value: str) -> None:
        self.resource = resource
        self.attribute = attribute
        self.value = value
        message = f"{resource} with {attribute} <{value}> does not exist."
        super().__init__(message)


class ReceiptClosedError(AppError):

    def __init__(self, receipt_id: str) -> None:
        self.receipt_id = receipt_id
        message = f"Receipt with id <{receipt_id}> is closed."
        super().__init__(message)


class ShiftClosedError(AppError):
    def __init__(self, shift_id: str) -> None:
        self.shift_id = shift_id
        message = f"Shift with id <{shift_id}> is already closed."
        super().__init__(message)
