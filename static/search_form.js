window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-form')
    
    form.onsubmit = async (event) =>{
        const searchValue = document.getElementById('search').value
        event.preventDefault()

        if (searchValue){
            const response = await fetch(`/find?search=${searchValue}`)
            const data = await response.json()
            if (data){
                const resultsTab = document.getElementById('results-tab')
                resultsTab.innerHTML = ''                
                resultsTab.style.display = 'block'

                data.forEach(element => {
                    if ('imageLinks' in element.volumeInfo){
                        let div = document.createElement('div')
                        div.innerHTML = `
                        <div id='displayEntry'>
                            <div id='entryThumbnail'>
                                <img src=${element.volumeInfo.imageLinks.thumbnail}>
                            </div>
                            <div id='entryDetails'>
                                <h2>${element.volumeInfo.title}</h2>
                                <h3>${element.volumeInfo.authors}</h3>
                                <p>${element.volumeInfo.description}</p>
                                <p>${element.volumeInfo.pageCount}</p>
                            </div
                        </div>
                            `
                        resultsTab.append(div)                        
                    }

                });
            }   
        }
    }
})