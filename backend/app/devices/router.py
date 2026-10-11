from fastapi import (
    APIRouter,
    HTTPException,
    status
)

from . import service

from .schema import (
    DeviceCreate,
    DeviceDetectResponse,
    DeviceResponse,
    DeviceUpdate
)


router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)


# ==================================================
# DETECT DEVICE BY IP
# ==================================================

@router.get(
    "/detect/{ip}",
    response_model=DeviceDetectResponse
)
def detect_device(ip: str):

    try:

        return service.detect_ip(ip)

    except Exception as e:

        print(
            f"DETECT DEVICE ERROR: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to detect device type"
        )


# ==================================================
# CREATE DEVICE (AUTO-DETECTS DEVICE TYPE BY IP)
# ==================================================

@router.post(
    "/",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_device(
    data: DeviceCreate
):

    try:

        device = service.create_device(
            name=data.name,
            ip=str(data.ip),
            device_type=data.device_type
        )

        return device

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print(
            f"CREATE DEVICE ERROR: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create device"
        )


# ==================================================
# GET ALL DEVICES
# ==================================================

@router.get(
    "/",
    response_model=list[DeviceResponse]
)
def get_devices():

    try:

        return service.get_devices()

    except Exception as e:

        print(
            f"GET DEVICES ERROR: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to get devices"
        )


# ==================================================
# GET DEVICE BY ID
# ==================================================

@router.get(
    "/{device_id}",
    response_model=DeviceResponse
)
def get_device(
    device_id: int
):

    device = service.get_device(
        device_id
    )

    if device is None:

        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    return device


# ==================================================
# UPDATE DEVICE
# ==================================================

@router.put(
    "/{device_id}",
    response_model=DeviceResponse
)
def update_device(
    device_id: int,
    data: DeviceUpdate
):

    try:

        device = service.update_device(
            device_id=device_id,
            name=data.name,
            ip=(
                str(data.ip)
                if data.ip is not None
                else None
            ),
            device_type=data.device_type
        )

        if device is None:

            raise HTTPException(
                status_code=404,
                detail="Device not found"
            )

        return device

    except HTTPException:
        raise

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print(
            f"UPDATE DEVICE ERROR: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update device"
        )


# ==================================================
# DELETE DEVICE
# ==================================================

@router.delete(
    "/{device_id}"
)
def delete_device(
    device_id: int
):

    try:

        result = service.delete_device(
            device_id
        )

        if result is None:

            raise HTTPException(
                status_code=404,
                detail="Device not found"
            )

        return {
            "message": "Device deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"DELETE DEVICE ERROR: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete device"
        )


# ==================================================
# RE-DETECT DEVICE TYPE FOR EXISTING DEVICE
# ==================================================

@router.post(
    "/{device_id}/redetect",
    response_model=DeviceResponse
)
def redetect_device(
    device_id: int
):

    try:

        device = service.redetect_device(
            device_id
        )

        if device is None:

            raise HTTPException(
                status_code=404,
                detail="Device not found"
            )

        return device

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"REDETECT DEVICE ERROR: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to re-detect device type"
        )