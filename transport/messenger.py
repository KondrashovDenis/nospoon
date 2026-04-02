"""
Высокоуровневый интерфейс Spoon Messenger.
Объединяет codec + IPFS + relay в один вызов.
"""

import os
from typing import Optional
from dotenv import load_dotenv

from core.codec import encode, decode, EncodeResult, DecodeResult
from transport.ipfs_client import IPFSClient, IPFSError
from transport.relay_client import RelayClient, RelayError

load_dotenv()


class MessengerError(Exception):
    """Ошибка мессенджера"""
    pass


class SpoonMessenger:
    def __init__(
        self,
        ipfs_client: IPFSClient = None,
        relay_client: RelayClient = None
    ):
        self.ipfs = ipfs_client or IPFSClient()
        self.relay = relay_client or RelayClient()

    def send(
        self,
        text: str,
        circle_key: str,
        ttl_seconds: int = 86400,
        password: Optional[str] = None
    ) -> dict:
        """
        Отправить сообщение в круг.

        Флоу:
            Text → codec.encode → .bin
            .bin → IPFS upload → CID
            CID → relay.publish → круг

        Вход:
            text        — текст сообщения
            circle_key  — ключ круга
            ttl_seconds — время жизни
            password    — опциональный пароль
        Выход:
            dict с cid и метаданными
        """
        try:
            # Шаг 1: кодировать
            encode_result = encode(text, ttl_seconds=ttl_seconds, password=password)

            # Шаг 2: загрузить в IPFS
            cid = self.ipfs.upload(
                encode_result.binary,
                filename='message.bin',
                expires_at=encode_result.expires_at
            )

            # Шаг 3: опубликовать CID в круг
            self.relay.publish(
                circle_key=circle_key,
                cid=cid,
                expires_at=encode_result.expires_at
            )

            return {
                'success': True,
                'cid': cid,
                'expires_at': encode_result.expires_at,
                'size_bytes': encode_result.size_bytes,
                'circle': circle_key,
            }

        except (IPFSError, RelayError) as e:
            raise MessengerError(f"Ошибка отправки: {e}")

    def receive(
        self,
        circle_key: str,
        password: Optional[str] = None
    ) -> list:
        """
        Получить сообщения из круга.

        Флоу:
            relay.get_feed → список CID
            для каждого CID: IPFS download → .bin → codec.decode → текст

        Вход:
            circle_key — ключ круга
            password   — опциональный пароль
        Выход:
            список dict с текстом и метаданными
        """
        try:
            # Шаг 1: получить список CID из relay
            entries = self.relay.get_feed(circle_key)

            if not entries:
                return []

            results = []
            for entry in entries:
                cid = entry.get('cid')
                if not cid:
                    continue

                try:
                    # Шаг 2: скачать .bin из IPFS
                    binary = self.ipfs.download(cid)

                    # Шаг 3: декодировать
                    decode_result = decode(binary, password=password)

                    results.append({
                        'cid': cid,
                        'text': decode_result.text if decode_result.success else None,
                        'success': decode_result.success,
                        'error': decode_result.error,
                        'published_at': entry.get('published_at'),
                        'expires_at': entry.get('expires_at'),
                    })

                except IPFSError as e:
                    results.append({
                        'cid': cid,
                        'text': None,
                        'success': False,
                        'error': str(e),
                        'published_at': entry.get('published_at'),
                        'expires_at': entry.get('published_at'),
                    })

            return results

        except RelayError as e:
            raise MessengerError(f"Ошибка получения сообщений: {e}")

    def get_stats(self) -> dict:
        """Получить статистику сети"""
        return self.relay.get_stats()
