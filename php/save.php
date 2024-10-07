<?php

// Set CORS headers to allow cross-origin requests
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");

// Handle preflight OPTIONS requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0);
}

// Constants for file paths
$responsesCsvFilePath = '../output/responses.csv';
$csvHeaders = ["UserID", "QuestionID", "StudentAnswer", "ResponseRating"];

// Function to save responses to CSV
function saveResponsesToCsv($responses, $csvFilePath, $csvHeaders) {
    $fileExists = file_exists($csvFilePath);
    $file = fopen($csvFilePath, 'a');

    // Write headers if file doesn't exist
    if (!$fileExists) {
        fputcsv($file, $csvHeaders);
    }

    // Write each response row
    foreach ($responses as $response) {
        fputcsv($file, $response);
    }

    fclose($file);
}

// Main logic for processing POST request and saving data
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Set response content type to JSON
    header('Content-Type: application/json');

    try {
        // Get the JSON data from the request body
        $formData = json_decode(file_get_contents('php://input'), true);

        // Validate if the form data contains 'userId'
        if (!isset($formData['userId'])) {
            throw new Exception('UserID is required.');
        }

        $userId = $formData['userId'];

        // Prepare the responses to be saved
        $responses = [];
        foreach ($formData as $key => $value) {
            if ($key !== 'userId') {
                $responses[] = [$userId, $key, $value, '']; // Assuming ResponseRating is empty for now
            }
        }

        // Save responses to CSV
        saveResponsesToCsv($responses, $responsesCsvFilePath, $csvHeaders);

        // Respond with success message
        echo json_encode(["message" => "Responses saved successfully to ", "Path" =>  $responsesCsvFilePath]);
    } catch (Exception $e) {
        // Log the error to the error log file
        error_log($e->getMessage());

        // Respond with error message
        echo json_encode(["error" => $e->getMessage()]);
    }
} else {
    // Return 405 Method Not Allowed for non-POST requests
    http_response_code(405);
    echo json_encode(["error" => "Method not allowed"]);
}
?>
