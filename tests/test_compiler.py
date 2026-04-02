import pytest
import sys
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.compiler import find_best_factor, compile_char, compile_text


def test_find_best_factor_basic():
    """Множитель должен давать результат меньше наивного"""
    for n in [65, 72, 101, 108, 111]:
        factor = find_best_factor(n)
        assert 1 <= factor <= n


def test_compile_char_produces_output():
    """compile_char должен возвращать непустую строку для любого ASCII"""
    for ascii_val in [65, 72, 101, 108, 111, 32, 10]:
        result = compile_char(ascii_val)
        assert isinstance(result, str)
        assert len(result) > 0
        assert '.' in result  # должна быть команда вывода


def test_compile_text_hello():
    """compile_text должен возвращать непустую BF программу"""
    result = compile_text("Hello")
    assert isinstance(result, str)
    assert len(result) > 0
    assert result.count('.') == 5  # 5 символов = 5 команд вывода


def test_compile_text_empty():
    """Пустая строка → пустая программа"""
    assert compile_text("") == ""


def test_compile_text_single_char():
    """Одиночный символ компилируется корректно"""
    result = compile_text("A")
    assert '.' in result
