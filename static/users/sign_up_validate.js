document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('sign-up-form')
    form.onsubmit = async (event) => {
        event.preventDefault()

        const userEmail = document.getElementById('email-input')
        const userPassword = document.getElementById('password-input')
        const firstName = document.getElementById('first-name')
        const lastName = document.getElementById('last-name')

        const response = await fetch('/sign_up', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: userEmail.value,
                password: userPassword.value,
                firstName: firstName.value,
                lastName: lastName.value
            }),
        })


        // Handle the response, e.g., show a success message or handle errors
        const data = await response.json()
        if (data.status === 'error'){
            // Highlight the email field
            userEmail.style.borderColor = 'red'

            // Display error message under email field
            const emailField = document.getElementById('email-field')
            const errorMessage = document.createElement('h6')
            errorMessage.className = 'error'
            errorMessage.textContent = data.message
            emailField.append(errorMessage)
        }
    }
})