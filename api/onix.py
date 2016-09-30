import datetime
import pytz
import re
from lxml import etree
from regluit.core import models
from regluit.core.cc import ccinfo
from regluit.bisac import Bisac
from .crosswalks import relator_contrib, iso639
feed_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ONIXMessage release="3.0" xmlns="http://ns.editeur.org/onix/3.0/reference" />
"""
bisac = Bisac()

def text_node(tag, text, attrib={}):
    node = etree.Element(tag, attrib=attrib)
    node.text = text
    return node

def onix_feed(facet, max=None):
    feed = etree.fromstring(feed_xml)
    feed.append(header(facet))
    works = facet.works[0:max] if max else facet.works
    for work in works:
        editions = models.Edition.objects.filter(work=work,ebooks__isnull=False)
        editions = facet.facet_object.filter_model("Edition",editions).distinct()
        for edition in editions:
            edition_prod = product(edition, facet.facet_object)
            if edition_prod:
                feed.append(edition_prod)    
    return etree.tostring(feed, pretty_print=True)
    
def onix_feed_for_work(work):
    feed = etree.fromstring(feed_xml)
    feed.append(header(work))
    for edition in models.Edition.objects.filter(work=work,ebooks__isnull=False).distinct():
        feed.append(product(edition))
    return etree.tostring(feed, pretty_print=True)
    
def header(facet=None):
    header_node = etree.Element("Header")	
    sender_node = etree.Element("Sender")	
    sender_node.append(text_node("SenderName", "unglue.it"))
    sender_node.append(text_node("EmailAddress", "support@gluejar.com"))
    header_node.append(sender_node)
    header_node.append(text_node("SentDateTime", pytz.utc.localize(datetime.datetime.utcnow()).strftime('%Y%m%dT%H%M%SZ')))
    header_node.append(text_node("MessageNote", facet.title if facet else "Unglue.it Editions"))
    return header_node

def product(edition, facet=None):
    ebooks=facet.filter_model("Ebook",edition.ebooks.filter(active=True)) if facet else edition.ebooks.filter(active=True)
    ebooks=ebooks.order_by('-created')
    # Just because an edition satisfies 2 facets with multiple ebooks doesn't mean that there is a single ebook satisfies both facets
    if not ebooks.exists():
        return None
        
    work=edition.work
    product_node = etree.Element("Product")
    product_node.append(text_node("RecordReference", "it.unglue.work.%s.%s" % (work.id, edition.id)))
    product_node.append(text_node("NotificationType", "03" )) # final

    ident_node =  etree.SubElement(product_node, "ProductIdentifier")
    ident_node.append(text_node("ProductIDType", "01" )) #proprietary
    ident_node.append(text_node("IDTypeName", "unglue.it edition id" )) #proprietary
    ident_node.append(text_node("IDValue", unicode(edition.id) )) 
    
    # wrong isbn better than no isbn
    isbn = edition.isbn_13 if edition.isbn_13 else edition.work.first_isbn_13()
    if isbn:
        ident_node =  etree.SubElement(product_node, "ProductIdentifier")
        ident_node.append(text_node("ProductIDType", "03" )) #proprietary
        ident_node.append(text_node("IDValue", isbn )) 

    # Descriptive Detail Block
    descriptive_node =  etree.SubElement(product_node, "DescriptiveDetail")
    descriptive_node.append(text_node("ProductComposition", "00" )) # single item 
    descriptive_node.append(text_node("ProductForm", "ED" )) # download 

    ebook = None
    latest_ebooks = []
    ebook_formats = []
    for ebook in ebooks:
        if ebook.format not in ebook_formats:
            ebook_formats.append(ebook.format)
            latest_ebooks.append(ebook)
            if ebook.format=='epub':
                descriptive_node.append(text_node("ProductFormDetail", "E101" )) 
            elif ebook.format=='pdf':
                descriptive_node.append(text_node("ProductFormDetail", "E107" )) 
            elif ebook.format=='mobi':
                descriptive_node.append(text_node("ProductFormDetail", "E116" )) 
    if ebook.rights:
        license_node =  etree.SubElement(descriptive_node, "EpubLicense")
        license_node.append(text_node("EpubLicenseName", ebook.rights )) 
        lic_expr_node =  etree.SubElement(license_node, "EpubLicenseExpression")
        lic_expr_node.append(text_node("EpubLicenseExpressionType", '01' )) #human readable
        lic_expr_node.append(text_node("EpubLicenseExpressionLink", ccinfo(ebook.rights).url )) 

    title_node =  etree.SubElement(descriptive_node, "TitleDetail")
    title_node.append(text_node("TitleType", '01' )) #distinctive title
    title_el = etree.SubElement(title_node, "TitleElement")
    title_el.append(text_node("TitleElementLevel", '01' ))
    title_el.append(text_node("TitleText", edition.title ))
    contrib_i = 0
    for contrib in edition.relators.all():
        contrib_i+=1
        contrib_node = etree.SubElement(descriptive_node, "Contributor")
        contrib_node.append(text_node("SequenceNumber", unicode(contrib_i )))
        contrib_node.append(text_node("ContributorRole", relator_contrib.get(contrib.relation.code,"") ))
        contrib_node.append(text_node("PersonName", contrib.author.name))
        contrib_node.append(text_node("PersonNameInverted", contrib.author.last_name_first))
    (lang, locale) = (edition.work.language, None)
    if '_' in lang:
        (lang, locale) = lang.split('_')
    if len(lang)==2: 
        lang = iso639.get(lang, None)
    if lang:
        lang_node = etree.SubElement(descriptive_node, "Language")
        lang_node.append(text_node("LanguageRole", "01"))
        lang_node.append(text_node("LanguageCode", lang))
    if locale:
        lang_node.append(text_node("CountryCode", locale))
    for subject in work.subjects.all():
        subj_node = etree.SubElement(descriptive_node, "Subject")
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
            audience_range_node = etree.SubElement(descriptive_node, "AudienceRange")
            audience_range_node.append(text_node("AudienceRangeQualifier", "17")) #Interest age, years
            if range_match.group(1):
                audience_range_node.append(text_node("AudienceRangePrecision", "03")) #from
                audience_range_node.append(text_node("AudienceRangeValue", range_match.group(1))) 
            if range_match.group(2):
                audience_range_node.append(text_node("AudienceRangePrecision", "04")) #from
                audience_range_node.append(text_node("AudienceRangeValue", range_match.group(2))) 
                    
    # Collateral Detail Block
    coll_node =  etree.SubElement(product_node, "CollateralDetail")
    desc_node =  etree.SubElement(coll_node, "TextContent")
    desc_node.append(text_node("TextType", '03')) # description
    desc_node.append(text_node("ContentAudience", '00')) #unrestricted
    desc = (work.description if work.description else '') + '<br /><br />Listed by <a href="https://unglue.it/work/%s/">Unglue.it</a>.' % work.id
    try :
        content = etree.XML("<div>" + desc + "</div>")
        content_node =  etree.SubElement(desc_node, "Text", attrib={"textformat":"05"}) #xhtml
        content_node.append(content)
    except etree.XMLSyntaxError:
        content_node = etree.SubElement(desc_node, "Text", attrib={"textformat":"02"}) #html
        content_node.text = etree.CDATA(desc)
    supp_node = etree.SubElement(coll_node, "SupportingResource")
    supp_node.append(text_node("ResourceContentType", '01')) #front cover
    supp_node.append(text_node("ContentAudience", '00')) #unrestricted
    supp_node.append(text_node("ResourceMode", '03')) #image
    cover_node =  etree.SubElement(supp_node, "ResourceVersion")
    cover_node.append(text_node("ResourceForm", '01')) #linkable
    coverfeat_node =   etree.SubElement(cover_node, "ResourceVersionFeature")
    coverfeat_node.append(text_node("ResourceVersionFeatureType", '01')) #image format
    coverfeat_node.append(text_node("FeatureValue", 'D502')) #jpeg
    cover_node.append(text_node("ResourceLink", edition.cover_image_thumbnail())) #link

    # Publishing Detail Block
    pubdetail_node =  etree.SubElement(product_node, "PublishingDetail")
    if edition.publisher_name:
        pub_node =  etree.SubElement(pubdetail_node, "Publisher")
        pub_node.append(text_node("PublishingRole", '01')) #publisher
        pub_node.append(text_node("PublisherName", edition.publisher_name.name))
    pubdetail_node.append(text_node("PublishingStatus", '00')) #unspecified
    
    #consumers really want a pub date
    publication_date = edition.publication_date if edition.publication_date else edition.work.earliest_publication_date
    if publication_date:
        pubdate_node =  etree.SubElement(pubdetail_node, "PublishingDate")
        pubdate_node.append(text_node("PublishingDateRole", '01')) #nominal pub date
        pubdate_node.append(text_node("Date", publication_date.replace('-',''))) 
        
    # Product Supply Block
    supply_node =  etree.SubElement(product_node,"ProductSupply")
    market_node =  etree.SubElement(supply_node,"Market")
    terr_node =  etree.SubElement(market_node,"Territory")
    terr_node.append(text_node("RegionsIncluded", 'WORLD'))
    supply_detail_node =  etree.SubElement(supply_node,"SupplyDetail")
    supplier_node =  etree.SubElement(supply_detail_node,"Supplier")
    supplier_node.append(text_node("SupplierRole", '11')) #non-exclusive distributer
    supplier_node.append(text_node("SupplierName", 'Unglue.it')) #non-exclusive distributer
    for ebook in latest_ebooks:
        website_node =  etree.SubElement(supplier_node,"Website")
        website_node.append(text_node("WebsiteRole", '29')) #full content
        website_node.append(text_node("WebsiteDescription", '%s file download' % ebook.format, attrib={'textformat':'06'})) #full content
        website_node.append(text_node("WebsiteLink", ebook.download_url)) #full content
    supply_detail_node.append(text_node("ProductAvailability", '20')) #Available
    price_node = etree.SubElement(supply_detail_node,"Price")
    price_node.append(text_node("PriceType", '01')) #retail excluding tax
    price_node.append(text_node("PriceAmount", '0.00')) #retail excluding tax
    price_node.append(text_node("CurrencyCode", 'USD')) #retail excluding tax
    return product_node
    