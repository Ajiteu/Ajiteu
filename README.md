2. 모달 전체 점검 및 1차 수정
분석한 구조

모달 HTML: post_detail.html, profile.html, post_create.html, main.html의 #ajiteuPageOverlay
열기: openPostDetailModal, openProfileModal, openWriteModal, openAjiteuActionSheet
닫기: closeAjiteuPageOverlay, .js-close-page-overlay (document 위임)
main.js는 주석 처리되어 있어 충돌 없음
수정한 문제

소개글 클릭 → 프로필 모달 (openProfileModal 연결)
모달 닫기 (X, 취소, ESC, 바깥 클릭)
... 메뉴 (수정 → openWriteModalFromUri, 이동 로직 정리)
댓글 등록 후 overlay 유지 + 내용 갱신 (fetch POST 후 reloadPostDetailInOverlay)
JS 중복 제거 (post_detail.html block script 정리, bindPostDetailOverlay로 통합)
이벤트 리스너 중복 방지 (data-*-bound 플래그)
수정 파일

ajiteu/templates/main.html (핵심 JS)
ajiteu/templates/post_detail.html
ajiteu/templates/profile.html
3. 추가 수정 (2가지)
① 게시물로 이동 시 overlay/backdrop 잔류
resetModalUiState() 추가 → action sheet, page overlay, .modal-backdrop, body.modal-open 정리
closeAjiteuPageOverlay, closeAjiteuActionSheet 보강
② 1번째 댓글만 수정 안 됨
원인: onclick="editComment(id, {{ content | tojson }})"에서 HTML 속성 따옴표 충돌 + 내용 미이스케이프
해결: js-edit-comment + data-comment-id + .comment-text에서 textContent 읽기
댓글 본문 | e 이스케이프 적용
4. 게시물로 이동 overlay 미적용 (최종 수정)
일반 게시물 클릭	게시물로 이동 (수정 전)
함수
openPostDetailModal()
navigateToPostPage() → 전체 페이지 이동
배경
#ajiteuPageOverlay ✅
overlay 없음 ❌
최종 수정

navigateToPostPage() 제거
게시물로 이동도 closeAjiteuActionSheet() → openPostDetailModal(postId) 사용 (일반 클릭과 동일)
