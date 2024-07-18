function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}


document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('questionnaireForm');
    const userID = generateUUID(); // Generate a userID when the form loads

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        handleSubmit(e, userID); // Pass userID to the handler
    });

    // Handle clicks on the form for dynamically added "+" buttons
    form.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-answer')) {
            addInputField(e.target.dataset.questionId);
        }
    });
});


async function handleSubmit(e, userID) {
    e.preventDefault();
    const inputs = document.querySelectorAll("#questionnaireForm input[type='text']");
    for (let input of inputs) {
        if (input.value.trim() !== '') { // Only send non-empty inputs
            await sendInputData(userID, input);
        }
    }
}

async function sendInputData( userID, input) {
    const formData = {  userId: userID, [input.name]: input.value };
    // Show loading spinner
    const spinner = document.createElement('span');
    spinner.className = 'spinner';
    //spinner.textContent = 'Loading...';
    input.parentNode.insertBefore(spinner, input.nextSibling);
    
    try {
        const response = await fetch('http://10.1.158.22:5000/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        const data = await response.json();
        
        // Remove spinner
        input.parentNode.removeChild(spinner);
        
        const ratingElement = document.createElement('div');
        ratingElement.textContent = `Rating: ${data[input.name]}`;
        ratingElement.className = 'rating';
        input.parentNode.insertBefore(ratingElement, input.nextSibling);
    } catch (error) {
        console.error('Error:', error);
        input.parentNode.removeChild(spinner);
    }
}
// Correct function to handle adding inputs
function addInputField(questionId) {
    const questionDiv = document.getElementById(questionId);
    if (questionDiv) {  // Check if the element exists
        const newInputNumber = questionDiv.querySelectorAll('input[type="text"]').length + 1;
        const newInput = document.createElement('input');
        newInput.type = 'text';
        newInput.name = `${questionId}-${newInputNumber}`;
        questionDiv.appendChild(newInput);
        newInput.focus();  // Focus the new input
    } else {
        console.error('No element found with ID:', questionId);
    }
}

