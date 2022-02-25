'''
Monkey patch to fix S3 backend slowness in sorl.thumbnail
https://github.com/jazzband/sorl-thumbnail/issues/301
'''

from django.utils.functional import LazyObject

import sorl.thumbnail.default
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class
from sorl.thumbnail import get_thumbnail

_storage = None

class Storage(LazyObject):
    def _setup(self):
        global _storage
        if not _storage:
            _storage = get_module_class(settings.THUMBNAIL_STORAGE)()

        self._wrapped = _storage

sorl.thumbnail.default.storage = Storage()
