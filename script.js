
// Variables
let currentQuestionIndex = 0;
const userId = localStorage.getItem('userId');
const totalQuestions = 9; // Update based on the number of questions


// Function to generate a UUID
function generateUUID() { 
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}



// Function to fetch question data
function fetchQuestionData(index) {
    const requestBody = { id: index };
    
    console.log('Sending request with body:', requestBody); // Log the request body

    return fetch('./php/getQues.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => {
        console.log('Response status:', response); // Log the response status code

        // Log the response before parsing to JSON
        return response.text().then(text => {

            try {
                const jsonResponse = JSON.parse(text);
                console.log('Parsed JSON response: ', jsonResponse); // Log parsed JSON response
                return jsonResponse;
            } catch (error) {
                console.error('Error parsing JSON:', error);
                throw new Error('Invalid JSON response');
            }
        });
    })
    .catch(error => {
        console.error('Error fetching question:', error); // Log any errors
        throw error;
    });
}


// Function to render the question form
function renderQuestionForm(index , questionText) {
    // Calculate progress percentage
    const progressPercentage = Math.round(((index-1) / totalQuestions) * 100);
    
    document.getElementById("questionContainer").innerHTML = `
        <form id="questionnaireForm">
            <div class="question" id="question${index}">
                <h4> Aufgabe ${index}: </h4>
                <label for="q${index}-1"> ${questionText}</label>
                <p>Deine Antwort.</p>
                <input type="text" id="q${index}-1" name="q${index}-1">
                <p>Gib andere Antworten, die falsch sind, aber richtig erscheinen. Versuche, das System zu überlasten (auszutricksen).</p>
                <input type="text" id="q${index}-2" name="q${index}-2">
                <input type="text" id="q${index}-3" name="q${index}-3">
                <input type="text" id="q${index}-4" name="q${index}-4">
                <input type="text" id="q${index}-5" name="q${index}-5">
            </div>
        </form>

        <!-- Progress Bar Section -->
        <div id="progressBarContainer" style="margin-top: 20px;">
    <div class="progress-bar-background">
        <div id="progressBar" class="progress-bar-fill" style="width: ${progressPercentage}%;">
            <span class="progress-bar-text">${progressPercentage}%</span>
        </div>
    </div>
</div>
    `;
}


// Function to validate question inputs
function validateQuestionInputs() {
    const questions = document.querySelectorAll(".question");
    let validSubmission = true;

    questions.forEach(question => {
        const questionInputs = question.querySelectorAll('input[type="text"]');
        
        // Filter to get non-empty inputs
        const nonEmptyInputs = Array.from(questionInputs).filter(input => input.value.trim() !== '');
        
        // Ensure at least 3 input fields are non-empty
        if (nonEmptyInputs.length < 3) {
            validSubmission = false;
            // Highlight the question or show an error message
            question.style.border = '2px solid red'; // Example of highlighting invalid fields
        } else {
            question.style.border = ''; // Remove highlight if valid
        }
    });

    if (!validSubmission) {
        alert('Bitte gib zu jeder Frage mindestens drei Antworten.');
        return false; // Validation failed
    }
    return true; // Validation passed
}

// Function to load a question
function loadQuestion(index) {
    fetchQuestionData(index)
        .then(data => {
            const questionText = data.question;
            renderQuestionForm(index, questionText );
        })
        .catch(error => {
            console.error('Error loading question:', error);
        });
}

// Function to save response and load next question
async function nextQuestion(e) {
    e.preventDefault(); // Prevent default behavior if it's a form submit
    // Call validation method before saving inputs
    const isValid = validateQuestionInputs();
    if (!isValid) {
        return; // Stop further execution if validation fails
    }

    // Gather all the text inputs from the form
    const inputs = document.querySelectorAll("#questionnaireForm input[type='text']");
    const jsonData = { userId: userId }; // Assuming 'userId' is a global variable

    // Collect non-empty input values
    inputs.forEach(input => {
        if (input.value.trim() !== '') {
            jsonData[input.name] = input.value;
        }
    });

    // Save the current response
    await saveResponse(jsonData);

    // Clear the input fields after saving
    inputs.forEach(input => {
        input.value = '';
    });

    // Increment the question index and load the next question
    currentQuestionIndex += 1;
    if (currentQuestionIndex <= totalQuestions) {
        loadQuestion(currentQuestionIndex);
    } else {
        window.location.href = 'thankyou.html';
    }
}

// Function to save the response
async function saveResponse(jsonData) {
    await fetch('./php/save.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Data saved');
    })
    .catch(error => {
        console.error('Error saving data:', error);
    });
}

// Function to load the previous question
function previousQuestion() {
    if (currentQuestionIndex > 1) {
        currentQuestionIndex -= 1;
        loadQuestion(currentQuestionIndex);
    }
}

// Function to handle feedback form submission
async function handleFeedbackFormSubmission(userId) {
    // Get the form inputs
    const emailInput = document.getElementById('email').value.trim();
    const familiarityInput = document.getElementById('familiarity').value;
    const usageFrequencyInput = document.querySelector('input[name="usage_frequency"]:checked');
    const otherLLMsInput = document.getElementById('other_llms').value.trim();

    // Ensure all necessary inputs are provided and valid
    if (!userId) {
        alert('User ID is missing. Please fill out the form.');
        window.location.href = 'index.html'; // Redirect to your instructions page
        
    }

    if ( familiarityInput && usageFrequencyInput) {
        const feedbackData = {
            email: emailInput,
            LLM_familiarity: familiarityInput,
            LLM_usage_frequency: usageFrequencyInput.value, // Get value from selected radio button
            other_LLMs: otherLLMsInput || "None" // Default to "None" if the field is empty
        };

        try {
            const response = await fetch('./php/saveFeedback.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(feedbackData)
            });

            if (response.ok) {
                // Success: Redirect to the instructions page after 1 second
                console.log("response:", response)
                setTimeout(() => {
                    alert("Danke für Deine Teilnahme!");
                    window.location.href = 'index.html'; // Redirect to your instructions page
                }, 500); // 1 second delay before redirection
            } else {
                console.error('Failed to save feedback');
            }
        } catch (error) {
            console.error('Error:', error);
        }

    } else {
        alert('Bitte alle mit * gekennzeichneten Felder ausfüllen.');
    }
}

function addInputField() {
    const Qid =  `question${currentQuestionIndex}`;
    const questionDiv = document.getElementById(Qid);
    if (questionDiv) {
        const newInputNumber = questionDiv.querySelectorAll('input[type="text"]').length + 1;
        const newInput = document.createElement('input');
        newInput.type = 'text';
        newInput.name = `q${currentQuestionIndex+1}-${newInputNumber}`;
        questionDiv.appendChild(newInput);
        newInput.focus();
    } else {
        console.error('No element found with ID:', Qid);
    }
}

// Handle thank you page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check if the page contains the nextButton and prevButton elements
    const nextButton   = document.getElementById('nextButton');
    const prevButton   = document.getElementById('prevButton');
    // Handle feedback form functionality
    const feedbackForm = document.getElementById('feedbackForm');
    const addAnswer    = document.getElementById('add-answer')
    
    if (nextButton) {
        nextButton.addEventListener('click', nextQuestion);
    }
    
    if (prevButton) {
        prevButton.addEventListener('click', previousQuestion);
    }

    //

    // Listener for the feedback form submission
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function (e) {
            e.preventDefault();
            handleFeedbackFormSubmission(userId); // Call the function and pass userId
        });
    }

    if(addAnswer){
        addAnswer.addEventListener('click', addInputField)
    }
});
