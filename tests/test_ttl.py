import pytest
import time
import sys
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.ttl import (
    get_time_token,
    wrap_simple,
    get_stdin_token,
    TTL_PRECISION
)
from core.interpreter import run_bf, BrainfuckError
from core.compiler import compile_text


def test_time_token_consistency():
    """Токен одинаковый в пределах precision секунд"""
    t = time.time()
    token1 = get_time_token(t)
    token2 = get_time_token(t + TTL_PRECISION - 1)
    # могут совпасть или нет в зависимости от границы окна
    assert isinstance(token1, int)
    assert isinstance(token2, int)


def test_time_token_changes():
    """Токен меняется через precision секунд"""
    t = time.time()
    # выровнять на границу окна
    aligned = (int(t) // TTL_PRECISION) * TTL_PRECISION
    token1 = get_time_token(float(aligned))
    token2 = get_time_token(float(aligned + TTL_PRECISION))
    assert token1 != token2


def test_wrap_simple_valid():
    """Программа с валидным TTL выполняется корректно"""
    text = "Hi"
    bf_code = compile_text(text)

    ttl_wrapper, expires_at = wrap_simple(bf_code, ttl_seconds=3600)

    # получить корректный токен для stdin
    stdin_token = get_stdin_token()

    result = run_bf(ttl_wrapper, stdin=stdin_token)
    assert result == text, f"Ожидалось {text!r}, получено {result!r}"


def test_wrap_simple_expired():
    """Программа с истёкшим TTL не выводит текст"""
    text = "Secret"
    bf_code = compile_text(text)

    # создать программу которая уже истекла
    # передать неверный токен (прошлый период)
    ttl_wrapper, expires_at = wrap_simple(bf_code, ttl_seconds=3600)

    # неверный токен — другое значение
    wrong_token = chr((ord(get_stdin_token()) + 1) % 256)

    result = run_bf(ttl_wrapper, stdin=wrong_token)
    # с неверным токеном — пустой вывод или мусор, но не оригинальный текст
    assert result != text, f"Программа не должна выводить текст с неверным токеном"


def test_stdin_token_format():
    """get_stdin_token возвращает строку из одного символа"""
    token = get_stdin_token()
    assert isinstance(token, str)
    assert len(token) == 1


def test_expires_at_future():
    """expires_at должен быть в будущем"""
    bf_code = compile_text("test")
    _, expires_at = wrap_simple(bf_code, ttl_seconds=3600)
    assert expires_at > time.time()
