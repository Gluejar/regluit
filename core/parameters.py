(REWARDS, BUY2UNGLUE, THANKS) = (1, 2, 3)
(INDIVIDUAL, LIBRARY, BORROWED, RESERVE, THANKED) = (1, 2, 3, 4, 5)
TESTING = 0
OFFER_CHOICES = ((INDIVIDUAL, 'Individual license'),(LIBRARY, 'Library License'))
ACQ_CHOICES = ((INDIVIDUAL, 'Individual license'), (LIBRARY, 'Library License'),
               (BORROWED, 'Borrowed from Library'), (TESTING, 'Just for Testing'),
               (RESERVE, 'On Reserve'), (THANKED, 'Already Thanked'),)

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
    ('part', 'part'),
    ('unspecified', 'unspecified')
)

ID_CHOICES = (
    ('http', 'Web Address'),
    ('isbn', 'ISBN'),
    ('doab', 'DOABooks handle'),
    ('gtbg', 'Project Gutenberg Number'),
    ('doi', 'Digital Object Identifier'),
    ('oclc', 'OCLC Number'),
    ('goog', 'Google Books ID'),
    ('thng', 'Library Thing ID'),
    ('olwk', 'Open Library Work ID'),
    ('ltwk', 'Library Thing Work ID'),
    ('oapn', 'OAPEN ID'),
)

OTHER_ID_CHOICES = (
    ('glue', 'Unglue.it ID'),
    ('edid', 'pragmatic edition ID'),
)

WORK_IDENTIFIERS = ('doi', 'olwk', 'glue', 'ltwk', 'http', 'doab')

ID_CHOICES_MAP = dict(ID_CHOICES)

GOOD_PROVIDERS = ('Internet Archive', 'Unglue.it', 'Github', 'OAPEN Library', 'SciELO')

DOMAIN_TO_PROVIDER = dict([
    [u'adelaide.edu.au', u'University of Adelaide'],
    [u'aliprandi.org', u'Simone Aliprandi'],
    [u'antilia.to.it', u'antilia.to.it'],
    [u'antropologie.zcu.cz', u'AntropoWeb'],
    [u'aupress.ca', u'Athabasca University Press'],
    [u'bloomsburyacademic.com', u'Bloomsbury Academic'],
    [u'books.mdpi.com', u'MDPI Books'],
    [u'books.openedition.org', u'OpenEdition Books'],
    [u'books.scielo.org', u'SciELO'],
    [u'ccdigitalpress.org', u'Computers and Composition Digital Press'],
    [u'co-action.net', u'Co-Action Publishing'],
    [u'degruyter.com', u'De Gruyter Online'],
    [u'digitalcommons.usu.edu', u'DigitalCommons, Utah State University'],
    [u'dl.dropboxusercontent.com', u'Dropbox'],
    [u'doabooks.org', u'Directory of Open Access Books'],
    [u'doi.org', u'DOI Resolver'],
    [u'dropbox.com', u'Dropbox'],
    [u'dspace.ucalgary.ca', u'Institutional Repository at the University of Calgary'],
    [u'dx.doi.org', u'DOI Resolver'],
    [u'ebooks.iospress.nl', u'IOS Press Ebooks'],
    [u'hdl.handle.net', u'Handle Proxy'],
    [u'hw.oeaw.ac.at', u'Austrian Academy of Sciences'],
    [u'img.mdpi.org', u'MDPI Books'],
    [u'ledibooks.com', u'LediBooks'],
    [u'ledizioni.it', u'Ledizioni'],
    [u'leo.cilea.it', u'LEO '],
    [u'leo.cineca.it', u'Letteratura Elettronica Online'],
    [u'library.oapen.org', u'OAPEN Library'],
    [u'link.springer.com', u'Springer'],
    [u'maestrantonella.it', u'maestrantonella.it'],
    [u'oapen.org', u'OAPEN Library'],
    [u'openbookpublishers.com', u'Open Book Publishers'],
    [u'palgraveconnect.com', u'Palgrave Connect'],
    [u'press.openedition.org', u'OpenEdition Press'],
    [u'scribd.com', u'Scribd'],
    [u'springerlink.com', u'Springer'],
    [u'transcript-verlag.de', u'Transcript-Verlag'],
    [u'ubiquitypress.com', u'Ubiquity Press'],
    [u'unglueit-files.s3.amazonaws.com', u'Unglue.it'],
    [u'unimib.it', u'University of Milano-Bicocca'],
    [u'unito.it', u"University of Turin"],
    [u'windsor.scholarsportal.info', u'Scholars Portal'],
])

ORDER_BY_KEYS = {
    'newest':['-featured', '-created'],
    'oldest':['created'],
    'featured':['-featured', '-num_wishes'],
    'popular':['-num_wishes'],
    'title':['title'],
    'none':[], #no ordering
}
