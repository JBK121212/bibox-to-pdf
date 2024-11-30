# Fixed alpine version due to: https://github.com/ocrmypdf/OCRmyPDF/issues/1395
FROM python:3-alpine3.19

LABEL maintainer=LasseR15
LABEL email=lasse.roth@nexy.dev

WORKDIR /app

RUN apk add --no-cache tesseract-ocr tesseract-ocr-data-deu ghostscript

COPY /src ./src
COPY /requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app/src/
ENV BASE_OUTPUT_PATH=/app/output

ENTRYPOINT ["python3", "/app/src/main.py"]
