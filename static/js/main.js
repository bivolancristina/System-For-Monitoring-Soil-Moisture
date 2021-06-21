///////////////////////// Automated Watering /////////////////////////
const autoSwitch = document.getElementById("autoSwitch");
const manualSwitch = document.getElementById("manualSwitch");

function getStatus() {
  jQuery.ajax({
    url: "/api/status",
    type: "POST",
    success: function (ndata) {
      status = ndata[Object.keys(ndata)[Object.keys(ndata).length - 1]].Status;
      console.log(status);
      if (status == "A") {
        autoSwitch.checked = true;
        manualSwitch.disabled = true;
        manualSwitch.checked = false;
      } else if (status == "M" || status == "F") {
        autoSwitch.checked = false;
        manualSwitch.checked = false;
      } else if (status == "O") {
        autoSwitch.checked = false;
        manualSwitch.checked = true;
      } else {
        autoSwitch.checked = true;
        manualSwitch.disabled = true;
        manualSwitch.checked = false;
      }
    }
  })
}

function auto() {
  let autoStatus;
  if (autoSwitch.checked) {
    autoStatus = "A";
    manualSwitch.disabled = true;
    manualSwitch.checked = false;
  } else {
    autoStatus = "M";
    manualSwitch.disabled = false;
  }
  // console.log(autoStatus);

  $.ajax({
    url: "changeStatus/" + autoStatus
  })

}

function manual() {
  let manualStatus;
  if (manualSwitch.checked) {
    manualStatus = "O";
  } else {
    manualStatus = "F";
  }
  // console.log(manualStatus);
  $.ajax({
    url: "changeStatus/" + manualStatus
  })
}

///////////////////////// Get readings /////////////////////////
function getData() {
  jQuery.ajax({
    url: "/api/getData",
    type: "POST",
    success: function (ndata) {
      console.log(ndata);
      tempAirValue = ndata[Object.keys(ndata)[Object.keys(ndata).length - 1]].temperatureAir;
      tempWaterValue = ndata[Object.keys(ndata)[Object.keys(ndata).length - 1]].temperatureWater;
      humValue = ndata[Object.keys(ndata)[Object.keys(ndata).length - 1]].humidity;
      soilValue = ndata[Object.keys(ndata)[Object.keys(ndata).length - 1]].moisture;
      usedWaterValue = ndata[Object.keys(ndata)[Object.keys(ndata).length - 1]].usedWater;
      console.log(soilValue);
      $('#tempAirValue').html(tempAirValue);
      $('#tempWaterValue').html(tempWaterValue);
      $('#humValue').html(humValue);
      $('#soilValue').html(soilValue);
      $('#usedWaterValue').html(usedWaterValue);
    }
  })
}

/////////////////////// Get Chart data ///////////////////////
function getChartData() {
  jQuery.ajax({
    url: "/api/getChartData",
    type: "POST",
    success: function (ndata) {
      console.log(ndata)
      const chartData = ndata;
      console.log("Getting Chart data")

      let tempAirArr = [];
      let tempWaterArr = [];
      let humArr = [];
      let soilArr = [];
      let usedWaterArr = [];
      let timeArr = [];
      Object.keys(chartData).forEach((e) => {
        tempAirArr.push(chartData[e].temperatureAir);
        tempWaterArr.push(chartData[e].temperatureWater);
        humArr.push(chartData[e].humidity);
        soilArr.push(chartData[e].moisture);
        usedWaterArr.push(chartData[e].usedWater);

        let datetime = chartData[e].DateTime;
        console.log(datetime);
        jsdatetime = new Date(Date.parse(datetime));
        jstime = jsdatetime.toLocaleTimeString();
        timeArr.push(jstime);
      })

      createGraph(tempAirArr, timeArr, '#tempAirChart');
      createGraph(tempWaterArr, timeArr, '#tempWaterChart');
      createGraph(humArr, timeArr, '#humChart');
      createGraph(soilArr, timeArr, '#soilChart');
      createGraph(usedWaterArr, timeArr, '#usedWaterChart');

    }
  })
}

// Charts
function createGraph(data, newTime, newChart) {

  let chartData = {
    labels: newTime,
    series: [data]
  };
  // console.log(chartData);

  let options = {
    axisY: {
      onlyInteger: true
    },
    fullWidth: true,

    width: '100%',
    height: '100%',
    lineSmooth: true,
    chartPadding: {
      right: 50
    }
  };

  new Chartist.Line(newChart, chartData, options);

}

/////////////////////// run functions ///////////////////////
$(document).ready(function () {
  getData();
  getStatus();
  getChartData();

  setTimeout(function run() {
    getData();
    getChartData();
    setTimeout(run,300000);
  }, 300000);
  setTimeout(function run() {
    getStatus();
    setTimeout(run,1000);
  }, 1000);
})