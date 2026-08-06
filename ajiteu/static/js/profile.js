document.addEventListener("DOMContentLoaded", () => {
  const photoInput = document.getElementById("image");
  const profileImg = document.getElementById("profileImg");
  const photoPlaceholder = document.getElementById("photoPlaceholder");

  if (!photoInput || !profileImg || !photoPlaceholder) return;

  photoInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowedTypes = ["image/jpeg", "image/jpg", "image/png"];
    if (!allowedTypes.includes(file.type)) {
      alert("JPG, JPEG, PNG 파일만 업로드할 수 있습니다.");
      photoInput.value = "";
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      profileImg.src = event.target.result;
      profileImg.hidden = false;
      photoPlaceholder.hidden = true;
    };
    reader.readAsDataURL(file);
  });
});