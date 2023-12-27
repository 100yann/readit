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

                <p>${element[1]}</p>
                <p><em>Stoyan Kolev</em> ${element[3]}</p>
            `
        if (userId === element[5]){
            newReview.innerHTML += `<button id=delete-review data-review-id=${element[0]}>Delete</button>`
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