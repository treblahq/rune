from dataclasses import dataclass


@dataclass(slots=True)
class RuneError(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return self.message
