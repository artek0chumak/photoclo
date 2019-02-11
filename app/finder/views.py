import re

from natasha import DatesExtractor
from photo_load.models import Photo
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT
)
from rest_framework.viewsets import ViewSet

year_regexp = re.compile(r'[\d]{2,4}')
month_year_regexp = re.compile(r'[\d]{1,2}(\.|\s)[\d]{2,4}')
full_date_regexp = re.compile(r'([\d]{1,2}(\.|\s)){2}[\d]{2,4}')
natasha_extractor = DatesExtractor()


class FinderView(ViewSet):
    def list(self, request, pk=None):
        field = request.query_params['query']
        size = request.query_params['size']
        photos = Photo.objects.filter(owner=request.user)
        day, month, year = 0, 0, 0

        result = natasha_extractor(field)
        if len(result) == 0:
            if year_regexp.match(field):
                year = int(year_regexp.findall(field)[0])
            elif month_year_regexp.match(field):
                month, year = map(int, re.findall(r'[\d]+', field))
            elif full_date_regexp.match(field):
                day, month, year = map(int, re.findall(r'[\d]+', field))
            else:
                photos = photos.filter(face__avatar__name=field.strip)
        else:
            fact = result[0].fact
            day = fact.day if fact.day else 0
            month = fact.month if fact.month else 0
            year = fact.year if fact.year else 0

        if day > 0:
            photos = photos.filter(photoinfo__time_created__day=day)
        if month > 0:
            photos = photos.filter(photoinfo__time_created__month=month)
        if year > 0:
            photos = photos.filter(photoinfo__time_created__year=year)

        if len(photos) == 0:
            return Response(status=HTTP_204_NO_CONTENT)

        client_photos = [{'url': getattr(photo, '{0}_size'.format(size)).url,
                          'height': photo.photoinfo.height,
                          'width': photo.photoinfo.width,
                          'id': photo.id} for photo in photos]

        return Response({'photos': client_photos}, status=HTTP_200_OK)
