document.addEventListener("DOMContentLoaded", function () {
  const countDown = document.getElementById("countdown");
  const startButton = document.getElementById("start-timer");
  const pauseButton = document.getElementById("pause-timer");
  const resumeButton = document.getElementById("resume-timer");
  const resetButton = document.getElementById("reset-timer");
  const modeSelect = document.getElementById("mode-select");

  let interval; // タイマーのID
  let targetTime; // カウントダウンの終了時間
  let startTime; // カウントダウンの開始時間
  let remainingTime = 0; // 一時停止時の残り時間
  let isPaused = false; // 一時停止状態かどうか

  // 残り時間を表示する関数
  function updateCountDown() {
    const now = new Date().getTime(); // 現在の時刻を取得（ミリ秒単位）
    const distance = targetTime - now;

    if (distance <= 0) {
      clearInterval(interval); // タイマーを停止
      countDown.textContent = "終了しました";
      storeElapsedTime();
      modeSelect.disabled = false;
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

    let workTime = localStorage.getItem("workTime") || 60; // 設定された作業時間を取得（デフォルトは60分）
    workTime = parseInt(workTime, 10); // 数値に変換

    startTime = new Date().getTime(); // 作業開始時間を記録
    targetTime = new Date().getTime() + workTime * 60000; // 選択された時間でカウントダウン開始
    interval = setInterval(updateCountDown, 1000); // 1000ミリ秒（1秒）ごとにupdateCountDownを行う
    updateCountDown();

    isPaused = false;
    pauseButton.disabled = false;
    resumeButton.disabled = true;
    resetButton.disabled = false;
    modeSelect.disabled = true;
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

    let workTime = localStorage.getItem("workTime") || 60;
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
  }

  // カウントした時間をグラフに反映させる関数
  function storeElapsedTime() {
    if (!startTime) return;

    const endTime = new Date().getTime();
    const elapsed = Math.floor((endTime - startTime) / 1000) / 60; // 分単位
    const mode = modeSelect.value;

    let data = JSON.parse(localStorage.getItem("timerData")) || {
      input: 0,
      output: 0,
    }; // ローカルストレージに保存されたtimerDataを取得し、JSON.parse() で JavaScript オブジェクトに変換
    data[mode] += elapsed; // カウントした時間をmode（"input" または "output"）ごとに累積させる
    localStorage.setItem("timerData", JSON.stringify(data)); //更新されたデータを JSON.stringify() で文字列に変換し、再び localStorage に保存

    window.dispatchEvent(new Event("updateGraph")); // new Event(eventtype)によって、カスタムイベントである"updateGraph"を定義し、window.dispatchEventメソッドによって、カスタムイベントを発火させ、graph.jsにあるwindow.addEventListenerを動かす
  }

  startButton.addEventListener("click", startTimer);
  pauseButton.addEventListener("click", pauseTimer);
  resumeButton.addEventListener("click", resumeTimer);
  resetButton.addEventListener("click", resetTimer);

  window.addEventListener("load", function () {
    let workTime = localStorage.getItem("workTime") || 60;
    workTime = parseInt(workTime, 10);
    let hours = Math.floor(workTime / 60);
    let minutes = workTime % 60;
    countDown.textContent = `${String(hours).padStart(2, "0")}:${String(
      minutes
    ).padStart(2, "0")}:00`;
  });
});
