document.addEventListener('DOMContentLoaded', () => {
    const bookSearchField = document.getElementById('review-book-field')
    const bookForm = document.getElementById('book-form')
    const buttonNext = document.getElementById('next-button')
    buttonNext.style.display = 'none'

    bookForm.onsubmit = async (event) => {
        event.preventDefault()
        const searchValue = bookSearchField.value

        // Check if there is any search input
        if (searchValue){
            // Display the results on the page
            const results = await displaySearchResults(searchValue)

            const resultEntries = document.querySelectorAll('#entryThumbnail')
            const resultArray = Array.from(resultEntries)

            resultEntries.forEach((element1) => {
                
                // On click of a book entry hide all the other entries
                // and display only the clicked entry
                element1.onclick = () => {

                    if (buttonNext.style.display === 'none'){
                        buttonNext.style.display = 'block'
                    } else {
                        buttonNext.style.display = 'none'
                    }
                    resultEntries.forEach((element2) => {
                        // Hide other entries
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
        const resultsTab = document.getElementById('display-results')
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
