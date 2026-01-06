(function () {
  console.log("[RT] realtime.js loaded");

  const root = document.getElementById("realtime-root");
  if (!root) {
    console.warn("[RT] no realtime-root found");
    return;
  }

  const sessionId = Number(root.dataset.sessionId);
  const currentQid = root.dataset.questionId ? Number(root.dataset.questionId) : null;

  if (!sessionId) {
    console.warn("[RT] sessionId missing");
    return;
  }

  const sseUrl = `/realtime/sse/sessions/${sessionId}/`;

  // ✅ SSE 한 번만
  if (!window.__sse__) {
    console.log("[RT] connect", sseUrl);
    window.__sse__ = new EventSource(sseUrl);
    window.__sse__.addEventListener("open", () => console.log("[RT] SSE open"));
    window.__sse__.addEventListener("error", (e) => console.error("[RT] SSE error", e));
  }

  const es = window.__sse__;

  // ✅ handler 중복 방지
  if (window.__rt_handler_attached__) return;
  window.__rt_handler_attached__ = true;

  // 유틸
  const normalizeType = (t) => String(t || "").replace(/\s+/g, "");
  const qs = (sel) => document.querySelector(sel);

  es.onmessage = async (e) => {
    console.log("[RT] raw:", e.data);

    let msg;
    try {
      msg = JSON.parse(e.data);
    } catch (err) {
      console.error("[RT] JSON parse fail", err);
      return;
    }

    const type = normalizeType(msg.type);
    const data = msg.data || {};

    // =========================
    // 1) 댓글 새로 추가
    // =========================
    if (type === "comment:new") {
      const qid = Number(data.question_id);
      const cid = Number(data.comment_id);

      // 디테일 페이지가 아니면(현재 QID 없음) 댓글 DOM 붙일 곳이 없음 → 무시
      if (!currentQid) return;
      if (qid !== currentQid) return;

      const list = qs(`#comments-${qid}`);
      if (!list) {
        console.warn("[RT] comment list not found");
        return;
      }

      // partial endpoint로 HTML 가져오기(권장)
      const fetchUrl = `/questions/api/sessions/${sessionId}/questions/${qid}/comments/${cid}/partial/`;
      console.log("[RT] fetch", fetchUrl);

      const res = await fetch(fetchUrl);
      if (!res.ok) {
        console.error("[RT] partial fetch fail", res.status);
        return;
      }

      const html = await res.text();

      const empty = qs(`#no-comments-${qid}`);
      if (empty) empty.remove();

      list.insertAdjacentHTML("beforeend", html);
      console.log("[RT] comment appended");
      return;
    }

    // =========================
    // 2) 질문 새로 추가(선택)
    // =========================
    if (type === "question:new") {
      // 질문도 partial로 받아서 리스트에 append 하는 구조 추천
      // data: {question_id, ...}
      const qid = Number(data.question_id);
      const list = qs("#question-list");
      if (!list) return;

      const fetchUrl = `/questions/api/sessions/${sessionId}/questions/${qid}/partial/`;
      const res = await fetch(fetchUrl);
      if (!res.ok) return;

      const html = await res.text();
      list.insertAdjacentHTML("afterbegin", html); // 최신을 위로
      console.log("[RT] question appended");
      return;
    }

    console.log("[RT] ignore type:", type);
  };
})();
