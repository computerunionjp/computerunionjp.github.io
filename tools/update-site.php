<?php
$secret = $argv[1];
$zipFile = $argv[2];

if ($secret !== "TO BE SET") {
  echo "Invalid secret";
  exit(1);
}

$baseUrl =
  "https://github.com/computerunionjp/computerunionjp.github.io/releases/download/latest";
$zipUrl = $baseUrl . "/" . $zipFile;
$zipFile = "../../work/" . $zipFile;
$unzipDir = "../";

echo $zipFile;
file_put_contents($zipFile, file_get_contents($zipUrl));

echo " has downloaded";

#exec("unzip -o $zipFile -d $unzipDir");
echo " and extracted.";
