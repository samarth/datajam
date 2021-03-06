function _getArtistListing (queryParams) {
    var deferred = Q.defer();
    d3.json("/listing" + queryParams , function (error, response) {
        // Handle error gracefully , by throwing it in the face at the very least ..

        if (error) {
            deferred.reject(error);
        }

        deferred.resolve(response);
    });

    return deferred.promise;
}



function _getTimeAggregation (queryParams) {

    var deferred = Q.defer();

    d3.json("/artists/time" + queryParams , function (error, response) {
        // Handle error gracefully , by throwing it in the face at the very least ..

        if (error) {
            deferred.reject(error);
        }

        deferred.resolve(response);
    });

    return deferred.promise;
}


function _load(d3Data, queryParams) {

    var margin = {top: 20, right: 20, bottom: 30, left: 40},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;


    var values = d3Data.artistListing.data.map(function (d) {
        return new Date(d.date).getUTCHours();
    });

    // A formatter for counts.
    var formatCount = d3.format(",.0f");

    var barClicked = false;
    var selectedBar = null;
    var barId       = 0;

    var x = d3.scale.linear()
            .domain([0, 24])
            .range([0, width]);

    // Generate a histogram using twenty four uniformly-spaced bins.
    var data = d3.layout.histogram()
            .bins(x.ticks(24))(values);

    // Samarth : 7th Feb
    // Giving probabilities for hourly metric was a stupid idea
    // the length of the historgrams already denote that, but atleast
    // the tool tip worked.

    var hourlyProbabilities = [];

    data.forEach(function (array , idx) {
        array.probability = array.length / d3Data.artistListing.data.length ;
    });


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


    var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-10, 0])
            .html(function(d) {
                return "<strong>P(x):</strong> <span style='color:red'>" + d.probability + "</span>";
            });


    function drawTable() {

        //Don't draw a table if any bar is clicked
        if (barClicked) {
            return;
        }

        // The hour of the bar that was hovered upon

        var hour = arguments[1];
        // The data that corresponds to this

        var artistData = d3Data.hourAggregation.data[hour];

        var table = d3.select('#aggTable');

        var columns = ["Artist Name", "Artist Count"];

        table.append('thead').append('tr')
            .selectAll('th')
            .data(columns).enter()
            .append('th')
            .html(function (header) {return header;});

        var serverHost = "http://datajam.com/listing";

        var tr = table.selectAll('tr')
                .data(artistData).enter()
                .append('tr');

        tr.append('td')
            .html(function(artist) { return "<a target=\"blank\" href="+ serverHost + queryParams + "&artist=" + artist[0] + ">" + artist[0] +"</a>"; });

        tr.append('td')
            .html(function(artist) { return artist[1]; });

    }

    function toggleState () {
        // Select the bar to change the color

        var currentColor;
        var clickedBarId = d3.select(this).attr('id');

        if (selectedBar && (clickedBarId !== selectedBar)) {
            // Don't do anything,  let the user switch off the highlighted
            // bar first.
            console.log("#### selected bar not equal clickedBarId");
            return ;
        }

        if (barClicked) {
            currentColor = "steelblue";
            selectedBar = null;
        } else {
            currentColor = "red";
            selectedBar = clickedBarId;
        }

        barClicked = !barClicked;

        d3.select(this).style("fill", currentColor);
        return;
    }


    function clearTable() {
        if (barClicked) {
            // Don't empty the table if any bar is clicked
            return;
        }
        $("#aggTable").empty();
    }

    svg.call(tip);

    var bar = svg.selectAll(".bar")
            .data(data)
            .enter().append("g")
            .attr("class", "bar")
            .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", x(data[0].dx) - 1)
        .attr("id", function(d) { return barId++;})
        .attr("height", function(d) { return height - y(d.y); })
        .on('mouseover', drawTable)
        .on('mouseout', clearTable)
        .on('click', toggleState);


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

    var username    = $("#username").val();
    var fromdate    = $("#fromdate").val();
    var todate      = $("#todate").val();
    var artistName  = $("#artistName").val();

    //Options more specific to aggs ...

    var minDocCount = $("#minDocCount").val();
    var order       = $("input[name=optradio]:checked").val();
    var limit       = $("#limit").val();

    var queryParams = "?username=" + username;


    if (fromdate) {
        queryParams += "&fromdate=" + fromdate;
    }

    if (todate) {
        queryParams += "&todate=" + todate;
    }

    if (artistName) {
        queryParams += "&artist=" + artistName;
    }

    if (minDocCount) {
        queryParams += "&minDocCount=" + minDocCount;
    }

    if (order) {
        queryParams += "&order=" + order;
    }


    if (limit) {
        queryParams += "&limit=" + limit;
    }

   /*
     May want to expose : min doc count and order and limits later
     Really cool metric .
   */

    // Lets make this promise dependent ,
    // we can query both time aggregations to
    // draw the tool tips too .

    var d3Data = {};
    _getArtistListing(queryParams)
        .then(function (artistListing) {
            d3Data.artistListing = artistListing;
            return _getTimeAggregation(queryParams);
        })
        .then(function(hourAggregation) {
            d3Data.hourAggregation = hourAggregation;
            // queryParams are used in listing incase a user clicks on an artist
            _load(d3Data, queryParams);
        })
        .fail(function(error) {
            alert (error);
        });
}


/*
 Initialize date time controls on the html ...
 */
(function () {
    $('#fromdatectrl').datetimepicker({
        defaultDate: "11/1/2011",
        format: 'DD/MM/YYYY'
    });

    $('#todatectrl').datetimepicker({
        defaultDate: new Date(),
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
