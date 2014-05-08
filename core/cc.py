# mostly constants related to Creative Commons
# let's be DRY with these parameters

INFO_CC = (
    ('CC BY-NC-ND', 'by-nc-nd', 'Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported (CC BY-NC-ND 3.0)', 'http://creativecommons.org/licenses/by-nc-nd/3.0/'),     
    ('CC BY-NC-SA', 'by-nc-sa', 'Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)', 'http://creativecommons.org/licenses/by-nc-sa/3.0/'),
    ('CC BY-NC', 'by-nc', 'Creative Commons Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0)', 'http://creativecommons.org/licenses/by-nc/3.0/'),
    ('CC BY-ND', 'nc-nd', 'Creative Commons Attribution-NoDerivs 3.0 Unported (CC BY-ND 3.0)', 'http://creativecommons.org/licenses/by-nd/3.0/'), 
    ('CC BY-SA', 'by-sa', 'Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)', 'http://creativecommons.org/licenses/by-sa/3.0/'),
    ('CC BY', 'by', 'Creative Commons Attribution 3.0 Unported (CC BY 3.0)', 'http://creativecommons.org/licenses/by/3.0/'), 
    ('CC0', 'cc0', 'No Rights Reserved (CC0)', 'http://creativecommons.org/about/cc0'),
)
INFO_PD = (
    ('PD-US', 'pd-us', 'Public Domain, US', 'http://creativecommons.org/about/pdm'),
)
INFO_ALL = INFO_CC + INFO_PD
# CCHOICES, CCGRANTS, and FORMATS are all used in places that expect tuples
# CONTENT_TYPES will be easiest to manipulate in ungluify_record as a dict

CCCHOICES = tuple([(item[0],item[2]) for item in INFO_CC])
    
CHOICES = tuple([(item[0],item[2]) for item in INFO_ALL])

CCGRANTS = tuple([(item[0],item[3]) for item in INFO_CC])

GRANTS = tuple([(item[0],item[3]) for item in INFO_ALL])

LICENSE_LIST =  [item[0] for item in INFO_CC]
LICENSE_LIST_ALL =  [item[0] for item in INFO_ALL]
FACET_LIST = [item[1] for item in INFO_CC] 

class CCLicense():
    @staticmethod
    def url(license):
        if license in LICENSE_LIST_ALL:
            return INFO_ALL[LICENSE_LIST_ALL.index(license)][3]
        else:
            return ''

    @staticmethod
    def badge(license):
        if license == 'PD-US':
            return 'https://i.creativecommons.org/p/mark/1.0/88x31.png'
        elif license == 'CC0':
            return 'https://i.creativecommons.org/p/zero/1.0/88x31.png'
        elif license == 'CC BY':
            return 'https://i.creativecommons.org/l/by/3.0/88x31.png'
        elif license == 'CC BY-NC-ND':
            return 'https://i.creativecommons.org/l/by-nc-nd/3.0/88x31.png'
        elif license == 'CC BY-NC-SA':
            return 'https://i.creativecommons.org/l/by-nc-sa/3.0/88x31.png'
        elif license == 'CC BY-NC':
            return 'https://i.creativecommons.org/l/by-nc/3.0/88x31.png'
        elif license == 'CC BY-SA':
            return 'https://i.creativecommons.org/l/by-sa/3.0/88x31.png'
        elif license == 'CC BY-ND':
            return 'https://i.creativecommons.org/l/by-nd/3.0/88x31.png'
        else:
            return ''
