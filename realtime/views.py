import queue
import time
from django.http import StreamingHttpResponse 
from django.views.decorators.http import require_GET
from .services import SESSION_SUBSCRIBERS
from django.shortcuts import render

# Create your views here.

@require_GET
def session_event_stream(request, session_code):
    """
    GET /realtime/sse/sessions/<session_code>/

    :param session_code: code 대상의 세션을 갱신?
    """

    # 브라우저 1개 = 큐 1개
    q = queue.Queue()
    SESSION_SUBSCRIBERS[session_code].append(q)

    # 연결 끊길 때까지 반복
    def event_stream():
        try:
            while True:
                try:
                    data = q.get(timeout=15)
                    yield f"data: {data}\n\n"
                except queue.Empty:

                    yield ": ping \n\n"
        finally:
            # 연결 끊기니까 목록에서 제거
            SESSION_SUBSCRIBERS[session_code].remove(q)

    # Streaming = 조금씩 계속 전송
    response = StreamingHttpResponse(
        event_stream(),
        
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    return response