FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY scripts/init_db.py ./scripts/init_db.py

COPY start.sh ./start.sh
RUN chmod +x ./start.sh

CMD ["./start.sh"]