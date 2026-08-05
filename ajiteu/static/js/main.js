document.addEventListener('DOMContentLoaded', () => {
    let currentCategory = 'all';
    let currentSearchQuery = '';
    
    // 슬라이드 모달 관리용 변수
    let globalPosts = [];
    let currentSlideIndex = 0;

    // 슬라이드 모달 DOM 생성
    createSlideModal();

    // 초기 게시글 로드
    fetchPosts();

    // 1. 카테고리 클릭 이벤트
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', (e) => {
            document.querySelectorAll('.category-item').forEach(el => el.classList.remove('active'));
            e.target.classList.add('active');
            currentCategory = e.target.dataset.category || 'all';
            fetchPosts();
        });
    });

    // 2. 검색 이벤트
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');

    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            currentSearchQuery = searchInput.value.trim();
            fetchPosts();
        });
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                currentSearchQuery = e.target.value.trim();
                fetchPosts();
            }
        });
    }

    // 3. API 데이터 호출
    function fetchPosts() {
        const url = `/api/posts?category=${encodeURIComponent(currentCategory)}&search=${encodeURIComponent(currentSearchQuery)}`;

        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('서버 미연결 (Live Server)');
                return response.json();
            })
            .then(data => {
                globalPosts = data.posts || [];
                renderPosts(globalPosts);
            })
            .catch(err => {
                console.warn('Backend API 미연결. 더미 데이터를 출력합니다.');
                globalPosts = getDummyPosts();
                renderPosts(globalPosts);
            });
    }

    // 4. 게시글 카드 동적 렌더링
    function renderPosts(posts) {
        const postGrid = document.getElementById('postGrid');
        if (!postGrid) return;

        postGrid.innerHTML = '';

        if (!posts || posts.length === 0) {
            postGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem;">게시글이 존재하지 않습니다.</p>';
            return;
        }

        posts.forEach((post, index) => {
            const card = document.createElement('div');
            card.className = 'card-item';
            card.style.cursor = 'pointer';
            
            // 카드 클릭 시 크게 보기 슬라이드 모달 오픈 (더보기 버튼 클릭 제외)
            card.addEventListener('click', (e) => {
                if (e.target.classList.contains('btn-more')) return;
                openSlideModal(index);
            });

            card.innerHTML = `
                <div class="card-top">
                    <div class="author-box">
                        <div class="author-avatar"></div>
                        <div class="author-meta">
                            <div class="author-name">${escapeHtml(post.author)}</div>
                            <div class="post-date">${post.created_at}</div>
                        </div>
                    </div>
                    <button class="btn-more" data-id="${post.id}">...</button>
                </div>
                <div class="card-middle">
                    <div class="thumb-box"></div>
                    <div class="text-box">
                        <div class="card-title">${escapeHtml(post.title)}</div>
                        <div class="card-desc">${escapeHtml(post.excerpt)}</div>
                    </div>
                </div>
                <div class="card-bottom">
                    <!-- 글자 제거, 아이콘과 숫자만 표시 -->
                    <span class="action-item"><i class="icon">👍</i> ${post.like_count}</span>
                    <span class="action-item"><i class="icon">💬</i> ${post.comment_count || 0}</span>
                    <!-- 해시태그 SVG 아이콘 적용 -->
                    <span class="action-item" style="display: inline-flex; align-items: center; gap: 4px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;">
                            <line x1="4" y1="9" x2="20" y2="9"></line>
                            <line x1="4" y1="15" x2="20" y2="15"></line>
                            <line x1="10" y1="3" x2="8" y2="21"></line>
                            <line x1="16" y1="3" x2="14" y2="21"></line>
                        </svg>
                        ${post.view_count || 156}
                    </span>
                </div>
            `;
            postGrid.appendChild(card);
        });

        // 더보기 (...) 버튼 이벤트
        document.querySelectorAll('.btn-more').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const modal = document.getElementById('postOptionModal');
                if (modal) modal.classList.remove('hidden');
            });
        });
    }

    // 5. 슬라이드 모달 생성 및 관리
    function createSlideModal() {
        const modalOverlay = document.createElement('div');
        modalOverlay.id = 'cardSlideModal';
        modalOverlay.className = 'card-modal-overlay';
        modalOverlay.innerHTML = `
            <div class="modal-card-container">
                <button class="modal-close-btn">&times;</button>
                <button class="slide-btn prev">&lt;</button>
                <button class="slide-btn next">&gt;</button>
                <div class="slide-wrapper" id="slideWrapper"></div>
            </div>
        `;
        document.body.appendChild(modalOverlay);

        modalOverlay.querySelector('.modal-close-btn').addEventListener('click', closeSlideModal);
        modalOverlay.querySelector('.slide-btn.prev').addEventListener('click', () => changeSlide(-1));
        modalOverlay.querySelector('.slide-btn.next').addEventListener('click', () => changeSlide(1));
        
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeSlideModal();
        });
    }

    function openSlideModal(index) {
        currentSlideIndex = index;
        const modal = document.getElementById('cardSlideModal');
        modal.classList.add('active');
        renderSlideContent();
    }

    function closeSlideModal() {
        const modal = document.getElementById('cardSlideModal');
        modal.classList.remove('active');
    }

    function changeSlide(direction) {
        const newIndex = currentSlideIndex + direction;
        if (newIndex >= 0 && newIndex < globalPosts.length) {
            currentSlideIndex = newIndex;
            renderSlideContent();
        }
    }

    function renderSlideContent() {
        const wrapper = document.getElementById('slideWrapper');
        const post = globalPosts[currentSlideIndex];
        if (!post) return;

        const newSlide = document.createElement('div');
        newSlide.className = 'slide-card';
        newSlide.innerHTML = `
            <div class="card-top" style="border-bottom: 1px solid #eee; padding-bottom: 15px;">
                <div class="author-box" style="display: flex; align-items: center; gap: 12px;">
                    <div class="author-avatar" style="width: 48px; height: 48px; border-radius: 50%; background: #e0e0e0;"></div>
                    <div class="author-meta">
                        <div class="author-name" style="font-size: 1.4rem; font-weight: bold; color: #222;">${escapeHtml(post.author)}</div>
                        <div class="post-date" style="font-size: 0.9rem; color: #888;">${post.created_at}</div>
                    </div>
                </div>
            </div>
            <div class="card-middle" style="margin: 30px 0; flex: 1; overflow-y: auto;">
                <h1 style="font-size: 2rem; font-weight: bold; margin-bottom: 20px; color: #111;">${escapeHtml(post.title)}</h1>
                <p style="font-size: 1.15rem; line-height: 1.8; color: #444; white-space: pre-line;">${escapeHtml(post.excerpt)}</p>
            </div>
            <div class="card-bottom" style="border-top: 1px solid #eee; padding-top: 15px; display: flex; gap: 20px; font-size: 1rem; color: #666;">
                <span class="action-item"><i class="icon">👍</i> ${post.like_count}</span>
                <span class="action-item"><i class="icon">💬</i> ${post.comment_count || 0}</span>
                <span class="action-item" style="display: inline-flex; align-items: center; gap: 6px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="4" y1="9" x2="20" y2="9"></line>
                        <line x1="4" y1="15" x2="20" y2="15"></line>
                        <line x1="10" y1="3" x2="8" y2="21"></line>
                        <line x1="16" y1="3" x2="14" y2="21"></line>
                    </svg>
                    ${post.view_count || 156}
                </span>
            </div>
        `;

        wrapper.innerHTML = '';
        wrapper.appendChild(newSlide);

        setTimeout(() => {
            newSlide.classList.add('active');
        }, 10);
    }

    // 팝업 모달 닫기 이벤트
    const btnCloseModal = document.getElementById('btnCloseModal');
    if (btnCloseModal) {
        btnCloseModal.addEventListener('click', () => {
            document.getElementById('postOptionModal').classList.add('hidden');
        });
    }

    // HTML 태그 이스케이프 함수
    function escapeHtml(str) {
        return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : '';
    }

    // 더미 데이터 생성기
    function getDummyPosts() {
        const dummy = [];
        for (let i = 1; i <= 10; i++) {
            dummy.push({
                id: i,
                author: 'Author Name ' + i,
                title: 'Community communities size test ' + i,
                excerpt: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                created_at: '2024.08.13',
                like_count: i * 2,
                comment_count: i,
                view_count: 156 + i
            });
        }
        return dummy;
    }
});
