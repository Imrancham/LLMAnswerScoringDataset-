<?php
// Enable error reporting for debugging
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);


// Set CORS headers to allow cross-origin requests
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");

// Handle preflight OPTIONS requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0);
}

$participantsCsvFilePath = './output/participants.csv';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json');

    try {
        $data = json_decode(file_get_contents(filename: 'php://input'), true);
        $email = $data['email'];
        $userId = $data['userId'];
        $LLM_familiarity = $data['LLM_familiarity'];
        $LLM_usage_frequency = $data['LLM_usage_frequency'];
        $other_LLMs = $data['other_LLMs'];

        if ($email && $userId) {
            $fileExists = file_exists($participantsCsvFilePath);
            $file = fopen($participantsCsvFilePath, 'a');

            if (!$fileExists) {
                fputcsv($file, ['userID', 'email', 'LLM_familiarity', 'LLM_usage_frequency', 'other_LLMs']);
            }

            fputcsv($file, [$userId, $email, $LLM_familiarity, $LLM_usage_frequency, $other_LLMs]);
            fclose($file);

            echo json_encode(["message" => "Email and user data saved successfully!"]);
        } else {
            echo json_encode(["error" => "Email or UserID not provided!"]);
        }
    } catch (Exception $e) {
        echo json_encode(["error" => $e->getMessage()]);
    }
} else {
    http_response_code(405);
    echo json_encode(["error" => "Method not allowed"]);
}
?>
