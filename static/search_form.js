window.addEventListener('DOMContentLoaded', async () => {
    await displayReview()

    const btnDeleteReview = document.querySelectorAll('#delete-review')
    btnDeleteReview.forEach(button => {
        button.addEventListener('click', function() {
            // Get the id of the review
            const reviewId = this.getAttribute('data-review-id');
            deleteReview(reviewId);

            // Hide the deleted review
            button.parentElement.style.display = 'none'
        });
    });
    const btnEditReview = document.querySelectorAll('#edit-review')
    btnEditReview.forEach(button => {
        button.addEventListener('click', function() {
            editReviewText(this)
        })
    })
})


async function displayAuthor(author){
    const response = await fetch(`/author?author=${author}`)
    const data = await response.json()

    if (data){
        const authorTab = document.getElementById('author-tab')
        const div = document.createElement('div')
        console.log(data)
        div.innerHTML = `<h2>${author}</h2>`
        for (const key in data){
            element = data[key]
            div.innerHTML += 
            `
            <div>
                <p>${element.volumeInfo.title}</p>
                <p>${element.volumeInfo.publishedDate}</p>
            </div>
            `        
        }

        
        authorTab.append(div)
        hideTabsExcept('author-tab')
    }
}


function hideTabsExcept(tab){
    const tabs = ['search-tab', 'results-tab', 'author-tab']
    tabs.forEach(element => {
        if (element != tab){
            const tabDiv = document.getElementById(element)
            tabDiv.style.display = 'none'
        }
    })
    document.getElementById(tab).style.display = 'block'
}

// Save and display new post
async function displayReview(){
    const response = await fetch(`/get_reviews`)
    const data = await response.json()
    
    // Get the current user id
    const userIdResponse = await fetch('/get_user_id')
    const userId = await userIdResponse.json()

    const divContainer = document.getElementById('display-posts')
    data.forEach((element) => {
        const newReview = document.createElement('div')
        newReview.innerHTML = 
            `
                <img src=${element[8]}>
                <h5>Review of ${element[6]}</h5> 
                <p>by ${element[7]}<p>
                <div id='review-body'>
                    <p id='review-text'>${element[1]}</p>
                </div>
                <p><em>Stoyan Kolev</em> ${element[3]}</p>
            `
        if (userId === element[5]){
            const reviewControls = document.createElement('div')
            reviewControls.innerHTML += `<button id=delete-review data-review-id=${element[0]}>Delete</button>`
            reviewControls.innerHTML += `<button id=edit-review data-review-id=${element[0]}>Edit</button>`
            newReview.appendChild(reviewControls)
        }
        divContainer.append(newReview)          
    })
}

// Delete a review
function deleteReview(id){
    fetch(`delete_review/${id}`, {
        method: 'DELETE'
    })
}


// Edit an existing review's text
function editReviewText(element){
    // Get the id of the review
    const reviewId = element.getAttribute('data-review-id');

    const reviewBody = document.getElementById('review-body')
    const currentText = document.getElementById('review-text').textContent
    reviewBody.innerHTML = `<textarea id='edit-review-body'>${currentText}</textarea>`
    
    element.style.display = 'none'
    const saveButton = document.createElement('button')
    saveButton.textContent = 'Save'
    let reviewControls = element.parentElement
    reviewControls.appendChild(saveButton)
    
    saveButton.addEventListener('click', function() {
        const newText = document.getElementById(`edit-review-body`).value;
        if (newText){
            const apiUrl = `edit_review/${reviewId}`
            const data = {
                'text': newText
            }
            const requestOptions = {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            } 
            fetch(apiUrl, requestOptions)
            .then(response => {
                if (response.ok){
                    return response.json()
                }
            })
            .then(data => {
                console.log(data)
            })
            
            reviewBody.innerHTML = `<p id='review-text'>${newText}</p>`
            reviewControls.removeChild(reviewControls.lastChild);
            element.style.display = 'inline-block'
        }

    })


}