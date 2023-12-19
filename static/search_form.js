window.addEventListener('DOMContentLoaded', () => {

    const post = document.getElementById('post-form')
    post.onsubmit = async (event) => {
        event.preventDefault()
        const postValue = document.getElementById('post-value')

        if (postValue.value){
            newPost(postValue.value)
        }
    }    
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