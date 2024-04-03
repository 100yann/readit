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
