/*Theslert( "Load was performed." );
  });e lines are all chart setup.  Pick and choose which chart features you want to utilize. */

function reloadGraph(){
 $.get( "http://localhost:3784/instrumentation/getCounters?c=metrics5", function( data ) {
    //$( ".result" ).html( data );
//    alert( "Load was performed." );
 
nv.addGraph(function() {
  var chart = nv.models.lineChart()
                .margin({left: 100})  //Adjust chart margins to give the x-axis some breathing room.
                .useInteractiveGuideline(true)  //We want nice looking tooltips and a guideline!
                .transitionDuration(350)  //how fast do you want the lines to transition?
                .showLegend(true)       //Show the legend, allowing users to turn on/off line series.
                .showYAxis(true)        //Show the y-axis
                .showXAxis(true)        //Show the x-axis
                .forceX([0,720])  
;


  chart.xAxis     //Chart x-axis settings
      .axisLabel('Time (ms)')
      .tickFormat(d3.format(',r'));

  chart.yAxis     //Chart y-axis settings
      .axisLabel('Average Response Time')
      .tickFormat(d3.format('.02f'));

//  var myData = sinAndCos();   //You need data...

  d3.select('#chart svg')    //Select the <svg> element you want to render the chart in.   
      .datum(data)         //Populate the <svg> element with chart data...
      .call(chart);          //Finally, render the chart!

  //Update the chart when window resizes.
  nv.utils.windowResize(function() { chart.update() });
  return chart;
});
});
}

function updatePage() {
  reloadGraph();
setTimeout(function() {
    updatePage();  // You used `el`, not `element`?
}, 10000);
  //setTimeout(30000 /* 60 seconds */, updatePage());
}
updatePage();
