/** main.html ↔ Flask 세션 API 연결 (main.js 보조) */

document.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("postGrid")) return;

  initUserSummary();
  initTrending();
  initPostActions();
  initPostOptionMenu();
  initWriteForm();
  initCommentForm();
  initDetailModal();
  initMyPostsPage();
  initProfileModal();
  bindImagePreview("imageUploadInput", "imagePreview");
  bindImagePreview("commentImageInput", "commentImagePreview");
  bindImagePreview("profileImageInput", "profileImagePreview");
});

async function apiRequest(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(path, {
    ...options,
    headers,
    credentials: "same-origin",
  });
  const data = await response.json().catch(() => ({}));

  if (!response.ok || data.ok === false) {
    throw new Error(data.message || "요청에 실패했습니다.");
  }

  return data.data !== undefined ? data.data : data;
}

function showToast(message, isError = false) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    toast.style.cssText =
      "position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#222;color:#fff;padding:12px 20px;border-radius:8px;z-index:9999;opacity:0;transition:opacity .2s";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.style.background = isError ? "#c0392b" : "#222";
  toast.style.opacity = "1";
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    toast.style.opacity = "0";
  }, 2500);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function uploadImageFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch("/api/posts/upload", {
    method: "POST",
    body: formData,
    credentials: "same-origin",
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.ok === false) {
    throw new Error(data.message || "이미지 업로드에 실패했습니다.");
  }
  const payload = data.data !== undefined ? data.data : data;
  return payload.url || payload.image_path;
}

async function uploadImageFiles(fileList) {
  const files = Array.from(fileList || []).filter((file) => file && file.type.startsWith("image/"));
  const urls = [];
  for (const file of files) {
    urls.push(await uploadImageFile(file));
  }
  return urls;
}

