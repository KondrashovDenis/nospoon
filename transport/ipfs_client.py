"""
IPFS клиент для Spoon Messenger через Pinata.
Загрузка и скачивание .bin файлов.
"""

import os
import io
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv(override=True)

PINATA_JWT = os.getenv('PINATA_JWT', '')
PINATA_GATEWAY_DOMAIN = os.getenv('PINATA_GATEWAY_DOMAIN', 'moccasin-immense-bandicoot-136.mypinata.cloud')
# v2 pinning API — файлы доступны через dedicated gateway
PINATA_PIN_URL = 'https://api.pinata.cloud/pinning/pinFileToIPFS'
IPFS_GATEWAY_URL = f'https://{PINATA_GATEWAY_DOMAIN}/ipfs'


class IPFSError(Exception):
    """Ошибка IPFS клиента"""
    pass


class IPFSClient:
    def __init__(self, jwt: str = None):
        self.jwt = jwt or PINATA_JWT
        if not self.jwt:
            raise IPFSError("PINATA_JWT не найден в .env")

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.jwt}'
        })

    def upload(
        self,
        data: bytes,
        filename: str = 'message.bin',
        expires_at: Optional[int] = None
    ) -> str:
        """
        Загрузить .bin файл в IPFS через Pinata (v2 pinning API).

        Вход:
            data       — содержимое .bin файла
            filename   — имя файла
            expires_at — Unix timestamp истечения (для метаданных)
        Выход:
            CID хэш строкой (IpfsHash)
        """
        try:
            files = {
                'file': (filename, io.BytesIO(data), 'application/octet-stream')
            }

            if expires_at:
                import json
                files['pinataMetadata'] = (
                    None,
                    json.dumps({'name': filename, 'keyvalues': {'expires_at': str(expires_at)}}),
                    'application/json'
                )

            response = self.session.post(
                PINATA_PIN_URL,
                files=files,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # v2 API возвращает IpfsHash
            cid = result.get('IpfsHash')
            if not cid:
                raise IPFSError(f"CID не найден в ответе: {result}")

            return cid

        except requests.RequestException as e:
            raise IPFSError(f"Ошибка загрузки в IPFS: {e}")

    def download(self, cid: str) -> bytes:
        """
        Скачать .bin файл из IPFS по CID через dedicated gateway (с JWT).

        Вход:
            cid — IPFS CID хэш
        Выход:
            bytes содержимое файла
        """
        url = f"{IPFS_GATEWAY_URL}/{cid}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.content

        except requests.RequestException as e:
            raise IPFSError(f"Ошибка скачивания из IPFS: {e}")

    def get_file_list(self) -> list:
        """
        Получить список загруженных файлов (v2 API).
        """
        try:
            response = self.session.get(
                'https://api.pinata.cloud/data/pinList?status=pinned&pageLimit=10',
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('rows', [])

        except requests.RequestException as e:
            raise IPFSError(f"Ошибка получения списка файлов: {e}")


def get_ipfs_client() -> IPFSClient:
    """Фабричная функция — получить настроенный клиент"""
    return IPFSClient()
