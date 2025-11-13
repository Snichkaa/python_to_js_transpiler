from enum import Enum
from typing import List, Optional, Union


class NodeType(Enum):
    PROGRAM = "program"
    FUNCTION_DECLARATION = "function_declaration"
    VARIABLE_DECLARATION = "variable_declaration"
    ASSIGNMENT = "assignment"
    BINARY_OPERATION = "binary_operation"
    UNARY_OPERATION = "unary_operation"
    IDENTIFIER = "identifier"
    LITERAL = "literal"
    IF_STATEMENT = "if_statement"
    WHILE_LOOP = "while_loop"
    FOR_LOOP = "for_loop"
    EXPRESSION_STATEMENT = "expression_statement"
    RETURN_STATEMENT = "return_statement"
    BLOCK = "block"
    IMPORT = "import"
    FUNCTION_CALL = "function_call"
    BREAK_STATEMENT = "break_statement"
    CONTINUE_STATEMENT = "continue_statement"


class DataType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    LIST = "list"
    NONE = "none"
    ANY = "any"


class Node:
    """Базовый класс для всех узлов AST"""

    def __init__(self, node_type: NodeType, line: int, column: int):
        self.node_type = node_type
        self.line = line
        self.column = column

    def accept(self, visitor):
        """Метод для принятия посетителя (Visitor pattern)"""
        method_name = f'visit_{self.node_type.value}'
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)


class Program(Node):
    """Корневой узел программы"""

    def __init__(self, statements: List[Node], line: int, column: int):
        super().__init__(NodeType.PROGRAM, line, column)
        self.statements = statements


class FunctionDeclaration(Node):
    """Объявление функции"""

    def __init__(self, name: str, parameters: List['Identifier'],
                 body: 'Block', return_type: DataType = DataType.NONE,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.FUNCTION_DECLARATION, line, column)
        self.name = name
        self.parameters = parameters
        self.body = body
        self.return_type = return_type


class VariableDeclaration(Node):
    """Объявление переменной"""

    def __init__(self, name: str, value: Optional[Node] = None,
                 var_type: DataType = DataType.ANY, line: int = 0, column: int = 0):
        super().__init__(NodeType.VARIABLE_DECLARATION, line, column)
        self.name = name
        self.value = value
        self.var_type = var_type


class Assignment(Node):
    """Присваивание значения переменной"""

    def __init__(self, target: 'Identifier', value: Node, line: int, column: int):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.target = target
        self.value = value


class BinaryOperation(Node):
    """Бинарная операция"""

    def __init__(self, left: Node, operator: str, right: Node, line: int, column: int):
        super().__init__(NodeType.BINARY_OPERATION, line, column)
        self.left = left
        self.operator = operator
        self.right = right


class UnaryOperation(Node):
    """Унарная операция"""

    def __init__(self, operator: str, operand: Node, line: int, column: int):
        super().__init__(NodeType.UNARY_OPERATION, line, column)
        self.operator = operator
        self.operand = operand


class Identifier(Node):
    """Идентификатор (имя переменной, функции и т.д.)"""

    def __init__(self, name: str, line: int, column: int):
        super().__init__(NodeType.IDENTIFIER, line, column)
        self.name = name


class Literal(Node):
    """Литерал (число, строка, булево значение и т.д.)"""

    def __init__(self, value: Union[int, float, str, bool, None, list],
                 literal_type: DataType, line: int, column: int):
        super().__init__(NodeType.LITERAL, line, column)
        self.value = value
        self.literal_type = literal_type


class IfStatement(Node):
    """Условный оператор if"""

    def __init__(self, condition: Node, then_branch: 'Block',
                 else_branch: Optional['Block'] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.IF_STATEMENT, line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class WhileLoop(Node):
    """Цикл while"""

    def __init__(self, condition: Node, body: 'Block', line: int, column: int):
        super().__init__(NodeType.WHILE_LOOP, line, column)
        self.condition = condition
        self.body = body


class ForLoop(Node):
    """Цикл for"""

    def __init__(self, variable: Identifier, iterable: Node,
                 body: 'Block', line: int, column: int):
        super().__init__(NodeType.FOR_LOOP, line, column)
        self.variable = variable
        self.iterable = iterable
        self.body = body


class Block(Node):
    """Блок кода"""

    def __init__(self, statements: List[Node], line: int, column: int):
        super().__init__(NodeType.BLOCK, line, column)
        self.statements = statements


class ExpressionStatement(Node):
    """Выражение как оператор"""

    def __init__(self, expression: Node, line: int, column: int):
        super().__init__(NodeType.EXPRESSION_STATEMENT, line, column)
        self.expression = expression


class ReturnStatement(Node):
    """Оператор return"""

    def __init__(self, value: Optional[Node] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.RETURN_STATEMENT, line, column)
        self.value = value


class Import(Node):
    """Импорт модуля"""

    def __init__(self, module_name: str, line: int, column: int):
        super().__init__(NodeType.IMPORT, line, column)
        self.module_name = module_name


class FunctionCall(Node):
    """Вызов функции"""

    def __init__(self, name: Identifier, arguments: List[Node], line: int, column: int):
        super().__init__(NodeType.FUNCTION_CALL, line, column)
        self.name = name
        self.arguments = arguments


class BreakStatement(Node):
    """Оператор break"""

    def __init__(self, line: int, column: int):
        super().__init__(NodeType.BREAK_STATEMENT, line, column)


class ContinueStatement(Node):
    """Оператор continue"""

    def __init__(self, line: int, column: int):
        super().__init__(NodeType.CONTINUE_STATEMENT, line, column)