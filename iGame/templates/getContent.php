<?php
if(!empty($_GET['id'])){
    // Database configuration
    $dbHost = 'igame-instance.cj3l9swcgrzl.us-east-1.rds.amazonaws.com';
    $dbUsername = 'postgres';
    $dbPassword = 'password';
    $dbName = 'igame_db';

    // Create connection and select database
    $db = new mysqli($dbHost, $dbUsername, $dbPassword, $dbName);

    if ($db->connect_error) {
        die("Unable to connect database: " . $db->connect_error);
    }

    // Get content from the database
    $query = $db->query("SELECT * FROM games WHERE id = {$_GET['id']}");

    if($query->num_rows > 0){
        $gameData = $query->fetch_assoc();
        echo '<h5>'.$gameData['name'].'</h5>';
        echo '<p>'.$gameData['age_ratings'].'</p>';
        echo '<p>'.$gameData['keywords'].'</p>';
        echo '<p>'.$gameData['rating'].'</p>';
        echo '<p>'.$gameData['similar_games'].'</p>';
    }else{
        echo 'Content not found....';
    }
}else{
    echo 'Content not found....';
}
?>