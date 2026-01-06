document.addEventListener("DOMContentLoaded", () => {
  const yesBtn = document.getElementById("yes-btn");
  if (!yesBtn) return;

  const countText = document.getElementById("count-text");
  const progressBar = document.getElementById("progress-bar");

  const url = yesBtn.dataset.url;
  const csrf = yesBtn.dataset.csrf;
  const checkId = yesBtn.dataset.id;

  yesBtn.addEventListener("click", () => {
    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrf,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `check_id=${checkId}`,
    })
    .then(res => res.json())
    .then(data => {
      if (!data.created) {
        alert("이미 응답하셨습니다 🙂");
        return;
      }

      countText.textContent = `${data.response_count} / 24`;
      progressBar.style.width = `${data.progress}%`;
    });
  });
});
