/* ============================================================
   TRAFFICSENSE
   TRAFFIC PREDICTION + ORACLE ANALYTICS
============================================================ */


/* ============================================================
   GLOBAL CHART INSTANCES
   Used by the Model Comparison page
============================================================ */

let maeChartInstance = null;
let rmseChartInstance = null;
let r2ChartInstance = null;
let trainingTimeChartInstance = null;


/* ============================================================
   PREDICT TRAFFIC
============================================================ */

async function predictTraffic() {

    const dateInput =
        document.getElementById("dateInput");

    const timeInput =
        document.getElementById("timeInput");


    if (!dateInput || !timeInput) {
        return;
    }


    const date =
        dateInput.value;

    const time =
        timeInput.value;


    if (!date || !time) {

        alert(
            "Please select both date and time."
        );

        return;
    }


    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/predict?date=" +
                encodeURIComponent(date) +
                "&time=" +
                encodeURIComponent(time),
                {
                    method: "POST"
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            alert(
                result.detail ||
                "Prediction failed."
            );

            return;
        }


        updateResult(result);


    } catch (error) {

        console.error(
            "Prediction error:",
            error
        );


        alert(
            "Could not connect to the TrafficSense backend.\n\n" +
            "Make sure FastAPI is running on port 8000."
        );

    }

}


/* ============================================================
   UPDATE PREDICTION RESULT
============================================================ */

function updateResult(result) {

    const resultTitle =
        document.getElementById(
            "resultTitle"
        );


    const actualValue =
        document.getElementById(
            "actualValue"
        );


    const errorValue =
        document.getElementById(
            "errorValue"
        );


    const trafficBadge =
        document.querySelector(
            ".traffic-badge"
        );


    if (!result) {
        return;
    }


    const predicted =
        Number(
            result.predicted
        );


    const actual =
        Number(
            result.actual
        );


    const error =
        Number(
            result.error
        );


    const errorPercentage =
        Number(
            result.error_percentage
        );


    if (resultTitle) {

        resultTitle.innerHTML =

            predicted.toLocaleString(
                undefined,
                {
                    maximumFractionDigits: 0
                }
            )

            +

            ' <span>vehicles/hour</span>';

    }


    if (actualValue) {

        actualValue.innerText =

            actual.toLocaleString(
                undefined,
                {
                    maximumFractionDigits: 0
                }
            );

    }


    if (errorValue) {

        errorValue.innerText =

            error.toLocaleString(
                undefined,
                {
                    maximumFractionDigits: 0
                }
            )

            +

            " ↓ "

            +

            errorPercentage.toFixed(2)

            +

            "%";

    }


    if (trafficBadge) {

        trafficBadge.innerText =
            result.traffic_status ||
            "PREDICTED";

    }


    animateResultCard();


    /*
       Refresh prediction history so that the newly
       inserted Oracle record appears immediately.
    */

    if (
        typeof loadPredictionHistory ===
        "function"
    ) {

        loadPredictionHistory();

    }

}


/* ============================================================
   RESULT CARD ANIMATION
============================================================ */

function animateResultCard() {

    const card =
        document.getElementById(
            "resultCard"
        );


    if (!card) {
        return;
    }


    card.animate(

        [

            {
                transform:
                    "rotate(2deg) translateY(0)"
            },

            {
                transform:
                    "rotate(-1deg) translateY(-8px)"
            },

            {
                transform:
                    "rotate(2deg) translateY(0)"
            }

        ],

        {

            duration: 500,

            easing: "ease-out"

        }

    );

}


/* ============================================================
   MOUSE PARALLAX EFFECT
============================================================ */

document.addEventListener(
    "mousemove",
    function(event) {

        const visual =
            document.querySelector(
                ".visual-section"
            );


        if (!visual) {
            return;
        }


        const x =
            event.clientX /
            window.innerWidth -
            0.5;


        const y =
            event.clientY /
            window.innerHeight -
            0.5;


        const road =
            document.querySelector(
                ".road-art"
            );


        const resultCard =
            document.querySelector(
                ".result-card"
            );


        if (road) {

            road.style.transform =

                "perspective(900px) " +

                "rotateX(" +

                (12 + y * 3) +

                "deg) " +

                "rotateZ(" +

                (-5 + x * 2) +

                "deg)";

        }


        if (resultCard) {

            resultCard.style.marginLeft =
                (x * 8) + "px";


            resultCard.style.marginTop =
                (y * 6) + "px";

        }

    }
);


 /* ============================================================
    LOAD ORACLE ANALYTICS
 ============================================================ */

