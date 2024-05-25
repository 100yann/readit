
const FASTAPI_URL = 'http://127.0.0.1:8000'
var icons = {
    'Favorites': '<i class="fa-solid fa-star" id="#bookmark-icon"></i>',
    'Read': '<i class="fa-solid fa-book id="#bookmark-icon""></i>',
}
var defaultIcon = '<i id="bookmark-icon" class="fa-solid fa-bookmark fa-fw"></i>'
var page = 1

document.addEventListener('DOMContentLoaded', () => {
    getReviews()
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
        displayDropdownMenu(bookStatus.textContent)
    }


    // Rating
    var stars = document.querySelectorAll('.rating-stars');
    
    // If a user has rated the book - fill the appropriate number of stars
    var userRating = document.querySelector('#rating-section').dataset['rating']
    stars.forEach((star, index) => {
        if (userRating && index <= userRating-1) {
            star.style.color = '#ff764c'
        }
        // On hover, highlight all stars up until and including the one hovered
        star.onmouseover = () => {
            stars.forEach((s, i) => {
                if (i <= index){
                    s.style.color = '#ff764c'
                } else {
                    s.style.color = ''
                }
            })
        }
        // On click, highlight all stars up until and including the one clicked
        star.onclick = () => {
            userRating = index + 1
            // Save the rating
            rateBook(userRating)
            stars.forEach((star2, index2) => {
                if (index2 <= index) {
                    star2.style.color = '#ff764c'
                } else {
                    star2.style.color = ''
                }
            })
        }
    })

    const ratingContainer = document.getElementById('rating-container')
    // On mouse leave highlight the amount of stars equal to the user's rating
    ratingContainer.onmouseleave = () => {
        stars.forEach((star, index) => {
            if (userRating && index <= userRating-1){
                star.style.color = '#ff764c'
            } else {
                star.style.color = ''
            }
        })
    }
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
    response = await fetch(`${FASTAPI_URL}/book/save`, {
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


async function displayDropdownMenu(bookshelf) {
    const defaultBookshelves = ['Read', 'Favorites']
    const dropdownMenu = document.getElementById('dropdown-menu')
    var currentUserBookshelves = dropdownMenu.dataset.shelves
    currentUserBookshelves = JSON.parse(currentUserBookshelves.replace(/'/g, '"'));

    dropdownMenu.classList.toggle('hidden')
    if (dropdownMenu.classList.contains('hidden')){
        dropdownMenu.innerHTML = ""
        dropdownMenu.style.display = 'none'
        return
    }
    defaultBookshelves.forEach((shelf) => {
        if (shelf == bookshelf) {
            return
        }
        const shelfButton = document.createElement('button')
        shelfButton.textContent = shelf
        
        if (currentUserBookshelves.includes(shelf)) {
            shelfButton.classList += 'shelved'
        } 
    
        shelfButton.onclick = async () => {
            var status = await saveBookToBookshelf(shelf)
            shelfButton.classList.toggle('shelved')
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

  respone = fetch(`${FASTAPI_URL}/book/rate`, {
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


async function getReviews() {
    const bookId = getBookInfo().bookId
    const response = await fetch(`${FASTAPI_URL}/book/reviews/${bookId}?page=${page}`)
    if (!response.ok){
        return
    }
    const data = await response.json()
    const reviews = data.reviews
    displayReviews(reviews)
}


function displayReviews(reviews) {
    const bookReviewsContainer = document.getElementById('book-reviews');
    const userId = window.userId

    // Clear existing reviews before displaying new ones
    bookReviewsContainer.innerHTML = '';

    reviews.forEach((review) => {
        console.log(review)
        // Create review container
        const reviewContainer = document.createElement('div');
        reviewContainer.id = 'review-container';

        // Create user preview container
        const userPreviewContainer = document.createElement('div');
        userPreviewContainer.id = 'user-preview';

        // Create user profile picture container
        const userProfilePicContainer = document.createElement('div');
        userProfilePicContainer.id = 'user-pfp-container';
        const userProfilePic = document.createElement('img');
        userProfilePic.className = 'user-pfp-preview';
        userProfilePic.src = ''; // Update with the actual URL
        userProfilePic.alt = 'User Profile Picture';
        userProfilePicContainer.appendChild(userProfilePic);
        userPreviewContainer.appendChild(userProfilePicContainer);

        // Create user name container
        const userNameContainer = document.createElement('div');
        userNameContainer.id = 'user-name-container';
        const userName = document.createElement('h5');
        userName.textContent = review.Reviews.owner.email;
        const reviewCount = document.createElement('span');
        reviewCount.textContent = `Placeholder reviews`;
        const followersCount = document.createElement('span');
        followersCount.textContent = `Placeholder followers`;
        userNameContainer.appendChild(userName);
        userNameContainer.appendChild(reviewCount);
        userNameContainer.appendChild(followersCount);
        userPreviewContainer.appendChild(userNameContainer);

        // Append user preview container to review container
        reviewContainer.appendChild(userPreviewContainer);

        // Create review content container
        const reviewContentContainer = document.createElement('div');
        reviewContentContainer.id = 'review-content';
        const reviewDateRating = document.createElement('div');
        reviewDateRating.id = 'review-date-rating';
        const starRating = document.createElement('span');
        // Logic to generate star rating based on review.rating
        // Update this logic based on your rating representation
        starRating.textContent = '☆☆☆☆☆'; // Placeholder for now
        const reviewDate = document.createElement('p');
        reviewDate.textContent = review.Reviews.date_read;
        reviewDateRating.appendChild(starRating);
        reviewDateRating.appendChild(reviewDate);
        reviewContentContainer.appendChild(reviewDateRating);
        const reviewContent = document.createElement('p');
        reviewContent.textContent = review.Reviews.content;
        reviewContentContainer.appendChild(reviewContent);

        // Append review content container to review container
        reviewContainer.appendChild(reviewContentContainer);
        
        // Create a like button
        const likeButton = document.createElement('div')
        var likesAmount = review.total_likes
        if (review.has_user_liked) {
            likeButton.innerHTML = `<i class="fa-solid fa-heart"></i>${likesAmount}`
        } else {
            likeButton.innerHTML = `<i class="fa-regular fa-heart"></i>${likesAmount}`
        }
        reviewContainer.appendChild(likeButton)
        likeButton.onclick = () => {
            likeReview(reviewId=review.Reviews.id)
            .then(likeStatus => {
                if (likeStatus === 'Liked') {
                    likesAmount++
                    likeButton.innerHTML = `<i class="fa-solid fa-heart"></i>${likesAmount}`
                } else {
                    likesAmount--
                    likeButton.innerHTML = `<i class="fa-regular fa-heart"></i>${likesAmount}`
                }
            })
        }
        if (userId == review.Reviews.owner.id) {
            const deleteButton = document.createElement('div')
            deleteButton.innerHTML = '<i class="fa-regular fa-trash-can"></i>'
            reviewContainer.appendChild(deleteButton)
            deleteButton.onclick = () => {
                deleteReview(review.Reviews.id).then(
                    bookReviewsContainer.removeChild(reviewContainer)
                )
            }
        }
        // Append review container to book reviews container
        bookReviewsContainer.appendChild(reviewContainer);
    });
    
    var totalReviews = document.querySelector('.book-total-reviews').textContent
    const numPages = Math.ceil(totalReviews/5)
    for (i=1; i<=numPages; i++){
        const pageButton = document.createElement('button')
        pageButton.textContent = i
        bookReviewsContainer.appendChild(pageButton)
        pageButton.onclick = function() {
            if (page == pageButton.textContent) {
                return
            }
            page = pageButton.textContent
            getReviews()
        }
    }
}


async function likeReview(reviewId) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value

    response = await fetch(`${FASTAPI_URL}/like/${reviewId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        }
    })

    if (!response.ok) {
        throw new Error(`Failed to like review`)
    }

    const data = await response.json()
    const status = data.status
    return status
}


async function deleteReview(reviewId) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value

    response = await fetch(`${FASTAPI_URL}/delete/${reviewId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        }
    })    
    if (!response.ok) {
        throw new Error(`Failed to delete review`)
    }
    return response

}