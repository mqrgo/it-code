from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q, Min, Max, Avg, Count, F, Sum
from models_and_fields import models


def index(request):
    #Base
    base_all_authors = models.Author.objects.all()
    base_fltr = models.Author.objects.filter(first_name='Юрий')
    base_excld = models.Author.objects.exclude(first_name='Юрий')
    base_fltr_and_excld = models.Author.objects.filter(first_name='Юрий').exclude(birthday__year=1920)
    base_exists = models.Author.objects.filter(first_name='Юрий').exists()
    base_get = models.Author.objects.get(first_name='Юрий')

    #Limitation
    limit = models.Author.objects.all()[:4]
    limit_offset = models.Author.objects.all()[5:10]
    each_second = models.Author.objects.all()[10:30:2]
    first_author = models.Author.objects.first()
    last_author = models.Author.objects.last()
    ordered = models.Author.objects.order_by('-first_name')

    #Search by fields
    lte = models.Author.objects.filter(birthday__month__lte=5)
    gte = models.Author.objects.filter(birthday__month__gte=5)
    lt = models.Author.objects.filter(birthday__month__lt=5)
    gt = models.Author.objects.filter(birthday__month__gt=5)
    exact = models.Author.objects.filter(first_name__exact='Лев')
    iexact = models.Author.objects.filter(first_name__iexact='Лев')
    contains = models.Author.objects.filter(first_name__contains='ий')
    icontains = models.Author.objects.filter(first_name__icontains='ий')
    startswith = models.Author.objects.filter(first_name__startswith='Л')
    istartswith = models.Author.objects.filter(first_name__istartswith='л')
    endswith = models.Author.objects.filter(first_name__endswith='й')
    iendswith = models.Author.objects.filter(first_name__iendswith='Й')

    #Search that uses relationships
    quote = models.Quote.objects.filter(author__firts_name='Юрий')
    author_with_no_desc = models.Book.objects.filter(author__description__isnull=True)

    #Q F Min Max Sum Count Avg
    authors_name_or_lastname = models.Author.objects.filter(Q(first_name="Лев") | Q(last_name="Толстой"))
    authors_name_not_lastname = models.Author.objects.filter(Q(first_name="Юрий") & ~Q(last_name="Никонов"))
    min_rating = models.Author.objects.aggregate(Min('total_rating'))
    max_rating = models.Author.objects.aggregate(Max('total_rating'))
    average_age = models.Author.objects.aggregate(Avg('age'))
    high_rating_authors_count = models.Author.objects.filter(total_rating__gt=8).aggregate(Count('id'))
    total_age_sum = models.Author.objects.aggregate(Sum('age'))

    return HttpResponse(f'{icontains}')
