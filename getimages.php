<?php
echo "<script>console.log('in getimages');</script>"
$db = new SQLite3('database.db');
$ret="";
$res = $db->query('SELECT productId, image FROM products');

while ($row = $res->fetchArray()) {
    $st = "{$row['productId']},{$row['image']};";
    $ret .= $st;
}
echo $ret