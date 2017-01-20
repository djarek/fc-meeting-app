from django import template
from apps.council.models import Person, Point

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    person = Person.objects.get(email=user.email)
    return person.group == group_name


@register.filter(name='is_point_owner')
def is_point_owner(user, point_pk):
    person = Person.objects.get(email=user.email)
    point = Point.objects.get(pk=point_pk)
    return point.owner.person == person
