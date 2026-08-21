import os
import time

from fastapi import Request
from starlette.responses import Response


SLOW_REQUEST_THRESHOLD_MS = float(
    os.getenv("SLOW_REQUEST_THRESHOLD_MS", "500")
)


async def request_logger_middleware(
    request: Request,
    call_next,
) -> Response:
    """Measure every request and log response time in the terminal."""

    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        process_time = (time.perf_counter() - start_time) * 1000

        print(
            f"[REQUEST] {request.method} {request.url.path} "
            f"| Status: 500/EXCEPTION "
            f"| Response Time: {process_time:.2f}ms"
        )

        if process_time > SLOW_REQUEST_THRESHOLD_MS:
            print(
                f"[SLOW REQUEST] {request.method} {request.url.path} "
                f"took {process_time:.2f}ms "
                f"(threshold: {SLOW_REQUEST_THRESHOLD_MS:.0f}ms)"
            )

        raise

    process_time = (time.perf_counter() - start_time) * 1000

    # Expose response time to the client as well.
    response.headers["X-Response-Time"] = f"{process_time:.2f}ms"

    print(
        f"[REQUEST] {request.method} {request.url.path} "
        f"| Status: {response.status_code} "
        f"| Response Time: {process_time:.2f}ms"
    )

    if process_time > SLOW_REQUEST_THRESHOLD_MS:
        print(
            f"[SLOW REQUEST] {request.method} {request.url.path} "
            f"took {process_time:.2f}ms "
            f"(threshold: {SLOW_REQUEST_THRESHOLD_MS:.0f}ms)"
        )

    return response
