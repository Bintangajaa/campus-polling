FROM python:3.12-slim
WORKDIR /app
COPY app.py .
RUN mkdir -p /var/lib/backend_data
VOLUME ["/var/lib/backend_data"]
EXPOSE 5000
CMD ["python", "-u", "app.py"]
