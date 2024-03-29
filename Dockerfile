# first stage
FROM python:3.7 as builder
WORKDIR /app
RUN python -m venv .venv && .venv/bin/pip install --no-cache-dir -U pip setuptools

# do some manual preinstallation fails requirements for torch cpu
# RUN .venv/bin/pip install --no-cache-dir numpy==1.19.4
# RUN .venv/bin/pip install --no-cache-dir torch==1.13.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

COPY requirements_cpu.txt /app
RUN .venv/bin/pip install --no-cache-dir -r requirements_cpu.txt
COPY requirements.txt /app
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

# second unnamed stage
FROM python:3.7-slim-bullseye as runner
WORKDIR /app
RUN apt-get update
RUN apt-get install -y libsndfile1
COPY --from=builder /app/.venv /app/.venv
ENV PATH=/app/.venv:/app/.venv/lib:/app/.venv/bin:/app:$PATH

## final image
from runner
COPY ./run.py /app
COPY ./service /app/service
CMD [ "uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
