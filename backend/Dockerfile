FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY data_pipeline/ ./data_pipeline/
COPY backend/ ./backend/

CMD ["sh", "-c", "python data_pipeline/generate_mock_data.py && python backend/risk_engine.py"]
