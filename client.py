import socket
import time
import argparse 
import threading 
import math


PROXY_HOST = "192.168.1.11"       
PROXY_PORT = 8080

WEB_HOST = "192.168.1.10"         
UDP_PORT = 9000

BUFFER = 4096


def tcp(path="/index.html"):
    try:
        start = time.time()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((PROXY_HOST, PROXY_PORT))

        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {PROXY_HOST}\r\n"
            f"Connection: close\r\n\r\n"
        )

        s.sendall(req.encode())

        res = b""
        while True:
            data = s.recv(BUFFER)
            if not data:
                break
            res += data

        s.close()

        text = res.decode(errors="ignore")
        status = text.split("\r\n")[0]

        print("Mode TCP")
        print("Status:", status)
        print("Response time:", round(time.time() - start, 4), "detik")
        print("Ukuran response:", len(res), "bytes")
        print("\nIsi response:\n", text)

    except Exception as e:
        print("Error TCP:", e)


def udp():
    rtts = []
    sent = 10
    received = 0
    total_bytes = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)

    print("Mode UDP QoS")

    start_total = time.time()

    for i in range(1, sent + 1):
        msg = f"ping {i} {time.time()}"

        try:
            start = time.time()
            s.sendto(msg.encode(), (WEB_HOST, UDP_PORT))
            data, _ = s.recvfrom(BUFFER)

            rtt = time.time() - start
            rtts.append(rtt)
            received += 1
            total_bytes += len(data)

            print("Packet", i, "RTT", round(rtt, 4), "detik")

        except socket.timeout:
            print("Packet", i, "timeout")

    s.close()

    total_time = time.time() - start_total
    lost = sent - received
    loss = lost / sent * 100

    if rtts:
        min_rtt = min(rtts)
        avg_rtt = sum(rtts) / len(rtts)
        max_rtt = max(rtts)
    else:
        min_rtt = avg_rtt = max_rtt = 0

    diff = [rtts[i] - rtts[i - 1] for i in range(1, len(rtts))]
    jitter = math.sqrt(sum(x * x for x in diff) / len(diff)) if diff else 0

    throughput = (total_bytes * 8) / (total_time * 1000) if total_time > 0 else 0

    print("\nStatistik QoS")
    print("Min RTT:", round(min_rtt, 4), "detik")
    print("Avg RTT:", round(avg_rtt, 4), "detik")
    print("Max RTT:", round(max_rtt, 4), "detik")
    print("Jitter:", round(jitter, 6), "detik")
    print("Throughput:", round(throughput, 4), "kbps")
    print("Packet dikirim:", sent)
    print("Packet diterima:", received)
    print("Packet hilang:", lost)
    print("Packet loss:", round(loss, 2), "%")


def multi(path="/index.html"):
    print("Mode Multi Client")

    threads = []

    for i in range(5):
        t = threading.Thread(target=tcp, args=(path,))
        threads.append(t)
        t.start()
        print("Client", i + 1, "dijalankan")

    for t in threads:
        t.join()

    print("Semua client selesai")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["tcp", "udp", "multi"], required=True)
    parser.add_argument("--path", default="/index.html")
    args = parser.parse_args()

    if args.mode == "tcp":
        tcp(args.path)
    elif args.mode == "udp":
        udp()
    elif args.mode == "multi":
        multi(args.path)


if __name__ == "__main__":
    main()