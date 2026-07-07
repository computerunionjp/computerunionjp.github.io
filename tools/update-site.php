<?php
$token = $_GET["token"] ?? "";

if ($token !== "TO BE SET") {
  http_response_code(403);
  exit("Invalid token");
}
try {
  $zipUrl =
    "https://github.com/computerunionjp/computerunionjp.github.io/releases/download/latest/site.zip";
  $zipFile = "../../work/site.zip";
  $unzipDir = "../";

  echo $zipFile;
  file_put_contents($zipFile, file_get_contents($zipUrl));

  echo " has downloaded";

  #exec("unzip -o $zipFile -d $unzipDir");
  echo " and extracted.";

  http_response_code(200);
  echo "OK";
} catch (Throwable $e) {
  http_response_code(500);
  echo $e->getMessage();
  exit();
}
