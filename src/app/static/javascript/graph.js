document.addEventListener("DOMContentLoaded", function () {
  const ctx = document.getElementById("chart-week"); // IDが "chart-week" のキャンバス要素を取得
  ctx.style.height = "250px"; // キャンバスの高さを明示的に設定
  ctx.style.width = "300px"; // キャンバスの高さを明示的に設定

  let chartInstance = null;

  function updateChart() {
    fetch(`/home/api/update_chart/`)
      .then((response) => response.json())
      .then((data) => {
        // Chart.js を使って棒グラフを作成
        if (chartInstance) {
          chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
          type: "bar", // グラフの種類を棒グラフに設定
          data: {
            labels: ["インプット", "アウトプット"], // X軸のラベル
            datasets: [
              {
                data: [data.input, data.output],
                backgroundColor: [
                  "rgba(175, 223, 248, 1)",
                  "rgba(12, 45, 142, 1)",
                ],
              },
            ],
          },
          options: {
            scales: {
              x: { grid: { display: false } }, // X軸のグリッド線を非表示
              y: { grid: { display: false }, beginAtZero: true }, // Y軸のグリッド線を非表示、かつ0から開始
            },
            maxBarThickness: 50, // 棒グラフの最大太さを指定
            plugins: {
              legend: { display: false }, // 凡例（ラベル）を非表示
              title: {
                display: true, // グラフのタイトルを表示
                text: `合計：${(data.input + data.output).toFixed(1)} 分`, // タイトルとして合計時間を表示
              },
            },
          },
        });

        return chartInstance;
      })
      .catch((error) => console.error("graphの取得に失敗しました:", error));
  }

  updateChart(); // 初回グラフの描画

  window.addEventListener("updateGraph", function () {
    updateChart();
  });
});
