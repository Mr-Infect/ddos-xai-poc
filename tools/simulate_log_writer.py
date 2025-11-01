#!/usr/bin/env python3

import argparse, time, random, ipaddress, sys
from datetime import datetime, timezone

NGINX_FMT = '{ip} - - [{ts}] "GET {path} HTTP/1.1" {status} {bytes} "-" "{ua}"'

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/7.68.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "python-requests/2.25.1"
]

STATUS = [200, 200, 200, 404, 500]

def gen_ip(pool_start_int, idx):
    # return pseudo-random IPv4 from seeded range
    return str(ipaddress.IPv4Address(pool_start_int + (idx % 65535)))

def now_nginx_ts():
    # e.g. 28/Oct/2025:12:34:56 +0000
    dt = datetime.now(timezone.utc)
    return dt.strftime("%d/%b/%Y:%H:%M:%S +0000")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--log', required=True, help='Path to logfile to append to (local)')
    p.add_argument('--qps', type=int, default=100, help='Requests per second to simulate (int)')
    p.add_argument('--duration', type=int, default=30, help='Duration in seconds to run')
    p.add_argument('--unique', type=int, default=100, help='Number of unique source IPs to cycle through')
    p.add_argument('--path', default='/login', help='Target path to simulate')
    p.add_argument('--burst', type=int, default=0, help='Optional burst multiplier for randomness (0 = disabled)')
    args = p.parse_args()

    # seed IP pool base (private block)
    base = int(ipaddress.IPv4Address("10.0.0.1"))
    total = args.qps * args.duration
    unique = max(1, args.unique)
    interval = 1.0 / max(1, args.qps)
    end = time.time() + args.duration
    outfh = open(args.log, 'a', buffering=1)  # line-buffered append

    print(f"[simulator] appending to {args.log} qps={args.qps} duration={args.duration}s unique={unique} path={args.path}")
    try:
        counter = 0
        while time.time() < end:
            start_loop = time.time()
            # optionally emit a small burst
            to_emit = 1
            if args.burst and random.random() < 0.05:
                to_emit = args.burst
            for _ in range(to_emit):
                idx = random.randrange(unique)
                ip = gen_ip(base, idx)
                ts = now_nginx_ts()
                ua = random.choice(USER_AGENTS)
                status = random.choice(STATUS)
                bytes_sent = random.randint(200, 5000)
                line = NGINX_FMT.format(ip=ip, ts=ts, path=args.path, status=status, bytes=bytes_sent, ua=ua)
                outfh.write(line + "\n")
                counter += 1
            # sleep to maintain approximate qps pace
            elapsed = time.time() - start_loop
            sleep_for = max(0, interval - elapsed)
            time.sleep(sleep_for)
    except KeyboardInterrupt:
        print("[simulator] interrupted by user")
    finally:
        outfh.close()
        print(f"[simulator] finished, wrote ~{counter} lines")
        sys.exit(0)

if __name__ == '__main__':
    main()
