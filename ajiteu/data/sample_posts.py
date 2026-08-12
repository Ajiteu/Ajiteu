from datetime import datetime, timedelta
import random

# 사용 가능한 이미지 리스트 (요청하신 파일명 반영)
# [수정] url_for('static', filename=...) 이 실제로 만드는 형식과 동일하게
#        앞에 '/'를 붙여서 저장 (라우트 함수 저장 형식과 일치)
# images = [
#     "/static/img/banner_main.png",
#     "/static/img/namseoul.png",
#     "/static/img/rec_D.png",
#     "/static/img/midus.png",
#     "/static/img/rec_I.png",
#     "/static/img/rec_U.png",
#     "/static/img/rec_W.png"
# ]
# content, user, image_path, view, liker, comment, create_date
# 30개의 골프 커뮤니티 예시 게시글

sample_posts_data = [
    # Travel 카테고리
    {
        "content": "서울에서 부산으로 떠난 주말 여행! 해운대 해수욕장에서 일몰을 봤는데 정말 멋있었다. 해동용궁사도 방문했어. #여행 #부산 #휴가",
        "create_date": datetime.now() - timedelta(days=15),
        "modify_date": datetime.now() - timedelta(days=14),
        "image_path": ["sample_images/001.JPG", "sample_images/002.JPG"],
        "view_count": 245,
        "user_id": 1
    },
    {
        "content": "꿈에 그리던 일본 도쿄 trip! 스카이트리에서의 야경은 정말 최고다. 다음엔 교토도 꼭 가봐야지 🗼 #travel #도쿄 #일본",
        "create_date": datetime.now() - timedelta(days=20),
        "modify_date": datetime.now() - timedelta(days=19),
        "image_path": None,
        "view_count": 512,
        "user_id": 2
    },
    {
        "content": "태국 방콕 자유여행 완성! 왕궁도 보고 야시장에서 길거리 음식도 먹고. 관광지보다 골목골목이 재미있더라 🌏",
        "create_date": datetime.now() - timedelta(days=25),
        "modify_date": datetime.now() - timedelta(days=23),
        "image_path": ["sample_images/004.JPG"],
        "view_count": 389,
        "user_id": 3
    },
    {
        "content": "국내여행 추천 - 제주도! 용머리해안에서 사진 찍었어. 정말 숨이 막힐 정도로 아름다웠다. 휴가 때 한 번 꼭 가봐야 할 곳!",
        "create_date": datetime.now() - timedelta(days=30),
        "modify_date": datetime.now() - timedelta(days=28),
        "image_path": None,
        "view_count": 678,
        "user_id": 4
    },
    {
        "content": "뉴욕 출장에서 짬내서 타임스퀘어도 보고, 센트럴파크도 산책했다. 해외 출장도 여행이 될 수 있다는 걸 알았어 ✈️",
        "create_date": datetime.now() - timedelta(days=35),
        "modify_date": datetime.now() - timedelta(days=34),
        "image_path": ["sample_images/005.JPG", "sample_images/006.JPG"],
        "view_count": 421,
        "user_id": 5
    },
    {
        "content": "북유럽 관광 일정 짜기! 스웨덴 스톡홀름에서 시작해서 노르웨이까지. 백야의 신비로움을 경험하고 싶다",
        "create_date": datetime.now() - timedelta(days=10),
        "modify_date": datetime.now() - timedelta(days=9),
        "image_path": ["sample_images/007.JPG"],
        "view_count": 156,
        "user_id": 6
    },
    {
        "content": "강릉 여행 2박3일 완주! 정동진에서 해돋이 보고, 커피거리도 구경했어. 근처 여행지 중에 최고다 ☀️",
        "create_date": datetime.now() - timedelta(days=8),
        "modify_date": datetime.now() - timedelta(days=7),
        "image_path": None,
        "view_count": 234,
        "user_id": 7
    },
    {
        "content": "홍콩 trip에서 스타페리 탔어! 빅토리아 하버의 야경은 정말 비현실적이다. 다시 한 번 가고 싶은 곳 🌃",
        "create_date": datetime.now() - timedelta(days=5),
        "modify_date": datetime.now() - timedelta(days=4),
        "image_path": ["sample_images/008.JPG"],
        "view_count": 567,
        "user_id": 8
    },

    # Exercise 카테고리
    {
        "content": "새벽 러닝 30일 챌린지 완성! 5km를 매일 뛰었는데 체력이 눈에 띄게 좋아졌다. 다음은 10km 도전! 💪",
        "create_date": datetime.now() - timedelta(days=12),
        "modify_date": datetime.now() - timedelta(days=11),
        "image_path": ["sample_images/009.JPG", "sample_images/010.JPG"],
        "view_count": 398,
        "user_id": 2
    },
    {
        "content": "헬스 3개월 차! 벤치프레스 중량이 30kg에서 50kg까지 올랐어. 근력 운동의 매력에 빠졌다 🏋️",
        "create_date": datetime.now() - timedelta(days=18),
        "modify_date": datetime.now() - timedelta(days=16),
        "image_path": None,
        "view_count": 542,
        "user_id": 1
    },
    {
        "content": "요가로 시작한 아침운동! 요가는 생각보다 훨씬 힘들지만 정신이 맑아지는 기분이 좋다. 계속 해봐야겠어",
        "create_date": datetime.now() - timedelta(days=22),
        "modify_date": datetime.now() - timedelta(days=21),
        "image_path": ["sample_images/011.JPG"],
        "view_count": 267,
        "user_id": 3
    },
    {
        "content": "필라테스 레슨 받기 시작했다! 코어가 이렇게 약했나 싶을 정도... 꾸준히 하면 몸이 확 달라질 것 같아 🧘‍♀️",
        "create_date": datetime.now() - timedelta(days=28),
        "modify_date": datetime.now() - timedelta(days=27),
        "image_path": None,
        "view_count": 189,
        "user_id": 4
    },
    {
        "content": "운동하는 습관이 생겼어! 예전엔 헬스장 가기도 힘들었는데 이제는 안 가면 불안하다 ㅋㅋ 운동 중독인 듯",
        "create_date": datetime.now() - timedelta(days=3),
        "modify_date": datetime.now() - timedelta(days=2),
        "image_path": ["sample_images/012.JPG"],
        "view_count": 312,
        "user_id": 5
    },
    {
        "content": "런닝머신에서 10km 신기록! 내가 이렇게까지 뛸 수 있나 싶었는데 해냈다. 아침 exercise는 정말 최고다 🏃",
        "create_date": datetime.now() - timedelta(days=7),
        "modify_date": datetime.now() - timedelta(days=6),
        "image_path": None,
        "view_count": 276,
        "user_id": 6
    },
    {
        "content": "요가 명상으로 스트레스 해소! 근력 운동도 좋지만 요가의 여유로움도 정말 좋다. 일주일에 2-3번은 꼭 하자",
        "create_date": datetime.now() - timedelta(days=14),
        "modify_date": datetime.now() - timedelta(days=13),
        "image_path": ["sample_images/013.JPG"],
        "view_count": 213,
        "user_id": 7
    },
    {
        "content": "헬스 처음 가본 사람들 필수 루틴! 벤치프레스, 스쿼트, 데드리프트는 기본이지. 재미있고 힘들고 뿌듯해! 💪",
        "create_date": datetime.now() - timedelta(days=19),
        "modify_date": datetime.now() - timedelta(days=18),
        "image_path": ["sample_images/014.JPG", "sample_images/015.JPG"],
        "view_count": 445,
        "user_id": 8
    },

    # Food 카테고리
    {
        "content": "강남역 맛집 발견! 뼈해장국이 정말 진한 국물에 고기도 실하고 최고다. 다음엔 친구들이랑 또 가야지 🍜",
        "create_date": datetime.now() - timedelta(days=11),
        "modify_date": datetime.now() - timedelta(days=10),
        "image_path": None,
        "view_count": 523,
        "user_id": 2
    },
    {
        "content": "홈쿡! 처음 만들어본 파스타인데 생각보다 맛있게 나왔다. 요리는 하면 할수록 재미있는 것 같아 👨‍🍳",
        "create_date": datetime.now() - timedelta(days=9),
        "modify_date": datetime.now() - timedelta(days=8),
        "image_path": ["sample_images/016.JPG"],
        "view_count": 387,
        "user_id": 3
    },
    {
        "content": "신촌 카페 거리 투어! 예쁜 카페들이 정말 많네. 라떼 한 잔하며 책 읽으니 기분이 정말 좋다 ☕",
        "create_date": datetime.now() - timedelta(days=16),
        "modify_date": datetime.now() - timedelta(days=15),
        "image_path": None,
        "view_count": 298,
        "user_id": 4
    },
    {
        "content": "먹방이 취미! 한 끼에 정성스럽게 밥을 차리는 것만으로도 행복해진다. 음식이야말로 최고의 힐링이다 😋",
        "create_date": datetime.now() - timedelta(days=24),
        "modify_date": datetime.now() - timedelta(days=22),
        "image_path": ["sample_images/017.JPG"],
        "view_count": 612,
        "user_id": 5
    },
    {
        "content": "최고의 맛집 발견! 주인장이 정성스럽게 만드는 음식 맛이 다르더라. 이런 식당이야말로 진정한 맛집 🥢",
        "create_date": datetime.now() - timedelta(days=6),
        "modify_date": datetime.now() - timedelta(days=5),
        "image_path": None,
        "view_count": 441,
        "user_id": 6
    },
    {
        "content": "요리는 예술이다! 계란 계란말이를 만드는데 생각보다 어렵네. 그래도 맛있으면 장땡이지 🍚",
        "create_date": datetime.now() - timedelta(days=13),
        "modify_date": datetime.now() - timedelta(days=12),
        "image_path": ["sample_images/018.JPG"],
        "view_count": 325,
        "user_id": 7
    },
    {
        "content": "카페에서의 힐링 시간! 핸드드립 커피 한 잔하며 명상하는 시간... 이런 게 진짜 여유다 ☕✨",
        "create_date": datetime.now() - timedelta(days=4),
        "modify_date": datetime.now() - timedelta(days=3),
        "image_path": ["sample_images/019.JPG"],
        "view_count": 287,
        "user_id": 8
    },
    {
        "content": "홈쿡 도전기! 스테이크를 구워봤는데 소스까지 완벽해졌다. 간단한 음식도 손이 가는 이유가 뭘까 🥩",
        "create_date": datetime.now() - timedelta(days=21),
        "modify_date": datetime.now() - timedelta(days=20),
        "image_path": None,
        "view_count": 389,
        "user_id": 1
    },

    # 추가 다양한 데이터들
    {
        "content": "인천 여행 플랜! 송도 센트럴파크에서 자전거 타고 관광했어. 야경도 멋있고 분위기 좋아 🚴",
        "create_date": datetime.now() - timedelta(days=17),
        "modify_date": datetime.now() - timedelta(days=16),
        "image_path": ["sample_images/020.JPG"],
        "view_count": 156,
        "user_id": 2
    },
    {
        "content": "라자냐 만드는 과정! 만드는 건 복잡하지만 맛은 정말 최고. 집에서 만든 음식이 최고다 🍝",
        "create_date": datetime.now() - timedelta(days=2),
        "modify_date": datetime.now() - timedelta(days=1),
        "image_path": None,
        "view_count": 234,
        "user_id": 3
    },
    {
        "content": "마라톤 완주! 처음 뛰어본 풀코스인데 해냈다! 운동을 꾸준히 하니까 이런 일도 가능하네 🏃‍♂️",
        "create_date": datetime.now() - timedelta(days=29),
        "modify_date": datetime.now() - timedelta(days=28),
        "image_path": ["sample_images/021.JPG"],
        "view_count": 678,
        "user_id": 4
    },
    {
        "content": "가평 여행 추천! 쁘띠 프랑스에서 인증샷 찍고 캠핑까지. 서울 근처 관광지 최고 👍",
        "create_date": datetime.now() - timedelta(days=32),
        "modify_date": datetime.now() - timedelta(days=31),
        "image_path": None,
        "view_count": 512,
        "user_id": 5
    },
    {
        "content": "운동 후 회복 식사! 단백질 보충이 중요하다는 걸 깨달았어. 맛있게 먹으며 건강해지자 🥗",
        "create_date": datetime.now() - timedelta(days=10),
        "modify_date": datetime.now() - timedelta(days=9),
        "image_path": ["sample_images/022.JPG"],
        "view_count": 198,
        "user_id": 6
    },
    {
        "content": "종로 식당 순례! 맛있는 음식들이 너무 많아서 고르는 것도 힘들더라. 먹는 것이 낙이다 😍",
        "create_date": datetime.now() - timedelta(days=1),
        "modify_date": datetime.now(),
        "image_path": None,
        "view_count": 367,
        "user_id": 7
    },
    {
        "content": "바다 여행 가는 길! 수평선 보는 것만으로도 마음이 편해진다. 이런 여유가 필요한 시간이야 🌊",
        "create_date": datetime.now() - timedelta(days=27),
        "modify_date": datetime.now() - timedelta(days=26),
        "image_path": ["sample_images/023.JPG", "sample_images/024.JPG"],
        "view_count": 489,
        "user_id": 8
    },
    {
        "content": "스트릿 헬스 운동! 공원에서 맨몸 운동하는 것도 나름 짜릿하다. 자연 속에서 운동하니 기분 좋아 💪",
        "create_date": datetime.now() - timedelta(days=11),
        "modify_date": datetime.now() - timedelta(days=10),
        "image_path": None,
        "view_count": 241,
        "user_id": 1
    },
    {
        "content": "베트남 hanoi 여행! 혼잡하지만 매력있는 도시다. 현지 음식도 맛있고 관광도 재미있어 🇻🇳",
        "create_date": datetime.now() - timedelta(days=38),
        "modify_date": datetime.now() - timedelta(days=37),
        "image_path": None,
        "view_count": 356,
        "user_id": 2
    },
    {
        "content": "아침식사가 중요해! 맛있는 아침밥으로 하루를 시작하니 에너지가 다르네. 음식으로 시작하는 좋은 하루 🍳",
        "create_date": datetime.now() - timedelta(days=12),
        "modify_date": datetime.now() - timedelta(days=11),
        "image_path": None,
        "view_count": 424,
        "user_id": 3
    },
    {
        "content": "필라테스 그룹 레슨! 선생님이 정말 친절하고 동료들도 좋아서 운동이 더 즐겁다. 계속할 거야 🧘",
        "create_date": datetime.now() - timedelta(days=33),
        "modify_date": datetime.now() - timedelta(days=32),
        "image_path": None,
        "view_count": 267,
        "user_id": 4
    },
    {
        "content": "남이섬 봄 여행! 벚꽃 축제 시즌에 가니 사람도 많고 분위기도 최고다. 관광지 추천! 🌸",
        "create_date": datetime.now() - timedelta(days=23),
        "modify_date": datetime.now() - timedelta(days=22),
        "image_path": None,
        "view_count": 589,
        "user_id": 5
    },
    {
        "content": "초콜릿 디저트 만들기! 달콤한 케이크는 피로를 녹여줘. 집에서 만드는 홈메이드의 진정한 맛 🍰",
        "create_date": datetime.now() - timedelta(days=19),
        "modify_date": datetime.now() - timedelta(days=18),
        "image_path": None,
        "view_count": 445,
        "user_id": 6
    },
    {
        "content": "요가는 마음의 스포츠다! 몸도 좋아지지만 정신도 맑아지는 게 신기하네. 계속 해봐야겠다는 생각이 들어",
        "create_date": datetime.now() - timedelta(days=8),
        "modify_date": datetime.now() - timedelta(days=7),
        "image_path": None,
        "view_count": 312,
        "user_id": 7
    },
    {
        "content": "포항 여행 코스! 호미곶에서 해맞이 하고 영일만 카페거리도 최고. 해외 안 가도 좋은 곳이 많네 🏖️",
        "create_date": datetime.now() - timedelta(days=26),
        "modify_date": datetime.now() - timedelta(days=25),
        "image_path": None,
        "view_count": 434,
        "user_id": 8
    },
    {
        "content": "맛있는 국물요리! 되직한 육수에 신선한 재료... 음식은 정말 마법이야. 요리에 빠져있는 중 👨‍🍳",
        "create_date": datetime.now() - timedelta(days=15),
        "modify_date": datetime.now() - timedelta(days=14),
        "image_path": None,
        "view_count": 521,
        "user_id": 1
    },
    {
        "content": "런닝은 명상이다! 음악 들으며 달리다 보면 마음이 한결 가벼워진다. 건강하고 행복해지는 느낌 🎧",
        "create_date": datetime.now() - timedelta(days=31),
        "modify_date": datetime.now() - timedelta(days=30),
        "image_path": None,
        "view_count": 398,
        "user_id": 2
    }
]


