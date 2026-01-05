document.addEventListener("DOMContentLoaded", function() {
    console.log("main_ny.js loaded successfully!");

    // [기능 추가] 이미지 파일 선택 시 미리보기 (선택사항)
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
});