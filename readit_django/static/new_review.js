document.addEventListener("DOMContentLoaded", () => {

  const bookForm = document.getElementById("book-form");
  const reviewForm = document.getElementById("review-form");

  const bookSearchField = document.getElementById("review-book-field");
  const buttonNext = document.getElementById("next-button");
  buttonNext.style.display = "none";

  bookForm.onsubmit = async (event) => {
    
    event.preventDefault();
    const searchValue = bookSearchField.value;
    // Check if there is any search input
    if (searchValue) {
      // Display the results on the page
      const results = await displaySearchResults(searchValue);

      const resultEntries = document.querySelectorAll(".book-result");
      const resultArray = Array.from(resultEntries);

      resultEntries.forEach((element1) => {
        // On click of a book entry hide all the other entries
        // and display only the clicked entry
        element1.onclick = () => {
          if (buttonNext.style.display === "none") {
            buttonNext.style.display = "block";
          } else {
            buttonNext.style.display = "none";
          }
          resultEntries.forEach((element2) => {
            // Hide other entries
            if (element1 != element2) {
              element2.style.display = "none";
            }
          });
          // If currently only one entry is displayed and it's
          // clicked again - show all entries again
          if (element1.id === "picked") {
            element1.id = "";
            resultArray.forEach((element2) => {
              element2.style.display = "flex";
            });
          } else {
            element1.style.display = "flex";
            element1.id = "picked";
          }
        };
      });
    }
  };

  buttonNext.onclick = () => {
    bookForm.style.display = "none";
    document.getElementById("display-results").style.display = "none";
    buttonNext.style.display = "none";
    reviewForm.style.display = "block";

    reviewForm.onsubmit = (event) => {
      event.preventDefault();
      const date = document.getElementById("date-field").value;
      const review = document.getElementById("review-field").value;
      if (date && review) {
        var bookData = getBookInfo();
        var reviewData = {
          content: review,
          date_read: date
        }

        saveReview(bookData, reviewData);
      }
    };
  };
})

// Display books returned by the Google API
async function displaySearchResults(searchValue) {
  // fetch the results
  const response = await fetch(`/find/${searchValue}`);
  const data = await response.json();

  if (data) {
    // display the results tab where all results will be displayed
    const resultsTab = document.getElementById("display-results");
    resultsTab.innerHTML = "";
    resultsTab.style.display = "block";

    data.forEach((element) => {
      resultsTab.append(createEntry(element));
    });
    return data;
  }
}

function createEntry(element) {
  let div = document.createElement("div");
  div.className = "book-result";
  div.innerHTML = `
        <div>
            <img id='result-thumbnail' src=${element.thumbnail}>
        </div>
        <div id='result-details'>
            <h3 id='book-title' data-isbn='${element.isbn}'>${element.title}</h3>
            <h5>by <a href='' id='author-link'>${element.authors}</a></h5>
            <p>Genres: ${ element.categories }</p>
            <div id="book-additional-info">
              <div>
                  <p class="book-info-label">Publisher</p>
                  <p class="book-info-value">${ element.publisher }</p>
              </div>
              <div>
                  <p class="book-info-label">Pages</p>
                  <p class="book-info-value">${ element.pageCount }</p>
              </div>
            </div>
        </div>
        `;
  return div;
}

function getBookInfo() {
  const selectedBook = document.getElementById("picked");
  bookData = {
    title: selectedBook.querySelector("#book-title").textContent,
    author: selectedBook.querySelector("#author-link").textContent,
    isbn: selectedBook.querySelector("#book-title").dataset.isbn,
    thumbnail: selectedBook.querySelector("#book-thumbnail").src,
  };

  return bookData;
};

function saveReview(bookData, reviewData) {
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
  const requestBody = {
    review: reviewData,
    book: bookData
  };

  fetch(`/new`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(requestBody),
  })  
  .then(response => {
    if (response.ok) {
      // window.location.href = '/home';
      console.log('ok')
    } else {
      window.location.href = '/user/logout'
      console.log('not ok')
    }
  }).then((data) => {
    console.log(data)
  })
};

