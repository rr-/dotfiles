class DrillError(RuntimeError):
    pass


class CardNotFoundError(DrillError):
    pass


class DeckNotFoundError(DrillError):
    pass


class AmbiguousDeckError(DrillError):
    pass


class CardAlreadyExistsError(DrillError):
    pass


class DeckAlreadyExistsError(DrillError):
    pass
