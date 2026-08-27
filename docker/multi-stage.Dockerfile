FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy


RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM python:3.12.14-slim-bookworm

WORKDIR /app

RUN groupadd --system appuser \
    && useradd --system --gid appuser --home-dir /app appuser

USER appuser

COPY --from=builder --chown=appuser:appuser /app .

ENV PATH="/app/.venv/bin:$PATH"

CMD [ "python", "main.py" ]