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

      const resultEntries = document.querySelectorAll(".displayEntry");
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
          if (element1.style.display === "block") {
            element1.id = "";
            resultArray.forEach((element2) => {
              element2.style.display = "flex";
            });
          } else {
            element1.style.display = "block";
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
        var bookData = getBookIsbn();
        bookData.review = review;
        bookData.date_read = date;
        console.log(bookData)
        saveReview(bookData);
      }
    };
  };
});

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
  div.className = "displayEntry";
  div.innerHTML = `
        <div id='entryThumbnail'>
            <img id='book-thumbnail' src=${element.thumbnail}>
        </div>
        <div id='entryDetails'>
            <h2 id='book-title' data-isbn='${element.isbn}'>${element.title}</h2>
            <h4>by <a href='' id='author-link'>${element.authors}</a></h4>
            <p id='book-description'>${element.description}</p>
            <p>${element.pageCount}</p>
        </div
        `;
  return div;
}

function getBookIsbn() {
  const selectedBook = document.getElementById("picked");
  const bookIsbn = selectedBook.querySelector("#book-title").dataset.isbn;
  const bookData = {
    bookIsbn
  }
  return bookData;
}


function saveReview(data) {
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
  fetch(`/new`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(data),
  })  
  .then(response => {
    if (response.ok) {
      window.location.href = '/home';
    }
  })
};

