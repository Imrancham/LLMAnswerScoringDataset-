// Function to get the value of a query parameter by name
function getQueryParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

document.addEventListener('DOMContentLoaded', function() {
    const userID = getQueryParameter('userID');
    const emailForm = document.getElementById('emailForm');

    if (emailForm) {
        emailForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const emailInput = document.getElementById('email');
            const email = emailInput.value.trim();

            if (email && userID) {
                const emailData = {
                    email: email,
                    userId: userID
                };

                try {
                    const response = await fetch('http://10.1.158.22:5000/saveEmail', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(emailData)
                    });

                    if (response.ok) {

                        // Redirect back to the home page after 3 seconds
                        setTimeout(() => {
                            window.location.href = 'index.html'; // Replace 'index.html' with the path to your home page
                        }, 1000); // 3000 milliseconds = 3 seconds
                    } else {
                        console.error('Failed to save email and userID');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            } else {
                alert('Please enter an email address.');
            }
        });
    }
});
