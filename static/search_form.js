window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-form')
    
    form.onsubmit = async (event) => {
        event.preventDefault()
        const searchValue = document.getElementById('search').value

        // Check if there is any search input
        if (searchValue){
            // Display the results on the page
            const results = await displaySearchResults(searchValue)

            const resultEntries = document.getElementsByClassName('displayEntry')
            const resultArray = Array.from(resultEntries)
            resultArray.forEach((element1) => {
                // On click of a book entry hide all the other entries
                // and display only the clicked entry
                element1.onclick = () => {
                    resultArray.forEach((element2) => {
                        if (element1 != element2){
                            element2.style.display = 'none'
                        }
                    })
                    // If currently only one entry is displayed and it's
                    // clicked again - show all entries again
                    if (element1.style.display === 'block') {
                        resultArray.forEach((element2) => {
                            element2.style.display = 'flex';
                        });
                    } else {
                        element1.style.display = 'block';
                    }
                }
            })

            const authorLinks = document.querySelectorAll('#author-link')
            console.log(authorLinks)
            authorLinks.forEach((element) => {
                element.onclick = (event) => {
                    event.preventDefault()
                    const response = fetch(`/author?author=${element.textContent}`)
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
