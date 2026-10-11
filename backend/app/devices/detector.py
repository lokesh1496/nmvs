import ipaddress
import re
import socket
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

from app.discovery.ping import check_device_status

# Key ports probed to classify device types
COMMON_PORTS = [
    53,    # DNS (Router / Gateway / Domain Controller)
    80,    # HTTP (Web Management / Web Server / Camera / Router GUI)
    443,   # HTTPS (Web Management / Server / Router GUI)
    8080,  # HTTP Alternate (Management / Web)
    22,    # SSH (Linux Server / Managed Network Appliance)
    23,    # Telnet (Switch / Router / Legacy Device)
    161,   # SNMP (Managed Switch / Router)
    135,   # MSRPC (Windows PC / Server)
    139,   # NetBIOS (Windows PC / Server)
    445,   # SMB (Windows PC / Server)
    3389,  # RDP (Windows Workstation / Server)
    9100,  # RAW JetDirect (Network Printer)
    515,   # LPD (Printer)
    631,   # IPP (Printer)
    554,   # RTSP (IP Camera / CCTV)
    8000,  # Hikvision / Web Management
    37777, # Dahua DVR/NVR
    3306,  # MySQL Database Server
    5432,  # PostgreSQL Database Server
    27017, # MongoDB Server
    6379,  # Redis Server
    1433,  # MSSQL Database Server
]


def check_tcp_port(ip: str, port: int, timeout: float = 0.3) -> bool:
    """Check if a specific TCP port is open on the target IP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((ip, port)) == 0
    except Exception:
        return False


def scan_ports(ip: str, timeout: float = 0.3) -> set[int]:
    """Scan key ports concurrently with short timeouts."""
    open_ports = set()
    with ThreadPoolExecutor(max_workers=min(len(COMMON_PORTS), 20)) as executor:
        future_to_port = {
            executor.submit(check_tcp_port, ip, port, timeout): port
            for port in COMMON_PORTS
        }
        for future in future_to_port:
            port = future_to_port[future]
            try:
                if future.result():
                    open_ports.add(port)
            except Exception:
                pass
    return open_ports


def get_hostname(ip: str, timeout: float = 0.4) -> str | None:
    """Reverse DNS lookup capped by a daemon thread timeout."""
    result = [None]

    def _resolve():
        try:
            name, _, _ = socket.gethostbyaddr(ip)
            result[0] = name
        except Exception:
            pass

    t = threading.Thread(target=_resolve, daemon=True)
    t.start()
    t.join(timeout=timeout)
    return result[0]


def is_default_gateway(ip: str) -> bool:
    """Check if target IP matches system default gateway."""
    try:
        proc = subprocess.run(
            ["route", "print", "0.0.0.0"],
            capture_output=True,
            text=True,
            timeout=0.8
        )
        for match in re.finditer(
            r"0\.0\.0\.0\s+0\.0\.0\.0\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)",
            proc.stdout
        ):
            if match.group(1) == ip:
                return True
    except Exception:
        pass
    return False


def is_likely_gateway_ip(ip_str: str) -> bool:
    """Check if IPv4 address commonly designates a router/gateway (.1 or .254)."""
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.version == 4:
            last_octet = int(str(ip_obj).split(".")[-1])
            return last_octet in (1, 254)
    except Exception:
        pass
    return False


def get_mac_address(ip: str) -> str | None:
    """Read ARP cache for MAC address if on local network."""
    try:
        proc = subprocess.run(
            ["arp", "-a", ip],
            capture_output=True,
            text=True,
            timeout=0.6
        )
        match = re.search(
            r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}",
            proc.stdout
        )
        if match:
            return match.group(0).lower().replace("-", ":")
    except Exception:
        pass
    return None


def grab_http_banner(ip: str, port: int = 80, timeout: float = 0.5) -> str:
    """Grab HTTP banner / response text to inspect device signatures."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))
            req = f"GET / HTTP/1.0\r\nHost: {ip}\r\nUser-Agent: NMVS\r\n\r\n"
            s.sendall(req.encode("utf-8", errors="ignore"))
            data = s.recv(2048)
            return data.decode("utf-8", errors="ignore").lower()
    except Exception:
        return ""