function bindImagePreview(inputId, previewId) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  if (!input || !preview) return;

  input.addEventListener("change", () => {
    preview.innerHTML = "";
    Array.from(input.files || []).forEach((file) => {
      const reader = new FileReader();
      reader.onload = (event) => {
        const img = document.createElement("img");
        img.src = event.target.result;
        img.className = "preview-img";
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  });
}

function setProfileImage(url) {
  const img = document.getElementById("sidebarProfileImg");
  if (img && url) img.src = url;
}

function renderDetailImages(images) {
  const box = document.querySelector(".detail-image-box");
  if (!box) return;
  const list = (images || []).filter(Boolean);
  if (!list.length) {
    box.innerHTML = "";
    box.classList.remove("empty-placeholder");
    return;
  }
  box.classList.remove("empty-placeholder");
  box.innerHTML = list
    .map(
      (url) =>
        `<img src="${escapeHtml(url)}" alt="게시글 이미지" class="detail-post-image">`
    )
    .join("");
}

async function initUserSummary() {
  const userName = document.getElementById("userName");
  const userBio = document.getElementById("userBio");
  const modalNickname = document.getElementById("modalUserNickname");
  if (!userName) return;

  try {
    const me = await apiRequest("/api/me");
    userName.textContent = me.nickname || me.username;
    userBio.textContent = me.bio || "프로필 소개를 작성해 보세요.";
    if (modalNickname) modalNickname.textContent = me.nickname || me.username;
    if (me.profile_image) setProfileImage(me.profile_image);
  } catch (_) {
    userName.textContent = "닉네임";
    userBio.textContent = "프로필 소개";
  }
}

async function initTrending() {
  const list =
    document.getElementById("trend-list") ||
    document.querySelector(".widget-list.trend");
  if (!list) return;

  try {
    const data = await apiRequest("/api/posts/trending?limit=5");
    const items = data.items || [];
    if (!items.length) {
      list.innerHTML = '<li class="list-item">트렌드 게시글이 없습니다.</li>';
      return;
    }

    list.innerHTML = items
      .map(
        (post) =>
          `<li class="list-item trend-item" data-post-id="${post.id}" style="cursor:pointer;">${escapeHtml(post.title)}</li>`
      )
      .join("");

    list.querySelectorAll(".trend-item").forEach((el) => {
      el.addEventListener("click", async () => {
        const postId = Number(el.dataset.postId);
        const post = (window.globalPosts || []).find((p) => p.id === postId);
        if (post) {
          openDetailWithFetch(post);
          return;
        }
        try {
          const detail = await apiRequest(`/api/posts/${postId}`);
          openDetailWithFetch(detail);
        } catch (error) {
          showToast(error.message, true);
        }
      });
    });
  } catch (error) {
    list.innerHTML = `<li class="list-item">${escapeHtml(error.message)}</li>`;
  }
}

function initPostActions() {
  const grid = document.getElementById("postGrid");
  if (!grid || grid.dataset.statsBound === "true") return;
  grid.dataset.statsBound = "true";

  grid.addEventListener("click", async (e) => {
    const likeEl = e.target.closest(".action-like");
    const commentEl = e.target.closest(".action-comment");
    const viewEl = e.target.closest(".action-view");

    if (likeEl) {
      e.preventDefault();
      e.stopPropagation();
      await toggleLike(Number(likeEl.dataset.postId), likeEl);
      return;
    }

    if (commentEl || viewEl) {
      e.preventDefault();
      e.stopPropagation();
      const postId = Number((commentEl || viewEl).dataset.postId);
      const post = (window.globalPosts || []).find((p) => p.id === postId);
      if (post) openDetailWithFetch(post);
    }
  });

  const detailModal = document.getElementById("postDetailModal");
  if (detailModal) {
    detailModal.addEventListener("click", async (e) => {
      const likeEl = e.target.closest(".action-like");
      if (!likeEl) return;
      e.preventDefault();
      const post = window.currentDetailPost;
      if (!post) return;
      await toggleLike(post.id, likeEl, true);
    });
  }
}

async function toggleLike(postId, element, isDetail = false) {
  try {
    const result = await apiRequest(`/api/posts/${postId}/like`, {
      method: "POST",
    });

    if (isDetail) {
      element.innerHTML = `<i class="icon">👍</i> <strong id="bottomLikeCount">${result.like_count}</strong>`;
    } else {
      element.innerHTML = `<i class="icon">👍</i> ${result.like_count}`;
    }

    const post = (window.globalPosts || []).find((p) => p.id === postId);
    if (post) {
      post.like_count = result.like_count;
      post.liked_by_me = result.liked;
    }
    if (window.currentDetailPost && window.currentDetailPost.id === postId) {
      window.currentDetailPost.like_count = result.like_count;
      const countEl = document.getElementById("bottomLikeCount");
      if (countEl) countEl.textContent = result.like_count;
    }

    showToast(result.liked ? "좋아요!" : "좋아요 취소");
  } catch (error) {
    showToast(error.message, true);
  }
}

function initWriteForm() {
  const writeOpenBtn = document.getElementById("btnWriteOpen");
  writeOpenBtn?.addEventListener("click", () => {
    resetWriteModalMode();
  });

  window.handlePostSubmit = async function handlePostSubmit() {
    const contentEl = document.getElementById("postContent");
    const imageInput = document.getElementById("imageUploadInput");
    const content = contentEl ? contentEl.value.trim() : "";
    const editingId = window.editingPostId || null;
    const existingPost = editingId
      ? (window.globalPosts || []).find((p) => p.id === editingId) ||
        window.currentDetailPost
      : null;

    try {
      let imagePath = existingPost?.image_path || null;
      if (imageInput?.files?.length) {
        const urls = await uploadImageFiles(imageInput.files);
        imagePath = urls.join(",");
      }

      if (!content && !imagePath) {
        showToast("내용 또는 사진을 입력해주세요.", true);
        return;
      }

      if (editingId) {
        await apiRequest(`/api/posts/${editingId}`, {
          method: "PUT",
          body: JSON.stringify({ content, image_path: imagePath }),
        });
        showToast("글이 수정되었습니다.");
      } else {
        await apiRequest("/api/posts", {
          method: "POST",
          body: JSON.stringify({ content, image_path: imagePath }),
        });
        showToast("글이 등록되었습니다.");
      }

      resetWriteModalMode();
      document.getElementById("postModal")?.classList.remove("active");
      document.getElementById("postForm")?.reset();
      document.getElementById("imagePreview").innerHTML = "";

      if (window.currentDetailPost?.id === editingId) {
        closeDetailModal();
      }

      if (typeof window.fetchPosts === "function") {
        window.fetchPosts(
          typeof window.getCurrentPage === "function" ? window.getCurrentPage() : 1
        );
      }
      initTrending();
    } catch (error) {
      showToast(error.message, true);
    }
  };
}

function resetWriteModalMode() {
  window.editingPostId = null;
  window.editingPostImagePath = null;
  const title = document.querySelector("#postModal h5");
  if (title) title.textContent = "새글 작성";
}

window.resetWriteModalMode = resetWriteModalMode;

function initPostOptionMenu() {
  bindPostMenuAction("btnDetailDelete", handlePostDelete);
  bindPostMenuAction("btnDetailEdit", handlePostEdit);
  bindPostMenuAction("btnDetailGo", handlePostGo);
  bindPostMenuAction("btnDetailCancel", closeDetailDropdown);

  bindPostMenuAction("btnDeletePost", () =>
    handlePostDelete(getSelectedOptionPost())
  );
  bindPostMenuAction("btnEditPost", () => handlePostEdit(getSelectedOptionPost()));
  bindPostMenuAction("btnGoPost", () => handlePostGo(getSelectedOptionPost()));
}

function bindPostMenuAction(buttonId, handler) {
  const button = document.getElementById(buttonId);
  if (!button || button.dataset.bound === "true") return;
  button.dataset.bound = "true";
  button.addEventListener("click", async (e) => {
    e.stopPropagation();
    await handler();
  });
}

function getSelectedOptionPost() {
  const postId = Number(window.selectedOptionPostId);
  if (!Number.isFinite(postId)) return null;
  return (window.globalPosts || []).find((p) => p.id === postId) || { id: postId };
}

function closeDetailDropdown() {
  document.getElementById("detailDropdownMenu")?.classList.add("hidden");
}

function closePostOptionModal() {
  document.getElementById("postOptionModal")?.classList.add("hidden");
  window.selectedOptionPostId = null;
}

function closeDetailModal() {
  document.getElementById("postDetailModal")?.classList.remove("active");
  document.getElementById("commentForm")?.reset();
  document.getElementById("commentImagePreview").innerHTML = "";
  closeDetailDropdown();
}

async function ensureOwnPost(post) {
  if (!post?.id) {
    showToast("게시글 정보를 찾을 수 없습니다.", true);
    return false;
  }

  try {
    const me = await apiRequest("/api/me");
    if (post.user_id && post.user_id !== me.id) {
      showToast("본인이 작성한 글만 할 수 있습니다.", true);
      return false;
    }
    return true;
  } catch (error) {
    showToast(error.message, true);
    return false;
  }
}

async function handlePostDelete(post = window.currentDetailPost) {
  closeDetailDropdown();
  closePostOptionModal();

  if (!(await ensureOwnPost(post))) return;
  if (!confirm("정말로 삭제하시겠습니까?")) return;

  try {
    await apiRequest(`/api/posts/${post.id}`, { method: "DELETE" });
    showToast("게시글이 삭제되었습니다.");
    closeDetailModal();
    if (typeof window.fetchPosts === "function") {
      window.fetchPosts(
        typeof window.getCurrentPage === "function" ? window.getCurrentPage() : 1
      );
    }
    initTrending();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function handlePostEdit(post = window.currentDetailPost) {
  closeDetailDropdown();
  closePostOptionModal();

  if (!post?.id) {
    showToast("게시글 정보를 찾을 수 없습니다.", true);
    return;
  }

  let detail;
  try {
    detail = await apiRequest(`/api/posts/${post.id}?count_view=0`);
    if (!(await ensureOwnPost(detail))) return;
  } catch (error) {
    showToast(error.message, true);
    return;
  }

  window.editingPostId = detail.id;
  window.editingPostImagePath = detail.image_path || null;

  const title = document.querySelector("#postModal h5");
  if (title) title.textContent = "글 수정";

  const contentEl = document.getElementById("postContent");
  if (contentEl) {
    contentEl.value =
      detail.content && detail.content !== "(사진)" ? detail.content : "";
  }

  const preview = document.getElementById("imagePreview");
  if (preview) {
    preview.innerHTML = "";
    const images =
      detail.images ||
      (detail.image_path ? String(detail.image_path).split(",") : []);
    images.filter(Boolean).forEach((url) => {
      const img = document.createElement("img");
      img.src = url;
      img.alt = "기존 이미지";
      preview.appendChild(img);
    });
  }

  document.getElementById("imageUploadInput").value = "";
  closeDetailModal();
  document.getElementById("postModal")?.classList.add("active");
}

function handlePostGo(post = window.currentDetailPost) {
  closeDetailDropdown();
  closePostOptionModal();

  if (!post?.id) {
    showToast("게시글 정보를 찾을 수 없습니다.", true);
    return;
  }

  closeDetailModal();

  const card =
    document.querySelector(`.btn-more[data-id="${post.id}"]`)?.closest(".card-item") ||
    document.querySelector(`.card-item[data-post-id="${post.id}"]`);

  if (!card) {
    showToast("현재 목록에서 게시물을 찾을 수 없습니다.", true);
    return;
  }

  document.querySelector(".cards-scroll-area")?.scrollTo({ top: 0, behavior: "smooth" });
  card.scrollIntoView({ behavior: "smooth", block: "center" });
  card.classList.add("post-highlight");
  window.setTimeout(() => card.classList.remove("post-highlight"), 1800);
}

function initCommentForm() {
  window.handleCommentSubmit = async function handleCommentSubmit() {
    const post = window.currentDetailPost;
    const input = document.getElementById("commentInput");
    const imageInput = document.getElementById("commentImageInput");
    const content = input ? input.value.trim() : "";

    if (!post) return;

    try {
      let imagePath = null;
      if (imageInput?.files?.[0]) {
        imagePath = await uploadImageFile(imageInput.files[0]);
      }

      if (!content && !imagePath) {
        showToast("댓글 내용 또는 사진을 입력해주세요.", true);
        return;
      }

      await apiRequest(`/api/posts/${post.id}/comments`, {
        method: "POST",
        body: JSON.stringify({ content, image_path: imagePath }),
      });
      input.value = "";
      if (imageInput) imageInput.value = "";
      document.getElementById("commentImagePreview").innerHTML = "";
      post.comment_count = (post.comment_count || 0) + 1;
      document.getElementById("bottomCommentCount").textContent =
        post.comment_count;
      document.getElementById("mainCommentCount").textContent =
        post.comment_count;
      await loadComments(post.id);
      showToast("댓글이 등록되었습니다.");
      if (typeof window.fetchPosts === "function") {
        window.fetchPosts(typeof window.getCurrentPage === "function" ? window.getCurrentPage() : 1);
      }
    } catch (error) {
      showToast(error.message, true);
    }
  };
}

function initDetailModal() {
  document.addEventListener("ajiteu:detail-open", async (event) => {
    const post = event.detail?.post;
    if (!post) return;
    await openDetailWithFetch(post);
  });

  const prevBtn = document.getElementById("btnDetailPrev");
  const nextBtn = document.getElementById("btnDetailNext");

  prevBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    navigateDetailPost(-1);
  });

  nextBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    navigateDetailPost(1);
  });

  document.addEventListener("keydown", (e) => {
    const modal = document.getElementById("postDetailModal");
    if (!modal?.classList.contains("active")) return;
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      navigateDetailPost(-1);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      navigateDetailPost(1);
    }
  });
}

