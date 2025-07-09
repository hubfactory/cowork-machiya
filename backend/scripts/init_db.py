import boto3
import os
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'ap-northeast-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'dummy'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'dummy'),
    endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL', 'http://dynamodb-local:8000')
)

def create_tables():
    # reservations
    try:
        dynamodb.create_table(
            TableName='reservations',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print('Created table: reservations')
    except Exception as e:
        print('reservations:', e)
    # seats
    try:
        dynamodb.create_table(
            TableName='seats',
            KeySchema=[
                {'AttributeName': 'date', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'date', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print('Created table: seats')
    except Exception as e:
        print('seats:', e)
    # holidays
    try:
        dynamodb.create_table(
            TableName='holidays',
            KeySchema=[
                {'AttributeName': 'date', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'date', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print('Created table: holidays')
    except Exception as e:
        print('holidays:', e)
    # default_seat
    try:
        dynamodb.create_table(
            TableName='default_seat',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print('Created table: default_seat')
    except Exception as e:
        print('default_seat:', e)
    # default_holiday
    try:
        dynamodb.create_table(
            TableName='default_holiday',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print('Created table: default_holiday')
    except Exception as e:
        print('default_holiday:', e)

def put_sample_data():
    # default_seat
    default_seat = dynamodb.Table('default_seat')
    default_seat.put_item(Item={"id": "default", "seats": 10})
    # default_holiday（月曜・日曜）
    default_holiday = dynamodb.Table('default_holiday')
    default_holiday.put_item(Item={"id": "default", "weekdays": [0, 6]})
    # seats（特定日だけ席数変更）
    seats = dynamodb.Table('seats')
    seats.put_item(Item={"date": "2024-07-15", "seats": 5})
    # holidays（特定日だけ休日追加）
    holidays = dynamodb.Table('holidays')
    holidays.put_item(Item={"date": "2024-07-17"})
    # reservations（サンプル予約）
    reservations = dynamodb.Table('reservations')
    reservations.put_item(Item={
        "id": "sample-1",
        "name": "テスト太郎",
        "email": "test@example.com",
        "date": "2024-07-15",
        "seats": 2,
        "created_at": "2024-07-01T10:00:00Z"
    })
    print('Sample data inserted.')

if __name__ == "__main__":
    create_tables()
    put_sample_data() 