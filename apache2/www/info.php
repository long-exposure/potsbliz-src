<?php

header("Content-Type: text/plain"); 

passthru("apt-cache show potsbliz-rpi");
passthru("uname -a");

?>
