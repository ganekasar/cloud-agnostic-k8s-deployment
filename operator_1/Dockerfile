FROM bitnami/python:3.7.3 as builder
COPY ./src /app
WORKDIR /app
RUN virtualenv . && \
    . bin/activate && \
    pip install -r requirements.txt

FROM bitnami/python:3.7.3-prod
COPY --from=builder /app /app
WORKDIR /app
CMD bash -c "source bin/activate && kopf run /app/handlers.py --verbose"
