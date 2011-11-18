## {{{ http://code.activestate.com/recipes/498104/ (r1)

## also http://stackoverflow.com/questions/4047511/checking-if-an-isbn-number-is-correct

import re

def check_digit_10(isbn):
    assert len(isbn) == 9
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        w = i + 1
        sum += w * c
    r = sum % 11
    if r == 10: return 'X'
    else: return str(r)

def check_digit_13(isbn):
    assert len(isbn) == 12
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        if i % 2: w = 3
        else: w = 1
        sum += w * c
    r = 10 - (sum % 10)
    if r == 10: return '0'
    else: return str(r)

def convert_10_to_13(isbn):
    assert len(isbn) == 10
    prefix = '978' + isbn[:-1]
    check = check_digit_13(prefix)
    return prefix + check

def strip(s):
    """Strips away any - or spaces.  If the remaining string is of length 10 or 13 with digits only in anything but the last
    check digit (which may be X), then return '' -- otherwise return the remaining string"""
    s = s.replace("-", "").replace(" ", "").upper();
    match = re.search(r'^(\d{9}|\d{12})(\d|X)$', s)
    if not match:
        return None
    else:
        return s
   
def convert_13_to_10(isbn):
    assert len(isbn) == 13
    # only ISBN-13 starting with 978 can have a valid ISBN 10 partner
    assert isbn[0:3] == '978'
    return isbn [3:12] + check_digit_10(isbn[3:12])
    
class ISBNException(Exception):
    pass

class ISBN(object):
    def __init__(self, input_isbn):
        self.input_isbn = input_isbn
        stripped_isbn = strip(input_isbn)
            
        if stripped_isbn is None:
            raise(ISBNException("input_isbn %s does not seem to be a valid ISBN" % (input_isbn)))
        elif len(stripped_isbn) == 10:
            self.__type = '10'
            self.__isbn10 = stripped_isbn
            self.__valid_10 = stripped_isbn[0:9] + check_digit_10(stripped_isbn[0:9])
            self.__valid = (self.__isbn10 == self.__valid_10)
            
            # this is the corresponding ISBN 13 based on the assumption of a valid ISBN 10
            self.__isbn13 = convert_10_to_13(stripped_isbn)
            self.__valid_13 = self.__isbn13  

        elif len(stripped_isbn) == 13:
            self.__type = '13'
            self.__isbn13 = stripped_isbn
            self.__valid_13 = stripped_isbn[0:12] + check_digit_13(stripped_isbn[0:12])
            self.__valid = (self.__isbn13 == self.__valid_13)
            
            self.__isbn10 = convert_13_to_10(stripped_isbn)
            self.__valid_10 = self.__isbn10
            
        else:
            raise(ISBNException("stripped_isbn %s is of the wrong length" % (stripped_isbn)))

    @property
    def type(self):
        return self.__type
    @property
    def valid (self):
        return self.__valid
    def validate (self):
        """ replace the ISBN value with the checksumed version """
        if self.type == '10':
            self.__isbn10 = self.__valid_10
            self.__valid = True
            return self
        else:
            self.__isbn13 = self.__valid_13
            self.__valid = True
            return self
    def to_string(self, type='13', hyphenate=False):
        if type == '10' or type == 10:
            if hyphenate:
                s = self.__isbn10
                return "%s-%s-%s-%s" % (s[0], s[1:4], s[4:9], s[9])
            else:
                return self.__isbn10
        else:
            if hyphenate:
                s = self.__isbn13
                return "%s-%s-%s-%s-%s" % (s[0:3], s[3], s[4:7], s[7:12], s[12])
            else:
                return self.__isbn13 
    def __unicode__(self):
        return unicode(self.to_string(type=self.type,hyphenate=False))
    def __str__(self):
        return self.to_string(type=self.type,hyphenate=False)
    def __eq__(self, other):
        """ both equal if both valid checksums and ISBN 13 equal """
        if isinstance(other, ISBN):
            if (self.valid and other.valid) and (self.to_string('13') == other.to_string('13')):
                return True
            else:
                return False
        else:
            try:
                other_isbn = ISBN(other)
                if (self.valid and other_isbn.valid) and (self.to_string('13') == other_isbn.to_string('13')):
                    return True
                else:
                    return False
            except:
                return False
                
    def __ne__(self, other):
        return not (self.__eq__(other))
    
    
