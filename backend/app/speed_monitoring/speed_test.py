

import speedtest


def run_speed_test(ip: str = "internet") -> dict:
    """
    Run an Internet Speed Test using python speedtest-cli.
    Measures download speed (Mbps), upload speed (Mbps), and ping latency (ms).
    """
    ip_str = str(ip).strip() if ip else "internet"

    try:
        st = speedtest.Speedtest(secure=True)
        st.get_best_server()

        download_bps = st.download()
        upload_bps = st.upload()
        results = st.results.dict()

        ping_val = results.get("ping")
        ping_ms = round(float(ping_val), 2) if ping_val is not None else None

        server_info = results.get("server", {})
        sponsor = server_info.get("sponsor")
        server_name = server_info.get("name")
        server_label = (
            f"{sponsor} ({server_name})"
            if sponsor and server_name
            else (sponsor or server_name)
        )

        return {
            "ip": ip_str,
            "download_mbps": round(download_bps / 1_000_000, 2),
            "upload_mbps": round(upload_bps / 1_000_000, 2),
            "ping_ms": ping_ms,
            "server": server_label,
            "isp": results.get("client", {}).get("isp"),
            "client_ip": results.get("client", {}).get("ip"),
            "error": None
        }

    except Exception as e:
        return {
            "ip": ip_str,
            "download_mbps": None,
            "upload_mbps": None,
            "ping_ms": None,
            "server": None,
            "isp": None,
            "client_ip": None,
            "error": f"Speed test failed: {str(e)}"
        }