function getDetailPostIndex() {
  const posts = window.globalPosts || [];
  const current = window.currentDetailPost;
  if (!current) return -1;
  return posts.findIndex((p) => p.id === current.id);
}

function updateDetailNavButtons() {
  const prevBtn = document.getElementById("btnDetailPrev");
  const nextBtn = document.getElementById("btnDetailNext");
  if (!prevBtn || !nextBtn) return;

  const posts = window.globalPosts || [];
  const idx = getDetailPostIndex();
  const page = typeof window.getCurrentPage === "function" ? window.getCurrentPage() : 1;
  const totalPages =
    typeof window.getTotalPages === "function" ? window.getTotalPages() : 1;

  if (idx < 0) {
    prevBtn.disabled = true;
    nextBtn.disabled = true;
    return;
  }

  prevBtn.disabled = idx <= 0 && page <= 1;
  nextBtn.disabled = idx >= posts.length - 1 && page >= totalPages;
}

async function navigateDetailPost(offset) {
  const posts = window.globalPosts || [];
  const idx = getDetailPostIndex();
  if (idx < 0) return;

  const page = typeof window.getCurrentPage === "function" ? window.getCurrentPage() : 1;
  const totalPages =
    typeof window.getTotalPages === "function" ? window.getTotalPages() : 1;
  const nextIdx = idx + offset;

  if (nextIdx >= 0 && nextIdx < posts.length) {
    await openDetailWithFetch(posts[nextIdx]);
    return;
  }

  if (offset < 0 && idx === 0 && page > 1 && typeof window.fetchPosts === "function") {
    await window.fetchPosts(page - 1);
    const prevPagePosts = window.globalPosts || [];
    if (prevPagePosts.length) {
      await openDetailWithFetch(prevPagePosts[prevPagePosts.length - 1]);
    }
    return;
  }

  if (
    offset > 0 &&
    idx === posts.length - 1 &&
    page < totalPages &&
    typeof window.fetchPosts === "function"
  ) {
    await window.fetchPosts(page + 1);
    const nextPagePosts = window.globalPosts || [];
    if (nextPagePosts.length) {
      await openDetailWithFetch(nextPagePosts[0]);
    }
  }
}

