

class BooXtreamError(Exception):
    """  list of errors returned in xml
    """
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        errormsg='BooXtream errors:'
        for error in self.errors:
            errormsg += 'Error %s: %s\n'% (error.find('Code').text,error.find('Msg').text)
        return errormsg