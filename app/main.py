import argparse
from scanner import Detector, ScanConfig

parser = argparse.ArgumentParser(
    prog="ratelimit-scanner"
)

parser.add_argument(
    "-d",
    "--domain",
    type=str,
    help="Input domain target you want to test"
)
parser.add_argument(
    "--timeout",
    type=float,
    help="Input timeout"
)

args = parser.parse_args()

if args.domain is None:
    print("Invalid domain")
    exit(0)

config = ScanConfig(
    domain=args.domain,
    timeout=args.timeout
)

detect = Detector.gateway(config)
detect()