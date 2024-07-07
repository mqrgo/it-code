def get_upload_book_cover_path(instance, filename):
    return f'books/{instance.author.slug}/{instance.title}'