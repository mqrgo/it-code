from django.db import models
from django.core.validators import MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from slugify import slugify
from .datatools import get_upload_book_cover_path
from .consts import PublishedStatus


class PublishedBookManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=PublishedStatus.PUBLISHED)


class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    first_name = models.CharField('Имя', max_length=255)
    last_name = models.CharField('Фамилия', max_length=255)
    middle_name = models.CharField('Отчество', max_length=255, null=True, blank=True)
    photo = models.ImageField('Фото', upload_to='authors/', null=True, blank=True)
    birthday = models.DateField('Дата рождения')
    age = models.PositiveSmallIntegerField(
        'Возраст',
        editable=False,
        validators=[MaxValueValidator(120)],
        null=True,
        blank=True,
    )
    description = models.TextField('Описание', null=True, blank=True)
    still_alive = models.BooleanField('Жив', default=True)
    total_rating = models.FloatField('Рейтинг', null=True, blank=True, editable=False)
    slug = models.SlugField('Слаг', editable=False, unique=True)


    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ['first_name', 'last_name', 'middle_name']
        unique_together = ['first_name', 'last_name', 'middle_name', 'birthday']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def clean(self):
        if self.birthday >= timezone.now().date():
            raise ValidationError('Автор не может быть рожден сегодня или в будущем времени')

    def save(self, *args, **kwargs):
        self.clean()
        self.slug = slugify(f'{self.first_name}-{self.last_name}-{self.middle_name}-{self.birthday}')
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name} {self.middle_name}'

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('authors', args=[
            self.slug
        ])


class Book(models.Model):
    book_id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        related_name='book',
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField('Genre', related_name='books', related_query_name='book')
    title = models.CharField('Название', max_length=255)
    total_rating = models.FloatField('Рейтинг', null=True, blank=True, editable=False)
    slug = models.SlugField('Слаг', editable=False)
    cover = models.ImageField('Обложка', upload_to=get_upload_book_cover_path)
    published = models.DateField('Дата публикации')
    description = models.TextField('Описание', null=True, blank=True)
    status = models.CharField(
        'Статус книги',
        max_length=255,
        choices=PublishedStatus.CHOICES,
        default=PublishedStatus.PUBLISHED,
    )

    publish = PublishedBookManager()
    object = models.Manager()

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def save(self, *args, **kwargs):
        self.slug = slugify(f'{self.title}')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Genre(models.Model):
    title = models.CharField('Жанр', max_length=255)
    slug = models.SlugField('Слаг', editable=False)
    description = models.TextField('Описание', null=True, blank=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(f'{self.title}')
        super().save(*args, **kwargs)