async function loadAnalytics() {

    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/analytics"
            );


        if (!response.ok) {

            throw new Error(
                "Analytics request failed."
            );

        }


        const data =
            await response.json();


        if (
            !data ||
            data.status !== "success"
        ) {

            throw new Error(
                "Invalid analytics response."
            );

        }


        /* =====================================================
           TRAFFIC STATISTICS
        ====================================================== */

        const averageTraffic =
            document.getElementById(
                "averageTraffic"
            );


        const minimumTraffic =
            document.getElementById(
                "minimumTraffic"
            );


        const maximumTraffic =
            document.getElementById(
                "maximumTraffic"
            );


        const busiestHour =
            document.getElementById(
                "busiestHour"
            );


        const busiestHourValue =
            document.getElementById(
                "busiestHourValue"
            );


        if (averageTraffic) {

            averageTraffic.innerText =
                Number(
                    data.traffic.average
                ).toLocaleString(
                    undefined,
                    {
                        maximumFractionDigits: 2
                    }
                );

        }


        if (minimumTraffic) {

            minimumTraffic.innerText =
                Number(
                    data.traffic.minimum
                ).toLocaleString();

        }


        if (maximumTraffic) {

            maximumTraffic.innerText =
                Number(
                    data.traffic.maximum
                ).toLocaleString();

        }


        if (busiestHour) {

            busiestHour.innerText =
                formatHour(
                    data.busiest_hour.hour
                );

        }


        if (busiestHourValue) {

            busiestHourValue.innerText =

                Number(
                    data.busiest_hour.average
                ).toLocaleString(
                    undefined,
                    {
                        maximumFractionDigits: 2
                    }
                )

                +

                " vehicles/hour";

        }



        /* =====================================================
           WEEKDAY / WEEKEND
        ====================================================== */

        const weekdayAverage =
            document.getElementById(
                "weekdayAverage"
            );


        const weekendAverage =
            document.getElementById(
                "weekendAverage"
            );


        if (weekdayAverage) {

            weekdayAverage.innerText =
                Number(
                    data.weekday_average
                ).toLocaleString(
                    undefined,
                    {
                        maximumFractionDigits: 2
                    }
                );

        }


        if (weekendAverage) {

            weekendAverage.innerText =
                Number(
                    data.weekend_average
                ).toLocaleString(
                    undefined,
                    {
                        maximumFractionDigits: 2
                    }
                );

        }


        updateAnalysisBars(
            data.weekday_average,
            data.weekend_average
        );



        /* =====================================================
           PEAK HOUR
        ====================================================== */

        const peakHourText =
            document.getElementById(
                "peakHourText"
            );


        const peakTrafficValue =
            document.getElementById(
                "peakTrafficValue"
            );


        if (peakHourText) {

            peakHourText.innerText =
                formatHour(
                    data.busiest_hour.hour
                );

        }


        if (peakTrafficValue) {

            peakTrafficValue.innerText =
                Number(
                    data.busiest_hour.average
                ).toLocaleString(
                    undefined,
                    {
                        maximumFractionDigits: 2
                    }
                );

        }



        /* =====================================================
           MODEL PERFORMANCE
        ====================================================== */

        if (
            Array.isArray(data.models)
        ) {

            updateModelCards(
                data.models
            );

            updateOracleModelTable(
                data.models
            );

        }


        /* =====================================================
           ORACLE STATISTICS
        ====================================================== */

        /*
           The current analytics API returns average,
           minimum and maximum traffic.

           These values are also displayed in the
           Oracle analytics section.
        */

        const oracleAverageTraffic =
            document.getElementById(
                "oracleAverageTraffic"
            );


        const oracleMinimumTraffic =
            document.getElementById(
                "oracleMinimumTraffic"
            );


        const oracleMaximumTraffic =
            document.getElementById(
                "oracleMaximumTraffic"
            );


        if (oracleAverageTraffic) {

            oracleAverageTraffic.innerText =
                Number(
                    data.traffic.average
                ).toLocaleString(
                    undefined,
                    {
                        maximumFractionDigits: 2
                    }
                );

        }


        if (oracleMinimumTraffic) {

            oracleMinimumTraffic.innerText =
                Number(
                    data.traffic.minimum
                ).toLocaleString();

        }


        if (oracleMaximumTraffic) {

            oracleMaximumTraffic.innerText =
                Number(
                    data.traffic.maximum
                ).toLocaleString();

        }



        console.log(
            "Oracle analytics loaded successfully."
        );


    } catch (error) {

        console.error(
            "Analytics error:",
            error
        );

    }

}


