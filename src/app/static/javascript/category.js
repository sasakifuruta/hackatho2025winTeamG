document.addEventListener("DOMContentLoaded", function () {
  const modeSelect = document.getElementById("mode-select");
  const categorySelect = document.getElementById("category-select");

  function updateCategories() {
    const selectedMode = modeSelect.value;

    fetch(`/home/api/get_categories/?mode=${selectedMode}`)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        categorySelect.innerHTML = ""; // 既存のオプションをクリア
        data.categories.forEach((category) => {
          let option = document.createElement("option");
          option.value = category.id;
          option.textContent = category.name;
          categorySelect.appendChild(option);
        });
      })
      .catch((error) => console.error("カテゴリの取得に失敗しました:", error));
  }

  // 初回ロード時にカテゴリを更新
  updateCategories();

  modeSelect.addEventListener("change", updateCategories);
});
