document.addEventListener('DOMContentLoaded', () => {
    var form = document.getElementById('sign-up-form')
    form.onsubmit = (event) => {
        event.preventDefault();
        
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        fetch(event.target.action, {
            method: 'POST',
            headers: {
                "X-CSRFToken": csrfToken,
            },
            body: new FormData(form)
        }).then((response) => {
            if (!response.ok){
                return response.json()
            } else {
                window.location.href = '/home'
            }
        }).then((data) => {
            let errorField = document.createElement('span')
            errorField.className = 'error-message'
            errorField.textContent = data.detail
            const emailField = document.getElementById('email-field')
            emailField.append(errorField)
            const emailInput = document.getElementById('email-input')
            emailInput.style.borderColor = 'red'
        })
    }
})