document.addEventListener('DOMContentLoaded', () => {
    const editButtons = document.querySelectorAll('#edit-button')
    editButtons.forEach((button) => {
        button.onclick = () => {
            editReview(button)
        }
    })

    const deleteButtons = document.querySelectorAll('#delete-button')
    deleteButtons.forEach((button) => {
        button.onclick = () => {
            deleteReview(button)
        }
    })

    const likeButtons = document.querySelectorAll('#like-button')
    likeButtons.forEach((button) => {
        button.onclick = () => {
            likeReview(button)
        }
    })
})


function editReview(editButton) {
    editButton.hidden = true;
    
    const saveButton = editButton.parentElement.querySelector('#save-button')
    saveButton.hidden = false;

    const reviewContainer = editButton.closest('#review').querySelector('#review-container');

    const reviewText = reviewContainer.querySelector('#review-text');
    reviewText.hidden = true;

    const newReview = reviewContainer.querySelector('#edit-review-area')
    newReview.textContent = reviewText.textContent
    newReview.hidden = false;
    newReview.focus()
    newReview.setSelectionRange(newReview.textContent.length, newReview.textContent.length)

    saveButton.onclick = () => {
        if (newReview.value != reviewText.textContent && newReview.value.trim().length > 0) {
            reviewText.textContent = newReview.value
            const reviewId = reviewContainer.closest('#review').getAttribute('data-review-id')
            saveReview(reviewId, reviewText.textContent)
        }
        newReview.hidden = true;
        reviewText.hidden = false;
        
        saveButton.hidden = true;
        editButton.hidden = false;
    }
}


function saveReview(reviewId, reviewText) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    response = fetch(`edit/${reviewId}`, {
        method: 'PUT',
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(reviewText)
    })
}


function deleteReview(button) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    const reviewContainer = button.closest('#review');
    const reviewId = reviewContainer.getAttribute('data-review-id')

    reviewContainer.hidden = true;

    response = fetch(`delete/${reviewId}`, {
        method: 'DELETE',
        headers: {
            "X-CSRFToken": csrfToken,
        }
    })
}


function likeReview(button) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    const reviewId = button.closest('#review').getAttribute('data-review-id')
    const totalLikes = button.parentElement.querySelector('#review-likes')

    const response = fetch(`like/${reviewId}`, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    response.then((response) => response.json())
    .then((data) => {
        const isLiked = data.status
        if (isLiked === 'unliked'){
            button.textContent = 'Like'
            totalLikes.textContent = parseInt(totalLikes.textContent) - 1
        } else {
            button.textContent = 'Liked'
            totalLikes.textContent = parseInt(totalLikes.textContent) + 1
        }
    });
}