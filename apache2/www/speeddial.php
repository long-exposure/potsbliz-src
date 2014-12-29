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

function check_input($dbconn)
{
  if (!preg_match("/^[0-9#\*]{1,3}$/", $_POST["shortcut"])) 
    return "Invalid speed dial number!";
    
  if (!preg_match("/^[0-9#\*\-\/]{1,20}$/", $_POST["phonenumber"])) 
    return "Invalid phone number!";
  
  if($_GET["action"] == "create")
  {
    $sql = "SELECT * FROM speeddial WHERE shortcut = " . $_POST["shortcut"] . ";";
    $result = $dbconn->query($sql);
    if ($result->num_rows > 0)
      return "Speed dial number already exists!";
  }
    
  return true;
}

// Create connection
$dbconn = new mysqli('localhost', 'potsbliz', 'potsbliz', 'potsbliz');
if ($dbconn->connect_error) {
  send_error($dbconn->connect_error);
} 

if($_GET["action"] == "list")
{
  $sql = "SELECT * FROM speeddial;";
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
  
if($_GET["action"] == "create")
{
  $result = check_input($dbconn);
  if ($result === true)
  {
    $sql = "INSERT INTO speeddial(shortcut, phonenumber, comment) VALUES('" .
            $_POST["shortcut"] . "', '" .
            $_POST["phonenumber"] . "', '" .
            $dbconn->real_escape_string($_POST["comment"]) . "');";
    $dbconn->query($sql);

    $sql = "SELECT * FROM speeddial WHERE id = LAST_INSERT_ID();";
    $result = $dbconn->query($sql);
    $row = $result->fetch_array();

    //Return result to jTable
    $jTableResult = array();
    $jTableResult['Result'] = "OK";
    $jTableResult['Record'] = $row;
    print json_encode($jTableResult);
  }
  else
    send_error(var_export($result, true));
}
  
if($_GET["action"] == "update")
{
  $result = check_input($dbconn);
  if ($result === true)
  {
    $sql = "UPDATE speeddial SET shortcut = '" . $_POST["shortcut"] .
           "', phonenumber = '" . $_POST["phonenumber"] .
           "', comment = '" . $dbconn->real_escape_string($_POST["comment"]) .
           "' WHERE id = " . $_POST["id"] . ";";
    $dbconn->query($sql);

    //Return result to jTable
    $jTableResult = array();
    $jTableResult['Result'] = "OK";
    print json_encode($jTableResult);
  }
  else
    send_error(var_export($result, true));
}
  
if($_GET["action"] == "delete")
{
  $sql = "DELETE FROM speeddial WHERE id = " . $_POST["id"] . ";";
  $dbconn->query($sql);
 
  //Return result to jTable
  $jTableResult = array();
  $jTableResult['Result'] = "OK";
  print json_encode($jTableResult);
}

$dbconn->close();

?>
