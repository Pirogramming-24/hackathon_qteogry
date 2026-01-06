/*
사용방법:

<script type="module">
    import {
    connectRealtime,
    registerRealtimeHandler
    } from "{% static 'realtime/realtime.js' %}";

    const sessionCode = "{{ session.code }}";

    // 질문 새로 생기면: 서버에서 partial HTML을 받아서 리스트 앞에 붙임
    registerRealtimeHandler("question:new", async ({ question_id }) => {
        const res = await fetch(`/api/questions/${question_id}/partial/`);
        if (!res.ok) return;
        const html = await res.text();
        document.querySelector("#question-list")
        .insertAdjacentHTML("afterbegin", html);
    });

    connectRealtime("{{ session.code }}");
</script>
*/
const realtimeHandlers = {};

export function registerRealtimeHandler(type, handler) {
  realtimeHandlers[type] = handler;
}

export function connectRealtime(sessionCode) {
  const es = new EventSource(
    `/realtime/sse/sessions/${sessionCode}/`
  );

  es.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    const handler = realtimeHandlers[msg.type];
    if (handler) handler(msg.data);
  };

  es.onerror = () => {
    console.warn("SSE disconnected");
  };
}
