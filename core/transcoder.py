# Таблица замен BF → Spoon (префиксный код)
BF_TO_SPOON = {
    '+':  '1',
    '-':  '000',
    '>':  '010',
    '<':  '0110',
    '[':  '00110',
    ']':  '0111',
    '.':  '001110',
    ',':  '0011110',
}

# Обратная таблица Spoon → BF (для декодирования)
SPOON_TO_BF = {v: k for k, v in BF_TO_SPOON.items()}


def bf_to_spoon(bf_code: str) -> str:
    """
    Перекодировать BF код в Spoon битовую строку.

    Вход:  "++++++++[>+++++++++<-]>."
    Выход: "11111111001100101111111110110000011100101110"
    """
    result = []
    for char in bf_code:
        if char in BF_TO_SPOON:
            result.append(BF_TO_SPOON[char])
        # остальные символы игнорируются (комментарии в BF)
    return ''.join(result)


def spoon_to_bf(spoon_bits: str) -> str:
    """
    Декодировать Spoon битовую строку обратно в BF код.
    Читает биты слева направо, жадно сопоставляет префиксы.

    Вход:  "11111111001100101111111110110000011100101110"
    Выход: "++++++++[>+++++++++<-]>."
    """
    result = []
    i = 0
    while i < len(spoon_bits):
        matched = False
        # пробуем префиксы от короткого к длинному (1..7 бит)
        for length in range(1, 8):
            prefix = spoon_bits[i:i+length]
            if prefix in SPOON_TO_BF:
                result.append(SPOON_TO_BF[prefix])
                i += length
                matched = True
                break
        if not matched:
            # неизвестный префикс — пропускаем бит
            i += 1
    return ''.join(result)


def bits_to_bytes(bits: str) -> bytes:
    """
    Упаковать битовую строку в байты (дополнить нулями до кратности 8).

    Вход:  "10110011"
    Выход: b'\xb3'
    """
    # дополнить до кратности 8
    padding = (8 - len(bits) % 8) % 8
    bits_padded = bits + '0' * padding

    result = []
    for i in range(0, len(bits_padded), 8):
        byte = int(bits_padded[i:i+8], 2)
        result.append(byte)

    return bytes(result)


def bytes_to_bits(data: bytes) -> str:
    """
    Распаковать байты в битовую строку.

    Вход:  b'\xb3'
    Выход: "10110011"
    """
    return ''.join(format(byte, '08b') for byte in data)


def encode_to_bin(bf_code: str) -> bytes:
    """
    Полный путь: BF код → Spoon биты → бинарные байты (.bin файл)

    Формат: [4 байта big-endian: кол-во бит][данные]
    Заголовок позволяет точно отсечь паддинг при декодировании.

    Вход:  BF код строкой
    Выход: bytes для записи в .bin файл
    """
    spoon_bits = bf_to_spoon(bf_code)
    bit_count = len(spoon_bits)
    payload = bits_to_bytes(spoon_bits)
    header = bit_count.to_bytes(4, byteorder='big')
    return header + payload


def decode_from_bin(data: bytes) -> str:
    """
    Обратный путь: бинарные байты → Spoon биты → BF код

    Вход:  bytes из .bin файла (с 4-байтным заголовком длины)
    Выход: BF код строкой
    """
    bit_count = int.from_bytes(data[:4], byteorder='big')
    spoon_bits = bytes_to_bits(data[4:])[:bit_count]
    return spoon_to_bf(spoon_bits)
