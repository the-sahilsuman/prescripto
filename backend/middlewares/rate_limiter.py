import os
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request
from starlette.responses import JSONResponse, Response


# Configure through .env
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


# In-memory store:
# { "client_ip": deque([timestamp1, timestamp2, ...]) }
_request_store: dict[str, deque[float]] = defaultdict(deque)
_store_lock = Lock()


def get_client_ip(request: Request) -> str:
    """Return the client's IP address."""
    return request.client.host if request.client else "unknown"


def is_rate_limited(client_ip: str) -> tuple[bool, int]:
    """
    Check whether an IP has exceeded the configured request limit.

    Returns:
        (is_limited, remaining_requests)
    """
    now = time.monotonic()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    with _store_lock:
        timestamps = _request_store[client_ip]

        # Remove requests outside the current time window.
        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        if len(timestamps) >= RATE_LIMIT_REQUESTS:
            return True, 0

        timestamps.append(now)
        remaining = RATE_LIMIT_REQUESTS - len(timestamps)

        return False, remaining


async def rate_limit_middleware(
    request: Request,
    call_next,
) -> Response:
    """Limit requests per client IP using a sliding time window."""

    # Let CORS preflight requests pass through without consuming a rate-limit slot.
    if request.method == "OPTIONS":
        return await call_next(request)

    client_ip = get_client_ip(request)
    limited, remaining = is_rate_limited(client_ip)

    if limited:
        print(
            f"[RATE LIMIT] BLOCKED {request.method} "
            f"{request.url.path} | IP: {client_ip}"
        )

        response = JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": "Too many requests. Please try again later.",
            },
            headers={
                "Retry-After": str(RATE_LIMIT_WINDOW_SECONDS),
                "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
            },
        )

        return response

    response = await call_next(request)

    # Tell the client how much of its current limit remains.
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    return response
