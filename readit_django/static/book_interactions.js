var icons = {
    'Favorites': '<i class="fa-solid fa-star" id="#bookmark-icon"></i>',
    'Read': '<i class="fa-solid fa-book id="#bookmark-icon""></i>',
}
var defaultIcon = '<i id="bookmark-icon" class="fa-solid fa-bookmark fa-fw"></i>'


document.addEventListener('DOMContentLoaded', () => {
    const writeReview = document.getElementById('write-new-review')

    if (writeReview){
      writeReview.onclick = () => {
          const form = document.getElementById('review-form')
          form.style.display = 'block';
          form.addEventListener('submit', (event) => {
              event.preventDefault()
              const date = document.getElementById("date-field").value;
              const review = document.getElementById("review-field").value;
              if (date && review) {
                var data = getBookInfo();
                data.review = review;
                data.date_read = date;
        
                saveReview(data);
              }
          })
      }
    }

    // Add book to bookshelf
    const bookStatus = document.getElementById('add-to-bookshelf')

    if (icons.hasOwnProperty(bookStatus.textContent)) {
        bookStatus.innerHTML = `${icons[bookStatus.textContent]}${bookStatus.textContent}`
    } else {
        bookStatus.innerHTML = `${defaultIcon}${bookStatus.textContent}`
    }
    
    bookStatus.onclick = async () => {
        const status = await saveBookToBookshelf(bookStatus.textContent)
        updateShelfButtonText(bookStatus.textContent, status)
    }

    // Custom shelves dropdown
    const dropdownButton = document.getElementById('custom-shelves')
    dropdownButton.onclick = () => {
        displayDropdownMenu()
    }


    // Rating
    var stars = document.querySelectorAll('.rating-stars');
    
    // If a user has rated the book - fill the appropriate number of stars
    var userRating = document.querySelector('#rating-section').dataset['rating']
    stars.forEach((element, index) => {
        if (index <= userRating-1) {
            element.style.color = '#ff764c'
        }
    })

    var rated = false;
    var rating = 0;

    stars.forEach((element, index) => {
        element.addEventListener('mouseover', () => {
                stars.forEach((element2, index2) => {
                    if (index2 <= index) {
                        element2.style.color = '#ff764c'
                    } else {
                        element2.style.color = ''
                    }
                })
            }
        )

        element.addEventListener('click', () => {
            rated = true
            rating = index + 1;
            rateBook(rating)
            stars.forEach((element2, index2) => {
                if (index2 <= index) {
                    element2.style.color = '#ff764c'
                } else {
                    element2.style.color = ''
                }
            })
        })

        element.addEventListener('mouseleave', () => {
            if (!rated) {
                stars.forEach((element2, index3) => {
                    if (!userRating || index3 > userRating - 1) {
                        element2.style.color = ''
                    } else {
                        element2.style.color = '#ff764c'
                    }
                })
            }
        })
    })
});


function getBookInfo() {
    bookData = {
      bookTitle: document.querySelector("#book-title").textContent,
      bookIsbn: document.querySelector("#book-title").dataset.isbn,
      bookId: document.querySelector('#book-title').dataset.id,
      bookAuthor: document.querySelector("#author").textContent,
      bookThumbnail: document.querySelector("#book-thumbnail").src,
    };
  
    return bookData;
};
  

async function saveBookToBookshelf(bookshelf) {
    const bookIsbn = getBookInfo().bookIsbn
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    response = await fetch(`http://127.0.0.1:8000/book/save`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({'isbn': bookIsbn, 'bookshelf': bookshelf}),
            })

    if (!response.ok) {
        throw new Error('Failed to save book to bookshelf')
    }

    return response.status
};


async function displayDropdownMenu() {
    const userBookshelves = ['Read', 'Favorites', 'Gibberish']
    const dropdownMenu = document.getElementById('dropdown-menu')
    dropdownMenu.classList.toggle('hidden')
    if (dropdownMenu.classList.contains('hidden')){
        dropdownMenu.innerHTML = ""
        dropdownMenu.style.display = 'none'
        return
    }
    userBookshelves.forEach((shelf) => {
        const shelfButton = document.createElement('button')
        shelfButton.textContent = shelf
        shelfButton.onclick = async () => {
            var status = await saveBookToBookshelf(shelf)
            updateShelfButtonText(shelf, status)
        }
        dropdownMenu.append(shelfButton)
    })

    const newShelfButton = document.createElement('button')
    newShelfButton.id = 'new-custom-shelf'
    newShelfButton.textContent = '+'
    dropdownMenu.append(newShelfButton)

    newShelfButton.onclick = () => {
        const newCustomShelf = document.createElement('form')
        newCustomShelf.innerHTML = '<input type="text" placeholder="New shelf"></input><input type="submit" text="Save"></input'
        dropdownMenu.append(newCustomShelf)
    }
    dropdownMenu.style.display = 'block'
}


function rateBook(rating) {
  const bookId = getBookInfo().bookId
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  respone = fetch(`http://127.0.0.1:8000/book/rate`, {
    method: 'POST',
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({'rating': rating, 'book_id': bookId})
  })
}


function updateShelfButtonText(shelf, status) {
    const icon = document.querySelector('#bookmark-icon')
    const buttonParent = document.getElementById('shelve-button-container')
    const buttonText = document.getElementById('add-to-bookshelf')

    if (icons.hasOwnProperty(shelf)) {
        buttonText.innerHTML = `${icons[shelf]}${shelf}`
    } else {
        buttonText.innerHTML = `${defaultIcon}${shelf}`
    }

    if (status == 204) {
        buttonParent.classList.remove('shelved')
        // icon.classList.remove('fa-solid')
        // icon.classList.add('fa-regular')
    } else {
        buttonParent.classList.add('shelved')
        // icon.classList.remove('fa-regular')
        // icon.classList.add('fa-solid')
    }

}