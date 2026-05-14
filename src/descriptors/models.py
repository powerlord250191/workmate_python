from dataclasses import dataclass
from typing import Any, TypeAlias

JSON: TypeAlias = dict[str, Any]


class Model:
    def __init__(self, payload: JSON):
        self.payload = payload


@dataclass
class Field:
    path: str

    def _get_based(self, data: dict) -> Any:
        keys = self.path.split('.')
        current = data
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        return current

    def _set_nested(self, data: dict, value: Any) -> None:
        keys = self.path.split('.')
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def _del_nested(self, data: dict) -> None:
        keys = self.path.split('.')
        current = data
        for key in keys[:-1]:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]

        if isinstance(current, dict) and keys[-1] in current:
            del current[keys[-1]]

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self
        return self._get_based(instance.payload)

    def __set__(self, instance: Any, value: Any) -> None:
        self._set_nested(instance.payload, value)

    def __delete__(self, instance: Any) -> None:
        self._del_nested(instance.payload)