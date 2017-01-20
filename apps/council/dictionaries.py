# -*- coding:utf-8 -*-

TITLES_CHOICES = [
    ('1', u'inż.'),
    ('2', u'mgr inż.'),
    ('3', u'dr'),
    ('4', u'dr inż.'),
    ('5', u'dr hab.'),
    ('6', u'dr hab. inż.'),
    ('7', u'prof. dr hab.'),
    ('8', u'prof. dr hab. inż.'),
]

SUPERVISOR_GROUP = 'supervisor'
SMALL_QUORUM_GROUP = 'small_quorum'
BIG_QUORUM_GROUP = 'big_quorum'
GROUPS = [
    (SUPERVISOR_GROUP, u'Konto zarządzające'),
    (SMALL_QUORUM_GROUP, u'Małe kworum'),
    (BIG_QUORUM_GROUP, u'Duże kworum'),
]