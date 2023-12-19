import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ClientData:
    client_id: str
    shared_secret: str
    period: int = 30
    password_length: int = 6

    def __post_init__(self) -> None:
        # Validate types
        for field_name, field_type in self.__annotations__.items():
            if not isinstance(getattr(self, field_name), field_type):
                error_message = (
                    f"{field_name} should be of type {field_type.__name__}"
                )
                raise TypeError(error_message)

        if not self.client_id:
            raise ValueError("client_id cannot be empty")
        if not self.shared_secret:
            raise ValueError("shared_secret cannot be empty")
        if self.password_length < 1 or self.password_length > 10:
            raise ValueError("password_length must be between 1 and 10")
        if self.period <= 0:
            raise ValueError("period must be a positive integer")


class DuplicateKeyError(KeyError):
    pass


class ClientFile:
    def __init__(self, path: Path) -> None:
        self.path = path

    def exists(self) -> bool:
        return self.path.exists()

    def load(self) -> list[ClientData]:
        if not self.path.exists():
            return []
        return [
            ClientData(**item)
            for item in json.loads(self.path.read_text(encoding="utf-8"))
        ]

    def save(self, client_data_list: list[ClientData]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
        data = json.dumps(
            [asdict(cd) for cd in client_data_list],
            indent=4,
        )
        self.path.write_text(data, encoding="utf-8")

    def add_client_data(self, cd_new: ClientData) -> None:
        cds_existing = self.load()
        for cd_existing in cds_existing:
            if cd_new.client_id == cd_existing.client_id:
                raise DuplicateKeyError("That configuration already exists.")
        cds_new = [*cds_existing, cd_new]
        self.save(cds_new)

    def update_client_data(self, cd: ClientData) -> None:
        changed = False
        cds = self.load()
        for i in range(0, len(cds)):
            if cd.client_id == cds[i].client_id:
                cds[i] = cd
                changed = True
        if changed:
            self.save(cds)
