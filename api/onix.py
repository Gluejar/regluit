import datetime
import re

from bs4 import BeautifulSoup
import pytz

from django.core.paginator import Paginator, InvalidPage

from regluit.bisac import Bisac
from regluit.core import models
from regluit.core.cc import ccinfo
from .crosswalks import relator_contrib, iso639

WORKS_PER_PAGE = 30

feed_header = """<?xml version="1.0" encoding="UTF-8"?>
<ONIXMessage release="3.0" xmlns="http://ns.editeur.org/onix/3.0/reference" >
"""
feed_xml = feed_header + '</ONIXMessage>\r\n'
soup = None
bisac = Bisac()

def text_node(tag, text, attrib=None):
    node = soup.new_tag(tag)
    if attrib:
        node.attrs = attrib
    node.string = text
    return node

def sub_element(node, tag, attrib=None):
    sub = soup.new_tag(tag)
    if attrib:
        sub.attrs = attrib
    node.append(sub)
    return sub


def onix_feed(facet, max=None, page_number=None):
    global soup
    if not soup:
        soup = BeautifulSoup('', 'lxml')

    yield feed_header + str(header(facet))
    works = facet.works[0:max] if max else facet.works

    if page_number is not None:
        try:
            p = Paginator(works, WORKS_PER_PAGE)
            works = p.page(page_number)
        except InvalidPage:
            works = []

    for work in works:
        editions = models.Edition.objects.filter(work=work, ebooks__isnull=False)
        editions = facet.facet_object.filter_model("Edition", editions).distinct()
        for edition in editions:
            edition_prod = product(edition, facet.facet_object)
            if edition_prod is not None:
                yield edition_prod
    yield '</ONIXMessage>'

def onix_feed_for_work(work):
    global soup
    if not soup:
        soup = BeautifulSoup('', 'lxml')

    feed = BeautifulSoup(feed_xml, 'xml')
    feed.ONIXMessage.append(header(work))
    for edition in models.Edition.objects.filter(work=work, ebooks__isnull=False).distinct():
        edition_prod = product(edition)
        if edition_prod is not None:
            feed.ONIXMessage.append(product(edition))
    return str(feed)

def header(facet=None):
    header_node = soup.new_tag("Header")
    sender_node = soup.new_tag("Sender")
    sender_node.append(text_node("SenderName", "unglue.it"))
    sender_node.append(text_node("EmailAddress", "unglueit@ebookfoundation.org"))
    header_node.append(sender_node)
    header_node.append(text_node(
        "SentDateTime",
        pytz.utc.localize(datetime.datetime.utcnow()).strftime('%Y%m%dT%H%M%SZ')
    ))
    header_node.append(text_node("MessageNote", facet.title if facet else "Unglue.it Editions"))
    return header_node

