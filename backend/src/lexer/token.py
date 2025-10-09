from .token_types import TokenType

class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type #тип токена
        self.value = value #строковое значение токена
        self.line = line #номер строки в исходном коде
        self.column = column #номер столбца в исходном коде

    def __repr__(self):
        return f"Token({self.type.value}, '{self.value}', line={self.line}, col={self.column})"

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and
                self.value == other.value and
                self.line == other.line and
                self.column == other.column)

    def to_dict(self):
        """Преобразуем токен в словарь для удобства отладки"""
        return {
            'type': self.type.value,
            'value': self.value,
            'line': self.line,
            'column': self.column
        }