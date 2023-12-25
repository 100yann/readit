document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('sign-up-form')
    form.onsubmit = async (event) => {
        event.preventDefault()

        const userEmail = document.getElementById('email-input').value
        const userPassword = document.getElementById('password-input').value

        const response = await fetch('/sign_up', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: userEmail,
                password: userPassword,
            }),
        })


        // Handle the response, e.g., show a success message or handle errors
        const data = await response.json()
        console.log(data)
    }
})