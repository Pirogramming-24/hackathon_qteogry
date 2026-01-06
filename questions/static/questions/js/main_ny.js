document.addEventListener("DOMContentLoaded", function() {
    console.log("main_ny.js loaded successfully!");

    // 이미지 파일 선택 시 미리보기
    const imageInput = document.querySelector('.input-image_ny');
    
    if (imageInput) {
        imageInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                // 이미지가 선택되었을 때 로직 (필요시 구현)
                console.log("이미지가 선택되었습니다:", file.name);
            }
        });
    }

    /* 2. 좋아요(공감) 버튼 AJAX 처리 (새로운 기능) */
    const likeButtons = document.querySelectorAll('.like-btn_ny');

    likeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // 부모 태그(<a> 링크)로 클릭 이벤트가 전파되어 페이지가 이동하는 것을 막음
            e.preventDefault(); 
            e.stopPropagation();

            const questionId = this.getAttribute('data-question-id');
            const url = `/questions/like/${questionId}/`; // urls.py에 설정한 경로

            // AJAX 요청 (Fetch API)
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // 아래 함수로 토큰 가져옴
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("로그인이 필요합니다.");
                    return;
                }

                // [동기화 핵심] 리스트와 상세뷰 양쪽의 숫자를 모두 찾아 업데이트
                
                // 1. 리스트 쪽 숫자 업데이트
                const listCountSpan = document.getElementById(`like-count-list-${questionId}`);
                if (listCountSpan) {
                    listCountSpan.innerText = data.count;
                }

                // 2. 상세뷰 쪽 숫자 업데이트
                const detailCountSpan = document.getElementById(`like-count-detail-${questionId}`);
                if (detailCountSpan) {
                    detailCountSpan.innerText = data.count;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

/* [보조 함수] 쿠키에서 CSRF Token 가져오기 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}