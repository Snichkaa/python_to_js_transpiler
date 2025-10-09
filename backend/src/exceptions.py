class TranspilerError(Exception):
    """Базовое исключение для всех ошибок транслятора"""

    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())

    def _format_message(self):
        """Форматируем сообщение об ошибке с указанием позиции"""
        if self.line is not None:
            location = f"Line {self.line}"
            if self.column is not None:
                location += f", column {self.column}"
            return f"{location}\n{self.message}"
        return self.message


class LexerError(TranspilerError):
    """Базовый класс для ошибок лексического анализа"""
    def __init__(self, message, line, column):
        super().__init__(message, line, column)


class InvalidCharacterError(LexerError):
    """Недопустимый символ в исходном коде"""

    def __init__(self, char, line, column):
        message = f"Invalid character: '{char}'"
        super().__init__(message, line, column)


class UnclosedStringError(LexerError):
    """Незакрытая строковая константа"""

    def __init__(self, line, column, quote_type):
        message = f"Unclosed {quote_type} quote string literal"
        super().__init__(message, line, column)


class InvalidNumberError(LexerError):
    """Некорректный числовой литерал"""

    def __init__(self, value, line, column):
        message = f"Invalid number literal: '{value}'"
        super().__init__(message, line, column)


class ParserError(TranspilerError):
    """Базовый класс для ошибок синтаксического анализа"""
    pass


class UnexpectedTokenError(ParserError):
    """Неожиданный токен"""
    def __init__(self, expected, actual, line, column):
        message = f"Expected {expected}, but got {actual}"
        super().__init__(message, line, column)


class MissingTokenError(ParserError):
    """Отсутствует обязательный токен"""
    def __init__(self, token_type, line, column):
        message = f"Missing required token: {token_type}"
        super().__init__(message, line, column)


class SyntaxError(ParserError):
    """Синтаксическая ошибка"""
    def __init__(self, message, line, column):
        super().__init__(message, line, column)


# Семантические ошибки
class SemanticError(TranspilerError):
    """Базовый класс для ошибок семантического анализа"""
    pass


class UndefinedVariableError(SemanticError):
    """Использование необъявленной переменной"""
    def __init__(self, var_name, line, column):
        message = f"Undefined variable: '{var_name}'"
        super().__init__(message, line, column)


class RedeclarationError(SemanticError):
    """Повторное объявление переменной/функции"""
    def __init__(self, name, line, column):
        message = f"Redeclaration of '{name}'"
        super().__init__(message, line, column)


class TypeMismatchError(SemanticError):
    """Несоответствие типов"""
    def __init__(self, expected, actual, line, column):
        message = f"Type mismatch: expected {expected}, got {actual}"
        super().__init__(message, line, column)


class InvalidOperationError(SemanticError):
    """Недопустимая операция для данного типа"""
    def __init__(self, operation, operand_type, line, column):
        message = f"Invalid operation '{operation}' for type '{operand_type}'"
        super().__init__(message, line, column)


class ReservedWordError(SemanticError):
    """Использование зарезервированного слова JS в качестве идентификатора Python"""
    def __init__(self, word, line, column):
        message = f"'{word}' is a reserved word in JavaScript and cannot be used as identifier"
        super().__init__(message, line, column)


# Ошибки генерации кода
class CodeGenError(TranspilerError):
    """Ошибка генерации кода"""
    pass


class UnsupportedFeatureError(CodeGenError):
    """Неподдерживаемая фича Python"""
    def __init__(self, feature, line, column):
        message = f"Unsupported Python feature: {feature}"
        super().__init__(message, line, column)