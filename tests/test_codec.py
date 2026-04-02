import pytest
import time
import sys
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.codec import encode, decode, get_ttl_options, EncodeResult, DecodeResult


def test_encode_returns_result():
    """encode возвращает EncodeResult с корректными полями"""
    result = encode("Hello", ttl_seconds=3600)
    assert isinstance(result, EncodeResult)
    assert isinstance(result.binary, bytes)
    assert len(result.binary) > 0
    assert isinstance(result.bf_code, str)
    assert len(result.bf_code) > 0
    assert result.expires_at > time.time()
    assert result.size_bytes == len(result.binary)


def test_decode_success():
    """Полный roundtrip encode → decode"""
    text = "Hello"
    encoded = encode(text, ttl_seconds=3600)
    decoded = decode(encoded.binary)
    assert decoded.success is True
    assert decoded.text == text
    assert isinstance(decoded.bf_code, str)


def test_decode_various_texts():
    """Roundtrip для разных текстов"""
    texts = ["Hi", "Hello World", "Test 123", "A"]
    for text in texts:
        encoded = encode(text, ttl_seconds=3600)
        decoded = decode(encoded.binary)
        assert decoded.success is True
        assert decoded.text == text, f"Failed for {text!r}"


def test_encode_empty_text_raises():
    """Пустой текст вызывает ValueError"""
    with pytest.raises(ValueError):
        encode("")


def test_encode_with_password():
    """encode с паролем возвращает корректный результат"""
    result = encode("Secret", ttl_seconds=3600, password="key123")
    assert isinstance(result.binary, bytes)
    assert len(result.binary) > 0


def test_decode_with_password():
    """Roundtrip с паролем"""
    text = "Secret message"
    password = "mypassword"
    encoded = encode(text, ttl_seconds=3600, password=password)
    decoded = decode(encoded.binary, password=password)
    assert decoded.success is True
    assert decoded.text == text


def test_decode_wrong_token_fails():
    """Неверный временной токен → success=False"""
    encoded = encode("Hello", ttl_seconds=3600)
    # передать неверное время (далёкое прошлое)
    past_time = time.time() - 999999
    decoded = decode(encoded.binary, timestamp=past_time)
    assert decoded.success is False
    assert decoded.text == ""


def test_get_ttl_options():
    """get_ttl_options возвращает словарь с корректными значениями"""
    options = get_ttl_options()
    assert '1h' in options
    assert '24h' in options
    assert options['1h'] == 3600
    assert options['24h'] == 86400
