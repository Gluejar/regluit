pyepub
======

An enhanced python library for dealing with EPUB2 files.
Based on latest [py-clave](http://github.com/gabalese/py-clave) development release.

Installation
------------

Grab the [latest stable release](https://github.com/gabalese/pyepub/archive/master.zip). Unpack the tarball and execute:

```
$ cd pyepub
$ python setup.py install
```

This will install the EPUB library in your current python environment as `pyepub`.

Basic usage
-----------

The code is as documented as I could. First `import` the EPUB class to use:

```python
from pyepub import EPUB
```

And you're pretty much done. Since pyepub.EPUB inherits largely from zipfile.Zipfile, the inferface is quite familiar.

For example, you can create a new EPUB to write into using the "w" flag:

```python
from pyepub import EPUB
epub = EPUB("newfile.epub", "w")
```

By default the epub is `open`-ed in read-only mode and exposes json-able dictionary of OPF properties.

```python
>>> from pyepub import EPUB
>>> epub = EPUB("file.epub")
>>> epub.info
{"metadata":[...], "manifest": [...], "spine": [...], "guide": [...]}
```

The EPUB can be opened in append ("a") mode, thus enabling adding content.
Due to the internal nature of zipfile stdlib module, a zipfile can't overwrite its contents.
Thusly, a EPUB opened for append is never overwritten. The `EPUB.__init__` constructor closes the local file and swaps
the reference with a `StringIO` file-like object. To write the final file to disk, you can call the `EPUB.writetodisk()`
method:

```python
>>> from pyepub import EPUB
>>> epub = EPUB("file.epub","a")
>>> epub.close()  # not necessary, since .writetodisk() will close the file for you.
>>> epub.writetodisk("newfile.epub")
>>> epub.filename  # the "file" remains available at .filename property, and can be .read() as usual.
<StringIO.StringIO instance at 0x1004a8c20>
```

License
-------

pyepub is distributed according to the MIT license. I don't like GPL-esque licenses, and I reinvented the wheel (since
there already is a EPUB library in pypi) to avoid involving GPL in my projects.
