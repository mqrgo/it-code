from django.db import models
from django.core.validators import MaxValueValidator
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from slugify import slugify
from .datatools import get_upload_book_path
from .consts import PublishedStatus


class PublishedBookManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=PublishedStatus.PUBLISHED)


class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    first_name = models.CharField('Имя', max_length=255)
    last_name = models.CharField('Фамилия', max_length=255)
    middle_name = models.CharField(
        'Отчество',
        max_length=255,
        null=True,
        blank=True,
        db_column='surname',
        db_comment='Some info for comment'
    )
    birthday = models.DateField('Дата рождения')
    age = models.PositiveSmallIntegerField(
        'Возраст',
        editable=False,
        validators=[MaxValueValidator(120)],
        null=True,
        blank=True,
    )
    description = models.TextField('Описание', null=True, blank=True)
    slug = models.SlugField('Слаг', editable=False, unique=True)

    class Meta:
        abstract = True
        ordering = ['first_name', 'last_name', 'middle_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name} {self.middle_name}'

    def save(self, *args, **kwargs):
        self.clean()
        self.slug = slugify(f'{self.first_name}-{self.last_name}-{self.middle_name}-{self.birthday}')
        super().save(*args, **kwargs)


class Author(Person):
    photo = models.ImageField('Фото', upload_to='authors/photo', null=True, blank=True)
    still_alive = models.BooleanField('Жив', default=True)
    total_rating = models.FloatField('Рейтинг', null=True, blank=True, editable=False)

    class Meta(Person.Meta):
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        db_table_comment = 'В таблицу вносятся только великие авторы'
        get_latest_by = ['total_rating']
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name', 'middle_name', 'birthday'], name='unique_person'
            )
        ]

    def clean(self):
        if self.birthday >= timezone.now().date():
            raise ValidationError('Автор не может быть рожден сегодня или в будущем времени')

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('authors', args=[
            self.slug
        ])


class BookReviewer(Person):
    photo = models.ImageField('Фото', upload_to='book_reviewer/', null=True, blank=True)
    book_publishing_house = models.CharField('Издательство', max_length=255)

    class Meta(Person.Meta):
        verbose_name = 'Книжный обозреватель'
        verbose_name_plural = 'Книжные обозреватели'


class Quote(models.Model):
    quote = models.CharField('Цитата', max_length=255)
    author = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='quote')

    class Meta:
        ordering = ['quote']
        verbose_name = 'Цитата'
        verbose_name_plural = 'Цитаты'

    def __str__(self):
        return self.quote


class Book(models.Model):
    book_id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        related_name='book',
        null=True,
        blank=True,
        verbose_name='Автор',
    )
    genre = models.ManyToManyField(
        'Genre',
        related_name='books',
        related_query_name='book',
        verbose_name='Жанр',
        through='AboutGenre',
    )
    title = models.CharField('Название', max_length=255, unique_for_year='published')
    total_rating = models.FloatField('Рейтинг', null=True, blank=True, editable=False)
    slug = models.SlugField('Слаг', editable=False)
    cover = models.ImageField('Обложка', upload_to=get_upload_book_path)
    published = models.DateField('Дата публикации')
    description = models.TextField('Описание', null=True, blank=True)
    status = models.CharField(
        'Статус книги',
        max_length=255,
        choices=PublishedStatus.CHOICES,
        default=PublishedStatus.PUBLISHED,
    )
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    book_file = models.FileField('Книга', upload_to=get_upload_book_path)

    publish = PublishedBookManager()
    object = models.Manager()

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']
        constraints = [
            models.CheckConstraint(
                check=Q(price__gt=0), name='price_positive'
            )
        ]

    def save(self, *args, **kwargs):
        self.slug = slugify(f'{self.title}')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Genre(models.Model):
    title = models.CharField('Жанр', max_length=255)
    slug = models.SlugField('Слаг', editable=False)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(f'{self.title}')
        super().save(*args, **kwargs)


class ProxyBookLogic(Book):
    class Meta:
        proxy = True

    def get_price_with_discount(self, discount: int):
        return self.price - (self.price * discount//100)


class AboutGenre(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        related_name='about_genre',
        null=True,
        blank=True,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        related_name='about_genre',
        null=True,
        blank=True,
    )
    date_found = models.DateField('Дата образования')
    description = models.TextField('Описание жанра')

    class Meta:
        verbose_name = 'О жанре'
        verbose_name_plural = 'О жанрах'

    def __str__(self):
        return f'{self.genre.title} - {self.date_found}'