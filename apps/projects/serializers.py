import logging
logger = logging.getLogger(__name__)

import sys

from django.conf import settings
from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.fields import RelatedField, ManyRelatedField, Field, HyperlinkedIdentityField
from sorl.thumbnail.shortcuts import get_thumbnail

from apps.geo.models import Country
from .models import Project


# TODO move this to utils class
# TODO Think about adding a feature to set thumbnail quality based on country.
#      This would be useful for countries with slow internet connections.
class SorlImageField(Field):

    def __init__(self, source, geometry_string, **options):
        super(SorlImageField, self).__init__(source)
        self.geometry_string = geometry_string
        self.options = options

    def to_native(self, value):
        if not value:
            return ""
        # The get_thumbnail() helper doesn't respect the THUMBNAIL_DEBUG setting
        # so we need to deal with exceptions like is done in the template tag.
        thumbnail = ""
        try:
            thumbnail = unicode(get_thumbnail(value, self.geometry_string, **self.options))
        except Exception:
            if settings.THUMBNAIL_DEBUG:
                raise
            logger.error('Thumbnail failed:', exc_info=sys.exc_info())
            return ""
        request = self.context.get('request')
        relative_url = settings.MEDIA_URL + thumbnail
        if request:
            return request.build_absolute_uri(relative_url)
        return relative_url


# TODO: make a patch for DRF2 to set the look field other than pk.
# TODO: Don't send HyperlinkedFields in json? Not sure if this is a big deal or not.
class SlugHyperlinkedIdentityField(HyperlinkedIdentityField):
    def field_to_native(self, obj, field_name):
        request = self.context.get('request', None)
        view_name = self.view_name or self.parent.opts.view_name
        view_kwargs = {'slug': obj.slug}
        return reverse(view_name, kwargs=view_kwargs, request=request)


class ProjectCountrySerializer(serializers.ModelSerializer):
    subregion = Field()

    class Meta:
        model = Country
        fields = ('name', 'subregion')


class ProjectOwnerSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'picture')


class ProjectDetailSerializer(serializers.ModelSerializer):
    country = ProjectCountrySerializer()
    image = SorlImageField('image', '480x360', fit='center')
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    language = Field(source='get_language_display')
    organization = RelatedField()
    owner = ProjectOwnerSerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    phase = Field(source='get_phase_display')
    tags = ManyRelatedField()
    url = SlugHyperlinkedIdentityField(view_name='project-instance')
    money_asked = Field(source='money_asked')
    money_donated = Field(source='money_donated')

    class Meta:
        model = Project
        fields = ('country', 'created', 'id', 'image', 'language', 'latitude',
                  'longitude', 'money_asked', 'money_donated', 'organization',
                  'owner', 'phase', 'planned_end_date', 'planned_start_date',
                  'tags', 'themes', 'title', 'url')


class ProjectPreviewSerializer(ProjectDetailSerializer):
    image = SorlImageField('image', '230x150', crop='center')

    class Meta:
        model = Project
        fields = ('country', 'id', 'image', 'money_asked', 'money_donated',
                  'slug', 'title', 'url')
