# first stage
FROM python:3.6.12 as builder
WORKDIR /app
RUN python -m venv .venv && .venv/bin/pip install --no-cache-dir -U pip setuptools

# do some manual preinstallation fails requirements for torch cpu
RUN .venv/bin/pip install --no-cache-dir numpy==1.19.4
RUN .venv/bin/pip install --no-cache-dir torch==1.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

COPY requirements.txt /app
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

# second unnamed stage
FROM python:3.6.12-slim-stretch as runner
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
ENV PATH=/app/.venv:/app/.venv/lib:/app/.venv/bin:/app:$PATH

## final image
from runner
COPY ./run.py /app
COPY ./service /app/service
CMD [ "uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]