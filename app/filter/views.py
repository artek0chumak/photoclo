import re

import maya
from natasha import DatesExtractor
from photo_load.models import Photo
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT
)
from rest_framework.viewsets import ViewSet

from .parser import rel_date_parser

year_regexp = re.compile(r'[\d]{2,4}')
month_year_regexp = re.compile(r'[\d]{1,2}(\.|\s)[\d]{2,4}')
full_date_regexp = re.compile(r'([\d]{1,2}(\.|\s)){2}[\d]{2,4}')
natasha_extractor = DatesExtractor()


def exact_day(field, photos):
    day, month, year = 0, 0, 0
    now = maya.now()

    result = natasha_extractor(field)
    if len(result) == 0:
        if year_regexp.match(field):
            year = int(year_regexp.findall(field)[0])
        elif month_year_regexp.match(field):
            month, year = map(int, re.findall(r'[\d]+', field))
        elif full_date_regexp.match(field):
            day, month, year = map(int, re.findall(r'[\d]+', field))
        elif field.find('сегодня') != -1:
            return photos.filter(photoinfo__time_created__date=now.date)
        elif field.find('вчера') != -1:
            now = now.subtract(days=1)
            return photos.filter(photoinfo__time_created__date=now.date)
        else:
            return photos.filter(face__avatar__name=field.strip)

    fact = result[0].fact
    day = fact.day if fact.day else 0
    month = fact.month if fact.month else 0
    year = fact.year if fact.year else 0

    if field.find('до') != -1:
        if day > 0:
            photos = photos.filter(photoinfo__time_created__day__lte=day)
        if month > 0:
            photos = photos.filter(photoinfo__time_created__month__lte=month)
        if year > 0:
            photos = photos.filter(photoinfo__time_created__year__lte=year)
    elif field.find('после') != -1:
        if day > 0:
            photos = photos.filter(photoinfo__time_created__day__gte=day)
        if month > 0:
            photos = photos.filter(photoinfo__time_created__month__gte=month)
        if year > 0:
            photos = photos.filter(photoinfo__time_created__year__gte=year)
    else:
        if day > 0:
            photos = photos.filter(photoinfo__time_created__day=day)
        if month > 0:
            photos = photos.filter(photoinfo__time_created__month=month)
        if year > 0:
            photos = photos.filter(photoinfo__time_created__year=year)

    return photos


def rel_day(field, photos):
    result = next(rel_date_parser.findall(field)).fact
    days = int(result.relDay) if result.relDay else 0
    weeks = int(result.relWeek) if result.relWeek else 0
    months = int(result.relMonth) if result.relMonth else 0
    years = int(result.relYear) if result.relYear else 0

    date = maya.now().subtract(days=days, weeks=weeks, months=months,
                                years=years)

    if field.find('до') != -1:
        photos = photos.filter(photoinfo__time_created__lte=date.date)
    else:
        photos = photos.filter(photoinfo__time_created__gte=date.date)

    return photos


class FinderView(ViewSet):
    def list(self, request, pk=None):
        field = request.query_params['query']
        size = request.query_params['size']
        photos = Photo.objects.filter(owner=request.user)

        if len(list(rel_date_parser.findall(field))) != 0:
            photos = rel_day(field, photos)
        else:
            photos = exact_day(field, photos)

        if len(photos) == 0:
            return Response(status=HTTP_204_NO_CONTENT)

        client_photos = [{'url': getattr(photo, '{0}_size'.format(size)).url,
                          'height': photo.photoinfo.height,
                          'width': photo.photoinfo.width,
                          'id': photo.id} for photo in photos.order_by('id')]

        return Response({'photos': client_photos}, status=HTTP_200_OK)
