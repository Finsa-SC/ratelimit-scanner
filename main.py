import requests
import time
import datetime

class Detector:
    def __init__(self, domain: str, timeout: float = 3.0):
        self.url = f"https://{domain}/"
        self.domain = domain
        self.timeout = timeout
        self.output = []

    def _send_request(self):
        try:
            res = requests.get(self.url, timeout=self.timeout)
            return res
        except requests.exceptions.RequestException as e:
            print(f"[x] {self.domain}: {e}")
            exit(1)

    def start_bruteforce(self):
        count = 0
        status = None
        while status == 200 or status is None:
            status = self._send_request().status_code
            count += 1

        self.output.append(f"[*] {count} requests send until rate limiting")
        self.tire_timing()

    def tire_timing(self):
        start_time = datetime.datetime.now()
        end_time = None
        while True:
            res = self._send_request()
            if res.status_code == 200:
                end_time = datetime.datetime.now()
                break
            time.sleep(1)

        self.output.append(f"[*] Tire Timing: {end_time-start_time}s")

    def __call__(self, *args, **kwargs):
        self.start_bruteforce()
        for output in self.output:
            print(output)


if __name__ == "__main__":
    send = Detector("mdigi.tech")
    send()