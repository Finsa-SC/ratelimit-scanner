import datetime
from dataclasses import dataclass
import httpx
import asyncio

@dataclass
class ScanConfig:
    domain: str = None
    timeout: float = 3.0
    burst_size: int = 5

@dataclass
class RequestResult:
    seq: int
    status: int
    sent_at: datetime.datetime
    received_at: datetime.datetime

    @property
    def latency(self):
        return (self.received_at - self.sent_at).total_seconds()

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

    async def _send_tracked(self, client, seq: int) -> RequestResult:
        sent = datetime.datetime.now()
        try:
            res = await client.get(self.url, timeout=self.timeout)
            status = res.status_code
        except Exception:
            status = 999
        return RequestResult(
            seq=seq,
            status=status,
            sent_at=sent,
            received_at=datetime.datetime.now()
        )

    # async def _send_single_request(self, client):
    #     try:
    #         res = await client.get(self.url, timeout=self.timeout)
    #         print(res.status_code)
    #         return res.status_code
    #     except Exception:
    #         return 999
    #

    async def send_burst(self) -> list[RequestResult]:
        print(f"[C] Starting burst attack...")
        results = []
        seq: int = 0

        async with httpx.AsyncClient() as client:
            while True:
                batch = [
                    self._send_tracked(client, seq + i)
                    for i in range(self.burst_size)
                ]
                seq += self.burst_size

                batch_results = await asyncio.gather(*batch)
                results.extend(batch_results)

                if any(r.status != 200 for r in batch_results):
                    break

                print(f"[C] Batch done, total sent: {seq}")
        return results

    def analyze(self, results: list[RequestResult]) -> int:
        sorted_results = sorted(results, key=lambda r: r.sent_at)

        count_200 = 0
        first_fail = None

        for r in sorted_results:
            if r.status == 200:
                count_200 += 1
            else:
                first_fail = r
                break

        print(f"\n{'=' * 40}")
        print(f"  Requests before rate limit : {count_200}")
        print(f"  First non-200 status       : {first_fail.status if first_fail else 'N/A'}")
        print(f"  First non-200 at seq       : {first_fail.seq if first_fail else 'N/A'}")
        print(f"  Total requests fired       : {len(results)}")
        print(f"{'=' * 40}\n")

        return count_200

    async def tire_timing(self):
        start_time = datetime.datetime.now()
        print(f"[C] Waiting for release since {start_time}")
        wait = 1.0

        async with httpx.AsyncClient() as client:
            while True:
                await asyncio.sleep(wait)
                result = await self._send_tracked(client, -1)
                if result.status == 200:
                    return (datetime.datetime.now() - start_time).total_seconds()

                print("[-] Still banned...")

    async def __call__(self, *args, **kwargs):
        results = await self.send_burst()
        count_200 = self.analyze(results)
        ban_time = await self.tire_timing()
        print(f"  Ban duration: {ban_time}")