function scrollDetailToTop() {
  document.querySelector(".modal-detail-body")?.scrollTo({ top: 0, behavior: "smooth" });
}

function updateCardViewCount(postId, viewCount) {
  const viewEl = document.querySelector(
    `.action-view[data-post-id="${postId}"]`
  );
  if (!viewEl) return;

  const svg = viewEl.querySelector("svg");
  viewEl.innerHTML = "";
  if (svg) viewEl.appendChild(svg.cloneNode(true));
  viewEl.append(` ${viewCount}`);
}

async function openDetailWithFetch(post) {
  try {
    const detail = await apiRequest(`/api/posts/${post.id}`);
    window.currentDetailPost = { ...post, ...detail };

    document.getElementById("detailAuthorName").innerText =
      detail.author || post.author || "닉네임";
    document.getElementById("detailContent").innerText =
      detail.content || post.content || "";
    renderDetailImages(
      detail.images ||
        (detail.image_url ? [detail.image_url] : []) ||
        (detail.image_path ? String(detail.image_path).split(",") : [])
    );
    document.getElementById("bottomLikeCount").innerText =
      detail.like_count || 0;
    document.getElementById("bottomCommentCount").innerText =
      detail.comment_count || 0;
    document.getElementById("bottomViewCount").innerText =
      detail.view_count || 0;
    document.getElementById("mainCommentCount").innerText =
      detail.comment_count || 0;

    const detailModal = document.getElementById("postDetailModal");
    if (detailModal) detailModal.classList.add("active");

    document.getElementById("commentForm")?.reset();
    document.getElementById("commentImagePreview").innerHTML = "";

    await loadComments(post.id);
    scrollDetailToTop();
    updateDetailNavButtons();

    const cardPost = (window.globalPosts || []).find((p) => p.id === post.id);
    if (cardPost) cardPost.view_count = detail.view_count;
    updateCardViewCount(post.id, detail.view_count || 0);
  } catch (error) {
    showToast(error.message, true);
  }
}

