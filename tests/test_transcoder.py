import pytest
import sys
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.transcoder import (
    bf_to_spoon, spoon_to_bf,
    bits_to_bytes, bytes_to_bits,
    encode_to_bin, decode_from_bin
)


def test_bf_to_spoon_single_commands():
    """Каждая BF команда кодируется корректно"""
    assert bf_to_spoon('+') == '1'
    assert bf_to_spoon('-') == '000'
    assert bf_to_spoon('>') == '010'
    assert bf_to_spoon('<') == '0110'
    assert bf_to_spoon('[') == '00110'
    assert bf_to_spoon(']') == '0111'
    assert bf_to_spoon('.') == '001110'
    assert bf_to_spoon(',') == '0011110'


def test_spoon_to_bf_single_commands():
    """Каждый Spoon префикс декодируется обратно"""
    assert spoon_to_bf('1') == '+'
    assert spoon_to_bf('000') == '-'
    assert spoon_to_bf('010') == '>'
    assert spoon_to_bf('0110') == '<'
    assert spoon_to_bf('00110') == '['
    assert spoon_to_bf('0111') == ']'
    assert spoon_to_bf('001110') == '.'
    assert spoon_to_bf('0011110') == ','


def test_roundtrip_simple():
    """BF → Spoon → BF должен давать оригинал"""
    original = '+++++[>++++<-]>.'
    spoon = bf_to_spoon(original)
    restored = spoon_to_bf(spoon)
    assert restored == original


def test_roundtrip_bin():
    """BF → bytes → BF должен давать оригинал"""
    original = '+++++[>++++<-]>.'
    binary = encode_to_bin(original)
    assert isinstance(binary, bytes)
    restored = decode_from_bin(binary)
    assert restored == original


def test_bits_to_bytes_roundtrip():
    """bits → bytes → bits должен давать оригинал (с учётом паддинга)"""
    bits = '10110011' * 3
    data = bits_to_bytes(bits)
    restored = bytes_to_bits(data)
    assert restored == bits


def test_encode_produces_bytes():
    """encode_to_bin должен возвращать bytes"""
    result = encode_to_bin('+++.')
    assert isinstance(result, bytes)
    assert len(result) > 0
