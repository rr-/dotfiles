class NoContentError(RuntimeError):
    pass


class DuplicateUploadError(RuntimeError):
    pass


class ApiError(RuntimeError):
    pass


class NotFoundError(ApiError):
    pass
