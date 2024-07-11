def get_upload_book_path(instance, filename):
    return f'books/{instance.author.slug}/{instance.title}'