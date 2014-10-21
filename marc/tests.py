"""
django imports
"""
from django.test import TestCase
from django.test.client import Client
from django.db.models import get_model

"""
regluit imports
"""
from . import models, load

a_marc_record = '''<?xml version="1.0" encoding="UTF-8"?><record xmlns="http://www.loc.gov/MARC21/slim" xmlns:cinclude="http://apache.org/cocoon/include/1.0" xmlns:zs="http://www.loc.gov/zing/srw/">
  <leader>01021cam a2200301 a 4500</leader>
  <controlfield tag="001">3057297</controlfield>
  <controlfield tag="005">19970108080513.5</controlfield>
  <controlfield tag="008">960131r19761970ke b     b    000 0 eng  </controlfield>
  <datafield tag="035" ind1=" " ind2=" ">
    <subfield code="9">(DLC)   96109467</subfield>
  </datafield>
  <datafield tag="906" ind1=" " ind2=" ">
    <subfield code="a">7</subfield>
    <subfield code="b">cbc</subfield>
    <subfield code="c">orignew</subfield>
    <subfield code="d">u</subfield>
    <subfield code="e">ncip</subfield>
    <subfield code="f">19</subfield>
    <subfield code="g">y-gencatlg</subfield>
  </datafield>
  <datafield tag="955" ind1=" " ind2=" ">
    <subfield code="a">082 done aa11</subfield>
  </datafield>
  <datafield tag="010" ind1=" " ind2=" ">
    <subfield code="a">   96109467 </subfield>
  </datafield>
  <datafield tag="020" ind1=" " ind2=" ">
    <subfield code="a">0195724135</subfield>
  </datafield>
  <datafield tag="040" ind1=" " ind2=" ">
    <subfield code="a">DLC</subfield>
    <subfield code="c">DLC</subfield>
    <subfield code="d">DLC</subfield>
  </datafield>
  <datafield tag="043" ind1=" " ind2=" ">
    <subfield code="a">f------</subfield>
  </datafield>
  <datafield tag="050" ind1="0" ind2="0">
    <subfield code="a">PL8010</subfield>
    <subfield code="b">.F5 1976</subfield>
  </datafield>
  <datafield tag="082" ind1="0" ind2="0">
    <subfield code="a">398.2/096</subfield>
    <subfield code="2">20</subfield>
  </datafield>
  <datafield tag="100" ind1="1" ind2=" ">
    <subfield code="a">Finnegan, Ruth H.</subfield>
  </datafield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Oral literature in Africa /</subfield>
    <subfield code="c">Ruth Finnegan.</subfield>
  </datafield>
  <datafield tag="260" ind1=" " ind2=" ">
    <subfield code="a">Nairobi :</subfield>
    <subfield code="b">Oxford University Press,</subfield>
    <subfield code="c">1976 (1994 printing).</subfield>
  </datafield>
  <datafield tag="300" ind1=" " ind2=" ">
    <subfield code="a">xviii, 558 p. :</subfield>
    <subfield code="b">map ;</subfield>
    <subfield code="c">21 cm.</subfield>
  </datafield>
  <datafield tag="440" ind1=" " ind2="0">
    <subfield code="a">Oxford library of African literature</subfield>
  </datafield>
  <datafield tag="500" ind1=" " ind2=" ">
    <subfield code="a">Originally published: Oxford : Clarendon Press, 1970.</subfield>
  </datafield>
  <datafield tag="504" ind1=" " ind2=" ">
    <subfield code="a">Includes index and bibliographical references (p. [522]-536).</subfield>
  </datafield>
  <datafield tag="650" ind1=" " ind2="0">
    <subfield code="a">Folk literature, African</subfield>
    <subfield code="x">History and criticism.</subfield>
  </datafield>
  <datafield tag="650" ind1=" " ind2="0">
    <subfield code="a">Oral tradition</subfield>
    <subfield code="z">Africa.</subfield>
  </datafield>
  <datafield tag="922" ind1=" " ind2=" ">
    <subfield code="a">ap</subfield>
  </datafield>
  <datafield tag="991" ind1=" " ind2=" ">
    <subfield code="b">c-GenColl</subfield>
    <subfield code="h">PL8010</subfield>
    <subfield code="i">.F5 1976</subfield>
    <subfield code="t">Copy 1</subfield>
    <subfield code="w">BOOKS</subfield>
  </datafield>
</record>'''

class MarcTests(TestCase):
    work_id=None
    
    def test_records(self):
        w = get_model('core','Work').objects.create(title="Work 1")
        e = get_model('core','Edition').objects.create(title=w.title,work=w) 
        eb = get_model('core','Ebook').objects.create(url = "http://example.org",edition = e,format = 'epub', rights='CC BY')

        mr = models.MARCRecord.objects.create(guts=a_marc_record, edition=e )

        mr.direct_record_xml()
        mr.direct_record_mrc()
        mr.via_record_xml()
        mr.via_record_mrc()
        
        load.stub(e)
        
        w.description='test'
        e.set_publisher('test pub')
        e.publication_date = '2000'
        e.add_author('joe writer')
        id = get_model('core','Identifier').objects.create(work=w,edition=e, type='isbn', value='0030839939') 
        id = get_model('core','Identifier').objects.create(work=w,edition=e, type='oclc', value='0074009772') 
        
        load.stub(e)
        
        mr2 = models.MARCRecord.objects.create(guts=a_marc_record, edition=e )
        mr2.load_from_lc()

        mr2.direct_record_xml()
        mr2.direct_record_mrc()
        mr2.via_record_xml()
        mr2.via_record_mrc()
