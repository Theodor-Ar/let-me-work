FROM ghcr.io/astral-sh/uv:0.12.5-python3.12-alpine3.23 AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN apk add --no-cache build-base libffi-dev zlib-dev

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN uv run --with pyinstaller pyinstaller --onefile main.py -n main


FROM alpine:3.23

WORKDIR /app

RUN addgroup -S appuser && adduser -S -G appuser -h /app appuser 

COPY --from=builder --chown=appuser:appuser /app/dist/main /app/main

ENTRYPOINT [ "/app/main" ]