def detect_device_info(ip: str) -> dict:
    """
    Run automated detection heuristics on an IP address.
    Returns full diagnostics and the detected device type.
    """
    ip_str = str(ip).strip()

    try:
        ip_obj = ipaddress.ip_address(ip_str)
    except ValueError:
        return {
            "ip": ip_str,
            "device_type": "Unknown Device",
            "status": "Offline",
            "hostname": None,
            "open_ports": [],
            "mac_address": None,
            "is_gateway": False
        }

    # Special handling: Loopback address
    if ip_obj.is_loopback:
        return {
            "ip": ip_str,
            "device_type": "Server",
            "status": "Online",
            "hostname": get_hostname(ip_str) or "localhost",
            "open_ports": sorted(list(scan_ports(ip_str))),
            "mac_address": None,
            "is_gateway": False
        }

    # Run port scan and reachability / DNS concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_ports = executor.submit(scan_ports, ip_str)
        f_ping = executor.submit(check_device_status, ip_str)
        f_host = executor.submit(get_hostname, ip_str)

        open_ports = f_ports.result()
        ping_res = f_ping.result()
        hostname = f_host.result()

    is_online = (ping_res.get("status") == "Online") or len(open_ports) > 0
    mac_address = get_mac_address(ip_str)
    is_gateway = is_default_gateway(ip_str) or is_likely_gateway_ip(ip_str)

    host_lower = (hostname or "").lower()

    # Grab HTTP banner if port 80 or 8080 is open
    banner = ""
    for p in (80, 8080):
        if p in open_ports:
            banner = grab_http_banner(ip_str, p)
            if banner:
                break

    device_type = _classify_device_type(
        open_ports=open_ports,
        hostname=host_lower,
        banner=banner,
        is_gateway=is_gateway,
        is_online=is_online
    )

    return {
        "ip": ip_str,
        "device_type": device_type,
        "status": "Online" if is_online else "Offline",
        "hostname": hostname,
        "open_ports": sorted(list(open_ports)),
        "mac_address": mac_address,
        "is_gateway": is_gateway
    }


def _classify_device_type(
    open_ports: set[int],
    hostname: str,
    banner: str,
    is_gateway: bool,
    is_online: bool
) -> str:
    """Internal classifier mapping network signatures to clean device types."""

    # 1. Network Printer
    printer_ports = {9100, 515, 631}
    printer_keywords = (
        "printer", "cups", "jetdirect", "epson", "brother",
        "canon", "xerox", "laserjet", "deskjet", "officejet"
    )
    if open_ports.intersection(printer_ports) or any(
        k in hostname or k in banner for k in printer_keywords
    ):
        return "Printer"

    # 2. IP Camera / CCTV
    camera_ports = {554, 37777}
    camera_keywords = (
        "camera", "cctv", "dvr", "nvr", "hikvision",
        "dahua", "amcrest", "reolink", "axis", "webcam"
    )
    if open_ports.intersection(camera_ports) or any(
        k in hostname or k in banner for k in camera_keywords
    ):
        return "IP Camera"

    # 3. Router / Gateway
    router_keywords = (
        "router", "gateway", "openwrt", "asuswrt", "tplink",
        "tp-link", "netgear", "d-link", "linksys", "mikrotik",
        "dd-wrt", "huawei", "tenda", "zyxel", "fritz"
    )
    if any(k in hostname or k in banner for k in router_keywords):
        return "Router"

    # Gateway IP with typical router management ports or DNS
    if is_gateway and (
        53 in open_ports or
        80 in open_ports or
        443 in open_ports or
        8080 in open_ports or
        23 in open_ports
    ):
        return "Router"

    # Standalone DNS service (without Windows domain services)
    if 53 in open_ports and not any(
        p in open_ports for p in (135, 139, 445, 3389)
    ):
        return "Router"

    # 4. Network Switch
    switch_keywords = ("switch", "catalyst", "procurve", "managed switch")
    if any(k in hostname or k in banner for k in switch_keywords):
        return "Switch"
    if (23 in open_ports or 161 in open_ports) and not any(
        p in open_ports for p in (135, 139, 445, 3389)
    ):
        return "Switch"

    # 5. Database / Application Server
    db_ports = {3306, 5432, 27017, 6379, 1433}
    if open_ports.intersection(db_ports):
        return "Server"

    server_keywords = (
        "server", "srv", "linux", "ubuntu", "debian", "centos",
        "redhat", "nas", "synology", "qnap", "truenas", "freenas"
    )
    if any(k in hostname or k in banner for k in server_keywords):
        return "Server"

    # SSH open with no workstation ports
    if 22 in open_ports and not any(
        p in open_ports for p in (135, 139, 445, 3389)
    ):
        return "Server"

    # 6. Workstation / PC
    workstation_keywords = (
        "desktop", "laptop", "pc", "hp15", "win-",
        "macbook", "imac", "workstation", "surface"
    )
    if any(k in hostname for k in workstation_keywords):
        return "Workstation"

    if any(p in open_ports for p in (135, 139, 445, 3389)):
        return "Workstation"

    # 7. Mobile Device
    mobile_keywords = ("phone", "android", "iphone", "ipad", "galaxy", "pixel")
    if any(k in hostname for k in mobile_keywords):
        return "Mobile Device"

    # 8. Gateway heuristic fallback
    if is_gateway:
        return "Router"

    # 9. Generic active device
    if is_online or open_ports:
        return "Network Device"

    # 10. Fallback for completely unreachable / offline
    return "Unknown Device"


def detect_device_type(ip: str) -> str:
    """Convenience function returning the classified device type string."""
    info = detect_device_info(ip)
    return info.get("device_type", "Unknown Device")
