<?php
// Enter your Host, username, password, database below.
$host = "localhost";
$username = "root";
$password = "";
$database = "paypal";
$port = 3307; // Try 3306 first (default), or 3307 if that's what XAMPP uses

$con = mysqli_connect($host, $username, $password, $database, $port);

if(!$con){
    die("Connection Error: ".mysqli_connect_error());
}
?>