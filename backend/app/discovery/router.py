import ipaddress

from fastapi import APIRouter, HTTPException

from . import service


router = APIRouter(
    prefix="/discovery",
    tags=["Discovery"]
)


@router.get("/ping/{ip}")
def ping(ip: str):

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid IP address"
        )

    return service.check_device(ip)


@router.get("/scan")
def scan(network: str):

    try:
        ipaddress.ip_network(
            network,
            strict=False
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid network address"
        )

    devices = service.discover_network(network)

    return {
        "status": "success",
        "network": network,
        "count": len(devices),
        "devices": devices
    }