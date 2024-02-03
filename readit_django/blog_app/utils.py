import requests
from django.http import JsonResponse


def get_books_by_title(title):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': title
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        return JsonResponse({'error': 'Failed to fetch books'}, status=response.status_code)


def format_results(results):
    formatted_results = []
    fields = ['title', 'authors', 'thumbnail', 'publisher', 'description', 'pageCount', 'categories', 'isbn']
    for result in results:
        if 'volumeInfo' in result and 'imageLinks' in result['volumeInfo']:
            curr = {}
            for field in fields:
                try:
                    if field == 'thumbnail':
                        curr[field] = result['volumeInfo']['imageLinks']['thumbnail']
                    elif field == 'isbn':
                        curr[field] = result['volumeInfo']['industryIdentifiers'][0]['identifier']
                    else:
                        curr[field] = result['volumeInfo'][field]
                except KeyError:
                    pass

            formatted_results.append(curr)
    return formatted_results

def get_book_by_isbn(isbn, preview=False):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f'isbn:{isbn}'
    }
    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch books'}, status=response.status_code)
    
    data = response.json()
    book = data.get("items", [])

    if not book:
        return JsonResponse({'error': 'No book found'}, status=response.status_code)
    
    book_info = book[0]['volumeInfo']

    filtered_data = {
        'title': book_info['title'],
        'thumbnail': book_info['imageLinks']['thumbnail']
    }

    if len(book_info['authors']) == 1:
        filtered_data['author'] = book_info['authors'][0]
    else:
        authors = ''
        index = 0
        for author in book_info['authors']:
            authors += author 
            if not index == len(book_info['authors']) - 1:
                authors += ', '
            index += 1

        filtered_data['author'] = authors

    if not preview:
        additional_data = [
            'subtitle',
            'publisher',
            'publishedDate',
            'description',
            'pageCount',
            'categories',
            ]

        for field in additional_data:
            filtered_data[field] = book_info[field]
    
    return filtered_data