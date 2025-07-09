from fastapi import FastAPI, HTTPException, Query
import boto3
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from calendar import monthrange

load_dotenv()

app = FastAPI()

dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'ap-northeast-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'dummy'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'dummy'),
    endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL', 'http://dynamodb-local:8000')
)

# --- Pydantic Models ---
class ReservationCreate(BaseModel):
    name: str
    email: EmailStr
    date: str  # yyyy-MM-dd
    seats: int

class Reservation(ReservationCreate):
    id: str
    created_at: str

class Seat(BaseModel):
    date: str  # yyyy-MM-dd
    seats: int

class Holiday(BaseModel):
    date: str  # yyyy-MM-dd

class DefaultSeat(BaseModel):
    seats: int

class DefaultHoliday(BaseModel):
    weekdays: List[int]  # 0=月曜, 6=日曜

# --- API Endpoints ---

# ユーザー用
@app.get("/api/seat/")
def get_seats(month: str = Query(..., description="yyyy/MM")):
    """指定月の日毎の席数一覧取得"""
    seats_table = dynamodb.Table('seats')
    default_seat_table = dynamodb.Table('default_seat')
    # 月の日付リストを作成
    year, mon = map(int, month.split("/"))
    num_days = monthrange(year, mon)[1]
    dates = [f"{year:04d}-{mon:02d}-{d:02d}" for d in range(1, num_days+1)]
    # デフォルト席数取得
    default_resp = default_seat_table.get_item(Key={"id": "default"})
    default_seats = default_resp["Item"]["seats"] if "Item" in default_resp else 0
    # 各日付の席数を取得
    result = []
    for date in dates:
        seat_resp = seats_table.get_item(Key={"date": date})
        seats = seat_resp["Item"]["seats"] if "Item" in seat_resp else default_seats
        result.append({"date": date, "seats": seats})
    return result

@app.get("/api/holiday/")
def get_holidays(month: str = Query(..., description="yyyy/MM")):
    """指定月の日毎の休日一覧取得"""
    holidays_table = dynamodb.Table('holidays')
    default_holiday_table = dynamodb.Table('default_holiday')
    year, mon = map(int, month.split("/"))
    num_days = monthrange(year, mon)[1]
    dates = [f"{year:04d}-{mon:02d}-{d:02d}" for d in range(1, num_days+1)]
    # デフォルト休日（曜日リスト）取得
    default_resp = default_holiday_table.get_item(Key={"id": "default"})
    default_weekdays = default_resp["Item"]["weekdays"] if "Item" in default_resp else []
    # 各日付の休日判定
    result = []
    for date in dates:
        holiday_resp = holidays_table.get_item(Key={"date": date})
        if "Item" in holiday_resp:
            is_holiday = True
        else:
            # デフォルト休日（曜日）
            dt = datetime.strptime(date, "%Y-%m-%d")
            is_holiday = dt.weekday() in default_weekdays
        if is_holiday:
            result.append({"date": date})
    return result

@app.post("/api/reservations", response_model=Reservation)
def create_reservation(reservation: ReservationCreate):
    """予約登録"""
    reservations_table = dynamodb.Table('reservations')
    seats_table = dynamodb.Table('seats')
    default_seat_table = dynamodb.Table('default_seat')

    # 1. 指定日の席数を取得
    seat_resp = seats_table.get_item(Key={"date": reservation.date})
    if "Item" in seat_resp:
        max_seats = seat_resp["Item"]["seats"]
    else:
        # 日毎の席数がなければデフォルト席数
        default_resp = default_seat_table.get_item(Key={"id": "default"})
        if "Item" in default_resp:
            max_seats = default_resp["Item"]["seats"]
        else:
            max_seats = 0  # 席数未設定の場合は0

    # 2. 既存予約数を集計
    resp = reservations_table.scan(
        FilterExpression="#date = :date",
        ExpressionAttributeNames={"#date": "date"},
        ExpressionAttributeValues={":date": reservation.date}
    )
    reserved_seats = sum(item["seats"] for item in resp.get("Items", []))

    # 3. 席数超過チェック
    if reserved_seats + reservation.seats > max_seats:
        raise HTTPException(status_code=400, detail="席数を超えています")

    # 4. 予約登録
    now = datetime.utcnow().isoformat()
    reservation_id = str(uuid4())
    item = {
        "id": reservation_id,
        "name": reservation.name,
        "email": reservation.email,
        "date": reservation.date,
        "seats": reservation.seats,
        "created_at": now
    }
    reservations_table.put_item(Item=item)

    return Reservation(id=reservation_id, created_at=now, **reservation.dict())

@app.get("/api/reservations/")
def get_user_reservations(email: EmailStr):
    """ユーザー予約一覧取得"""
    reservations_table = dynamodb.Table('reservations')
    resp = reservations_table.scan(
        FilterExpression="#email = :email",
        ExpressionAttributeNames={"#email": "email"},
        ExpressionAttributeValues={":email": email}
    )
    items = resp.get("Items", [])
    # 日付降順で返す
    items.sort(key=lambda x: x["date"], reverse=True)
    return items

@app.delete("/api/reservations/{reservation_id}")
def delete_reservation(reservation_id: str):
    """予約削除"""
    reservations_table = dynamodb.Table('reservations')
    # まず予約が存在するか確認
    resp = reservations_table.get_item(Key={"id": reservation_id})
    if "Item" not in resp:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    reservations_table.delete_item(Key={"id": reservation_id})
    return {"message": "予約を削除しました"}

# 管理者用
@app.get("/api/admin/reservations/")
def get_admin_reservations(month: str = Query(..., description="yyyy/MM")):
    """月ごとの予約一覧取得"""
    reservations_table = dynamodb.Table('reservations')
    year, mon = map(int, month.split("/"))
    prefix = f"{year:04d}-{mon:02d}-"
    resp = reservations_table.scan(
        FilterExpression="begins_with(#date, :prefix)",
        ExpressionAttributeNames={"#date": "date"},
        ExpressionAttributeValues={":prefix": prefix}
    )
    items = resp.get("Items", [])
    items.sort(key=lambda x: x["date"])  # 日付昇順
    return items

@app.post("/api/admin/default_holiday")
def set_default_holiday(default_holiday: DefaultHoliday):
    """デフォルト休日登録"""
    default_holiday_table = dynamodb.Table('default_holiday')
    default_holiday_table.put_item(Item={"id": "default", "weekdays": default_holiday.weekdays})
    return {"message": "デフォルト休日を登録しました"}

@app.post("/api/admin/default_seat")
def set_default_seat(default_seat: DefaultSeat):
    """デフォルト席数登録"""
    default_seat_table = dynamodb.Table('default_seat')
    default_seat_table.put_item(Item={"id": "default", "seats": default_seat.seats})
    return {"message": "デフォルト席数を登録しました"}

@app.post("/api/holiday")
def set_holiday(holiday: Holiday):
    """休日登録"""
    holidays_table = dynamodb.Table('holidays')
    holidays_table.put_item(Item={"date": holiday.date})
    return {"message": f"{holiday.date} を休日に登録しました"}

@app.post("/api/seat/")
def set_seat(seat: Seat):
    """日毎の席数登録"""
    seats_table = dynamodb.Table('seats')
    seats_table.put_item(Item={"date": seat.date, "seats": seat.seats})
    return {"message": f"{seat.date} の席数を {seat.seats} に設定しました"}

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI + DynamoDB!"} 