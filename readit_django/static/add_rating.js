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

    bookStatus.onclick = async () => {
        const shelveButton = await saveBookToBookshelf('Want to read')
        const icon = bookStatus.querySelector('#bookmark-icon')
        const buttonParent = document.getElementById('shelve-button-container')
        if (shelveButton === 'active') {
            buttonParent.classList.add('shelved')
            icon.classList.remove('fa-regular')
            icon.classList.add('fa-solid')
        } else {
            buttonParent.classList.remove('shelved')
            icon.classList.remove('fa-solid')
            icon.classList.add('fa-regular')
        }
    }

    var stars = document.querySelectorAll('.fa-star');
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
            saveRating(rating)
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
      bookAuthor: document.querySelector("#author").textContent,
      bookIsbn: document.querySelector("#book-title").dataset.isbn,
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

    const data = await response.json()
    const shelveButton = data.status

    return shelveButton
};


function saveRating(rating) {
  const bookIsbn = document.querySelector("#book-title").dataset.isbn
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  respone = fetch(``, {
    method: 'POST',
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({'rating': rating, 'action': 'rate'})
  })
}
