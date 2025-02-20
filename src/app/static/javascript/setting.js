document
  .getElementById("save-work-time")
  .addEventListener("click", function () {
    const selectedTime = document.getElementById("work-time").value;

    fetch("/setting/api/save_work_time/", {
      method: "POST",
      headers: {
        "Content-Type": "application",
      },
      body: JSON.stringify({ study: selectedTime }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert("作業時間を " + selectedTime + " 分に設定しました！");
      })
      .catch((error) => console.error("作業時間の変更に失敗しました", error));
  });

document
  .getElementById("save-rest-time")
  .addEventListener("click", function () {
    const selectedTime = document.getElementById("rest-time").value;

    fetch("/setting/api/save_rest_time/", {
      method: "POST",
      headers: {
        "Content-Type": "application",
      },
      body: JSON.stringify({ rest: selectedTime }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert("休憩時間を " + selectedTime + " 分に設定しました！");
      })
      .catch((error) => console.error("休憩時間の変更に失敗しました", error));
  });

// 「カテゴリーを追加」を押したら作動する
document.getElementById("add-category").addEventListener("click", function () {
  const categoryName = document.getElementById("category-name").value.trim(); // .trim()で余計な空白を削除
  const categoryMode = document.querySelector(
    'input[name="category-mode"]:checked'
  ).value;
  const isOutput = categoryMode === "output"; // output なら true、それ以外は false に変換

  if (!categoryName) {
    alert("カテゴリー名を入力してください。");
    return;
  }

  fetch("/setting/api/add_category/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json", //送信するデータの形式を JSON に指定。
      "X-CSRFToken": getCookie("csrftoken"), // Django の CSRF トークンを取得
    },
    body: JSON.stringify({ category: categoryName, is_output: isOutput }), //categoryName（文字列）と isOutput（true/false）を JSON に変換し、リクエストの body に入れる
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("カテゴリーが追加されました！");
        document.getElementById("category-name").value = ""; // 入力フィールドをクリア
      } else {
        alert("カテゴリーの追加に失敗しました: " + data.message);
      }
    })
    .catch((error) => console.error("カテゴリーの追加に失敗しました:", error));
});

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".delete-category").forEach((button) => {
    button.addEventListener("click", function () {
      let categoryItem = this.closest(".category-item");

      if (!categoryItem) {
        console.error("削除エラー: categoryItem が見つかりません");
        alert("削除エラー: 要素が見つかりません");
        return;
      }

      let categoryId = categoryItem.dataset.id;

      // サーバーに削除リクエストを送信
      fetch("/setting/api/delete_category/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ id: categoryId }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            categoryItem.remove();
          } else {
            console.error("削除エラー：", data.error);
            alert("削除に失敗しました");
          }
        });
    });
  });
});

// DjangoのCSRFトークンを取得する関数;
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + "=")) {
        //クッキーが csrftoken=xxxxx の形式かチェック。
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1)); //クッキーの値を取得し、URLエンコードされている場合はデコード。
        break;
      }
    }
  }
  return cookieValue;
}

// CSRF トークン取得関数
function getCSRFToken() {
  let csrfToken = document.querySelector("input[name=csrfmiddlewaretoken]");
  return csrfToken ? csrfToken.value : "";
}
