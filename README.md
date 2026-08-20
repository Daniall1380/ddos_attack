====================================================
        DDoS - tool v3.1
        made by BHH
====================================================

•run as Linux
 
```sudo git clone https://github.com/Daniall1380/ddos_attack.git```

```cd ddos_attack```

```sudo chmod +x ddos.py```

```python DDoS.py```

•run as termux

```git clone https://github.com/Daniall1380/ddos_attack.git```

```cd ddos_attack```

```chmod +x ddos.py```

```python DDoS.py```

[ DESCRIPTION ]
DDoSH is a multi-vector network stress testing tool
designed for authorized security assessments only.
It supports 6 attack modes for testing server resilience
under various traffic patterns.

[ REQUIREMENTS ]
- Termux (Android) or any Linux terminal
- Python 3.8+
- No additional packages required (uses built-in modules)

[ INSTALLATION ]
1. Update packages:
   pkg update && pkg upgrade -y

2. Install Python:
   pkg install python -y

3. Create the script file:
   nano ddos.py

4. Paste the entire script content into the file.
   Save with Ctrl+X, then Y, then Enter.

5. Make it executable (optional):
   chmod +x ddos.py

[ QUICK START - One-liner ]
python ddos.py <target> <port> <threads> <mode> <duration>

Examples:
  python ddos.py example.com 443 500 http 60
  python ddos.py 192.168.1.100 80 800 auto 120
  python ddos.py example.com 8443 1000 combo 300

[ PARAMETERS ]
  target    = Domain name or IP address
  port      = Target port (80, 443, 8080, etc.)
  threads   = Number of concurrent threads (200-1000)
  mode      = Attack vector type (see modes below)
  duration  = Test duration in seconds (0 = unlimited)

[ ATTACK MODES ]
  1. HTTP     - Layer 7 HTTP/HTTPS request flood
               Sends GET/POST requests with random
               headers, paths, and user-agents.

  2. SLOWRIS  - Slowloris-style attack
               Opens connections and sends HTTP headers
               very slowly to exhaust server connection pool.

  3. TLS      - TLS handshake exhaustion
               Repeatedly opens SSL/TLS connections
               to consume CPU resources on HTTPS servers.

  4. UDP      - UDP packet flood
               Sends random UDP packets to the target
               Useful for non-HTTP services and game servers.

  5. COMBO    - Random cycle through all modes
               Automatically switches between HTTP,
               Slowloris, TLS, and UDP randomly.

  6. AUTO     - Smart mode selection
               Automatically chooses best mode based
               on port number (80→HTTP, 443→COMBO, else→UDP)

[ INTERACTIVE MODE ]
If you run the script without arguments:
  python ddos.py

It will ask for each parameter step by step.

[ TIPS FOR BEST PERFORMANCE ]
- For Termux, keep threads between 400-800 (max ~1024)
- Use "combo" mode for HTTPS targets (port 443)
- Use "http" mode for HTTP targets (port 80)
- Set a duration limit (60-300s) to avoid hanging
- On WiFi, use proxy lists to distribute traffic
- For slowloris, fewer threads (200-400) work better
- Run multiple instances in different Termux sessions:
    python ddos.py target1.com 443 500 http 120 &
    python ddos.py target1.com 443 500 slowris 120 &

[ MONITORING ]
While running, you will see live stats:
  Sent: 45,832 | Errors: 231 | Rate: 382/s | BW: 2.3 Mbps | Time: 120s

  Sent    = Total requests/packets sent
  Errors  = Failed connections/requests
  Rate    = Requests per second
  BW      = Approximate bandwidth usage
  Time    = Elapsed test duration

[ STOP ]
Press Ctrl+C at any time to stop the attack.
Stats will be displayed after stopping.

made by BHH
====================================================