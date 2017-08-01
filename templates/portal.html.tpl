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




</head>
<body>

<ul class="list-group">
 {%   for k,v in data.items()    %}
 <li class="list-group-item" >{{ k }}
    {%   for item in v   %}
    <ul class="">
       <li class="">
        <a href="{{item[1]}}">{{item[0]}}</a>
        </li>
    </ul>
    {% endfor %}

 {% endfor %}
</ul>


</body>
</html>