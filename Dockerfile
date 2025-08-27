FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir fastmcp>=2.0.0 selenium>=4.15.0 beautifulsoup4>=4.12.0 \
    requests>=2.31.0 webdriver-manager>=4.0.0 python-pptx>=0.6.21
ENV PYTHONUNBUFFERED=1 PYTHONPATH=.
EXPOSE 8000
CMD ["python", "-m", "server"]
