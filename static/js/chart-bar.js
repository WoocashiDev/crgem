// init the function initBarChart within html file providign chart id as string and labels as lists from the database


function initBarChart(chart_id, data, color) {

const users = data.map(element => element.user_name);
const tasks = data.map(element => element.task_count)
let highest_number = Math.max(...tasks)
console.log(highest_number)


console.log(users)
console.log(tasks)
// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Bar Chart Example
var ctx = document.getElementById(chart_id);
var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: users,
    datasets: [{
      label: "Task count",
      backgroundColor: color,
      borderColor: color,
      data: tasks,
    }],
  },
  options: {
    scales: {
      xAxes: [{
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 20,
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: highest_number,
          maxTicksLimit: 5,
        },
        gridLines: {
          display: true
        }
      }],
    },
    legend: {
      display: false
    }
  }
});
}