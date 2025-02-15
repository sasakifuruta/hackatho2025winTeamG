document.addEventListener("DOMContentLoaded", function () {
  const countDown = document.getElementById("countdown");
  const startButton = document.getElementById("start-timer");
  const pauseButton = document.getElementById("pause-timer");
  const resumeButton = document.getElementById("resume-timer");
  const resetButton = document.getElementById("reset-timer");
  const modeSelect = document.getElementById("mode-select");
  const categorySelect = document.getElementById("category-select");
  const stopRestButton = document.getElementById("stop-rest-timer");
  const statusText = document.getElementById("status-text");

  let interval; // タイマーのID
  let targetTime; // カウントダウンの終了時間
  let startTime; // カウントダウンの開始時間
  let remainingTime = 0; // 一時停止時の残り時間
  let isPaused = false; // 一時停止状態かどうか
  let isStudy = true; // 勉強時間かどうか（falseの場合は休憩時間）

  // 残り時間を表示する関数
  function updateCountDown() {
    const now = new Date().getTime(); // 現在の時刻を取得（ミリ秒単位）
    const distance = targetTime - now;
    if (isStudy) {
      statusText.textContent = "作業中";
    } else {
      statusText.textContent = "休憩中";
    }

    if (distance <= 0) {
      clearInterval(interval); // タイマーを停止
      if (isStudy) {
        storeElapsedTime();
        startRestTimer();
      } else {
        startButton.disabled = false;
        modeSelect.disabled = false;
        categorySelect.disabled = false;
        stopRestButton.disabled = true;
        isStudy = true;
        statusText.textContent = "準備中";
      }
      return;
    }

    const hours = Math.floor(
      (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
    );
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    countDown.textContent = `${String(hours).padStart(2, "0")}:${String(
      minutes
    ).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`; // カウントダウンの時間をフォーマットして表示（2桁に揃える）
  }

  // タイマーを起動する関数
  function startTimer() {
    if (interval) {
      clearInterval(interval);
    }

    fetch("/home/api/get_study_time")
      .then((response) => response.json())
      .then((data) => {
        let workTime = data.study || 25; // 設定された作業時間を取得（デフォルトは60分）
        workTime = parseInt(workTime, 10); // 数値に変換

        startTime = new Date().getTime(); // 作業開始時間を記録
        targetTime = new Date().getTime() + workTime * 60000; // 選択された時間でカウントダウン開始
        isStudy = true;
        isPaused = false;

        interval = setInterval(updateCountDown, 1000); // 1000ミリ秒（1秒）ごとにupdateCountDownを行う
        updateCountDown();

        pauseButton.disabled = false;
        resumeButton.disabled = true;
        resetButton.disabled = false;
        modeSelect.disabled = true;
        categorySelect.disabled = true;
      })
      .catch((error) => {
        console.error("作業時間の取得に失敗！", error);
      });
  }

  // 休憩タイマーを起動する関数
  function startRestTimer() {
    if (interval) {
      clearInterval(interval);
    }

    fetch("/home/api/get_rest_time")
      .then((response) => response.json())
      .then((data) => {
        let restTime = data.rest || 5;
        restTime = parseInt(restTime, 10);

        startTime = new Date().getTime(); // 作業開始時間を記録
        targetTime = new Date().getTime() + restTime * 60000; // 選択された時間でカウントダウン開始
        isStudy = false;
        isPaused = false;

        interval = setInterval(updateCountDown, 1000); // 1000ミリ秒（1秒）ごとにupdateCountDownを行う
        updateCountDown();

        startButton.disabled = true;
        pauseButton.disabled = true;
        resumeButton.disabled = true;
        resetButton.disabled = true;
        modeSelect.disabled = true;
        categorySelect.disabled = true;
        stopRestButton.disabled = false;
      })
      .catch((error) => {
        console.error("休憩時間の取得に失敗！", error);
      });
  }

  // タイマーを一時停止する関数
  function pauseTimer() {
    if (!isPaused) {
      clearInterval(interval);
      remainingTime = targetTime - new Date().getTime(); // 現在の残り時間を保存
      isPaused = true;
      pauseButton.disabled = true;
      resumeButton.disabled = false;
    }
  }

  // タイマーを再開する関数
  function resumeTimer() {
    if (isPaused) {
      targetTime = new Date().getTime() + remainingTime; // 残り時間をもとに再開
      interval = setInterval(updateCountDown, 1000);
      updateCountDown();

      isPaused = false;
      pauseButton.disabled = false;
      resumeButton.disabled = true;
    }
  }

  // タイマーをリセットする関数
  function resetTimer() {
    clearInterval(interval);
    storeElapsedTime();

    fetch("/home/api/get_study_time/")
      .then((response) => response.json())
      .then((data) => {
        let workTime = data.study || 25;
        workTime = parseInt(workTime, 10);
        let hours = Math.floor(workTime / 60);
        let minutes = workTime % 60;
        countDown.textContent = `${String(hours).padStart(2, "0")}:${String(
          minutes
        ).padStart(2, "0")}:00`;

        remainingTime = 0;
        isPaused = false;

        pauseButton.disabled = true;
        resumeButton.disabled = true;
        resetButton.disabled = true;
        modeSelect.disabled = false;
        categorySelect.disabled = false;
      })
      .catch((error) => {
        console.error("ダメでした！", error);
      });
  }

  // 休憩タイマーをストップする関数
  function stopRestTimer() {
    clearInterval(interval);

    fetch("/home/api/get_study_time/")
      .then((response) => response.json())
      .then((data) => {
        let workTime = data.study || 25;
        workTime = parseInt(workTime, 10);
        let hours = Math.floor(workTime / 60);
        let minutes = workTime % 60;
        countDown.textContent = `${String(hours).padStart(2, "0")}:${String(
          minutes
        ).padStart(2, "0")}:00`;

        remainingTime = 0;
        isPaused = false;

        startButton.disabled = false;
        modeSelect.disabled = false;
        categorySelect.disabled = false;
        stopRestButton.disabled = true;
        isStudy = true;
        statusText.textContent = "作業中";
      })
      .catch((error) => {
        console.error("ダメでした！", error);
      });
  }

  // カウントした時間をグラフに反映させる関数
  function storeElapsedTime() {
    if (!startTime) return;

    const endTime = new Date().getTime();
    const elapsed = Math.floor((endTime - startTime) / 1000) / 60; // 分単位
    const mode = modeSelect.value;
    const categoryId = categorySelect.value; // カテゴリ選択のID（カテゴリ選択UIがある場合）

    fetch("/home/api/store_elapsed_time/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        mode: mode,
        elapsed: elapsed,
        category_id: categoryId, // 選択されたカテゴリ
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("記録が保存されました:", data);
        window.dispatchEvent(new Event("updateGraph")); // グラフを更新
      })
      .catch((error) => {
        console.error("時間の保存に失敗しました:", error);
      });
  }

  // 作業時間を取得する関数
  function getWorkTime() {
    fetch("/home/api/get_study_time/")
      .then((response) => response.json())
      .then((data) => {
        let workTime = data.study || 25;
        workTime = parseInt(workTime, 10);
        let hours = Math.floor(workTime / 60);
        let minutes = workTime % 60;
        countDown.textContent = `${String(hours).padStart(2, "0")}:${String(
          minutes
        ).padStart(2, "0")}:00`;
      })
      .catch((error) => {
        console.error("作業時間の取得に失敗してますよ！！", error);
      });
  }

  startButton.addEventListener("click", startTimer);
  pauseButton.addEventListener("click", pauseTimer);
  resumeButton.addEventListener("click", resumeTimer);
  resetButton.addEventListener("click", resetTimer);
  stopRestButton.addEventListener("click", stopRestTimer);
  getWorkTime();

  // window.addEventListener("load", function () {
  //   // 作業時間を取得
  //   fetch("/home/api/get_study_time/")
  //     .then((response) => response.json())
  //     .then((data) => {
  //       let workTime = data.study || 25;
  //       workTime = parseInt(workTime, 10);
  //       let hours = Math.floor(workTime / 60);
  //       let minutes = workTime % 60;
  //       countDown.textContent = `${String(hours).padStart(2, "0")}:${String(
  //         minutes
  //       ).padStart(2, "0")}:00`;
  //     })
  //     .catch((error) => {
  //       console.error("作業時間の取得に失敗してますよ！！", error);
  //     });
  // });
});
