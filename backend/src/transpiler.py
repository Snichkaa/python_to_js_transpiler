# transpiler.py - исправленная версия
try:
    from .lexer.lexer import Lexer
    from .parser.parser import Parser
    from .semantic.analyzer import SemanticAnalyzer
    from .codegen.generator import CodeGenerator
    from .exceptions import TranspilerError
except ImportError:
    # Альтернативные импорты для тестов
    from lexer.lexer import Lexer
    from parser.parser import Parser
    from semantic.analyzer import SemanticAnalyzer
    from codegen.generator import CodeGenerator
    from exceptions import TranspilerError


class Transpiler:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = SemanticAnalyzer()
        self.code_generator = CodeGenerator()

    def transpile(self, source_code: str) -> str:
        """
        Транспилирует код Python в JavaScript
        """
        try:
            print(f"DEBUG: Transpiling: {repr(source_code)}")  # ДЛЯ ОТЛАДКИ

            # 1. Лексический анализ (только для отладки)
            debug_lexer = Lexer(source_code)
            tokens = debug_lexer.tokenize()
            print(f"DEBUG: Tokens: {tokens}")  # ДЛЯ ОТЛАДКИ

            # 2. Синтаксический анализ (используем ОТДЕЛЬНЫЙ лексер)
            parser_lexer = Lexer(source_code)  # ← ВАЖНО: новый лексер для парсера
            self.parser = Parser(parser_lexer)
            ast = self.parser.parse()
            print(f"DEBUG: AST: {ast}")  # ДЛЯ ОТЛАДКИ

            # 3. Семантический анализ (пока закомментируем)
            # self.semantic_analyzer.analyze(ast)

            # 4. Генерация кода
            js_code = self.code_generator.generate(ast)
            print(f"DEBUG: Generated JS: {repr(js_code)}")  # ДЛЯ ОТЛАДКИ

            return js_code

        except Exception as e:
            print(f"DEBUG: Error: {e}")  # ДЛЯ ОТЛАДКИ
            raise TranspilerError(f"Transpilation failed: {str(e)}")