/* ============================================================
   FORMAT HOUR
============================================================ */

function formatHour(hour) {

    const numericHour =
        Number(hour);


    if (
        Number.isNaN(
            numericHour
        )
    ) {

        return "—";

    }


    const suffix =
        numericHour >= 12
            ? "PM"
            : "AM";


    let displayHour =
        numericHour % 12;


    if (displayHour === 0) {

        displayHour = 12;

    }


    return (
        displayHour +
        ":00 " +
        suffix
    );

}


/* ============================================================
   UPDATE WEEKDAY / WEEKEND BARS
============================================================ */

function updateAnalysisBars(
    weekday,
    weekend
) {

    const weekdayBar =
        document.getElementById(
            "weekdayBar"
        );


    const weekendBar =
        document.getElementById(
            "weekendBar"
        );


    const weekdayValue =
        Number(weekday);


    const weekendValue =
        Number(weekend);


    const maximum =
        Math.max(
            weekdayValue,
            weekendValue
        );


    if (
        !Number.isFinite(maximum) ||
        maximum <= 0
    ) {

        return;

    }


    if (weekdayBar) {

        weekdayBar.style.width =

            (
                weekdayValue /
                maximum *
                100
            ) +

            "%";

    }


    if (weekendBar) {

        weekendBar.style.width =

            (
                weekendValue /
                maximum *
                100
            ) +

            "%";

    }

}


/* ============================================================
   UPDATE MODEL CARDS
============================================================ */

function updateModelCards(models) {

    const lightgbm =
        models.find(
            model =>
                model.model
                    .toLowerCase()
                    .includes("lightgbm")
        );


    const xgboost =
        models.find(
            model =>
                model.model
                    .toLowerCase()
                    .includes("xgboost")
        );


    if (lightgbm) {

        setElementText(
            "lightgbmMae",
            formatNumber(
                lightgbm.test_mae
            )
        );


        setElementText(
            "lightgbmRmse",
            formatNumber(
                lightgbm.test_rmse
            )
        );


        setElementText(
            "lightgbmR2",
            formatR2(
                lightgbm.test_r2
            )
        );


        setElementText(
            "lightgbmTime",
            formatTrainingTime(
                lightgbm.training_time
            )
        );

    }


    if (xgboost) {

        setElementText(
            "xgboostMae",
            formatNumber(
                xgboost.test_mae
            )
        );


        setElementText(
            "xgboostRmse",
            formatNumber(
                xgboost.test_rmse
            )
        );


        setElementText(
            "xgboostR2",
            formatR2(
                xgboost.test_r2
            )
        );


        setElementText(
            "xgboostTime",
            formatTrainingTime(
                xgboost.training_time
            )
        );

    }

}


/* ============================================================
   UPDATE ORACLE MODEL TABLE
============================================================ */

function updateOracleModelTable(models) {

    const tableBody =
        document.getElementById(
            "oracleModelTableBody"
        );


    if (!tableBody) {
        return;
    }


    tableBody.innerHTML = "";


    models.forEach(
        function(model) {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML =

                "<td>" +

                escapeHtml(
                    model.model
                )

                +

                "</td>" +

                "<td>" +

                formatNumber(
                    model.test_mae
                )

                +

                "</td>" +

                "<td>" +

                formatNumber(
                    model.test_rmse
                )

                +

                "</td>" +

                "<td>" +

                formatR2(
                    model.test_r2
                )

                +

                "</td>" +

                "<td>" +

                formatTrainingTime(
                    model.training_time
                )

                +

                "</td>";


            tableBody.appendChild(
                row
            );

        }
    );

}


/* ============================================================
   HELPER: SET ELEMENT TEXT
============================================================ */

function setElementText(
    id,
    value
) {

    const element =
        document.getElementById(id);


    if (element) {

        element.innerText =
            value;

    }

}


/* ============================================================
   NUMBER FORMATTING
============================================================ */

function formatNumber(value) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return "—";

    }


    return number.toFixed(2);

}


/* ============================================================
   R² FORMATTING
============================================================ */

