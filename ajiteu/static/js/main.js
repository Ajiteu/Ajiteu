document.addEventListener('DOMContentLoaded', () => {
    let currentCategory = 'all';
    let currentSearchQuery = '';
    let globalPosts = [];

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
                if (!response.ok) throw new Error('서버 미연결');
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

    // 4. 게시글 카드 동적 렌더링 (타이틀 완전 삭제)
    function renderPosts(posts) {
        const postGrid = document.getElementById('postGrid');
        if (!postGrid) return;

        postGrid.innerHTML = '';

        if (!posts || posts.length === 0) {
            postGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem;">게시글이 존재하지 않습니다.</p>';
            return;
        }

        posts.forEach((post) => {
            const card = document.createElement('div');
            card.className = 'card-item';
            card.style.cursor = 'pointer';
            
            // 카드 클릭 시 닉네임 상세보기 모달만 단일 오픈
            card.addEventListener('click', (e) => {
                if (e.target.closest('.btn-more') || e.target.closest('.action-item')) return;
                openDetailModal(post);
            });

            // 타이틀 삭제 적용
            card.innerHTML = `
                <div class="card-top">
                    <div class="author-box">
                        <div class="author-avatar"></div>
                        <div class="author-meta">
                            <div class="author-name">${escapeHtml(post.author)}</div>
                            <div class="post-date">${escapeHtml(post.created_at)}</div>
                        </div>
                    </div>
                    <button class="btn-more" data-id="${post.id}">...</button>
                </div>
                <div class="card-middle">
                    <div class="thumb-box"></div>
                    <div class="text-box">
                        <div class="card-desc"></div>
                    </div>
                </div>
                <div class="card-bottom">
                    <a href="/like" class="action-item text-decoration-none text-reset">
                        <i class="icon">👍</i> ${post.like_count}
                    </a>
                    <a href="/comment" class="action-item text-decoration-none text-reset">
                        <i class="icon">💬</i> ${post.comment_count || 0}
                    </a>
                    <a href="/view" class="action-item text-decoration-none text-reset" style="display: inline-flex; align-items: center; gap: 4px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;">
                            <line x1="4" y1="9" x2="20" y2="9"></line>
                            <line x1="4" y1="15" x2="20" y2="15"></line>
                            <line x1="10" y1="3" x2="8" y2="21"></line>
                            <line x1="16" y1="3" x2="14" y2="21"></line>
                        </svg>
                        ${post.view_count || 156}
                    </a>
                </div>
            `;
            postGrid.appendChild(card);
        });

        // 카드 상단 더보기(...) 버튼 클릭 시 옵션 모달 오픈
        document.querySelectorAll('.btn-more').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const modal = document.getElementById('postOptionModal');
                if (modal) modal.classList.remove('hidden');
            });
        });
    }

    /* --- 5. 새글 작성 모달 제어 --- */
    const btnWriteOpen = document.getElementById('btnWriteOpen');
    if (btnWriteOpen) {
        btnWriteOpen.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('postModal').classList.add('active');
        });
    }

    const btnCancelWrite = document.getElementById('btnCancelWrite');
    if (btnCancelWrite) {
        btnCancelWrite.addEventListener('click', closeWriteModal);
    }

    function closeWriteModal() {
        document.getElementById('postModal').classList.remove('active');
        document.getElementById('postForm').reset();
        document.getElementById('imagePreview').innerHTML = '';
    }

    // 이미지 업로드 미리보기
    const imageUploadInput = document.getElementById('imageUploadInput');
    if (imageUploadInput) {
        imageUploadInput.addEventListener('change', (event) => {
            const previewContainer = document.getElementById('imagePreview');
            previewContainer.innerHTML = '';
            const files = event.target.files;

            if (files) {
                Array.from(files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'preview-img';
                        previewContainer.appendChild(img);
                    };
                    reader.readAsDataURL(file);
                });
            }
        });
    }

    document.getElementById('postForm').addEventListener('submit', (e) => {
        e.preventDefault();
        alert('글이 성공적으로 등록되었습니다.');
        closeWriteModal();
    });

    /* --- 6. 게시글 상세보기 모달 제어 --- */
    function openDetailModal(post) {
        if (post) {
            document.getElementById('detailAuthorName').innerText = post.author || '닉네임';
            document.getElementById('bottomLikeCount').innerText = post.like_count || 0;
            document.getElementById('bottomCommentCount').innerText = post.comment_count || 0;
            document.getElementById('bottomViewCount').innerText = post.view_count || 156;
        }
        document.getElementById('postDetailModal').classList.add('active');
    }

    const btnCloseDetail = document.getElementById('btnCloseDetail');
    if (btnCloseDetail) {
        btnCloseDetail.addEventListener('click', closeDetailModal);
    }

    function closeDetailModal() {
        document.getElementById('postDetailModal').classList.remove('active');
        document.getElementById('commentForm').reset();
        hideDetailDropdown();
    }

    // 모달 우측 상단 더보기(...) 내림 메뉴 토글
    const btnDetailMore = document.getElementById('btnDetailMore');
    const detailDropdownMenu = document.getElementById('detailDropdownMenu');

    if (btnDetailMore && detailDropdownMenu) {
        btnDetailMore.addEventListener('click', (e) => {
            e.stopPropagation();
            detailDropdownMenu.classList.toggle('hidden');
        });
    }

    function hideDetailDropdown() {
        if (detailDropdownMenu) {
            detailDropdownMenu.classList.add('hidden');
        }
    }

    // 상세보기 모달 우측 상단 팝업 메뉴 액션 버튼
    document.getElementById('btnDetailDelete')?.addEventListener('click', () => {
        alert('삭제 요청되었습니다.');
        hideDetailDropdown();
    });
    document.getElementById('btnDetailEdit')?.addEventListener('click', () => {
        alert('수정 화면으로 이동합니다.');
        hideDetailDropdown();
    });
    document.getElementById('btnDetailGo')?.addEventListener('click', () => {
        alert('게시물로 이동합니다.');
        hideDetailDropdown();
    });
    document.getElementById('btnDetailCancel')?.addEventListener('click', () => {
        hideDetailDropdown();
    });

    // 댓글 등록 처리
    document.getElementById('commentForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const input = document.getElementById('commentInput');
        if (input.value.trim() === '') return;

        const commentList = document.getElementById('commentList');
        const newComment = document.createElement('div');
        newComment.className = 'comment-item';
        newComment.innerHTML = `
            <div class="d-flex align-items-start gap-2">
                <div class="comment-profile-circle flex-shrink-0"></div>
                <div>
                    <div class="fw-bold small text-dark">작성자</div>
                    <div class="small text-secondary">${escapeHtml(input.value)}</div>
                </div>
            </div>
        `;
        commentList.appendChild(newComment);
        input.value = '';

        const mainCount = document.getElementById('mainCommentCount');
        const current = parseInt(mainCount.innerText) || 0;
        mainCount.innerText = current + 1;
        document.getElementById('bottomCommentCount').innerText = current + 1;
    });

    // 메인 더보기(...) 옵션 팝업 닫기 처리
    const btnCloseModal = document.getElementById('btnCloseModal');
    if (btnCloseModal) {
        btnCloseModal.addEventListener('click', () => {
            document.getElementById('postOptionModal').classList.add('hidden');
        });
    }

    // 배경 클릭 시 드롭다운 및 모달 닫기 이벤트
    window.addEventListener('click', (e) => {
        hideDetailDropdown();
        
        const optionModal = document.getElementById('postOptionModal');
        if (e.target === optionModal) {
            optionModal.classList.add('hidden');
        }
    });

    // HTML 태그 이스케이프 함수
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // 더미 데이터 생성기 (제목 없는 스펙 반영)
    function getDummyPosts() {
        const dummy = [];
        for (let i = 1; i <= 10; i++) {
            dummy.push({
                id: i,
                author: 'Author Name ' + i,
                created_at: '2024.08.13',
                like_count: i * 2,
                comment_count: i,
                view_count: 156 + i
            });
        }
        return dummy;
    }
});