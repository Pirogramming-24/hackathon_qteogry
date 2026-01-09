document.addEventListener("DOMContentLoaded", function() {
    // 1. 요소 가져오기
    const startTimeInput = document.getElementById("uc-start-time");
    const endTimeInput = document.getElementById("uc-end-time");
    const timerDisplay = document.getElementById("realtime-timer");
    const yesBtn = document.getElementById("yes-btn");
    const progressBar = document.getElementById("progress-bar");
    const countText = document.getElementById("count-text");

    // 요소가 없으면 실행 중지 (이해도 체크가 없는 페이지일 수 있음)
    if (!startTimeInput || !timerDisplay) return;

    // 2. 시간 파싱
    const startTime = new Date(startTimeInput.value).getTime();
    let endTime = endTimeInput.value ? new Date(endTimeInput.value).getTime() : null;
    let timerInterval;

    // 3. 타이머 업데이트 함수 (1초마다 실행됨)
    function updateTimer() {
        const now = new Date().getTime();
        
        // 종료 시간이 있으면 '종료-시작', 없으면 '현재-시작' 시간으로 계산
        // 즉, 이미 끝났으면 타이머가 멈춘 채로 보이고, 안 끝났으면 계속 올라감
        const targetTime = endTime ? endTime : now;
        const diff = Math.floor((targetTime - startTime) / 1000); // 초 단위 변환

        if (diff < 0) {
            timerDisplay.textContent = "00:00";
            return;
        }

        // 분:초 포맷팅
        const minutes = Math.floor(diff / 60);
        const seconds = diff % 60;
        timerDisplay.textContent = 
            `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    // 4. 타이머 시작
    updateTimer(); // 화면 켜지자마자 한 번 실행
    if (!endTime) {
        // 끝나지 않았다면 1초마다 업데이트 인터벌 시작
        timerInterval = setInterval(updateTimer, 1000);
    } else {
        // 이미 끝났다면 텍스트 색상을 빨간색 등으로 변경해 표시 (선택사항)
        timerDisplay.style.color = "#FF6B6B"; 
    }

    // 5. "네" 버튼 클릭 이벤트 (AJAX)
    if (yesBtn) {
        yesBtn.addEventListener("click", function() {
            const checkId = this.dataset.id;
            const url = this.dataset.url;
            const csrfToken = this.dataset.csrf;

            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrfToken
                },
                body: `check_id=${checkId}`
            })
            .then(res => res.json())
            .then(data => {
                // (1) 프로그레스바 & 텍스트 업데이트
                if (progressBar) progressBar.style.width = `${data.progress}%`;
                if (countText) countText.textContent = `${data.response_count} / ${data.total_count}`;

                // (2) 서버에서 "끝났다(is_finished)"고 응답이 오면?
                if (data.is_finished) {
                    // 타이머 멈춤
                    clearInterval(timerInterval);
                    
                    // 현재 시간을 종료 시간으로 설정하고 마지막 업데이트
                    endTime = new Date().getTime(); 
                    updateTimer();
                    
                    // 버튼 숨기기 & 알림
                    yesBtn.style.display = "none";
                    timerDisplay.style.color = "#FF6B6B"; // 타이머 색 변경 (종료됨)
                    alert("🎉 목표 인원을 달성했습니다! 이해도 체크가 종료됩니다.");
                    
                    // 필요하다면 페이지 새로고침해서 '난이도 결과' 보여주기
                    // location.reload(); 
                }
            })
            .catch(err => console.error("Error:", err));
        });
    }
});