function formatR2(value) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return "—";

    }


    return number.toFixed(4);

}


/* ============================================================
   TRAINING TIME FORMATTING
============================================================ */

function formatTrainingTime(value) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return "—";

    }


    return number.toFixed(2) + " sec";

}


/* ============================================================
   HTML ESCAPE
============================================================ */

function escapeHtml(value) {

    if (value === null || value === undefined) {

        return "";

    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}



/* ============================================================
   MODEL COMPARISON
   ============================================================ */

async function loadModelComparison() {

    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/analytics"
            );


        if (!response.ok) {

            throw new Error(
                "Could not load model comparison data."
            );

        }


        const data =
            await response.json();


        if (
            !data ||
            data.status !== "success" ||
            !Array.isArray(data.models)
        ) {

            throw new Error(
                "Invalid model comparison data."
            );

        }


        const lightgbm =
            data.models.find(
                model =>
                    model.model
                        .toLowerCase()
                        .includes("lightgbm")
            );


        const xgboost =
            data.models.find(
                model =>
                    model.model
                        .toLowerCase()
                        .includes("xgboost")
            );


        if (!lightgbm || !xgboost) {

            throw new Error(
                "LightGBM or XGBoost data not found."
            );

        }


        /*
           Destroy previous charts before creating
           new ones. This prevents Chart.js from
           throwing a canvas reuse error.
        */

        destroyComparisonCharts();


        createMAEChart(
            lightgbm,
            xgboost
        );


        createRMSEChart(
            lightgbm,
            xgboost
        );


        createR2Chart(
            lightgbm,
            xgboost
        );


        createTrainingTimeChart(
            lightgbm,
            xgboost
        );


        console.log(
            "Model comparison loaded successfully."
        );


    } catch (error) {

        console.error(
            "Model comparison error:",
            error
        );

    }

}


/* ============================================================
   DESTROY EXISTING COMPARISON CHARTS
============================================================ */

function destroyComparisonCharts() {

    if (maeChartInstance) {

        maeChartInstance.destroy();

        maeChartInstance = null;

    }


    if (rmseChartInstance) {

        rmseChartInstance.destroy();

        rmseChartInstance = null;

    }


    if (r2ChartInstance) {

        r2ChartInstance.destroy();

        r2ChartInstance = null;

    }


    if (trainingTimeChartInstance) {

        trainingTimeChartInstance.destroy();

        trainingTimeChartInstance = null;

    }

}


/* ============================================================
   COMMON CHART OPTIONS
============================================================ */

function getComparisonChartOptions(
    decimalPlaces = 2
) {

    return {

        responsive: true,

        maintainAspectRatio: false,

        animation: {

            duration: 700

        },

        plugins: {

            legend: {

                display: false

            },

            tooltip: {

                callbacks: {

                    label: function(context) {

                        return (
                            context.dataset.label +
                            ": " +
                            Number(
                                context.raw
                            ).toFixed(
                                decimalPlaces
                            )
                        );

                    }

                }

            }

        },

        scales: {

            x: {

                grid: {

                    display: false

                },

                ticks: {

                    font: {

                        family:
                            "DM Sans",

                        size: 11

                    }

                }

            },


            y: {

                beginAtZero: true,

                grid: {

                    color:
                        "rgba(0,0,0,0.07)"

                },

                ticks: {

                    font: {

                        family:
                            "DM Sans",

                        size: 10

                    }

                }

            }

        }

    };

}


/* ============================================================
   TEST MAE CHART
============================================================ */

function createMAEChart(
    lightgbm,
    xgboost
) {

    const canvas =
        document.getElementById(
            "maeChart"
        );


    if (!canvas) {
        return;
    }


    const context =
        canvas.getContext("2d");


    maeChartInstance =
        new Chart(
            context,
            {

                type: "bar",

                data: {

                    labels: [
                        "LightGBM",
                        "XGBoost"
                    ],

                    datasets: [

                        {

                            label:
                                "Test MAE",

                            data: [

                                Number(
                                    lightgbm.test_mae
                                ),

                                Number(
                                    xgboost.test_mae
                                )

                            ],

                            backgroundColor: [

                                "#111111",
                                "#8d63ff"

                            ],

                            borderRadius: 4,

                            borderSkipped: false

                        }

                    ]

                },

                options:
                    getComparisonChartOptions(2)

            }
        );

}


