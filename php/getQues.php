<?php
// Enable error reporting for debugging
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);



// Set CORS headers to allow cross-origin requests
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
// Handle preflight OPTIONS requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0);
}

$questionDirectory = "./data";

// Function to load the question prompt
function loadQuestionPrompt($filePath) {
    if (file_exists($filePath)) {
        return file_get_contents($filePath);
    } else {
        return null;
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json');

    try {
        $data = json_decode(file_get_contents('php://input'), true);
        $questionId = $data['id'];
        $filePath = $questionDirectory . "/q" . $questionId . ".txt";

        // Load the question
        $question = loadQuestionPrompt($filePath);
        if ($question) {
            echo json_encode(["question" => $question]);
        } else {
            echo json_encode(["error" => "Question not found".  $filePath]);
        }
    } catch (Exception $e) {
        echo json_encode(["error" => $e->getMessage()]);
    }
} else {
    http_response_code(405);
    echo json_encode(["error" => "Method not allowed"]);
}
?>
