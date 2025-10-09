from .lexer.lexer import Lexer
from .parser.parser import Parser
from .semantic.analyzer import SemanticAnalyzer
from .codegen.generator import CodeGenerator
from .exceptions import TranspilerError


class Transpiler:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = SemanticAnalyzer()
        self.code_generator = CodeGenerator()

    def transpile(self, source_code: str) -> str:
        """
        Транспилирует код Python в JavaScript

        Args:
            source_code: Исходный код на Python

        Returns:
            JavaScript код

        Raises:
            TranspilerError: Если возникла ошибка на любом этапе трансляции
        """
        try:
            # 1. Лексический анализ
            self.lexer = Lexer(source_code)
            tokens = self.lexer.tokenize()

            # 2. Синтаксический анализ
            self.parser = Parser(self.lexer)
            ast = self.parser.parse()

            # 3. Семантический анализ
            if not self.semantic_analyzer.analyze(ast):
                errors = "\n".join([str(e) for e in self.semantic_analyzer.errors])
                raise TranspilerError(f"Semantic errors found:\n{errors}")

            # 4. Генерация кода
            js_code = self.code_generator.generate(ast)

            return js_code

        except TranspilerError:
            # Пробрасываем наши кастомные ошибки
            raise
        except Exception as e:
            # Оборачиваем любые другие ошибки в TranspilerError
            raise TranspilerError(f"Transpilation failed: {str(e)}")