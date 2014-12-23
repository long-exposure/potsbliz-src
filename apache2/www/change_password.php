<?php

// breaks JSON error output!
//error_reporting(E_ALL);
//ini_set('display_errors', '1');

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
else
{
	$sql = "UPDATE mysql_auth SET passwd=MD5('" . $_POST["newpw"] . "') WHERE username='admin' AND passwd=MD5('" . $_POST["oldpw"] . "');";
	if ($dbconn->query($sql))
	{
	  if ($dbconn->affected_rows == 1)
	  {
	    //Return result to jTable
	    $jTableResult = array();
	    $jTableResult['Result'] = "OK";
	    $jTableResult['Message'] = "Password successfully changed";
	    print json_encode($jTableResult);
	  }
	  else
	  {
	    send_error("Old password is wrong!");
	  }
	}
	else
	{
	  send_error($dbconn->error);
	}
}
$dbconn->close();

?>
