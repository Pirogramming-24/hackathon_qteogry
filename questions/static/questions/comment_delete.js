document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".comment-delete-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      if (!confirm("댓글을 삭제할까요?")) return;

      const commentId = btn.dataset.id;
      const url = btn.dataset.url;
      const csrf = btn.dataset.csrf;

      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrf,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `comment_id=${commentId}`,
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // DOM에서 제거
          btn.closest(".comment-item-hs").remove();
        } else {
          alert("삭제할 수 없습니다.");
        }
      });
    });
  });
});
