document.addEventListener('DOMContentLoaded', () => {
    var form = document.getElementById('sign-in-form')
    form.onsubmit = (event) => {
        event.preventDefault()

        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        
        fetch(event.target.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: new FormData(form)

        }).then((response) => {
            if (response.ok){
                window.location.href = '/home'
            }
            return response.json()
        }).then((data) => {
            if (!document.querySelector('.error-message') && data.detail){
                var errorDiv = document.createElement('div')
                errorDiv.innerHTML = `<span class="error-message">${data.detail}</span>`
                form.insertBefore(errorDiv, form.querySelector('#btn-submit'))  
            }
        })
    }
})


// Function to get cookie value by name
function checkAccessTokenCookie() {
    // Split the document's cookies into an array of key-value pairs
    const cookies = document.cookie.split(';').map(cookie => cookie.trim());

    // Loop through the cookies array to find the access_token cookie
    for (const cookie of cookies) {
        // Check if the cookie name matches 'access_token'
        if (cookie.startsWith('access_token=')) {
            // The access_token cookie exists
            return true;
        }
    }

    // The access_token cookie doesn't exist
    return false;
}