window.openDetailWithFetch = openDetailWithFetch;

function initProfileModal() {
  const openBtn = document.getElementById("btnProfileOpen");
  const modal = document.getElementById("profileModal");
  const form = document.getElementById("profileForm");
  const cancelBtn = document.getElementById("btnCancelProfile");
  if (!openBtn || !modal || !form) return;

  openBtn.addEventListener("click", async () => {
    try {
      const me = await apiRequest("/api/me");
      document.getElementById("profileNickname").value =
        me.nickname || me.username || "";
      document.getElementById("profileBio").value = me.bio || "";
      const preview = document.getElementById("profileImagePreview");
      if (preview) {
        preview.innerHTML = me.profile_image
          ? `<img src="${escapeHtml(me.profile_image)}" class="preview-img" alt="프로필 미리보기">`
          : "";
      }
      modal.classList.add("active");
    } catch (error) {
      showToast(error.message, true);
    }
  });

  cancelBtn?.addEventListener("click", () => {
    modal.classList.remove("active");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const nickname = document.getElementById("profileNickname").value.trim();
    const bio = document.getElementById("profileBio").value.trim();
    const imageInput = document.getElementById("profileImageInput");
    if (!nickname) {
      showToast("닉네임을 입력해주세요.", true);
      return;
    }

    try {
      let profileImage = null;
      if (imageInput?.files?.[0]) {
        profileImage = await uploadImageFile(imageInput.files[0]);
      }

      const payload = { nickname, bio };
      if (profileImage) payload.profile_image = profileImage;

      const updated = await apiRequest("/api/profile", {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      document.getElementById("userName").textContent =
        updated.nickname || updated.username;
      document.getElementById("userBio").textContent =
        updated.bio || "프로필 소개를 작성해 보세요.";
      document.getElementById("modalUserNickname").textContent =
        updated.nickname || updated.username;
      if (updated.profile_image) setProfileImage(updated.profile_image);
      if (imageInput) imageInput.value = "";
      modal.classList.remove("active");
      showToast("프로필이 저장되었습니다.");
    } catch (error) {
      showToast(error.message, true);
    }
  });
}

async function loadComments(postId) {
  const commentList = document.getElementById("commentList");
  if (!commentList) return;

  try {
    const comments = await apiRequest(`/api/posts/${postId}/comments`);
    if (!comments.length) {
      commentList.innerHTML =
        '<div class="small text-secondary">아직 댓글이 없습니다.</div>';
      return;
    }

    commentList.innerHTML = comments
      .map(
        (comment) => `
        <div class="comment-item">
          <div class="d-flex align-items-start gap-2">
            <div class="comment-profile-circle flex-shrink-0"></div>
            <div>
              <div class="fw-bold small text-dark">${escapeHtml(comment.author.nickname)}</div>
              <div class="small text-secondary">${escapeHtml(comment.content)}</div>
              ${
                comment.image_url
                  ? `<img src="${escapeHtml(comment.image_url)}" alt="댓글 이미지" class="comment-image mt-1">`
                  : ""
              }
            </div>
          </div>
        </div>`
      )
      .join("");
  } catch (error) {
    commentList.innerHTML = `<div class="small text-danger">${escapeHtml(error.message)}</div>`;
  }
}

async function initMyPostsPage() {
  if (window.PAGE_MODE !== "my_posts") return;

  const title = document.querySelector(".community-title");
  if (title) title.textContent = "내가 쓴 글";

  try {
    const data = await apiRequest("/api/posts/mine?page=1&per_page=20");
    window.globalPosts = data.items || data.posts || [];
    if (typeof window.renderPosts === "function") {
      window.renderPosts(window.globalPosts);
    }
    if (typeof window.renderPagination === "function") {
      window.renderPagination({
        total: data.total || window.globalPosts.length,
        page: 1,
        pages: 1,
      });
    }
  } catch (error) {
    document.getElementById("postGrid").innerHTML =
      `<p style="grid-column:1/-1;text-align:center;padding:2rem;">${escapeHtml(error.message)}</p>`;
  }
}

window.renderPosts = window.renderPosts;