def product(edition, facet=None):
    ebooks = facet.filter_model(
        "Ebook",
        edition.ebooks.filter(active=True)
    ) if facet else edition.ebooks.filter(active=True)
    ebooks = ebooks.order_by('-created')
    # Just because an edition satisfies 2 facets with multiple ebooks doesn't mean that there
    # is a single ebook satisfies both facets
    if not ebooks.exists():
        return None

    work = edition.work
    product_node = soup.new_tag("Product")
    product_node.append(text_node(
        "RecordReference", "it.unglue.work.%s.%s" % (work.id, edition.id)
    ))
    product_node.append(text_node("NotificationType", "03")) # final

    ident_node = sub_element(product_node, "ProductIdentifier")
    ident_node.append(text_node("ProductIDType", "01")) #proprietary
    ident_node.append(text_node("IDTypeName", "unglue.it edition id")) #proprietary
    ident_node.append(text_node("IDValue", str(edition.id)))

    # wrong isbn better than no isbn
    isbn = edition.isbn_13 if edition.isbn_13 else edition.work.first_isbn_13()
    if isbn:
        ident_node = sub_element(product_node, "ProductIdentifier")
        ident_node.append(text_node("ProductIDType", "03")) #proprietary
        ident_node.append(text_node("IDValue", isbn))

    # Descriptive Detail Block
    descriptive_node = sub_element(product_node, "DescriptiveDetail")
    descriptive_node.append(text_node("ProductComposition", "00")) # single item
    descriptive_node.append(text_node("ProductForm", "ED")) # download

    ebook = None
    latest_ebooks = []
    ebook_formats = []
    for ebook in ebooks:
        if ebook.format not in ebook_formats:
            ebook_formats.append(ebook.format)
            latest_ebooks.append(ebook)
            if ebook.format == 'epub':
                descriptive_node.append(text_node("ProductFormDetail", "E101"))
            elif ebook.format == 'pdf':
                descriptive_node.append(text_node("ProductFormDetail", "E107"))
            elif ebook.format == 'mobi':
                descriptive_node.append(text_node("ProductFormDetail", "E116"))
    if ebook.rights:
        license_node = sub_element(descriptive_node, "EpubLicense")
        license_node.append(text_node("EpubLicenseName", ebook.rights))
        lic_expr_node = sub_element(license_node, "EpubLicenseExpression")
        lic_expr_node.append(text_node("EpubLicenseExpressionType", '01')) #human readable
        lic_expr_node.append(text_node("EpubLicenseExpressionLink", ccinfo(ebook.rights).url))

    title_node = sub_element(descriptive_node, "TitleDetail")
    title_node.append(text_node("TitleType", '01')) #distinctive title
    title_el = sub_element(title_node, "TitleElement")
    title_el.append(text_node("TitleElementLevel", '01'))
    title_el.append(text_node("TitleText", edition.title))
    contrib_i = 0
    for contrib in edition.relators.all():
        contrib_i += 1
        contrib_node = sub_element(descriptive_node, "Contributor")
        contrib_node.append(text_node("SequenceNumber", str(contrib_i)))
        contrib_node.append(text_node("ContributorRole",
                                      relator_contrib.get(contrib.relation.code, "")))
        contrib_node.append(text_node("PersonName", contrib.author.name))
        contrib_node.append(text_node("PersonNameInverted", contrib.author.last_name_first))
    (lang, locale) = (edition.work.language, None)
    if '_' in lang:
        (lang, locale) = lang.split('_')
    if len(lang) == 2:
        lang = iso639.get(lang, None)
    if lang:
        lang_node = sub_element(descriptive_node, "Language")
        lang_node.append(text_node("LanguageRole", "01"))
        lang_node.append(text_node("LanguageCode", lang))
    if locale:
        lang_node.append(text_node("CountryCode", locale))
    for subject in work.subjects.all():
        subj_node = sub_element(descriptive_node, "Subject")
        if  subject.authority == 'lcsh':
            subj_node.append(text_node("SubjectSchemeIdentifier", "04"))
            subj_node.append(text_node("SubjectHeadingText", subject.name))
        elif subject.authority == 'lcc':
            subj_node.append(text_node("SubjectSchemeIdentifier", "03"))
            subj_node.append(text_node("SubjectCode", subject.name))
        elif subject.authority == 'bisacsh':
            subj_node.append(text_node("SubjectSchemeIdentifier", "10"))
            subj_node.append(text_node("SubjectCode", bisac.code(subject.name)))
            subj_node.append(text_node("SubjectHeadingText", subject.name))
        else:
            subj_node.append(text_node("SubjectSchemeIdentifier", "20"))
            subj_node.append(text_node("SubjectHeadingText", subject.name))

    # audience range composite
    if work.age_level:
        range_match = re.search(r'(\d?\d?)-(\d?\d?)', work.age_level)
        if range_match:
            audience_range_node = sub_element(descriptive_node, "AudienceRange")
            #Interest age, years
            audience_range_node.append(text_node("AudienceRangeQualifier", "17"))
            if range_match.group(1):
                audience_range_node.append(text_node("AudienceRangePrecision", "03")) #from
                audience_range_node.append(text_node("AudienceRangeValue", range_match.group(1)))
            if range_match.group(2):
                audience_range_node.append(text_node("AudienceRangePrecision", "04")) #from
                audience_range_node.append(text_node("AudienceRangeValue", range_match.group(2)))

    # Collateral Detail Block
    coll_node = sub_element(product_node, "CollateralDetail")
    desc_node = sub_element(coll_node, "TextContent")
    desc_node.append(text_node("TextType", '03')) # description
    desc_node.append(text_node("ContentAudience", '00')) #unrestricted
    desc = (work.description if work.description else '') + \
            '<br /><br />Listed by <a href="https://unglue.it/work/%s/">Unglue.it</a>.' % work.id
    content = BeautifulSoup('<div>' + desc  + '</div>', 'lxml')
    content_node = sub_element(desc_node, "Text", attrib={"textformat":"05"}) #xhtml
    content_node.append(content.body.div)
    supp_node = sub_element(coll_node, "SupportingResource")
    supp_node.append(text_node("ResourceContentType", '01')) #front cover
    supp_node.append(text_node("ContentAudience", '00')) #unrestricted
    supp_node.append(text_node("ResourceMode", '03')) #image
    cover_node = sub_element(supp_node, "ResourceVersion")
    cover_node.append(text_node("ResourceForm", '01')) #linkable
    coverfeat_node = sub_element(cover_node, "ResourceVersionFeature")
    coverfeat_node.append(text_node("ResourceVersionFeatureType", '01')) #image format
    coverfeat_node.append(text_node("FeatureValue", 'D502')) #jpeg
    cover_node.append(text_node("ResourceLink", edition.cover_image_thumbnail())) #link

    # Publishing Detail Block
    pubdetail_node = sub_element(product_node, "PublishingDetail")
    if edition.publisher_name:
        pub_node = sub_element(pubdetail_node, "Publisher")
        pub_node.append(text_node("PublishingRole", '01')) #publisher
        pub_node.append(text_node("PublisherName", edition.publisher_name.name))
    pubdetail_node.append(text_node("PublishingStatus", '00')) #unspecified

    #consumers really want a pub date
    publication_date = edition.publication_date if edition.publication_date else \
            edition.work.earliest_publication_date
    if publication_date:
        pubdate_node = sub_element(pubdetail_node, "PublishingDate")
        pubdate_node.append(text_node("PublishingDateRole", '01')) #nominal pub date
        pubdate_node.append(text_node("Date", publication_date.replace('-', '')))

    # Product Supply Block
    supply_node = sub_element(product_node, "ProductSupply")
    market_node = sub_element(supply_node, "Market")
    terr_node = sub_element(market_node, "Territory")
    terr_node.append(text_node("RegionsIncluded", 'WORLD'))
    supply_detail_node = sub_element(supply_node, "SupplyDetail")
    supplier_node = sub_element(supply_detail_node, "Supplier")
    supplier_node.append(text_node("SupplierRole", '11')) #non-exclusive distributer
    supplier_node.append(text_node("SupplierName", 'Unglue.it')) #non-exclusive distributer
    for ebook in latest_ebooks:
        website_node = sub_element(supplier_node, "Website")
        website_node.append(text_node("WebsiteRole", '29')) #full content
        #full content
        website_node.append(text_node("WebsiteDescription",
                                      '%s file download' % ebook.format,
                                      attrib={'textformat':'06'}))
        website_node.append(text_node("WebsiteLink", ebook.download_url)) #full content
    supply_detail_node.append(text_node("ProductAvailability", '20')) #Available
    price_node = sub_element(supply_detail_node, "Price")
    price_node.append(text_node("PriceType", '01')) #retail excluding tax
    price_node.append(text_node("PriceAmount", '0.00')) #retail excluding tax
    price_node.append(text_node("CurrencyCode", 'USD')) #retail excluding tax
    return product_node
