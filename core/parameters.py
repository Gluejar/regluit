(REWARDS, BUY2UNGLUE, THANKS) = (1, 2, 3)
(INDIVIDUAL, LIBRARY, BORROWED, RESERVE, THANKED) = (1, 2, 3, 4, 5)
TESTING = 0
OFFER_CHOICES = ((INDIVIDUAL,'Individual license'),(LIBRARY,'Library License'))
ACQ_CHOICES = ((INDIVIDUAL,'Individual license'),(LIBRARY,'Library License'),(BORROWED,'Borrowed from Library'), (TESTING,'Just for Testing'), (RESERVE,'On Reserve'),(THANKED,'Already Thanked'),)

AGE_LEVEL_CHOICES = (
    ('', 'No Rating'),
    ('5-6', 'Children\'s - Kindergarten, Age 5-6'),
    ('6-7', 'Children\'s - Grade 1-2, Age 6-7'),
    ('7-8', 'Children\'s - Grade 2-3, Age 7-8'),
    ('8-9', 'Children\'s - Grade 3-4, Age 8-9'),
    ('9-11', 'Children\'s - Grade 4-6, Age 9-11'),
    ('12-14', 'Teen - Grade 7-9, Age 12-14'),
    ('15-18', 'Teen - Grade 10-12, Age 15-18'),
    ('18-', 'Adult/Advanced Reader')
)

TEXT_RELATION_CHOICES = (
    ('translation', 'translation'),
    ('revision', 'revision'),
    ('sequel', 'sequel'),
    ('part', 'part')
)

ID_CHOICES = (
    ('http', 'Web Address'),    
    ('isbn', 'ISBN'),
    ('doab', 'DOABooks ID'),
    ('gtbg', 'Project Gutenberg Number'),
    ('doi', 'Digital Object Identifier'),
    ('oclc', 'OCLC Number'),
    ('goog', 'Google Books ID'),
    ('gdrd', 'Goodreads ID'),
    ('thng', 'Library Thing ID'),
    ('olwk', 'Open Library Work ID'),
    ('ltwk', 'Library Thing Work ID'),
    ('oapn', 'OAPEN ID'),
)

OTHER_ID_CHOICES = (
    ('glue', 'Unglue.it ID'),
    ('edid', 'pragmatic edition ID'),
)

WORK_IDENTIFIERS = ('doi','olwk','glue','ltwk', 'http', 'doab')

ID_CHOICES_MAP = dict(ID_CHOICES)






