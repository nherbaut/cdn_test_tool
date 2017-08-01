 <!DOCTYPE html>
<html lang="en">
<head>
  <title>nextnet.top</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
 <!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">

<!-- jQuery library -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<!-- Latest compiled JavaScript -->
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
<style media="screen" type="text/css">

.dropdown-menu.multi-column {
    width: 400px;
}

.dropdown-menu.multi-column .dropdown-menu {
    display: block !important;
    position: static !important;
    margin: 0 !important;
    border: none !important;
    box-shadow: none !important;
}

</style>



</head>
<body>

<h1>Presentation</h1>
<p>
This page presents the experimental results of the impact of DNS server selection on the route from end-user to content.
</p>

<ul class="nav" style="float: left;" >
 {%   for k,v in data.items()    %}
 <li class="dropdown" style="float: left;">  <a href="#" data-toggle="dropdown">{{ k }}</a>
 <div class="dropdown-menu multi-column">
              <div class="container-fluid">
                <div class="row-fluid">

    {%   for item in v   %}
    <div class="span6">
    <ul class="dropdown-menu">
       <li class="">
        <a href="{{item[1]}}">{{item[0]}}</a>
        </li>
    </ul>
    </div>
    {% endfor %}
    </div></div></div>

 {% endfor %}
</ul>


</body>
</html>