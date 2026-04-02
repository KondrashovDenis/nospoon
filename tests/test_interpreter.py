import pytest
import sys
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.interpreter import run_bf, BrainfuckError


def test_simple_output():
    """Простой вывод одного символа A (ASCII 65)"""
    # 65 = 5*13
    bf = '+++++[>+++++++++++++<-]>.'
    result = run_bf(bf)
    assert result == 'A'


def test_hello_world():
    """Классический Hello World на BF"""
    bf = '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.'
    result = run_bf(bf)
    assert result == 'Hello World!\n'


def test_stdin_input():
    """Команда , читает из stdin"""
    bf = ',.'  # прочитать символ и вывести
    result = run_bf(bf, stdin='X')
    assert result == 'X'


def test_infinite_loop_protection():
    """Бесконечный цикл должен бросать исключение"""
    with pytest.raises(BrainfuckError):
        run_bf('+[]', max_steps=1000)


def test_unbalanced_brackets():
    """Несбалансированные скобки должны бросать исключение"""
    with pytest.raises(BrainfuckError):
        run_bf('+++[.')


def test_empty_program():
    """Пустая программа возвращает пустую строку"""
    assert run_bf('') == ''


def test_compiler_interpreter_roundtrip():
    """Полный roundtrip: текст → BF → выполнить → текст"""
    from core.compiler import compile_text

    test_strings = ['Hi', 'A', 'Hello']
    for text in test_strings:
        bf_code = compile_text(text)
        result = run_bf(bf_code)
        assert result == text, f"Roundtrip failed for {text!r}: got {result!r}"