/* ============================================================
   TEST RMSE CHART
============================================================ */

function createRMSEChart(
    lightgbm,
    xgboost
) {

    const canvas =
        document.getElementById(
            "rmseChart"
        );


    if (!canvas) {
        return;
    }


    const context =
        canvas.getContext("2d");


    rmseChartInstance =
        new Chart(
            context,
            {

                type: "bar",

                data: {

                    labels: [
                        "LightGBM",
                        "XGBoost"
                    ],

                    datasets: [

                        {

                            label:
                                "Test RMSE",

                            data: [

                                Number(
                                    lightgbm.test_rmse
                                ),

                                Number(
                                    xgboost.test_rmse
                                )

                            ],

                            backgroundColor: [

                                "#111111",
                                "#8d63ff"

                            ],

                            borderRadius: 4,

                            borderSkipped: false

                        }

                    ]

                },

                options:
                    getComparisonChartOptions(2)

            }
        );

}


/* ============================================================
   TEST R² CHART
============================================================ */

function createR2Chart(
    lightgbm,
    xgboost
) {

    const canvas =
        document.getElementById(
            "r2Chart"
        );


    if (!canvas) {
        return;
    }


    const context =
        canvas.getContext("2d");


    r2ChartInstance =
        new Chart(
            context,
            {

                type: "bar",

                data: {

                    labels: [
                        "LightGBM",
                        "XGBoost"
                    ],

                    datasets: [

                        {

                            label:
                                "Test R²",

                            data: [

                                Number(
                                    lightgbm.test_r2
                                ),

                                Number(
                                    xgboost.test_r2
                                )

                            ],

                            backgroundColor: [

                                "#111111",
                                "#8d63ff"

                            ],

                            borderRadius: 4,

                            borderSkipped: false

                        }

                    ]

                },

                options:
                    getComparisonChartOptions(4)

            }
        );

}


/* ============================================================
   TRAINING TIME CHART
============================================================ */

function createTrainingTimeChart(
    lightgbm,
    xgboost
) {

    const canvas =
        document.getElementById(
            "trainingTimeChart"
        );


    if (!canvas) {
        return;
    }


    const context =
        canvas.getContext("2d");


    trainingTimeChartInstance =
        new Chart(
            context,
            {

                type: "bar",

                data: {

                    labels: [
                        "LightGBM",
                        "XGBoost"
                    ],

                    datasets: [

                        {

                            label:
                                "Training Time",

                            data: [

                                Number(
                                    lightgbm.training_time
                                ),

                                Number(
                                    xgboost.training_time
                                )

                            ],

                            backgroundColor: [

                                "#111111",
                                "#8d63ff"

                            ],

                            borderRadius: 4,

                            borderSkipped: false

                        }

                    ]

                },

                options:
                    getComparisonChartOptions(2)

            }
        );

}



/* ============================================================
   SHOW DASHBOARD
============================================================ */

function showDashboard() {

    const heroSection =
        document.querySelector(
            ".hero-section"
        );

    const featureStrip =
        document.querySelector(
            ".feature-strip"
        );

    const analyticsSection =
        document.querySelector(
            ".analytics-section"
        );

    const oracleAnalytics =
        document.querySelector(
            ".oracle-analytics-section"
        );

    const historyPage =
        document.getElementById(
            "historyPage"
        );

    const comparisonPage =
        document.getElementById(
            "comparisonPage"
        );


    /* Show Dashboard content */

    if (heroSection) {

        heroSection.style.display =
            "grid";

    }


    if (featureStrip) {

        featureStrip.style.display =
            "grid";

    }


    if (analyticsSection) {

        analyticsSection.style.display =
            "block";

    }


    if (oracleAnalytics) {

        oracleAnalytics.style.display =
            "block";

    }


    /* Hide other pages */

    if (historyPage) {

        historyPage.style.display =
            "none";

    }


    if (comparisonPage) {

        comparisonPage.style.display =
            "none";

    }


    updateNavigation(
        "dashboard"
    );


    loadAnalytics();

}


/* ============================================================
   SHOW PREDICTION HISTORY
============================================================ */

