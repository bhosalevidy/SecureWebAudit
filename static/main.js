let chart;
let totalSteps = 7; // total Selenium steps including forced failures

async function startScan() {
  let url = document.getElementById("urlInput").value;

  // Reset progress bar
  updateProgress(0);

  await fetch("/run-tests", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  });

  pollResults();
}

function pollResults() {
  const interval = setInterval(async () => {
    let res = await fetch("/results");
    let data = await res.json();

    if (data && data.details) {
      let completedSteps = data.details.tests.length;
      updateProgress((completedSteps / totalSteps) * 100);

      updateChart(data.summary);
      updateTestSteps(data.details.tests);

      if (completedSteps >= totalSteps) {
        clearInterval(interval);
        updateProgress(100); // Ensure full bar at end
      }
    }
  }, 1000);
}

function updateProgress(percent) {
  const bar = document.getElementById("progressBar");
  bar.style.width = percent + "%";
  bar.textContent = Math.round(percent) + "%";
}

function updateChart(summary) {
  const ctx = document.getElementById("functionalChart").getContext("2d");

  if (!chart) {
    chart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Passed", "Failed"],
        datasets: [{
          data: [summary.passed, summary.failed],
          backgroundColor: ["green", "red"]
        }]
      },
      options: { responsive: true, plugins: { legend: { position: "bottom" } } }
    });
  } else {
    chart.data.datasets[0].data = [summary.passed, summary.failed];
    chart.update();
  }
}
function updateTestSteps(tests) {
  const container = document.getElementById("testSteps");
  container.innerHTML = ""; // Clear before re-render

  for (let i = 0; i < tests.length; i++) {
    let step = document.createElement("div");
    step.className = (tests[i].status.toLowerCase() === "passed") ? "test-step passed" : "test-step failed";
    step.textContent = tests[i].name + (tests[i].error ? " → " + tests[i].error : " → " + tests[i].status.toUpperCase());
    container.appendChild(step);
  }
}