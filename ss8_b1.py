from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
carriers = [
    {"id": 1, "code": "GHN", "name": "Giao Hang Nhanh", "max_weight_capacity": 5000, "status": "ACTIVE"},
    {"id": 2, "code": "GHTK", "name": "Giao Hang Tiet Kiem", "max_weight_capacity": 3000, "status": "ACTIVE"},
    {"id": 3, "code": "VTP", "name": "Viettel Post", "max_weight_capacity": 10000, "status": "SUSPENDED"}
]

shipments = [
    {
        "id": 1,
        "carrier_id": 1,
        "order_reference": "ORD-2026-001",
        "total_weight": 4200,
        "dispatch_date": "2026-07-01",
        "shift": "MORNING"
    }
]

class Carrier(BaseModel):
    code: str
    name: str
    max_weight_capacity: int
    status: str

class Shipment(BaseModel):
    carrier_id: int
    order_reference: str
    total_weight: int
    dispatch_date: str
    shift: str

def find_carrier(carrier_id):
    for carrier in carriers:
        if carrier["id"] == carrier_id:
            return carrier
    return None

@app.post("/carriers")
def create_carrier(carrier: Carrier):
    for c in carriers:
        if c["code"] == carrier.code:
            raise HTTPException(
                status_code=400,
                detail="mã code đã tồn taij"
            )

    if len(carrier.name.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Tên có ít nhất 3 kí tự"
        )

    if carrier.max_weight_capacity <= 0:
        raise HTTPException(
            status_code=400,
            detail="max_weight_capacity phải là số nguyên lớn hơn 0."
        )

    if carrier.status not in ["ACTIVE", "INACTIVE", "SUSPENDED"]:
        raise HTTPException(
            status_code=400,
            detail="KHÔNg hợp lệ"
        )

    new_carrier = {
        "id": len(carriers) + 1,
        "code": carrier.code,
        "name": carrier.name,
        "max_weight_capacity": carrier.max_weight_capacity,
        "status": carrier.status
    }

    carriers.append(new_carrier)
    return new_carrier

@app.get("/carriers")
def get_carriers(keyword="", status="", min_weight=0):

    result = []

    for carrier in carriers:

        if keyword != "":
            if (keyword.lower() not in carrier["code"].lower()
                    and keyword.lower() not in carrier["name"].lower()):
                continue

        if status != "":
            if carrier["status"] != status:
                continue

        if min_weight != 0:
            if carrier["max_weight_capacity"] < min_weight:
                continue

        result.append(carrier)

    return result

@app.get("/carriers/{carrier_id}")
def get_carrier(carrier_id: int):
    carrier = find_carrier(carrier_id)
    if carrier is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy"
        )

    return carrier

@app.put("/carriers/{carrier_id}")
def update_carrier(carrier_id: int, carrier_data: Carrier):
    carrier = find_carrier(carrier_id)
    if carrier is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy"
        )

    for c in carriers:
        if c["id"] != carrier_id and c["code"] == carrier_data.code:
            raise HTTPException(
                status_code=400,
                detail="mã code đã tồn tại"
            )

    carrier["code"] = carrier_data.code
    carrier["name"] = carrier_data.name
    carrier["max_weight_capacity"] = carrier_data.max_weight_capacity
    carrier["status"] = carrier_data.status
    return carrier

@app.delete("/carriers/{carrier_id}")
def delete_carrier(carrier_id: int):
    carrier = find_carrier(carrier_id)
    if carrier is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy"
        )

    carriers.remove(carrier)
    return {
        "message": "Xoá thành công"
    }

@app.post("/shipments")
def create_shipment(shipment: Shipment):
    carrier = find_carrier(shipment.carrier_id)
    if carrier is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy"
        )

    if carrier["status"] != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Carrier không hoạt động"
        )

    if shipment.total_weight <= 0:
        raise HTTPException(
            status_code=400,
            detail="không hợp lệ"
        )

    if shipment.total_weight > carrier["max_weight_capacity"]:
        raise HTTPException(
            status_code=400,
            detail="Khối lượng chuyến hàng total_weight không được phép vượt quá năng lực vận chuyển tối đa"
        )

    if shipment.shift not in ["MORNING", "AFTERNOON", "NIGHT"]:
        raise HTTPException(
            status_code=400,
            detail="không hợp lệ"
        )

    for s in shipments:
        if s["carrier_id"] == shipment.carrier_id and s["dispatch_date"] == shipment.dispatch_date and s["shift"] == shipment.shift:
            raise HTTPException(
                status_code=400,
                detail="không được xếp trùng lịch "
            )

    new_shipment = {
        "id": len(shipments) + 1,
        "carrier_id": shipment.carrier_id,
        "order_reference": shipment.order_reference,
        "total_weight": shipment.total_weight,
        "dispatch_date": shipment.dispatch_date,
        "shift": shipment.shift
    }

    shipments.append(new_shipment)
    return new_shipment

@app.get("/shipments")
def get_shipments():
    return shipments