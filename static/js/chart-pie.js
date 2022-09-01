function initPieChart(chart_id, data) {

    // Set new default font family and font color to mimic Bootstrap's default styling
    Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
    Chart.defaults.global.defaultFontColor = '#292b2c';
    // Pie Chart Example
    var ctx = document.getElementById(chart_id);
    var myPieChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ["Completed", "Accepted", "Pending"],
        datasets: [{
          data: [data.completed, data.accepted, data.pending],
          backgroundColor: ['green', 'orange', 'yellow'],
        }],
      },
    });
}
