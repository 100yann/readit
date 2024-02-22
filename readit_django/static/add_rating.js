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
        bookStatus.innerHTML = '<i id="not-bookmarked" class="fa-regular fa-bookmark fa-fw"></i>Want to read'
    } else {
        bookStatus.style.backgroundColor = '#BFEAAA'
        bookStatus.innerHTML = `<i id="bookmarked" class="fa-solid fa-bookmark fa-fw"></i>${bookStatus.dataset['status']}`

    }

    bookStatus.onclick = () => {
        // if the book hasn't been saved by the user
        if (bookStatus.dataset['status'] == '') {
            // animate button from grey to green
            animateElement(bookStatus, 'change-button-color', '0.2s', 'forwards')
            bookStatus.dataset['status'] = 'Want to read';

            // animate the regular bookmark 
            animateElement(document.querySelector('#not-bookmarked'), 'pop-up', '0.1s', 'forwards')

            // replace the regular bookmark with a solid bookmark and animate it into place
            bookStatus.innerHTML = `<i id="bookmarked" class="fa-solid fa-bookmark fa-fw"></i>${bookStatus.dataset['status']}`;
            animateElement(document.querySelector('#bookmarked'), 'pop-up', '0.1s', 'reverse')
            saveReview({'action': 'save_book'})
        } else {
            // if user has the book saved
            // change the button color from green to grey
            animateElement(bookStatus, 'change-button-color', '0.2s', 'reverse')
            bookStatus.style.backgroundColor = ''
            bookStatus.dataset['status'] = '';

            animateElement(document.querySelector('#bookmarked'), 'pop-up', '0.1s', 'forwards')

            bookStatus.innerHTML = `<i id="not-bookmarked" class="fa-regular fa-bookmark fa-fw"></i>Want to read`;
            
            animateElement(document.querySelector('#not-bookmarked'), 'pop-up', '0.1s', 'reverse')
            saveReview({'action': 'remove_book'})
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
  

function saveReview(data) {
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



function animateElement(element, animationName, duration, direction){
    element.style.animation = `${animationName} ${duration} ${direction}`
}