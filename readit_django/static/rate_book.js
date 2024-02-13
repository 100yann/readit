document.addEventListener('DOMContentLoaded', () => {
    var stars = document.querySelectorAll('.fa-star');
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
