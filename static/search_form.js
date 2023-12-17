window.addEventListener('DOMContentLoaded', () => {

    const post = document.getElementById('post-form')
    post.onsubmit = async (event) => {
        event.preventDefault()
        const postValue = document.getElementById('post-value')

        if (postValue.value){
            newPost(postValue.value)
        }
    }    
    const form = document.getElementById('search-form')
    
    form.onsubmit = async (event) => {
        event.preventDefault()
        const searchValue = document.getElementById('search').value

        // Check if there is any search input
        if (searchValue){
            // Display the results on the page
            const results = await displaySearchResults(searchValue)

            // On authort name click display get and display data
            // about the author
            const authorLinks = document.querySelectorAll('#author-link')
            authorLinks.forEach((element) => {
                element.onclick = (event) => {
                    event.preventDefault()
                    displayAuthor(element.textContent)
                }
            })

            const resultEntries = document.querySelectorAll('#entryThumbnail')
            const resultArray = Array.from(resultEntries)

            resultEntries.forEach((element1) => {
                // On click of a book entry hide all the other entries
                // and display only the clicked entry
                element1.onclick = () => {
                    console.log(element1)
                    resultEntries.forEach((element2) => {
                        if (element1 != element2){
                            element2.parentElement.style.display = 'none'
                        }
                    })
                    // If currently only one entry is displayed and it's
                    // clicked again - show all entries again
                    if (element1.parentElement.style.display === 'block') {
                        resultArray.forEach((element2) => {
                            element2.parentElement.style.display = 'flex';
                        });
                    } else {
                        element1.parentElement.style.display = 'block';
                    }
                }
            })
        }
    }

})

// Display books returned by the Google API
async function displaySearchResults(searchValue){
    // fetch the results
    const response = await fetch(`/find?search=${searchValue}`)
    const data = await response.json()

    if (data){
        // display the results tab where all results will be displayed
        const resultsTab = document.getElementById('results-tab')
        resultsTab.innerHTML = ''                
        resultsTab.style.display = 'block'

        data.forEach(element => {
            // display only results that have cover photos
            if ('imageLinks' in element.volumeInfo){
                let div = document.createElement('div')
                div.className = 'displayEntry'
                div.innerHTML = `
                    <div id='entryThumbnail'>
                        <img src=${element.volumeInfo.imageLinks.thumbnail}>
                    </div>
                    <div id='entryDetails'>
                        <h2>${element.volumeInfo.title}</h2>
                        <h4>by <a href='' id='author-link'>${element.volumeInfo.authors}</a></h4>
                        <p>${element.volumeInfo.description}</p>
                        <p>${element.volumeInfo.pageCount}</p>
                    </div
                    `
                resultsTab.append(div)                        
            }
        });
        return data
    }   
}


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
            console.log(key)
            console.log(element)
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
async function newPost(post){
    const response = await fetch(`post/?post=${post}`)
    console.log(response)
    if (response.status === 200){
        const divContainer = document.getElementById('display-posts')
        const newPost = document.createElement('div')
        const time = Date.now();
        const date = new Date(time);
        const currentDate = date.toString();

        newPost.innerHTML = 
            `
                <h3>Book Title</h3>
                <p>${post}</p>
                <p><em>Stoyan Kolev</em> ${currentDate}</p>
            `
        divContainer.append(newPost)
    }

}