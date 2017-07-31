 <!DOCTYPE html>
<html lang="en">
<head>
  <title>nextnet.top</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
  <script src="https://cdn.rawgit.com/ariutta/svg-pan-zoom/f324a9d3/dist/svg-pan-zoom.min.js"></script>


</head>
<body>
<center>

<center>
<div id="mytable">
 {{ table }}
 </div>

<object class="img-responsive" id="worldmap" type="image/svg+xml" data="output.svg" style="width: 80%;  border:1px solid black; " >Your browser does not support SVG</object>



<script>
$( document ).ready(function() {
$("#mytable table").addClass("table table-striped table-bordered table-hover");
  svgPanZoom('#worldmap', {
          zoomEnabled: true,
          controlIconsEnabled: true
        });
});
</script>

</body>
</html> 