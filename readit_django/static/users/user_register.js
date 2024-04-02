document.addEventListener('DOMContentLoaded', () => {
    form = document.getElementById('sign-up-form')
    form.onsubmit = (event) => {
        event.preventDefault();
        
        let formFields = new FormData(form)
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        console.log(formFields)
        fetch(event.target.action, {
            method: 'POST',
            headers: {
                "X-CSRFToken": csrfToken,
            },
            body: formFields
        }).then((response) => {
            if (!response.ok){
                return response.text()
            } else {
                window.location.href = '/home'
            }
        }).then((data) => {
            let errorField = document.createElement('span')
            errorField.className = 'error-message'
            errorField.textContent = data
            const emailField = document.getElementById('email-field')
            emailField.append(errorField)
            const emailInput = document.getElementById('email-input')
            emailInput.style.borderColor = 'red'
        })
    }
})