function showHistory() {

    const heroSection =
        document.querySelector(
            ".hero-section"
        );

    const featureStrip =
        document.querySelector(
            ".feature-strip"
        );

    const analyticsSection =
        document.querySelector(
            ".analytics-section"
        );

    const oracleAnalytics =
        document.querySelector(
            ".oracle-analytics-section"
        );

    const historyPage =
        document.getElementById(
            "historyPage"
        );

    const comparisonPage =
        document.getElementById(
            "comparisonPage"
        );


    /* Hide Dashboard content */

    if (heroSection) {

        heroSection.style.display =
            "none";

    }


    if (featureStrip) {

        featureStrip.style.display =
            "none";

    }


    if (analyticsSection) {

        analyticsSection.style.display =
            "none";

    }


    if (oracleAnalytics) {

        oracleAnalytics.style.display =
            "none";

    }


    /* Show History */

    if (historyPage) {

        historyPage.style.display =
            "block";

    }


    /* Hide Comparison */

    if (comparisonPage) {

        comparisonPage.style.display =
            "none";

    }


    updateNavigation(
        "history"
    );


    loadPredictionHistory();

}


/* ============================================================
   SHOW MODEL COMPARISON
============================================================ */

function showComparison() {

    const heroSection =
        document.querySelector(
            ".hero-section"
        );

    const featureStrip =
        document.querySelector(
            ".feature-strip"
        );

    const analyticsSection =
        document.querySelector(
            ".analytics-section"
        );

    const oracleAnalytics =
        document.querySelector(
            ".oracle-analytics-section"
        );

    const historyPage =
        document.getElementById(
            "historyPage"
        );

    const comparisonPage =
        document.getElementById(
            "comparisonPage"
        );


    /* Hide Dashboard content */

    if (heroSection) {

        heroSection.style.display =
            "none";

    }


    if (featureStrip) {

        featureStrip.style.display =
            "none";

    }


    if (analyticsSection) {

        analyticsSection.style.display =
            "none";

    }


    if (oracleAnalytics) {

        oracleAnalytics.style.display =
            "none";

    }


    /* Hide History */

    if (historyPage) {

        historyPage.style.display =
            "none";

    }


    /* Show Model Comparison */

    if (comparisonPage) {

        comparisonPage.style.display =
            "block";

    }


    updateNavigation(
        "comparison"
    );


    loadModelComparison();

}


/* ============================================================
   UPDATE NAVIGATION ACTIVE STATE
============================================================ */

function updateNavigation(page) {

    const buttons =
        document.querySelectorAll(
            ".nav-button"
        );


    buttons.forEach(
        function(button) {

            button.classList.remove(
                "active"
            );

        }
    );


    let activeButton = null;


    if (page === "dashboard") {

        activeButton =
            document.querySelector(
                '.nav-button[onclick="showDashboard()"]'
            );

    }


    else if (page === "history") {

        activeButton =
            document.querySelector(
                '.nav-button[onclick="showHistory()"]'
            );

    }


    else if (page === "comparison") {

        activeButton =
            document.querySelector(
                '.nav-button[onclick="showComparison()"]'
            );

    }


    if (activeButton) {

        activeButton.classList.add(
            "active"
        );

    }

}


/* ============================================================
   REFRESH PREDICTION HISTORY
============================================================ */

async function refreshPredictionHistory() {

    const button =
        document.getElementById("historyRefreshButton");

    const buttonText =
        document.getElementById("refreshButtonText");

    if (button && button.disabled) {
        return;
    }

    if (button) {
        button.disabled = true;
    }

    if (buttonText) {
        buttonText.innerText = "REFRESHING...";
    }

    try {
        await loadPredictionHistory();
    } finally {
        if (button) {
            button.disabled = false;
        }

        if (buttonText) {
            buttonText.innerText = "REFRESH HISTORY";
        }
    }
}


/* ============================================================
   LOAD PREDICTION HISTORY
============================================================ */

