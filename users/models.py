from django.db import models
from django.contrib.auth.models import User
import random

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', '수강생'),
        ('staff', '운영진'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    generation = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 형용사와 명사 리스트
    ADJECTIVES = [
        '행복한', '슬픈', '즐거운', '화난', '놀란', '지친', '신나는', '우울한',
        '귀여운', '멋진', '용감한', '겁많은', '똑똑한', '어리석은', '빠른', '느린',
        '강한', '약한', '큰', '작은', '뜨거운', '차가운', '밝은', '어두운',
        '시끄러운', '조용한', '부지런한', '게으른', '친절한', '무서운', '재미있는', '지루한',
        '억울한', '당황한', '설레는', '긴장한', '편안한', '불안한', '자신있는', '부끄러운'
    ]
    
    NOUNS = [
        '사자', '호랑이', '곰', '여우', '늑대', '토끼', '다람쥐', '고양이',
        '강아지', '햄스터', '기린', '코끼리', '판다', '코알라', '캥거루', '펭귄',
        '독수리', '부엉이', '앵무새', '까마귀', '참새', '비둘기', '백조', '오리',
        '돌고래', '고래', '상어', '문어', '오징어', '거북이', '악어', '뱀',
        '개구리', '나비', '벌', '개미', '거미', '잠자리', '사슴', '다람쥐'
    ]
    
    def generate_random_nickname(self):
        """랜덤 닉네임 생성 (중복 방지)"""
        max_attempts = 100
        for _ in range(max_attempts):
            adjective = random.choice(self.ADJECTIVES)
            noun = random.choice(self.NOUNS)
            nickname = f"{adjective} {noun}"
            
            # 중복 체크 (자기 자신은 제외)
            if not UserProfile.objects.filter(nickname=nickname).exclude(id=self.id).exists():
                return nickname
        
        # 100번 시도해도 중복이면 숫자 추가
        return f"{random.choice(self.ADJECTIVES)} {random.choice(self.NOUNS)} {random.randint(1, 9999)}"
    
    def regenerate_nickname(self):
        """닉네임 재생성 (로그인 시마다 호출)"""
        self.nickname = self.generate_random_nickname()
        self.save()
        return self.nickname
    
    def save(self, *args, **kwargs):
        """프로필 생성 시 자동으로 랜덤 닉네임 생성"""
        if not self.nickname:
            self.nickname = self.generate_random_nickname()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.nickname}"
