window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-form')
    
    form.onsubmit = async (event) =>{
        const searchValue = document.getElementById('search').value
        event.preventDefault()

        if (searchValue){
            window.location = `/find?search=${searchValue}`     
        }
    }
})