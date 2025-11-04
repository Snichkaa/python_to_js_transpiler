from enum import Enum
from typing import Optional

class SymbolType(Enum):
    VARIABLE = "variable"
    FUNCTION = "function"
    PARAMETER = "parameter"

class DataType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    LIST = "list"
    NONE = "none"
    ANY = "any"

class Symbol:
    def __init__(self, name: str, symbol_type: SymbolType, data_type: DataType, line: int, column: int):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type
        self.line = line
        self.column = column

class Scope:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, symbol: Symbol):
        """Добавляет символ в текущую область видимости"""
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Ищет символ в текущей и родительских областях видимости"""
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Ищет символ только в текущей области видимости"""
        return self.symbols.get(name)

class SymbolTable:
    def __init__(self):
        self.current_scope = Scope()
        self.scope_stack = [self.current_scope]

    def enter_scope(self):
        """Вход в новую область видимости"""
        new_scope = Scope(self.current_scope)
        self.current_scope = new_scope
        self.scope_stack.append(new_scope)

    def exit_scope(self):
        """Выход из текущей области видимости"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]

    def define(self, name: str, symbol_type: SymbolType, data_type: DataType, line: int, column: int):
        """Добавляет символ в текущую область видимости"""
        symbol = Symbol(name, symbol_type, data_type, line, column)
        self.current_scope.define(symbol)

    def lookup(self, name: str) -> Optional[Symbol]:
        """Ищет символ в текущей и всех родительских областях видимости"""
        return self.current_scope.lookup(name)

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Ищет символ только в текущей области видимости"""
        return self.current_scope.lookup_local(name)