async function loadPredictionHistory() {

    const tableBody =
        document.getElementById("historyTableBody");

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML =
        '<div class="history-loading">Loading prediction history...</div>';

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/prediction-history",
            { cache: "no-store" }
        );

        if (!response.ok) {
            throw new Error(
                "History API returned HTTP " + response.status
            );
        }

        const data = await response.json();

        if (
            data.status !== "success" ||
            !Array.isArray(data.predictions)
        ) {
            throw new Error(
                "Unexpected prediction-history response."
            );
        }

        const predictions = data.predictions;

        tableBody.innerHTML = "";

        if (predictions.length === 0) {

            updateHistorySummary([]);

            tableBody.innerHTML =
                '<div class="history-empty">No predictions found in Oracle Database.</div>';

            return;
        }

        // Newest records first.
        predictions.sort(function(a, b) {
            return new Date(b.date_time) - new Date(a.date_time);
        });

        updateHistorySummary(predictions);

        predictions.forEach(function(prediction) {

            // Support both API naming conventions.
            const actual = Number(
                prediction.actual ??
                prediction.actual_traffic_volume
            );

            const predicted = Number(
                prediction.predicted ??
                prediction.predicted_traffic_volume
            );

            const error = Number.isFinite(actual) &&
                          Number.isFinite(predicted)
                ? Math.abs(actual - predicted)
                : Number(prediction.error);

            const row = document.createElement("div");

            row.className = "history-table-row";

            const dateTime = formatHistoryDate(
                prediction.date_time
            );

            const status =
                prediction.traffic_status ||
                (
                    Number.isFinite(predicted)
                        ? getTrafficStatus(predicted)
                        : "UNKNOWN"
                );

            row.innerHTML = `
                <span>${escapeHtml(dateTime)}</span>
                <span>${formatWholeNumber(actual)}</span>
                <span>${formatWholeNumber(predicted)}</span>
                <span>${formatWholeNumber(error)}</span>
                <span class="history-status">${escapeHtml(status)}</span>
            `;

            tableBody.appendChild(row);
        });

        console.log(
            "Prediction history refreshed:",
            predictions.length,
            "records"
        );

    } catch (error) {

        console.error("Prediction history error:", error);

        tableBody.innerHTML =
            '<div class="history-error">' +
            'Unable to load history. Check the backend and Oracle connection, then try Refresh History again.' +
            '</div>';

    }
}


/* ============================================================
   UPDATE HISTORY SUMMARY
============================================================ */

function updateHistorySummary(predictions) {

    const totalElement =
        document.getElementById("historyTotal");

    const averageErrorElement =
        document.getElementById("historyAverageError");

    const lastPredictionElement =
        document.getElementById("historyLastPrediction");

    const total = predictions.length;

    let totalError = 0;
    let validErrorCount = 0;

    predictions.forEach(function(prediction) {

        const actual = Number(
            prediction.actual ??
            prediction.actual_traffic_volume
        );

        const predicted = Number(
            prediction.predicted ??
            prediction.predicted_traffic_volume
        );

        let error;

        if (
            Number.isFinite(actual) &&
            Number.isFinite(predicted)
        ) {
            error = Math.abs(actual - predicted);
        } else {
            error = Number(prediction.error);
        }

        if (Number.isFinite(error)) {
            totalError += error;
            validErrorCount++;
        }
    });

    const averageError = validErrorCount > 0
        ? totalError / validErrorCount
        : null;

    if (totalElement) {
        totalElement.innerText = total.toLocaleString();
    }

    if (averageErrorElement) {
        averageErrorElement.innerText =
            averageError === null
                ? "—"
                : averageError.toFixed(2);
    }

    if (lastPredictionElement) {
        lastPredictionElement.innerText =
            total > 0
                ? formatHistoryDate(predictions[0].date_time)
                : "—";
    }
}


/* ============================================================
   FORMAT HISTORY DATE
============================================================ */

function formatHistoryDate(
    value
) {

    if (!value) {

        return "—";

    }


    const date =
        new Date(value);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return String(value);

    }


    return (

        date.toLocaleDateString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        )

        +

        " · " +

        date.toLocaleTimeString(
            "en-IN",
            {
                hour: "2-digit",
                minute: "2-digit",
                hour12: true
            }
        )

    );

}


/* ============================================================
   FORMAT WHOLE NUMBER
============================================================ */

function formatWholeNumber(
    value
) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return "—";

    }


    return number.toLocaleString(
        undefined,
        {
            maximumFractionDigits: 0
        }
    );

}


/* ============================================================
   TRAFFIC STATUS
============================================================ */

function getTrafficStatus(
    traffic
) {

    const value =
        Number(traffic);


    if (
        !Number.isFinite(value)
    ) {

        return "UNKNOWN";

    }


    if (value >= 5000) {

        return "HIGH";

    }


    if (value >= 3000) {

        return "MODERATE";

    }


    return "LOW";

}


/* ============================================================
   INITIAL PAGE LOAD
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        /*
           Dashboard is the default page.
        */

        showDashboard();


        /*
           Load analytics from Oracle immediately.
        */

        loadAnalytics();

    }
);