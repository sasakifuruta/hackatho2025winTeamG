// ==========
// グラフ画面
// =========
document.addEventListener("DOMContentLoaded", function () {
    // 週間データ（初期表示）
    let isInitialData = true;  // 初期データ表示中は true
    const weekData = JSON.parse(document.getElementById('week_data').textContent);
    const weekChartRatio = JSON.parse(document.getElementById('week_chart_ratio').textContent);
    const weekLabel = JSON.parse(document.getElementById('week_labels').textContent);

    const graphTitle = document.getElementById('graph_title');
    const prevBtn = document.getElementById('prev_period');
    const nextBtn = document.getElementById('next_period');
    let currentIdx = 0; // < >を押すと増減する
    if (currentIdx == 0){
        prevBtn.style.visibility = "hidden";
    }
    graphTitle.textContent = weekData[currentIdx].period;
    function updateWeekChart() {
        // 画面アクセス時に表示する週間グラフ　<>を押したときに変更
        graphTitle.textContent = weekData[currentIdx].period;
        chart.data.datasets[0].data = weekData[currentIdx].input_data;
        chart.data.datasets[1].data = weekData[currentIdx].output_data;
        const total = weekData[currentIdx].total;
        chart.options.plugins.title.text = '合計：' + total + '時間';
        chart.update();

        // 比率グラフ
        chartRatio.data.datasets[0].data = [weekChartRatio[currentIdx].input_ratio];
        chartRatio.data.datasets[1].data = [weekChartRatio[currentIdx].output_ratio];
        chartRatio.update();

        // <>ボタンの表示
        if (currentIdx == 0 && currentIdx == weekData.length - 1) {
                prevBtn.style.visibility = "hidden";
                nextBtn.style.visibility = "hidden";
            }
            else if (currentIdx == 0) {
                prevBtn.style.visibility = "hidden";
                nextBtn.style.visibility = "visible";
            } else if (currentIdx == weekData.length - 1) {
                prevBtn.style.visibility = "visible";
                nextBtn.style.visibility = "hidden";
            } else {
                prevBtn.style.visibility = "visible";
                nextBtn.style.visibility = "visible";
            }
    }


    const ct1 = document.getElementById("chart");
    const chart = new Chart(ct1, {
        type: 'bar',
        data: {
            labels: weekLabel,
            datasets: [
                {
                    label: 'インプット',
                    data: weekData[currentIdx].input_data,
                    backgroundColor: "rgba(175, 223, 248, 1)"
                }, {
                    label: 'アウトプット',
                    data: weekData[currentIdx].output_data,
                    backgroundColor: "rgba(12, 45, 142, 1)"
                }
            ]
        },
        options: {
            maxBarThickness: 50,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: '合計：' + weekData[currentIdx].total + '時間',
                    font:{
                        size: 18,
                        weight: "bold"
                    },
                    color:"#000"
                },
            },
            scales:{
                x:{
                    ticks:{
                        font:{
                            size:14,
                            weight:"bold"
                        },
                        color:"#000",
                    }
                },
                y:{
                    title:{
                        display: true,
                        text: "学習時間（分）",
                        font:{
                            size: 14,
                            weight: "bold"
                        },
                        color: "#000",
                        padding:{
                            bottom:10
                        }
                    },
                    ticks:{
                        font:{
                            size:14,
                            weight:"bold"
                        },
                        color:"#000"
                    }
                }
            },
            layout:{
                padding:{
                    top: 20,
                    bottom: 20,
                    left: 10,
                    right: 10
                }
            }
            
        }
    });

    const ctx = document.getElementById("chart_ratio");
    const chartRatio = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['インプット', 'アウトプット'],
            datasets: [
                {
                    label: 'インプット',
                    data: [weekChartRatio[currentIdx].input_ratio],
                    backgroundColor: "rgba(175, 223, 248, 1)",
                    borderColor: "#fff",
                    borderWidth: 5,
                    datalabels: {
                        color: '#000',
                    }
                },
                {
                    label: 'アウトプット',
                    data: [weekChartRatio[currentIdx].output_ratio],
                    backgroundColor: "rgba(12, 45, 142, 1)",
                    borderColor: "#fff",
                    borderWidth: 5,
                }
            ]
        },
        options: {
            indexAxis: 'y',
            barThickness: 70,
            scales: {
                x: {
                    stacked: true,
                    display: false
                },
                y: {
                    stacked: true,
                    display: false
                }
            },
            plugins: {
                tooltip: {
                    enabled: false
                },
                legend: {
                    display: false
                },
                datalabels: {
                    font: {
                        size: 16,
                        weight: "bold"
                    },
                    color: "#fff",
                    formatter: function (value, context) {
                        const datasetLabel = context.chart.data.datasets[context.datasetIndex].label;
                        return datasetLabel + ' ' + value + '%';
                    }
                }
            },
        },
        plugins: [ChartDataLabels],
    });

    // ボタンを押したらAPIを取得しグラフを切り替え
    let chartData = [];
    let ratioData = [];
    function fetchData(period) {
        fetch(`/summary/${period}`)
            .then(response => response.json())
            .then(chart_data => {
                if (typeof chart_data.chart === "string") {
                    chart_data.chart = JSON.parse(chart_data.chart);
                    chart_data.chart_ratio = JSON.parse(chart_data.chart_ratio);
                }
                chartData = chart_data.chart;
                ratioData = chart_data.chart_ratio
                isInitialData = false;
                updateChart(period);
                console.log(ratioData);
            })
            .catch(error => console.error("データ取得エラー: ", error)
            )
    }

    function updateChart(period) {
        if (chartData.length > 0 && currentIdx >= 0 && currentIdx < chartData.length) {
            // console.log("currentIdx:", currentIdx);
            // console.log("chartData:", chartData);
            // console.log("ratioData:", ratioData);
            if (period == 'week') {
                chart.data.labels = ['月', '火', '水', '木', '金', '土', '日']
            } else if (period == 'month') {
                chart.data.labels = Array.from({ length: chartData[currentIdx].input_data.length }, (_, k) => `${k + 1}週目`) //[1週目, 2週目, 3週目, 4週目]
            } else if (period == 'year') {
                chart.data.labels = Array.from({ length: chartData[currentIdx].input_data.length }, (_, k) => `${k + 1}月`)
            }
            graphTitle.textContent = chartData[currentIdx].period;
            chart.data.datasets[0].data = chartData[currentIdx].input_data;
            chart.data.datasets[1].data = chartData[currentIdx].output_data;
            const total = chartData[currentIdx].total;
            chart.options.plugins.title.text = '合計：' + total + '時間';
            chart.update();

            chartRatio.data.datasets[0].data = [ratioData[currentIdx].input_ratio];
            chartRatio.data.datasets[1].data = [ratioData[currentIdx].output_ratio];
            chartRatio.update();

            if (currentIdx == 0 && currentIdx == chartData.length - 1) {
                prevBtn.style.visibility = "hidden";
                nextBtn.style.visibility = "hidden";
            }
            else if (currentIdx == 0) {
                prevBtn.style.visibility = "hidden";
                nextBtn.style.visibility = "visible";
            } else if (currentIdx == chartData.length - 1) {
                prevBtn.style.visibility = "visible";
                nextBtn.style.visibility = "hidden";
            } else {
                prevBtn.style.visibility = "visible";
                nextBtn.style.visibility = "visible";
            }
        }
    }


    BtnWeek = document.getElementById("btn-week");
    BtnWeek.addEventListener("click", () => {
        currentIdx = 0;
        fetchData("week")
    });

    BtnMonth = document.getElementById("btn-month");
    BtnMonth.addEventListener("click", () => {
        currentIdx = 0;
        fetchData("month")
    });

    BtnYear = document.getElementById("btn-year");
    BtnYear.addEventListener("click", () => {
        currentIdx = 0;
        fetchData("year")
    });

    // 矢印ボタンクリック時の処理
    prevBtn.addEventListener('click', (period) => {
        if (currentIdx > 0) {
            currentIdx--;
            if (isInitialData) {
                updateWeekChart();
            } else {
                updateChart(period);
            }
        }
    });
    nextBtn.addEventListener('click', (period) => {
        if (currentIdx < weekData.length - 1) {
            if (isInitialData) {
                currentIdx++;
                updateWeekChart();
            }
        }
        if (currentIdx < chartData.length - 1) {
            if (!isInitialData) {
                currentIdx++;
                updateChart(period);
            }
        }
    });

});