def init_sample_posts():
    """example_talk_data의 30개 예시 글을 데이터베이스에 추가하는 함수"""
    # 순환 참조 방지를 위해 함수 내부에서 임포트
    from ajiteu import db, create_app         # 본인 플라스크 앱 파일명에 맞게 수정 (예: from main import db)
    from ajiteu.models import Post, User     # 본인 모델 파일명에 맞게 수정



    try:
        # 현재 사용자 수 확인
        user_count = User.query.count()

        # 총 8명이 되도록 부족한 사용자만 생성
        if User.query.count() < 8:
            for i in range(user_count + 1, 9):
                user = User(
                    username=f"user{i}",
                    nickname=f"사용자{i}",
                    email=f"user{i}@example.com",
                    password="hashed_password"
                )
                db.session.add(user)
            db.session.commit()
            print(f"✅샘플 사용자 {8 - user_count}명이 추가되었습니다")

        for data in sample_posts_data:

            image_path = None
            if data["image_path"]:
                image_path = ",".join(data["image_path"])
            post = Post(
                content=data["content"],
                create_date=data["create_date"],
                modify_date=data["modify_date"],
                image_path=image_path,
                view_count=data["view_count"],
                user_id=data["user_id"]
            )
            db.session.add(post)

        db.session.commit()
        print("✅게시글 40개가 데이터베이스에 성공적으로 추가되었습니다!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ 데이터 추가 중 오류 발생: {e}")

# # 스크립트 직접 실행 시 함수 호출
# if __name__ == "__main__":
#     init_sample_posts()