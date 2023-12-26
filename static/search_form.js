window.addEventListener('DOMContentLoaded', () => {
    displayPosts()
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
async function displayPosts(){
    const response = await fetch(`/get_reviews`)
    const data = await response.json()
    const divContainer = document.getElementById('display-posts')
    data.forEach((element) => {
        console.log(element)
        const newReview = document.createElement('div')
        newReview.innerHTML = 
            `
                <img src=${element[7]}>
                <h5>Review of ${element[5]}</h5> 
                <p>by ${element[6]}<p>

                <p>${element[1]}</p>
                <p><em>Stoyan Kolev</em> ${element[3]}</p>
            `
        divContainer.append(newReview)            
    })

}
