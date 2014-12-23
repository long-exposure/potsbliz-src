<?php

error_reporting(E_ALL);
ini_set('display_errors', '1');

function send_error($message)
{
  $jTableResult = array();
  $jTableResult['Result'] = "ERROR";
  $jTableResult['Message'] = $message;
  print json_encode($jTableResult);
}

// Create connection
$dbconn = new mysqli('localhost', 'potsbliz', 'potsbliz', 'potsbliz');
if ($dbconn->connect_error) {
  send_error($dbconn->connect_error);
} 

if($_GET["action"] == "list")
{
  $sql = "SELECT * FROM config ORDER BY position;";
  $result = $dbconn->query($sql);
  $rows = array();
  while($row = $result->fetch_array())
    $rows[] = $row;

  //Return result to jTable
  $jTableResult = array();
  $jTableResult['Result'] = "OK";
  $jTableResult['Records'] = $rows;
  print json_encode($jTableResult);
}
  
if($_GET["action"] == "update")
{
  $sql = "UPDATE config SET config_value = '" . $_POST["config_value"] . "' WHERE config_key = '" . $_POST["config_key"] . "';";
  $dbconn->query($sql);

  //Return result to jTable
  $jTableResult = array();
  $jTableResult['Result'] = "OK";
  print json_encode($jTableResult);
}

$dbconn->close();

?>
