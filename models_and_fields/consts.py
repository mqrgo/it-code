class PublishedStatus:
    PUBLISHED = 'Published'
    IN_PROGRESS = 'IN PROGRESS'

    PUBLISHED_RUS = 'Опубликована'
    IN_PROGRESS_RUS = 'В процессе написания'

    CHOICES = (
        (PUBLISHED, PUBLISHED_RUS),
        (IN_PROGRESS, IN_PROGRESS_RUS),
    )


