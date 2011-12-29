# The truncatechars filter is part of Django dev, but we're on 1.3.1
# The following is the filter and its dependencies
import unicodedata
from django import template
from django.template.base import Library
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy, SimpleLazyObject
from django.utils.translation import pgettext

register = Library()

class Truncator(SimpleLazyObject):
    """
    An object used to truncate text, either by characters or words.
    """
    def __init__(self, text):
        super(Truncator, self).__init__(lambda: force_unicode(text))

    def add_truncation_text(self, text, truncate=None):
        if truncate is None:
            truncate = pgettext(
                'String to return when truncating text',
                u'%(truncated_text)s...')
        truncate = force_unicode(truncate)
        if '%(truncated_text)s' in truncate:
            return truncate % {'truncated_text': text}
        # The truncation text didn't contain the %(truncated_text)s string
        # replacement argument so just append it to the text.
        if text.endswith(truncate):
            # But don't append the truncation text if the current text already
            # ends in this.
            return text
        return '%s%s' % (text, truncate)

    def chars(self, num, truncate=None):
        """
        Returns the text truncated to be no longer than the specified number
        of characters.

        Takes an optional argument of what should be used to notify that the
        string has been truncated, defaulting to a translatable string of an
        ellipsis (...).
        """
        length = int(num)
        uniself = unicode(self._wrapped)
        text = unicodedata.normalize('NFC', uniself)

        # Calculate the length to truncate to (max length - end_text length)
        truncate_len = length
        for char in self.add_truncation_text('', truncate):
            if not unicodedata.combining(char):
                truncate_len -= 1
                if truncate_len == 0:
                    break

        s_len = 0
        end_index = None
        for i, char in enumerate(text):
            if unicodedata.combining(char):
                # Don't consider combining characters
                # as adding to the string length
                continue
            s_len += 1
            if end_index is None and s_len > truncate_len:
                end_index = i
            if s_len > length:
                # Return the truncated string
                return self.add_truncation_text(text[:end_index or 0],
                                                truncate)

        # Return the original string since no truncation was necessary
        return text
    chars = allow_lazy(chars)

    def words(self, num, truncate=None, html=False):
        """
        Truncates a string after a certain number of words. Takes an optional
        argument of what should be used to notify that the string has been
        truncated, defaulting to ellipsis (...).
        """
        length = int(num)
        if html:
            return self._html_words(length, truncate)
        return self._text_words(length, truncate)
    words = allow_lazy(words)

    def _text_words(self, length, truncate):
        """
        Truncates a string after a certain number of words.

        Newlines in the string will be stripped.
        """
        words = self._wrapped.split()
        if len(words) > length:
            words = words[:length]
            return self.add_truncation_text(u' '.join(words), truncate)
        return u' '.join(words)

    def _html_words(self, length, truncate):
        """
        Truncates HTML to a certain number of words (not counting tags and
        comments). Closes opened tags if they were correctly closed in the
        given HTML.

        Newlines in the HTML are preserved.
        """
        if length <= 0:
            return u''
        html4_singlets = (
            'br', 'col', 'link', 'base', 'img',
            'param', 'area', 'hr', 'input'
        )
        # Count non-HTML words and keep note of open tags
        pos = 0
        end_text_pos = 0
        words = 0
        open_tags = []
        while words <= length:
            m = re_words.search(self._wrapped, pos)
            if not m:
                # Checked through whole string
                break
            pos = m.end(0)
            if m.group(1):
                # It's an actual non-HTML word
                words += 1
                if words == length:
                    end_text_pos = pos
                continue
            # Check for tag
            tag = re_tag.match(m.group(0))
            if not tag or end_text_pos:
                # Don't worry about non tags or tags after our truncate point
                continue
            closing_tag, tagname, self_closing = tag.groups()
            # Element names are always case-insensitive
            tagname = tagname.lower()
            if self_closing or tagname in html4_singlets:
                pass
            elif closing_tag:
                # Check for match in open tags list
                try:
                    i = open_tags.index(tagname)
                except ValueError:
                    pass
                else:
                    # SGML: An end tag closes, back to the matching start tag,
                    # all unclosed intervening start tags with omitted end tags
                    open_tags = open_tags[i + 1:]
            else:
                # Add it to the start of the open tags list
                open_tags.insert(0, tagname)
        if words <= length:
            # Don't try to close tags if we don't need to truncate
            return self._wrapped
        out = self._wrapped[:end_text_pos]
        truncate_text = self.add_truncation_text('', truncate)
        if truncate_text:
            out += truncate_text
        # Close any tags still open
        for tag in open_tags:
            out += '</%s>' % tag
        # Return string
        return out
        
# django dev uses filter(is_safe=True) syntax here, but that's not yet available in 1.3.1      
@register.filter()
@stringfilter
def truncatechars(value, arg):
    """
    Truncates a string after a certain number of characters.

    Argument: Number of characters to truncate after.
    """
    try:
        length = int(arg)
    except ValueError: # Invalid literal for int().
        return value # Fail silently.
    return Truncator(value).chars(length)
truncatechars.is_safe = True