import json
from collections import defaultdict

# 세션별 연결된 큐 목록
SESSION_SUBSCRIBERS = defaultdict(list)


def publish_session_event(session_code: str, event_type: str, payload: dict):
    """
    session_code: 라이브 세션 코드 = LiveSession.code
    event_type: 'progress:update' | 'question:new' | 'comment:new'
    payload: JSON 직렬화 가능한 dict

    JS와의 인터페이스 구조: {type, data} 
    호출 예) 
    # question 저장 직후
    publish_session_event(
        session.code,
        "question:new",
        {"question_id": question.id}
    )
    """
    message = {
        "type": event_type,
        "data": payload,
    }

    dead_queues = []
    # 세션 구독자 == 세선 보는 모든 브라우저 마다
    for q in SESSION_SUBSCRIBERS[session_code]:
        try:
            # 이벤트 메시지 전송
            q.put_nowait(json.dumps(message))
        except Exception:
            dead_queues.append(q)

    for q in dead_queues:
        SESSION_SUBSCRIBERS[session_code].remove(q)
