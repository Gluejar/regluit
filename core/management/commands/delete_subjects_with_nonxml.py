from django.core.management.base import BaseCommand

from regluit.core.models import Subject

#https://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python

def valid_xml_char_ordinal(c):
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF
        )

def clean_string(input_string):
    return ''.join(c for c in input_string if valid_xml_char_ordinal(c))

class Command(BaseCommand):
    help = "delete subjects whose names are not expressible in XML"
    
    def handle(self, **options):
       bad_subjects = [subject for subject in Subject.objects.all() if clean_string(subject.name) != subject.name]
       print ("number of bad subjects:", len(bad_subjects))
       for bad_subject in bad_subjects:
            self.stdout.write('{}, {}'.format(
                bad_subject.name.encode('ascii', 'ignore'),
                bad_subject.works.count()
            ))
            bad_subject.delete()
