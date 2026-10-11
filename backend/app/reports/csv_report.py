import csv
import io


def generate_devices_csv(devices: list) -> str:
    """Generate CSV string of network devices inventory."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Device ID", "Name", "IP Address", "Device Type", "Registered At"])

    for d in devices:
        writer.writerow([
            d.id,
            d.name,
            d.ip,
            d.device_type,
            d.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(d, "created_at", None) else "N/A"
        ])

    return output.getvalue()
