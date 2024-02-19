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
    const bookStatus = document.getElementById('add-to-books-list')

    if (bookStatus.dataset['status'] == '') {
        bookStatus.textContent = 'Want to read'
    } else {
        bookStatus.style.backgroundColor = 'green'
        bookStatus.textContent = bookStatus.dataset['status']

    }

    bookStatus.onclick = () => {
        if (bookStatus.dataset['status'] == '')
        {
            bookStatus.style.backgroundColor = 'green'
            bookStatus.dataset['status'] = 'Want to read'
            saveReview({'action': 'save_book'})
        } else 
        {
            bookStatus.style.backgroundColor = 'gray'
            bookStatus.dataset['status'] = ''
            saveReview({'action': 'remove_book'})
        }
    }

    var stars = document.querySelectorAll('.fa-star');
    var userRating = document.querySelector('#rating-section').dataset['rating']
    stars.forEach((element, index) => {
        if (index <= userRating-1) {
            element.style.color = 'yellow'
        }
    })

    var rated = false;
    var rating = 0;

    stars.forEach((element, index) => {
        element.addEventListener('mouseover', () => {
                stars.forEach((element2, index2) => {
                    if (index2 <= index) {
                        element2.style.color = 'yellow'
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
                    element2.style.color = 'yellow'
                } else {
                    element2.style.color = ''
                }
            })
        })

        element.addEventListener('mouseleave', () => {
            if (!rated) {
                stars.forEach((element2) => {
                    element2.style.color = ''
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
  

function saveReview(data) {
    console.log(data)
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    fetch(``, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(data),
    })  
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