# debug_pipeline.py в КОРНЕ проекта
import sys
import os

# Добавляем текущую директорию в path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.lexer.lexer import Lexer
from backend.src.parser.parser import Parser
from backend.src.codegen.generator import CodeGenerator


def test_pipeline(code, test_name):
    print(f"\n{'=' * 50}")
    print(f"ТЕСТ: {test_name}")
    print(f"Код: '{code}'")
    print(f"{'=' * 50}")

    # Лексер для показа токенов
    debug_lexer = Lexer(code)
    tokens = debug_lexer.tokenize()
    print("Токены:", [f"{t.type.name}('{t.value}')" for t in tokens])

    # ОТДЕЛЬНЫЙ лексер для парсера - ВАЖНО!
    parser_lexer = Lexer(code)
    parser = Parser(parser_lexer)

    ast = parser.parse()
    print(f"AST: {type(ast)}")
    print(f"Количество statements: {len(ast.statements)}")

    for i, stmt in enumerate(ast.statements):
        print(f"Statement {i}: {type(stmt).__name__}")
        if hasattr(stmt, '__dict__'):
            for attr, value in stmt.__dict__.items():
                print(f"    {attr}: {value}")

    # Генератор
    generator = CodeGenerator()
    js_code = generator.generate(ast)
    print("Сгенерированный JS:")
    print(repr(js_code))
    print("Форматированный JS:")
    print(js_code)
    print(f"{'=' * 50}")


# Тестируем
test_pipeline("x = 5", "Простое присваивание")
test_pipeline("result = a + b * c", "Бинарные операции")