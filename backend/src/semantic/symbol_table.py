from enum import Enum
from typing import Optional, Dict, Any
from ..parser.ast_nodes import DataType


class SymbolType(Enum):
    VARIABLE = "variable"
    FUNCTION = "function"
    PARAMETER = "parameter"


class Symbol:
    """Запись в таблице символов"""

    def __init__(self, name: str, symbol_type: SymbolType,
                 data_type: DataType = DataType.ANY, value: Any = None,
                 line: int = 0, column: int = 0):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type
        self.value = value
        self.line = line
        self.column = column


class Scope:
    """Область видимости"""

    def __init__(self, parent: Optional['Scope'] = None):
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}

    def declare(self, symbol: Symbol) -> bool:
        """Объявление символа в текущей области видимости"""
        if symbol.name in self.symbols:
            return False  # символ уже объявлен
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str) -> Optional[Symbol]:
        """Поиск символа в текущей и родительских областях видимости"""
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Поиск символа только в текущей области видимости"""
        return self.symbols.get(name)


class SymbolTable:
    """Таблица символов с поддержкой вложенных областей видимости"""

    def __init__(self):
        self.current_scope = Scope()

    def enter_scope(self):
        """Вход в новую область видимости"""
        self.current_scope = Scope(self.current_scope)

    def exit_scope(self):
        """Выход из текущей области видимости"""
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    def declare(self, name: str, symbol_type: SymbolType,
                data_type: DataType = DataType.ANY, value: Any = None,
                line: int = 0, column: int = 0) -> bool:
        """Объявление символа"""
        symbol = Symbol(name, symbol_type, data_type, value, line, column)
        return self.current_scope.declare(symbol)

    def lookup(self, name: str) -> Optional[Symbol]:
        """Поиск символа"""
        return self.current_scope.lookup(name)

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Поиск символа в текущей области видимости"""
        return self.current_scope.lookup_local(name)