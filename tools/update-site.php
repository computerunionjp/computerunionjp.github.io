<?php
$secret = $argv[1];
$zipFile = $argv[2];

if ($secret !== "TO BE SET") {
  exit("Invalid secret");
}

$baseUrl =
  "https://github.com/computerunionjp/computerunionjp.github.io/releases/download/";
$zipUrl = $baseUrl . "/" . $zipFile;
$zipFile = "../../work/" . $zipFile;
$unzipDir = "../";

file_put_contents($zipFile, file_get_contents($zipUrl));

#exec("unzip -o $zipFile -d $unzipDir");
