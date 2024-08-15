function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function replaceUmlauts(text) {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = text;
    text = textarea.value;

    // Replace newlines with <br> tags
    return text.replace(/\n/g, '<br>');
}

function decodeUnicodeEscapes(text) {
    return text.replace(/\\u([0-9a-fA-F]{4})/g, function (match, group) {
        return String.fromCharCode(parseInt(group, 16));
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('questionnaireForm');
    const userID = generateUUID(); // Generate a userID when the form loads

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        handleSubmit(e, userID); // Pass userID to the handler
    });

    form.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-answer')) {
            addInputField(e.target.dataset.questionId);
        }
    });
});

async function handleSubmit(e, userID) {
    e.preventDefault();
    const inputs = document.querySelectorAll("#questionnaireForm input[type='text']");
    const formData = { userId: userID };
     // Create a spinner element
     const spinner = document.createElement('div');
     spinner.className = 'spinner';
 
     // Add the spinner to the body or a container that covers the entire page
     document.body.appendChild(spinner);

    inputs.forEach(input => {
        if (input.value.trim() !== '') { // Only include non-empty inputs
            formData[input.name] = input.value;
        }
    });

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
        spinner.remove();

        inputs.forEach(input => {
            if (input.value.trim() !== '') { // Only include non-empty inputs
                // Check if there's an existing rating element and remove it
                let existingRating = input.nextElementSibling;
                if (existingRating && existingRating.classList.contains('rating')) {
                    existingRating.remove();
                }

                // Create a new rating element and insert it after the input
                const ratingElement = document.createElement('div');
                // Replace newline escape characters with actual HTML line breaks
                const decodedText = decodeUnicodeEscapes(data[input.name]);
                const formattedText = decodedText.replace(/\\n/g, '<br>');
                ratingElement.innerHTML = `Rating: ${formattedText}`;
                ratingElement.className = 'rating';
                input.insertAdjacentElement('afterend', ratingElement);
            }
        });
    } catch (error) {
        console.error('Error:', error);
        // Remove spinner
        spinner.remove();
    }
}

function addInputField(questionId) {
    const questionDiv = document.getElementById(questionId);
    if (questionDiv) {
        const newInputNumber = questionDiv.querySelectorAll('input[type="text"]').length + 1;
        const newInput = document.createElement('input');
        newInput.type = 'text';
        newInput.name = `${questionId}-${newInputNumber}`;
        questionDiv.appendChild(newInput);
        newInput.focus();
    } else {
        console.error('No element found with ID:', questionId);
    }
}
