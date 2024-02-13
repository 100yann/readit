document.addEventListener('DOMContentLoaded', () => {
    const writeReview = document.getElementById('write-new-review')
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
})


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
    fetch(`/new`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(data),
    })  
};
  