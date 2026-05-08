import datetime
from dataclasses import dataclass

import httpx
import asyncio


@dataclass()
class ScanConfig:
    domain: str = None
    timeout: float = 3.0
    burst_size: int = 20

class Detector:
    def __init__(self, config: ScanConfig):
        self.url = config.domain
        self.timeout = config.timeout
        self.burst_size = config.burst_size

    @classmethod
    def gateway(cls, config: ScanConfig):
        if not config.domain.strip().startswith(("http://", "https://")):
            config.domain = f"https://{config.domain}"
        return cls(config)

    async def _send_single_request(self, client):
        try:
            res = await client.get(self.url, timeout=self.timeout)
            return res.status_code
        except Exception:
            return 999


    async def send_burst(self):
        print(f"[C] Starting burst attack...")
        count: int = 0
        async with httpx.AsyncClient() as client:
            while True:
                task = [self._send_single_request(client) for _ in range(self.burst_size)]
                results = await asyncio.gather(*task)

                for status in results:
                    count += 1
                    if status != 200:
                        print(f"[*] Rate limiting triggered at request {count}")
                        return count
                print(f"[C] Total request send: {count}")

    async def tire_timing(self):
        start_time = datetime.datetime.now()
        print(f"[C] Waiting for release since {start_time}")

        async with httpx.AsyncClient() as client:
            while True:
                status = await self._send_single_request(client)
                if status == 200:
                    end_time = datetime.datetime.now()
                    return end_time - start_time

                print("[-] Still banned...")
                await asyncio.sleep(1)

    @staticmethod
    def summary(req: int, ban):
        return (f"Summary"
                f"Total request to ban: {req}"
                f"Ban time            : {ban}")

    async def __call__(self, *args, **kwargs):
        total_request = await self.send_burst()
        ban_time = await self.tire_timing()
        print(self.summary(total_request, ban_time))
