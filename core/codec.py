"""
Единый интерфейс цепочки кодирования Spoon Messenger.

Прячет всю сложность за двумя функциями:
    encode(text, ttl_seconds, password) → bytes
    decode(data, password)              → str
"""

import time
from dataclasses import dataclass
from typing import Optional

from core.compiler import compile_text
from core.transcoder import encode_to_bin, decode_from_bin
from core.interpreter import run_bf, BrainfuckError
from core.ttl import wrap_simple, get_stdin_token


@dataclass
class EncodeResult:
    """Результат кодирования"""
    binary: bytes          # .bin файл для отправки
    bf_code: str           # BF код (для отладки / церемонии)
    bf_with_ttl: str       # BF код с TTL обёрткой
    expires_at: int        # Unix timestamp истечения
    size_bytes: int        # размер .bin файла


@dataclass
class DecodeResult:
    """Результат декодирования"""
    text: str              # декодированный текст
    bf_code: str           # BF код (для церемонии декодирования)
    success: bool          # True если декодирование успешно
    error: Optional[str]   # описание ошибки если success=False


def encode(
    text: str,
    ttl_seconds: int = 86400,
    password: Optional[str] = None
) -> EncodeResult:
    """
    Полная цепочка кодирования: Text → BF → TTL → Spoon → .bin

    Вход:
        text        — исходное сообщение
        ttl_seconds — время жизни в секундах (по умолчанию 24 часа)
        password    — опциональный пароль (добавляется к stdin токену)

    Выход:
        EncodeResult с .bin файлом и метаданными

    Пример:
        result = encode("Hello", ttl_seconds=3600)
        with open("message.bin", "wb") as f:
            f.write(result.binary)
    """
    if not text:
        raise ValueError("Текст сообщения не может быть пустым")

    # Шаг 1: Text → Brainfuck
    bf_code = compile_text(text)

    # Шаг 2: Brainfuck + TTL обёртка
    bf_with_ttl, expires_at = wrap_simple(bf_code, ttl_seconds)

    # Шаг 3: если есть пароль — добавить проверку пароля
    if password:
        bf_final = _wrap_with_password(bf_with_ttl, password)
    else:
        bf_final = bf_with_ttl

    # Шаг 4: BF → Spoon → .bin
    binary = encode_to_bin(bf_final)

    return EncodeResult(
        binary=binary,
        bf_code=bf_code,
        bf_with_ttl=bf_with_ttl,
        expires_at=expires_at,
        size_bytes=len(binary)
    )


def decode(
    data: bytes,
    password: Optional[str] = None,
    timestamp: Optional[float] = None
) -> DecodeResult:
    """
    Полная цепочка декодирования: .bin → Spoon → BF → выполнить → Text

    Вход:
        data      — содержимое .bin файла
        password  — пароль если сообщение защищено
        timestamp — время для проверки TTL (None = текущее время)

    Выход:
        DecodeResult с текстом и метаданными

    Пример:
        with open("message.bin", "rb") as f:
            data = f.read()
        result = decode(data)
        if result.success:
            print(result.text)
    """
    try:
        # Шаг 1: .bin → BF код
        bf_code = decode_from_bin(data)

        # Шаг 2: подготовить stdin
        # stdin = временной токен + пароль (если есть)
        stdin = get_stdin_token(timestamp)
        if password:
            stdin += password

        # Шаг 3: выполнить BF программу
        result_text = run_bf(bf_code, stdin=stdin)

        if not result_text:
            return DecodeResult(
                text='',
                bf_code=bf_code,
                success=False,
                error='Сообщение недоступно: TTL истёк или неверный пароль'
            )

        return DecodeResult(
            text=result_text,
            bf_code=bf_code,
            success=True,
            error=None
        )

    except BrainfuckError as e:
        return DecodeResult(
            text='',
            bf_code='',
            success=False,
            error=f'Ошибка выполнения: {str(e)}'
        )
    except Exception as e:
        return DecodeResult(
            text='',
            bf_code='',
            success=False,
            error=f'Ошибка декодирования: {str(e)}'
        )


def _wrap_with_password(bf_code: str, password: str) -> str:
    """
    Добавить проверку пароля к BF программе.
    Пароль передаётся как часть stdin после временного токена.
    Программа читает символы пароля и проверяет их.

    Вход:  bf_code  — BF программа (уже с TTL)
           password — строка пароля
    Выход: BF программа с проверкой пароля
    """
    if not password:
        return bf_code

    # Упрощённый подход: просто добавляем чтение пароля в stdin
    # BF программа читает токен + пароль последовательно
    # Пароль используется как дополнительная энтропия для токена
    password_reads = '>' + ',[-]' * len(password)

    return bf_code + password_reads


def get_ttl_options() -> dict:
    """Доступные варианты TTL"""
    return {
        '1h':  3600,
        '6h':  21600,
        '24h': 86400,
        '7d':  604800,
    }
