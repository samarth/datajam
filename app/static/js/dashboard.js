function _load(lastfmData) {

    var margin = {top: 20, right: 20, bottom: 30, left: 40},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;


    var values = lastfmData.map(function (d) {
        return new Date(d.date).getUTCHours();
    });

    // A formatter for counts.
    var formatCount = d3.format(",.0f");


    var x = d3.scale.linear()
            .domain([0, 24])
            .range([0, width]);


    // Generate a histogram using twenty four uniformly-spaced bins.
    var data = d3.layout.histogram()
            .bins(x.ticks(24))
    (values);

    var y = d3.scale.linear()
            .domain([0, d3.max(data, function(d) { return d.y; })])
            .range([height, 0]);


    var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");


    var svg = d3.select("#dashboard").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    var bar = svg.selectAll(".bar")
            .data(data)
            .enter().append("g")
            .attr("class", "bar")
            .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", x(data[0].dx) - 1)
        .attr("height", function(d) { return height - y(d.y); });

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", 6)
        .attr("x", x(data[0].dx) / 2)
        .attr("text-anchor", "middle")
        .text(function(d) { return formatCount(d.y); });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

}

function getUserData () {
    $("#dashboard").empty();

    var username = $("#username").val();
    var fromdate = $("#fromdate").val();
    var todate   = $("#todate").val();


    var queryParams = "?username=" + username;


    if (fromdate) {
	queryParams += "&fromdate=" + fromdate;
    }

    if (todate) {
	queryParams += "&todate=" + todate;
    }

    d3.json("/listing" + queryParams , function (error, response) {
            // Handle error gracefully , by throwing it in the face at the very least ..

            if (error) {
                alert("It didn't work " + (error.message || response.error || response.data));
            }

            _load(response.data);
        });
}


/*
 Initialize date time controls on the html ...
 */
(function () {
    $('#fromdatectrl').datetimepicker({
	format: 'DD/MM/YYYY'
    });

    $('#todatectrl').datetimepicker({
	format: 'DD/MM/YYYY',
        useCurrent: false //Important! See issue #1075
    });

    $("#fromdatectrl").on("dp.change", function (e) {
        $('#todatectrl').data("DateTimePicker").minDate(e.date);
    });

    $("#todatectrl").on("dp.change", function (e) {
        $('#fromdatectrl').data("DateTimePicker").maxDate(e.date);
    });
}());
