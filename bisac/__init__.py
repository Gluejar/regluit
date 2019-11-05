# data from https://github.com/edsu/bisac
class Bisac(object):
    
    def __init__(self):
        self.top_categories ={}
        for key in bisac.keys():
            if bisac[key]['notation'].endswith('000000'):
                top_cat = key.split('/')[0].strip()
                self.top_categories[top_cat] = bisac[key]['notation']
        self.inv_top_categories = {v: k for k, v in self.top_categories.items()}
    
    def code(self, subject):
        top = self.top_categories.get(subject,None)
        if top:
            return top
        return bisac.get(subject, {}).get('notation','')
        
bisac= {
  "Religion / Christian Life / Social Issues": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Social Issues", 
    "notation": "REL012110", 
    "alt_label": []
  }, 
  "Business & Economics / Motivational": {
    "related": [], 
    "pref_label": "Business & Economics / Motivational", 
    "notation": "BUS046000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Catechisms": {
    "related": [], 
    "pref_label": "Religion / Christianity / Catechisms", 
    "notation": "REL009000", 
    "alt_label": [
      "Religion / Catechisms"
    ]
  }, 
  "Biography & Autobiography / Entertainment & Performing Arts": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Entertainment & Performing Arts", 
    "notation": "BIO005000", 
    "alt_label": [
      "Biography & Autobiography / Performing Arts"
    ]
  }, 
  "Political Science / Public Policy / General": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / General", 
    "notation": "POL028000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Family / Parents": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Family / Parents", 
    "notation": "JUV013060", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Comics & Graphic Novels / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Comics & Graphic Novels / General", 
    "notation": "JUV008000", 
    "alt_label": []
  }, 
  "Education / Home Schooling": {
    "related": [], 
    "pref_label": "Education / Home Schooling", 
    "notation": "EDU017000", 
    "alt_label": []
  }, 
  "Computers / Intelligence (ai) & Semantics": {
    "related": [], 
    "pref_label": "Computers / Intelligence (ai) & Semantics", 
    "notation": "COM004000", 
    "alt_label": []
  }, 
  "Philosophy / Methodology": {
    "related": [], 
    "pref_label": "Philosophy / Methodology", 
    "notation": "PHI014000", 
    "alt_label": []
  }, 
  "Social Science / Ethnic Studies / General": {
    "related": [], 
    "pref_label": "Social Science / Ethnic Studies / General", 
    "notation": "SOC008000", 
    "alt_label": []
  }, 
  "History / Europe / Russia & The Former Soviet Union": {
    "related": [], 
    "pref_label": "History / Europe / Russia & The Former Soviet Union", 
    "notation": "HIS032000", 
    "alt_label": [
      "History / Europe / Soviet Union"
    ]
  }, 
  "Bibles / Other Translations / General": {
    "related": [], 
    "pref_label": "Bibles / Other Translations / General", 
    "notation": "BIB018000", 
    "alt_label": []
  }, 
  "Philosophy / Good & Evil": {
    "related": [], 
    "pref_label": "Philosophy / Good & Evil", 
    "notation": "PHI008000", 
    "alt_label": []
  }, 
  "Bibles / New King James Version / Text": {
    "related": [], 
    "pref_label": "Bibles / New King James Version / Text", 
    "notation": "BIB014060", 
    "alt_label": []
  }, 
  "Law / Arbitration, Negotiation, Mediation": {
    "related": [], 
    "pref_label": "Law / Arbitration, Negotiation, Mediation", 
    "notation": "LAW006000", 
    "alt_label": [
      "Law / Mediation", 
      "Law / Negotiation"
    ]
  }, 
  "Language Arts & Disciplines / Library & Information Science / Archives & Special Libraries": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Library & Information Science / Archives & Special Libraries", 
    "notation": "LAN025020", 
    "alt_label": []
  }, 
  "Performing Arts / Television / History & Criticism": {
    "related": [], 
    "pref_label": "Performing Arts / Television / History & Criticism", 
    "notation": "PER010030", 
    "alt_label": []
  }, 
  "Health & Fitness / Allergies": {
    "related": [], 
    "pref_label": "Health & Fitness / Allergies", 
    "notation": "HEA027000", 
    "alt_label": []
  }, 
  "Mathematics / Infinity": {
    "related": [], 
    "pref_label": "Mathematics / Infinity", 
    "notation": "MAT016000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Nursery Rhymes": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Nursery Rhymes", 
    "notation": "JUV055000", 
    "alt_label": []
  }, 
  "Business & Economics / Business Communication / General": {
    "related": [], 
    "pref_label": "Business & Economics / Business Communication / General", 
    "notation": "BUS007000", 
    "alt_label": []
  }, 
  "Architecture / Interior Design / General": {
    "related": [], 
    "pref_label": "Architecture / Interior Design / General", 
    "notation": "ARC007000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Zoos": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Zoos", 
    "notation": "JUV002260", 
    "alt_label": []
  }, 
  "Business & Economics / Small Business": {
    "related": [], 
    "pref_label": "Business & Economics / Small Business", 
    "notation": "BUS060000", 
    "alt_label": []
  }, 
  "Architecture / Individual Architects & Firms / General": {
    "related": [], 
    "pref_label": "Architecture / Individual Architects & Firms / General", 
    "notation": "ARC006000", 
    "alt_label": []
  }, 
  "Gardening / Regional / West (ak, Ca, Co, Hi, Id, Mt, Nv, Ut, Wy)": {
    "related": [], 
    "pref_label": "Gardening / Regional / West (ak, Ca, Co, Hi, Id, Mt, Nv, Ut, Wy)", 
    "notation": "GAR019080", 
    "alt_label": []
  }, 
  "Fiction / Psychological": {
    "related": [], 
    "pref_label": "Fiction / Psychological", 
    "notation": "FIC025000", 
    "alt_label": []
  }, 
  "Art / Techniques / Printmaking": {
    "related": [], 
    "pref_label": "Art / Techniques / Printmaking", 
    "notation": "ART024000", 
    "alt_label": []
  }, 
  "Psychology / Interpersonal Relations": {
    "related": [], 
    "pref_label": "Psychology / Interpersonal Relations", 
    "notation": "PSY017000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Sports": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Sports", 
    "notation": "BIO016000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Church Of Jesus Christ Of Latter-day Saints (mormon)": {
    "related": [], 
    "pref_label": "Religion / Christianity / Church Of Jesus Christ Of Latter-day Saints (mormon)", 
    "notation": "REL046000", 
    "alt_label": [
      "Religion / Christianity / Mormon"
    ]
  }, 
  "Bibles / God's Word / Text": {
    "related": [], 
    "pref_label": "Bibles / God's Word / Text", 
    "notation": "BIB004060", 
    "alt_label": []
  }, 
  "Technology & Engineering / Research": {
    "related": [], 
    "pref_label": "Technology & Engineering / Research", 
    "notation": "TEC066000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Body": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Body", 
    "notation": "JUV009120", 
    "alt_label": []
  }, 
  "Psychology / Psychotherapy / Couples & Family": {
    "related": [], 
    "pref_label": "Psychology / Psychotherapy / Couples & Family", 
    "notation": "PSY041000", 
    "alt_label": []
  }, 
  "Travel / General": {
    "related": [], 
    "pref_label": "Travel / General", 
    "notation": "TRV000000", 
    "alt_label": []
  }, 
  "Humor / Form / Essays": {
    "related": [], 
    "pref_label": "Humor / Form / Essays", 
    "notation": "HUM003000", 
    "alt_label": []
  }, 
  "Nature / Animals / Fish": {
    "related": [], 
    "pref_label": "Nature / Animals / Fish", 
    "notation": "NAT012000", 
    "alt_label": []
  }, 
  "History / Military / Persian Gulf War (1991)": {
    "related": [], 
    "pref_label": "History / Military / Persian Gulf War (1991)", 
    "notation": "HIS027040", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Microbiology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Microbiology", 
    "notation": "SCI045000", 
    "alt_label": []
  }, 
  "Bibles / Christian Standard Bible / Children": {
    "related": [], 
    "pref_label": "Bibles / Christian Standard Bible / Children", 
    "notation": "BIB001010", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / New Thought": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / New Thought", 
    "notation": "OCC014000", 
    "alt_label": []
  }, 
  "Computers / Programming / Algorithms": {
    "related": [], 
    "pref_label": "Computers / Programming / Algorithms", 
    "notation": "COM051300", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Potpourri": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Potpourri", 
    "notation": "CRA027000", 
    "alt_label": []
  }, 
  "Computers / Web / User Generated Content": {
    "related": [], 
    "pref_label": "Computers / Web / User Generated Content", 
    "notation": "COM060150", 
    "alt_label": []
  }, 
  "Technology & Engineering / Sensors": {
    "related": [], 
    "pref_label": "Technology & Engineering / Sensors", 
    "notation": "TEC064000", 
    "alt_label": []
  }, 
  "Bibles / Common English Bible / Children": {
    "related": [], 
    "pref_label": "Bibles / Common English Bible / Children", 
    "notation": "BIB022010", 
    "alt_label": []
  }, 
  "Bibles / Today's New International Version / Children": {
    "related": [], 
    "pref_label": "Bibles / Today's New International Version / Children", 
    "notation": "BIB021010", 
    "alt_label": []
  }, 
  "Technology & Engineering / Electrical": {
    "related": [], 
    "pref_label": "Technology & Engineering / Electrical", 
    "notation": "TEC007000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Foxes": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Foxes", 
    "notation": "JNF003100", 
    "alt_label": []
  }, 
  "Fiction / Mystery & Detective / Women Sleuths": {
    "related": [], 
    "pref_label": "Fiction / Mystery & Detective / Women Sleuths", 
    "notation": "FIC022040", 
    "alt_label": []
  }, 
  "Computers / Security / General": {
    "related": [], 
    "pref_label": "Computers / Security / General", 
    "notation": "COM053000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Jewish & Kosher": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Jewish & Kosher", 
    "notation": "CKB049000", 
    "alt_label": []
  }, 
  "Business & Economics / Marketing / Industrial": {
    "related": [], 
    "pref_label": "Business & Economics / Marketing / Industrial", 
    "notation": "BUS043020", 
    "alt_label": []
  }, 
  "Business & Economics / Insurance / Life": {
    "related": [], 
    "pref_label": "Business & Economics / Insurance / Life", 
    "notation": "BUS033060", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Pets": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Pets", 
    "notation": "JUV002190", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Spirituality / Celtic": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Spirituality / Celtic", 
    "notation": "OCC036010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Cows": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Cows", 
    "notation": "JUV002310", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Business": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Business", 
    "notation": "BIO003000", 
    "alt_label": []
  }, 
  "Computers / Networking / Network Protocols": {
    "related": [], 
    "pref_label": "Computers / Networking / Network Protocols", 
    "notation": "COM043040", 
    "alt_label": []
  }, 
  "Political Science / World / Caribbean & Latin American": {
    "related": [], 
    "pref_label": "Political Science / World / Caribbean & Latin American", 
    "notation": "POL057000", 
    "alt_label": []
  }, 
  "House & Home / Do-it-yourself / General": {
    "related": [], 
    "pref_label": "House & Home / Do-it-yourself / General", 
    "notation": "HOM005000", 
    "alt_label": []
  }, 
  "Social Science / Sociology Of Religion": {
    "related": [], 
    "pref_label": "Social Science / Sociology Of Religion", 
    "notation": "SOC039000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Boys & Men": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Boys & Men", 
    "notation": "JUV005000", 
    "alt_label": [
      "Juvenile Fiction / Men"
    ]
  }, 
  "Law / Malpractice": {
    "related": [], 
    "pref_label": "Law / Malpractice", 
    "notation": "LAW095000", 
    "alt_label": []
  }, 
  "Medical / Audiology & Speech Pathology": {
    "related": [], 
    "pref_label": "Medical / Audiology & Speech Pathology", 
    "notation": "MED007000", 
    "alt_label": [
      "Medical / Hearing", 
      "Medical / Speech Pathology"
    ]
  }, 
  "Games / Sudoku": {
    "related": [], 
    "pref_label": "Games / Sudoku", 
    "notation": "GAM017000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Transportation": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Transportation", 
    "notation": "BUS070100", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Dogs": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Dogs", 
    "notation": "JUV002070", 
    "alt_label": []
  }, 
  "Philosophy / Aesthetics": {
    "related": [], 
    "pref_label": "Philosophy / Aesthetics", 
    "notation": "PHI001000", 
    "alt_label": []
  }, 
  "Gardening / Regional / Southwest (az, Nm, Ok, Tx)": {
    "related": [], 
    "pref_label": "Gardening / Regional / Southwest (az, Nm, Ok, Tx)", 
    "notation": "GAR019070", 
    "alt_label": []
  }, 
  "Study Aids / Mcat (medical College Admission Test)": {
    "related": [], 
    "pref_label": "Study Aids / Mcat (medical College Admission Test)", 
    "notation": "STU032000", 
    "alt_label": []
  }, 
  "Architecture / History / Baroque & Rococo": {
    "related": [], 
    "pref_label": "Architecture / History / Baroque & Rococo", 
    "notation": "ARC005050", 
    "alt_label": []
  }, 
  "Foreign Language Study / Norwegian": {
    "related": [], 
    "pref_label": "Foreign Language Study / Norwegian", 
    "notation": "FOR039000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Middle East": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Middle East", 
    "notation": "JNF038080", 
    "alt_label": []
  }, 
  "Computers / Software Development & Engineering / Quality Assurance & Testing": {
    "related": [], 
    "pref_label": "Computers / Software Development & Engineering / Quality Assurance & Testing", 
    "notation": "COM051330", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Contagious": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Contagious", 
    "notation": "HEA039040", 
    "alt_label": []
  }, 
  "Bibles / Reina Valera / Reference": {
    "related": [], 
    "pref_label": "Bibles / Reina Valera / Reference", 
    "notation": "BIB019040", 
    "alt_label": []
  }, 
  "Games / General": {
    "related": [], 
    "pref_label": "Games / General", 
    "notation": "GAM000000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Values & Virtues": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Values & Virtues", 
    "notation": "JNF049310", 
    "alt_label": []
  }, 
  "Photography / Photojournalism": {
    "related": [], 
    "pref_label": "Photography / Photojournalism", 
    "notation": "PHO015000", 
    "alt_label": []
  }, 
  "Social Science / Holidays (non-religious)": {
    "related": [], 
    "pref_label": "Social Science / Holidays (non-religious)", 
    "notation": "SOC014000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Health & Daily Living": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Health & Daily Living", 
    "notation": "JNF049230", 
    "alt_label": []
  }, 
  "Games / Backgammon": {
    "related": [], 
    "pref_label": "Games / Backgammon", 
    "notation": "GAM001010", 
    "alt_label": [
      "Games / Board / Backgammon"
    ]
  }, 
  "Juvenile Fiction / Animals / Elephants": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Elephants", 
    "notation": "JUV002080", 
    "alt_label": []
  }, 
  "Bibles / New Revised Standard Version / General": {
    "related": [], 
    "pref_label": "Bibles / New Revised Standard Version / General", 
    "notation": "BIB016000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Needlework / Embroidery": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Needlework / Embroidery", 
    "notation": "CRA008000", 
    "alt_label": []
  }, 
  "Gardening / Climatic / General": {
    "related": [], 
    "pref_label": "Gardening / Climatic / General", 
    "notation": "GAR027000", 
    "alt_label": []
  }, 
  "Bibles / New International Reader's Version / Study": {
    "related": [], 
    "pref_label": "Bibles / New International Reader's Version / Study", 
    "notation": "BIB012050", 
    "alt_label": []
  }, 
  "Design / Book": {
    "related": [], 
    "pref_label": "Design / Book", 
    "notation": "DES001000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Dragons, Unicorns & Mythical": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Dragons, Unicorns & Mythical", 
    "notation": "JUV002270", 
    "alt_label": []
  }, 
  "Family & Relationships / Alternative Family": {
    "related": [], 
    "pref_label": "Family & Relationships / Alternative Family", 
    "notation": "FAM006000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Science / Customs, Traditions, Anthropology": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Science / Customs, Traditions, Anthropology", 
    "notation": "JNF052020", 
    "alt_label": []
  }, 
  "Medical / Tropical Medicine": {
    "related": [], 
    "pref_label": "Medical / Tropical Medicine", 
    "notation": "MED097000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Computers / Programming": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Computers / Programming", 
    "notation": "JNF012040", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Stewardship & Giving": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Stewardship & Giving", 
    "notation": "REL063000", 
    "alt_label": [
      "Religion / Stewardship"
    ]
  }, 
  "Business & Economics / Marketing / General": {
    "related": [], 
    "pref_label": "Business & Economics / Marketing / General", 
    "notation": "BUS043000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Diseases, Illnesses & Injuries": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Diseases, Illnesses & Injuries", 
    "notation": "JNF024020", 
    "alt_label": []
  }, 
  "Bibles / New American Standard Bible / Text": {
    "related": [], 
    "pref_label": "Bibles / New American Standard Bible / Text", 
    "notation": "BIB010060", 
    "alt_label": []
  }, 
  "Medical / Physicians": {
    "related": [], 
    "pref_label": "Medical / Physicians", 
    "notation": "MED104000", 
    "alt_label": []
  }, 
  "Computers / Hardware / General": {
    "related": [], 
    "pref_label": "Computers / Hardware / General", 
    "notation": "COM067000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Industrial Technology": {
    "related": [], 
    "pref_label": "Technology & Engineering / Industrial Technology", 
    "notation": "TEC018000", 
    "alt_label": []
  }, 
  "Law / Depositions": {
    "related": [], 
    "pref_label": "Law / Depositions", 
    "notation": "LAW029000", 
    "alt_label": []
  }, 
  "Social Science / Gerontology": {
    "related": [], 
    "pref_label": "Social Science / Gerontology", 
    "notation": "SOC013000", 
    "alt_label": []
  }, 
  "Medical / Forensic Medicine": {
    "related": [], 
    "pref_label": "Medical / Forensic Medicine", 
    "notation": "MED030000", 
    "alt_label": []
  }, 
  "Bibles / New Century Version / Children": {
    "related": [], 
    "pref_label": "Bibles / New Century Version / Children", 
    "notation": "BIB011010", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Study & Teaching": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Study & Teaching", 
    "notation": "LAN020000", 
    "alt_label": []
  }, 
  "Business & Economics / Bookkeeping": {
    "related": [], 
    "pref_label": "Business & Economics / Bookkeeping", 
    "notation": "BUS005000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / United States / Native American": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / United States / Native American", 
    "notation": "JUV011040", 
    "alt_label": []
  }, 
  "Education / Multicultural Education": {
    "related": [], 
    "pref_label": "Education / Multicultural Education", 
    "notation": "EDU020000", 
    "alt_label": []
  }, 
  "Nature / Animals / Wildlife": {
    "related": [], 
    "pref_label": "Nature / Animals / Wildlife", 
    "notation": "NAT037000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Holidays & Celebrations / Passover": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Holidays & Celebrations / Passover", 
    "notation": "JNF026120", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Health & Daily Living / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Health & Daily Living / General", 
    "notation": "JUV015000", 
    "alt_label": []
  }, 
  "Bibles / God's Word / Children": {
    "related": [], 
    "pref_label": "Bibles / God's Word / Children", 
    "notation": "BIB004010", 
    "alt_label": []
  }, 
  "Fiction / Suspense": {
    "related": [], 
    "pref_label": "Fiction / Suspense", 
    "notation": "FIC030000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Zoology / General": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Zoology / General", 
    "notation": "SCI070000", 
    "alt_label": []
  }, 
  "Medical / Surgery / Neurosurgery": {
    "related": [], 
    "pref_label": "Medical / Surgery / Neurosurgery", 
    "notation": "MED085010", 
    "alt_label": [
      "Medical / Neurosurgery"
    ]
  }, 
  "Sports & Recreation / Sailing": {
    "related": [], 
    "pref_label": "Sports & Recreation / Sailing", 
    "notation": "SPO036000", 
    "alt_label": []
  }, 
  "Business & Economics / Organizational Behavior": {
    "related": [], 
    "pref_label": "Business & Economics / Organizational Behavior", 
    "notation": "BUS085000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Hockey": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Hockey", 
    "notation": "JUV032110", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Parapsychology / Out-of-body Experience": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Parapsychology / Out-of-body Experience", 
    "notation": "OCC035000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Transportation / Cars & Trucks": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Transportation / Cars & Trucks", 
    "notation": "JUV041030", 
    "alt_label": []
  }, 
  "Religion / Christian Ministry / Youth": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / Youth", 
    "notation": "REL109030", 
    "alt_label": []
  }, 
  "Health & Fitness / Men's Health": {
    "related": [], 
    "pref_label": "Health & Fitness / Men's Health", 
    "notation": "HEA015000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Fiber Optics": {
    "related": [], 
    "pref_label": "Technology & Engineering / Fiber Optics", 
    "notation": "TEC011000", 
    "alt_label": []
  }, 
  "Psychology / Psychotherapy / General": {
    "related": [], 
    "pref_label": "Psychology / Psychotherapy / General", 
    "notation": "PSY028000", 
    "alt_label": []
  }, 
  "Religion / Eschatology": {
    "related": [], 
    "pref_label": "Religion / Eschatology", 
    "notation": "REL085000", 
    "alt_label": []
  }, 
  "Psychology / Suicide": {
    "related": [], 
    "pref_label": "Psychology / Suicide", 
    "notation": "PSY037000", 
    "alt_label": []
  }, 
  "Education / Educational Psychology": {
    "related": [], 
    "pref_label": "Education / Educational Psychology", 
    "notation": "EDU009000", 
    "alt_label": []
  }, 
  "Political Science / American Government / Judicial Branch": {
    "related": [], 
    "pref_label": "Political Science / American Government / Judicial Branch", 
    "notation": "POL040030", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Linguistics / Syntax": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Linguistics / Syntax", 
    "notation": "LAN009060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Cows": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Cows", 
    "notation": "JNF003260", 
    "alt_label": []
  }, 
  "Sports & Recreation / General": {
    "related": [], 
    "pref_label": "Sports & Recreation / General", 
    "notation": "SPO000000", 
    "alt_label": []
  }, 
  "Business & Economics / Accounting / Financial": {
    "related": [], 
    "pref_label": "Business & Economics / Accounting / Financial", 
    "notation": "BUS001010", 
    "alt_label": []
  }, 
  "Medical / Nursing / Critical & Intensive Care": {
    "related": [], 
    "pref_label": "Medical / Nursing / Critical & Intensive Care", 
    "notation": "MED058030", 
    "alt_label": []
  }, 
  "Science / Acoustics & Sound": {
    "related": [], 
    "pref_label": "Science / Acoustics & Sound", 
    "notation": "SCI001000", 
    "alt_label": [
      "Science / Sound"
    ]
  }, 
  "Music / Genres & Styles / Choral": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Choral", 
    "notation": "MUS051000", 
    "alt_label": []
  }, 
  "Fiction / Classics": {
    "related": [], 
    "pref_label": "Fiction / Classics", 
    "notation": "FIC004000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Mining": {
    "related": [], 
    "pref_label": "Technology & Engineering / Mining", 
    "notation": "TEC026000", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Game": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Game", 
    "notation": "CKB032000", 
    "alt_label": []
  }, 
  "Fiction / Religious": {
    "related": [], 
    "pref_label": "Fiction / Religious", 
    "notation": "FIC026000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / Africa": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Africa", 
    "notation": "JUV030010", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Children": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Children", 
    "notation": "PHO023020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Performing Arts / Dance": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Performing Arts / Dance", 
    "notation": "JNF039020", 
    "alt_label": []
  }, 
  "Business & Economics / Insurance / Risk Assessment & Management": {
    "related": [], 
    "pref_label": "Business & Economics / Insurance / Risk Assessment & Management", 
    "notation": "BUS033070", 
    "alt_label": [
      "Business & Economics / Risk Assessment & Management"
    ]
  }, 
  "Reference / Word Lists": {
    "related": [], 
    "pref_label": "Reference / Word Lists", 
    "notation": "REF025000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Games & Activities / Magic": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Games & Activities / Magic", 
    "notation": "JNF021030", 
    "alt_label": []
  }, 
  "Computers / Expert Systems": {
    "related": [], 
    "pref_label": "Computers / Expert Systems", 
    "notation": "COM025000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Robotics": {
    "related": [], 
    "pref_label": "Technology & Engineering / Robotics", 
    "notation": "TEC037000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Sports": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Sports", 
    "notation": "CGN004200", 
    "alt_label": []
  }, 
  "Religion / Christianity / Baptist": {
    "related": [], 
    "pref_label": "Religion / Christianity / Baptist", 
    "notation": "REL073000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Textiles & Polymers": {
    "related": [], 
    "pref_label": "Technology & Engineering / Textiles & Polymers", 
    "notation": "TEC055000", 
    "alt_label": [
      "Technology & Engineering / Polymers"
    ]
  }, 
  "Study Aids / Sat": {
    "related": [], 
    "pref_label": "Study Aids / Sat", 
    "notation": "STU024000", 
    "alt_label": []
  }, 
  "Transportation / Ships & Shipbuilding / Repair & Maintenance": {
    "related": [], 
    "pref_label": "Transportation / Ships & Shipbuilding / Repair & Maintenance", 
    "notation": "TRA006030", 
    "alt_label": []
  }, 
  "Travel / United States / West / Pacific (ak, Ca, Hi, Nv, Or, Wa)": {
    "related": [], 
    "pref_label": "Travel / United States / West / Pacific (ak, Ca, Hi, Nv, Or, Wa)", 
    "notation": "TRV025130", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Performing Arts / Television & Radio": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Performing Arts / Television & Radio", 
    "notation": "JUV031050", 
    "alt_label": []
  }, 
  "Law / Comparative": {
    "related": [], 
    "pref_label": "Law / Comparative", 
    "notation": "LAW016000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Asia": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Asia", 
    "notation": "JUV016030", 
    "alt_label": []
  }, 
  "Science / Mechanics / General": {
    "related": [], 
    "pref_label": "Science / Mechanics / General", 
    "notation": "SCI041000", 
    "alt_label": []
  }, 
  "Social Science / Statistics": {
    "related": [], 
    "pref_label": "Social Science / Statistics", 
    "notation": "SOC027000", 
    "alt_label": []
  }, 
  "Science / Mechanics / Hydrodynamics": {
    "related": [], 
    "pref_label": "Science / Mechanics / Hydrodynamics", 
    "notation": "SCI095000", 
    "alt_label": []
  }, 
  "Poetry / Subjects & Themes / Death": {
    "related": [], 
    "pref_label": "Poetry / Subjects & Themes / Death", 
    "notation": "POE023010", 
    "alt_label": []
  }, 
  "Science / General": {
    "related": [], 
    "pref_label": "Science / General", 
    "notation": "SCI000000", 
    "alt_label": []
  }, 
  "Political Science / American Government / State & Provincial": {
    "related": [], 
    "pref_label": "Political Science / American Government / State & Provincial", 
    "notation": "POL020000", 
    "alt_label": []
  }, 
  "Religion / Christian Church / Administration": {
    "related": [], 
    "pref_label": "Religion / Christian Church / Administration", 
    "notation": "REL014000", 
    "alt_label": [
      "Religion / Church Administration"
    ]
  }, 
  "Juvenile Fiction / Paranormal": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Paranormal", 
    "notation": "JUV058000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Insects, Spiders, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Insects, Spiders, Etc.", 
    "notation": "JUV002140", 
    "alt_label": []
  }, 
  "Music / Printed Music / Vocal": {
    "related": [], 
    "pref_label": "Music / Printed Music / Vocal", 
    "notation": "MUS037110", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Sports & Recreation": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Sports & Recreation", 
    "notation": "JNF049300", 
    "alt_label": []
  }, 
  "Science / Electron Microscopes & Microscopy": {
    "related": [], 
    "pref_label": "Science / Electron Microscopes & Microscopy", 
    "notation": "SCI023000", 
    "alt_label": []
  }, 
  "Music / Musical Instruments / General": {
    "related": [], 
    "pref_label": "Music / Musical Instruments / General", 
    "notation": "MUS023000", 
    "alt_label": []
  }, 
  "Gardening / General": {
    "related": [], 
    "pref_label": "Gardening / General", 
    "notation": "GAR000000", 
    "alt_label": []
  }, 
  "Business & Economics / Careers / Resumes": {
    "related": [], 
    "pref_label": "Business & Economics / Careers / Resumes", 
    "notation": "BUS056030", 
    "alt_label": [
      "Business & Economics / Resumes"
    ]
  }, 
  "Education / Counseling / Crisis Management": {
    "related": [], 
    "pref_label": "Education / Counseling / Crisis Management", 
    "notation": "EDU045000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Developmental Biology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Developmental Biology", 
    "notation": "SCI072000", 
    "alt_label": []
  }, 
  "Political Science / Public Affairs & Administration": {
    "related": [], 
    "pref_label": "Political Science / Public Affairs & Administration", 
    "notation": "POL017000", 
    "alt_label": []
  }, 
  "Law / Sports": {
    "related": [], 
    "pref_label": "Law / Sports", 
    "notation": "LAW084000", 
    "alt_label": []
  }, 
  "Study Aids / Act": {
    "related": [], 
    "pref_label": "Study Aids / Act", 
    "notation": "STU001000", 
    "alt_label": []
  }, 
  "Business & Economics / Accounting/general": {
    "related": [], 
    "pref_label": "Business & Economics / Accounting/general", 
    "notation": "BUS001000", 
    "alt_label": []
  }, 
  "Study Aids / Study Guides": {
    "related": [], 
    "pref_label": "Study Aids / Study Guides", 
    "notation": "STU026000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Games & Activities / Questions & Answers": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Games & Activities / Questions & Answers", 
    "notation": "JNF021050", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / United States / 19th Century": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / United States / 19th Century", 
    "notation": "JUV016140", 
    "alt_label": []
  }, 
  "Social Science / Women's Studies": {
    "related": [], 
    "pref_label": "Social Science / Women's Studies", 
    "notation": "SOC028000", 
    "alt_label": []
  }, 
  "Religion / Eckankar": {
    "related": [], 
    "pref_label": "Religion / Eckankar", 
    "notation": "REL107000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Ice & Figure Skating": {
    "related": [], 
    "pref_label": "Sports & Recreation / Ice & Figure Skating", 
    "notation": "SPO023000", 
    "alt_label": [
      "Sports & Recreation / Figure Skating"
    ]
  }, 
  "History / Jewish": {
    "related": [], 
    "pref_label": "History / Jewish", 
    "notation": "HIS022000", 
    "alt_label": []
  }, 
  "Art / American / African American": {
    "related": [], 
    "pref_label": "Art / American / African American", 
    "notation": "ART038000", 
    "alt_label": []
  }, 
  "Design / General": {
    "related": [], 
    "pref_label": "Design / General", 
    "notation": "DES000000", 
    "alt_label": []
  }, 
  "Social Science / Minority Studies": {
    "related": [], 
    "pref_label": "Social Science / Minority Studies", 
    "notation": "SOC020000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Dye": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Dye", 
    "notation": "CRA007000", 
    "alt_label": []
  }, 
  "Religion / Sermons / General": {
    "related": [], 
    "pref_label": "Religion / Sermons / General", 
    "notation": "REL058000", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Landscapes": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Landscapes", 
    "notation": "PHO023040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Prehistory": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Prehistory", 
    "notation": "JUV016090", 
    "alt_label": []
  }, 
  "Technology & Engineering / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / General", 
    "notation": "TEC000000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Farm Animals": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Farm Animals", 
    "notation": "JUV002090", 
    "alt_label": []
  }, 
  "Bibles / Reina Valera / General": {
    "related": [], 
    "pref_label": "Bibles / Reina Valera / General", 
    "notation": "BIB019000", 
    "alt_label": []
  }, 
  "Family & Relationships / Eldercare": {
    "related": [], 
    "pref_label": "Family & Relationships / Eldercare", 
    "notation": "FAM017000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / General", 
    "notation": "JUV030000", 
    "alt_label": []
  }, 
  "Family & Relationships / Abuse / Domestic Partner Abuse": {
    "related": [], 
    "pref_label": "Family & Relationships / Abuse / Domestic Partner Abuse", 
    "notation": "FAM001030", 
    "alt_label": []
  }, 
  "Literary Collections / European / English, Irish, Scottish, Welsh": {
    "related": [], 
    "pref_label": "Literary Collections / European / English, Irish, Scottish, Welsh", 
    "notation": "LCO009000", 
    "alt_label": []
  }, 
  "Social Science / Emigration & Immigration": {
    "related": [], 
    "pref_label": "Social Science / Emigration & Immigration", 
    "notation": "SOC007000", 
    "alt_label": [
      "Social Science / Immigration"
    ]
  }, 
  "Music / Religious / Muslim": {
    "related": [], 
    "pref_label": "Music / Religious / Muslim", 
    "notation": "MUS048030", 
    "alt_label": []
  }, 
  "Cooking / Methods / Quick & Easy": {
    "related": [], 
    "pref_label": "Cooking / Methods / Quick & Easy", 
    "notation": "CKB070000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Environmental / Water Supply": {
    "related": [], 
    "pref_label": "Technology & Engineering / Environmental / Water Supply", 
    "notation": "TEC010030", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Fortran": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Fortran", 
    "notation": "COM051090", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Friendship": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Friendship", 
    "notation": "JUV033120", 
    "alt_label": []
  }, 
  "Religion / Christianity / Calvinist": {
    "related": [], 
    "pref_label": "Religion / Christianity / Calvinist", 
    "notation": "REL093000", 
    "alt_label": []
  }, 
  "Social Science / Ethnic Studies / African American Studies": {
    "related": [], 
    "pref_label": "Social Science / Ethnic Studies / African American Studies", 
    "notation": "SOC001000", 
    "alt_label": [
      "Social Science / African American Studies"
    ]
  }, 
  "Law / Business & Financial": {
    "related": [], 
    "pref_label": "Law / Business & Financial", 
    "notation": "LAW009000", 
    "alt_label": [
      "Law / Franchising"
    ]
  }, 
  "Comics & Graphic Novels / Anthologies": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Anthologies", 
    "notation": "CGN001000", 
    "alt_label": []
  }, 
  "Business & Economics / International / Economics": {
    "related": [], 
    "pref_label": "Business & Economics / International / Economics", 
    "notation": "BUS069020", 
    "alt_label": [
      "Business & Economics / Economics / International"
    ]
  }, 
  "Computers / Programming Languages / Vbscript": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Vbscript", 
    "notation": "COM051420", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / International": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / International", 
    "notation": "MUS024000", 
    "alt_label": []
  }, 
  "Computers / Data Transmission Systems / Wireless": {
    "related": [], 
    "pref_label": "Computers / Data Transmission Systems / Wireless", 
    "notation": "COM020090", 
    "alt_label": []
  }, 
  "Literary Collections / European / Scandinavian": {
    "related": [], 
    "pref_label": "Literary Collections / European / Scandinavian", 
    "notation": "LCO008050", 
    "alt_label": []
  }, 
  "Science / Physics / Mathematical & Computational": {
    "related": [], 
    "pref_label": "Science / Physics / Mathematical & Computational", 
    "notation": "SCI040000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Monsters": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Monsters", 
    "notation": "JUV052000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Origami": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Origami", 
    "notation": "CRA023000", 
    "alt_label": []
  }, 
  "Art / History / Prehistoric & Primitive": {
    "related": [], 
    "pref_label": "Art / History / Prehistoric & Primitive", 
    "notation": "ART015050", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Study Aids / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Study Aids / General", 
    "notation": "JNF055000", 
    "alt_label": []
  }, 
  "Computers / Systems Architecture / General": {
    "related": [], 
    "pref_label": "Computers / Systems Architecture / General", 
    "notation": "COM011000", 
    "alt_label": []
  }, 
  "Business & Economics / Management": {
    "related": [], 
    "pref_label": "Business & Economics / Management", 
    "notation": "BUS041000", 
    "alt_label": []
  }, 
  "Fiction / Christian / General": {
    "related": [], 
    "pref_label": "Fiction / Christian / General", 
    "notation": "FIC042000", 
    "alt_label": []
  }, 
  "Nature / Fossils": {
    "related": [], 
    "pref_label": "Nature / Fossils", 
    "notation": "NAT015000", 
    "alt_label": []
  }, 
  "Study Aids / Armed Forces": {
    "related": [], 
    "pref_label": "Study Aids / Armed Forces", 
    "notation": "STU003000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Humorous": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Humorous", 
    "notation": "JUV033160", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Books": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Books", 
    "notation": "ANT005000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Wrestling": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Wrestling", 
    "notation": "JUV032160", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Reference": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Reference", 
    "notation": "ANT038000", 
    "alt_label": []
  }, 
  "Poetry / Canadian": {
    "related": [], 
    "pref_label": "Poetry / Canadian", 
    "notation": "POE011000", 
    "alt_label": []
  }, 
  "Law / Research": {
    "related": [], 
    "pref_label": "Law / Research", 
    "notation": "LAW081000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Easter & Lent": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Easter & Lent", 
    "notation": "JUV017020", 
    "alt_label": []
  }, 
  "Religion / Islam / General": {
    "related": [], 
    "pref_label": "Religion / Islam / General", 
    "notation": "REL037000", 
    "alt_label": []
  }, 
  "Business & Economics / International / Taxation": {
    "related": [], 
    "pref_label": "Business & Economics / International / Taxation", 
    "notation": "BUS064020", 
    "alt_label": [
      "Business & Economics / Taxation / International"
    ]
  }, 
  "Architecture / History / Prehistoric & Primitive": {
    "related": [], 
    "pref_label": "Architecture / History / Prehistoric & Primitive", 
    "notation": "ARC005010", 
    "alt_label": []
  }, 
  "Philosophy / Hindu": {
    "related": [], 
    "pref_label": "Philosophy / Hindu", 
    "notation": "PHI033000", 
    "alt_label": []
  }, 
  "Bibles / Reina Valera / Children": {
    "related": [], 
    "pref_label": "Bibles / Reina Valera / Children", 
    "notation": "BIB019010", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Humanism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Humanism", 
    "notation": "PHI010000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Civil / Flood Control": {
    "related": [], 
    "pref_label": "Technology & Engineering / Civil / Flood Control", 
    "notation": "TEC009130", 
    "alt_label": []
  }, 
  "Literary Criticism / Renaissance": {
    "related": [], 
    "pref_label": "Literary Criticism / Renaissance", 
    "notation": "LIT019000", 
    "alt_label": []
  }, 
  "Performing Arts / Animation": {
    "related": [], 
    "pref_label": "Performing Arts / Animation", 
    "notation": "PER017000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Law & Crime": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Law & Crime", 
    "notation": "JNF030000", 
    "alt_label": [
      "Juvenile Nonfiction / Crime"
    ]
  }, 
  "Juvenile Nonfiction / Social Issues / Drugs, Alcohol, Substance Abuse": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Drugs, Alcohol, Substance Abuse", 
    "notation": "JNF053040", 
    "alt_label": [
      "Juvenile Nonfiction / Social Issues / Substance Abuse"
    ]
  }, 
  "Art / Subjects & Themes / Plants & Animals": {
    "related": [], 
    "pref_label": "Art / Subjects & Themes / Plants & Animals", 
    "notation": "ART050030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Mexico": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Mexico", 
    "notation": "JNF025110", 
    "alt_label": []
  }, 
  "History / Europe / General": {
    "related": [], 
    "pref_label": "History / Europe / General", 
    "notation": "HIS010000", 
    "alt_label": []
  }, 
  "Religion / Clergy": {
    "related": [], 
    "pref_label": "Religion / Clergy", 
    "notation": "REL081000", 
    "alt_label": []
  }, 
  "Literary Collections / Canadian": {
    "related": [], 
    "pref_label": "Literary Collections / Canadian", 
    "notation": "LCO006000", 
    "alt_label": []
  }, 
  "History / Ancient / Egypt": {
    "related": [], 
    "pref_label": "History / Ancient / Egypt", 
    "notation": "HIS002030", 
    "alt_label": [
      "History / Africa / Egypt"
    ]
  }, 
  "Architecture / General": {
    "related": [], 
    "pref_label": "Architecture / General", 
    "notation": "ARC000000", 
    "alt_label": []
  }, 
  "Music / Musical Instruments / Guitar": {
    "related": [], 
    "pref_label": "Music / Musical Instruments / Guitar", 
    "notation": "MUS023060", 
    "alt_label": []
  }, 
  "Medical / Physical Medicine & Rehabilitation": {
    "related": [], 
    "pref_label": "Medical / Physical Medicine & Rehabilitation", 
    "notation": "MED073000", 
    "alt_label": [
      "Medical / Diseases / Neuromuscular"
    ]
  }, 
  "Nature / Animals / Marine Life": {
    "related": [], 
    "pref_label": "Nature / Animals / Marine Life", 
    "notation": "NAT020000", 
    "alt_label": []
  }, 
  "Reference / Genealogy & Heraldry": {
    "related": [], 
    "pref_label": "Reference / Genealogy & Heraldry", 
    "notation": "REF013000", 
    "alt_label": []
  }, 
  "Games / Word & Word Search": {
    "related": [], 
    "pref_label": "Games / Word & Word Search", 
    "notation": "GAM014000", 
    "alt_label": []
  }, 
  "Medical / Psychiatry / General": {
    "related": [], 
    "pref_label": "Medical / Psychiatry / General", 
    "notation": "MED105000", 
    "alt_label": []
  }, 
  "Law / Mergers & Acquisitions": {
    "related": [], 
    "pref_label": "Law / Mergers & Acquisitions", 
    "notation": "LAW114000", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Desserts": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Desserts", 
    "notation": "CKB024000", 
    "alt_label": []
  }, 
  "Medical / Pathophysiology": {
    "related": [], 
    "pref_label": "Medical / Pathophysiology", 
    "notation": "MED068000", 
    "alt_label": []
  }, 
  "Bibles / New Century Version / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / New Century Version / New Testament & Portions", 
    "notation": "BIB011030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Comics & Graphic Novels / History": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Comics & Graphic Novels / History", 
    "notation": "JNF062020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Legends, Myths, Fables / Greek & Roman": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Legends, Myths, Fables / Greek & Roman", 
    "notation": "JUV022020", 
    "alt_label": []
  }, 
  "Nature / Animals / Horses": {
    "related": [], 
    "pref_label": "Nature / Animals / Horses", 
    "notation": "NAT016000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / American / Southwestern States": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / American / Southwestern States", 
    "notation": "CKB002070", 
    "alt_label": []
  }, 
  "Medical / Chiropractic": {
    "related": [], 
    "pref_label": "Medical / Chiropractic", 
    "notation": "MED013000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Mathematics / Algebra": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Mathematics / Algebra", 
    "notation": "JNF035020", 
    "alt_label": []
  }, 
  "Bibles / English Standard Version / Text": {
    "related": [], 
    "pref_label": "Bibles / English Standard Version / Text", 
    "notation": "BIB003060", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / Agronomy / Crop Science": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / Agronomy / Crop Science", 
    "notation": "TEC003030", 
    "alt_label": []
  }, 
  "Technology & Engineering / Surveying": {
    "related": [], 
    "pref_label": "Technology & Engineering / Surveying", 
    "notation": "TEC054000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Construction / Roofing": {
    "related": [], 
    "pref_label": "Technology & Engineering / Construction / Roofing", 
    "notation": "TEC005080", 
    "alt_label": []
  }, 
  "Music / Instruction & Study / Exercises": {
    "related": [], 
    "pref_label": "Music / Instruction & Study / Exercises", 
    "notation": "MUS016000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Crime & Mystery": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Crime & Mystery", 
    "notation": "CGN004010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Technology / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Technology / General", 
    "notation": "JNF061000", 
    "alt_label": []
  }, 
  "Religion / Hinduism / History": {
    "related": [], 
    "pref_label": "Religion / Hinduism / History", 
    "notation": "REL032010", 
    "alt_label": []
  }, 
  "History / Americas (north, Central, South, West Indies)": {
    "related": [], 
    "pref_label": "History / Americas (north, Central, South, West Indies)", 
    "notation": "HIS038000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Humor / Comic Strips & Cartoons": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Humor / Comic Strips & Cartoons", 
    "notation": "JNF028010", 
    "alt_label": []
  }, 
  "Social Science / Future Studies": {
    "related": [], 
    "pref_label": "Social Science / Future Studies", 
    "notation": "SOC037000", 
    "alt_label": []
  }, 
  "Poetry / European / Italian": {
    "related": [], 
    "pref_label": "Poetry / European / Italian", 
    "notation": "POE019000", 
    "alt_label": []
  }, 
  "Art / Techniques / Sculpting": {
    "related": [], 
    "pref_label": "Art / Techniques / Sculpting", 
    "notation": "ART053000", 
    "alt_label": []
  }, 
  "Art / Russian & Former Soviet Union": {
    "related": [], 
    "pref_label": "Art / Russian & Former Soviet Union", 
    "notation": "ART049000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Television & Video": {
    "related": [], 
    "pref_label": "Technology & Engineering / Television & Video", 
    "notation": "TEC043000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Science Fiction": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Science Fiction", 
    "notation": "CGN004190", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Sewing": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Sewing", 
    "notation": "CRA035000", 
    "alt_label": []
  }, 
  "Art / Caribbean & Latin American": {
    "related": [], 
    "pref_label": "Art / Caribbean & Latin American", 
    "notation": "ART044000", 
    "alt_label": [
      "Art / Latin American"
    ]
  }, 
  "Bibles / New Living Translation / Devotional": {
    "related": [], 
    "pref_label": "Bibles / New Living Translation / Devotional", 
    "notation": "BIB015020", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Biology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Biology", 
    "notation": "SCI008000", 
    "alt_label": []
  }, 
  "Performing Arts / Dance / Jazz": {
    "related": [], 
    "pref_label": "Performing Arts / Dance / Jazz", 
    "notation": "PER003030", 
    "alt_label": []
  }, 
  "Law / Real Estate": {
    "related": [], 
    "pref_label": "Law / Real Estate", 
    "notation": "LAW078000", 
    "alt_label": []
  }, 
  "Education / Counseling / Career Guidance": {
    "related": [], 
    "pref_label": "Education / Counseling / Career Guidance", 
    "notation": "EDU031000", 
    "alt_label": []
  }, 
  "Fiction / Gay": {
    "related": [], 
    "pref_label": "Fiction / Gay", 
    "notation": "FIC011000", 
    "alt_label": []
  }, 
  "Gardening / Climatic / Tropical": {
    "related": [], 
    "pref_label": "Gardening / Climatic / Tropical", 
    "notation": "GAR027030", 
    "alt_label": []
  }, 
  "Fiction / Westerns": {
    "related": [], 
    "pref_label": "Fiction / Westerns", 
    "notation": "FIC033000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Divination / General": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Divination / General", 
    "notation": "OCC005000", 
    "alt_label": [
      "Body, Mind & Spirit / Dowsing"
    ]
  }, 
  "Juvenile Fiction / Mysteries & Detective Stories": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Mysteries & Detective Stories", 
    "notation": "JUV028000", 
    "alt_label": [
      "Juvenile Fiction / Detective Stories"
    ]
  }, 
  "Travel / Australia & Oceania": {
    "related": [], 
    "pref_label": "Travel / Australia & Oceania", 
    "notation": "TRV004000", 
    "alt_label": [
      "Travel / Oceania"
    ]
  }, 
  "Bibles / New Century Version / Devotional": {
    "related": [], 
    "pref_label": "Bibles / New Century Version / Devotional", 
    "notation": "BIB011020", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Folkcrafts": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Folkcrafts", 
    "notation": "CRA047000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Gay & Lesbian": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Gay & Lesbian", 
    "notation": "CGN004130", 
    "alt_label": []
  }, 
  "Self-help / Personal Growth / Memory Improvement": {
    "related": [], 
    "pref_label": "Self-help / Personal Growth / Memory Improvement", 
    "notation": "SEL030000", 
    "alt_label": [
      "Self-help / Memory Improvement"
    ]
  }, 
  "Juvenile Fiction / Social Issues / Special Needs": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Special Needs", 
    "notation": "JUV039150", 
    "alt_label": []
  }, 
  "Religion / Christianity / Mennonite": {
    "related": [], 
    "pref_label": "Religion / Christianity / Mennonite", 
    "notation": "REL043000", 
    "alt_label": []
  }, 
  "Design / Graphic Arts / Commercial & Corporate": {
    "related": [], 
    "pref_label": "Design / Graphic Arts / Commercial & Corporate", 
    "notation": "DES007030", 
    "alt_label": []
  }, 
  "Science / Chemistry / Toxicology": {
    "related": [], 
    "pref_label": "Science / Chemistry / Toxicology", 
    "notation": "SCI013090", 
    "alt_label": []
  }, 
  "Technology & Engineering / Power Resources / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / Power Resources / General", 
    "notation": "TEC031000", 
    "alt_label": []
  }, 
  "History / Military / Afghan War (2001-)": {
    "related": [], 
    "pref_label": "History / Military / Afghan War (2001-)", 
    "notation": "HIS027190", 
    "alt_label": []
  }, 
  "Drama / African": {
    "related": [], 
    "pref_label": "Drama / African", 
    "notation": "DRA011000", 
    "alt_label": []
  }, 
  "Business & Economics / Office Management": {
    "related": [], 
    "pref_label": "Business & Economics / Office Management", 
    "notation": "BUS096000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Butterflies, Moths & Caterpillars": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Butterflies, Moths & Caterpillars", 
    "notation": "JUV002300", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Rabbits": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Rabbits", 
    "notation": "JUV002210", 
    "alt_label": []
  }, 
  "Business & Economics / Public Finance": {
    "related": [], 
    "pref_label": "Business & Economics / Public Finance", 
    "notation": "BUS051000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Other, Religious": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Other, Religious", 
    "notation": "JUV017090", 
    "alt_label": []
  }, 
  "Political Science / World / Russian &  Former Soviet Union": {
    "related": [], 
    "pref_label": "Political Science / World / Russian &  Former Soviet Union", 
    "notation": "POL060000", 
    "alt_label": []
  }, 
  "Fiction / Mystery & Detective / Traditional British": {
    "related": [], 
    "pref_label": "Fiction / Mystery & Detective / Traditional British", 
    "notation": "FIC022030", 
    "alt_label": []
  }, 
  "Literary Criticism / Ancient & Classical": {
    "related": [], 
    "pref_label": "Literary Criticism / Ancient & Classical", 
    "notation": "LIT004190", 
    "alt_label": [
      "Literary Criticism / Classical"
    ]
  }, 
  "Business & Economics / Purchasing & Buying": {
    "related": [], 
    "pref_label": "Business & Economics / Purchasing & Buying", 
    "notation": "BUS076000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Construction / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / Construction / General", 
    "notation": "TEC005000", 
    "alt_label": []
  }, 
  "Bibles / God's Word / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / God's Word / Youth & Teen", 
    "notation": "BIB004070", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Biography & Autobiography / Presidents And First Families (u.s.)": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Biography & Autobiography / Presidents And First Families (u.s.)", 
    "notation": "JNF007130", 
    "alt_label": []
  }, 
  "Art / History / Ancient & Classical": {
    "related": [], 
    "pref_label": "Art / History / Ancient & Classical", 
    "notation": "ART015060", 
    "alt_label": []
  }, 
  "Study Aids / Regents": {
    "related": [], 
    "pref_label": "Study Aids / Regents", 
    "notation": "STU022000", 
    "alt_label": []
  }, 
  "Business & Economics / Women In Business": {
    "related": [], 
    "pref_label": "Business & Economics / Women In Business", 
    "notation": "BUS109000", 
    "alt_label": []
  }, 
  "Music / Business Aspects": {
    "related": [], 
    "pref_label": "Music / Business Aspects", 
    "notation": "MUS004000", 
    "alt_label": []
  }, 
  "Nature / Plants / Aquatic": {
    "related": [], 
    "pref_label": "Nature / Plants / Aquatic", 
    "notation": "NAT047000", 
    "alt_label": []
  }, 
  "Medical / Caregiving": {
    "related": [], 
    "pref_label": "Medical / Caregiving", 
    "notation": "MED011000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Holidays & Celebrations / Patriotic Holidays": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Holidays & Celebrations / Patriotic Holidays", 
    "notation": "JNF026130", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Body": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Body", 
    "notation": "JNF013110", 
    "alt_label": []
  }, 
  "Literary Collections / Australian & Oceanian": {
    "related": [], 
    "pref_label": "Literary Collections / Australian & Oceanian", 
    "notation": "LCO005000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Science Fiction": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Science Fiction", 
    "notation": "CGN004070", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Biographical / European": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Biographical / European", 
    "notation": "JUV004010", 
    "alt_label": []
  }, 
  "Fiction / Horror": {
    "related": [], 
    "pref_label": "Fiction / Horror", 
    "notation": "FIC015000", 
    "alt_label": []
  }, 
  "Travel / Hikes & Walks": {
    "related": [], 
    "pref_label": "Travel / Hikes & Walks", 
    "notation": "TRV034000", 
    "alt_label": []
  }, 
  "Science / Chemistry / General": {
    "related": [], 
    "pref_label": "Science / Chemistry / General", 
    "notation": "SCI013000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Readers / Intermediate": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Readers / Intermediate", 
    "notation": "JUV044000", 
    "alt_label": []
  }, 
  "Self-help / Abuse": {
    "related": [], 
    "pref_label": "Self-help / Abuse", 
    "notation": "SEL001000", 
    "alt_label": []
  }, 
  "Travel / United States / South / East South Central (al, Ky, Ms, Tn)": {
    "related": [], 
    "pref_label": "Travel / United States / South / East South Central (al, Ky, Ms, Tn)", 
    "notation": "TRV025080", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Clothing & Dress": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Clothing & Dress", 
    "notation": "JUV048000", 
    "alt_label": []
  }, 
  "Medical / Immunology": {
    "related": [], 
    "pref_label": "Medical / Immunology", 
    "notation": "MED044000", 
    "alt_label": [
      "Medical / Diseases / Immunological"
    ]
  }, 
  "Law / Witnesses": {
    "related": [], 
    "pref_label": "Law / Witnesses", 
    "notation": "LAW091000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Biography & Autobiography / Art": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Biography & Autobiography / Art", 
    "notation": "JNF007010", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Crafts For Children": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Crafts For Children", 
    "notation": "CRA043000", 
    "alt_label": []
  }, 
  "Literary Collections / Women Authors": {
    "related": [], 
    "pref_label": "Literary Collections / Women Authors", 
    "notation": "LCO019000", 
    "alt_label": []
  }, 
  "Religion / Agnosticism": {
    "related": [], 
    "pref_label": "Religion / Agnosticism", 
    "notation": "REL001000", 
    "alt_label": []
  }, 
  "Performing Arts / Television / General": {
    "related": [], 
    "pref_label": "Performing Arts / Television / General", 
    "notation": "PER010000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / United States / Hispanic & Latino": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / United States / Hispanic & Latino", 
    "notation": "JUV011030", 
    "alt_label": []
  }, 
  "Literary Criticism / Medieval": {
    "related": [], 
    "pref_label": "Literary Criticism / Medieval", 
    "notation": "LIT011000", 
    "alt_label": []
  }, 
  "Gardening / Greenhouses": {
    "related": [], 
    "pref_label": "Gardening / Greenhouses", 
    "notation": "GAR008000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Books & Libraries": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Books & Libraries", 
    "notation": "JUV047000", 
    "alt_label": []
  }, 
  "Science / Weights & Measures": {
    "related": [], 
    "pref_label": "Science / Weights & Measures", 
    "notation": "SCI068000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Philosophers": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Philosophers", 
    "notation": "BIO009000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Violence": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Violence", 
    "notation": "JUV039180", 
    "alt_label": []
  }, 
  "Religion / Christianity / Seventh-day Adventist": {
    "related": [], 
    "pref_label": "Religion / Christianity / Seventh-day Adventist", 
    "notation": "REL098000", 
    "alt_label": []
  }, 
  "Medical / Mental Health": {
    "related": [], 
    "pref_label": "Medical / Mental Health", 
    "notation": "MED102000", 
    "alt_label": []
  }, 
  "Literary Collections / Ancient & Classical": {
    "related": [], 
    "pref_label": "Literary Collections / Ancient & Classical", 
    "notation": "LCO003000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Music / Jazz": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / Jazz", 
    "notation": "JNF036040", 
    "alt_label": []
  }, 
  "Foreign Language Study / Spanish": {
    "related": [], 
    "pref_label": "Foreign Language Study / Spanish", 
    "notation": "FOR026000", 
    "alt_label": []
  }, 
  "Bibles / New American Bible / Study": {
    "related": [], 
    "pref_label": "Bibles / New American Bible / Study", 
    "notation": "BIB009050", 
    "alt_label": []
  }, 
  "Philosophy / History & Surveys / Medieval": {
    "related": [], 
    "pref_label": "Philosophy / History & Surveys / Medieval", 
    "notation": "PHI012000", 
    "alt_label": []
  }, 
  "Gardening / Flowers / Roses": {
    "related": [], 
    "pref_label": "Gardening / Flowers / Roses", 
    "notation": "GAR004060", 
    "alt_label": []
  }, 
  "Medical / Physiology": {
    "related": [], 
    "pref_label": "Medical / Physiology", 
    "notation": "MED075000", 
    "alt_label": [
      "Medical / Diseases / Neuromuscular"
    ]
  }, 
  "Poetry / Caribbean & Latin American": {
    "related": [], 
    "pref_label": "Poetry / Caribbean & Latin American", 
    "notation": "POE012000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Running & Jogging": {
    "related": [], 
    "pref_label": "Sports & Recreation / Running & Jogging", 
    "notation": "SPO035000", 
    "alt_label": [
      "Sports & Recreation / Jogging"
    ]
  }, 
  "Bibles / Multiple Translations / Children": {
    "related": [], 
    "pref_label": "Bibles / Multiple Translations / Children", 
    "notation": "BIB008010", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Mediterranean": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Mediterranean", 
    "notation": "CKB055000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Imaging Systems": {
    "related": [], 
    "pref_label": "Technology & Engineering / Imaging Systems", 
    "notation": "TEC015000", 
    "alt_label": []
  }, 
  "Psychology / Mental Health": {
    "related": [], 
    "pref_label": "Psychology / Mental Health", 
    "notation": "PSY036000", 
    "alt_label": []
  }, 
  "Photography / General": {
    "related": [], 
    "pref_label": "Photography / General", 
    "notation": "PHO000000", 
    "alt_label": []
  }, 
  "Family & Relationships / Adoption & Fostering": {
    "related": [], 
    "pref_label": "Family & Relationships / Adoption & Fostering", 
    "notation": "FAM004000", 
    "alt_label": []
  }, 
  "Bibles / New Living Translation / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / New Living Translation / Youth & Teen", 
    "notation": "BIB015070", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Miniatures": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Miniatures", 
    "notation": "CRA018000", 
    "alt_label": []
  }, 
  "Gardening / Climatic / Temperate": {
    "related": [], 
    "pref_label": "Gardening / Climatic / Temperate", 
    "notation": "GAR027020", 
    "alt_label": []
  }, 
  "Religion / Christianity / Catholic": {
    "related": [], 
    "pref_label": "Religion / Christianity / Catholic", 
    "notation": "REL010000", 
    "alt_label": [
      "Religion / Christianity / Roman Catholic"
    ]
  }, 
  "Business & Economics / Industries / Automobile Industry": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Automobile Industry", 
    "notation": "BUS070020", 
    "alt_label": []
  }, 
  "Reference / Research": {
    "related": [], 
    "pref_label": "Reference / Research", 
    "notation": "REF020000", 
    "alt_label": []
  }, 
  "Literary Criticism / American / Asian American": {
    "related": [], 
    "pref_label": "Literary Criticism / American / Asian American", 
    "notation": "LIT004030", 
    "alt_label": []
  }, 
  "Computers / Desktop Applications / Word Processing": {
    "related": [], 
    "pref_label": "Computers / Desktop Applications / Word Processing", 
    "notation": "COM058000", 
    "alt_label": []
  }, 
  "Nature / Natural Resources": {
    "related": [], 
    "pref_label": "Nature / Natural Resources", 
    "notation": "NAT038000", 
    "alt_label": []
  }, 
  "Self-help / Adult Children Of Substance Abusers": {
    "related": [], 
    "pref_label": "Self-help / Adult Children Of Substance Abusers", 
    "notation": "SEL003000", 
    "alt_label": []
  }, 
  "Law / Living Trusts": {
    "related": [], 
    "pref_label": "Law / Living Trusts", 
    "notation": "LAW100000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Stenciling": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Stenciling", 
    "notation": "CRA036000", 
    "alt_label": []
  }, 
  "Travel / Middle East / Turkey": {
    "related": [], 
    "pref_label": "Travel / Middle East / Turkey", 
    "notation": "TRV015030", 
    "alt_label": []
  }, 
  "Art / Canadian": {
    "related": [], 
    "pref_label": "Art / Canadian", 
    "notation": "ART015040", 
    "alt_label": []
  }, 
  "Technology & Engineering / Aeronautics & Astronautics": {
    "related": [], 
    "pref_label": "Technology & Engineering / Aeronautics & Astronautics", 
    "notation": "TEC002000", 
    "alt_label": [
      "Technology & Engineering / Astronautics"
    ]
  }, 
  "Medical / Dentistry / Periodontics": {
    "related": [], 
    "pref_label": "Medical / Dentistry / Periodontics", 
    "notation": "MED016040", 
    "alt_label": []
  }, 
  "Travel / Europe / Italy": {
    "related": [], 
    "pref_label": "Travel / Europe / Italy", 
    "notation": "TRV009110", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Stuffed Animals": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Stuffed Animals", 
    "notation": "CRA037000", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Dairy": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Dairy", 
    "notation": "CKB096000", 
    "alt_label": []
  }, 
  "Medical / Allied Health Services / Medical Technology": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / Medical Technology", 
    "notation": "MED003040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Equestrian": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Equestrian", 
    "notation": "JNF054170", 
    "alt_label": []
  }, 
  "Gardening / Container": {
    "related": [], 
    "pref_label": "Gardening / Container", 
    "notation": "GAR001000", 
    "alt_label": []
  }, 
  "Health & Fitness / Naturopathy": {
    "related": [], 
    "pref_label": "Health & Fitness / Naturopathy", 
    "notation": "HEA016000", 
    "alt_label": []
  }, 
  "Cooking / Entertaining": {
    "related": [], 
    "pref_label": "Cooking / Entertaining", 
    "notation": "CKB029000", 
    "alt_label": [
      "Cooking / Cigars & Tobacco"
    ]
  }, 
  "Music / Musical Instruments / Strings": {
    "related": [], 
    "pref_label": "Music / Musical Instruments / Strings", 
    "notation": "MUS023040", 
    "alt_label": []
  }, 
  "History / United States / State & Local / Middle Atlantic (dc, De, Md, Nj, Ny, Pa)": {
    "related": [], 
    "pref_label": "History / United States / State & Local / Middle Atlantic (dc, De, Md, Nj, Ny, Pa)", 
    "notation": "HIS036080", 
    "alt_label": []
  }, 
  "Political Science / Political Ideologies / General": {
    "related": [], 
    "pref_label": "Political Science / Political Ideologies / General", 
    "notation": "POL042000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Portuguese": {
    "related": [], 
    "pref_label": "Foreign Language Study / Portuguese", 
    "notation": "FOR020000", 
    "alt_label": []
  }, 
  "Medical / Pain Medicine": {
    "related": [], 
    "pref_label": "Medical / Pain Medicine", 
    "notation": "MED093000", 
    "alt_label": []
  }, 
  "Bibles / New Century Version / General": {
    "related": [], 
    "pref_label": "Bibles / New Century Version / General", 
    "notation": "BIB011000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Polar Regions": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Polar Regions", 
    "notation": "JNF038090", 
    "alt_label": []
  }, 
  "Education / Inclusive Education": {
    "related": [], 
    "pref_label": "Education / Inclusive Education", 
    "notation": "EDU048000", 
    "alt_label": [
      "Education / Mainstreaming"
    ]
  }, 
  "Computers / Document Management": {
    "related": [], 
    "pref_label": "Computers / Document Management", 
    "notation": "COM063000", 
    "alt_label": []
  }, 
  "Transportation / Automotive / Repair & Maintenance": {
    "related": [], 
    "pref_label": "Transportation / Automotive / Repair & Maintenance", 
    "notation": "TRA001140", 
    "alt_label": []
  }, 
  "Medical / Pediatrics": {
    "related": [], 
    "pref_label": "Medical / Pediatrics", 
    "notation": "MED069000", 
    "alt_label": []
  }, 
  "Poetry / Native American": {
    "related": [], 
    "pref_label": "Poetry / Native American", 
    "notation": "POE015000", 
    "alt_label": []
  }, 
  "Music / Discography & Buyer's Guides": {
    "related": [], 
    "pref_label": "Music / Discography & Buyer's Guides", 
    "notation": "MUS012000", 
    "alt_label": [
      "Music / Buyer's Guides"
    ]
  }, 
  "Juvenile Nonfiction / Animals / Ducks, Geese, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Ducks, Geese, Etc.", 
    "notation": "JNF003210", 
    "alt_label": []
  }, 
  "Bibles / Other Translations / Devotional": {
    "related": [], 
    "pref_label": "Bibles / Other Translations / Devotional", 
    "notation": "BIB018020", 
    "alt_label": []
  }, 
  "Family & Relationships / Family Relationships": {
    "related": [], 
    "pref_label": "Family & Relationships / Family Relationships", 
    "notation": "FAM019000", 
    "alt_label": []
  }, 
  "Bibles / Nueva Version International / Text": {
    "related": [], 
    "pref_label": "Bibles / Nueva Version International / Text", 
    "notation": "BIB017060", 
    "alt_label": []
  }, 
  "Design / Furniture": {
    "related": [], 
    "pref_label": "Design / Furniture", 
    "notation": "DES006000", 
    "alt_label": []
  }, 
  "Social Science / People With Disabilities": {
    "related": [], 
    "pref_label": "Social Science / People With Disabilities", 
    "notation": "SOC029000", 
    "alt_label": [
      "Social Science / Disabled", 
      "Social Science / Handicapped"
    ]
  }, 
  "Medical / Optometry": {
    "related": [], 
    "pref_label": "Medical / Optometry", 
    "notation": "MED064000", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Plants & Animals": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Plants & Animals", 
    "notation": "PHO013000", 
    "alt_label": []
  }, 
  "Education / Aims & Objectives": {
    "related": [], 
    "pref_label": "Education / Aims & Objectives", 
    "notation": "EDU003000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Pneumatology": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Pneumatology", 
    "notation": "REL067090", 
    "alt_label": [
      "Religion / Christianity / Holy Spirit"
    ]
  }, 
  "Body, Mind & Spirit / Sacred Sexuality": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Sacred Sexuality", 
    "notation": "OCC041000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Royalty": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Royalty", 
    "notation": "JUV034000", 
    "alt_label": []
  }, 
  "Law / Criminal Procedure": {
    "related": [], 
    "pref_label": "Law / Criminal Procedure", 
    "notation": "LAW027000", 
    "alt_label": []
  }, 
  "Photography / Techniques / Darkroom": {
    "related": [], 
    "pref_label": "Photography / Techniques / Darkroom", 
    "notation": "PHO006000", 
    "alt_label": []
  }, 
  "Medical / Surgery / Transplant": {
    "related": [], 
    "pref_label": "Medical / Surgery / Transplant", 
    "notation": "MED085070", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Lifestyles / Country Life": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Lifestyles / Country Life", 
    "notation": "JUV024000", 
    "alt_label": [
      "Juvenile Fiction / Country Life"
    ]
  }, 
  "Law / Liability": {
    "related": [], 
    "pref_label": "Law / Liability", 
    "notation": "LAW113000", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / Jesus, The Gospels & Acts": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / Jesus, The Gospels & Acts", 
    "notation": "REL006710", 
    "alt_label": []
  }, 
  "History / Military / Canada": {
    "related": [], 
    "pref_label": "History / Military / Canada", 
    "notation": "HIS027160", 
    "alt_label": []
  }, 
  "Science / Gravity": {
    "related": [], 
    "pref_label": "Science / Gravity", 
    "notation": "SCI033000", 
    "alt_label": []
  }, 
  "Family & Relationships / Abuse / General": {
    "related": [], 
    "pref_label": "Family & Relationships / Abuse / General", 
    "notation": "FAM001000", 
    "alt_label": []
  }, 
  "Travel / Europe / Iceland & Greenland": {
    "related": [], 
    "pref_label": "Travel / Europe / Iceland & Greenland", 
    "notation": "TRV009090", 
    "alt_label": []
  }, 
  "Religion / Judaism / Theology": {
    "related": [], 
    "pref_label": "Religion / Judaism / Theology", 
    "notation": "REL040090", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Colors": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Colors", 
    "notation": "JNF013020", 
    "alt_label": []
  }, 
  "Art / History / Baroque & Rococo": {
    "related": [], 
    "pref_label": "Art / History / Baroque & Rococo", 
    "notation": "ART015090", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / United States / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / United States / General", 
    "notation": "JNF038100", 
    "alt_label": []
  }, 
  "Political Science / General": {
    "related": [], 
    "pref_label": "Political Science / General", 
    "notation": "POL000000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Model Railroading": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Model Railroading", 
    "notation": "CRA045000", 
    "alt_label": []
  }, 
  "Gardening / Regional / South (al, Ar, Fl, Ga, Ky, La, Ms, Nc, Sc, Tn, Va, Wv)": {
    "related": [], 
    "pref_label": "Gardening / Regional / South (al, Ar, Fl, Ga, Ky, La, Ms, Nc, Sc, Tn, Va, Wv)", 
    "notation": "GAR019060", 
    "alt_label": []
  }, 
  "Mathematics / Graphic Methods": {
    "related": [], 
    "pref_label": "Mathematics / Graphic Methods", 
    "notation": "MAT013000", 
    "alt_label": []
  }, 
  "History / Ancient / Rome": {
    "related": [], 
    "pref_label": "History / Ancient / Rome", 
    "notation": "HIS002020", 
    "alt_label": []
  }, 
  "Law / Insurance": {
    "related": [], 
    "pref_label": "Law / Insurance", 
    "notation": "LAW049000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / I Ching": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / I Ching", 
    "notation": "OCC038000", 
    "alt_label": []
  }, 
  "Bibles / New American Bible / Children": {
    "related": [], 
    "pref_label": "Bibles / New American Bible / Children", 
    "notation": "BIB009010", 
    "alt_label": []
  }, 
  "Psychology / Developmental / Adulthood & Aging": {
    "related": [], 
    "pref_label": "Psychology / Developmental / Adulthood & Aging", 
    "notation": "PSY043000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Mysticism": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Mysticism", 
    "notation": "OCC012000", 
    "alt_label": []
  }, 
  "Sports & Recreation / History": {
    "related": [], 
    "pref_label": "Sports & Recreation / History", 
    "notation": "SPO019000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Pentecostal & Charismatic": {
    "related": [], 
    "pref_label": "Religion / Christianity / Pentecostal & Charismatic", 
    "notation": "REL079000", 
    "alt_label": []
  }, 
  "Bibles / Multiple Translations / Devotional": {
    "related": [], 
    "pref_label": "Bibles / Multiple Translations / Devotional", 
    "notation": "BIB008020", 
    "alt_label": []
  }, 
  "Sports & Recreation / Tennis": {
    "related": [], 
    "pref_label": "Sports & Recreation / Tennis", 
    "notation": "SPO045000", 
    "alt_label": []
  }, 
  "Philosophy / Mind & Body": {
    "related": [], 
    "pref_label": "Philosophy / Mind & Body", 
    "notation": "PHI015000", 
    "alt_label": []
  }, 
  "Computers / Operating Systems / Unix": {
    "related": [], 
    "pref_label": "Computers / Operating Systems / Unix", 
    "notation": "COM046030", 
    "alt_label": []
  }, 
  "Literary Criticism / Feminist": {
    "related": [], 
    "pref_label": "Literary Criticism / Feminist", 
    "notation": "LIT003000", 
    "alt_label": []
  }, 
  "Religion / Counseling": {
    "related": [], 
    "pref_label": "Religion / Counseling", 
    "notation": "REL019000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Christology": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Christology", 
    "notation": "REL067040", 
    "alt_label": []
  }, 
  "Travel / Amusement & Theme Parks": {
    "related": [], 
    "pref_label": "Travel / Amusement & Theme Parks", 
    "notation": "TRV029000", 
    "alt_label": []
  }, 
  "Study Aids / Bar Exam": {
    "related": [], 
    "pref_label": "Study Aids / Bar Exam", 
    "notation": "STU034000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / General": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / General", 
    "notation": "COM051010", 
    "alt_label": []
  }, 
  "Medical / Nosology": {
    "related": [], 
    "pref_label": "Medical / Nosology", 
    "notation": "MED091000", 
    "alt_label": []
  }, 
  "Bibles / Reina Valera / Text": {
    "related": [], 
    "pref_label": "Bibles / Reina Valera / Text", 
    "notation": "BIB019060", 
    "alt_label": []
  }, 
  "Law / Jury": {
    "related": [], 
    "pref_label": "Law / Jury", 
    "notation": "LAW053000", 
    "alt_label": []
  }, 
  "Art / African": {
    "related": [], 
    "pref_label": "Art / African", 
    "notation": "ART015010", 
    "alt_label": []
  }, 
  "Bibles / God's Word / Devotional": {
    "related": [], 
    "pref_label": "Bibles / God's Word / Devotional", 
    "notation": "BIB004020", 
    "alt_label": []
  }, 
  "Computers / Security / Cryptography": {
    "related": [], 
    "pref_label": "Computers / Security / Cryptography", 
    "notation": "COM083000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Danish": {
    "related": [], 
    "pref_label": "Foreign Language Study / Danish", 
    "notation": "FOR004000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Art / Fashion": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Art / Fashion", 
    "notation": "JNF006030", 
    "alt_label": []
  }, 
  "Science / Radiation": {
    "related": [], 
    "pref_label": "Science / Radiation", 
    "notation": "SCI058000", 
    "alt_label": []
  }, 
  "Architecture / Individual Architects & Firms / Essays": {
    "related": [], 
    "pref_label": "Architecture / Individual Architects & Firms / Essays", 
    "notation": "ARC006010", 
    "alt_label": []
  }, 
  "Fiction / African American / Erotica": {
    "related": [], 
    "pref_label": "Fiction / African American / Erotica", 
    "notation": "FIC049030", 
    "alt_label": []
  }, 
  "Fiction / Literary": {
    "related": [], 
    "pref_label": "Fiction / Literary", 
    "notation": "FIC019000", 
    "alt_label": []
  }, 
  "Education / Research": {
    "related": [], 
    "pref_label": "Education / Research", 
    "notation": "EDU037000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Middle Eastern": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Middle Eastern", 
    "notation": "CKB093000", 
    "alt_label": []
  }, 
  "Computers / Desktop Applications / Suites": {
    "related": [], 
    "pref_label": "Computers / Desktop Applications / Suites", 
    "notation": "COM084030", 
    "alt_label": []
  }, 
  "Technology & Engineering / Manufacturing": {
    "related": [], 
    "pref_label": "Technology & Engineering / Manufacturing", 
    "notation": "TEC020000", 
    "alt_label": []
  }, 
  "Study Aids / Civil Service": {
    "related": [], 
    "pref_label": "Study Aids / Civil Service", 
    "notation": "STU007000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Holidays & Celebrations": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Holidays & Celebrations", 
    "notation": "JNF049240", 
    "alt_label": []
  }, 
  "Cooking / Beverages / Non-alcoholic": {
    "related": [], 
    "pref_label": "Cooking / Beverages / Non-alcoholic", 
    "notation": "CKB008000", 
    "alt_label": []
  }, 
  "Business & Economics / Development / General": {
    "related": [], 
    "pref_label": "Business & Economics / Development / General", 
    "notation": "BUS092000", 
    "alt_label": []
  }, 
  "Psychology / Assessment, Testing & Measurement": {
    "related": [], 
    "pref_label": "Psychology / Assessment, Testing & Measurement", 
    "notation": "PSY042000", 
    "alt_label": [
      "Psychology / Testing & Measurement"
    ]
  }, 
  "Foreign Language Study / Serbian & Croatian": {
    "related": [], 
    "pref_label": "Foreign Language Study / Serbian & Croatian", 
    "notation": "FOR023000", 
    "alt_label": []
  }, 
  "Political Science / Public Policy / Social Security": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Social Security", 
    "notation": "POL027000", 
    "alt_label": []
  }, 
  "Religion / Mysticism": {
    "related": [], 
    "pref_label": "Religion / Mysticism", 
    "notation": "REL047000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Roller & In-line Skating": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Roller & In-line Skating", 
    "notation": "JNF054200", 
    "alt_label": []
  }, 
  "Bibles / Today's New International Version / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / Today's New International Version / Youth & Teen", 
    "notation": "BIB021070", 
    "alt_label": []
  }, 
  "History / Europe / Austria & Hungary": {
    "related": [], 
    "pref_label": "History / Europe / Austria & Hungary", 
    "notation": "HIS040000", 
    "alt_label": [
      "History / Europe / Hungary"
    ]
  }, 
  "Science / Earth Sciences / Mineralogy": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / Mineralogy", 
    "notation": "SCI048000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Music / Classical": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / Classical", 
    "notation": "JNF036010", 
    "alt_label": []
  }, 
  "Fiction / Media Tie-in": {
    "related": [], 
    "pref_label": "Fiction / Media Tie-in", 
    "notation": "FIC021000", 
    "alt_label": [
      "Fiction / Television Tie-in"
    ]
  }, 
  "Mathematics / Recreations & Games": {
    "related": [], 
    "pref_label": "Mathematics / Recreations & Games", 
    "notation": "MAT025000", 
    "alt_label": [
      "Mathematics / Games"
    ]
  }, 
  "Science / Paleontology": {
    "related": [], 
    "pref_label": "Science / Paleontology", 
    "notation": "SCI054000", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Portraits": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Portraits", 
    "notation": "PHO016000", 
    "alt_label": []
  }, 
  "Bibles / Contemporary English Version / Text": {
    "related": [], 
    "pref_label": "Bibles / Contemporary English Version / Text", 
    "notation": "BIB002060", 
    "alt_label": []
  }, 
  "Bibles / International Children's Bible / Text": {
    "related": [], 
    "pref_label": "Bibles / International Children's Bible / Text", 
    "notation": "BIB005060", 
    "alt_label": []
  }, 
  "Self-help / Mood Disorders": {
    "related": [], 
    "pref_label": "Self-help / Mood Disorders", 
    "notation": "SEL020000", 
    "alt_label": []
  }, 
  "Religion / Blasphemy, Heresy & Apostasy": {
    "related": [], 
    "pref_label": "Religion / Blasphemy, Heresy & Apostasy", 
    "notation": "REL115000", 
    "alt_label": []
  }, 
  "Bibles / Christian Standard Bible / General": {
    "related": [], 
    "pref_label": "Bibles / Christian Standard Bible / General", 
    "notation": "BIB001000", 
    "alt_label": []
  }, 
  "Religion / Ethnic & Tribal": {
    "related": [], 
    "pref_label": "Religion / Ethnic & Tribal", 
    "notation": "REL029000", 
    "alt_label": []
  }, 
  "Medical / Nursing / Management & Leadership": {
    "related": [], 
    "pref_label": "Medical / Nursing / Management & Leadership", 
    "notation": "MED058110", 
    "alt_label": []
  }, 
  "Computers / Certification Guides / General": {
    "related": [], 
    "pref_label": "Computers / Certification Guides / General", 
    "notation": "COM055000", 
    "alt_label": []
  }, 
  "Religion / Biblical Commentary / Old Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Commentary / Old Testament", 
    "notation": "REL006060", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Post-structuralism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Post-structuralism", 
    "notation": "PHI043000", 
    "alt_label": []
  }, 
  "Law / Common": {
    "related": [], 
    "pref_label": "Law / Common", 
    "notation": "LAW103000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Romance": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Romance", 
    "notation": "CGN004090", 
    "alt_label": []
  }, 
  "Fiction / Legal": {
    "related": [], 
    "pref_label": "Fiction / Legal", 
    "notation": "FIC034000", 
    "alt_label": []
  }, 
  "Computers / Online Services / Resource Directories": {
    "related": [], 
    "pref_label": "Computers / Online Services / Resource Directories", 
    "notation": "COM069010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Elephants": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Elephants", 
    "notation": "JNF003070", 
    "alt_label": []
  }, 
  "Business & Economics / Careers / General": {
    "related": [], 
    "pref_label": "Business & Economics / Careers / General", 
    "notation": "BUS012000", 
    "alt_label": []
  }, 
  "Computers / Utilities": {
    "related": [], 
    "pref_label": "Computers / Utilities", 
    "notation": "COM056000", 
    "alt_label": []
  }, 
  "Computers / Client-server Computing": {
    "related": [], 
    "pref_label": "Computers / Client-server Computing", 
    "notation": "COM061000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / American / California Style": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / American / California Style", 
    "notation": "CKB002010", 
    "alt_label": []
  }, 
  "Mathematics / Transformations": {
    "related": [], 
    "pref_label": "Mathematics / Transformations", 
    "notation": "MAT031000", 
    "alt_label": []
  }, 
  "Law / Defamation": {
    "related": [], 
    "pref_label": "Law / Defamation", 
    "notation": "LAW106000", 
    "alt_label": [
      "Law / Libel & Slander"
    ]
  }, 
  "Juvenile Nonfiction / Careers": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Careers", 
    "notation": "JNF011000", 
    "alt_label": [
      "Juvenile Nonfiction / Vocational Guidance"
    ]
  }, 
  "Mathematics / Arithmetic": {
    "related": [], 
    "pref_label": "Mathematics / Arithmetic", 
    "notation": "MAT004000", 
    "alt_label": [
      "Mathematics / Fractions"
    ]
  }, 
  "Antiques & Collectibles / Transportation": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Transportation", 
    "notation": "ANT009000", 
    "alt_label": [
      "Antiques & Collectibles / Automobiles", 
      "Antiques & Collectibles / Cars", 
      "Antiques & Collectibles / Nautical"
    ]
  }, 
  "Technology & Engineering / Optics": {
    "related": [], 
    "pref_label": "Technology & Engineering / Optics", 
    "notation": "TEC030000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Personal Memoirs": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Personal Memoirs", 
    "notation": "BIO026000", 
    "alt_label": []
  }, 
  "Fiction / Romance / Western": {
    "related": [], 
    "pref_label": "Fiction / Romance / Western", 
    "notation": "FIC027100", 
    "alt_label": []
  }, 
  "Fiction / Sports": {
    "related": [], 
    "pref_label": "Fiction / Sports", 
    "notation": "FIC038000", 
    "alt_label": []
  }, 
  "Art / Techniques / Oil Painting": {
    "related": [], 
    "pref_label": "Art / Techniques / Oil Painting", 
    "notation": "ART018000", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Coastal Regions & Shorelines": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Coastal Regions & Shorelines", 
    "notation": "NAT045050", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Pastry": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Pastry", 
    "notation": "CKB062000", 
    "alt_label": []
  }, 
  "Medical / Nephrology": {
    "related": [], 
    "pref_label": "Medical / Nephrology", 
    "notation": "MED055000", 
    "alt_label": []
  }, 
  "Computers / Database Management / Data Warehousing": {
    "related": [], 
    "pref_label": "Computers / Database Management / Data Warehousing", 
    "notation": "COM021040", 
    "alt_label": []
  }, 
  "Religion / Holidays / Easter & Lent": {
    "related": [], 
    "pref_label": "Religion / Holidays / Easter & Lent", 
    "notation": "REL034030", 
    "alt_label": []
  }, 
  "Pets / Reptiles, Amphibians & Terrariums": {
    "related": [], 
    "pref_label": "Pets / Reptiles, Amphibians & Terrariums", 
    "notation": "PET009000", 
    "alt_label": [
      "Pets / Amphibians"
    ]
  }, 
  "Sports & Recreation / Sociology Of Sports": {
    "related": [], 
    "pref_label": "Sports & Recreation / Sociology Of Sports", 
    "notation": "SPO066000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / History Of Science": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / History Of Science", 
    "notation": "JNF051190", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Exploration & Discovery": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Exploration & Discovery", 
    "notation": "JNF025080", 
    "alt_label": []
  }, 
  "Design / Graphic Arts / Typography": {
    "related": [], 
    "pref_label": "Design / Graphic Arts / Typography", 
    "notation": "DES007050", 
    "alt_label": []
  }, 
  "Performing Arts / Radio / General": {
    "related": [], 
    "pref_label": "Performing Arts / Radio / General", 
    "notation": "PER008000", 
    "alt_label": []
  }, 
  "History / Caribbean & West Indies / Cuba": {
    "related": [], 
    "pref_label": "History / Caribbean & West Indies / Cuba", 
    "notation": "HIS041010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / Middle East": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Middle East", 
    "notation": "JUV030110", 
    "alt_label": []
  }, 
  "Travel / Canada / Quebec (qc)": {
    "related": [], 
    "pref_label": "Travel / Canada / Quebec (qc)", 
    "notation": "TRV006060", 
    "alt_label": []
  }, 
  "Psychology / Psychotherapy / Counseling": {
    "related": [], 
    "pref_label": "Psychology / Psychotherapy / Counseling", 
    "notation": "PSY010000", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Family": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Family", 
    "notation": "REL012030", 
    "alt_label": []
  }, 
  "Performing Arts / Dance / Modern": {
    "related": [], 
    "pref_label": "Performing Arts / Dance / Modern", 
    "notation": "PER003040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Language Arts / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Language Arts / General", 
    "notation": "JNF029000", 
    "alt_label": []
  }, 
  "Family & Relationships / Friendship": {
    "related": [], 
    "pref_label": "Family & Relationships / Friendship", 
    "notation": "FAM021000", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Utilitarianism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Utilitarianism", 
    "notation": "PHI030000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Communication Studies": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Communication Studies", 
    "notation": "LAN004000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Electronics / Transistors": {
    "related": [], 
    "pref_label": "Technology & Engineering / Electronics / Transistors", 
    "notation": "TEC008110", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Patchwork": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Patchwork", 
    "notation": "CRA026000", 
    "alt_label": []
  }, 
  "Fiction / Fantasy / Contemporary": {
    "related": [], 
    "pref_label": "Fiction / Fantasy / Contemporary", 
    "notation": "FIC009010", 
    "alt_label": []
  }, 
  "Art / Mixed Media": {
    "related": [], 
    "pref_label": "Art / Mixed Media", 
    "notation": "ART017000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Baseball & Softball": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Baseball & Softball", 
    "notation": "JNF054010", 
    "alt_label": []
  }, 
  "Poetry / American / African American": {
    "related": [], 
    "pref_label": "Poetry / American / African American", 
    "notation": "POE005050", 
    "alt_label": []
  }, 
  "Family & Relationships / Child Development": {
    "related": [], 
    "pref_label": "Family & Relationships / Child Development", 
    "notation": "FAM011000", 
    "alt_label": []
  }, 
  "Medical / Gynecology & Obstetrics": {
    "related": [], 
    "pref_label": "Medical / Gynecology & Obstetrics", 
    "notation": "MED033000", 
    "alt_label": [
      "Medical / Obstetrics"
    ]
  }, 
  "Law / Courts": {
    "related": [], 
    "pref_label": "Law / Courts", 
    "notation": "LAW025000", 
    "alt_label": []
  }, 
  "Health & Fitness / Herbal Medications": {
    "related": [], 
    "pref_label": "Health & Fitness / Herbal Medications", 
    "notation": "HEA011000", 
    "alt_label": []
  }, 
  "Business & Economics / Workplace Culture": {
    "related": [], 
    "pref_label": "Business & Economics / Workplace Culture", 
    "notation": "BUS097000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Mexican": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Mexican", 
    "notation": "CKB056000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Technology / Machinery & Tools": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Technology / Machinery & Tools", 
    "notation": "JNF051130", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Travel": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Travel", 
    "notation": "JNF058000", 
    "alt_label": []
  }, 
  "Social Science / Regional Studies": {
    "related": [], 
    "pref_label": "Social Science / Regional Studies", 
    "notation": "SOC053000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / United States / African American": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / United States / African American", 
    "notation": "JUV011010", 
    "alt_label": []
  }, 
  "Computers / Keyboarding": {
    "related": [], 
    "pref_label": "Computers / Keyboarding", 
    "notation": "COM035000", 
    "alt_label": []
  }, 
  "Health & Fitness / First Aid": {
    "related": [], 
    "pref_label": "Health & Fitness / First Aid", 
    "notation": "HEA033000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Animals": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Animals", 
    "notation": "JUV033050", 
    "alt_label": []
  }, 
  "Medical / Biotechnology": {
    "related": [], 
    "pref_label": "Medical / Biotechnology", 
    "notation": "MED009000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Bible Stories / Old Testament": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Bible Stories / Old Testament", 
    "notation": "JNF049140", 
    "alt_label": []
  }, 
  "History / Military / Other": {
    "related": [], 
    "pref_label": "History / Military / Other", 
    "notation": "HIS027130", 
    "alt_label": []
  }, 
  "Science / Reference": {
    "related": [], 
    "pref_label": "Science / Reference", 
    "notation": "SCI060000", 
    "alt_label": []
  }, 
  "Science / Chemistry / Inorganic": {
    "related": [], 
    "pref_label": "Science / Chemistry / Inorganic", 
    "notation": "SCI013030", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Pop Vocal": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Pop Vocal", 
    "notation": "MUS029000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / Agronomy / Soil Science": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / Agronomy / Soil Science", 
    "notation": "TEC003060", 
    "alt_label": []
  }, 
  "History / Europe / Former Soviet Republics": {
    "related": [], 
    "pref_label": "History / Europe / Former Soviet Republics", 
    "notation": "HIS012000", 
    "alt_label": []
  }, 
  "Bibles / Nueva Version International / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / Nueva Version International / Youth & Teen", 
    "notation": "BIB017070", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Soul & R 'n B": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Soul & R 'n B", 
    "notation": "MUS039000", 
    "alt_label": [
      "Music / Genres & Styles / Rhythm & Blues"
    ]
  }, 
  "Political Science / Public Policy / Cultural Policy": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Cultural Policy", 
    "notation": "POL038000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Electronics / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / Electronics / General", 
    "notation": "TEC008000", 
    "alt_label": []
  }, 
  "Self-help / Codependency": {
    "related": [], 
    "pref_label": "Self-help / Codependency", 
    "notation": "SEL008000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / General": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / General", 
    "notation": "CKB031000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Science & Technology": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Science & Technology", 
    "notation": "JUV036000", 
    "alt_label": [
      "Juvenile Fiction / Technology"
    ]
  }, 
  "Law / Disability": {
    "related": [], 
    "pref_label": "Law / Disability", 
    "notation": "LAW031000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Performing Arts / Music": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Performing Arts / Music", 
    "notation": "JUV031040", 
    "alt_label": [
      "Juvenile Fiction / Music"
    ]
  }, 
  "Juvenile Nonfiction / Art / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Art / General", 
    "notation": "JNF006000", 
    "alt_label": []
  }, 
  "Nature / Sky Observation": {
    "related": [], 
    "pref_label": "Nature / Sky Observation", 
    "notation": "NAT033000", 
    "alt_label": []
  }, 
  "Political Science / Labor & Industrial Relations": {
    "related": [], 
    "pref_label": "Political Science / Labor & Industrial Relations", 
    "notation": "POL013000", 
    "alt_label": []
  }, 
  "Business & Economics / Mail Order": {
    "related": [], 
    "pref_label": "Business & Economics / Mail Order", 
    "notation": "BUS040000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Soteriology": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Soteriology", 
    "notation": "REL067100", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Handwriting": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Handwriting", 
    "notation": "LAN007000", 
    "alt_label": []
  }, 
  "Health & Fitness / Weight Loss": {
    "related": [], 
    "pref_label": "Health & Fitness / Weight Loss", 
    "notation": "HEA019000", 
    "alt_label": [
      "Health & Fitness / Reducing"
    ]
  }, 
  "Business & Economics / Finance": {
    "related": [], 
    "pref_label": "Business & Economics / Finance", 
    "notation": "BUS027000", 
    "alt_label": []
  }, 
  "Bibles / La Biblia De Las Americas / General": {
    "related": [], 
    "pref_label": "Bibles / La Biblia De Las Americas / General", 
    "notation": "BIB007000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Reggae": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Reggae", 
    "notation": "MUS047000", 
    "alt_label": []
  }, 
  "Medical / Diet Therapy": {
    "related": [], 
    "pref_label": "Medical / Diet Therapy", 
    "notation": "MED021000", 
    "alt_label": []
  }, 
  "Bibles / Multiple Translations / Text": {
    "related": [], 
    "pref_label": "Bibles / Multiple Translations / Text", 
    "notation": "BIB008060", 
    "alt_label": []
  }, 
  "Gardening / Herbs": {
    "related": [], 
    "pref_label": "Gardening / Herbs", 
    "notation": "GAR009000", 
    "alt_label": []
  }, 
  "Law / Torts": {
    "related": [], 
    "pref_label": "Law / Torts", 
    "notation": "LAW087000", 
    "alt_label": []
  }, 
  "Mathematics / Combinatorics": {
    "related": [], 
    "pref_label": "Mathematics / Combinatorics", 
    "notation": "MAT036000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Canada / Pre-confederation (to 1867)": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Canada / Pre-confederation (to 1867)", 
    "notation": "JUV016170", 
    "alt_label": []
  }, 
  "History / North America": {
    "related": [], 
    "pref_label": "History / North America", 
    "notation": "HIS029000", 
    "alt_label": []
  }, 
  "Social Science / Jewish Studies": {
    "related": [], 
    "pref_label": "Social Science / Jewish Studies", 
    "notation": "SOC049000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Prolog": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Prolog", 
    "notation": "COM051140", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Ice Skating": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Ice Skating", 
    "notation": "JUV032120", 
    "alt_label": []
  }, 
  "History / Canada / Post-confederation (1867-)": {
    "related": [], 
    "pref_label": "History / Canada / Post-confederation (1867-)", 
    "notation": "HIS006020", 
    "alt_label": []
  }, 
  "History / Military / Pictorial": {
    "related": [], 
    "pref_label": "History / Military / Pictorial", 
    "notation": "HIS027050", 
    "alt_label": []
  }, 
  "History / Europe / Ireland": {
    "related": [], 
    "pref_label": "History / Europe / Ireland", 
    "notation": "HIS018000", 
    "alt_label": []
  }, 
  "Education / Classroom Management": {
    "related": [], 
    "pref_label": "Education / Classroom Management", 
    "notation": "EDU044000", 
    "alt_label": []
  }, 
  "Bibles / New International Version / Children": {
    "related": [], 
    "pref_label": "Bibles / New International Version / Children", 
    "notation": "BIB013010", 
    "alt_label": []
  }, 
  "Study Aids / College Entrance": {
    "related": [], 
    "pref_label": "Study Aids / College Entrance", 
    "notation": "STU009000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Performing Arts / Dance": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Performing Arts / Dance", 
    "notation": "JUV031020", 
    "alt_label": []
  }, 
  "Drama / Canadian": {
    "related": [], 
    "pref_label": "Drama / Canadian", 
    "notation": "DRA013000", 
    "alt_label": []
  }, 
  "Transportation / Aviation / General": {
    "related": [], 
    "pref_label": "Transportation / Aviation / General", 
    "notation": "TRA002000", 
    "alt_label": []
  }, 
  "Bibles / La Biblia De Las Americas / Text": {
    "related": [], 
    "pref_label": "Bibles / La Biblia De Las Americas / Text", 
    "notation": "BIB007060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Anatomy & Physiology": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Anatomy & Physiology", 
    "notation": "JNF051030", 
    "alt_label": []
  }, 
  "Music / General": {
    "related": [], 
    "pref_label": "Music / General", 
    "notation": "MUS000000", 
    "alt_label": []
  }, 
  "Family & Relationships / Education": {
    "related": [], 
    "pref_label": "Family & Relationships / Education", 
    "notation": "FAM016000", 
    "alt_label": []
  }, 
  "Fiction / Christian / Classic & Allegory": {
    "related": [], 
    "pref_label": "Fiction / Christian / Classic & Allegory", 
    "notation": "FIC042010", 
    "alt_label": []
  }, 
  "Law / Family Law / Divorce & Separation": {
    "related": [], 
    "pref_label": "Law / Family Law / Divorce & Separation", 
    "notation": "LAW038020", 
    "alt_label": [
      "Law / Divorce", 
      "Law / Separation"
    ]
  }, 
  "Sports & Recreation / Volleyball": {
    "related": [], 
    "pref_label": "Sports & Recreation / Volleyball", 
    "notation": "SPO049000", 
    "alt_label": []
  }, 
  "Psychology / Practice Management": {
    "related": [], 
    "pref_label": "Psychology / Practice Management", 
    "notation": "PSY046000", 
    "alt_label": []
  }, 
  "Mathematics / Differential Equations / General": {
    "related": [], 
    "pref_label": "Mathematics / Differential Equations / General", 
    "notation": "MAT007000", 
    "alt_label": []
  }, 
  "Performing Arts / Puppets & Puppetry": {
    "related": [], 
    "pref_label": "Performing Arts / Puppets & Puppetry", 
    "notation": "PER007000", 
    "alt_label": []
  }, 
  "Architecture / Historic Preservation / General": {
    "related": [], 
    "pref_label": "Architecture / Historic Preservation / General", 
    "notation": "ARC014000", 
    "alt_label": []
  }, 
  "Fiction / Action & Adventure": {
    "related": [], 
    "pref_label": "Fiction / Action & Adventure", 
    "notation": "FIC002000", 
    "alt_label": [
      "Fiction / Adventure"
    ]
  }, 
  "Travel / Parks & Campgrounds": {
    "related": [], 
    "pref_label": "Travel / Parks & Campgrounds", 
    "notation": "TRV018000", 
    "alt_label": [
      "Travel / Campgrounds", 
      "Travel / National Parks"
    ]
  }, 
  "Drama / Russian & Former Soviet Union": {
    "related": [], 
    "pref_label": "Drama / Russian & Former Soviet Union", 
    "notation": "DRA016000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Pharmaceutical & Biotechnology": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Pharmaceutical & Biotechnology", 
    "notation": "BUS070130", 
    "alt_label": []
  }, 
  "Art / Techniques / Pen & Ink Drawing": {
    "related": [], 
    "pref_label": "Art / Techniques / Pen & Ink Drawing", 
    "notation": "ART033000", 
    "alt_label": []
  }, 
  "Gardening / Garden Furnishings": {
    "related": [], 
    "pref_label": "Gardening / Garden Furnishings", 
    "notation": "GAR007000", 
    "alt_label": []
  }, 
  "Bibles / Reina Valera / Devotional": {
    "related": [], 
    "pref_label": "Bibles / Reina Valera / Devotional", 
    "notation": "BIB019020", 
    "alt_label": []
  }, 
  "Art / History / Romanticism": {
    "related": [], 
    "pref_label": "Art / History / Romanticism", 
    "notation": "ART015120", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Performing Arts": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Performing Arts", 
    "notation": "ANT025000", 
    "alt_label": [
      "Antiques & Collectibles / Dance", 
      "Antiques & Collectibles / Movies", 
      "Antiques & Collectibles / Musical Instruments", 
      "Antiques & Collectibles / Televisions & Television-related", 
      "Antiques & Collectibles / Theater"
    ]
  }, 
  "Juvenile Fiction / Historical / Other": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Other", 
    "notation": "JUV016130", 
    "alt_label": []
  }, 
  "Political Science / International Relations / Arms Control": {
    "related": [], 
    "pref_label": "Political Science / International Relations / Arms Control", 
    "notation": "POL001000", 
    "alt_label": []
  }, 
  "Gardening / Techniques": {
    "related": [], 
    "pref_label": "Gardening / Techniques", 
    "notation": "GAR022000", 
    "alt_label": [
      "Gardening / Hydroponics", 
      "Gardening / Xeriscaping"
    ]
  }, 
  "Business & Economics / Economics / General": {
    "related": [], 
    "pref_label": "Business & Economics / Economics / General", 
    "notation": "BUS069000", 
    "alt_label": []
  }, 
  "Law / Election Law": {
    "related": [], 
    "pref_label": "Law / Election Law", 
    "notation": "LAW108000", 
    "alt_label": []
  }, 
  "Medical / Psychiatry / Child & Adolescent": {
    "related": [], 
    "pref_label": "Medical / Psychiatry / Child & Adolescent", 
    "notation": "MED105010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Giraffes": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Giraffes", 
    "notation": "JUV002320", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Metal Work": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Metal Work", 
    "notation": "CRA017000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Angelology & Demonology": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Angelology & Demonology", 
    "notation": "REL067010", 
    "alt_label": []
  }, 
  "Psychology / Movements / Existential": {
    "related": [], 
    "pref_label": "Psychology / Movements / Existential", 
    "notation": "PSY045040", 
    "alt_label": []
  }, 
  "Foreign Language Study / Russian": {
    "related": [], 
    "pref_label": "Foreign Language Study / Russian", 
    "notation": "FOR021000", 
    "alt_label": []
  }, 
  "Science / Physics / Condensed Matter": {
    "related": [], 
    "pref_label": "Science / Physics / Condensed Matter", 
    "notation": "SCI077000", 
    "alt_label": []
  }, 
  "Architecture / Sustainability & Green Design": {
    "related": [], 
    "pref_label": "Architecture / Sustainability & Green Design", 
    "notation": "ARC018000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Hydraulics": {
    "related": [], 
    "pref_label": "Technology & Engineering / Hydraulics", 
    "notation": "TEC014000", 
    "alt_label": []
  }, 
  "Literary Collections / American / African American": {
    "related": [], 
    "pref_label": "Literary Collections / American / African American", 
    "notation": "LCO002010", 
    "alt_label": []
  }, 
  "Reference / Almanacs": {
    "related": [], 
    "pref_label": "Reference / Almanacs", 
    "notation": "REF001000", 
    "alt_label": []
  }, 
  "Religion / Faith": {
    "related": [], 
    "pref_label": "Religion / Faith", 
    "notation": "REL077000", 
    "alt_label": []
  }, 
  "Computers / Web / Blogs": {
    "related": [], 
    "pref_label": "Computers / Web / Blogs", 
    "notation": "COM060100", 
    "alt_label": []
  }, 
  "Science / Chemistry / Industrial & Technical": {
    "related": [], 
    "pref_label": "Science / Chemistry / Industrial & Technical", 
    "notation": "SCI013060", 
    "alt_label": []
  }, 
  "Business & Economics / Home-based Businesses": {
    "related": [], 
    "pref_label": "Business & Economics / Home-based Businesses", 
    "notation": "BUS080000", 
    "alt_label": []
  }, 
  "Literary Criticism / Jewish": {
    "related": [], 
    "pref_label": "Literary Criticism / Jewish", 
    "notation": "LIT004210", 
    "alt_label": []
  }, 
  "Computers / Internet / General": {
    "related": [], 
    "pref_label": "Computers / Internet / General", 
    "notation": "COM060000", 
    "alt_label": []
  }, 
  "Science / Chemistry / Physical & Theoretical": {
    "related": [], 
    "pref_label": "Science / Chemistry / Physical & Theoretical", 
    "notation": "SCI013050", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Wolves & Coyotes": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Wolves & Coyotes", 
    "notation": "JUV002250", 
    "alt_label": []
  }, 
  "Social Science / Human Geography": {
    "related": [], 
    "pref_label": "Social Science / Human Geography", 
    "notation": "SOC015000", 
    "alt_label": []
  }, 
  "House & Home / Do-it-yourself / Plumbing": {
    "related": [], 
    "pref_label": "House & Home / Do-it-yourself / Plumbing", 
    "notation": "HOM014000", 
    "alt_label": []
  }, 
  "Computers / Cd-dvd Technology": {
    "related": [], 
    "pref_label": "Computers / Cd-dvd Technology", 
    "notation": "COM009000", 
    "alt_label": []
  }, 
  "Transportation / Public Transportation": {
    "related": [], 
    "pref_label": "Transportation / Public Transportation", 
    "notation": "TRA009000", 
    "alt_label": []
  }, 
  "Social Science / Lesbian Studies": {
    "related": [], 
    "pref_label": "Social Science / Lesbian Studies", 
    "notation": "SOC017000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Family / Adoption": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Family / Adoption", 
    "notation": "JUV013010", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Fantasy": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Fantasy", 
    "notation": "CGN004120", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Canada / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Canada / General", 
    "notation": "JNF038040", 
    "alt_label": []
  }, 
  "Technology & Engineering / Remote Sensing & Geographic Information Systems": {
    "related": [], 
    "pref_label": "Technology & Engineering / Remote Sensing & Geographic Information Systems", 
    "notation": "TEC036000", 
    "alt_label": [
      "Technology & Engineering / Geographic Information Systems"
    ]
  }, 
  "Health & Fitness / Exercise": {
    "related": [], 
    "pref_label": "Health & Fitness / Exercise", 
    "notation": "HEA007000", 
    "alt_label": [
      "Health & Fitness / Stretching"
    ]
  }, 
  "Reference / Encyclopedias": {
    "related": [], 
    "pref_label": "Reference / Encyclopedias", 
    "notation": "REF010000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Law & Crime": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Law & Crime", 
    "notation": "JUV021000", 
    "alt_label": [
      "Juvenile Fiction / Crime"
    ]
  }, 
  "Juvenile Fiction / Robots": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Robots", 
    "notation": "JUV056000", 
    "alt_label": []
  }, 
  "Nature / Animals / Primates": {
    "related": [], 
    "pref_label": "Nature / Animals / Primates", 
    "notation": "NAT002000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Mathematics / Geometry": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Mathematics / Geometry", 
    "notation": "JNF035050", 
    "alt_label": []
  }, 
  "Political Science / Civil Rights": {
    "related": [], 
    "pref_label": "Political Science / Civil Rights", 
    "notation": "POL004000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Holidays & Celebrations / Kwanzaa": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Holidays & Celebrations / Kwanzaa", 
    "notation": "JNF026050", 
    "alt_label": []
  }, 
  "Bibles / New American Standard Bible / Devotional": {
    "related": [], 
    "pref_label": "Bibles / New American Standard Bible / Devotional", 
    "notation": "BIB010020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Fairy Tales & Folklore / Anthologies": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Fairy Tales & Folklore / Anthologies", 
    "notation": "JUV012000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Html": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Html", 
    "notation": "COM051270", 
    "alt_label": [
      "Computers / Hypertext Systems"
    ]
  }, 
  "Political Science / Human Rights": {
    "related": [], 
    "pref_label": "Political Science / Human Rights", 
    "notation": "POL035010", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Records": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Records", 
    "notation": "ANT037000", 
    "alt_label": []
  }, 
  "History / Asia / General": {
    "related": [], 
    "pref_label": "History / Asia / General", 
    "notation": "HIS003000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Yiddish": {
    "related": [], 
    "pref_label": "Foreign Language Study / Yiddish", 
    "notation": "FOR028000", 
    "alt_label": []
  }, 
  "History / General": {
    "related": [], 
    "pref_label": "History / General", 
    "notation": "HIS000000", 
    "alt_label": []
  }, 
  "Social Science / Research": {
    "related": [], 
    "pref_label": "Social Science / Research", 
    "notation": "SOC024000", 
    "alt_label": []
  }, 
  "Games / Trivia": {
    "related": [], 
    "pref_label": "Games / Trivia", 
    "notation": "GAM012000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Science / Archaeology": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Science / Archaeology", 
    "notation": "JNF052010", 
    "alt_label": []
  }, 
  "History / Canada / Pre-confederation (to 1867)": {
    "related": [], 
    "pref_label": "History / Canada / Pre-confederation (to 1867)", 
    "notation": "HIS006010", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Library & Information Science / Cataloging & Classification": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Library & Information Science / Cataloging & Classification", 
    "notation": "LAN025030", 
    "alt_label": []
  }, 
  "Technology & Engineering / Lasers & Photonics": {
    "related": [], 
    "pref_label": "Technology & Engineering / Lasers & Photonics", 
    "notation": "TEC019000", 
    "alt_label": []
  }, 
  "House & Home / Remodeling & Renovation": {
    "related": [], 
    "pref_label": "House & Home / Remodeling & Renovation", 
    "notation": "HOM017000", 
    "alt_label": []
  }, 
  "Bibles / New Revised Standard Version / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / New Revised Standard Version / New Testament & Portions", 
    "notation": "BIB016030", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Emotions & Feelings": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Emotions & Feelings", 
    "notation": "JUV039050", 
    "alt_label": []
  }, 
  "Science / Physics / Astrophysics": {
    "related": [], 
    "pref_label": "Science / Physics / Astrophysics", 
    "notation": "SCI005000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Silver, Gold & Other Metals": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Silver, Gold & Other Metals", 
    "notation": "ANT041000", 
    "alt_label": [
      "Antiques & Collectibles / Gold", 
      "Antiques & Collectibles / Pewter"
    ]
  }, 
  "True Crime / Organized Crime": {
    "related": [], 
    "pref_label": "True Crime / Organized Crime", 
    "notation": "TRU003000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Clothing & Dress": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Clothing & Dress", 
    "notation": "JNF059000", 
    "alt_label": []
  }, 
  "Education / Study Skills": {
    "related": [], 
    "pref_label": "Education / Study Skills", 
    "notation": "EDU028000", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Spiritual Warfare": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Spiritual Warfare", 
    "notation": "REL099000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Biochemistry": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Biochemistry", 
    "notation": "SCI007000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Soccer": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Soccer", 
    "notation": "JUV032150", 
    "alt_label": []
  }, 
  "Gardening / Essays": {
    "related": [], 
    "pref_label": "Gardening / Essays", 
    "notation": "GAR002000", 
    "alt_label": []
  }, 
  "Education / Administration / School Superintendents & Principals": {
    "related": [], 
    "pref_label": "Education / Administration / School Superintendents & Principals", 
    "notation": "EDU001040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Apes, Monkeys, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Apes, Monkeys, Etc.", 
    "notation": "JUV002020", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / Exegesis & Hermeneutics": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / Exegesis & Hermeneutics", 
    "notation": "REL006400", 
    "alt_label": []
  }, 
  "Poetry / African": {
    "related": [], 
    "pref_label": "Poetry / African", 
    "notation": "POE007000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Sexuality & Pregnancy": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Sexuality & Pregnancy", 
    "notation": "JNF024090", 
    "alt_label": []
  }, 
  "Music / History & Criticism": {
    "related": [], 
    "pref_label": "Music / History & Criticism", 
    "notation": "MUS020000", 
    "alt_label": []
  }, 
  "History / Ancient / Greece": {
    "related": [], 
    "pref_label": "History / Ancient / Greece", 
    "notation": "HIS002010", 
    "alt_label": []
  }, 
  "Science / Radiology": {
    "related": [], 
    "pref_label": "Science / Radiology", 
    "notation": "SCI059000", 
    "alt_label": []
  }, 
  "Fiction / Fantasy / General": {
    "related": [], 
    "pref_label": "Fiction / Fantasy / General", 
    "notation": "FIC009000", 
    "alt_label": []
  }, 
  "Law / Litigation": {
    "related": [], 
    "pref_label": "Law / Litigation", 
    "notation": "LAW064000", 
    "alt_label": []
  }, 
  "Art / Conservation & Preservation": {
    "related": [], 
    "pref_label": "Art / Conservation & Preservation", 
    "notation": "ART056000", 
    "alt_label": []
  }, 
  "Family & Relationships / Love & Romance": {
    "related": [], 
    "pref_label": "Family & Relationships / Love & Romance", 
    "notation": "FAM029000", 
    "alt_label": [
      "Family & Relationships / Romance"
    ]
  }, 
  "Art / Film & Video": {
    "related": [], 
    "pref_label": "Art / Film & Video", 
    "notation": "ART057000", 
    "alt_label": [
      "Art / Video"
    ]
  }, 
  "Nature / Animals / Dinosaurs & Prehistoric Creatures": {
    "related": [], 
    "pref_label": "Nature / Animals / Dinosaurs & Prehistoric Creatures", 
    "notation": "NAT007000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Field Sports": {
    "related": [], 
    "pref_label": "Sports & Recreation / Field Sports", 
    "notation": "SPO013000", 
    "alt_label": []
  }, 
  "Religion / Holidays / Jewish": {
    "related": [], 
    "pref_label": "Religion / Holidays / Jewish", 
    "notation": "REL034040", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Erotica": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Erotica", 
    "notation": "PHO023030", 
    "alt_label": []
  }, 
  "Bibles / New King James Version / General": {
    "related": [], 
    "pref_label": "Bibles / New King James Version / General", 
    "notation": "BIB014000", 
    "alt_label": []
  }, 
  "Reference / General": {
    "related": [], 
    "pref_label": "Reference / General", 
    "notation": "REF000000", 
    "alt_label": []
  }, 
  "Psychology / Movements / Humanism": {
    "related": [], 
    "pref_label": "Psychology / Movements / Humanism", 
    "notation": "PSY045020", 
    "alt_label": []
  }, 
  "Technology & Engineering / Environmental / Pollution Control": {
    "related": [], 
    "pref_label": "Technology & Engineering / Environmental / Pollution Control", 
    "notation": "TEC010010", 
    "alt_label": []
  }, 
  "Philosophy / Reference": {
    "related": [], 
    "pref_label": "Philosophy / Reference", 
    "notation": "PHI021000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Sports & Recreation": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Sports & Recreation", 
    "notation": "JUV033230", 
    "alt_label": []
  }, 
  "Health & Fitness / Pregnancy & Childbirth": {
    "related": [], 
    "pref_label": "Health & Fitness / Pregnancy & Childbirth", 
    "notation": "HEA041000", 
    "alt_label": [
      "Health & Fitness / Childbirth"
    ]
  }, 
  "Fiction / Christian / Romance": {
    "related": [], 
    "pref_label": "Fiction / Christian / Romance", 
    "notation": "FIC042040", 
    "alt_label": []
  }, 
  "Medical / Hematology": {
    "related": [], 
    "pref_label": "Medical / Hematology", 
    "notation": "MED038000", 
    "alt_label": []
  }, 
  "Literary Criticism / Mystery & Detective": {
    "related": [], 
    "pref_label": "Literary Criticism / Mystery & Detective", 
    "notation": "LIT004230", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Zoology / Entomology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Zoology / Entomology", 
    "notation": "SCI025000", 
    "alt_label": []
  }, 
  "True Crime / Hoaxes & Deceptions": {
    "related": [], 
    "pref_label": "True Crime / Hoaxes & Deceptions", 
    "notation": "TRU004000", 
    "alt_label": []
  }, 
  "Family & Relationships / Parenting / Stepparenting": {
    "related": [], 
    "pref_label": "Family & Relationships / Parenting / Stepparenting", 
    "notation": "FAM042000", 
    "alt_label": []
  }, 
  "Medical / Public Health": {
    "related": [], 
    "pref_label": "Medical / Public Health", 
    "notation": "MED078000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Skateboarding": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Skateboarding", 
    "notation": "JNF054210", 
    "alt_label": []
  }, 
  "Technology & Engineering / Social Aspects": {
    "related": [], 
    "pref_label": "Technology & Engineering / Social Aspects", 
    "notation": "TEC052000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Music / Instruments": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / Instruments", 
    "notation": "JNF036090", 
    "alt_label": []
  }, 
  "Photography / Commercial": {
    "related": [], 
    "pref_label": "Photography / Commercial", 
    "notation": "PHO021000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Counting & Numbers": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Counting & Numbers", 
    "notation": "JUV009030", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Rivers": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Rivers", 
    "notation": "NAT029000", 
    "alt_label": []
  }, 
  "Psychology / Reference": {
    "related": [], 
    "pref_label": "Psychology / Reference", 
    "notation": "PSY029000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Finnish": {
    "related": [], 
    "pref_label": "Foreign Language Study / Finnish", 
    "notation": "FOR037000", 
    "alt_label": []
  }, 
  "Education / Violence & Harassment": {
    "related": [], 
    "pref_label": "Education / Violence & Harassment", 
    "notation": "EDU055000", 
    "alt_label": []
  }, 
  "Law / Entertainment": {
    "related": [], 
    "pref_label": "Law / Entertainment", 
    "notation": "LAW033000", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Seafood": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Seafood", 
    "notation": "CKB076000", 
    "alt_label": []
  }, 
  "Performing Arts / Television / Screenwriting": {
    "related": [], 
    "pref_label": "Performing Arts / Television / Screenwriting", 
    "notation": "PER010050", 
    "alt_label": []
  }, 
  "Education / Administration / Facility Management": {
    "related": [], 
    "pref_label": "Education / Administration / Facility Management", 
    "notation": "EDU001010", 
    "alt_label": []
  }, 
  "Poetry / Asian / Japanese": {
    "related": [], 
    "pref_label": "Poetry / Asian / Japanese", 
    "notation": "POE009020", 
    "alt_label": []
  }, 
  "Pets / Essays": {
    "related": [], 
    "pref_label": "Pets / Essays", 
    "notation": "PET010000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Runaways": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Runaways", 
    "notation": "JUV039130", 
    "alt_label": []
  }, 
  "Health & Fitness / Nutrition": {
    "related": [], 
    "pref_label": "Health & Fitness / Nutrition", 
    "notation": "HEA017000", 
    "alt_label": []
  }, 
  "Drama / European / Spanish & Portuguese": {
    "related": [], 
    "pref_label": "Drama / European / Spanish & Portuguese", 
    "notation": "DRA004040", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Puppets & Puppetry": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Puppets & Puppetry", 
    "notation": "CRA030000", 
    "alt_label": []
  }, 
  "Medical / Pediatric Emergencies": {
    "related": [], 
    "pref_label": "Medical / Pediatric Emergencies", 
    "notation": "MED094000", 
    "alt_label": []
  }, 
  "House & Home / Furniture": {
    "related": [], 
    "pref_label": "House & Home / Furniture", 
    "notation": "HOM008000", 
    "alt_label": []
  }, 
  "Science / Physics / Quantum Theory": {
    "related": [], 
    "pref_label": "Science / Physics / Quantum Theory", 
    "notation": "SCI057000", 
    "alt_label": []
  }, 
  "Mathematics / Logic": {
    "related": [], 
    "pref_label": "Mathematics / Logic", 
    "notation": "MAT018000", 
    "alt_label": []
  }, 
  "Photography / Techniques / Lighting": {
    "related": [], 
    "pref_label": "Photography / Techniques / Lighting", 
    "notation": "PHO012000", 
    "alt_label": []
  }, 
  "Nature / Rocks & Minerals": {
    "related": [], 
    "pref_label": "Nature / Rocks & Minerals", 
    "notation": "NAT030000", 
    "alt_label": [
      "Nature / Minerals"
    ]
  }, 
  "Juvenile Nonfiction / Games & Activities / Video & Electronic Games": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Games & Activities / Video & Electronic Games", 
    "notation": "JNF021060", 
    "alt_label": []
  }, 
  "Religion / Comparative Religion": {
    "related": [], 
    "pref_label": "Religion / Comparative Religion", 
    "notation": "REL017000", 
    "alt_label": []
  }, 
  "History / Civilization": {
    "related": [], 
    "pref_label": "History / Civilization", 
    "notation": "HIS039000", 
    "alt_label": []
  }, 
  "Science / Physics / Electricity": {
    "related": [], 
    "pref_label": "Science / Physics / Electricity", 
    "notation": "SCI021000", 
    "alt_label": []
  }, 
  "Social Science / Ethnic Studies / Asian American Studies": {
    "related": [], 
    "pref_label": "Social Science / Ethnic Studies / Asian American Studies", 
    "notation": "SOC043000", 
    "alt_label": []
  }, 
  "Reference / Questions & Answers": {
    "related": [], 
    "pref_label": "Reference / Questions & Answers", 
    "notation": "REF018000", 
    "alt_label": []
  }, 
  "Business & Economics / Total Quality Management": {
    "related": [], 
    "pref_label": "Business & Economics / Total Quality Management", 
    "notation": "BUS065000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Reference / Almanacs": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Reference / Almanacs", 
    "notation": "JNF048010", 
    "alt_label": []
  }, 
  "Family & Relationships / Interpersonal Relations": {
    "related": [], 
    "pref_label": "Family & Relationships / Interpersonal Relations", 
    "notation": "FAM027000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Hungarian": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Hungarian", 
    "notation": "CKB043000", 
    "alt_label": []
  }, 
  "Business & Economics / Insurance / Health": {
    "related": [], 
    "pref_label": "Business & Economics / Insurance / Health", 
    "notation": "BUS033040", 
    "alt_label": []
  }, 
  "Medical / Pharmacy": {
    "related": [], 
    "pref_label": "Medical / Pharmacy", 
    "notation": "MED072000", 
    "alt_label": []
  }, 
  "Mathematics / Vector Analysis": {
    "related": [], 
    "pref_label": "Mathematics / Vector Analysis", 
    "notation": "MAT033000", 
    "alt_label": []
  }, 
  "Performing Arts / Comedy": {
    "related": [], 
    "pref_label": "Performing Arts / Comedy", 
    "notation": "PER015000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / United States / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / United States / General", 
    "notation": "JUV016110", 
    "alt_label": []
  }, 
  "Religion / Prayerbooks / Islamic": {
    "related": [], 
    "pref_label": "Religion / Prayerbooks / Islamic", 
    "notation": "REL052030", 
    "alt_label": []
  }, 
  "House & Home / Hand Tools": {
    "related": [], 
    "pref_label": "House & Home / Hand Tools", 
    "notation": "HOM009000", 
    "alt_label": []
  }, 
  "Nature / Weather": {
    "related": [], 
    "pref_label": "Nature / Weather", 
    "notation": "NAT036000", 
    "alt_label": []
  }, 
  "Art / Techniques / Acrylic Painting": {
    "related": [], 
    "pref_label": "Art / Techniques / Acrylic Painting", 
    "notation": "ART031000", 
    "alt_label": []
  }, 
  "Travel / South America / Brazil": {
    "related": [], 
    "pref_label": "Travel / South America / Brazil", 
    "notation": "TRV024020", 
    "alt_label": []
  }, 
  "Fiction / Erotica": {
    "related": [], 
    "pref_label": "Fiction / Erotica", 
    "notation": "FIC005000", 
    "alt_label": []
  }, 
  "Art / Subjects & Themes / Erotica": {
    "related": [], 
    "pref_label": "Art / Subjects & Themes / Erotica", 
    "notation": "ART050050", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Deconstruction": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Deconstruction", 
    "notation": "PHI027000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Death & Dying": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Death & Dying", 
    "notation": "JNF053030", 
    "alt_label": []
  }, 
  "Bibles / King James Version / Study": {
    "related": [], 
    "pref_label": "Bibles / King James Version / Study", 
    "notation": "BIB006050", 
    "alt_label": []
  }, 
  "Political Science / American Government / Legislative Branch": {
    "related": [], 
    "pref_label": "Political Science / American Government / Legislative Branch", 
    "notation": "POL006000", 
    "alt_label": [
      "Political Science / Congress"
    ]
  }, 
  "Juvenile Fiction / Religious / Christian / Family": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Family", 
    "notation": "JUV033100", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Sounds": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Sounds", 
    "notation": "JNF013100", 
    "alt_label": []
  }, 
  "Law / Elder Law": {
    "related": [], 
    "pref_label": "Law / Elder Law", 
    "notation": "LAW107000", 
    "alt_label": []
  }, 
  "Religion / Cults": {
    "related": [], 
    "pref_label": "Religion / Cults", 
    "notation": "REL020000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Senses & Sensation": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Senses & Sensation", 
    "notation": "JUV009050", 
    "alt_label": []
  }, 
  "Education / Educational Policy & Reform / Federal Legislation": {
    "related": [], 
    "pref_label": "Education / Educational Policy & Reform / Federal Legislation", 
    "notation": "EDU034030", 
    "alt_label": []
  }, 
  "Transportation / Automotive / Customizing": {
    "related": [], 
    "pref_label": "Transportation / Automotive / Customizing", 
    "notation": "TRA001030", 
    "alt_label": [
      "Transportation / Automotive / High Performance & Engine Rebuilding"
    ]
  }, 
  "Juvenile Nonfiction / History / United States / 20th Century": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / United States / 20th Century", 
    "notation": "JNF025210", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Aids & Hiv": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Aids & Hiv", 
    "notation": "HEA039020", 
    "alt_label": []
  }, 
  "Law / Bankruptcy & Insolvency": {
    "related": [], 
    "pref_label": "Law / Bankruptcy & Insolvency", 
    "notation": "LAW008000", 
    "alt_label": []
  }, 
  "Literary Criticism / African": {
    "related": [], 
    "pref_label": "Literary Criticism / African", 
    "notation": "LIT004010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Classics": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Classics", 
    "notation": "JUV007000", 
    "alt_label": []
  }, 
  "Nature / Animals / Reptiles & Amphibians": {
    "related": [], 
    "pref_label": "Nature / Animals / Reptiles & Amphibians", 
    "notation": "NAT028000", 
    "alt_label": []
  }, 
  "Travel / Europe / Denmark": {
    "related": [], 
    "pref_label": "Travel / Europe / Denmark", 
    "notation": "TRV009030", 
    "alt_label": []
  }, 
  "Philosophy / Social": {
    "related": [], 
    "pref_label": "Philosophy / Social", 
    "notation": "PHI034000", 
    "alt_label": []
  }, 
  "Medical / Ophthalmology": {
    "related": [], 
    "pref_label": "Medical / Ophthalmology", 
    "notation": "MED063000", 
    "alt_label": []
  }, 
  "Reference / Quotations": {
    "related": [], 
    "pref_label": "Reference / Quotations", 
    "notation": "REF019000", 
    "alt_label": []
  }, 
  "Business & Economics / Economic History": {
    "related": [], 
    "pref_label": "Business & Economics / Economic History", 
    "notation": "BUS023000", 
    "alt_label": []
  }, 
  "Bibles / New American Bible / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / New American Bible / Youth & Teen", 
    "notation": "BIB009070", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Realism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Realism", 
    "notation": "PHI044000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Xml": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Xml", 
    "notation": "COM051320", 
    "alt_label": []
  }, 
  "Philosophy / History & Surveys / Modern": {
    "related": [], 
    "pref_label": "Philosophy / History & Surveys / Modern", 
    "notation": "PHI016000", 
    "alt_label": []
  }, 
  "Computers / Web / Browsers": {
    "related": [], 
    "pref_label": "Computers / Web / Browsers", 
    "notation": "COM060010", 
    "alt_label": []
  }, 
  "Mathematics / Number Systems": {
    "related": [], 
    "pref_label": "Mathematics / Number Systems", 
    "notation": "MAT021000", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / Cancer": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / Cancer", 
    "notation": "CKB103000", 
    "alt_label": []
  }, 
  "Bibles / Reina Valera / Study": {
    "related": [], 
    "pref_label": "Bibles / Reina Valera / Study", 
    "notation": "BIB019050", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Ancient Mysteries & Controversial Knowledge": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Ancient Mysteries & Controversial Knowledge", 
    "notation": "OCC031000", 
    "alt_label": []
  }, 
  "Fiction / Science Fiction / Steampunk": {
    "related": [], 
    "pref_label": "Fiction / Science Fiction / Steampunk", 
    "notation": "FIC028060", 
    "alt_label": []
  }, 
  "Technology & Engineering / Fisheries & Aquaculture": {
    "related": [], 
    "pref_label": "Technology & Engineering / Fisheries & Aquaculture", 
    "notation": "TEC049000", 
    "alt_label": [
      "Technology & Engineering / Aquaculture"
    ]
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Other, Non-religious": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Other, Non-religious", 
    "notation": "JUV017080", 
    "alt_label": []
  }, 
  "Law / Legal History": {
    "related": [], 
    "pref_label": "Law / Legal History", 
    "notation": "LAW060000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Golf": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Golf", 
    "notation": "JUV032190", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Non-sports Cards": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Non-sports Cards", 
    "notation": "ANT028000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Holidays & Celebrations": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Holidays & Celebrations", 
    "notation": "JUV033150", 
    "alt_label": []
  }, 
  "Religion / Demonology & Satanism": {
    "related": [], 
    "pref_label": "Religion / Demonology & Satanism", 
    "notation": "REL100000", 
    "alt_label": [
      "Religion / Satanism"
    ]
  }, 
  "Business & Economics / Advertising & Promotion": {
    "related": [], 
    "pref_label": "Business & Economics / Advertising & Promotion", 
    "notation": "BUS002000", 
    "alt_label": [
      "Business & Economics / Promotion"
    ]
  }, 
  "Technology & Engineering / Fracture Mechanics": {
    "related": [], 
    "pref_label": "Technology & Engineering / Fracture Mechanics", 
    "notation": "TEC013000", 
    "alt_label": []
  }, 
  "Computers / Enterprise Applications / Collaboration Software": {
    "related": [], 
    "pref_label": "Computers / Enterprise Applications / Collaboration Software", 
    "notation": "COM066000", 
    "alt_label": []
  }, 
  "Gardening / Regional / Pacific Northwest (or, Wa)": {
    "related": [], 
    "pref_label": "Gardening / Regional / Pacific Northwest (or, Wa)", 
    "notation": "GAR019050", 
    "alt_label": []
  }, 
  "Bibles / New International Reader's Version / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / New International Reader's Version / Youth & Teen", 
    "notation": "BIB012070", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Sports Cards / Baseball": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Sports Cards / Baseball", 
    "notation": "ANT042010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Transportation / Railroads & Trains": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Transportation / Railroads & Trains", 
    "notation": "JNF057050", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Needlework / Cross-stitch": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Needlework / Cross-stitch", 
    "notation": "CRA044000", 
    "alt_label": []
  }, 
  "Travel / Asia / General": {
    "related": [], 
    "pref_label": "Travel / Asia / General", 
    "notation": "TRV003000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Industrial Health & Safety": {
    "related": [], 
    "pref_label": "Technology & Engineering / Industrial Health & Safety", 
    "notation": "TEC017000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Clocks & Watches": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Clocks & Watches", 
    "notation": "ANT010000", 
    "alt_label": [
      "Antiques & Collectibles / Watches"
    ]
  }, 
  "History / Historiography": {
    "related": [], 
    "pref_label": "History / Historiography", 
    "notation": "HIS016000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Antiques & Collectibles": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Antiques & Collectibles", 
    "notation": "JNF004000", 
    "alt_label": [
      "Juvenile Nonfiction / Collectibles"
    ]
  }, 
  "Computers / Programming Languages / Uml": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Uml", 
    "notation": "COM051450", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Pottery & Ceramics": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Pottery & Ceramics", 
    "notation": "CRA028000", 
    "alt_label": [
      "Crafts & Hobbies / Ceramics"
    ]
  }, 
  "Poetry / Gay & Lesbian": {
    "related": [], 
    "pref_label": "Poetry / Gay & Lesbian", 
    "notation": "POE021000", 
    "alt_label": []
  }, 
  "Bibles / Today's New International Version / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / Today's New International Version / New Testament & Portions", 
    "notation": "BIB021030", 
    "alt_label": []
  }, 
  "Art / Subjects & Themes / Portraits": {
    "related": [], 
    "pref_label": "Art / Subjects & Themes / Portraits", 
    "notation": "ART050040", 
    "alt_label": []
  }, 
  "Science / Time": {
    "related": [], 
    "pref_label": "Science / Time", 
    "notation": "SCI066000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Spirituality / Divine Mother, The Goddess, Quan Yin": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Spirituality / Divine Mother, The Goddess, Quan Yin", 
    "notation": "OCC036050", 
    "alt_label": []
  }, 
  "History / Military / Naval": {
    "related": [], 
    "pref_label": "History / Military / Naval", 
    "notation": "HIS027150", 
    "alt_label": []
  }, 
  "Computers / Web / Social Networking": {
    "related": [], 
    "pref_label": "Computers / Web / Social Networking", 
    "notation": "COM060140", 
    "alt_label": []
  }, 
  "Medical / Endocrinology & Metabolism": {
    "related": [], 
    "pref_label": "Medical / Endocrinology & Metabolism", 
    "notation": "MED027000", 
    "alt_label": [
      "Medical / Diseases / Diabetes", 
      "Medical / Diseases / Endocrine Glands", 
      "Medical / Metabolism"
    ]
  }, 
  "Health & Fitness / Women's Health": {
    "related": [], 
    "pref_label": "Health & Fitness / Women's Health", 
    "notation": "HEA024000", 
    "alt_label": []
  }, 
  "Medical / Dentistry / Endodontics": {
    "related": [], 
    "pref_label": "Medical / Dentistry / Endodontics", 
    "notation": "MED016060", 
    "alt_label": []
  }, 
  "Computers / Virtual Worlds": {
    "related": [], 
    "pref_label": "Computers / Virtual Worlds", 
    "notation": "COM057000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Motor Sports": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Motor Sports", 
    "notation": "JNF054100", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Self-esteem & Self-reliance": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Self-esteem & Self-reliance", 
    "notation": "JNF053160", 
    "alt_label": []
  }, 
  "History / United States / Civil War Period (1850-1877)": {
    "related": [], 
    "pref_label": "History / United States / Civil War Period (1850-1877)", 
    "notation": "HIS036050", 
    "alt_label": [
      "History / Military / United States / Civil War"
    ]
  }, 
  "Travel / South America / General": {
    "related": [], 
    "pref_label": "Travel / South America / General", 
    "notation": "TRV024000", 
    "alt_label": []
  }, 
  "Religion / Buddhism / Sacred Writings": {
    "related": [], 
    "pref_label": "Religion / Buddhism / Sacred Writings", 
    "notation": "REL007030", 
    "alt_label": []
  }, 
  "Drama / Shakespeare": {
    "related": [], 
    "pref_label": "Drama / Shakespeare", 
    "notation": "DRA010000", 
    "alt_label": []
  }, 
  "Philosophy / General": {
    "related": [], 
    "pref_label": "Philosophy / General", 
    "notation": "PHI000000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Pacific Rim": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Pacific Rim", 
    "notation": "CKB097000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Business, Careers, Occupations": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Business, Careers, Occupations", 
    "notation": "JUV006000", 
    "alt_label": [
      "Juvenile Fiction / Occupations", 
      "Juvenile Fiction / Work"
    ]
  }, 
  "Music / Genres & Styles / Big Band & Swing": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Big Band & Swing", 
    "notation": "MUS053000", 
    "alt_label": []
  }, 
  "Fiction / Christian / Historical": {
    "related": [], 
    "pref_label": "Fiction / Christian / Historical", 
    "notation": "FIC042030", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Quilts & Quilting": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Quilts & Quilting", 
    "notation": "CRA031000", 
    "alt_label": []
  }, 
  "Mathematics / Measurement": {
    "related": [], 
    "pref_label": "Mathematics / Measurement", 
    "notation": "MAT020000", 
    "alt_label": []
  }, 
  "Medical / Home Care": {
    "related": [], 
    "pref_label": "Medical / Home Care", 
    "notation": "MED041000", 
    "alt_label": []
  }, 
  "Psychology / Developmental / Lifespan Development": {
    "related": [], 
    "pref_label": "Psychology / Developmental / Lifespan Development", 
    "notation": "PSY044000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Family / New Baby": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Family / New Baby", 
    "notation": "JUV013040", 
    "alt_label": []
  }, 
  "Medical / Nursing / Anesthesia": {
    "related": [], 
    "pref_label": "Medical / Nursing / Anesthesia", 
    "notation": "MED058010", 
    "alt_label": []
  }, 
  "Technology & Engineering / Mobile & Wireless Communications": {
    "related": [], 
    "pref_label": "Technology & Engineering / Mobile & Wireless Communications", 
    "notation": "TEC061000", 
    "alt_label": []
  }, 
  "Science / Study & Teaching": {
    "related": [], 
    "pref_label": "Science / Study & Teaching", 
    "notation": "SCI063000", 
    "alt_label": []
  }, 
  "Fiction / Science Fiction / General": {
    "related": [], 
    "pref_label": "Fiction / Science Fiction / General", 
    "notation": "FIC028000", 
    "alt_label": []
  }, 
  "Fiction / Fantasy / Short Stories": {
    "related": [], 
    "pref_label": "Fiction / Fantasy / Short Stories", 
    "notation": "FIC009040", 
    "alt_label": []
  }, 
  "Science / Earth Sciences / General": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / General", 
    "notation": "SCI019000", 
    "alt_label": []
  }, 
  "Travel / Mexico": {
    "related": [], 
    "pref_label": "Travel / Mexico", 
    "notation": "TRV014000", 
    "alt_label": []
  }, 
  "History / United States / State & Local / South (al, Ar, Fl, Ga, Ky, La, Ms, Nc, Sc, Tn, Va, Wv)": {
    "related": [], 
    "pref_label": "History / United States / State & Local / South (al, Ar, Fl, Ga, Ky, La, Ms, Nc, Sc, Tn, Va, Wv)", 
    "notation": "HIS036120", 
    "alt_label": []
  }, 
  "Education / Curricula": {
    "related": [], 
    "pref_label": "Education / Curricula", 
    "notation": "EDU007000", 
    "alt_label": []
  }, 
  "Education / Driver Education": {
    "related": [], 
    "pref_label": "Education / Driver Education", 
    "notation": "EDU047000", 
    "alt_label": []
  }, 
  "Cooking / Essays": {
    "related": [], 
    "pref_label": "Cooking / Essays", 
    "notation": "CKB030000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Holidays & Celebrations / Birthdays": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Holidays & Celebrations / Birthdays", 
    "notation": "JNF026100", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Nervous System (incl. Brain)": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Nervous System (incl. Brain)", 
    "notation": "HEA039110", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Foreign Language Study / English As A Second Language": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Foreign Language Study / English As A Second Language", 
    "notation": "JNF020010", 
    "alt_label": []
  }, 
  "Education / Administration / General": {
    "related": [], 
    "pref_label": "Education / Administration / General", 
    "notation": "EDU001000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Nocturnal": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Nocturnal", 
    "notation": "JUV002360", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Polymer Clay": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Polymer Clay", 
    "notation": "CRA051000", 
    "alt_label": []
  }, 
  "History / Asia / Korea": {
    "related": [], 
    "pref_label": "History / Asia / Korea", 
    "notation": "HIS023000", 
    "alt_label": []
  }, 
  "Music / Instruction & Study / Songwriting": {
    "related": [], 
    "pref_label": "Music / Instruction & Study / Songwriting", 
    "notation": "MUS038000", 
    "alt_label": []
  }, 
  "Business & Economics / Development / Economic Development": {
    "related": [], 
    "pref_label": "Business & Economics / Development / Economic Development", 
    "notation": "BUS068000", 
    "alt_label": [
      "Business & Economics / Economic Development"
    ]
  }, 
  "Body, Mind & Spirit / Spiritualism": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Spiritualism", 
    "notation": "OCC027000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Other": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Other", 
    "notation": "JUV033030", 
    "alt_label": []
  }, 
  "Business & Economics / Interest": {
    "related": [], 
    "pref_label": "Business & Economics / Interest", 
    "notation": "BUS034000", 
    "alt_label": []
  }, 
  "Science / Experiments & Projects": {
    "related": [], 
    "pref_label": "Science / Experiments & Projects", 
    "notation": "SCI028000", 
    "alt_label": [
      "Science / Projects"
    ]
  }, 
  "Juvenile Nonfiction / Music / Rock": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / Rock", 
    "notation": "JNF036070", 
    "alt_label": []
  }, 
  "Games / Video & Electronic": {
    "related": [], 
    "pref_label": "Games / Video & Electronic", 
    "notation": "GAM013000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Teddy Bears": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Teddy Bears", 
    "notation": "ANT045000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Cell Biology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Cell Biology", 
    "notation": "SCI017000", 
    "alt_label": [
      "Science / Life Sciences / Cytology"
    ]
  }, 
  "Juvenile Fiction / Animals / Ducks, Geese, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Ducks, Geese, Etc.", 
    "notation": "JUV002280", 
    "alt_label": []
  }, 
  "Medical / Evidence-based Medicine": {
    "related": [], 
    "pref_label": "Medical / Evidence-based Medicine", 
    "notation": "MED112000", 
    "alt_label": []
  }, 
  "Business & Economics / Business Ethics": {
    "related": [], 
    "pref_label": "Business & Economics / Business Ethics", 
    "notation": "BUS008000", 
    "alt_label": []
  }, 
  "Travel / United States / South / West South Central (ar, La, Ok, Tx)": {
    "related": [], 
    "pref_label": "Travel / United States / South / West South Central (ar, La, Ok, Tx)", 
    "notation": "TRV025100", 
    "alt_label": []
  }, 
  "Medical / Surgery / Oral & Maxillofacial": {
    "related": [], 
    "pref_label": "Medical / Surgery / Oral & Maxillofacial", 
    "notation": "MED085020", 
    "alt_label": [
      "Medical / Oral & Maxillofacial Surgery"
    ]
  }, 
  "Education / Teaching Methods & Materials / Arts & Humanities": {
    "related": [], 
    "pref_label": "Education / Teaching Methods & Materials / Arts & Humanities", 
    "notation": "EDU029050", 
    "alt_label": []
  }, 
  "Pets / Reference": {
    "related": [], 
    "pref_label": "Pets / Reference", 
    "notation": "PET008000", 
    "alt_label": []
  }, 
  "Social Science / Reference": {
    "related": [], 
    "pref_label": "Social Science / Reference", 
    "notation": "SOC023000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Candle & Soap Making": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Candle & Soap Making", 
    "notation": "CRA049000", 
    "alt_label": []
  }, 
  "Business & Economics / Investments & Securities / Options": {
    "related": [], 
    "pref_label": "Business & Economics / Investments & Securities / Options", 
    "notation": "BUS036040", 
    "alt_label": []
  }, 
  "Computers / Software Development & Engineering / Project Management": {
    "related": [], 
    "pref_label": "Computers / Software Development & Engineering / Project Management", 
    "notation": "COM051430", 
    "alt_label": []
  }, 
  "Bibles / Today's New International Version / Reference": {
    "related": [], 
    "pref_label": "Bibles / Today's New International Version / Reference", 
    "notation": "BIB021040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Early Readers": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Early Readers", 
    "notation": "JNF049200", 
    "alt_label": []
  }, 
  "Education / Learning Styles": {
    "related": [], 
    "pref_label": "Education / Learning Styles", 
    "notation": "EDU051000", 
    "alt_label": []
  }, 
  "Medical / Physician & Patient": {
    "related": [], 
    "pref_label": "Medical / Physician & Patient", 
    "notation": "MED074000", 
    "alt_label": [
      "Medical / Patients"
    ]
  }, 
  "Foreign Language Study / Hindi": {
    "related": [], 
    "pref_label": "Foreign Language Study / Hindi", 
    "notation": "FOR038000", 
    "alt_label": []
  }, 
  "Gardening / Topiary": {
    "related": [], 
    "pref_label": "Gardening / Topiary", 
    "notation": "GAR023000", 
    "alt_label": []
  }, 
  "Science / Chemistry / Clinical": {
    "related": [], 
    "pref_label": "Science / Chemistry / Clinical", 
    "notation": "SCI013020", 
    "alt_label": []
  }, 
  "Bibles / International Children's Bible / Study": {
    "related": [], 
    "pref_label": "Bibles / International Children's Bible / Study", 
    "notation": "BIB005050", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Caribbean & West Indian": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Caribbean & West Indian", 
    "notation": "CKB016000", 
    "alt_label": [
      "Cooking / Regional & Ethnic / West Indian"
    ]
  }, 
  "Science / Earth Sciences / Limnology": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / Limnology", 
    "notation": "SCI083000", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Wilderness": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Wilderness", 
    "notation": "NAT045040", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Jazz": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Jazz", 
    "notation": "MUS025000", 
    "alt_label": []
  }, 
  "Transportation / Motorcycles / Repair & Maintenance": {
    "related": [], 
    "pref_label": "Transportation / Motorcycles / Repair & Maintenance", 
    "notation": "TRA003030", 
    "alt_label": []
  }, 
  "Games / Gambling / General": {
    "related": [], 
    "pref_label": "Games / Gambling / General", 
    "notation": "GAM004000", 
    "alt_label": []
  }, 
  "Religion / Monasticism": {
    "related": [], 
    "pref_label": "Religion / Monasticism", 
    "notation": "REL086000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Baby Animals": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Baby Animals", 
    "notation": "JUV002370", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Camping & Outdoor Activities": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Camping & Outdoor Activities", 
    "notation": "JNF054030", 
    "alt_label": []
  }, 
  "Business & Economics / Careers / Internships": {
    "related": [], 
    "pref_label": "Business & Economics / Careers / Internships", 
    "notation": "BUS012010", 
    "alt_label": []
  }, 
  "Medical / Ultrasonography": {
    "related": [], 
    "pref_label": "Medical / Ultrasonography", 
    "notation": "MED098000", 
    "alt_label": []
  }, 
  "Fiction / War & Military": {
    "related": [], 
    "pref_label": "Fiction / War & Military", 
    "notation": "FIC032000", 
    "alt_label": []
  }, 
  "Travel / Europe / Ireland": {
    "related": [], 
    "pref_label": "Travel / Europe / Ireland", 
    "notation": "TRV009100", 
    "alt_label": []
  }, 
  "Religion / Ecumenism": {
    "related": [], 
    "pref_label": "Religion / Ecumenism", 
    "notation": "REL025000", 
    "alt_label": []
  }, 
  "Gardening / Regional / General": {
    "related": [], 
    "pref_label": "Gardening / Regional / General", 
    "notation": "GAR019000", 
    "alt_label": []
  }, 
  "Bibles / Contemporary English Version / Devotional": {
    "related": [], 
    "pref_label": "Bibles / Contemporary English Version / Devotional", 
    "notation": "BIB002020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Media Tie-in": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Media Tie-in", 
    "notation": "JUV027000", 
    "alt_label": [
      "Juvenile Fiction / Television Tie-in"
    ]
  }, 
  "Medical / Surgery / Colon & Rectal": {
    "related": [], 
    "pref_label": "Medical / Surgery / Colon & Rectal", 
    "notation": "MED085060", 
    "alt_label": []
  }, 
  "Music / Instruction & Study / Theory": {
    "related": [], 
    "pref_label": "Music / Instruction & Study / Theory", 
    "notation": "MUS041000", 
    "alt_label": []
  }, 
  "Literary Criticism / Comics & Graphic Novels": {
    "related": [], 
    "pref_label": "Literary Criticism / Comics & Graphic Novels", 
    "notation": "LIT017000", 
    "alt_label": []
  }, 
  "Bibles / New International Version / Study": {
    "related": [], 
    "pref_label": "Bibles / New International Version / Study", 
    "notation": "BIB013050", 
    "alt_label": []
  }, 
  "Study Aids / Financial Aid": {
    "related": [], 
    "pref_label": "Study Aids / Financial Aid", 
    "notation": "STU031000", 
    "alt_label": [
      "Study Aids / Scholarships & Loans"
    ]
  }, 
  "Juvenile Nonfiction / Humor / Jokes & Riddles": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Humor / Jokes & Riddles", 
    "notation": "JNF028020", 
    "alt_label": []
  }, 
  "Health & Fitness / Health Care Issues": {
    "related": [], 
    "pref_label": "Health & Fitness / Health Care Issues", 
    "notation": "HEA028000", 
    "alt_label": []
  }, 
  "Family & Relationships / Life Stages / Teenagers": {
    "related": [], 
    "pref_label": "Family & Relationships / Life Stages / Teenagers", 
    "notation": "FAM043000", 
    "alt_label": []
  }, 
  "Religion / Ancient": {
    "related": [], 
    "pref_label": "Religion / Ancient", 
    "notation": "REL114000", 
    "alt_label": []
  }, 
  "History / Asia / Southeast Asia": {
    "related": [], 
    "pref_label": "History / Asia / Southeast Asia", 
    "notation": "HIS048000", 
    "alt_label": []
  }, 
  "Bibles / English Standard Version / Study": {
    "related": [], 
    "pref_label": "Bibles / English Standard Version / Study", 
    "notation": "BIB003050", 
    "alt_label": []
  }, 
  "Technology & Engineering / Radar": {
    "related": [], 
    "pref_label": "Technology & Engineering / Radar", 
    "notation": "TEC033000", 
    "alt_label": []
  }, 
  "Medical / Transportation": {
    "related": [], 
    "pref_label": "Medical / Transportation", 
    "notation": "MED087000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Crafts & Hobbies": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Crafts & Hobbies", 
    "notation": "JNF015000", 
    "alt_label": []
  }, 
  "Law / Legal Profession": {
    "related": [], 
    "pref_label": "Law / Legal Profession", 
    "notation": "LAW061000", 
    "alt_label": []
  }, 
  "Art / Popular Culture": {
    "related": [], 
    "pref_label": "Art / Popular Culture", 
    "notation": "ART023000", 
    "alt_label": []
  }, 
  "Law / Civil Law": {
    "related": [], 
    "pref_label": "Law / Civil Law", 
    "notation": "LAW011000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / General", 
    "notation": "JNF000000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Blues": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Blues", 
    "notation": "MUS003000", 
    "alt_label": []
  }, 
  "Science / Earth Sciences / Hydrology": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / Hydrology", 
    "notation": "SCI081000", 
    "alt_label": []
  }, 
  "Political Science / American Government / General": {
    "related": [], 
    "pref_label": "Political Science / American Government / General", 
    "notation": "POL040000", 
    "alt_label": []
  }, 
  "Social Science / Abortion & Birth Control": {
    "related": [], 
    "pref_label": "Social Science / Abortion & Birth Control", 
    "notation": "SOC046000", 
    "alt_label": []
  }, 
  "Computers / Digital Media / Audio": {
    "related": [], 
    "pref_label": "Computers / Digital Media / Audio", 
    "notation": "COM087010", 
    "alt_label": []
  }, 
  "Architecture / Buildings / Religious": {
    "related": [], 
    "pref_label": "Architecture / Buildings / Religious", 
    "notation": "ARC016000", 
    "alt_label": []
  }, 
  "Bibles / Multiple Translations / Study": {
    "related": [], 
    "pref_label": "Bibles / Multiple Translations / Study", 
    "notation": "BIB008050", 
    "alt_label": []
  }, 
  "Cooking / Vegetarian & Vegan": {
    "related": [], 
    "pref_label": "Cooking / Vegetarian & Vegan", 
    "notation": "CKB086000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Readers / Intermediate": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Readers / Intermediate", 
    "notation": "JNF046000", 
    "alt_label": []
  }, 
  "Business & Economics / Economic Conditions": {
    "related": [], 
    "pref_label": "Business & Economics / Economic Conditions", 
    "notation": "BUS022000", 
    "alt_label": []
  }, 
  "Study Aids / Gmat (graduate Management Admission Test)": {
    "related": [], 
    "pref_label": "Study Aids / Gmat (graduate Management Admission Test)", 
    "notation": "STU013000", 
    "alt_label": []
  }, 
  "Religion / Shintoism": {
    "related": [], 
    "pref_label": "Religion / Shintoism", 
    "notation": "REL060000", 
    "alt_label": []
  }, 
  "Family & Relationships / Abuse / Elder Abuse": {
    "related": [], 
    "pref_label": "Family & Relationships / Abuse / Elder Abuse", 
    "notation": "FAM001020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Water Sports": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Water Sports", 
    "notation": "JNF054150", 
    "alt_label": []
  }, 
  "Health & Fitness / Macrobiotics": {
    "related": [], 
    "pref_label": "Health & Fitness / Macrobiotics", 
    "notation": "HEA013000", 
    "alt_label": []
  }, 
  "Fiction / Romance / General": {
    "related": [], 
    "pref_label": "Fiction / Romance / General", 
    "notation": "FIC027000", 
    "alt_label": []
  }, 
  "Family & Relationships / Marriage": {
    "related": [], 
    "pref_label": "Family & Relationships / Marriage", 
    "notation": "FAM030000", 
    "alt_label": []
  }, 
  "Nature / Plants / Trees": {
    "related": [], 
    "pref_label": "Nature / Plants / Trees", 
    "notation": "NAT034000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Sports Psychology": {
    "related": [], 
    "pref_label": "Sports & Recreation / Sports Psychology", 
    "notation": "SPO041000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Passover": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Passover", 
    "notation": "JUV017120", 
    "alt_label": []
  }, 
  "Science / Mechanics / Statics": {
    "related": [], 
    "pref_label": "Science / Mechanics / Statics", 
    "notation": "SCI079000", 
    "alt_label": []
  }, 
  "Law / Banking": {
    "related": [], 
    "pref_label": "Law / Banking", 
    "notation": "LAW007000", 
    "alt_label": []
  }, 
  "Social Science / Sociology / Urban": {
    "related": [], 
    "pref_label": "Social Science / Sociology / Urban", 
    "notation": "SOC026030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / House & Home": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / House & Home", 
    "notation": "JNF027000", 
    "alt_label": []
  }, 
  "Literary Collections / European / German": {
    "related": [], 
    "pref_label": "Literary Collections / European / German", 
    "notation": "LCO008030", 
    "alt_label": []
  }, 
  "Science / Research & Methodology": {
    "related": [], 
    "pref_label": "Science / Research & Methodology", 
    "notation": "SCI043000", 
    "alt_label": [
      "Science / Methodology"
    ]
  }, 
  "Gardening / Flowers / Perennials": {
    "related": [], 
    "pref_label": "Gardening / Flowers / Perennials", 
    "notation": "GAR004050", 
    "alt_label": []
  }, 
  "Gardening / Organic": {
    "related": [], 
    "pref_label": "Gardening / Organic", 
    "notation": "GAR016000", 
    "alt_label": []
  }, 
  "Law / International": {
    "related": [], 
    "pref_label": "Law / International", 
    "notation": "LAW051000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Culinary": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Culinary", 
    "notation": "BIO029000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / United States / 21st Century": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / United States / 21st Century", 
    "notation": "JNF025250", 
    "alt_label": []
  }, 
  "History / Military / World War Ii": {
    "related": [], 
    "pref_label": "History / Military / World War Ii", 
    "notation": "HIS027100", 
    "alt_label": []
  }, 
  "Law / Dictionaries & Terminology": {
    "related": [], 
    "pref_label": "Law / Dictionaries & Terminology", 
    "notation": "LAW030000", 
    "alt_label": []
  }, 
  "House & Home / Woodworking": {
    "related": [], 
    "pref_label": "House & Home / Woodworking", 
    "notation": "HOM018000", 
    "alt_label": []
  }, 
  "Music / Printed Music / Opera & Classical Scores": {
    "related": [], 
    "pref_label": "Music / Printed Music / Opera & Classical Scores", 
    "notation": "MUS037070", 
    "alt_label": []
  }, 
  "Psychology / Creative Ability": {
    "related": [], 
    "pref_label": "Psychology / Creative Ability", 
    "notation": "PSY034000", 
    "alt_label": []
  }, 
  "Political Science / Political Ideologies / Radicalism": {
    "related": [], 
    "pref_label": "Political Science / Political Ideologies / Radicalism", 
    "notation": "POL042040", 
    "alt_label": []
  }, 
  "History / Modern / 17th Century": {
    "related": [], 
    "pref_label": "History / Modern / 17th Century", 
    "notation": "HIS037040", 
    "alt_label": []
  }, 
  "Transportation / Railroads / General": {
    "related": [], 
    "pref_label": "Transportation / Railroads / General", 
    "notation": "TRA004000", 
    "alt_label": []
  }, 
  "Study Aids / Toefl (test Of English As A Foreign Language)": {
    "related": [], 
    "pref_label": "Study Aids / Toefl (test Of English As A Foreign Language)", 
    "notation": "STU028000", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / Prophecy": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / Prophecy", 
    "notation": "REL006140", 
    "alt_label": []
  }, 
  "Bibles / New Living Translation / Study": {
    "related": [], 
    "pref_label": "Bibles / New Living Translation / Study", 
    "notation": "BIB015050", 
    "alt_label": []
  }, 
  "Technology & Engineering / Industrial Design / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / Industrial Design / General", 
    "notation": "TEC016000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Frogs & Toads": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Frogs & Toads", 
    "notation": "JUV002120", 
    "alt_label": []
  }, 
  "Medical / Allied Health Services / Hypnotherapy": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / Hypnotherapy", 
    "notation": "MED003020", 
    "alt_label": []
  }, 
  "Technology & Engineering / Electronics / Solid State": {
    "related": [], 
    "pref_label": "Technology & Engineering / Electronics / Solid State", 
    "notation": "TEC008100", 
    "alt_label": []
  }, 
  "Foreign Language Study / Celtic Languages": {
    "related": [], 
    "pref_label": "Foreign Language Study / Celtic Languages", 
    "notation": "FOR029000", 
    "alt_label": []
  }, 
  "Travel / United States / South / General": {
    "related": [], 
    "pref_label": "Travel / United States / South / General", 
    "notation": "TRV025070", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Fishes": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Fishes", 
    "notation": "JNF003090", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Healing / Prayer & Spiritual": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Healing / Prayer & Spiritual", 
    "notation": "OCC011020", 
    "alt_label": [
      "Body, Mind & Spirit / Spiritual Healing"
    ]
  }, 
  "History / Military / World War I": {
    "related": [], 
    "pref_label": "History / Military / World War I", 
    "notation": "HIS027090", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Superheroes": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Superheroes", 
    "notation": "CGN004080", 
    "alt_label": []
  }, 
  "Education / Teaching Methods & Materials / Language Arts": {
    "related": [], 
    "pref_label": "Education / Teaching Methods & Materials / Language Arts", 
    "notation": "EDU029080", 
    "alt_label": []
  }, 
  "Social Science / Sociology / General": {
    "related": [], 
    "pref_label": "Social Science / Sociology / General", 
    "notation": "SOC026000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Slavic Languages (other)": {
    "related": [], 
    "pref_label": "Foreign Language Study / Slavic Languages (other)", 
    "notation": "FOR024000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Classical": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Classical", 
    "notation": "MUS006000", 
    "alt_label": []
  }, 
  "Bibles / New American Standard Bible / Children": {
    "related": [], 
    "pref_label": "Bibles / New American Standard Bible / Children", 
    "notation": "BIB010010", 
    "alt_label": []
  }, 
  "Poetry / Middle Eastern": {
    "related": [], 
    "pref_label": "Poetry / Middle Eastern", 
    "notation": "POE013000", 
    "alt_label": []
  }, 
  "Cooking / Methods / Cookery For One": {
    "related": [], 
    "pref_label": "Cooking / Methods / Cookery For One", 
    "notation": "CKB020000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Homelessness & Poverty": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Homelessness & Poverty", 
    "notation": "JNF053070", 
    "alt_label": []
  }, 
  "Sports & Recreation / Dog Racing": {
    "related": [], 
    "pref_label": "Sports & Recreation / Dog Racing", 
    "notation": "SPO062000", 
    "alt_label": []
  }, 
  "Cooking / Baby Food": {
    "related": [], 
    "pref_label": "Cooking / Baby Food", 
    "notation": "CKB107000", 
    "alt_label": []
  }, 
  "Religion / Antiquities & Archaeology": {
    "related": [], 
    "pref_label": "Religion / Antiquities & Archaeology", 
    "notation": "REL072000", 
    "alt_label": [
      "Religion / Archaeology"
    ]
  }, 
  "Social Science / Gay Studies": {
    "related": [], 
    "pref_label": "Social Science / Gay Studies", 
    "notation": "SOC012000", 
    "alt_label": [
      "Social Science / Homosexuality"
    ]
  }, 
  "Fiction / Humorous": {
    "related": [], 
    "pref_label": "Fiction / Humorous", 
    "notation": "FIC016000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Multi-language Phrasebooks": {
    "related": [], 
    "pref_label": "Foreign Language Study / Multi-language Phrasebooks", 
    "notation": "FOR018000", 
    "alt_label": []
  }, 
  "Religion / Judaism / Conservative": {
    "related": [], 
    "pref_label": "Religion / Judaism / Conservative", 
    "notation": "REL040050", 
    "alt_label": []
  }, 
  "Religion / Islam / Rituals & Practice": {
    "related": [], 
    "pref_label": "Religion / Islam / Rituals & Practice", 
    "notation": "REL037030", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / General", 
    "notation": "JUV033010", 
    "alt_label": []
  }, 
  "Bibles / King James Version / Reference": {
    "related": [], 
    "pref_label": "Bibles / King James Version / Reference", 
    "notation": "BIB006040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Renaissance": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Renaissance", 
    "notation": "JNF025160", 
    "alt_label": []
  }, 
  "Computers / Optical Data Processing": {
    "related": [], 
    "pref_label": "Computers / Optical Data Processing", 
    "notation": "COM047000", 
    "alt_label": []
  }, 
  "Design / Industrial": {
    "related": [], 
    "pref_label": "Design / Industrial", 
    "notation": "DES009000", 
    "alt_label": []
  }, 
  "Religion / Christian Ministry / Pastoral Resources": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / Pastoral Resources", 
    "notation": "REL074000", 
    "alt_label": [
      "Religion / Pastoral Ministry"
    ]
  }, 
  "Business & Economics / Industrial Management": {
    "related": [], 
    "pref_label": "Business & Economics / Industrial Management", 
    "notation": "BUS082000", 
    "alt_label": []
  }, 
  "Political Science / International Relations / Trade & Tariffs": {
    "related": [], 
    "pref_label": "Political Science / International Relations / Trade & Tariffs", 
    "notation": "POL011020", 
    "alt_label": []
  }, 
  "Literary Criticism / Short Stories": {
    "related": [], 
    "pref_label": "Literary Criticism / Short Stories", 
    "notation": "LIT018000", 
    "alt_label": []
  }, 
  "Education / Bilingual Education": {
    "related": [], 
    "pref_label": "Education / Bilingual Education", 
    "notation": "EDU005000", 
    "alt_label": []
  }, 
  "Poetry / European / French": {
    "related": [], 
    "pref_label": "Poetry / European / French", 
    "notation": "POE017000", 
    "alt_label": []
  }, 
  "Nature / Animal Rights": {
    "related": [], 
    "pref_label": "Nature / Animal Rights", 
    "notation": "NAT039000", 
    "alt_label": []
  }, 
  "Religion / Jainism": {
    "related": [], 
    "pref_label": "Religion / Jainism", 
    "notation": "REL038000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Reptiles & Amphibians": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Reptiles & Amphibians", 
    "notation": "JUV002220", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Farm Animals": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Farm Animals", 
    "notation": "JNF003080", 
    "alt_label": []
  }, 
  "Medical / Nursing / Reference": {
    "related": [], 
    "pref_label": "Medical / Nursing / Reference", 
    "notation": "MED058190", 
    "alt_label": []
  }, 
  "Fiction / Fantasy / Historical": {
    "related": [], 
    "pref_label": "Fiction / Fantasy / Historical", 
    "notation": "FIC009030", 
    "alt_label": []
  }, 
  "Mathematics / Pre-calculus": {
    "related": [], 
    "pref_label": "Mathematics / Pre-calculus", 
    "notation": "MAT023000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Fishes": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Fishes", 
    "notation": "JUV002100", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Basic": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Basic", 
    "notation": "COM051050", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Mexico": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Mexico", 
    "notation": "JNF038070", 
    "alt_label": []
  }, 
  "Social Science / Criminology": {
    "related": [], 
    "pref_label": "Social Science / Criminology", 
    "notation": "SOC004000", 
    "alt_label": []
  }, 
  "History / Modern / 16th Century": {
    "related": [], 
    "pref_label": "History / Modern / 16th Century", 
    "notation": "HIS037090", 
    "alt_label": []
  }, 
  "Travel / Asia / China": {
    "related": [], 
    "pref_label": "Travel / Asia / China", 
    "notation": "TRV003020", 
    "alt_label": []
  }, 
  "Education / Training & Certification": {
    "related": [], 
    "pref_label": "Education / Training & Certification", 
    "notation": "EDU053000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Equipment & Supplies": {
    "related": [], 
    "pref_label": "Sports & Recreation / Equipment & Supplies", 
    "notation": "SPO063000", 
    "alt_label": []
  }, 
  "Business & Economics / International / Accounting": {
    "related": [], 
    "pref_label": "Business & Economics / International / Accounting", 
    "notation": "BUS001030", 
    "alt_label": [
      "Business & Economics / Accounting / International"
    ]
  }, 
  "Computers / Hardware / Handheld Devices": {
    "related": [], 
    "pref_label": "Computers / Hardware / Handheld Devices", 
    "notation": "COM074000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Transportation / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Transportation / General", 
    "notation": "JUV041000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Study Aids / Test Preparation": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Study Aids / Test Preparation", 
    "notation": "JNF055030", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Cobol": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Cobol", 
    "notation": "COM051080", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Discoveries": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Discoveries", 
    "notation": "JNF051170", 
    "alt_label": []
  }, 
  "Psychology / Movements / Transpersonal": {
    "related": [], 
    "pref_label": "Psychology / Movements / Transpersonal", 
    "notation": "PSY045030", 
    "alt_label": []
  }, 
  "Computers / Machine Theory": {
    "related": [], 
    "pref_label": "Computers / Machine Theory", 
    "notation": "COM037000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Quaker": {
    "related": [], 
    "pref_label": "Religion / Christianity / Quaker", 
    "notation": "REL088000", 
    "alt_label": [
      "Religion / Christianity / Friends", 
      "Religion / Christianity / Society Of Friends"
    ]
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Safety": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Safety", 
    "notation": "JNF024080", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Analytic": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Analytic", 
    "notation": "PHI039000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Methodist": {
    "related": [], 
    "pref_label": "Religion / Christianity / Methodist", 
    "notation": "REL044000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Glass & Glassware": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Glass & Glassware", 
    "notation": "CRA012000", 
    "alt_label": [
      "Crafts & Hobbies / Stained Glass"
    ]
  }, 
  "Cooking / Methods / Baking": {
    "related": [], 
    "pref_label": "Cooking / Methods / Baking", 
    "notation": "CKB004000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Sports Cards / Football": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Sports Cards / Football", 
    "notation": "ANT042030", 
    "alt_label": []
  }, 
  "Medical / Rheumatology": {
    "related": [], 
    "pref_label": "Medical / Rheumatology", 
    "notation": "MED083000", 
    "alt_label": []
  }, 
  "Science / Microscopes & Microscopy": {
    "related": [], 
    "pref_label": "Science / Microscopes & Microscopy", 
    "notation": "SCI047000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / Australia & Oceania": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Australia & Oceania", 
    "notation": "JUV030080", 
    "alt_label": []
  }, 
  "Photography / Collections, Catalogs, Exhibitions / General": {
    "related": [], 
    "pref_label": "Photography / Collections, Catalogs, Exhibitions / General", 
    "notation": "PHO004000", 
    "alt_label": []
  }, 
  "History / Africa / South / General": {
    "related": [], 
    "pref_label": "History / Africa / South / General", 
    "notation": "HIS001040", 
    "alt_label": []
  }, 
  "Social Science / Anthropology / Cultural": {
    "related": [], 
    "pref_label": "Social Science / Anthropology / Cultural", 
    "notation": "SOC002010", 
    "alt_label": [
      "Social Science / Ethnology"
    ]
  }, 
  "Mathematics / Trigonometry": {
    "related": [], 
    "pref_label": "Mathematics / Trigonometry", 
    "notation": "MAT032000", 
    "alt_label": []
  }, 
  "Social Science / Sociology / Marriage & Family": {
    "related": [], 
    "pref_label": "Social Science / Sociology / Marriage & Family", 
    "notation": "SOC026010", 
    "alt_label": []
  }, 
  "Business & Economics / Entrepreneurship": {
    "related": [], 
    "pref_label": "Business & Economics / Entrepreneurship", 
    "notation": "BUS025000", 
    "alt_label": []
  }, 
  "Political Science / Essays": {
    "related": [], 
    "pref_label": "Political Science / Essays", 
    "notation": "POL032000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Language Arts / Vocabulary & Spelling": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Language Arts / Vocabulary & Spelling", 
    "notation": "JNF029040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / Other": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Other", 
    "notation": "JUV030070", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / Old Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / Old Testament", 
    "notation": "REL006210", 
    "alt_label": []
  }, 
  "Social Science / Penology": {
    "related": [], 
    "pref_label": "Social Science / Penology", 
    "notation": "SOC030000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Spirituality / Paganism & Neo-paganism": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Spirituality / Paganism & Neo-paganism", 
    "notation": "OCC036020", 
    "alt_label": []
  }, 
  "Business & Economics / Quality Control": {
    "related": [], 
    "pref_label": "Business & Economics / Quality Control", 
    "notation": "BUS053000", 
    "alt_label": []
  }, 
  "Religion / Holidays / Christmas & Advent": {
    "related": [], 
    "pref_label": "Religion / Holidays / Christmas & Advent", 
    "notation": "REL034020", 
    "alt_label": []
  }, 
  "Literary Criticism / European / French": {
    "related": [], 
    "pref_label": "Literary Criticism / European / French", 
    "notation": "LIT004150", 
    "alt_label": []
  }, 
  "Medical / Chemotherapy": {
    "related": [], 
    "pref_label": "Medical / Chemotherapy", 
    "notation": "MED012000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Opposites": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Opposites", 
    "notation": "JNF013050", 
    "alt_label": []
  }, 
  "Health & Fitness / Aromatherapy": {
    "related": [], 
    "pref_label": "Health & Fitness / Aromatherapy", 
    "notation": "HEA029000", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Critical Theory": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Critical Theory", 
    "notation": "PHI040000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Hermetism & Rosicrucianism": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Hermetism & Rosicrucianism", 
    "notation": "OCC040000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Grammar & Punctuation": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Grammar & Punctuation", 
    "notation": "LAN006000", 
    "alt_label": []
  }, 
  "Architecture / History / Medieval": {
    "related": [], 
    "pref_label": "Architecture / History / Medieval", 
    "notation": "ARC005030", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Anxieties & Phobias": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Anxieties & Phobias", 
    "notation": "PSY022060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Dinosaurs & Prehistoric Creatures": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Dinosaurs & Prehistoric Creatures", 
    "notation": "JNF003050", 
    "alt_label": []
  }, 
  "Computers / Natural Language Processing": {
    "related": [], 
    "pref_label": "Computers / Natural Language Processing", 
    "notation": "COM042000", 
    "alt_label": []
  }, 
  "Medical / Ethics": {
    "related": [], 
    "pref_label": "Medical / Ethics", 
    "notation": "MED050000", 
    "alt_label": [
      "Medical / Medical Ethics"
    ]
  }, 
  "Literary Collections / African": {
    "related": [], 
    "pref_label": "Literary Collections / African", 
    "notation": "LCO001000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Zoology / Primatology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Zoology / Primatology", 
    "notation": "SCI070050", 
    "alt_label": []
  }, 
  "Foreign Language Study / Hebrew": {
    "related": [], 
    "pref_label": "Foreign Language Study / Hebrew", 
    "notation": "FOR011000", 
    "alt_label": []
  }, 
  "Medical / Medicaid & Medicare": {
    "related": [], 
    "pref_label": "Medical / Medicaid & Medicare", 
    "notation": "MED049000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Activity Books": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Activity Books", 
    "notation": "JUV054000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Music / Instruction & Study": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / Instruction & Study", 
    "notation": "JNF036030", 
    "alt_label": []
  }, 
  "Mathematics / Counting & Numeration": {
    "related": [], 
    "pref_label": "Mathematics / Counting & Numeration", 
    "notation": "MAT006000", 
    "alt_label": []
  }, 
  "Health & Fitness / Massage & Reflexotherapy": {
    "related": [], 
    "pref_label": "Health & Fitness / Massage & Reflexotherapy", 
    "notation": "HEA014000", 
    "alt_label": [
      "Health & Fitness / Reflexotherapy"
    ]
  }, 
  "Juvenile Fiction / Legends, Myths, Fables / Norse": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Legends, Myths, Fables / Norse", 
    "notation": "JUV022030", 
    "alt_label": []
  }, 
  "Business & Economics / Education": {
    "related": [], 
    "pref_label": "Business & Economics / Education", 
    "notation": "BUS024000", 
    "alt_label": []
  }, 
  "History / Renaissance": {
    "related": [], 
    "pref_label": "History / Renaissance", 
    "notation": "HIS037020", 
    "alt_label": [
      "History / World / Renaissance"
    ]
  }, 
  "Psychology / Movements / Psychoanalysis": {
    "related": [], 
    "pref_label": "Psychology / Movements / Psychoanalysis", 
    "notation": "PSY026000", 
    "alt_label": []
  }, 
  "Travel / Canada / Territories & Nunavut (nt, Nu, Yt)": {
    "related": [], 
    "pref_label": "Travel / Canada / Territories & Nunavut (nt, Nu, Yt)", 
    "notation": "TRV006040", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Human Anatomy & Physiology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Human Anatomy & Physiology", 
    "notation": "SCI036000", 
    "alt_label": []
  }, 
  "Games / Crosswords / Dictionaries": {
    "related": [], 
    "pref_label": "Games / Crosswords / Dictionaries", 
    "notation": "GAM003040", 
    "alt_label": []
  }, 
  "Bibles / Reina Valera / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / Reina Valera / New Testament & Portions", 
    "notation": "BIB019030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Reference / Encyclopedias": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Reference / Encyclopedias", 
    "notation": "JNF048040", 
    "alt_label": []
  }, 
  "Bibles / La Biblia De Las Americas / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / La Biblia De Las Americas / New Testament & Portions", 
    "notation": "BIB007030", 
    "alt_label": []
  }, 
  "Architecture / History / Ancient & Classical": {
    "related": [], 
    "pref_label": "Architecture / History / Ancient & Classical", 
    "notation": "ARC005020", 
    "alt_label": []
  }, 
  "Mathematics / Calculus": {
    "related": [], 
    "pref_label": "Mathematics / Calculus", 
    "notation": "MAT005000", 
    "alt_label": []
  }, 
  "Medical / Nursing Home Care": {
    "related": [], 
    "pref_label": "Medical / Nursing Home Care", 
    "notation": "MED059000", 
    "alt_label": []
  }, 
  "Political Science / Public Policy / Social Policy": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Social Policy", 
    "notation": "POL029000", 
    "alt_label": []
  }, 
  "Mathematics / Research": {
    "related": [], 
    "pref_label": "Mathematics / Research", 
    "notation": "MAT027000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Amish": {
    "related": [], 
    "pref_label": "Religion / Christianity / Amish", 
    "notation": "REL002000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Contemporary Women": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Contemporary Women", 
    "notation": "CGN008000", 
    "alt_label": []
  }, 
  "Medical / Parasitology": {
    "related": [], 
    "pref_label": "Medical / Parasitology", 
    "notation": "MED103000", 
    "alt_label": []
  }, 
  "Social Science / Gender Studies": {
    "related": [], 
    "pref_label": "Social Science / Gender Studies", 
    "notation": "SOC032000", 
    "alt_label": []
  }, 
  "Bibles / King James Version / Text": {
    "related": [], 
    "pref_label": "Bibles / King James Version / Text", 
    "notation": "BIB006060", 
    "alt_label": []
  }, 
  "Self-help / Time Management": {
    "related": [], 
    "pref_label": "Self-help / Time Management", 
    "notation": "SEL035000", 
    "alt_label": []
  }, 
  "Science / Scientific Instruments": {
    "related": [], 
    "pref_label": "Science / Scientific Instruments", 
    "notation": "SCI076000", 
    "alt_label": []
  }, 
  "Photography / History": {
    "related": [], 
    "pref_label": "Photography / History", 
    "notation": "PHO010000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / Irrigation": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / Irrigation", 
    "notation": "TEC003050", 
    "alt_label": []
  }, 
  "Psychology / Clinical Psychology": {
    "related": [], 
    "pref_label": "Psychology / Clinical Psychology", 
    "notation": "PSY007000", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Pragmatism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Pragmatism", 
    "notation": "PHI020000", 
    "alt_label": []
  }, 
  "Religion / Holidays / Other": {
    "related": [], 
    "pref_label": "Religion / Holidays / Other", 
    "notation": "REL034050", 
    "alt_label": []
  }, 
  "Sports & Recreation / Business Aspects": {
    "related": [], 
    "pref_label": "Sports & Recreation / Business Aspects", 
    "notation": "SPO068000", 
    "alt_label": []
  }, 
  "Humor / Form / Limericks & Verse": {
    "related": [], 
    "pref_label": "Humor / Form / Limericks & Verse", 
    "notation": "HUM005000", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Forests & Rainforests": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Forests & Rainforests", 
    "notation": "NAT014000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Values & Virtues": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Values & Virtues", 
    "notation": "JNF053200", 
    "alt_label": []
  }, 
  "Computers / Internet / Application Development": {
    "related": [], 
    "pref_label": "Computers / Internet / Application Development", 
    "notation": "COM060090", 
    "alt_label": []
  }, 
  "Family & Relationships / Parenting / Fatherhood": {
    "related": [], 
    "pref_label": "Family & Relationships / Parenting / Fatherhood", 
    "notation": "FAM020000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Music / Popular": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / Popular", 
    "notation": "JNF036050", 
    "alt_label": []
  }, 
  "Cooking / History": {
    "related": [], 
    "pref_label": "Cooking / History", 
    "notation": "CKB041000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Literature & The Arts": {
    "related": [], 
    "pref_label": "Religion / Christianity / Literature & The Arts", 
    "notation": "REL013000", 
    "alt_label": [
      "Religion / Christian Literature"
    ]
  }, 
  "Games / Card Games / Blackjack": {
    "related": [], 
    "pref_label": "Games / Card Games / Blackjack", 
    "notation": "GAM002030", 
    "alt_label": []
  }, 
  "Art / Annuals": {
    "related": [], 
    "pref_label": "Art / Annuals", 
    "notation": "ART054000", 
    "alt_label": []
  }, 
  "Art / Asian": {
    "related": [], 
    "pref_label": "Art / Asian", 
    "notation": "ART019000", 
    "alt_label": [
      "Art / Oriental"
    ]
  }, 
  "Fiction / Coming Of Age": {
    "related": [], 
    "pref_label": "Fiction / Coming Of Age", 
    "notation": "FIC043000", 
    "alt_label": []
  }, 
  "Bibles / God's Word / General": {
    "related": [], 
    "pref_label": "Bibles / God's Word / General", 
    "notation": "BIB004000", 
    "alt_label": []
  }, 
  "Computers / Database Management / General": {
    "related": [], 
    "pref_label": "Computers / Database Management / General", 
    "notation": "COM021000", 
    "alt_label": []
  }, 
  "History / United States / Colonial Period (1600-1775)": {
    "related": [], 
    "pref_label": "History / United States / Colonial Period (1600-1775)", 
    "notation": "HIS036020", 
    "alt_label": []
  }, 
  "History / Australia & New Zealand": {
    "related": [], 
    "pref_label": "History / Australia & New Zealand", 
    "notation": "HIS004000", 
    "alt_label": []
  }, 
  "History / Asia / India & South Asia": {
    "related": [], 
    "pref_label": "History / Asia / India & South Asia", 
    "notation": "HIS017000", 
    "alt_label": []
  }, 
  "Education / Experimental Methods": {
    "related": [], 
    "pref_label": "Education / Experimental Methods", 
    "notation": "EDU012000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Biographical / Other": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Biographical / Other", 
    "notation": "JUV004030", 
    "alt_label": []
  }, 
  "Gardening / Japanese Gardens": {
    "related": [], 
    "pref_label": "Gardening / Japanese Gardens", 
    "notation": "GAR013000", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / Low Cholesterol": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / Low Cholesterol", 
    "notation": "CKB050000", 
    "alt_label": []
  }, 
  "Computers / Information Theory": {
    "related": [], 
    "pref_label": "Computers / Information Theory", 
    "notation": "COM031000", 
    "alt_label": []
  }, 
  "Literary Criticism / European / General": {
    "related": [], 
    "pref_label": "Literary Criticism / European / General", 
    "notation": "LIT004130", 
    "alt_label": []
  }, 
  "Science / Physics / Crystallography": {
    "related": [], 
    "pref_label": "Science / Physics / Crystallography", 
    "notation": "SCI016000", 
    "alt_label": []
  }, 
  "Literary Collections / Russian & Former Soviet Union": {
    "related": [], 
    "pref_label": "Literary Collections / Russian & Former Soviet Union", 
    "notation": "LCO014000", 
    "alt_label": []
  }, 
  "Bibles / The Message / Children": {
    "related": [], 
    "pref_label": "Bibles / The Message / Children", 
    "notation": "BIB020010", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Lifestyles": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Lifestyles", 
    "notation": "PHO023090", 
    "alt_label": []
  }, 
  "Medical / Research": {
    "related": [], 
    "pref_label": "Medical / Research", 
    "notation": "MED106000", 
    "alt_label": []
  }, 
  "Business & Economics / Urban & Regional": {
    "related": [], 
    "pref_label": "Business & Economics / Urban & Regional", 
    "notation": "BUS067000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Native American": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Native American", 
    "notation": "CKB058000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Coaching / Soccer": {
    "related": [], 
    "pref_label": "Sports & Recreation / Coaching / Soccer", 
    "notation": "SPO061030", 
    "alt_label": []
  }, 
  "Design / Graphic Arts / Branding & Logo Design": {
    "related": [], 
    "pref_label": "Design / Graphic Arts / Branding & Logo Design", 
    "notation": "DES007020", 
    "alt_label": []
  }, 
  "History / Modern / General": {
    "related": [], 
    "pref_label": "History / Modern / General", 
    "notation": "HIS037030", 
    "alt_label": []
  }, 
  "Self-help / Aging": {
    "related": [], 
    "pref_label": "Self-help / Aging", 
    "notation": "SEL005000", 
    "alt_label": []
  }, 
  "Science / Earth Sciences / Geology": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / Geology", 
    "notation": "SCI031000", 
    "alt_label": []
  }, 
  "Political Science / Reference": {
    "related": [], 
    "pref_label": "Political Science / Reference", 
    "notation": "POL018000", 
    "alt_label": []
  }, 
  "Music / Printed Music / Piano & Keyboard Repertoire": {
    "related": [], 
    "pref_label": "Music / Printed Music / Piano & Keyboard Repertoire", 
    "notation": "MUS037090", 
    "alt_label": []
  }, 
  "Sports & Recreation / Swimming & Diving": {
    "related": [], 
    "pref_label": "Sports & Recreation / Swimming & Diving", 
    "notation": "SPO043000", 
    "alt_label": []
  }, 
  "Science / Physics / Geophysics": {
    "related": [], 
    "pref_label": "Science / Physics / Geophysics", 
    "notation": "SCI032000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Size & Shape": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Size & Shape", 
    "notation": "JNF013070", 
    "alt_label": []
  }, 
  "Social Science / Customs & Traditions": {
    "related": [], 
    "pref_label": "Social Science / Customs & Traditions", 
    "notation": "SOC005000", 
    "alt_label": []
  }, 
  "Political Science / Law Enforcement": {
    "related": [], 
    "pref_label": "Political Science / Law Enforcement", 
    "notation": "POL014000", 
    "alt_label": []
  }, 
  "Travel / Europe / Eastern": {
    "related": [], 
    "pref_label": "Travel / Europe / Eastern", 
    "notation": "TRV009040", 
    "alt_label": []
  }, 
  "Religion / Judaism / Kabbalah & Mysticism": {
    "related": [], 
    "pref_label": "Religion / Judaism / Kabbalah & Mysticism", 
    "notation": "REL040060", 
    "alt_label": []
  }, 
  "History / Study & Teaching": {
    "related": [], 
    "pref_label": "History / Study & Teaching", 
    "notation": "HIS035000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Comics & Graphic Novels": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Comics & Graphic Novels", 
    "notation": "JUV033070", 
    "alt_label": []
  }, 
  "Medical / Lasers In Medicine": {
    "related": [], 
    "pref_label": "Medical / Lasers In Medicine", 
    "notation": "MED048000", 
    "alt_label": []
  }, 
  "Pets / Dogs / Training": {
    "related": [], 
    "pref_label": "Pets / Dogs / Training", 
    "notation": "PET004020", 
    "alt_label": []
  }, 
  "Business & Economics / Marketing / Multilevel": {
    "related": [], 
    "pref_label": "Business & Economics / Marketing / Multilevel", 
    "notation": "BUS043040", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Magazines & Newspapers": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Magazines & Newspapers", 
    "notation": "ANT023000", 
    "alt_label": [
      "Antiques & Collectibles / Newspapers"
    ]
  }, 
  "Juvenile Fiction / Concepts / Size & Shape": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Size & Shape", 
    "notation": "JUV009060", 
    "alt_label": []
  }, 
  "Medical / Biostatistics": {
    "related": [], 
    "pref_label": "Medical / Biostatistics", 
    "notation": "MED090000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Power Resources / Fossil Fuels": {
    "related": [], 
    "pref_label": "Technology & Engineering / Power Resources / Fossil Fuels", 
    "notation": "TEC031030", 
    "alt_label": []
  }, 
  "Science / Laboratory Techniques": {
    "related": [], 
    "pref_label": "Science / Laboratory Techniques", 
    "notation": "SCI093000", 
    "alt_label": []
  }, 
  "History / United States / 19th Century": {
    "related": [], 
    "pref_label": "History / United States / 19th Century", 
    "notation": "HIS036040", 
    "alt_label": []
  }, 
  "Law / Practical Guides": {
    "related": [], 
    "pref_label": "Law / Practical Guides", 
    "notation": "LAW098000", 
    "alt_label": []
  }, 
  "Science / Mechanics / Solids": {
    "related": [], 
    "pref_label": "Science / Mechanics / Solids", 
    "notation": "SCI096000", 
    "alt_label": []
  }, 
  "Law / Gender & The Law": {
    "related": [], 
    "pref_label": "Law / Gender & The Law", 
    "notation": "LAW043000", 
    "alt_label": []
  }, 
  "Fiction / Romance / Time Travel": {
    "related": [], 
    "pref_label": "Fiction / Romance / Time Travel", 
    "notation": "FIC027090", 
    "alt_label": []
  }, 
  "House & Home / General": {
    "related": [], 
    "pref_label": "House & Home / General", 
    "notation": "HOM000000", 
    "alt_label": []
  }, 
  "Business & Economics / Investments & Securities / General": {
    "related": [], 
    "pref_label": "Business & Economics / Investments & Securities / General", 
    "notation": "BUS036000", 
    "alt_label": []
  }, 
  "Political Science / Women In Politics": {
    "related": [], 
    "pref_label": "Political Science / Women In Politics", 
    "notation": "POL052000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Linguistics / Semantics": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Linguistics / Semantics", 
    "notation": "LAN016000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Martial Arts & Self-defense": {
    "related": [], 
    "pref_label": "Sports & Recreation / Martial Arts & Self-defense", 
    "notation": "SPO027000", 
    "alt_label": [
      "Sports & Recreation / Judo", 
      "Sports & Recreation / Karate", 
      "Sports & Recreation / Self-defense"
    ]
  }, 
  "Bibles / The Message / Study": {
    "related": [], 
    "pref_label": "Bibles / The Message / Study", 
    "notation": "BIB020050", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Kwanzaa": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Kwanzaa", 
    "notation": "JUV017050", 
    "alt_label": []
  }, 
  "Medical / Nursing / Research & Theory": {
    "related": [], 
    "pref_label": "Medical / Nursing / Research & Theory", 
    "notation": "MED058200", 
    "alt_label": []
  }, 
  "Art / Folk & Outsider Art": {
    "related": [], 
    "pref_label": "Art / Folk & Outsider Art", 
    "notation": "ART013000", 
    "alt_label": []
  }, 
  "Transportation / Motorcycles / General": {
    "related": [], 
    "pref_label": "Transportation / Motorcycles / General", 
    "notation": "TRA003000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Butterflies, Moths & Caterpillars": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Butterflies, Moths & Caterpillars", 
    "notation": "JNF003250", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Media Studies": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Media Studies", 
    "notation": "JNF060000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Boxing": {
    "related": [], 
    "pref_label": "Sports & Recreation / Boxing", 
    "notation": "SPO008000", 
    "alt_label": []
  }, 
  "Humor / Topic / Political": {
    "related": [], 
    "pref_label": "Humor / Topic / Political", 
    "notation": "HUM006000", 
    "alt_label": []
  }, 
  "Education / Reference": {
    "related": [], 
    "pref_label": "Education / Reference", 
    "notation": "EDU024000", 
    "alt_label": []
  }, 
  "Drama / European / German": {
    "related": [], 
    "pref_label": "Drama / European / German", 
    "notation": "DRA004020", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Astrology / Eastern": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Astrology / Eastern", 
    "notation": "OCC030000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Winter Sports": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Winter Sports", 
    "notation": "JNF054160", 
    "alt_label": []
  }, 
  "Education / Organizations & Institutions": {
    "related": [], 
    "pref_label": "Education / Organizations & Institutions", 
    "notation": "EDU036000", 
    "alt_label": [
      "Education / Institutions"
    ]
  }, 
  "Cooking / Beverages / Beer": {
    "related": [], 
    "pref_label": "Cooking / Beverages / Beer", 
    "notation": "CKB007000", 
    "alt_label": []
  }, 
  "Law / General Practice": {
    "related": [], 
    "pref_label": "Law / General Practice", 
    "notation": "LAW044000", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Sauces & Dressings": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Sauces & Dressings", 
    "notation": "CKB102000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Games & Activities": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Games & Activities", 
    "notation": "JNF049220", 
    "alt_label": []
  }, 
  "Computers / Operating Systems / Virtualization": {
    "related": [], 
    "pref_label": "Computers / Operating Systems / Virtualization", 
    "notation": "COM046090", 
    "alt_label": []
  }, 
  "Business & Economics / Development / Business Development": {
    "related": [], 
    "pref_label": "Business & Economics / Development / Business Development", 
    "notation": "BUS020000", 
    "alt_label": []
  }, 
  "Transportation / Ships & Shipbuilding / General": {
    "related": [], 
    "pref_label": "Transportation / Ships & Shipbuilding / General", 
    "notation": "TRA006000", 
    "alt_label": []
  }, 
  "Computers / Web / Search Engines": {
    "related": [], 
    "pref_label": "Computers / Web / Search Engines", 
    "notation": "COM060120", 
    "alt_label": []
  }, 
  "Computers / Desktop Applications / General": {
    "related": [], 
    "pref_label": "Computers / Desktop Applications / General", 
    "notation": "COM084000", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / Diabetic & Sugar-free": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / Diabetic & Sugar-free", 
    "notation": "CKB025000", 
    "alt_label": [
      "Cooking / Health & Healing / Low Sugar"
    ]
  }, 
  "Drama / European / English, Irish, Scottish, Welsh": {
    "related": [], 
    "pref_label": "Drama / European / English, Irish, Scottish, Welsh", 
    "notation": "DRA003000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Reptiles & Amphibians": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Reptiles & Amphibians", 
    "notation": "JNF003190", 
    "alt_label": []
  }, 
  "Architecture / Regional": {
    "related": [], 
    "pref_label": "Architecture / Regional", 
    "notation": "ARC020000", 
    "alt_label": []
  }, 
  "Fiction / Romance / Contemporary": {
    "related": [], 
    "pref_label": "Fiction / Romance / Contemporary", 
    "notation": "FIC027020", 
    "alt_label": []
  }, 
  "Technology & Engineering / Technical Writing": {
    "related": [], 
    "pref_label": "Technology & Engineering / Technical Writing", 
    "notation": "TEC044000", 
    "alt_label": []
  }, 
  "Fiction / African American / General": {
    "related": [], 
    "pref_label": "Fiction / African American / General", 
    "notation": "FIC049000", 
    "alt_label": []
  }, 
  "Fiction / Christian / Western": {
    "related": [], 
    "pref_label": "Fiction / Christian / Western", 
    "notation": "FIC042070", 
    "alt_label": []
  }, 
  "Medical / Surgery / Vascular": {
    "related": [], 
    "pref_label": "Medical / Surgery / Vascular", 
    "notation": "MED085050", 
    "alt_label": []
  }, 
  "Art / Museum Studies": {
    "related": [], 
    "pref_label": "Art / Museum Studies", 
    "notation": "ART059000", 
    "alt_label": []
  }, 
  "Computers / History": {
    "related": [], 
    "pref_label": "Computers / History", 
    "notation": "COM080000", 
    "alt_label": []
  }, 
  "Fiction / Romance / Short Stories": {
    "related": [], 
    "pref_label": "Fiction / Romance / Short Stories", 
    "notation": "FIC027080", 
    "alt_label": []
  }, 
  "Business & Economics / Forecasting": {
    "related": [], 
    "pref_label": "Business & Economics / Forecasting", 
    "notation": "BUS086000", 
    "alt_label": []
  }, 
  "Bibles / The Message / Reference": {
    "related": [], 
    "pref_label": "Bibles / The Message / Reference", 
    "notation": "BIB020040", 
    "alt_label": []
  }, 
  "Business & Economics / Customer Relations": {
    "related": [], 
    "pref_label": "Business & Economics / Customer Relations", 
    "notation": "BUS018000", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Pies": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Pies", 
    "notation": "CKB063000", 
    "alt_label": []
  }, 
  "Education / Teaching Methods & Materials / Mathematics": {
    "related": [], 
    "pref_label": "Education / Teaching Methods & Materials / Mathematics", 
    "notation": "EDU029010", 
    "alt_label": []
  }, 
  "Transportation / Aviation / History": {
    "related": [], 
    "pref_label": "Transportation / Aviation / History", 
    "notation": "TRA002010", 
    "alt_label": []
  }, 
  "Social Science / Children's Studies": {
    "related": [], 
    "pref_label": "Social Science / Children's Studies", 
    "notation": "SOC047000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Drafting & Mechanical Drawing": {
    "related": [], 
    "pref_label": "Technology & Engineering / Drafting & Mechanical Drawing", 
    "notation": "TEC006000", 
    "alt_label": [
      "Technology & Engineering / Mechanical Drawing"
    ]
  }, 
  "Architecture / Project Management": {
    "related": [], 
    "pref_label": "Architecture / Project Management", 
    "notation": "ARC017000", 
    "alt_label": []
  }, 
  "Travel / Former Soviet Republics": {
    "related": [], 
    "pref_label": "Travel / Former Soviet Republics", 
    "notation": "TRV012000", 
    "alt_label": []
  }, 
  "Travel / Europe / Greece": {
    "related": [], 
    "pref_label": "Travel / Europe / Greece", 
    "notation": "TRV009080", 
    "alt_label": []
  }, 
  "Medical / Embryology": {
    "related": [], 
    "pref_label": "Medical / Embryology", 
    "notation": "MED025000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Care & Restoration": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Care & Restoration", 
    "notation": "ANT008000", 
    "alt_label": [
      "Antiques & Collectibles / Restoration"
    ]
  }, 
  "House & Home / Equipment, Appliances & Supplies": {
    "related": [], 
    "pref_label": "House & Home / Equipment, Appliances & Supplies", 
    "notation": "HOM020000", 
    "alt_label": []
  }, 
  "Education / Higher": {
    "related": [], 
    "pref_label": "Education / Higher", 
    "notation": "EDU015000", 
    "alt_label": []
  }, 
  "Fiction / African American / Urban Life": {
    "related": [], 
    "pref_label": "Fiction / African American / Urban Life", 
    "notation": "FIC049070", 
    "alt_label": []
  }, 
  "Travel / Europe / Germany": {
    "related": [], 
    "pref_label": "Travel / Europe / Germany", 
    "notation": "TRV009060", 
    "alt_label": []
  }, 
  "Games / Card Games / Poker": {
    "related": [], 
    "pref_label": "Games / Card Games / Poker", 
    "notation": "GAM002040", 
    "alt_label": []
  }, 
  "Music / Instruction & Study / Composition": {
    "related": [], 
    "pref_label": "Music / Instruction & Study / Composition", 
    "notation": "MUS007000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Korean": {
    "related": [], 
    "pref_label": "Foreign Language Study / Korean", 
    "notation": "FOR015000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Inspiration & Personal Growth": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Inspiration & Personal Growth", 
    "notation": "OCC019000", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Attention-deficit Disorder (add-adhd)": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Attention-deficit Disorder (add-adhd)", 
    "notation": "PSY022010", 
    "alt_label": []
  }, 
  "Poetry / Subjects & Themes / Inspirational & Religious": {
    "related": [], 
    "pref_label": "Poetry / Subjects & Themes / Inspirational & Religious", 
    "notation": "POE003000", 
    "alt_label": []
  }, 
  "Social Science / Discrimination & Race Relations": {
    "related": [], 
    "pref_label": "Social Science / Discrimination & Race Relations", 
    "notation": "SOC031000", 
    "alt_label": [
      "Social Science / Race Relations"
    ]
  }, 
  "Religion / Inspirational": {
    "related": [], 
    "pref_label": "Religion / Inspirational", 
    "notation": "REL036000", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Structuralism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Structuralism", 
    "notation": "PHI029000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Library & Information Science / Administration & Management": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Library & Information Science / Administration & Management", 
    "notation": "LAN025010", 
    "alt_label": []
  }, 
  "Religion / Islam / Sufi": {
    "related": [], 
    "pref_label": "Religion / Islam / Sufi", 
    "notation": "REL090000", 
    "alt_label": [
      "Religion / Sufi"
    ]
  }, 
  "Juvenile Nonfiction / Animals / Nocturnal": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Nocturnal", 
    "notation": "JNF003320", 
    "alt_label": []
  }, 
  "Music / Printed Music / Guitar & Fretted Instruments": {
    "related": [], 
    "pref_label": "Music / Printed Music / Guitar & Fretted Instruments", 
    "notation": "MUS037040", 
    "alt_label": []
  }, 
  "Travel / Africa / West": {
    "related": [], 
    "pref_label": "Travel / Africa / West", 
    "notation": "TRV002080", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Lifestyles / Country Life": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Lifestyles / Country Life", 
    "notation": "JNF032000", 
    "alt_label": []
  }, 
  "Fiction / Biographical": {
    "related": [], 
    "pref_label": "Fiction / Biographical", 
    "notation": "FIC041000", 
    "alt_label": []
  }, 
  "Art / Techniques / Life Drawing": {
    "related": [], 
    "pref_label": "Art / Techniques / Life Drawing", 
    "notation": "ART052000", 
    "alt_label": []
  }, 
  "Social Science / Anthropology / General": {
    "related": [], 
    "pref_label": "Social Science / Anthropology / General", 
    "notation": "SOC002000", 
    "alt_label": []
  }, 
  "Performing Arts / Circus": {
    "related": [], 
    "pref_label": "Performing Arts / Circus", 
    "notation": "PER002000", 
    "alt_label": []
  }, 
  "History / Modern / 19th Century": {
    "related": [], 
    "pref_label": "History / Modern / 19th Century", 
    "notation": "HIS037060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Deer, Moose & Caribou": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Deer, Moose & Caribou", 
    "notation": "JNF003230", 
    "alt_label": []
  }, 
  "Humor / Form / Jokes & Riddles": {
    "related": [], 
    "pref_label": "Humor / Form / Jokes & Riddles", 
    "notation": "HUM004000", 
    "alt_label": []
  }, 
  "Reference / Curiosities & Wonders": {
    "related": [], 
    "pref_label": "Reference / Curiosities & Wonders", 
    "notation": "REF007000", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Lakes, Ponds & Swamps": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Lakes, Ponds & Swamps", 
    "notation": "NAT018000", 
    "alt_label": []
  }, 
  "Poetry / European / General": {
    "related": [], 
    "pref_label": "Poetry / European / General", 
    "notation": "POE005030", 
    "alt_label": []
  }, 
  "Transportation / Automotive / History": {
    "related": [], 
    "pref_label": "Transportation / Automotive / History", 
    "notation": "TRA001050", 
    "alt_label": []
  }, 
  "Reference / Dictionaries": {
    "related": [], 
    "pref_label": "Reference / Dictionaries", 
    "notation": "REF008000", 
    "alt_label": []
  }, 
  "Business & Economics / Marketing / Telemarketing": {
    "related": [], 
    "pref_label": "Business & Economics / Marketing / Telemarketing", 
    "notation": "BUS043050", 
    "alt_label": []
  }, 
  "Science / Physics / Electromagnetism": {
    "related": [], 
    "pref_label": "Science / Physics / Electromagnetism", 
    "notation": "SCI022000", 
    "alt_label": []
  }, 
  "House & Home / Decorating": {
    "related": [], 
    "pref_label": "House & Home / Decorating", 
    "notation": "HOM003000", 
    "alt_label": []
  }, 
  "Law / Alternative Dispute Resolution": {
    "related": [], 
    "pref_label": "Law / Alternative Dispute Resolution", 
    "notation": "LAW003000", 
    "alt_label": []
  }, 
  "Fiction / Romance / Fantasy": {
    "related": [], 
    "pref_label": "Fiction / Romance / Fantasy", 
    "notation": "FIC027030", 
    "alt_label": []
  }, 
  "Political Science / Political Economy": {
    "related": [], 
    "pref_label": "Political Science / Political Economy", 
    "notation": "POL023000", 
    "alt_label": []
  }, 
  "Religion / Biblical Meditations / General": {
    "related": [], 
    "pref_label": "Religion / Biblical Meditations / General", 
    "notation": "REL006110", 
    "alt_label": []
  }, 
  "Computers / Networking / Intranets & Extranets": {
    "related": [], 
    "pref_label": "Computers / Networking / Intranets & Extranets", 
    "notation": "COM060030", 
    "alt_label": [
      "Computers / Internet / Intranets"
    ]
  }, 
  "Biography & Autobiography / Native Americans": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Native Americans", 
    "notation": "BIO028000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Park & Recreation Management": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Park & Recreation Management", 
    "notation": "BUS070070", 
    "alt_label": []
  }, 
  "Religion / Hinduism / Sacred Writings": {
    "related": [], 
    "pref_label": "Religion / Hinduism / Sacred Writings", 
    "notation": "REL032030", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Figurines": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Figurines", 
    "notation": "ANT053000", 
    "alt_label": [
      "Antiques & Collectibles / Hummels"
    ]
  }, 
  "Bibles / Multiple Translations / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / Multiple Translations / New Testament & Portions", 
    "notation": "BIB008030", 
    "alt_label": []
  }, 
  "Poetry / Australian & Oceanian": {
    "related": [], 
    "pref_label": "Poetry / Australian & Oceanian", 
    "notation": "POE010000", 
    "alt_label": []
  }, 
  "Travel / United States / Northeast / Middle Atlantic (nj, Ny, Pa)": {
    "related": [], 
    "pref_label": "Travel / United States / Northeast / Middle Atlantic (nj, Ny, Pa)", 
    "notation": "TRV025050", 
    "alt_label": []
  }, 
  "Medical / Allied Health Services / Medical Assistants": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / Medical Assistants", 
    "notation": "MED003030", 
    "alt_label": []
  }, 
  "Sports & Recreation / Table Tennis": {
    "related": [], 
    "pref_label": "Sports & Recreation / Table Tennis", 
    "notation": "SPO044000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Racket Sports": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Racket Sports", 
    "notation": "JNF054120", 
    "alt_label": []
  }, 
  "Games / Fantasy Sports": {
    "related": [], 
    "pref_label": "Games / Fantasy Sports", 
    "notation": "GAM016000", 
    "alt_label": []
  }, 
  "Travel / Canada / Atlantic Provinces (nb, Nf, Ns, Pe)": {
    "related": [], 
    "pref_label": "Travel / Canada / Atlantic Provinces (nb, Nf, Ns, Pe)", 
    "notation": "TRV006010", 
    "alt_label": []
  }, 
  "Technology & Engineering / Industrial Engineering": {
    "related": [], 
    "pref_label": "Technology & Engineering / Industrial Engineering", 
    "notation": "TEC009060", 
    "alt_label": []
  }, 
  "Religion / Christian Church / Leadership": {
    "related": [], 
    "pref_label": "Religion / Christian Church / Leadership", 
    "notation": "REL108030", 
    "alt_label": []
  }, 
  "Religion / Christianity / Anglican": {
    "related": [], 
    "pref_label": "Religion / Christianity / Anglican", 
    "notation": "REL003000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Gaia & Earth Energies": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Gaia & Earth Energies", 
    "notation": "OCC033000", 
    "alt_label": []
  }, 
  "Games / Travel Games": {
    "related": [], 
    "pref_label": "Games / Travel Games", 
    "notation": "GAM011000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Quality Control": {
    "related": [], 
    "pref_label": "Technology & Engineering / Quality Control", 
    "notation": "TEC032000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Lifestyles / Farm & Ranch Life": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Lifestyles / Farm & Ranch Life", 
    "notation": "JUV025000", 
    "alt_label": [
      "Juvenile Fiction / Farm Life"
    ]
  }, 
  "Business & Economics / Industries / Hospitality, Travel & Tourism": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Hospitality, Travel & Tourism", 
    "notation": "BUS081000", 
    "alt_label": [
      "Business & Economics / Hospitality, Travel & Tourism", 
      "Business & Economics / Travel & Tourism"
    ]
  }, 
  "Juvenile Fiction / Science Fiction": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Science Fiction", 
    "notation": "JUV053000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Ancient Civilizations": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Ancient Civilizations", 
    "notation": "JUV016020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Alligators & Crocodiles": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Alligators & Crocodiles", 
    "notation": "JUV002010", 
    "alt_label": []
  }, 
  "Philosophy / Zen": {
    "related": [], 
    "pref_label": "Philosophy / Zen", 
    "notation": "PHI025000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Holidays & Celebrations / Other, Non-religious": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Holidays & Celebrations / Other, Non-religious", 
    "notation": "JNF026080", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Historical Fiction": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Historical Fiction", 
    "notation": "CGN004140", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Readers / Beginner": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Readers / Beginner", 
    "notation": "JNF045000", 
    "alt_label": []
  }, 
  "Social Science / Disasters & Disaster Relief": {
    "related": [], 
    "pref_label": "Social Science / Disasters & Disaster Relief", 
    "notation": "SOC040000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Hockey": {
    "related": [], 
    "pref_label": "Sports & Recreation / Hockey", 
    "notation": "SPO020000", 
    "alt_label": []
  }, 
  "Religion / Unitarian Universalism": {
    "related": [], 
    "pref_label": "Religion / Unitarian Universalism", 
    "notation": "REL103000", 
    "alt_label": [
      "Religion / Christianity / Unitarian Universalism"
    ]
  }, 
  "Crafts & Hobbies / Woodwork": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Woodwork", 
    "notation": "CRA042000", 
    "alt_label": []
  }, 
  "Bibles / New Revised Standard Version / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / New Revised Standard Version / Youth & Teen", 
    "notation": "BIB016070", 
    "alt_label": []
  }, 
  "Medical / Nursing / Pharmacology": {
    "related": [], 
    "pref_label": "Medical / Nursing / Pharmacology", 
    "notation": "MED058170", 
    "alt_label": []
  }, 
  "Medical / Veterinary Medicine / General": {
    "related": [], 
    "pref_label": "Medical / Veterinary Medicine / General", 
    "notation": "MED089000", 
    "alt_label": []
  }, 
  "Computers / Computer Literacy": {
    "related": [], 
    "pref_label": "Computers / Computer Literacy", 
    "notation": "COM013000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Gymnastics": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Gymnastics", 
    "notation": "JNF054060", 
    "alt_label": []
  }, 
  "Science / Physics / Relativity": {
    "related": [], 
    "pref_label": "Science / Physics / Relativity", 
    "notation": "SCI061000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Games & Activities / Word Games": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Games & Activities / Word Games", 
    "notation": "JNF021070", 
    "alt_label": []
  }, 
  "Computers / Computer Graphics": {
    "related": [], 
    "pref_label": "Computers / Computer Graphics", 
    "notation": "COM012000", 
    "alt_label": []
  }, 
  "Art / Techniques / Color": {
    "related": [], 
    "pref_label": "Art / Techniques / Color", 
    "notation": "ART051000", 
    "alt_label": []
  }, 
  "Mathematics / History & Philosophy": {
    "related": [], 
    "pref_label": "Mathematics / History & Philosophy", 
    "notation": "MAT015000", 
    "alt_label": []
  }, 
  "Health & Fitness / Body Cleansing & Detoxification": {
    "related": [], 
    "pref_label": "Health & Fitness / Body Cleansing & Detoxification", 
    "notation": "HEA047000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Art / Drawing": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Art / Drawing", 
    "notation": "JNF006020", 
    "alt_label": []
  }, 
  "Architecture / Codes & Standards": {
    "related": [], 
    "pref_label": "Architecture / Codes & Standards", 
    "notation": "ARC019000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Paper Ephemera": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Paper Ephemera", 
    "notation": "ANT029000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Books & Libraries": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Books & Libraries", 
    "notation": "JNF063000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / United States / Civil War Period (1850-1877)": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / United States / Civil War Period (1850-1877)", 
    "notation": "JNF025270", 
    "alt_label": []
  }, 
  "Travel / United States / Northeast / New England (ct, Ma, Me, Nh, Ri, Vt)": {
    "related": [], 
    "pref_label": "Travel / United States / Northeast / New England (ct, Ma, Me, Nh, Ri, Vt)", 
    "notation": "TRV025060", 
    "alt_label": []
  }, 
  "Business & Economics / Business Communication / Meetings & Presentations": {
    "related": [], 
    "pref_label": "Business & Economics / Business Communication / Meetings & Presentations", 
    "notation": "BUS007010", 
    "alt_label": []
  }, 
  "Reference / Personal & Practical Guides": {
    "related": [], 
    "pref_label": "Reference / Personal & Practical Guides", 
    "notation": "REF015000", 
    "alt_label": [
      "Reference / Basic Skills"
    ]
  }, 
  "Religion / Education": {
    "related": [], 
    "pref_label": "Religion / Education", 
    "notation": "REL026000", 
    "alt_label": []
  }, 
  "True Crime / General": {
    "related": [], 
    "pref_label": "True Crime / General", 
    "notation": "TRU000000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Architecture": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Architecture", 
    "notation": "JNF005000", 
    "alt_label": []
  }, 
  "Business & Economics / Investments & Securities / Commodities": {
    "related": [], 
    "pref_label": "Business & Economics / Investments & Securities / Commodities", 
    "notation": "BUS014000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Models": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Models", 
    "notation": "CRA020000", 
    "alt_label": []
  }, 
  "Nature / Plants / Mushrooms": {
    "related": [], 
    "pref_label": "Nature / Plants / Mushrooms", 
    "notation": "NAT022000", 
    "alt_label": []
  }, 
  "Music / Religious / Contemporary Christian": {
    "related": [], 
    "pref_label": "Music / Religious / Contemporary Christian", 
    "notation": "MUS009000", 
    "alt_label": []
  }, 
  "Education / Elementary": {
    "related": [], 
    "pref_label": "Education / Elementary", 
    "notation": "EDU010000", 
    "alt_label": []
  }, 
  "Education / Evaluation & Assessment": {
    "related": [], 
    "pref_label": "Education / Evaluation & Assessment", 
    "notation": "EDU011000", 
    "alt_label": []
  }, 
  "Social Science / Volunteer Work": {
    "related": [], 
    "pref_label": "Social Science / Volunteer Work", 
    "notation": "SOC035000", 
    "alt_label": []
  }, 
  "Science / Mechanics / Thermodynamics": {
    "related": [], 
    "pref_label": "Science / Mechanics / Thermodynamics", 
    "notation": "SCI065000", 
    "alt_label": []
  }, 
  "Political Science / Imperialism": {
    "related": [], 
    "pref_label": "Political Science / Imperialism", 
    "notation": "POL047000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Eschatology": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Eschatology", 
    "notation": "REL067060", 
    "alt_label": []
  }, 
  "Computers / Digital Media / Desktop Publishing": {
    "related": [], 
    "pref_label": "Computers / Digital Media / Desktop Publishing", 
    "notation": "COM022000", 
    "alt_label": []
  }, 
  "Music / Individual Composer & Musician": {
    "related": [], 
    "pref_label": "Music / Individual Composer & Musician", 
    "notation": "MUS050000", 
    "alt_label": []
  }, 
  "Medical / Dentistry / Dental Assisting": {
    "related": [], 
    "pref_label": "Medical / Dentistry / Dental Assisting", 
    "notation": "MED016010", 
    "alt_label": []
  }, 
  "Bibles / La Biblia De Las Americas / Children": {
    "related": [], 
    "pref_label": "Bibles / La Biblia De Las Americas / Children", 
    "notation": "BIB007010", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Toy Animals": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Toy Animals", 
    "notation": "ANT049000", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / Low Salt": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / Low Salt", 
    "notation": "CKB052000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Science / Sociology": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Science / Sociology", 
    "notation": "JNF052040", 
    "alt_label": []
  }, 
  "Education / Vocational": {
    "related": [], 
    "pref_label": "Education / Vocational", 
    "notation": "EDU056000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Technology / Aeronautics, Astronautics & Space Science": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Technology / Aeronautics, Astronautics & Space Science", 
    "notation": "JNF051010", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Needlework / Crocheting": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Needlework / Crocheting", 
    "notation": "CRA004000", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / General": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / General", 
    "notation": "CKB039000", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / Wisdom Literature": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / Wisdom Literature", 
    "notation": "REL006740", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Transportation / Motorcycles": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Transportation / Motorcycles", 
    "notation": "JNF057040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Cooking & Food": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Cooking & Food", 
    "notation": "JUV050000", 
    "alt_label": []
  }, 
  "History / Essays": {
    "related": [], 
    "pref_label": "History / Essays", 
    "notation": "HIS049000", 
    "alt_label": []
  }, 
  "Medical / Holistic Medicine": {
    "related": [], 
    "pref_label": "Medical / Holistic Medicine", 
    "notation": "MED040000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Fantasy": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Fantasy", 
    "notation": "JUV033110", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Crime & Mystery": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Crime & Mystery", 
    "notation": "CGN004100", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Prejudice & Racism": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Prejudice & Racism", 
    "notation": "JUV039120", 
    "alt_label": []
  }, 
  "Foreign Language Study / Greek (modern)": {
    "related": [], 
    "pref_label": "Foreign Language Study / Greek (modern)", 
    "notation": "FOR010000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Environmental / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / Environmental / General", 
    "notation": "TEC010000", 
    "alt_label": []
  }, 
  "Fiction / Science Fiction / Space Opera": {
    "related": [], 
    "pref_label": "Fiction / Science Fiction / Space Opera", 
    "notation": "FIC028030", 
    "alt_label": []
  }, 
  "Bibles / King James Version / Children": {
    "related": [], 
    "pref_label": "Bibles / King James Version / Children", 
    "notation": "BIB006010", 
    "alt_label": []
  }, 
  "Law / Child Advocacy": {
    "related": [], 
    "pref_label": "Law / Child Advocacy", 
    "notation": "LAW010000", 
    "alt_label": []
  }, 
  "Travel / Europe / Western": {
    "related": [], 
    "pref_label": "Travel / Europe / Western", 
    "notation": "TRV009150", 
    "alt_label": []
  }, 
  "Social Science / Social Work": {
    "related": [], 
    "pref_label": "Social Science / Social Work", 
    "notation": "SOC025000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Electronic": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Electronic", 
    "notation": "MUS013000", 
    "alt_label": []
  }, 
  "Business & Economics / Personal Finance / Taxation": {
    "related": [], 
    "pref_label": "Business & Economics / Personal Finance / Taxation", 
    "notation": "BUS050050", 
    "alt_label": [
      "Business & Economics / Taxation / Personal"
    ]
  }, 
  "Juvenile Nonfiction / Social Issues / Pregnancy": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Pregnancy", 
    "notation": "JNF053130", 
    "alt_label": []
  }, 
  "Business & Economics / Economics / Theory": {
    "related": [], 
    "pref_label": "Business & Economics / Economics / Theory", 
    "notation": "BUS069030", 
    "alt_label": []
  }, 
  "Gardening / Shrubs": {
    "related": [], 
    "pref_label": "Gardening / Shrubs", 
    "notation": "GAR021000", 
    "alt_label": [
      "Gardening / Flowers / Azaleas"
    ]
  }, 
  "Education / Leadership": {
    "related": [], 
    "pref_label": "Education / Leadership", 
    "notation": "EDU032000", 
    "alt_label": []
  }, 
  "Transportation / Ships & Shipbuilding / Pictorial": {
    "related": [], 
    "pref_label": "Transportation / Ships & Shipbuilding / Pictorial", 
    "notation": "TRA006020", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / General": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / General", 
    "notation": "PSY022000", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Family": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Family", 
    "notation": "TRV011000", 
    "alt_label": [
      "Travel / Family Travel"
    ]
  }, 
  "Education / Educational Policy & Reform / School Safety": {
    "related": [], 
    "pref_label": "Education / Educational Policy & Reform / School Safety", 
    "notation": "EDU034010", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / Tropical Agriculture": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / Tropical Agriculture", 
    "notation": "TEC003010", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / C#": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / C#", 
    "notation": "COM051310", 
    "alt_label": []
  }, 
  "Literary Collections / Asian / Japanese": {
    "related": [], 
    "pref_label": "Literary Collections / Asian / Japanese", 
    "notation": "LCO004030", 
    "alt_label": []
  }, 
  "Technology & Engineering / Automotive": {
    "related": [], 
    "pref_label": "Technology & Engineering / Automotive", 
    "notation": "TEC009090", 
    "alt_label": []
  }, 
  "Religion / Reference": {
    "related": [], 
    "pref_label": "Religion / Reference", 
    "notation": "REL054000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Special Needs": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Special Needs", 
    "notation": "JNF053180", 
    "alt_label": []
  }, 
  "Bibles / New Living Translation / General": {
    "related": [], 
    "pref_label": "Bibles / New Living Translation / General", 
    "notation": "BIB015000", 
    "alt_label": []
  }, 
  "Philosophy / Essays": {
    "related": [], 
    "pref_label": "Philosophy / Essays", 
    "notation": "PHI035000", 
    "alt_label": []
  }, 
  "Bibles / God's Word / Reference": {
    "related": [], 
    "pref_label": "Bibles / God's Word / Reference", 
    "notation": "BIB004040", 
    "alt_label": []
  }, 
  "Psychology / Cognitive Psychology": {
    "related": [], 
    "pref_label": "Psychology / Cognitive Psychology", 
    "notation": "PSY008000", 
    "alt_label": []
  }, 
  "Mathematics / Probability & Statistics / Multivariate Analysis": {
    "related": [], 
    "pref_label": "Mathematics / Probability & Statistics / Multivariate Analysis", 
    "notation": "MAT029020", 
    "alt_label": []
  }, 
  "Literary Criticism / American / General": {
    "related": [], 
    "pref_label": "Literary Criticism / American / General", 
    "notation": "LIT004020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Asia": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Asia", 
    "notation": "JNF025030", 
    "alt_label": []
  }, 
  "Social Science / Freemasonry & Secret Societies": {
    "related": [], 
    "pref_label": "Social Science / Freemasonry & Secret Societies", 
    "notation": "SOC038000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Performing Arts / Television & Radio": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Performing Arts / Television & Radio", 
    "notation": "JNF039040", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Men's Issues": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Men's Issues", 
    "notation": "REL012060", 
    "alt_label": []
  }, 
  "Science / Physics / Magnetism": {
    "related": [], 
    "pref_label": "Science / Physics / Magnetism", 
    "notation": "SCI038000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Unexplained Phenomena": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Unexplained Phenomena", 
    "notation": "OCC029000", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Ecotourism": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Ecotourism", 
    "notation": "TRV026020", 
    "alt_label": []
  }, 
  "Computers / Speech & Audio Processing": {
    "related": [], 
    "pref_label": "Computers / Speech & Audio Processing", 
    "notation": "COM073000", 
    "alt_label": []
  }, 
  "Bibles / Common English Bible / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / Common English Bible / Youth & Teen", 
    "notation": "BIB022070", 
    "alt_label": []
  }, 
  "Mathematics / Geometry / General": {
    "related": [], 
    "pref_label": "Mathematics / Geometry / General", 
    "notation": "MAT012000", 
    "alt_label": []
  }, 
  "Travel / United States / West / Mountain (az, Co, Id, Mt, Nm, Ut, Wy)": {
    "related": [], 
    "pref_label": "Travel / United States / West / Mountain (az, Co, Id, Mt, Nm, Ut, Wy)", 
    "notation": "TRV025120", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / American / New England": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / American / New England", 
    "notation": "CKB002040", 
    "alt_label": []
  }, 
  "Business & Economics / Production & Operations Management": {
    "related": [], 
    "pref_label": "Business & Economics / Production & Operations Management", 
    "notation": "BUS087000", 
    "alt_label": [
      "Business & Economics / Operations Management"
    ]
  }, 
  "Computers / Programming Languages / Assembly Language": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Assembly Language", 
    "notation": "COM051040", 
    "alt_label": []
  }, 
  "Medical / Nursing / Pediatric & Neonatal": {
    "related": [], 
    "pref_label": "Medical / Nursing / Pediatric & Neonatal", 
    "notation": "MED058080", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Zoology / Mammals": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Zoology / Mammals", 
    "notation": "SCI070030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Biblical Commentaries & Interpretation": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Biblical Commentaries & Interpretation", 
    "notation": "JNF049030", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Library & Information Science / General": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Library & Information Science / General", 
    "notation": "LAN025000", 
    "alt_label": []
  }, 
  "Computers / Programming / General": {
    "related": [], 
    "pref_label": "Computers / Programming / General", 
    "notation": "COM051000", 
    "alt_label": []
  }, 
  "Performing Arts / Dance / Reference": {
    "related": [], 
    "pref_label": "Performing Arts / Dance / Reference", 
    "notation": "PER003070", 
    "alt_label": []
  }, 
  "Design / Fashion": {
    "related": [], 
    "pref_label": "Design / Fashion", 
    "notation": "DES005000", 
    "alt_label": []
  }, 
  "Self-help / Personal Growth / Success": {
    "related": [], 
    "pref_label": "Self-help / Personal Growth / Success", 
    "notation": "SEL027000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Outdoor Skills": {
    "related": [], 
    "pref_label": "Sports & Recreation / Outdoor Skills", 
    "notation": "SPO030000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Dutch": {
    "related": [], 
    "pref_label": "Foreign Language Study / Dutch", 
    "notation": "FOR006000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Nature Crafts": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Nature Crafts", 
    "notation": "CRA053000", 
    "alt_label": []
  }, 
  "Health & Fitness / Healing": {
    "related": [], 
    "pref_label": "Health & Fitness / Healing", 
    "notation": "HEA009000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Baseball / History": {
    "related": [], 
    "pref_label": "Sports & Recreation / Baseball / History", 
    "notation": "SPO003030", 
    "alt_label": []
  }, 
  "Business & Economics / Decision-making & Problem Solving": {
    "related": [], 
    "pref_label": "Business & Economics / Decision-making & Problem Solving", 
    "notation": "BUS019000", 
    "alt_label": []
  }, 
  "Art / Performance": {
    "related": [], 
    "pref_label": "Art / Performance", 
    "notation": "ART060000", 
    "alt_label": []
  }, 
  "Travel / Canada / General": {
    "related": [], 
    "pref_label": "Travel / Canada / General", 
    "notation": "TRV006000", 
    "alt_label": []
  }, 
  "Gardening / Landscape": {
    "related": [], 
    "pref_label": "Gardening / Landscape", 
    "notation": "GAR014000", 
    "alt_label": []
  }, 
  "Cooking / Methods / Professional": {
    "related": [], 
    "pref_label": "Cooking / Methods / Professional", 
    "notation": "CKB068000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Eastern": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Eastern", 
    "notation": "JNF049090", 
    "alt_label": []
  }, 
  "Religion / Buddhism / Tibetan": {
    "related": [], 
    "pref_label": "Religion / Buddhism / Tibetan", 
    "notation": "REL007050", 
    "alt_label": []
  }, 
  "Literary Criticism / Children's Literature": {
    "related": [], 
    "pref_label": "Literary Criticism / Children's Literature", 
    "notation": "LIT009000", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Poultry": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Poultry", 
    "notation": "CKB067000", 
    "alt_label": []
  }, 
  "Music / Printed Music / Musicals, Film & Tv": {
    "related": [], 
    "pref_label": "Music / Printed Music / Musicals, Film & Tv", 
    "notation": "MUS037060", 
    "alt_label": []
  }, 
  "Art / Criticism & Theory": {
    "related": [], 
    "pref_label": "Art / Criticism & Theory", 
    "notation": "ART009000", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Post-traumatic Stress Disorder (ptsd)": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Post-traumatic Stress Disorder (ptsd)", 
    "notation": "PSY022040", 
    "alt_label": []
  }, 
  "Business & Economics / Government & Business": {
    "related": [], 
    "pref_label": "Business & Economics / Government & Business", 
    "notation": "BUS079000", 
    "alt_label": []
  }, 
  "Political Science / Globalization": {
    "related": [], 
    "pref_label": "Political Science / Globalization", 
    "notation": "POL033000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Swahili": {
    "related": [], 
    "pref_label": "Foreign Language Study / Swahili", 
    "notation": "FOR042000", 
    "alt_label": []
  }, 
  "Medical / Allied Health Services / Respiratory Therapy": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / Respiratory Therapy", 
    "notation": "MED003080", 
    "alt_label": []
  }, 
  "Business & Economics / Personal Finance / Investing": {
    "related": [], 
    "pref_label": "Business & Economics / Personal Finance / Investing", 
    "notation": "BUS050020", 
    "alt_label": []
  }, 
  "Self-help / Substance Abuse & Addictions / General": {
    "related": [], 
    "pref_label": "Self-help / Substance Abuse & Addictions / General", 
    "notation": "SEL026000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Devotional & Prayer": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Devotional & Prayer", 
    "notation": "JNF049120", 
    "alt_label": []
  }, 
  "Study Aids / Advanced Placement": {
    "related": [], 
    "pref_label": "Study Aids / Advanced Placement", 
    "notation": "STU002000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Ufos & Extraterrestrials": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Ufos & Extraterrestrials", 
    "notation": "OCC025000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Health & Daily Living / Toilet Training": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Health & Daily Living / Toilet Training", 
    "notation": "JUV039170", 
    "alt_label": []
  }, 
  "Religion / Ethics": {
    "related": [], 
    "pref_label": "Religion / Ethics", 
    "notation": "REL028000", 
    "alt_label": []
  }, 
  "Computers / Digital Media / General": {
    "related": [], 
    "pref_label": "Computers / Digital Media / General", 
    "notation": "COM087000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Cats": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Cats", 
    "notation": "JNF003040", 
    "alt_label": []
  }, 
  "Computers / Cybernetics": {
    "related": [], 
    "pref_label": "Computers / Cybernetics", 
    "notation": "COM017000", 
    "alt_label": []
  }, 
  "Science / Physics / Atomic & Molecular": {
    "related": [], 
    "pref_label": "Science / Physics / Atomic & Molecular", 
    "notation": "SCI074000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Soccer": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Soccer", 
    "notation": "JNF054130", 
    "alt_label": []
  }, 
  "Art / Individual Artists / Monographs": {
    "related": [], 
    "pref_label": "Art / Individual Artists / Monographs", 
    "notation": "ART016030", 
    "alt_label": []
  }, 
  "Law / Public Utilities": {
    "related": [], 
    "pref_label": "Law / Public Utilities", 
    "notation": "LAW077000", 
    "alt_label": []
  }, 
  "Design / Product": {
    "related": [], 
    "pref_label": "Design / Product", 
    "notation": "DES011000", 
    "alt_label": []
  }, 
  "Psychology / Ethnopsychology": {
    "related": [], 
    "pref_label": "Psychology / Ethnopsychology", 
    "notation": "PSY050000", 
    "alt_label": []
  }, 
  "History / Africa / South / Republic Of South Africa": {
    "related": [], 
    "pref_label": "History / Africa / South / Republic Of South Africa", 
    "notation": "HIS047000", 
    "alt_label": []
  }, 
  "Family & Relationships / Conflict Resolution": {
    "related": [], 
    "pref_label": "Family & Relationships / Conflict Resolution", 
    "notation": "FAM013000", 
    "alt_label": []
  }, 
  "Political Science / Political Freedom": {
    "related": [], 
    "pref_label": "Political Science / Political Freedom", 
    "notation": "POL035000", 
    "alt_label": []
  }, 
  "Mathematics / Algebra / Linear": {
    "related": [], 
    "pref_label": "Mathematics / Algebra / Linear", 
    "notation": "MAT002050", 
    "alt_label": []
  }, 
  "Art / European": {
    "related": [], 
    "pref_label": "Art / European", 
    "notation": "ART015030", 
    "alt_label": []
  }, 
  "Psychology / Forensic Psychology": {
    "related": [], 
    "pref_label": "Psychology / Forensic Psychology", 
    "notation": "PSY014000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Visual Basic": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Visual Basic", 
    "notation": "COM051200", 
    "alt_label": []
  }, 
  "History / Military / Biological & Chemical Warfare": {
    "related": [], 
    "pref_label": "History / Military / Biological & Chemical Warfare", 
    "notation": "HIS027010", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Sports Cards / General": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Sports Cards / General", 
    "notation": "ANT042000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Seasonal": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Seasonal", 
    "notation": "CRA034000", 
    "alt_label": []
  }, 
  "Education / Distance & Online Education": {
    "related": [], 
    "pref_label": "Education / Distance & Online Education", 
    "notation": "EDU041000", 
    "alt_label": []
  }, 
  "Fiction / Satire": {
    "related": [], 
    "pref_label": "Fiction / Satire", 
    "notation": "FIC052000", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Deserts": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Deserts", 
    "notation": "NAT045010", 
    "alt_label": []
  }, 
  "Music / Ethnomusicology": {
    "related": [], 
    "pref_label": "Music / Ethnomusicology", 
    "notation": "MUS015000", 
    "alt_label": []
  }, 
  "Pets / Rabbits, Mice, Hamsters, Guinea Pigs, Etc.": {
    "related": [], 
    "pref_label": "Pets / Rabbits, Mice, Hamsters, Guinea Pigs, Etc.", 
    "notation": "PET011000", 
    "alt_label": []
  }, 
  "Medical / Pathology": {
    "related": [], 
    "pref_label": "Medical / Pathology", 
    "notation": "MED067000", 
    "alt_label": []
  }, 
  "Photography / Annuals": {
    "related": [], 
    "pref_label": "Photography / Annuals", 
    "notation": "PHO025000", 
    "alt_label": []
  }, 
  "Nature / Regional": {
    "related": [], 
    "pref_label": "Nature / Regional", 
    "notation": "NAT049000", 
    "alt_label": []
  }, 
  "Religion / Islam / Theology": {
    "related": [], 
    "pref_label": "Religion / Islam / Theology", 
    "notation": "REL037060", 
    "alt_label": []
  }, 
  "Fiction / Romance / Suspense": {
    "related": [], 
    "pref_label": "Fiction / Romance / Suspense", 
    "notation": "FIC027110", 
    "alt_label": []
  }, 
  "Games / Card Games / Solitaire": {
    "related": [], 
    "pref_label": "Games / Card Games / Solitaire", 
    "notation": "GAM002020", 
    "alt_label": []
  }, 
  "Medical / Practice Management & Reimbursement": {
    "related": [], 
    "pref_label": "Medical / Practice Management & Reimbursement", 
    "notation": "MED095000", 
    "alt_label": [
      "Medical / Reimbursement"
    ]
  }, 
  "Music / Genres & Styles / Heavy Metal": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Heavy Metal", 
    "notation": "MUS019000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Self-mutilation": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Self-mutilation", 
    "notation": "JNF053250", 
    "alt_label": []
  }, 
  "Political Science / Political Process / General": {
    "related": [], 
    "pref_label": "Political Science / Political Process / General", 
    "notation": "POL016000", 
    "alt_label": []
  }, 
  "Business & Economics / Marketing / Research": {
    "related": [], 
    "pref_label": "Business & Economics / Marketing / Research", 
    "notation": "BUS043060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Physical Impairments": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Physical Impairments", 
    "notation": "JNF024070", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Dreams": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Dreams", 
    "notation": "OCC006000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Adolescence": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Adolescence", 
    "notation": "JNF053010", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / General": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / General", 
    "notation": "MUS049000", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Adventure": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Adventure", 
    "notation": "TRV001000", 
    "alt_label": [
      "Travel / Adventure"
    ]
  }, 
  "Juvenile Fiction / Sports & Recreation / Football": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Football", 
    "notation": "JUV032030", 
    "alt_label": []
  }, 
  "Science / Astronomy": {
    "related": [], 
    "pref_label": "Science / Astronomy", 
    "notation": "SCI004000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Learning Concepts": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Learning Concepts", 
    "notation": "JNF049260", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Sports": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Sports", 
    "notation": "TRV026080", 
    "alt_label": []
  }, 
  "Technology & Engineering / Chemical & Biochemical": {
    "related": [], 
    "pref_label": "Technology & Engineering / Chemical & Biochemical", 
    "notation": "TEC009010", 
    "alt_label": []
  }, 
  "Fiction / Family Life": {
    "related": [], 
    "pref_label": "Fiction / Family Life", 
    "notation": "FIC045000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Ethics": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Ethics", 
    "notation": "REL067070", 
    "alt_label": []
  }, 
  "Study Aids / Mat (miller Analogies Test)": {
    "related": [], 
    "pref_label": "Study Aids / Mat (miller Analogies Test)", 
    "notation": "STU018000", 
    "alt_label": []
  }, 
  "Business & Economics / Real Estate / Mortgages": {
    "related": [], 
    "pref_label": "Business & Economics / Real Estate / Mortgages", 
    "notation": "BUS054030", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Lawyers & Judges": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Lawyers & Judges", 
    "notation": "BIO020000", 
    "alt_label": [
      "Biography & Autobiography / Judges"
    ]
  }, 
  "Architecture / History / General": {
    "related": [], 
    "pref_label": "Architecture / History / General", 
    "notation": "ARC005000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Horses": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Horses", 
    "notation": "JUV002130", 
    "alt_label": []
  }, 
  "Study Aids / Graduate School Guides": {
    "related": [], 
    "pref_label": "Study Aids / Graduate School Guides", 
    "notation": "STU015000", 
    "alt_label": []
  }, 
  "Religion / Biblical Criticism & Interpretation / General": {
    "related": [], 
    "pref_label": "Religion / Biblical Criticism & Interpretation / General", 
    "notation": "REL006080", 
    "alt_label": []
  }, 
  "Technology & Engineering / Electronics / Optoelectronics": {
    "related": [], 
    "pref_label": "Technology & Engineering / Electronics / Optoelectronics", 
    "notation": "TEC008080", 
    "alt_label": []
  }, 
  "Nature / Reference": {
    "related": [], 
    "pref_label": "Nature / Reference", 
    "notation": "NAT027000", 
    "alt_label": []
  }, 
  "Bibles / God's Word / Study": {
    "related": [], 
    "pref_label": "Bibles / God's Word / Study", 
    "notation": "BIB004050", 
    "alt_label": []
  }, 
  "Bibles / La Biblia De Las Americas / Reference": {
    "related": [], 
    "pref_label": "Bibles / La Biblia De Las Americas / Reference", 
    "notation": "BIB007040", 
    "alt_label": []
  }, 
  "House & Home / Design & Construction": {
    "related": [], 
    "pref_label": "House & Home / Design & Construction", 
    "notation": "HOM004000", 
    "alt_label": []
  }, 
  "Nature / Animals / General": {
    "related": [], 
    "pref_label": "Nature / Animals / General", 
    "notation": "NAT001000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Lifestyles / City & Town Life": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Lifestyles / City & Town Life", 
    "notation": "JNF031000", 
    "alt_label": [
      "Juvenile Nonfiction / City Life", 
      "Juvenile Nonfiction / Town Life"
    ]
  }, 
  "Psychology / Personality": {
    "related": [], 
    "pref_label": "Psychology / Personality", 
    "notation": "PSY023000", 
    "alt_label": []
  }, 
  "Science / Earth Sciences / Meteorology & Climatology": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / Meteorology & Climatology", 
    "notation": "SCI042000", 
    "alt_label": []
  }, 
  "Medical / Nutrition": {
    "related": [], 
    "pref_label": "Medical / Nutrition", 
    "notation": "MED060000", 
    "alt_label": [
      "Medical / Diseases / Nutritional"
    ]
  }, 
  "Computers / Programming Languages / C": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / C", 
    "notation": "COM051060", 
    "alt_label": []
  }, 
  "History / Polar Regions": {
    "related": [], 
    "pref_label": "History / Polar Regions", 
    "notation": "HIS046000", 
    "alt_label": []
  }, 
  "Art / General": {
    "related": [], 
    "pref_label": "Art / General", 
    "notation": "ART000000", 
    "alt_label": []
  }, 
  "Education / Counseling / Academic Development": {
    "related": [], 
    "pref_label": "Education / Counseling / Academic Development", 
    "notation": "EDU014000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Canada / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Canada / General", 
    "notation": "JUV016160", 
    "alt_label": []
  }, 
  "Study Aids / Psat & Nmsqt (national Merit Scholarship Qualifying Test)": {
    "related": [], 
    "pref_label": "Study Aids / Psat & Nmsqt (national Merit Scholarship Qualifying Test)", 
    "notation": "STU033000", 
    "alt_label": []
  }, 
  "Medical / Nursing / Assessment & Diagnosis": {
    "related": [], 
    "pref_label": "Medical / Nursing / Assessment & Diagnosis", 
    "notation": "MED058020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Interactive Adventures": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Interactive Adventures", 
    "notation": "JUV020000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Mathematics / Advanced": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Mathematics / Advanced", 
    "notation": "JNF035010", 
    "alt_label": []
  }, 
  "Medical / Biochemistry": {
    "related": [], 
    "pref_label": "Medical / Biochemistry", 
    "notation": "MED008000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Coaching / Baseball": {
    "related": [], 
    "pref_label": "Sports & Recreation / Coaching / Baseball", 
    "notation": "SPO003010", 
    "alt_label": []
  }, 
  "Literary Criticism / Australian & Oceanian": {
    "related": [], 
    "pref_label": "Literary Criticism / Australian & Oceanian", 
    "notation": "LIT004070", 
    "alt_label": [
      "Literary Criticism / Oceanian"
    ]
  }, 
  "Family & Relationships / Activities": {
    "related": [], 
    "pref_label": "Family & Relationships / Activities", 
    "notation": "FAM002000", 
    "alt_label": []
  }, 
  "Law / Commercial / General": {
    "related": [], 
    "pref_label": "Law / Commercial / General", 
    "notation": "LAW014000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Mice, Hamsters, Guinea Pigs, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Mice, Hamsters, Guinea Pigs, Etc.", 
    "notation": "JUV002180", 
    "alt_label": []
  }, 
  "Sports & Recreation / Olympics": {
    "related": [], 
    "pref_label": "Sports & Recreation / Olympics", 
    "notation": "SPO058000", 
    "alt_label": []
  }, 
  "Self-help / Neuro-linguistic Programming (nlp)": {
    "related": [], 
    "pref_label": "Self-help / Neuro-linguistic Programming (nlp)", 
    "notation": "SEL037000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / Mexico": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Mexico", 
    "notation": "JUV030100", 
    "alt_label": []
  }, 
  "Bibles / New American Standard Bible / General": {
    "related": [], 
    "pref_label": "Bibles / New American Standard Bible / General", 
    "notation": "BIB010000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Computers / Internet": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Computers / Internet", 
    "notation": "JNF012030", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Japanese": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Japanese", 
    "notation": "CKB048000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / French": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / French", 
    "notation": "CKB034000", 
    "alt_label": []
  }, 
  "Social Science / Poverty & Homelessness": {
    "related": [], 
    "pref_label": "Social Science / Poverty & Homelessness", 
    "notation": "SOC045000", 
    "alt_label": []
  }, 
  "Self-help / Dreams": {
    "related": [], 
    "pref_label": "Self-help / Dreams", 
    "notation": "SEL012000", 
    "alt_label": []
  }, 
  "Religion / Judaism / Sacred Writings": {
    "related": [], 
    "pref_label": "Religion / Judaism / Sacred Writings", 
    "notation": "REL040040", 
    "alt_label": []
  }, 
  "Sports & Recreation / Coaching / Football": {
    "related": [], 
    "pref_label": "Sports & Recreation / Coaching / Football", 
    "notation": "SPO061020", 
    "alt_label": []
  }, 
  "Performing Arts / Film & Video / Reference": {
    "related": [], 
    "pref_label": "Performing Arts / Film & Video / Reference", 
    "notation": "PER004040", 
    "alt_label": []
  }, 
  "Computers / Hardware / Personal Computers / Macintosh": {
    "related": [], 
    "pref_label": "Computers / Hardware / Personal Computers / Macintosh", 
    "notation": "COM050020", 
    "alt_label": []
  }, 
  "Religion / Christian Ministry / General": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / General", 
    "notation": "REL109000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Mathematics / Fractions": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Mathematics / Fractions", 
    "notation": "JNF035040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Boys & Men": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Boys & Men", 
    "notation": "JNF009000", 
    "alt_label": [
      "Juvenile Nonfiction / Men"
    ]
  }, 
  "Fiction / African American / Romance": {
    "related": [], 
    "pref_label": "Fiction / African American / Romance", 
    "notation": "FIC049060", 
    "alt_label": []
  }, 
  "Religion / Islam / Shi'a": {
    "related": [], 
    "pref_label": "Religion / Islam / Shi'a", 
    "notation": "REL037040", 
    "alt_label": []
  }, 
  "Computers / Desktop Applications / Project Management Software": {
    "related": [], 
    "pref_label": "Computers / Desktop Applications / Project Management Software", 
    "notation": "COM081000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Diet & Nutrition": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Diet & Nutrition", 
    "notation": "JNF024010", 
    "alt_label": []
  }, 
  "Religion / Prayerbooks / General": {
    "related": [], 
    "pref_label": "Religion / Prayerbooks / General", 
    "notation": "REL052000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / United States / Other": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / United States / Other", 
    "notation": "JUV011050", 
    "alt_label": []
  }, 
  "Sports & Recreation / Reference": {
    "related": [], 
    "pref_label": "Sports & Recreation / Reference", 
    "notation": "SPO033000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Fossils": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Fossils", 
    "notation": "JNF037050", 
    "alt_label": []
  }, 
  "Law / Property": {
    "related": [], 
    "pref_label": "Law / Property", 
    "notation": "LAW074000", 
    "alt_label": []
  }, 
  "Law / Natural Law": {
    "related": [], 
    "pref_label": "Law / Natural Law", 
    "notation": "LAW069000", 
    "alt_label": []
  }, 
  "Performing Arts / Theater / Playwriting": {
    "related": [], 
    "pref_label": "Performing Arts / Theater / Playwriting", 
    "notation": "PER011030", 
    "alt_label": []
  }, 
  "Architecture / Annuals": {
    "related": [], 
    "pref_label": "Architecture / Annuals", 
    "notation": "ARC023000", 
    "alt_label": []
  }, 
  "Political Science / Political Process / Political Parties": {
    "related": [], 
    "pref_label": "Political Science / Political Process / Political Parties", 
    "notation": "POL015000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Asia": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Asia", 
    "notation": "JNF038020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Strangers": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Strangers", 
    "notation": "JUV039270", 
    "alt_label": []
  }, 
  "Business & Economics / Secretarial Aids & Training": {
    "related": [], 
    "pref_label": "Business & Economics / Secretarial Aids & Training", 
    "notation": "BUS089000", 
    "alt_label": []
  }, 
  "Computers / Hardware / Personal Computers / General": {
    "related": [], 
    "pref_label": "Computers / Hardware / Personal Computers / General", 
    "notation": "COM050000", 
    "alt_label": []
  }, 
  "Education / Educational Policy & Reform / Charter Schools": {
    "related": [], 
    "pref_label": "Education / Educational Policy & Reform / Charter Schools", 
    "notation": "EDU034020", 
    "alt_label": []
  }, 
  "Drama / Asian / Japanese": {
    "related": [], 
    "pref_label": "Drama / Asian / Japanese", 
    "notation": "DRA005010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Family / Multigenerational": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Family / Multigenerational", 
    "notation": "JUV013030", 
    "alt_label": []
  }, 
  "Foreign Language Study / Multi-language Dictionaries": {
    "related": [], 
    "pref_label": "Foreign Language Study / Multi-language Dictionaries", 
    "notation": "FOR005000", 
    "alt_label": []
  }, 
  "Bibles / English Standard Version / General": {
    "related": [], 
    "pref_label": "Bibles / English Standard Version / General", 
    "notation": "BIB003000", 
    "alt_label": []
  }, 
  "History / Africa / West": {
    "related": [], 
    "pref_label": "History / Africa / West", 
    "notation": "HIS001050", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Technology / Agriculture": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Technology / Agriculture", 
    "notation": "JNF051020", 
    "alt_label": []
  }, 
  "Technology & Engineering / Tribology": {
    "related": [], 
    "pref_label": "Technology & Engineering / Tribology", 
    "notation": "TEC068000", 
    "alt_label": []
  }, 
  "Computers / Social Aspects / Human-computer Interaction": {
    "related": [], 
    "pref_label": "Computers / Social Aspects / Human-computer Interaction", 
    "notation": "COM079010", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Php": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Php", 
    "notation": "COM051400", 
    "alt_label": []
  }, 
  "History / Europe / Western": {
    "related": [], 
    "pref_label": "History / Europe / Western", 
    "notation": "HIS010020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Learning Concepts": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Learning Concepts", 
    "notation": "JUV033170", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Authorship": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Authorship", 
    "notation": "LAN002000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Zoos": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Zoos", 
    "notation": "JNF003200", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Zoology / Ornithology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Zoology / Ornithology", 
    "notation": "SCI070040", 
    "alt_label": []
  }, 
  "Literary Criticism / Russian & Former Soviet Union": {
    "related": [], 
    "pref_label": "Literary Criticism / Russian & Former Soviet Union", 
    "notation": "LIT004240", 
    "alt_label": []
  }, 
  "Travel / South America / Chile & Easter Island": {
    "related": [], 
    "pref_label": "Travel / South America / Chile & Easter Island", 
    "notation": "TRV024030", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Hanukkah": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Hanukkah", 
    "notation": "JUV017110", 
    "alt_label": []
  }, 
  "Computers / Logic Design": {
    "related": [], 
    "pref_label": "Computers / Logic Design", 
    "notation": "COM036000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Criminals & Outlaws": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Criminals & Outlaws", 
    "notation": "BIO024000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Health & Daily Living": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Health & Daily Living", 
    "notation": "JUV033130", 
    "alt_label": []
  }, 
  "Political Science / Comparative Politics": {
    "related": [], 
    "pref_label": "Political Science / Comparative Politics", 
    "notation": "POL009000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Lifestyles / City & Town Life": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Lifestyles / City & Town Life", 
    "notation": "JUV023000", 
    "alt_label": [
      "Juvenile Fiction / City Life", 
      "Juvenile Fiction / Town Life"
    ]
  }, 
  "Antiques & Collectibles / Furniture": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Furniture", 
    "notation": "ANT017000", 
    "alt_label": []
  }, 
  "Computers / Software Development & Engineering / Tools": {
    "related": [], 
    "pref_label": "Computers / Software Development & Engineering / Tools", 
    "notation": "COM051440", 
    "alt_label": []
  }, 
  "Design / History & Criticism": {
    "related": [], 
    "pref_label": "Design / History & Criticism", 
    "notation": "DES008000", 
    "alt_label": []
  }, 
  "Medical / Preventive Medicine": {
    "related": [], 
    "pref_label": "Medical / Preventive Medicine", 
    "notation": "MED076000", 
    "alt_label": []
  }, 
  "Art / Subjects & Themes / Religious": {
    "related": [], 
    "pref_label": "Art / Subjects & Themes / Religious", 
    "notation": "ART035000", 
    "alt_label": []
  }, 
  "Philosophy / Movements / General": {
    "related": [], 
    "pref_label": "Philosophy / Movements / General", 
    "notation": "PHI031000", 
    "alt_label": []
  }, 
  "Design / Decorative Arts": {
    "related": [], 
    "pref_label": "Design / Decorative Arts", 
    "notation": "DES003000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Public Speaking": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Public Speaking", 
    "notation": "LAN026000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / General", 
    "notation": "JUV032000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Scandinavian Languages (other)": {
    "related": [], 
    "pref_label": "Foreign Language Study / Scandinavian Languages (other)", 
    "notation": "FOR022000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Wrestling": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Wrestling", 
    "notation": "JNF054220", 
    "alt_label": []
  }, 
  "Study Aids / Vocational": {
    "related": [], 
    "pref_label": "Study Aids / Vocational", 
    "notation": "STU029000", 
    "alt_label": []
  }, 
  "Self-help / Substance Abuse & Addictions / Drug Dependence": {
    "related": [], 
    "pref_label": "Self-help / Substance Abuse & Addictions / Drug Dependence", 
    "notation": "SEL013000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Zoology / Invertebrates": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Zoology / Invertebrates", 
    "notation": "SCI070020", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Pasta": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Pasta", 
    "notation": "CKB061000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Food Science": {
    "related": [], 
    "pref_label": "Technology & Engineering / Food Science", 
    "notation": "TEC012000", 
    "alt_label": []
  }, 
  "Travel / Africa / Republic Of South Africa": {
    "related": [], 
    "pref_label": "Travel / Africa / Republic Of South Africa", 
    "notation": "TRV002060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Philosophy": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Philosophy", 
    "notation": "JNF040000", 
    "alt_label": []
  }, 
  "Business & Economics / Office Equipment & Supplies": {
    "related": [], 
    "pref_label": "Business & Economics / Office Equipment & Supplies", 
    "notation": "BUS095000", 
    "alt_label": []
  }, 
  "Art / Techniques / Painting": {
    "related": [], 
    "pref_label": "Art / Techniques / Painting", 
    "notation": "ART020000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / General", 
    "notation": "JNF054000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Sexual Abuse": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Sexual Abuse", 
    "notation": "JNF053170", 
    "alt_label": [
      "Juvenile Nonfiction / Family / Abuse", 
      "Juvenile Nonfiction / Social Issues / Abuse"
    ]
  }, 
  "Medical / Surgery / Plastic & Cosmetic": {
    "related": [], 
    "pref_label": "Medical / Surgery / Plastic & Cosmetic", 
    "notation": "MED085030", 
    "alt_label": [
      "Medical / Cosmetic Surgery", 
      "Medical / Plastic Surgery"
    ]
  }, 
  "Juvenile Nonfiction / Animals / Birds": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Birds", 
    "notation": "JNF003030", 
    "alt_label": []
  }, 
  "Fiction / Dystopian": {
    "related": [], 
    "pref_label": "Fiction / Dystopian", 
    "notation": "FIC055000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Miscellaneous": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Miscellaneous", 
    "notation": "JNF054090", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Performing Arts / Film": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Performing Arts / Film", 
    "notation": "JUV031030", 
    "alt_label": []
  }, 
  "Games / Board": {
    "related": [], 
    "pref_label": "Games / Board", 
    "notation": "GAM001000", 
    "alt_label": []
  }, 
  "Art / Techniques / Calligraphy": {
    "related": [], 
    "pref_label": "Art / Techniques / Calligraphy", 
    "notation": "ART003000", 
    "alt_label": []
  }, 
  "Bibles / Contemporary English Version / Study": {
    "related": [], 
    "pref_label": "Bibles / Contemporary English Version / Study", 
    "notation": "BIB002050", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Legends, Myths, Fables / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Legends, Myths, Fables / General", 
    "notation": "JUV022000", 
    "alt_label": []
  }, 
  "Philosophy / History & Surveys / Ancient & Classical": {
    "related": [], 
    "pref_label": "Philosophy / History & Surveys / Ancient & Classical", 
    "notation": "PHI002000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Cycling": {
    "related": [], 
    "pref_label": "Sports & Recreation / Cycling", 
    "notation": "SPO011000", 
    "alt_label": []
  }, 
  "Travel / Africa / General": {
    "related": [], 
    "pref_label": "Travel / Africa / General", 
    "notation": "TRV002000", 
    "alt_label": []
  }, 
  "Cooking / Beverages / Coffee & Tea": {
    "related": [], 
    "pref_label": "Cooking / Beverages / Coffee & Tea", 
    "notation": "CKB019000", 
    "alt_label": []
  }, 
  "Games / Quizzes": {
    "related": [], 
    "pref_label": "Games / Quizzes", 
    "notation": "GAM008000", 
    "alt_label": []
  }, 
  "Medical / Sports Medicine": {
    "related": [], 
    "pref_label": "Medical / Sports Medicine", 
    "notation": "MED084000", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Existentialism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Existentialism", 
    "notation": "PHI006000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Ecology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Ecology", 
    "notation": "SCI020000", 
    "alt_label": []
  }, 
  "Reference / Consumer Guides": {
    "related": [], 
    "pref_label": "Reference / Consumer Guides", 
    "notation": "REF030000", 
    "alt_label": []
  }, 
  "Architecture / Methods & Materials": {
    "related": [], 
    "pref_label": "Architecture / Methods & Materials", 
    "notation": "ARC009000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / American / General": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / American / General", 
    "notation": "CKB002000", 
    "alt_label": []
  }, 
  "Bibles / New Living Translation / Children": {
    "related": [], 
    "pref_label": "Bibles / New Living Translation / Children", 
    "notation": "BIB015010", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Literary": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Literary", 
    "notation": "TRV026090", 
    "alt_label": []
  }, 
  "Bibles / English Standard Version / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / English Standard Version / Youth & Teen", 
    "notation": "BIB003070", 
    "alt_label": []
  }, 
  "Fiction / Mystery & Detective / Short Stories": {
    "related": [], 
    "pref_label": "Fiction / Mystery & Detective / Short Stories", 
    "notation": "FIC022050", 
    "alt_label": []
  }, 
  "Fiction / Mystery & Detective / General": {
    "related": [], 
    "pref_label": "Fiction / Mystery & Detective / General", 
    "notation": "FIC022000", 
    "alt_label": []
  }, 
  "Humor / Form / Anecdotes & Quotations": {
    "related": [], 
    "pref_label": "Humor / Form / Anecdotes & Quotations", 
    "notation": "HUM015000", 
    "alt_label": []
  }, 
  "Photography / Reference": {
    "related": [], 
    "pref_label": "Photography / Reference", 
    "notation": "PHO017000", 
    "alt_label": []
  }, 
  "Medical / Acupuncture": {
    "related": [], 
    "pref_label": "Medical / Acupuncture", 
    "notation": "MED001000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Neuroscience": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Neuroscience", 
    "notation": "SCI089000", 
    "alt_label": []
  }, 
  "Music / Religious / Gospel": {
    "related": [], 
    "pref_label": "Music / Religious / Gospel", 
    "notation": "MUS018000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Mariology": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Mariology", 
    "notation": "REL104000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Camping": {
    "related": [], 
    "pref_label": "Sports & Recreation / Camping", 
    "notation": "SPO009000", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Depression": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Depression", 
    "notation": "PSY049000", 
    "alt_label": []
  }, 
  "Art / History / General": {
    "related": [], 
    "pref_label": "Art / History / General", 
    "notation": "ART015000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Social Scientists & Psychologists": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Social Scientists & Psychologists", 
    "notation": "BIO021000", 
    "alt_label": [
      "Biography & Autobiography / Psychologists"
    ]
  }, 
  "Cooking / Seasonal": {
    "related": [], 
    "pref_label": "Cooking / Seasonal", 
    "notation": "CKB077000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Ice Skating": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Ice Skating", 
    "notation": "JNF054190", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Leatherwork": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Leatherwork", 
    "notation": "CRA050000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Wine": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Wine", 
    "notation": "ANT051000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Fishing": {
    "related": [], 
    "pref_label": "Sports & Recreation / Fishing", 
    "notation": "SPO014000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Essays": {
    "related": [], 
    "pref_label": "Sports & Recreation / Essays", 
    "notation": "SPO012000", 
    "alt_label": []
  }, 
  "Business & Economics / Accounting / Governmental": {
    "related": [], 
    "pref_label": "Business & Economics / Accounting / Governmental", 
    "notation": "BUS001020", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Feng Shui": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Feng Shui", 
    "notation": "OCC037000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Civil / Transport": {
    "related": [], 
    "pref_label": "Technology & Engineering / Civil / Transport", 
    "notation": "TEC009160", 
    "alt_label": []
  }, 
  "Design / Textile & Costume": {
    "related": [], 
    "pref_label": "Design / Textile & Costume", 
    "notation": "DES013000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Royalty": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Royalty", 
    "notation": "BIO014000", 
    "alt_label": []
  }, 
  "Nature / Birdwatching Guides": {
    "related": [], 
    "pref_label": "Nature / Birdwatching Guides", 
    "notation": "NAT004000", 
    "alt_label": []
  }, 
  "Self-help / General": {
    "related": [], 
    "pref_label": "Self-help / General", 
    "notation": "SEL000000", 
    "alt_label": []
  }, 
  "Bibles / New American Standard Bible / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / New American Standard Bible / New Testament & Portions", 
    "notation": "BIB010030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Lifestyles / Farm & Ranch Life": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Lifestyles / Farm & Ranch Life", 
    "notation": "JNF033000", 
    "alt_label": [
      "Juvenile Nonfiction / Farm Life"
    ]
  }, 
  "Technology & Engineering / Emergency Management": {
    "related": [], 
    "pref_label": "Technology & Engineering / Emergency Management", 
    "notation": "TEC065000", 
    "alt_label": []
  }, 
  "History / Military / Iraq War (2003-)": {
    "related": [], 
    "pref_label": "History / Military / Iraq War (2003-)", 
    "notation": "HIS027170", 
    "alt_label": []
  }, 
  "Political Science / Public Policy / Regional Planning": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Regional Planning", 
    "notation": "POL026000", 
    "alt_label": []
  }, 
  "History / Middle East / Israel": {
    "related": [], 
    "pref_label": "History / Middle East / Israel", 
    "notation": "HIS019000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / General", 
    "notation": "JNF025000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / General": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / General", 
    "notation": "ANT000000", 
    "alt_label": []
  }, 
  "Law / General": {
    "related": [], 
    "pref_label": "Law / General", 
    "notation": "LAW000000", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Spiritual Growth": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Spiritual Growth", 
    "notation": "REL012120", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Short Stories": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Short Stories", 
    "notation": "JUV038000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Environmental Science & Ecosystems": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Environmental Science & Ecosystems", 
    "notation": "JNF051100", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Smalltalk": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Smalltalk", 
    "notation": "COM051160", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Anthropology": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Anthropology", 
    "notation": "REL067020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Seasons": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Seasons", 
    "notation": "JUV009100", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / First Aid": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / First Aid", 
    "notation": "JNF024030", 
    "alt_label": []
  }, 
  "Travel / Road Travel": {
    "related": [], 
    "pref_label": "Travel / Road Travel", 
    "notation": "TRV031000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Counting & Numbers": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Counting & Numbers", 
    "notation": "JNF013030", 
    "alt_label": [
      "Juvenile Nonfiction / Counting & Numbers"
    ]
  }, 
  "Business & Economics / Taxation / General": {
    "related": [], 
    "pref_label": "Business & Economics / Taxation / General", 
    "notation": "BUS064000", 
    "alt_label": []
  }, 
  "Computers / Educational Software": {
    "related": [], 
    "pref_label": "Computers / Educational Software", 
    "notation": "COM023000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Islam": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Islam", 
    "notation": "JNF049100", 
    "alt_label": []
  }, 
  "Health & Fitness / Safety": {
    "related": [], 
    "pref_label": "Health & Fitness / Safety", 
    "notation": "HEA021000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Religious": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Religious", 
    "notation": "CGN004220", 
    "alt_label": []
  }, 
  "Design / Graphic Arts / Illustration": {
    "related": [], 
    "pref_label": "Design / Graphic Arts / Illustration", 
    "notation": "DES007040", 
    "alt_label": []
  }, 
  "Sports & Recreation / Motor Sports": {
    "related": [], 
    "pref_label": "Sports & Recreation / Motor Sports", 
    "notation": "SPO028000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Healing / Energy (qigong, Reiki, Polarity)": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Healing / Energy (qigong, Reiki, Polarity)", 
    "notation": "OCC011010", 
    "alt_label": []
  }, 
  "Bibles / International Children's Bible / General": {
    "related": [], 
    "pref_label": "Bibles / International Children's Bible / General", 
    "notation": "BIB005000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Music / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / General", 
    "notation": "JNF036000", 
    "alt_label": []
  }, 
  "Medical / Anesthesiology": {
    "related": [], 
    "pref_label": "Medical / Anesthesiology", 
    "notation": "MED006000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Folk & Traditional": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Folk & Traditional", 
    "notation": "MUS017000", 
    "alt_label": []
  }, 
  "Religion / Christianity / History": {
    "related": [], 
    "pref_label": "Religion / Christianity / History", 
    "notation": "REL015000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Punk": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Punk", 
    "notation": "MUS030000", 
    "alt_label": []
  }, 
  "Medical / Critical Care": {
    "related": [], 
    "pref_label": "Medical / Critical Care", 
    "notation": "MED015000", 
    "alt_label": []
  }, 
  "Architecture / Buildings / Public, Commercial & Industrial": {
    "related": [], 
    "pref_label": "Architecture / Buildings / Public, Commercial & Industrial", 
    "notation": "ARC011000", 
    "alt_label": []
  }, 
  "Business & Economics / Knowledge Capital": {
    "related": [], 
    "pref_label": "Business & Economics / Knowledge Capital", 
    "notation": "BUS098000", 
    "alt_label": []
  }, 
  "History / Africa / Central": {
    "related": [], 
    "pref_label": "History / Africa / Central", 
    "notation": "HIS001010", 
    "alt_label": []
  }, 
  "Travel / Caribbean & West Indies": {
    "related": [], 
    "pref_label": "Travel / Caribbean & West Indies", 
    "notation": "TRV007000", 
    "alt_label": [
      "Travel / West Indies"
    ]
  }, 
  "Games / Reference": {
    "related": [], 
    "pref_label": "Games / Reference", 
    "notation": "GAM009000", 
    "alt_label": []
  }, 
  "Religion / Meditations": {
    "related": [], 
    "pref_label": "Religion / Meditations", 
    "notation": "REL042000", 
    "alt_label": []
  }, 
  "Law / Natural Resources": {
    "related": [], 
    "pref_label": "Law / Natural Resources", 
    "notation": "LAW070000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Foreign Language Study / French": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Foreign Language Study / French", 
    "notation": "JNF020020", 
    "alt_label": []
  }, 
  "History / Asia / China": {
    "related": [], 
    "pref_label": "History / Asia / China", 
    "notation": "HIS008000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Construction / Contracting": {
    "related": [], 
    "pref_label": "Technology & Engineering / Construction / Contracting", 
    "notation": "TEC005020", 
    "alt_label": []
  }, 
  "Computers / Hardware / Personal Computers / Pcs": {
    "related": [], 
    "pref_label": "Computers / Hardware / Personal Computers / Pcs", 
    "notation": "COM050010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Readers / Beginner": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Readers / Beginner", 
    "notation": "JUV043000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Suicide": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Suicide", 
    "notation": "JNF053190", 
    "alt_label": []
  }, 
  "Business & Economics / Commercial Policy": {
    "related": [], 
    "pref_label": "Business & Economics / Commercial Policy", 
    "notation": "BUS013000", 
    "alt_label": []
  }, 
  "Mathematics / Game Theory": {
    "related": [], 
    "pref_label": "Mathematics / Game Theory", 
    "notation": "MAT011000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Zoology": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Zoology", 
    "notation": "JNF051150", 
    "alt_label": []
  }, 
  "Sports & Recreation / Coaching / Basketball": {
    "related": [], 
    "pref_label": "Sports & Recreation / Coaching / Basketball", 
    "notation": "SPO061010", 
    "alt_label": []
  }, 
  "Literary Collections / Diaries & Journals": {
    "related": [], 
    "pref_label": "Literary Collections / Diaries & Journals", 
    "notation": "LCO015000", 
    "alt_label": []
  }, 
  "Study Aids / Professional": {
    "related": [], 
    "pref_label": "Study Aids / Professional", 
    "notation": "STU021000", 
    "alt_label": []
  }, 
  "Health & Fitness / Food Content Guides": {
    "related": [], 
    "pref_label": "Health & Fitness / Food Content Guides", 
    "notation": "HEA034000", 
    "alt_label": [
      "Health & Fitness / Calorie-content Guides", 
      "Health & Fitness / Cholesterol-content Guides", 
      "Health & Fitness / Fat-content Guides"
    ]
  }, 
  "Science / Life Sciences / Botany": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Botany", 
    "notation": "SCI011000", 
    "alt_label": []
  }, 
  "Medical / Nursing / Nurse & Patient": {
    "related": [], 
    "pref_label": "Medical / Nursing / Nurse & Patient", 
    "notation": "MED058140", 
    "alt_label": []
  }, 
  "Poetry / Subjects & Themes / General": {
    "related": [], 
    "pref_label": "Poetry / Subjects & Themes / General", 
    "notation": "POE023000", 
    "alt_label": []
  }, 
  "Medical / Essays": {
    "related": [], 
    "pref_label": "Medical / Essays", 
    "notation": "MED109000", 
    "alt_label": []
  }, 
  "History / Social History": {
    "related": [], 
    "pref_label": "History / Social History", 
    "notation": "HIS054000", 
    "alt_label": []
  }, 
  "Poetry / Women Authors": {
    "related": [], 
    "pref_label": "Poetry / Women Authors", 
    "notation": "POE024000", 
    "alt_label": []
  }, 
  "Mathematics / Differential Equations / Partial": {
    "related": [], 
    "pref_label": "Mathematics / Differential Equations / Partial", 
    "notation": "MAT007020", 
    "alt_label": []
  }, 
  "Computers / Networking / Vendor Specific": {
    "related": [], 
    "pref_label": "Computers / Networking / Vendor Specific", 
    "notation": "COM043060", 
    "alt_label": []
  }, 
  "History / Europe / Scandinavia": {
    "related": [], 
    "pref_label": "History / Europe / Scandinavia", 
    "notation": "HIS044000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Transportation / Boats, Ships & Underwater Craft": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Transportation / Boats, Ships & Underwater Craft", 
    "notation": "JUV041020", 
    "alt_label": []
  }, 
  "Science / Spectroscopy & Spectrum Analysis": {
    "related": [], 
    "pref_label": "Science / Spectroscopy & Spectrum Analysis", 
    "notation": "SCI078000", 
    "alt_label": []
  }, 
  "Mathematics / Differential Equations / Ordinary": {
    "related": [], 
    "pref_label": "Mathematics / Differential Equations / Ordinary", 
    "notation": "MAT007010", 
    "alt_label": []
  }, 
  "Medical / Nursing / Home & Community Care": {
    "related": [], 
    "pref_label": "Medical / Nursing / Home & Community Care", 
    "notation": "MED058070", 
    "alt_label": []
  }, 
  "Law / Privacy": {
    "related": [], 
    "pref_label": "Law / Privacy", 
    "notation": "LAW116000", 
    "alt_label": []
  }, 
  "Law / Science & Technology": {
    "related": [], 
    "pref_label": "Law / Science & Technology", 
    "notation": "LAW099000", 
    "alt_label": [
      "Law / Technology"
    ]
  }, 
  "Poetry / Asian / Chinese": {
    "related": [], 
    "pref_label": "Poetry / Asian / Chinese", 
    "notation": "POE009010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Mice, Hamsters, Guinea Pigs, Squirrels, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Mice, Hamsters, Guinea Pigs, Squirrels, Etc.", 
    "notation": "JNF003160", 
    "alt_label": []
  }, 
  "Mathematics / Probability & Statistics / Regression Analysis": {
    "related": [], 
    "pref_label": "Mathematics / Probability & Statistics / Regression Analysis", 
    "notation": "MAT029030", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Historical": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Historical", 
    "notation": "PHO023100", 
    "alt_label": []
  }, 
  "Gardening / Regional / Canada": {
    "related": [], 
    "pref_label": "Gardening / Regional / Canada", 
    "notation": "GAR019010", 
    "alt_label": []
  }, 
  "Performing Arts / Television / Direction & Production": {
    "related": [], 
    "pref_label": "Performing Arts / Television / Direction & Production", 
    "notation": "PER010010", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / General": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / General", 
    "notation": "CKB101000", 
    "alt_label": []
  }, 
  "Psychology / History": {
    "related": [], 
    "pref_label": "Psychology / History", 
    "notation": "PSY015000", 
    "alt_label": []
  }, 
  "Law / Family Law / Children": {
    "related": [], 
    "pref_label": "Law / Family Law / Children", 
    "notation": "LAW038010", 
    "alt_label": [
      "Law / Children"
    ]
  }, 
  "Juvenile Fiction / Dystopian": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Dystopian", 
    "notation": "JUV059000", 
    "alt_label": []
  }, 
  "Fiction / Technological": {
    "related": [], 
    "pref_label": "Fiction / Technological", 
    "notation": "FIC036000", 
    "alt_label": []
  }, 
  "Education / Administration / Higher": {
    "related": [], 
    "pref_label": "Education / Administration / Higher", 
    "notation": "EDU001030", 
    "alt_label": []
  }, 
  "Drama / Women Authors": {
    "related": [], 
    "pref_label": "Drama / Women Authors", 
    "notation": "DRA019000", 
    "alt_label": []
  }, 
  "Travel / United States / Midwest / West North Central (ia, Ks, Mn, Mo, Nd, Ne, Sd)": {
    "related": [], 
    "pref_label": "Travel / United States / Midwest / West North Central (ia, Ks, Mn, Mo, Nd, Ne, Sd)", 
    "notation": "TRV025030", 
    "alt_label": []
  }, 
  "Computers / Networking / Local Area Networks (lans)": {
    "related": [], 
    "pref_label": "Computers / Networking / Local Area Networks (lans)", 
    "notation": "COM043020", 
    "alt_label": []
  }, 
  "Computers / Operating Systems / Macintosh": {
    "related": [], 
    "pref_label": "Computers / Operating Systems / Macintosh", 
    "notation": "COM046020", 
    "alt_label": []
  }, 
  "Drama / American / African American": {
    "related": [], 
    "pref_label": "Drama / American / African American", 
    "notation": "DRA001010", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Witchcraft & Wicca": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Witchcraft & Wicca", 
    "notation": "OCC026000", 
    "alt_label": []
  }, 
  "Mathematics / Topology": {
    "related": [], 
    "pref_label": "Mathematics / Topology", 
    "notation": "MAT038000", 
    "alt_label": []
  }, 
  "Religion / Islam / Law": {
    "related": [], 
    "pref_label": "Religion / Islam / Law", 
    "notation": "REL037020", 
    "alt_label": []
  }, 
  "Computers / Certification Guides / A+": {
    "related": [], 
    "pref_label": "Computers / Certification Guides / A+", 
    "notation": "COM055010", 
    "alt_label": []
  }, 
  "Medical / Internal Medicine": {
    "related": [], 
    "pref_label": "Medical / Internal Medicine", 
    "notation": "MED045000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Fairy Tales & Folklore / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Fairy Tales & Folklore / General", 
    "notation": "JUV012030", 
    "alt_label": []
  }, 
  "Technology & Engineering / Civil / Highway & Traffic": {
    "related": [], 
    "pref_label": "Technology & Engineering / Civil / Highway & Traffic", 
    "notation": "TEC009140", 
    "alt_label": []
  }, 
  "History / United States / State & Local / West (ak, Ca, Co, Hi, Id, Mt, Nv, Ut, Wy)": {
    "related": [], 
    "pref_label": "History / United States / State & Local / West (ak, Ca, Co, Hi, Id, Mt, Nv, Ut, Wy)", 
    "notation": "HIS036140", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Astronomy": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Astronomy", 
    "notation": "JNF051040", 
    "alt_label": []
  }, 
  "Gardening / Urban": {
    "related": [], 
    "pref_label": "Gardening / Urban", 
    "notation": "GAR028000", 
    "alt_label": []
  }, 
  "Psychology / Mental Illness": {
    "related": [], 
    "pref_label": "Psychology / Mental Illness", 
    "notation": "PSY018000", 
    "alt_label": []
  }, 
  "Nature / Essays": {
    "related": [], 
    "pref_label": "Nature / Essays", 
    "notation": "NAT024000", 
    "alt_label": []
  }, 
  "Pets / Dogs / Breeds": {
    "related": [], 
    "pref_label": "Pets / Dogs / Breeds", 
    "notation": "PET004010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Games & Activities / Puzzles": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Games & Activities / Puzzles", 
    "notation": "JNF021040", 
    "alt_label": []
  }, 
  "Photography / Business Aspects": {
    "related": [], 
    "pref_label": "Photography / Business Aspects", 
    "notation": "PHO003000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Performing Arts / Circus": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Performing Arts / Circus", 
    "notation": "JNF039010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Europe": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Europe", 
    "notation": "JNF038060", 
    "alt_label": []
  }, 
  "Religion / Christianity / Denominations": {
    "related": [], 
    "pref_label": "Religion / Christianity / Denominations", 
    "notation": "REL094000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Indian & South Asian": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Indian & South Asian", 
    "notation": "CKB044000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Presbyterian": {
    "related": [], 
    "pref_label": "Religion / Christianity / Presbyterian", 
    "notation": "REL097000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Art / Painting": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Art / Painting", 
    "notation": "JNF006050", 
    "alt_label": []
  }, 
  "Fiction / Anthologies (multiple Authors)": {
    "related": [], 
    "pref_label": "Fiction / Anthologies (multiple Authors)", 
    "notation": "FIC003000", 
    "alt_label": [
      "Fiction / Short Stories (multiple Authors)"
    ]
  }, 
  "Juvenile Nonfiction / Religion / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / General", 
    "notation": "JNF049000", 
    "alt_label": []
  }, 
  "Literary Collections / Letters": {
    "related": [], 
    "pref_label": "Literary Collections / Letters", 
    "notation": "LCO011000", 
    "alt_label": []
  }, 
  "Literary Criticism / European / German": {
    "related": [], 
    "pref_label": "Literary Criticism / European / German", 
    "notation": "LIT004170", 
    "alt_label": []
  }, 
  "Technology & Engineering / Marine & Naval": {
    "related": [], 
    "pref_label": "Technology & Engineering / Marine & Naval", 
    "notation": "TEC060000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Rich & Famous": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Rich & Famous", 
    "notation": "BIO013000", 
    "alt_label": [
      "Biography & Autobiography / Famous"
    ]
  }, 
  "Fiction / Ghost": {
    "related": [], 
    "pref_label": "Fiction / Ghost", 
    "notation": "FIC012000", 
    "alt_label": []
  }, 
  "Social Science / Disease & Health Issues": {
    "related": [], 
    "pref_label": "Social Science / Disease & Health Issues", 
    "notation": "SOC057000", 
    "alt_label": []
  }, 
  "Literary Criticism / General": {
    "related": [], 
    "pref_label": "Literary Criticism / General", 
    "notation": "LIT000000", 
    "alt_label": []
  }, 
  "Performing Arts / Film & Video / Guides & Reviews": {
    "related": [], 
    "pref_label": "Performing Arts / Film & Video / Guides & Reviews", 
    "notation": "PER004020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Media Tie-in": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Media Tie-in", 
    "notation": "JNF064000", 
    "alt_label": []
  }, 
  "Education / Special Education / General": {
    "related": [], 
    "pref_label": "Education / Special Education / General", 
    "notation": "EDU026000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Personal Hygiene": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Personal Hygiene", 
    "notation": "JNF024060", 
    "alt_label": [
      "Juvenile Nonfiction / Health & Daily Living / Bodily Functions"
    ]
  }, 
  "Body, Mind & Spirit / Channeling & Mediumship": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Channeling & Mediumship", 
    "notation": "OCC003000", 
    "alt_label": []
  }, 
  "Art / Native American": {
    "related": [], 
    "pref_label": "Art / Native American", 
    "notation": "ART041000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Media & Communications": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Media & Communications", 
    "notation": "BUS070060", 
    "alt_label": []
  }, 
  "Technology & Engineering / Construction / Masonry": {
    "related": [], 
    "pref_label": "Technology & Engineering / Construction / Masonry", 
    "notation": "TEC005060", 
    "alt_label": []
  }, 
  "Philosophy / Ethics & Moral Philosophy": {
    "related": [], 
    "pref_label": "Philosophy / Ethics & Moral Philosophy", 
    "notation": "PHI005000", 
    "alt_label": [
      "Philosophy / Moral Philosophy"
    ]
  }, 
  "Science / Life Sciences / Mycology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Mycology", 
    "notation": "SCI094000", 
    "alt_label": []
  }, 
  "Fiction / Sea Stories": {
    "related": [], 
    "pref_label": "Fiction / Sea Stories", 
    "notation": "FIC047000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Python": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Python", 
    "notation": "COM051360", 
    "alt_label": []
  }, 
  "Bibles / New American Bible / General": {
    "related": [], 
    "pref_label": "Bibles / New American Bible / General", 
    "notation": "BIB009000", 
    "alt_label": []
  }, 
  "Medical / Orthopedics": {
    "related": [], 
    "pref_label": "Medical / Orthopedics", 
    "notation": "MED065000", 
    "alt_label": []
  }, 
  "Reference / Bibliographies & Indexes": {
    "related": [], 
    "pref_label": "Reference / Bibliographies & Indexes", 
    "notation": "REF004000", 
    "alt_label": [
      "Reference / Indexes"
    ]
  }, 
  "Cooking / Courses & Dishes / Soups & Stews": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Soups & Stews", 
    "notation": "CKB079000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Love & Romance": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Love & Romance", 
    "notation": "JUV026000", 
    "alt_label": [
      "Juvenile Fiction / Romance"
    ]
  }, 
  "Religion / Religious Intolerance, Persecution & Conflict": {
    "related": [], 
    "pref_label": "Religion / Religious Intolerance, Persecution & Conflict", 
    "notation": "REL116000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Nanotechnology & Mems": {
    "related": [], 
    "pref_label": "Technology & Engineering / Nanotechnology & Mems", 
    "notation": "TEC027000", 
    "alt_label": []
  }, 
  "Business & Economics / Mergers & Acquisitions": {
    "related": [], 
    "pref_label": "Business & Economics / Mergers & Acquisitions", 
    "notation": "BUS015000", 
    "alt_label": [
      "Business & Economics / Consolidation & Merger"
    ]
  }, 
  "Education / Non-formal Education": {
    "related": [], 
    "pref_label": "Education / Non-formal Education", 
    "notation": "EDU021000", 
    "alt_label": [
      "Education / Alternative Education"
    ]
  }, 
  "Cooking / Methods / Slow Cooking": {
    "related": [], 
    "pref_label": "Cooking / Methods / Slow Cooking", 
    "notation": "CKB109000", 
    "alt_label": []
  }, 
  "Psychology / Movements / Gestalt": {
    "related": [], 
    "pref_label": "Psychology / Movements / Gestalt", 
    "notation": "PSY045050", 
    "alt_label": []
  }, 
  "Sports & Recreation / Triathlon": {
    "related": [], 
    "pref_label": "Sports & Recreation / Triathlon", 
    "notation": "SPO048000", 
    "alt_label": []
  }, 
  "History / Native American": {
    "related": [], 
    "pref_label": "History / Native American", 
    "notation": "HIS028000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Flower Arranging": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Flower Arranging", 
    "notation": "CRA010000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Cancer": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Cancer", 
    "notation": "HEA039030", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Equestrian": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Equestrian", 
    "notation": "JUV032090", 
    "alt_label": []
  }, 
  "Law / Reference": {
    "related": [], 
    "pref_label": "Law / Reference", 
    "notation": "LAW079000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Turkish & Turkic Languages": {
    "related": [], 
    "pref_label": "Foreign Language Study / Turkish & Turkic Languages", 
    "notation": "FOR027000", 
    "alt_label": []
  }, 
  "Education / Preschool & Kindergarten": {
    "related": [], 
    "pref_label": "Education / Preschool & Kindergarten", 
    "notation": "EDU023000", 
    "alt_label": []
  }, 
  "Reference / Yearbooks & Annuals": {
    "related": [], 
    "pref_label": "Reference / Yearbooks & Annuals", 
    "notation": "REF027000", 
    "alt_label": [
      "Reference / Annuals"
    ]
  }, 
  "Medical / Diseases": {
    "related": [], 
    "pref_label": "Medical / Diseases", 
    "notation": "MED022000", 
    "alt_label": []
  }, 
  "Computers / Web / Site Directories": {
    "related": [], 
    "pref_label": "Computers / Web / Site Directories", 
    "notation": "COM060070", 
    "alt_label": []
  }, 
  "Technology & Engineering / Project Management": {
    "related": [], 
    "pref_label": "Technology & Engineering / Project Management", 
    "notation": "TEC062000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Environmentalists & Naturalists": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Environmentalists & Naturalists", 
    "notation": "BIO030000", 
    "alt_label": []
  }, 
  "Medical / Terminal Care": {
    "related": [], 
    "pref_label": "Medical / Terminal Care", 
    "notation": "MED042000", 
    "alt_label": [
      "Medical / Hospice Care"
    ]
  }, 
  "Juvenile Fiction / Social Issues / Sexual Abuse": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Sexual Abuse", 
    "notation": "JUV039210", 
    "alt_label": [
      "Juvenile Fiction / Family / Abuse", 
      "Juvenile Fiction / Social Issues / Abuse"
    ]
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Track & Field": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Track & Field", 
    "notation": "JNF054140", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / United States / State & Local": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / United States / State & Local", 
    "notation": "JNF025180", 
    "alt_label": []
  }, 
  "Social Science / Sociology / Rural": {
    "related": [], 
    "pref_label": "Social Science / Sociology / Rural", 
    "notation": "SOC026020", 
    "alt_label": []
  }, 
  "Music / Recording & Reproduction": {
    "related": [], 
    "pref_label": "Music / Recording & Reproduction", 
    "notation": "MUS032000", 
    "alt_label": []
  }, 
  "Law / Pension Law": {
    "related": [], 
    "pref_label": "Law / Pension Law", 
    "notation": "LAW115000", 
    "alt_label": []
  }, 
  "Religion / Theism": {
    "related": [], 
    "pref_label": "Religion / Theism", 
    "notation": "REL066000", 
    "alt_label": []
  }, 
  "True Crime / Murder / Serial Killers": {
    "related": [], 
    "pref_label": "True Crime / Murder / Serial Killers", 
    "notation": "TRU002010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Girls & Women": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Girls & Women", 
    "notation": "JUV014000", 
    "alt_label": [
      "Juvenile Fiction / Women"
    ]
  }, 
  "Antiques & Collectibles / Rugs": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Rugs", 
    "notation": "ANT040000", 
    "alt_label": []
  }, 
  "Mathematics / Geometry / Algebraic": {
    "related": [], 
    "pref_label": "Mathematics / Geometry / Algebraic", 
    "notation": "MAT012010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Biographical / United States": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Biographical / United States", 
    "notation": "JUV004020", 
    "alt_label": []
  }, 
  "Health & Fitness / Pain Management": {
    "related": [], 
    "pref_label": "Health & Fitness / Pain Management", 
    "notation": "HEA036000", 
    "alt_label": []
  }, 
  "Education / Rural": {
    "related": [], 
    "pref_label": "Education / Rural", 
    "notation": "EDU052000", 
    "alt_label": []
  }, 
  "Law / Antitrust": {
    "related": [], 
    "pref_label": "Law / Antitrust", 
    "notation": "LAW005000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Basketball": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Basketball", 
    "notation": "JNF054020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Deer, Moose & Caribou": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Deer, Moose & Caribou", 
    "notation": "JUV002290", 
    "alt_label": []
  }, 
  "Fiction / Science Fiction / Short Stories": {
    "related": [], 
    "pref_label": "Fiction / Science Fiction / Short Stories", 
    "notation": "FIC028040", 
    "alt_label": []
  }, 
  "Medical / Psychiatry / Psychopharmacology": {
    "related": [], 
    "pref_label": "Medical / Psychiatry / Psychopharmacology", 
    "notation": "MED105020", 
    "alt_label": []
  }, 
  "Architecture / Buildings / Landmarks & Monuments": {
    "related": [], 
    "pref_label": "Architecture / Buildings / Landmarks & Monuments", 
    "notation": "ARC024010", 
    "alt_label": []
  }, 
  "Religion / Christian Ministry / Counseling & Recovery": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / Counseling & Recovery", 
    "notation": "REL050000", 
    "alt_label": []
  }, 
  "Law / Public Contract": {
    "related": [], 
    "pref_label": "Law / Public Contract", 
    "notation": "LAW076000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Horses": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Horses", 
    "notation": "JNF003110", 
    "alt_label": []
  }, 
  "Games / Optical Illusions": {
    "related": [], 
    "pref_label": "Games / Optical Illusions", 
    "notation": "GAM018000", 
    "alt_label": []
  }, 
  "Computers / Internet / Security": {
    "related": [], 
    "pref_label": "Computers / Internet / Security", 
    "notation": "COM060040", 
    "alt_label": [
      "Computers / Security / Internet"
    ]
  }, 
  "Photography / Subjects & Themes / Celebrity": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Celebrity", 
    "notation": "PHO023080", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Comics & Graphic Novels / Superheroes": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Comics & Graphic Novels / Superheroes", 
    "notation": "JUV008020", 
    "alt_label": []
  }, 
  "Fiction / Romance / Historical": {
    "related": [], 
    "pref_label": "Fiction / Romance / Historical", 
    "notation": "FIC027050", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Plains & Prairies": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Plains & Prairies", 
    "notation": "NAT045020", 
    "alt_label": []
  }, 
  "Science / Physics / General": {
    "related": [], 
    "pref_label": "Science / Physics / General", 
    "notation": "SCI055000", 
    "alt_label": []
  }, 
  "Education / Decision-making & Problem Solving": {
    "related": [], 
    "pref_label": "Education / Decision-making & Problem Solving", 
    "notation": "EDU008000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Lisp": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Lisp", 
    "notation": "COM051100", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Family / Siblings": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Family / Siblings", 
    "notation": "JNF019070", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Bears": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Bears", 
    "notation": "JNF003020", 
    "alt_label": []
  }, 
  "Family & Relationships / Toilet Training": {
    "related": [], 
    "pref_label": "Family & Relationships / Toilet Training", 
    "notation": "FAM044000", 
    "alt_label": []
  }, 
  "Religion / Sikhism": {
    "related": [], 
    "pref_label": "Religion / Sikhism", 
    "notation": "REL061000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Family / Siblings": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Family / Siblings", 
    "notation": "JUV013070", 
    "alt_label": []
  }, 
  "Education / Statistics": {
    "related": [], 
    "pref_label": "Education / Statistics", 
    "notation": "EDU027000", 
    "alt_label": []
  }, 
  "Business & Economics / Environmental Economics": {
    "related": [], 
    "pref_label": "Business & Economics / Environmental Economics", 
    "notation": "BUS099000", 
    "alt_label": []
  }, 
  "Architecture / Criticism": {
    "related": [], 
    "pref_label": "Architecture / Criticism", 
    "notation": "ARC001000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Technology / Inventions": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Technology / Inventions", 
    "notation": "JNF061010", 
    "alt_label": []
  }, 
  "True Crime / White Collar Crime": {
    "related": [], 
    "pref_label": "True Crime / White Collar Crime", 
    "notation": "TRU005000", 
    "alt_label": []
  }, 
  "Cooking / Methods / Wok": {
    "related": [], 
    "pref_label": "Cooking / Methods / Wok", 
    "notation": "CKB089000", 
    "alt_label": []
  }, 
  "Political Science / Propaganda": {
    "related": [], 
    "pref_label": "Political Science / Propaganda", 
    "notation": "POL049000", 
    "alt_label": []
  }, 
  "Political Science / Utopias": {
    "related": [], 
    "pref_label": "Political Science / Utopias", 
    "notation": "POL051000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / United States / Civil War Period (1850-1877)": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / United States / Civil War Period (1850-1877)", 
    "notation": "JUV016200", 
    "alt_label": []
  }, 
  "Bibles / New Revised Standard Version / Text": {
    "related": [], 
    "pref_label": "Bibles / New Revised Standard Version / Text", 
    "notation": "BIB016060", 
    "alt_label": []
  }, 
  "Bibles / Multiple Translations / Reference": {
    "related": [], 
    "pref_label": "Bibles / Multiple Translations / Reference", 
    "notation": "BIB008040", 
    "alt_label": []
  }, 
  "Science / Chaotic Behavior In Systems": {
    "related": [], 
    "pref_label": "Science / Chaotic Behavior In Systems", 
    "notation": "SCI012000", 
    "alt_label": []
  }, 
  "Medical / Dentistry / Prosthodontics": {
    "related": [], 
    "pref_label": "Medical / Dentistry / Prosthodontics", 
    "notation": "MED016070", 
    "alt_label": []
  }, 
  "Religion / Christianity / Protestant": {
    "related": [], 
    "pref_label": "Religion / Christianity / Protestant", 
    "notation": "REL053000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Shooting": {
    "related": [], 
    "pref_label": "Sports & Recreation / Shooting", 
    "notation": "SPO037000", 
    "alt_label": []
  }, 
  "Law / Essays": {
    "related": [], 
    "pref_label": "Law / Essays", 
    "notation": "LAW101000", 
    "alt_label": []
  }, 
  "Computers / Operating Systems / General": {
    "related": [], 
    "pref_label": "Computers / Operating Systems / General", 
    "notation": "COM046000", 
    "alt_label": []
  }, 
  "Social Science / Ethnic Studies / Native American Studies": {
    "related": [], 
    "pref_label": "Social Science / Ethnic Studies / Native American Studies", 
    "notation": "SOC021000", 
    "alt_label": [
      "Social Science / Native American Studies"
    ]
  }, 
  "Juvenile Fiction / Social Issues / Death & Dying": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Death & Dying", 
    "notation": "JUV039030", 
    "alt_label": []
  }, 
  "Photography / Individual Photographers / Artists' Books": {
    "related": [], 
    "pref_label": "Photography / Individual Photographers / Artists' Books", 
    "notation": "PHO011010", 
    "alt_label": []
  }, 
  "Travel / Africa / Morocco": {
    "related": [], 
    "pref_label": "Travel / Africa / Morocco", 
    "notation": "TRV002040", 
    "alt_label": []
  }, 
  "Law / Construction": {
    "related": [], 
    "pref_label": "Law / Construction", 
    "notation": "LAW019000", 
    "alt_label": []
  }, 
  "Design / Reference": {
    "related": [], 
    "pref_label": "Design / Reference", 
    "notation": "DES012000", 
    "alt_label": []
  }, 
  "History / Europe / Great Britain": {
    "related": [], 
    "pref_label": "History / Europe / Great Britain", 
    "notation": "HIS015000", 
    "alt_label": []
  }, 
  "Literary Criticism / American / Hispanic American": {
    "related": [], 
    "pref_label": "Literary Criticism / American / Hispanic American", 
    "notation": "LIT004050", 
    "alt_label": []
  }, 
  "Business & Economics / Business Etiquette": {
    "related": [], 
    "pref_label": "Business & Economics / Business Etiquette", 
    "notation": "BUS009000", 
    "alt_label": []
  }, 
  "History / United States / State & Local / General": {
    "related": [], 
    "pref_label": "History / United States / State & Local / General", 
    "notation": "HIS036010", 
    "alt_label": []
  }, 
  "Medical / Podiatry": {
    "related": [], 
    "pref_label": "Medical / Podiatry", 
    "notation": "MED100000", 
    "alt_label": []
  }, 
  "Business & Economics / Management Science": {
    "related": [], 
    "pref_label": "Business & Economics / Management Science", 
    "notation": "BUS042000", 
    "alt_label": []
  }, 
  "Law / Legal Services": {
    "related": [], 
    "pref_label": "Law / Legal Services", 
    "notation": "LAW062000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Training": {
    "related": [], 
    "pref_label": "Sports & Recreation / Training", 
    "notation": "SPO047000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Australia & Oceania": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Australia & Oceania", 
    "notation": "JNF038030", 
    "alt_label": []
  }, 
  "Mathematics / Geometry / Non-euclidean": {
    "related": [], 
    "pref_label": "Mathematics / Geometry / Non-euclidean", 
    "notation": "MAT012040", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / General": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / General", 
    "notation": "CRA000000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Family / Parents": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Family / Parents", 
    "notation": "JNF019060", 
    "alt_label": []
  }, 
  "Medical / Nursing / Emergency": {
    "related": [], 
    "pref_label": "Medical / Nursing / Emergency", 
    "notation": "MED058040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Miscellaneous": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Miscellaneous", 
    "notation": "JUV032050", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Cookies": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Cookies", 
    "notation": "CKB021000", 
    "alt_label": []
  }, 
  "Social Science / Agriculture & Food": {
    "related": [], 
    "pref_label": "Social Science / Agriculture & Food", 
    "notation": "SOC055000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Westerns": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Westerns", 
    "notation": "JUV042000", 
    "alt_label": []
  }, 
  "House & Home / House Plans": {
    "related": [], 
    "pref_label": "House & Home / House Plans", 
    "notation": "HOM011000", 
    "alt_label": []
  }, 
  "Business & Economics / Labor": {
    "related": [], 
    "pref_label": "Business & Economics / Labor", 
    "notation": "BUS038000", 
    "alt_label": []
  }, 
  "Mathematics / Number Theory": {
    "related": [], 
    "pref_label": "Mathematics / Number Theory", 
    "notation": "MAT022000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / General": {
    "related": [], 
    "pref_label": "Biography & Autobiography / General", 
    "notation": "BIO000000", 
    "alt_label": []
  }, 
  "History / Europe / Spain & Portugal": {
    "related": [], 
    "pref_label": "History / Europe / Spain & Portugal", 
    "notation": "HIS045000", 
    "alt_label": [
      "History / Europe / Portugal"
    ]
  }, 
  "Nature / Natural Disasters": {
    "related": [], 
    "pref_label": "Nature / Natural Disasters", 
    "notation": "NAT023000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Legends, Myths, Fables / Arthurian": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Legends, Myths, Fables / Arthurian", 
    "notation": "JUV022010", 
    "alt_label": []
  }, 
  "Bibles / Contemporary English Version / Reference": {
    "related": [], 
    "pref_label": "Bibles / Contemporary English Version / Reference", 
    "notation": "BIB002040", 
    "alt_label": []
  }, 
  "Travel / Hotels, Inns & Hostels": {
    "related": [], 
    "pref_label": "Travel / Hotels, Inns & Hostels", 
    "notation": "TRV013000", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Rationalism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Rationalism", 
    "notation": "PHI032000", 
    "alt_label": []
  }, 
  "Medical / Radiology & Nuclear Medicine": {
    "related": [], 
    "pref_label": "Medical / Radiology & Nuclear Medicine", 
    "notation": "MED080000", 
    "alt_label": [
      "Medical / Nuclear Medicine"
    ]
  }, 
  "Medical / Neurology": {
    "related": [], 
    "pref_label": "Medical / Neurology", 
    "notation": "MED056000", 
    "alt_label": [
      "Medical / Diseases / Brain", 
      "Medical / Diseases / Cerebrovascular", 
      "Medical / Diseases / Neuromuscular"
    ]
  }, 
  "House & Home / Power Tools": {
    "related": [], 
    "pref_label": "House & Home / Power Tools", 
    "notation": "HOM015000", 
    "alt_label": []
  }, 
  "Medical / Test Preparation & Review": {
    "related": [], 
    "pref_label": "Medical / Test Preparation & Review", 
    "notation": "MED086000", 
    "alt_label": []
  }, 
  "Medical / Epidemiology": {
    "related": [], 
    "pref_label": "Medical / Epidemiology", 
    "notation": "MED028000", 
    "alt_label": []
  }, 
  "Religion / Christianity / General": {
    "related": [], 
    "pref_label": "Religion / Christianity / General", 
    "notation": "REL070000", 
    "alt_label": []
  }, 
  "Cooking / Methods / General": {
    "related": [], 
    "pref_label": "Cooking / Methods / General", 
    "notation": "CKB023000", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Architectural & Industrial": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Architectural & Industrial", 
    "notation": "PHO001000", 
    "alt_label": []
  }, 
  "Poetry / Russian & Former Soviet Union": {
    "related": [], 
    "pref_label": "Poetry / Russian & Former Soviet Union", 
    "notation": "POE016000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Comics & Graphic Novels / Media Tie-in": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Comics & Graphic Novels / Media Tie-in", 
    "notation": "JUV008030", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Scandinavian": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Scandinavian", 
    "notation": "CKB074000", 
    "alt_label": []
  }, 
  "Education / Testing & Measurement": {
    "related": [], 
    "pref_label": "Education / Testing & Measurement", 
    "notation": "EDU030000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Ecclesiology": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Ecclesiology", 
    "notation": "REL067050", 
    "alt_label": []
  }, 
  "Computers / Neural Networks": {
    "related": [], 
    "pref_label": "Computers / Neural Networks", 
    "notation": "COM044000", 
    "alt_label": []
  }, 
  "Photography / Techniques / Color": {
    "related": [], 
    "pref_label": "Photography / Techniques / Color", 
    "notation": "PHO020000", 
    "alt_label": []
  }, 
  "Health & Fitness / Infertility": {
    "related": [], 
    "pref_label": "Health & Fitness / Infertility", 
    "notation": "HEA045000", 
    "alt_label": []
  }, 
  "Travel / United States / Northeast / General": {
    "related": [], 
    "pref_label": "Travel / United States / Northeast / General", 
    "notation": "TRV025040", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Herbs, Spices, Condiments": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Herbs, Spices, Condiments", 
    "notation": "CKB040000", 
    "alt_label": []
  }, 
  "Art / Reference": {
    "related": [], 
    "pref_label": "Art / Reference", 
    "notation": "ART025000", 
    "alt_label": []
  }, 
  "Gardening / Regional / Middle Atlantic (dc, De, Md, Nj, Ny, Pa)": {
    "related": [], 
    "pref_label": "Gardening / Regional / Middle Atlantic (dc, De, Md, Nj, Ny, Pa)", 
    "notation": "GAR019020", 
    "alt_label": []
  }, 
  "Religion / Christian Church / Canon & Ecclesiastical Law": {
    "related": [], 
    "pref_label": "Religion / Christian Church / Canon & Ecclesiastical Law", 
    "notation": "REL008000", 
    "alt_label": [
      "Religion / Canon & Ecclesiastical Law", 
      "Religion / Ecclesiastical Law"
    ]
  }, 
  "Technology & Engineering / Environmental / Waste Management": {
    "related": [], 
    "pref_label": "Technology & Engineering / Environmental / Waste Management", 
    "notation": "TEC010020", 
    "alt_label": []
  }, 
  "Nature / Earthquakes & Volcanoes": {
    "related": [], 
    "pref_label": "Nature / Earthquakes & Volcanoes", 
    "notation": "NAT009000", 
    "alt_label": [
      "Nature / Volcanoes"
    ]
  }, 
  "Drama / Medieval": {
    "related": [], 
    "pref_label": "Drama / Medieval", 
    "notation": "DRA018000", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Confectionery": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Confectionery", 
    "notation": "CKB095000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Softball": {
    "related": [], 
    "pref_label": "Sports & Recreation / Softball", 
    "notation": "SPO067000", 
    "alt_label": []
  }, 
  "Religion / Biblical Commentary / New Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Commentary / New Testament", 
    "notation": "REL006070", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Readers / Chapter Books": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Readers / Chapter Books", 
    "notation": "JNF047000", 
    "alt_label": []
  }, 
  "Mathematics / Algebra / Elementary": {
    "related": [], 
    "pref_label": "Mathematics / Algebra / Elementary", 
    "notation": "MAT002030", 
    "alt_label": []
  }, 
  "Computers / Enterprise Applications / General": {
    "related": [], 
    "pref_label": "Computers / Enterprise Applications / General", 
    "notation": "COM005000", 
    "alt_label": []
  }, 
  "House & Home / Sustainable Living": {
    "related": [], 
    "pref_label": "House & Home / Sustainable Living", 
    "notation": "HOM022000", 
    "alt_label": []
  }, 
  "Religion / Psychology Of Religion": {
    "related": [], 
    "pref_label": "Religion / Psychology Of Religion", 
    "notation": "REL075000", 
    "alt_label": []
  }, 
  "Performing Arts / Dance / General": {
    "related": [], 
    "pref_label": "Performing Arts / Dance / General", 
    "notation": "PER003000", 
    "alt_label": []
  }, 
  "Social Science / Slavery": {
    "related": [], 
    "pref_label": "Social Science / Slavery", 
    "notation": "SOC054000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Gymnastics": {
    "related": [], 
    "pref_label": "Sports & Recreation / Gymnastics", 
    "notation": "SPO017000", 
    "alt_label": []
  }, 
  "Drama / American / General": {
    "related": [], 
    "pref_label": "Drama / American / General", 
    "notation": "DRA001000", 
    "alt_label": []
  }, 
  "Bibles / New American Bible / Text": {
    "related": [], 
    "pref_label": "Bibles / New American Bible / Text", 
    "notation": "BIB009060", 
    "alt_label": []
  }, 
  "Nature / Plants / General": {
    "related": [], 
    "pref_label": "Nature / Plants / General", 
    "notation": "NAT026000", 
    "alt_label": []
  }, 
  "Gardening / Regional / Midwest (ia, Il, In, Ks, Mi, Mn, Mo, Nd, Ne, Oh, Sd, Wi)": {
    "related": [], 
    "pref_label": "Gardening / Regional / Midwest (ia, Il, In, Ks, Mi, Mn, Mo, Nd, Ne, Oh, Sd, Wi)", 
    "notation": "GAR019030", 
    "alt_label": []
  }, 
  "Art / Ceramics": {
    "related": [], 
    "pref_label": "Art / Ceramics", 
    "notation": "ART045000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Needlework / General": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Needlework / General", 
    "notation": "CRA022000", 
    "alt_label": []
  }, 
  "Computers / Data Transmission Systems / Electronic Data Interchange": {
    "related": [], 
    "pref_label": "Computers / Data Transmission Systems / Electronic Data Interchange", 
    "notation": "COM020010", 
    "alt_label": []
  }, 
  "Performing Arts / Film & Video / General": {
    "related": [], 
    "pref_label": "Performing Arts / Film & Video / General", 
    "notation": "PER004000", 
    "alt_label": []
  }, 
  "Mathematics / Matrices": {
    "related": [], 
    "pref_label": "Mathematics / Matrices", 
    "notation": "MAT019000", 
    "alt_label": []
  }, 
  "Education / Secondary": {
    "related": [], 
    "pref_label": "Education / Secondary", 
    "notation": "EDU025000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Reference": {
    "related": [], 
    "pref_label": "Technology & Engineering / Reference", 
    "notation": "TEC035000", 
    "alt_label": []
  }, 
  "Poetry / Medieval": {
    "related": [], 
    "pref_label": "Poetry / Medieval", 
    "notation": "POE022000", 
    "alt_label": []
  }, 
  "Political Science / Civics & Citizenship": {
    "related": [], 
    "pref_label": "Political Science / Civics & Citizenship", 
    "notation": "POL003000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Lions, Tigers, Leopards, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Lions, Tigers, Leopards, Etc.", 
    "notation": "JUV002150", 
    "alt_label": []
  }, 
  "Political Science / Public Policy / Social Services & Welfare": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Social Services & Welfare", 
    "notation": "POL019000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Mountaineering": {
    "related": [], 
    "pref_label": "Sports & Recreation / Mountaineering", 
    "notation": "SPO029000", 
    "alt_label": []
  }, 
  "Self-help / Meditations": {
    "related": [], 
    "pref_label": "Self-help / Meditations", 
    "notation": "SEL019000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Bears": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Bears", 
    "notation": "JUV002030", 
    "alt_label": []
  }, 
  "Psychology / Applied Psychology": {
    "related": [], 
    "pref_label": "Psychology / Applied Psychology", 
    "notation": "PSY003000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Hunting": {
    "related": [], 
    "pref_label": "Sports & Recreation / Hunting", 
    "notation": "SPO022000", 
    "alt_label": []
  }, 
  "Art / Body Art & Tattooing": {
    "related": [], 
    "pref_label": "Art / Body Art & Tattooing", 
    "notation": "ART055000", 
    "alt_label": []
  }, 
  "Drama / Caribbean & Latin American": {
    "related": [], 
    "pref_label": "Drama / Caribbean & Latin American", 
    "notation": "DRA014000", 
    "alt_label": []
  }, 
  "Art / Techniques / Pastel Drawing": {
    "related": [], 
    "pref_label": "Art / Techniques / Pastel Drawing", 
    "notation": "ART021000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Women": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Women", 
    "notation": "BIO022000", 
    "alt_label": []
  }, 
  "House & Home / Reference": {
    "related": [], 
    "pref_label": "House & Home / Reference", 
    "notation": "HOM016000", 
    "alt_label": []
  }, 
  "Bibles / Common English Bible / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / Common English Bible / New Testament & Portions", 
    "notation": "BIB022030", 
    "alt_label": []
  }, 
  "Business & Economics / Nonprofit Organizations & Charities": {
    "related": [], 
    "pref_label": "Business & Economics / Nonprofit Organizations & Charities", 
    "notation": "BUS074000", 
    "alt_label": [
      "Business & Economics / Charities"
    ]
  }, 
  "Crafts & Hobbies / Baskets": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Baskets", 
    "notation": "CRA002000", 
    "alt_label": []
  }, 
  "Literary Collections / Middle Eastern": {
    "related": [], 
    "pref_label": "Literary Collections / Middle Eastern", 
    "notation": "LCO012000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Chronic Fatigue Syndrome": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Chronic Fatigue Syndrome", 
    "notation": "HEA039150", 
    "alt_label": []
  }, 
  "Business & Economics / Public Relations": {
    "related": [], 
    "pref_label": "Business & Economics / Public Relations", 
    "notation": "BUS052000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Library & Information Science / Collection Development": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Library & Information Science / Collection Development", 
    "notation": "LAN025040", 
    "alt_label": []
  }, 
  "Business & Economics / Econometrics": {
    "related": [], 
    "pref_label": "Business & Economics / Econometrics", 
    "notation": "BUS021000", 
    "alt_label": []
  }, 
  "History / Military / United States": {
    "related": [], 
    "pref_label": "History / Military / United States", 
    "notation": "HIS027110", 
    "alt_label": []
  }, 
  "Architecture / Interior Design / Lighting": {
    "related": [], 
    "pref_label": "Architecture / Interior Design / Lighting", 
    "notation": "ARC007010", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Molecular Biology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Molecular Biology", 
    "notation": "SCI049000", 
    "alt_label": []
  }, 
  "Medical / Laboratory Medicine": {
    "related": [], 
    "pref_label": "Medical / Laboratory Medicine", 
    "notation": "MED047000", 
    "alt_label": []
  }, 
  "Fiction / Espionage": {
    "related": [], 
    "pref_label": "Fiction / Espionage", 
    "notation": "FIC006000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Biophysics": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Biophysics", 
    "notation": "SCI009000", 
    "alt_label": [
      "Science / Physics / Biophysics"
    ]
  }, 
  "Bibles / Multiple Translations / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / Multiple Translations / Youth & Teen", 
    "notation": "BIB008070", 
    "alt_label": []
  }, 
  "Business & Economics / Commerce": {
    "related": [], 
    "pref_label": "Business & Economics / Commerce", 
    "notation": "BUS073000", 
    "alt_label": []
  }, 
  "Travel / United States / West / General": {
    "related": [], 
    "pref_label": "Travel / United States / West / General", 
    "notation": "TRV025110", 
    "alt_label": []
  }, 
  "Social Science / Archaeology": {
    "related": [], 
    "pref_label": "Social Science / Archaeology", 
    "notation": "SOC003000", 
    "alt_label": []
  }, 
  "Business & Economics / Personal Finance / Money Management": {
    "related": [], 
    "pref_label": "Business & Economics / Personal Finance / Money Management", 
    "notation": "BUS050030", 
    "alt_label": [
      "Business & Economics / Money Management"
    ]
  }, 
  "Business & Economics / Statistics": {
    "related": [], 
    "pref_label": "Business & Economics / Statistics", 
    "notation": "BUS061000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Structural": {
    "related": [], 
    "pref_label": "Technology & Engineering / Structural", 
    "notation": "TEC063000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Stories In Verse": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Stories In Verse", 
    "notation": "JUV057000", 
    "alt_label": [
      "Juvenile Fiction / Poetry"
    ]
  }, 
  "Bibles / The Message / General": {
    "related": [], 
    "pref_label": "Bibles / The Message / General", 
    "notation": "BIB020000", 
    "alt_label": []
  }, 
  "Family & Relationships / General": {
    "related": [], 
    "pref_label": "Family & Relationships / General", 
    "notation": "FAM000000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Giraffes": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Giraffes", 
    "notation": "JNF003280", 
    "alt_label": []
  }, 
  "Religion / Religion, Politics & State": {
    "related": [], 
    "pref_label": "Religion / Religion, Politics & State", 
    "notation": "REL084000", 
    "alt_label": [
      "Religion / Church & State"
    ]
  }, 
  "Crafts & Hobbies / Mixed Media": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Mixed Media", 
    "notation": "CRA054000", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / Weight Control": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / Weight Control", 
    "notation": "CKB026000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Music / Songbooks": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / Songbooks", 
    "notation": "JNF036080", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Pregnancy": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Pregnancy", 
    "notation": "JUV039110", 
    "alt_label": []
  }, 
  "History / United States / State & Local / New England (ct, Ma, Me, Nh, Ri, Vt)": {
    "related": [], 
    "pref_label": "History / United States / State & Local / New England (ct, Ma, Me, Nh, Ri, Vt)", 
    "notation": "HIS036100", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Irish": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Irish", 
    "notation": "CKB046000", 
    "alt_label": []
  }, 
  "Computers / Digital Media / Video & Animation": {
    "related": [], 
    "pref_label": "Computers / Digital Media / Video & Animation", 
    "notation": "COM071000", 
    "alt_label": []
  }, 
  "Business & Economics / E-commerce / Auctions & Small Business": {
    "related": [], 
    "pref_label": "Business & Economics / E-commerce / Auctions & Small Business", 
    "notation": "BUS090040", 
    "alt_label": []
  }, 
  "Architecture / Reference": {
    "related": [], 
    "pref_label": "Architecture / Reference", 
    "notation": "ARC012000", 
    "alt_label": []
  }, 
  "Law / Legal Education": {
    "related": [], 
    "pref_label": "Law / Legal Education", 
    "notation": "LAW059000", 
    "alt_label": [
      "Law / Study & Teaching"
    ]
  }, 
  "Foreign Language Study / Romance Languages (other)": {
    "related": [], 
    "pref_label": "Foreign Language Study / Romance Languages (other)", 
    "notation": "FOR041000", 
    "alt_label": []
  }, 
  "Fiction / Men's Adventure": {
    "related": [], 
    "pref_label": "Fiction / Men's Adventure", 
    "notation": "FIC020000", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Fashion": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Fashion", 
    "notation": "PHO009000", 
    "alt_label": []
  }, 
  "Architecture / Buildings / Residential": {
    "related": [], 
    "pref_label": "Architecture / Buildings / Residential", 
    "notation": "ARC003000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Measurement": {
    "related": [], 
    "pref_label": "Technology & Engineering / Measurement", 
    "notation": "TEC022000", 
    "alt_label": []
  }, 
  "Travel / Bed & Breakfast": {
    "related": [], 
    "pref_label": "Travel / Bed & Breakfast", 
    "notation": "TRV005000", 
    "alt_label": []
  }, 
  "Mathematics / Set Theory": {
    "related": [], 
    "pref_label": "Mathematics / Set Theory", 
    "notation": "MAT028000", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Gay & Lesbian": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Gay & Lesbian", 
    "notation": "TRV026070", 
    "alt_label": []
  }, 
  "Cooking / Methods / Special Appliances": {
    "related": [], 
    "pref_label": "Cooking / Methods / Special Appliances", 
    "notation": "CKB081000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Science / Folklore & Mythology": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Science / Folklore & Mythology", 
    "notation": "JNF052030", 
    "alt_label": []
  }, 
  "Computers / Desktop Applications / Email Clients": {
    "related": [], 
    "pref_label": "Computers / Desktop Applications / Email Clients", 
    "notation": "COM084020", 
    "alt_label": []
  }, 
  "Medical / Allied Health Services / Radiological & Ultrasound Technology": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / Radiological & Ultrasound Technology", 
    "notation": "MED003070", 
    "alt_label": []
  }, 
  "Sports & Recreation / Cricket": {
    "related": [], 
    "pref_label": "Sports & Recreation / Cricket", 
    "notation": "SPO054000", 
    "alt_label": []
  }, 
  "Bibles / God's Word / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / God's Word / New Testament & Portions", 
    "notation": "BIB004030", 
    "alt_label": []
  }, 
  "Computers / Computer Vision & Pattern Recognition": {
    "related": [], 
    "pref_label": "Computers / Computer Vision & Pattern Recognition", 
    "notation": "COM016000", 
    "alt_label": []
  }, 
  "Law / Intellectual Property / Copyright": {
    "related": [], 
    "pref_label": "Law / Intellectual Property / Copyright", 
    "notation": "LAW050010", 
    "alt_label": [
      "Law / Copyright"
    ]
  }, 
  "Law / Labor & Employment": {
    "related": [], 
    "pref_label": "Law / Labor & Employment", 
    "notation": "LAW054000", 
    "alt_label": [
      "Law / Employment"
    ]
  }, 
  "Juvenile Nonfiction / Games & Activities / Card Games": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Games & Activities / Card Games", 
    "notation": "JNF021020", 
    "alt_label": []
  }, 
  "Religion / Baha'i": {
    "related": [], 
    "pref_label": "Religion / Baha'i", 
    "notation": "REL005000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Presidents & Heads Of State": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Presidents & Heads Of State", 
    "notation": "BIO011000", 
    "alt_label": []
  }, 
  "Travel / Europe / Switzerland": {
    "related": [], 
    "pref_label": "Travel / Europe / Switzerland", 
    "notation": "TRV009140", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Biography & Autobiography / Royalty": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Biography & Autobiography / Royalty", 
    "notation": "JNF007140", 
    "alt_label": []
  }, 
  "Mathematics / Algebra / Abstract": {
    "related": [], 
    "pref_label": "Mathematics / Algebra / Abstract", 
    "notation": "MAT002010", 
    "alt_label": []
  }, 
  "Bibles / Common English Bible / Devotional": {
    "related": [], 
    "pref_label": "Bibles / Common English Bible / Devotional", 
    "notation": "BIB022020", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Knots, Macrame & Rope Work": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Knots, Macrame & Rope Work", 
    "notation": "CRA055000", 
    "alt_label": []
  }, 
  "Family & Relationships / Reference": {
    "related": [], 
    "pref_label": "Family & Relationships / Reference", 
    "notation": "FAM038000", 
    "alt_label": []
  }, 
  "Religion / Biblical Reference / Handbooks": {
    "related": [], 
    "pref_label": "Religion / Biblical Reference / Handbooks", 
    "notation": "REL006680", 
    "alt_label": []
  }, 
  "Business & Economics / Sales & Selling / General": {
    "related": [], 
    "pref_label": "Business & Economics / Sales & Selling / General", 
    "notation": "BUS058000", 
    "alt_label": []
  }, 
  "Bibles / La Biblia De Las Americas / Study": {
    "related": [], 
    "pref_label": "Bibles / La Biblia De Las Americas / Study", 
    "notation": "BIB007050", 
    "alt_label": []
  }, 
  "Political Science / World / Middle Eastern": {
    "related": [], 
    "pref_label": "Political Science / World / Middle Eastern", 
    "notation": "POL059000", 
    "alt_label": []
  }, 
  "Performing Arts / Film & Video / Screenwriting": {
    "related": [], 
    "pref_label": "Performing Arts / Film & Video / Screenwriting", 
    "notation": "PER004050", 
    "alt_label": []
  }, 
  "Literary Collections / Asian / Chinese": {
    "related": [], 
    "pref_label": "Literary Collections / Asian / Chinese", 
    "notation": "LCO004010", 
    "alt_label": []
  }, 
  "Law / Consumer": {
    "related": [], 
    "pref_label": "Law / Consumer", 
    "notation": "LAW020000", 
    "alt_label": []
  }, 
  "Reference / Etiquette": {
    "related": [], 
    "pref_label": "Reference / Etiquette", 
    "notation": "REF011000", 
    "alt_label": []
  }, 
  "Political Science / American Government / National": {
    "related": [], 
    "pref_label": "Political Science / American Government / National", 
    "notation": "POL030000", 
    "alt_label": [
      "Political Science / Federal Government"
    ]
  }, 
  "Biography & Autobiography / Political": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Political", 
    "notation": "BIO010000", 
    "alt_label": []
  }, 
  "Humor / Topic / Marriage & Family": {
    "related": [], 
    "pref_label": "Humor / Topic / Marriage & Family", 
    "notation": "HUM011000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Manufacturing": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Manufacturing", 
    "notation": "BUS070050", 
    "alt_label": []
  }, 
  "Technology & Engineering / Cartography": {
    "related": [], 
    "pref_label": "Technology & Engineering / Cartography", 
    "notation": "TEC048000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Musculoskeletal": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Musculoskeletal", 
    "notation": "HEA039100", 
    "alt_label": []
  }, 
  "Technology & Engineering / Construction / Plumbing": {
    "related": [], 
    "pref_label": "Technology & Engineering / Construction / Plumbing", 
    "notation": "TEC005070", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Linguistics / Morphology": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Linguistics / Morphology", 
    "notation": "LAN009020", 
    "alt_label": []
  }, 
  "Travel / Resorts & Spas": {
    "related": [], 
    "pref_label": "Travel / Resorts & Spas", 
    "notation": "TRV030000", 
    "alt_label": []
  }, 
  "Performing Arts / Dance / Notation": {
    "related": [], 
    "pref_label": "Performing Arts / Dance / Notation", 
    "notation": "PER003050", 
    "alt_label": []
  }, 
  "Games / Role Playing & Fantasy": {
    "related": [], 
    "pref_label": "Games / Role Playing & Fantasy", 
    "notation": "GAM010000", 
    "alt_label": [
      "Games / Fantasy Games"
    ]
  }, 
  "Biography & Autobiography / Cultural Heritage": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Cultural Heritage", 
    "notation": "BIO002000", 
    "alt_label": [
      "Biography & Autobiography / African American & Black"
    ]
  }, 
  "Philosophy / Logic": {
    "related": [], 
    "pref_label": "Philosophy / Logic", 
    "notation": "PHI011000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / General", 
    "notation": "JUV016000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Readers / Chapter Books": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Readers / Chapter Books", 
    "notation": "JUV045000", 
    "alt_label": []
  }, 
  "Law / Medical Law & Legislation": {
    "related": [], 
    "pref_label": "Law / Medical Law & Legislation", 
    "notation": "LAW093000", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Professional Growth": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Professional Growth", 
    "notation": "REL012090", 
    "alt_label": []
  }, 
  "Fiction / Fantasy / Paranormal": {
    "related": [], 
    "pref_label": "Fiction / Fantasy / Paranormal", 
    "notation": "FIC009050", 
    "alt_label": []
  }, 
  "Computers / System Administration / Windows Administration": {
    "related": [], 
    "pref_label": "Computers / System Administration / Windows Administration", 
    "notation": "COM088020", 
    "alt_label": []
  }, 
  "Literary Criticism / Reference": {
    "related": [], 
    "pref_label": "Literary Criticism / Reference", 
    "notation": "LIT012000", 
    "alt_label": []
  }, 
  "Education / Teaching Methods & Materials / General": {
    "related": [], 
    "pref_label": "Education / Teaching Methods & Materials / General", 
    "notation": "EDU029000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Reference": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Reference", 
    "notation": "OCC021000", 
    "alt_label": []
  }, 
  "Business & Economics / Foreign Exchange": {
    "related": [], 
    "pref_label": "Business & Economics / Foreign Exchange", 
    "notation": "BUS028000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Lions, Tigers, Leopards, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Lions, Tigers, Leopards, Etc.", 
    "notation": "JNF003130", 
    "alt_label": []
  }, 
  "Fiction / General": {
    "related": [], 
    "pref_label": "Fiction / General", 
    "notation": "FIC000000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Bullying": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Bullying", 
    "notation": "JUV039230", 
    "alt_label": []
  }, 
  "Medical / Family & General Practice": {
    "related": [], 
    "pref_label": "Medical / Family & General Practice", 
    "notation": "MED029000", 
    "alt_label": [
      "Medical / General Practice"
    ]
  }, 
  "Business & Economics / International / General": {
    "related": [], 
    "pref_label": "Business & Economics / International / General", 
    "notation": "BUS035000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Gay & Lesbian": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Gay & Lesbian", 
    "notation": "BIO031000", 
    "alt_label": []
  }, 
  "Business & Economics / Money & Monetary Policy": {
    "related": [], 
    "pref_label": "Business & Economics / Money & Monetary Policy", 
    "notation": "BUS045000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Date & Time": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Date & Time", 
    "notation": "JNF013080", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Symbols, Monuments, National Parks, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Symbols, Monuments, National Parks, Etc.", 
    "notation": "JNF025260", 
    "alt_label": []
  }, 
  "Business & Economics / Infrastructure": {
    "related": [], 
    "pref_label": "Business & Economics / Infrastructure", 
    "notation": "BUS032000", 
    "alt_label": []
  }, 
  "Business & Economics / Exports & Imports": {
    "related": [], 
    "pref_label": "Business & Economics / Exports & Imports", 
    "notation": "BUS026000", 
    "alt_label": [
      "Business & Economics / Imports"
    ]
  }, 
  "Body, Mind & Spirit / Healing / General": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Healing / General", 
    "notation": "OCC011000", 
    "alt_label": []
  }, 
  "Travel / Russia": {
    "related": [], 
    "pref_label": "Travel / Russia", 
    "notation": "TRV023000", 
    "alt_label": []
  }, 
  "Computers / Data Processing": {
    "related": [], 
    "pref_label": "Computers / Data Processing", 
    "notation": "COM018000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Golf": {
    "related": [], 
    "pref_label": "Sports & Recreation / Golf", 
    "notation": "SPO016000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Taxonomy": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Taxonomy", 
    "notation": "SCI087000", 
    "alt_label": []
  }, 
  "Bibles / Christian Standard Bible / Devotional": {
    "related": [], 
    "pref_label": "Bibles / Christian Standard Bible / Devotional", 
    "notation": "BIB001020", 
    "alt_label": []
  }, 
  "History / United States / State & Local / Southwest (az, Nm, Ok, Tx)": {
    "related": [], 
    "pref_label": "History / United States / State & Local / Southwest (az, Nm, Ok, Tx)", 
    "notation": "HIS036130", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Nonfiction": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Nonfiction", 
    "notation": "CGN007000", 
    "alt_label": []
  }, 
  "Foreign Language Study / General": {
    "related": [], 
    "pref_label": "Foreign Language Study / General", 
    "notation": "FOR000000", 
    "alt_label": []
  }, 
  "Religion / Religion & Science": {
    "related": [], 
    "pref_label": "Religion / Religion & Science", 
    "notation": "REL106000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Peer Pressure": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Peer Pressure", 
    "notation": "JNF053110", 
    "alt_label": []
  }, 
  "Technology & Engineering / Metallurgy": {
    "related": [], 
    "pref_label": "Technology & Engineering / Metallurgy", 
    "notation": "TEC023000", 
    "alt_label": []
  }, 
  "Business & Economics / Corporate Governance": {
    "related": [], 
    "pref_label": "Business & Economics / Corporate Governance", 
    "notation": "BUS104000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / General": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / General", 
    "notation": "BUS070000", 
    "alt_label": []
  }, 
  "Medical / Nursing / Oncology & Cancer": {
    "related": [], 
    "pref_label": "Medical / Nursing / Oncology & Cancer", 
    "notation": "MED058160", 
    "alt_label": []
  }, 
  "Medical / Occupational & Industrial Medicine": {
    "related": [], 
    "pref_label": "Medical / Occupational & Industrial Medicine", 
    "notation": "MED061000", 
    "alt_label": [
      "Medical / Industrial Medicine"
    ]
  }, 
  "Self-help / Personal Growth / Self-esteem": {
    "related": [], 
    "pref_label": "Self-help / Personal Growth / Self-esteem", 
    "notation": "SEL023000", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Chocolate": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Chocolate", 
    "notation": "CKB018000", 
    "alt_label": []
  }, 
  "Bibles / New Century Version / Reference": {
    "related": [], 
    "pref_label": "Bibles / New Century Version / Reference", 
    "notation": "BIB011040", 
    "alt_label": []
  }, 
  "Religion / Christianity / Jehovah's Witnesses": {
    "related": [], 
    "pref_label": "Religion / Christianity / Jehovah's Witnesses", 
    "notation": "REL096000", 
    "alt_label": []
  }, 
  "Health & Fitness / Reference": {
    "related": [], 
    "pref_label": "Health & Fitness / Reference", 
    "notation": "HEA020000", 
    "alt_label": []
  }, 
  "Study Aids / Ged (general Educational Development Tests)": {
    "related": [], 
    "pref_label": "Study Aids / Ged (general Educational Development Tests)", 
    "notation": "STU012000", 
    "alt_label": []
  }, 
  "Art / Business Aspects": {
    "related": [], 
    "pref_label": "Art / Business Aspects", 
    "notation": "ART043000", 
    "alt_label": []
  }, 
  "Design / Interior Decorating": {
    "related": [], 
    "pref_label": "Design / Interior Decorating", 
    "notation": "DES010000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Other": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Other", 
    "notation": "JNF025220", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Winter Sports": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Winter Sports", 
    "notation": "JUV032080", 
    "alt_label": []
  }, 
  "Religion / Zoroastrianism": {
    "related": [], 
    "pref_label": "Religion / Zoroastrianism", 
    "notation": "REL069000", 
    "alt_label": []
  }, 
  "Fiction / Christian / Short Stories": {
    "related": [], 
    "pref_label": "Fiction / Christian / Short Stories", 
    "notation": "FIC042050", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Apologetics": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Apologetics", 
    "notation": "REL067030", 
    "alt_label": []
  }, 
  "Medical / Infectious Diseases": {
    "related": [], 
    "pref_label": "Medical / Infectious Diseases", 
    "notation": "MED022090", 
    "alt_label": [
      "Medical / Communicable Diseases", 
      "Medical / Diseases / Bacterial", 
      "Medical / Diseases / Communicable", 
      "Medical / Diseases / Infectious", 
      "Medical / Diseases / Viral"
    ]
  }, 
  "Crafts & Hobbies / Book Printing & Binding": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Book Printing & Binding", 
    "notation": "CRA046000", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / General": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / General", 
    "notation": "PHO023000", 
    "alt_label": []
  }, 
  "Business & Economics / Insurance / General": {
    "related": [], 
    "pref_label": "Business & Economics / Insurance / General", 
    "notation": "BUS033000", 
    "alt_label": []
  }, 
  "Law / Transportation": {
    "related": [], 
    "pref_label": "Law / Transportation", 
    "notation": "LAW117000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Carving": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Carving", 
    "notation": "CRA003000", 
    "alt_label": []
  }, 
  "Business & Economics / E-commerce / Online Trading": {
    "related": [], 
    "pref_label": "Business & Economics / E-commerce / Online Trading", 
    "notation": "BUS090030", 
    "alt_label": []
  }, 
  "History / Historical Geography": {
    "related": [], 
    "pref_label": "History / Historical Geography", 
    "notation": "HIS052000", 
    "alt_label": []
  }, 
  "House & Home / Cleaning & Caretaking": {
    "related": [], 
    "pref_label": "House & Home / Cleaning & Caretaking", 
    "notation": "HOM019000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Emotions & Feelings": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Emotions & Feelings", 
    "notation": "JNF053050", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Educators": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Educators", 
    "notation": "BIO019000", 
    "alt_label": [
      "Biography & Autobiography / Teachers"
    ]
  }, 
  "Philosophy / Language": {
    "related": [], 
    "pref_label": "Philosophy / Language", 
    "notation": "PHI038000", 
    "alt_label": [
      "Philosophy / Philosophy Of Language"
    ]
  }, 
  "Religion / Judaism / Talmud": {
    "related": [], 
    "pref_label": "Religion / Judaism / Talmud", 
    "notation": "REL064000", 
    "alt_label": [
      "Religion / Talmud"
    ]
  }, 
  "Transportation / Automotive / Pictorial": {
    "related": [], 
    "pref_label": "Transportation / Automotive / Pictorial", 
    "notation": "TRA001060", 
    "alt_label": []
  }, 
  "History / Latin America / South America": {
    "related": [], 
    "pref_label": "History / Latin America / South America", 
    "notation": "HIS033000", 
    "alt_label": []
  }, 
  "Art / Subjects & Themes / General": {
    "related": [], 
    "pref_label": "Art / Subjects & Themes / General", 
    "notation": "ART050000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Fitness & Exercise": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Fitness & Exercise", 
    "notation": "JNF024040", 
    "alt_label": []
  }, 
  "Religion / Islam / History": {
    "related": [], 
    "pref_label": "Religion / Islam / History", 
    "notation": "REL037010", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Kitchenware": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Kitchenware", 
    "notation": "ANT022000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Dough": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Dough", 
    "notation": "CRA006000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Parapsychology / Esp (clairvoyance, Precognition, Telepathy)": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Parapsychology / Esp (clairvoyance, Precognition, Telepathy)", 
    "notation": "OCC007000", 
    "alt_label": []
  }, 
  "Humor / Topic / Business & Professional": {
    "related": [], 
    "pref_label": "Humor / Topic / Business & Professional", 
    "notation": "HUM010000", 
    "alt_label": []
  }, 
  "Performing Arts / Radio / Reference": {
    "related": [], 
    "pref_label": "Performing Arts / Radio / Reference", 
    "notation": "PER008020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Biographical / Canada": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Biographical / Canada", 
    "notation": "JUV004040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Judaism": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Judaism", 
    "notation": "JNF049110", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Spirituality / General": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Spirituality / General", 
    "notation": "OCC036000", 
    "alt_label": []
  }, 
  "Performing Arts / Theater / History & Criticism": {
    "related": [], 
    "pref_label": "Performing Arts / Theater / History & Criticism", 
    "notation": "PER011020", 
    "alt_label": []
  }, 
  "Law / Emigration & Immigration": {
    "related": [], 
    "pref_label": "Law / Emigration & Immigration", 
    "notation": "LAW032000", 
    "alt_label": [
      "Law / Immigration"
    ]
  }, 
  "Travel / United States / South / South Atlantic (dc, De, Fl, Ga, Md, Nc, Sc, Va, Wv)": {
    "related": [], 
    "pref_label": "Travel / United States / South / South Atlantic (dc, De, Fl, Ga, Md, Nc, Sc, Va, Wv)", 
    "notation": "TRV025090", 
    "alt_label": []
  }, 
  "Poetry / European / German": {
    "related": [], 
    "pref_label": "Poetry / European / German", 
    "notation": "PEO018000", 
    "alt_label": []
  }, 
  "Health & Fitness / Alternative Therapies": {
    "related": [], 
    "pref_label": "Health & Fitness / Alternative Therapies", 
    "notation": "HEA032000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Transportation / Railroads & Trains": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Transportation / Railroads & Trains", 
    "notation": "JUV041050", 
    "alt_label": []
  }, 
  "Political Science / Political Ideologies / Communism, Post-communism & Socialism": {
    "related": [], 
    "pref_label": "Political Science / Political Ideologies / Communism, Post-communism & Socialism", 
    "notation": "POL005000", 
    "alt_label": []
  }, 
  "Business & Economics / Office Automation": {
    "related": [], 
    "pref_label": "Business & Economics / Office Automation", 
    "notation": "BUS084000", 
    "alt_label": []
  }, 
  "Business & Economics / Green Business": {
    "related": [], 
    "pref_label": "Business & Economics / Green Business", 
    "notation": "BUS094000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Performing Arts / Theater": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Performing Arts / Theater", 
    "notation": "JNF039050", 
    "alt_label": []
  }, 
  "Computers / Hardware / Mainframes & Minicomputers": {
    "related": [], 
    "pref_label": "Computers / Hardware / Mainframes & Minicomputers", 
    "notation": "COM038000", 
    "alt_label": [
      "Computers / Mainframes & Minicomputers"
    ]
  }, 
  "Juvenile Nonfiction / Social Science / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Science / General", 
    "notation": "JNF052000", 
    "alt_label": []
  }, 
  "Literary Criticism / Humor": {
    "related": [], 
    "pref_label": "Literary Criticism / Humor", 
    "notation": "LIT016000", 
    "alt_label": []
  }, 
  "Medical / Alternative Medicine": {
    "related": [], 
    "pref_label": "Medical / Alternative Medicine", 
    "notation": "MED004000", 
    "alt_label": [
      "Medical / Complementary Medicine", 
      "Medical / Iridology", 
      "Medical / Mind-body Medicine (psychoneuroimmunology)"
    ]
  }, 
  "Political Science / Censorship": {
    "related": [], 
    "pref_label": "Political Science / Censorship", 
    "notation": "POL039000", 
    "alt_label": []
  }, 
  "Self-help / Spiritual": {
    "related": [], 
    "pref_label": "Self-help / Spiritual", 
    "notation": "SEL032000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Postcards": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Postcards", 
    "notation": "ANT033000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Diabetes": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Diabetes", 
    "notation": "HEA039050", 
    "alt_label": []
  }, 
  "Performing Arts / Screenplays": {
    "related": [], 
    "pref_label": "Performing Arts / Screenplays", 
    "notation": "PER016000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Needlework / Knitting": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Needlework / Knitting", 
    "notation": "CRA015000", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Cakes": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Cakes", 
    "notation": "CKB014000", 
    "alt_label": []
  }, 
  "Science / Mechanics / Dynamics": {
    "related": [], 
    "pref_label": "Science / Mechanics / Dynamics", 
    "notation": "SCI018000", 
    "alt_label": []
  }, 
  "Political Science / Political Ideologies / Nationalism & Patriotism": {
    "related": [], 
    "pref_label": "Political Science / Political Ideologies / Nationalism & Patriotism", 
    "notation": "POL031000", 
    "alt_label": []
  }, 
  "Law / Trial Practice": {
    "related": [], 
    "pref_label": "Law / Trial Practice", 
    "notation": "LAW088000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Christmas & Advent": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Christmas & Advent", 
    "notation": "JUV017010", 
    "alt_label": []
  }, 
  "Art / History / Contemporary (1945-)": {
    "related": [], 
    "pref_label": "Art / History / Contemporary (1945-)", 
    "notation": "ART015110", 
    "alt_label": []
  }, 
  "Business & Economics / Auditing": {
    "related": [], 
    "pref_label": "Business & Economics / Auditing", 
    "notation": "BUS003000", 
    "alt_label": []
  }, 
  "Family & Relationships / Aging": {
    "related": [], 
    "pref_label": "Family & Relationships / Aging", 
    "notation": "FAM005000", 
    "alt_label": []
  }, 
  "Business & Economics / Inflation": {
    "related": [], 
    "pref_label": "Business & Economics / Inflation", 
    "notation": "BUS031000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Entertainment": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Entertainment", 
    "notation": "BUS070110", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Endangered": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Endangered", 
    "notation": "JNF003270", 
    "alt_label": []
  }, 
  "Architecture / Adaptive Reuse & Renovation": {
    "related": [], 
    "pref_label": "Architecture / Adaptive Reuse & Renovation", 
    "notation": "ARC022000", 
    "alt_label": []
  }, 
  "Education / History": {
    "related": [], 
    "pref_label": "Education / History", 
    "notation": "EDU016000", 
    "alt_label": []
  }, 
  "Religion / Theology": {
    "related": [], 
    "pref_label": "Religion / Theology", 
    "notation": "REL102000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Peer Pressure": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Peer Pressure", 
    "notation": "JUV039100", 
    "alt_label": []
  }, 
  "Juvenile Fiction / School & Education": {
    "related": [], 
    "pref_label": "Juvenile Fiction / School & Education", 
    "notation": "JUV035000", 
    "alt_label": [
      "Juvenile Fiction / Education"
    ]
  }, 
  "Juvenile Fiction / Sports & Recreation / Basketball": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Basketball", 
    "notation": "JUV032020", 
    "alt_label": []
  }, 
  "Self-help / Motivational & Inspirational": {
    "related": [], 
    "pref_label": "Self-help / Motivational & Inspirational", 
    "notation": "SEL021000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Textiles & Costume": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Textiles & Costume", 
    "notation": "ANT047000", 
    "alt_label": [
      "Antiques & Collectibles / Costume"
    ]
  }, 
  "Games / Card Games / General": {
    "related": [], 
    "pref_label": "Games / Card Games / General", 
    "notation": "GAM002000", 
    "alt_label": []
  }, 
  "Religion / Biblical Biography / General": {
    "related": [], 
    "pref_label": "Religion / Biblical Biography / General", 
    "notation": "REL006020", 
    "alt_label": []
  }, 
  "Religion / Biblical Biography / Old Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Biography / Old Testament", 
    "notation": "REL006030", 
    "alt_label": []
  }, 
  "Psychology / Neuropsychology": {
    "related": [], 
    "pref_label": "Psychology / Neuropsychology", 
    "notation": "PSY020000", 
    "alt_label": []
  }, 
  "Law / Securities": {
    "related": [], 
    "pref_label": "Law / Securities", 
    "notation": "LAW083000", 
    "alt_label": []
  }, 
  "Gardening / Ornamental Plants": {
    "related": [], 
    "pref_label": "Gardening / Ornamental Plants", 
    "notation": "GAR017000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Entheogens & Visionary Substances": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Entheogens & Visionary Substances", 
    "notation": "OCC039000", 
    "alt_label": []
  }, 
  "Architecture / Decoration & Ornament": {
    "related": [], 
    "pref_label": "Architecture / Decoration & Ornament", 
    "notation": "ARC002000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Football": {
    "related": [], 
    "pref_label": "Sports & Recreation / Football", 
    "notation": "SPO015000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Europe": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Europe", 
    "notation": "JUV016040", 
    "alt_label": []
  }, 
  "Computers / Desktop Applications / Presentation Software": {
    "related": [], 
    "pref_label": "Computers / Desktop Applications / Presentation Software", 
    "notation": "COM078000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Tobacco-related": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Tobacco-related", 
    "notation": "ANT055000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Construction / Electrical": {
    "related": [], 
    "pref_label": "Technology & Engineering / Construction / Electrical", 
    "notation": "TEC005030", 
    "alt_label": []
  }, 
  "House & Home / Do-it-yourself / Carpentry": {
    "related": [], 
    "pref_label": "House & Home / Do-it-yourself / Carpentry", 
    "notation": "HOM001000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Spelling": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Spelling", 
    "notation": "LAN019000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Dating & Sex": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Dating & Sex", 
    "notation": "JUV039190", 
    "alt_label": [
      "Juvenile Fiction / Social Issues / Sexuality"
    ]
  }, 
  "Art / History / Renaissance": {
    "related": [], 
    "pref_label": "Art / History / Renaissance", 
    "notation": "ART015080", 
    "alt_label": []
  }, 
  "Art / Collections, Catalogs, Exhibitions / Group Shows": {
    "related": [], 
    "pref_label": "Art / Collections, Catalogs, Exhibitions / Group Shows", 
    "notation": "ART006010", 
    "alt_label": []
  }, 
  "Science / Life Sciences / General": {
    "related": [], 
    "pref_label": "Science / Life Sciences / General", 
    "notation": "SCI086000", 
    "alt_label": []
  }, 
  "Health & Fitness / Vision": {
    "related": [], 
    "pref_label": "Health & Fitness / Vision", 
    "notation": "HEA037000", 
    "alt_label": []
  }, 
  "History / Africa / East": {
    "related": [], 
    "pref_label": "History / Africa / East", 
    "notation": "HIS001020", 
    "alt_label": []
  }, 
  "Religion / Biblical Criticism & Interpretation / Old Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Criticism & Interpretation / Old Testament", 
    "notation": "REL006090", 
    "alt_label": []
  }, 
  "Foreign Language Study / Italian": {
    "related": [], 
    "pref_label": "Foreign Language Study / Italian", 
    "notation": "FOR013000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Reference": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Reference", 
    "notation": "LAN014000", 
    "alt_label": []
  }, 
  "Business & Economics / General": {
    "related": [], 
    "pref_label": "Business & Economics / General", 
    "notation": "BUS000000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Jungle Animals": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Jungle Animals", 
    "notation": "JUV002340", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Java": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Java", 
    "notation": "COM051280", 
    "alt_label": []
  }, 
  "Computers / Web / General": {
    "related": [], 
    "pref_label": "Computers / Web / General", 
    "notation": "COM060080", 
    "alt_label": []
  }, 
  "Music / Religious / Jewish": {
    "related": [], 
    "pref_label": "Music / Religious / Jewish", 
    "notation": "MUS048020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Weights & Measures": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Weights & Measures", 
    "notation": "JNF051200", 
    "alt_label": []
  }, 
  "Business & Economics / E-commerce / Internet Marketing": {
    "related": [], 
    "pref_label": "Business & Economics / E-commerce / Internet Marketing", 
    "notation": "BUS090010", 
    "alt_label": [
      "Business & Economics / Marketing / Internet"
    ]
  }, 
  "Self-help / Handwriting Analysis": {
    "related": [], 
    "pref_label": "Self-help / Handwriting Analysis", 
    "notation": "SEL015000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Disasters": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Disasters", 
    "notation": "JNF051160", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Sports Cards / Hockey": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Sports Cards / Hockey", 
    "notation": "ANT042040", 
    "alt_label": []
  }, 
  "Law / Civil Rights": {
    "related": [], 
    "pref_label": "Law / Civil Rights", 
    "notation": "LAW013000", 
    "alt_label": []
  }, 
  "Computers / System Administration / Linux & Unix Administration": {
    "related": [], 
    "pref_label": "Computers / System Administration / Linux & Unix Administration", 
    "notation": "COM088010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Bedtime & Dreams": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Bedtime & Dreams", 
    "notation": "JUV033060", 
    "alt_label": []
  }, 
  "Health & Fitness / Yoga": {
    "related": [], 
    "pref_label": "Health & Fitness / Yoga", 
    "notation": "HEA025000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Zoology / Ichthyology & Herpetology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Zoology / Ichthyology & Herpetology", 
    "notation": "SCI070010", 
    "alt_label": []
  }, 
  "Bibles / Nueva Version International / Devotional": {
    "related": [], 
    "pref_label": "Bibles / Nueva Version International / Devotional", 
    "notation": "BIB017020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Humor / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Humor / General", 
    "notation": "JNF028000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Gastrointestinal": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Gastrointestinal", 
    "notation": "HEA039010", 
    "alt_label": []
  }, 
  "Mathematics / Essays": {
    "related": [], 
    "pref_label": "Mathematics / Essays", 
    "notation": "MAT039000", 
    "alt_label": []
  }, 
  "Business & Economics / Business Law": {
    "related": [], 
    "pref_label": "Business & Economics / Business Law", 
    "notation": "BUS010000", 
    "alt_label": []
  }, 
  "Literary Criticism / Gay & Lesbian": {
    "related": [], 
    "pref_label": "Literary Criticism / Gay & Lesbian", 
    "notation": "LIT004160", 
    "alt_label": []
  }, 
  "History / Military / Vietnam War": {
    "related": [], 
    "pref_label": "History / Military / Vietnam War", 
    "notation": "HIS027070", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Biographical / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Biographical / General", 
    "notation": "JUV004000", 
    "alt_label": []
  }, 
  "Fiction / Mystery & Detective / Police Procedural": {
    "related": [], 
    "pref_label": "Fiction / Mystery & Detective / Police Procedural", 
    "notation": "FIC022020", 
    "alt_label": []
  }, 
  "House & Home / Do-it-yourself / Masonry": {
    "related": [], 
    "pref_label": "House & Home / Do-it-yourself / Masonry", 
    "notation": "HOM012000", 
    "alt_label": []
  }, 
  "Law / Media & The Law": {
    "related": [], 
    "pref_label": "Law / Media & The Law", 
    "notation": "LAW096000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Mammals": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Mammals", 
    "notation": "JNF003140", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / General": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / General", 
    "notation": "REL067000", 
    "alt_label": []
  }, 
  "Architecture / Urban & Land Use Planning": {
    "related": [], 
    "pref_label": "Architecture / Urban & Land Use Planning", 
    "notation": "ARC010000", 
    "alt_label": []
  }, 
  "Bibles / New International Version / Reference": {
    "related": [], 
    "pref_label": "Bibles / New International Version / Reference", 
    "notation": "BIB013040", 
    "alt_label": []
  }, 
  "Self-help / Death, Grief, Bereavement": {
    "related": [], 
    "pref_label": "Self-help / Death, Grief, Bereavement", 
    "notation": "SEL010000", 
    "alt_label": [
      "Self-help / Bereavement", 
      "Self-help / Grief"
    ]
  }, 
  "Medical / Clinical Medicine": {
    "related": [], 
    "pref_label": "Medical / Clinical Medicine", 
    "notation": "MED014000", 
    "alt_label": []
  }, 
  "Humor / Form / Parodies": {
    "related": [], 
    "pref_label": "Humor / Form / Parodies", 
    "notation": "HUM007000", 
    "alt_label": []
  }, 
  "Bibles / New International Reader's Version / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / New International Reader's Version / New Testament & Portions", 
    "notation": "BIB012030", 
    "alt_label": []
  }, 
  "Business & Economics / Reference": {
    "related": [], 
    "pref_label": "Business & Economics / Reference", 
    "notation": "BUS055000", 
    "alt_label": []
  }, 
  "Fiction / Science Fiction / Military": {
    "related": [], 
    "pref_label": "Fiction / Science Fiction / Military", 
    "notation": "FIC028050", 
    "alt_label": []
  }, 
  "Computers / Online Services / General": {
    "related": [], 
    "pref_label": "Computers / Online Services / General", 
    "notation": "COM069000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Literary": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Literary", 
    "notation": "CGN006000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Pascal": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Pascal", 
    "notation": "COM051130", 
    "alt_label": []
  }, 
  "Bibles / New International Reader's Version / Text": {
    "related": [], 
    "pref_label": "Bibles / New International Reader's Version / Text", 
    "notation": "BIB012060", 
    "alt_label": []
  }, 
  "Sports & Recreation / Wrestling": {
    "related": [], 
    "pref_label": "Sports & Recreation / Wrestling", 
    "notation": "SPO053000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Snowboarding": {
    "related": [], 
    "pref_label": "Sports & Recreation / Snowboarding", 
    "notation": "SPO072000", 
    "alt_label": []
  }, 
  "Business & Economics / Insurance / Automobile": {
    "related": [], 
    "pref_label": "Business & Economics / Insurance / Automobile", 
    "notation": "BUS033010", 
    "alt_label": []
  }, 
  "Computers / Networking / General": {
    "related": [], 
    "pref_label": "Computers / Networking / General", 
    "notation": "COM043000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Military & Marches": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Military & Marches", 
    "notation": "MUS045000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / General": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / General", 
    "notation": "CGN000000", 
    "alt_label": []
  }, 
  "Fiction / Romance / Erotica": {
    "related": [], 
    "pref_label": "Fiction / Romance / Erotica", 
    "notation": "FIC027010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Ancient": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Ancient", 
    "notation": "JNF025020", 
    "alt_label": []
  }, 
  "Photography / Individual Photographers / General": {
    "related": [], 
    "pref_label": "Photography / Individual Photographers / General", 
    "notation": "PHO011000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Genetics & Genomics": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Genetics & Genomics", 
    "notation": "SCI029000", 
    "alt_label": []
  }, 
  "Religion / Biblical Reference / Atlases": {
    "related": [], 
    "pref_label": "Religion / Biblical Reference / Atlases", 
    "notation": "REL006650", 
    "alt_label": []
  }, 
  "Business & Economics / Personal Finance / General": {
    "related": [], 
    "pref_label": "Business & Economics / Personal Finance / General", 
    "notation": "BUS050000", 
    "alt_label": []
  }, 
  "History / Europe / Eastern": {
    "related": [], 
    "pref_label": "History / Europe / Eastern", 
    "notation": "HIS010010", 
    "alt_label": []
  }, 
  "Bibles / Other Translations / Reference": {
    "related": [], 
    "pref_label": "Bibles / Other Translations / Reference", 
    "notation": "BIB018040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Africa": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Africa", 
    "notation": "JNF038010", 
    "alt_label": []
  }, 
  "Art / Conceptual": {
    "related": [], 
    "pref_label": "Art / Conceptual", 
    "notation": "ART008000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Meditation": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Meditation", 
    "notation": "OCC010000", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Nudes": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Nudes", 
    "notation": "PHO023050", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Composition & Creative Writing": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Composition & Creative Writing", 
    "notation": "LAN005000", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Vegetables": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Vegetables", 
    "notation": "CKB085000", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Phenomenology": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Phenomenology", 
    "notation": "PHI018000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Materials Science": {
    "related": [], 
    "pref_label": "Technology & Engineering / Materials Science", 
    "notation": "TEC021000", 
    "alt_label": []
  }, 
  "Political Science / Peace": {
    "related": [], 
    "pref_label": "Political Science / Peace", 
    "notation": "POL034000", 
    "alt_label": []
  }, 
  "Health & Fitness / Physical Impairments": {
    "related": [], 
    "pref_label": "Health & Fitness / Physical Impairments", 
    "notation": "HEA018000", 
    "alt_label": []
  }, 
  "Medical / Nursing / Maternity, Perinatal, Women's Health": {
    "related": [], 
    "pref_label": "Medical / Nursing / Maternity, Perinatal, Women's Health", 
    "notation": "MED058120", 
    "alt_label": []
  }, 
  "Religion / Theosophy": {
    "related": [], 
    "pref_label": "Religion / Theosophy", 
    "notation": "REL068000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Inspirational": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Inspirational", 
    "notation": "JNF049250", 
    "alt_label": []
  }, 
  "Family & Relationships / Prejudice": {
    "related": [], 
    "pref_label": "Family & Relationships / Prejudice", 
    "notation": "FAM037000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Telecommunications": {
    "related": [], 
    "pref_label": "Technology & Engineering / Telecommunications", 
    "notation": "TEC041000", 
    "alt_label": []
  }, 
  "Medical / Aids & Hiv": {
    "related": [], 
    "pref_label": "Medical / Aids & Hiv", 
    "notation": "MED022020", 
    "alt_label": [
      "Medical / Diseases / Aids & Hiv"
    ]
  }, 
  "Bibles / New King James Version / Study": {
    "related": [], 
    "pref_label": "Bibles / New King James Version / Study", 
    "notation": "BIB014050", 
    "alt_label": []
  }, 
  "Computers / Mathematical & Statistical Software": {
    "related": [], 
    "pref_label": "Computers / Mathematical & Statistical Software", 
    "notation": "COM077000", 
    "alt_label": []
  }, 
  "Gardening / Trees": {
    "related": [], 
    "pref_label": "Gardening / Trees", 
    "notation": "GAR024000", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Addiction": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Addiction", 
    "notation": "PSY038000", 
    "alt_label": []
  }, 
  "Education / Special Education / Mental Disabilities": {
    "related": [], 
    "pref_label": "Education / Special Education / Mental Disabilities", 
    "notation": "EDU026030", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Horror & Ghost Stories": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Horror & Ghost Stories", 
    "notation": "JUV018000", 
    "alt_label": [
      "Juvenile Fiction / Ghost Stories"
    ]
  }, 
  "Juvenile Fiction / Concepts / Date & Time": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Date & Time", 
    "notation": "JUV009070", 
    "alt_label": []
  }, 
  "History / Europe / France": {
    "related": [], 
    "pref_label": "History / Europe / France", 
    "notation": "HIS013000", 
    "alt_label": []
  }, 
  "Gardening / House Plants & Indoor": {
    "related": [], 
    "pref_label": "Gardening / House Plants & Indoor", 
    "notation": "GAR010000", 
    "alt_label": [
      "Gardening / Indoor"
    ]
  }, 
  "Bibles / New International Version / Devotional": {
    "related": [], 
    "pref_label": "Bibles / New International Version / Devotional", 
    "notation": "BIB013020", 
    "alt_label": []
  }, 
  "Education / Finance": {
    "related": [], 
    "pref_label": "Education / Finance", 
    "notation": "EDU013000", 
    "alt_label": [
      "Education / Funding"
    ]
  }, 
  "Juvenile Fiction / Historical / United States / Colonial & Revolutionary Periods": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / United States / Colonial & Revolutionary Periods", 
    "notation": "JUV016120", 
    "alt_label": []
  }, 
  "Humor / General": {
    "related": [], 
    "pref_label": "Humor / General", 
    "notation": "HUM000000", 
    "alt_label": []
  }, 
  "Art / Australian & Oceanian": {
    "related": [], 
    "pref_label": "Art / Australian & Oceanian", 
    "notation": "ART042000", 
    "alt_label": [
      "Art / Oceanian"
    ]
  }, 
  "Computers / Programming / Open Source": {
    "related": [], 
    "pref_label": "Computers / Programming / Open Source", 
    "notation": "COM051390", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Nonfiction": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Nonfiction", 
    "notation": "CGN004170", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Transportation / Boats, Ships & Underwater Craft": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Transportation / Boats, Ships & Underwater Craft", 
    "notation": "JNF057020", 
    "alt_label": []
  }, 
  "Study Aids / High School Entrance": {
    "related": [], 
    "pref_label": "Study Aids / High School Entrance", 
    "notation": "STU025000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Comics & Graphic Novels": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Comics & Graphic Novels", 
    "notation": "JNF049190", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Computers": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Computers", 
    "notation": "JUV049000", 
    "alt_label": []
  }, 
  "Law / Commercial / International Trade": {
    "related": [], 
    "pref_label": "Law / Commercial / International Trade", 
    "notation": "LAW014010", 
    "alt_label": []
  }, 
  "Bibles / Today's New International Version / General": {
    "related": [], 
    "pref_label": "Bibles / Today's New International Version / General", 
    "notation": "BIB021000", 
    "alt_label": []
  }, 
  "Business & Economics / Insurance / Liability": {
    "related": [], 
    "pref_label": "Business & Economics / Insurance / Liability", 
    "notation": "BUS033050", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Music / History": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / History", 
    "notation": "JNF036020", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Divination / Tarot": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Divination / Tarot", 
    "notation": "OCC024000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Cycling": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Cycling", 
    "notation": "JUV032180", 
    "alt_label": []
  }, 
  "Art / Color Theory": {
    "related": [], 
    "pref_label": "Art / Color Theory", 
    "notation": "ART007000", 
    "alt_label": []
  }, 
  "Fiction / Political": {
    "related": [], 
    "pref_label": "Fiction / Political", 
    "notation": "FIC037000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Kangaroos": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Kangaroos", 
    "notation": "JNF003310", 
    "alt_label": []
  }, 
  "Medical / Nursing / Medical & Surgical": {
    "related": [], 
    "pref_label": "Medical / Nursing / Medical & Surgical", 
    "notation": "MED058220", 
    "alt_label": []
  }, 
  "Fiction / Mashups": {
    "related": [], 
    "pref_label": "Fiction / Mashups", 
    "notation": "FIC05700", 
    "alt_label": []
  }, 
  "House & Home / Repair": {
    "related": [], 
    "pref_label": "House & Home / Repair", 
    "notation": "HOM010000", 
    "alt_label": []
  }, 
  "Science / Energy": {
    "related": [], 
    "pref_label": "Science / Energy", 
    "notation": "SCI024000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Wood Toys": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Wood Toys", 
    "notation": "CRA041000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Squirrels": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Squirrels", 
    "notation": "JUV002230", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / English, Scottish & Welsh": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / English, Scottish & Welsh", 
    "notation": "CKB011000", 
    "alt_label": [
      "Cooking / Regional & Ethnic / British", 
      "Cooking / Regional & Ethnic / Scottish", 
      "Cooking / Regional & Ethnic / Welsh"
    ]
  }, 
  "Antiques & Collectibles / Firearms & Weapons": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Firearms & Weapons", 
    "notation": "ANT016000", 
    "alt_label": [
      "Antiques & Collectibles / Weapons"
    ]
  }, 
  "Gardening / Shade": {
    "related": [], 
    "pref_label": "Gardening / Shade", 
    "notation": "GAR020000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Occultism": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Occultism", 
    "notation": "OCC016000", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / Paul's Letters": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / Paul's Letters", 
    "notation": "REL006720", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Skateboarding": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Skateboarding", 
    "notation": "JUV032140", 
    "alt_label": []
  }, 
  "Literary Collections / Gay & Lesbian": {
    "related": [], 
    "pref_label": "Literary Collections / Gay & Lesbian", 
    "notation": "LCO016000", 
    "alt_label": []
  }, 
  "Social Science / Islamic Studies": {
    "related": [], 
    "pref_label": "Social Science / Islamic Studies", 
    "notation": "SOC048000", 
    "alt_label": []
  }, 
  "Bibles / New American Standard Bible / Study": {
    "related": [], 
    "pref_label": "Bibles / New American Standard Bible / Study", 
    "notation": "BIB010050", 
    "alt_label": []
  }, 
  "Travel / Europe / Benelux Countries (belgium, Netherlands, Luxembourg)": {
    "related": [], 
    "pref_label": "Travel / Europe / Benelux Countries (belgium, Netherlands, Luxembourg)", 
    "notation": "TRV009020", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Composers & Musicians": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Composers & Musicians", 
    "notation": "BIO004000", 
    "alt_label": [
      "Biography & Autobiography / Musicians"
    ]
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Thanksgiving": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Thanksgiving", 
    "notation": "JUV017060", 
    "alt_label": []
  }, 
  "Family & Relationships / Emotions": {
    "related": [], 
    "pref_label": "Family & Relationships / Emotions", 
    "notation": "FAM018000", 
    "alt_label": []
  }, 
  "Business & Economics / Information Management": {
    "related": [], 
    "pref_label": "Business & Economics / Information Management", 
    "notation": "BUS083000", 
    "alt_label": []
  }, 
  "Science / System Theory": {
    "related": [], 
    "pref_label": "Science / System Theory", 
    "notation": "SCI064000", 
    "alt_label": []
  }, 
  "Art / Techniques / Drawing": {
    "related": [], 
    "pref_label": "Art / Techniques / Drawing", 
    "notation": "ART010000", 
    "alt_label": []
  }, 
  "Law / Landlord & Tenant": {
    "related": [], 
    "pref_label": "Law / Landlord & Tenant", 
    "notation": "LAW112000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Polish": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Polish", 
    "notation": "CKB065000", 
    "alt_label": []
  }, 
  "Cooking / Methods / Barbecue & Grilling": {
    "related": [], 
    "pref_label": "Cooking / Methods / Barbecue & Grilling", 
    "notation": "CKB005000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Biography & Autobiography / Music": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Biography & Autobiography / Music", 
    "notation": "JNF007040", 
    "alt_label": []
  }, 
  "Technology & Engineering / Petroleum": {
    "related": [], 
    "pref_label": "Technology & Engineering / Petroleum", 
    "notation": "TEC047000", 
    "alt_label": []
  }, 
  "Family & Relationships / Life Stages / General": {
    "related": [], 
    "pref_label": "Family & Relationships / Life Stages / General", 
    "notation": "FAM046000", 
    "alt_label": []
  }, 
  "Political Science / Political Process / Political Advocacy": {
    "related": [], 
    "pref_label": "Political Science / Political Process / Political Advocacy", 
    "notation": "POL043000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Autographs": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Autographs", 
    "notation": "ANT003000", 
    "alt_label": []
  }, 
  "Computers / Web / Podcasting & Webcasting": {
    "related": [], 
    "pref_label": "Computers / Web / Podcasting & Webcasting", 
    "notation": "COM060110", 
    "alt_label": []
  }, 
  "Poetry / Epic": {
    "related": [], 
    "pref_label": "Poetry / Epic", 
    "notation": "POE014000", 
    "alt_label": []
  }, 
  "Business & Economics / Investments & Securities / Stocks": {
    "related": [], 
    "pref_label": "Business & Economics / Investments & Securities / Stocks", 
    "notation": "BUS036060", 
    "alt_label": []
  }, 
  "Sports & Recreation / Walking": {
    "related": [], 
    "pref_label": "Sports & Recreation / Walking", 
    "notation": "SPO050000", 
    "alt_label": []
  }, 
  "Health & Fitness / Vitamins": {
    "related": [], 
    "pref_label": "Health & Fitness / Vitamins", 
    "notation": "HEA023000", 
    "alt_label": []
  }, 
  "History / Military / Weapons": {
    "related": [], 
    "pref_label": "History / Military / Weapons", 
    "notation": "HIS027080", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / People & Places": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / People & Places", 
    "notation": "JUV033190", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Visionary & Metaphysical": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Visionary & Metaphysical", 
    "notation": "JUV046000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Canadiana": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Canadiana", 
    "notation": "ANT054000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Needlework / Lace & Tatting": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Needlework / Lace & Tatting", 
    "notation": "CRA016000", 
    "alt_label": [
      "Crafts & Hobbies / Needlework / Tatting"
    ]
  }, 
  "Bibles / New King James Version / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / New King James Version / Youth & Teen", 
    "notation": "BIB014070", 
    "alt_label": []
  }, 
  "Literary Criticism / Science Fiction & Fantasy": {
    "related": [], 
    "pref_label": "Literary Criticism / Science Fiction & Fantasy", 
    "notation": "LIT004260", 
    "alt_label": [
      "Literary Criticism / Fantasy"
    ]
  }, 
  "Juvenile Fiction / Social Issues / Friendship": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Friendship", 
    "notation": "JUV039060", 
    "alt_label": []
  }, 
  "Religion / Christian Rituals & Practice / General": {
    "related": [], 
    "pref_label": "Religion / Christian Rituals & Practice / General", 
    "notation": "REL055000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Track & Field": {
    "related": [], 
    "pref_label": "Sports & Recreation / Track & Field", 
    "notation": "SPO046000", 
    "alt_label": []
  }, 
  "Fiction / African American / Mystery & Detective": {
    "related": [], 
    "pref_label": "Fiction / African American / Mystery & Detective", 
    "notation": "FIC049050", 
    "alt_label": []
  }, 
  "Bibles / King James Version / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / King James Version / New Testament & Portions", 
    "notation": "BIB006030", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Rap & Hip Hop": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Rap & Hip Hop", 
    "notation": "MUS031000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Literacy": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Literacy", 
    "notation": "LAN010000", 
    "alt_label": []
  }, 
  "Bibles / New American Standard Bible / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / New American Standard Bible / Youth & Teen", 
    "notation": "BIB010070", 
    "alt_label": []
  }, 
  "History / Latin America / Mexico": {
    "related": [], 
    "pref_label": "History / Latin America / Mexico", 
    "notation": "HIS025000", 
    "alt_label": []
  }, 
  "Drama / European / General": {
    "related": [], 
    "pref_label": "Drama / European / General", 
    "notation": "DRA004000", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / Low Carbohydrate": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / Low Carbohydrate", 
    "notation": "CKB108000", 
    "alt_label": []
  }, 
  "Games / Gambling / Sports": {
    "related": [], 
    "pref_label": "Games / Gambling / Sports", 
    "notation": "GAM004050", 
    "alt_label": []
  }, 
  "Fiction / Historical": {
    "related": [], 
    "pref_label": "Fiction / Historical", 
    "notation": "FIC014000", 
    "alt_label": []
  }, 
  "Business & Economics / Development / Sustainable Development": {
    "related": [], 
    "pref_label": "Business & Economics / Development / Sustainable Development", 
    "notation": "BUS072000", 
    "alt_label": [
      "Business & Economics / Sustainable Development"
    ]
  }, 
  "Science / Chemistry / Organic": {
    "related": [], 
    "pref_label": "Science / Chemistry / Organic", 
    "notation": "SCI013040", 
    "alt_label": []
  }, 
  "Science / History": {
    "related": [], 
    "pref_label": "Science / History", 
    "notation": "SCI034000", 
    "alt_label": []
  }, 
  "Health & Fitness / Healthy Living": {
    "related": [], 
    "pref_label": "Health & Fitness / Healthy Living", 
    "notation": "HEA010000", 
    "alt_label": []
  }, 
  "Cooking / Tablesetting": {
    "related": [], 
    "pref_label": "Cooking / Tablesetting", 
    "notation": "CKB082000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Process": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Process", 
    "notation": "REL067130", 
    "alt_label": []
  }, 
  "Reference / Weddings": {
    "related": [], 
    "pref_label": "Reference / Weddings", 
    "notation": "REF024000", 
    "alt_label": []
  }, 
  "Art / Study & Teaching": {
    "related": [], 
    "pref_label": "Art / Study & Teaching", 
    "notation": "ART027000", 
    "alt_label": []
  }, 
  "Business & Economics / Investments & Securities / Futures": {
    "related": [], 
    "pref_label": "Business & Economics / Investments & Securities / Futures", 
    "notation": "BUS036020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / People & Places": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / People & Places", 
    "notation": "JNF049270", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Colors": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Colors", 
    "notation": "JUV009020", 
    "alt_label": []
  }, 
  "Philosophy / Hermeneutics": {
    "related": [], 
    "pref_label": "Philosophy / Hermeneutics", 
    "notation": "PHI036000", 
    "alt_label": []
  }, 
  "Literary Criticism / European / Spanish & Portuguese": {
    "related": [], 
    "pref_label": "Literary Criticism / European / Spanish & Portuguese", 
    "notation": "LIT004280", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Eating Disorders": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Eating Disorders", 
    "notation": "PSY011000", 
    "alt_label": []
  }, 
  "Travel / Middle East / Israel": {
    "related": [], 
    "pref_label": "Travel / Middle East / Israel", 
    "notation": "TRV015020", 
    "alt_label": []
  }, 
  "Reference / Handbooks & Manuals": {
    "related": [], 
    "pref_label": "Reference / Handbooks & Manuals", 
    "notation": "REF028000", 
    "alt_label": []
  }, 
  "Computers / General": {
    "related": [], 
    "pref_label": "Computers / General", 
    "notation": "COM000000", 
    "alt_label": []
  }, 
  "Psychology / Movements / Jungian": {
    "related": [], 
    "pref_label": "Psychology / Movements / Jungian", 
    "notation": "PSY045060", 
    "alt_label": []
  }, 
  "Science / Earth Sciences / Oceanography": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / Oceanography", 
    "notation": "SCI052000", 
    "alt_label": []
  }, 
  "History / Europe / Italy": {
    "related": [], 
    "pref_label": "History / Europe / Italy", 
    "notation": "HIS020000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Food Industry": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Food Industry", 
    "notation": "BUS070120", 
    "alt_label": []
  }, 
  "Travel / Europe / Scandinavia": {
    "related": [], 
    "pref_label": "Travel / Europe / Scandinavia", 
    "notation": "TRV009120", 
    "alt_label": []
  }, 
  "Bibles / Contemporary English Version / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / Contemporary English Version / New Testament & Portions", 
    "notation": "BIB002030", 
    "alt_label": []
  }, 
  "Religion / Messianic Judaism": {
    "related": [], 
    "pref_label": "Religion / Messianic Judaism", 
    "notation": "REL101000", 
    "alt_label": []
  }, 
  "Pets / Horses / General": {
    "related": [], 
    "pref_label": "Pets / Horses / General", 
    "notation": "PET006000", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / Heart": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / Heart", 
    "notation": "CKB104000", 
    "alt_label": []
  }, 
  "Business & Economics / Strategic Planning": {
    "related": [], 
    "pref_label": "Business & Economics / Strategic Planning", 
    "notation": "BUS063000", 
    "alt_label": [
      "Business & Economics / Planning"
    ]
  }, 
  "Business & Economics / Investments & Securities / Mutual Funds": {
    "related": [], 
    "pref_label": "Business & Economics / Investments & Securities / Mutual Funds", 
    "notation": "BUS036030", 
    "alt_label": []
  }, 
  "Technology & Engineering / Microwaves": {
    "related": [], 
    "pref_label": "Technology & Engineering / Microwaves", 
    "notation": "TEC024000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Emigration & Immigration": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Emigration & Immigration", 
    "notation": "JNF053240", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Modern": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Modern", 
    "notation": "JNF025140", 
    "alt_label": []
  }, 
  "Medical / Nursing / Test Preparation & Review": {
    "related": [], 
    "pref_label": "Medical / Nursing / Test Preparation & Review", 
    "notation": "MED058210", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / General", 
    "notation": "JNF049130", 
    "alt_label": []
  }, 
  "Study Aids / Nte (national Teacher Examinations)": {
    "related": [], 
    "pref_label": "Study Aids / Nte (national Teacher Examinations)", 
    "notation": "STU019000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Medical": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Medical", 
    "notation": "BIO017000", 
    "alt_label": [
      "Biography & Autobiography / Doctors", 
      "Biography & Autobiography / Nurses", 
      "Biography & Autobiography / Physicians", 
      "Biography & Autobiography / Surgeons"
    ]
  }, 
  "Art / Digital": {
    "related": [], 
    "pref_label": "Art / Digital", 
    "notation": "ART046000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Dolls": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Dolls", 
    "notation": "ANT015000", 
    "alt_label": []
  }, 
  "Study Aids / Lsat (law School Admission Test)": {
    "related": [], 
    "pref_label": "Study Aids / Lsat (law School Admission Test)", 
    "notation": "STU017000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Pigs": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Pigs", 
    "notation": "JUV002200", 
    "alt_label": []
  }, 
  "Law / Family Law / General": {
    "related": [], 
    "pref_label": "Law / Family Law / General", 
    "notation": "LAW038000", 
    "alt_label": []
  }, 
  "Law / Administrative Law & Regulatory Practice": {
    "related": [], 
    "pref_label": "Law / Administrative Law & Regulatory Practice", 
    "notation": "LAW001000", 
    "alt_label": []
  }, 
  "Self-help / Substance Abuse & Addictions / Tobacco": {
    "related": [], 
    "pref_label": "Self-help / Substance Abuse & Addictions / Tobacco", 
    "notation": "SEL026010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Bible Stories / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Bible Stories / General", 
    "notation": "JNF049040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Girls & Women": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Girls & Women", 
    "notation": "JNF023000", 
    "alt_label": [
      "Juvenile Nonfiction / Women"
    ]
  }, 
  "Architecture / Historic Preservation / Restoration Techniques": {
    "related": [], 
    "pref_label": "Architecture / Historic Preservation / Restoration Techniques", 
    "notation": "ARC014010", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / General": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / General", 
    "notation": "OCC000000", 
    "alt_label": [
      "Body, Mind & Spirit / New Age"
    ]
  }, 
  "Cooking / Courses & Dishes / Pizza": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Pizza", 
    "notation": "CKB064000", 
    "alt_label": []
  }, 
  "Business & Economics / Insurance / Property": {
    "related": [], 
    "pref_label": "Business & Economics / Insurance / Property", 
    "notation": "BUS033080", 
    "alt_label": []
  }, 
  "Pets / Horses / Riding": {
    "related": [], 
    "pref_label": "Pets / Horses / Riding", 
    "notation": "PET006010", 
    "alt_label": []
  }, 
  "Art / Collections, Catalogs, Exhibitions / General": {
    "related": [], 
    "pref_label": "Art / Collections, Catalogs, Exhibitions / General", 
    "notation": "ART006000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Transportation / Aviation": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Transportation / Aviation", 
    "notation": "JUV041010", 
    "alt_label": []
  }, 
  "Art / Subjects & Themes / Human Figure": {
    "related": [], 
    "pref_label": "Art / Subjects & Themes / Human Figure", 
    "notation": "ART050010", 
    "alt_label": []
  }, 
  "Literary Collections /  European / Italian": {
    "related": [], 
    "pref_label": "Literary Collections /  European / Italian", 
    "notation": "LC008040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Activity Books": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Activity Books", 
    "notation": "JNF001000", 
    "alt_label": []
  }, 
  "Computers / Desktop Applications / Spreadsheets": {
    "related": [], 
    "pref_label": "Computers / Desktop Applications / Spreadsheets", 
    "notation": "COM054000", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Bipolar Disorder": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Bipolar Disorder", 
    "notation": "PSY022030", 
    "alt_label": []
  }, 
  "Philosophy / Metaphysics": {
    "related": [], 
    "pref_label": "Philosophy / Metaphysics", 
    "notation": "PHI013000", 
    "alt_label": []
  }, 
  "Travel / Africa / North": {
    "related": [], 
    "pref_label": "Travel / Africa / North", 
    "notation": "TRV002050", 
    "alt_label": []
  }, 
  "Business & Economics / Operations Research": {
    "related": [], 
    "pref_label": "Business & Economics / Operations Research", 
    "notation": "BUS049000", 
    "alt_label": []
  }, 
  "Nature / Animals / Bears": {
    "related": [], 
    "pref_label": "Nature / Animals / Bears", 
    "notation": "NAT003000", 
    "alt_label": []
  }, 
  "Nature / Plants / Flowers": {
    "related": [], 
    "pref_label": "Nature / Plants / Flowers", 
    "notation": "NAT013000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Reference": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Reference", 
    "notation": "CRA032000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Americana": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Americana", 
    "notation": "ANT001000", 
    "alt_label": [
      "Antiques & Collectibles / Disneyana"
    ]
  }, 
  "Religion / Biblical Studies / Bible Study Guides": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / Bible Study Guides", 
    "notation": "REL006700", 
    "alt_label": []
  }, 
  "Mathematics / Group Theory": {
    "related": [], 
    "pref_label": "Mathematics / Group Theory", 
    "notation": "MAT014000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Divination / Fortune Telling": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Divination / Fortune Telling", 
    "notation": "OCC008000", 
    "alt_label": []
  }, 
  "Fiction / Contemporary Women": {
    "related": [], 
    "pref_label": "Fiction / Contemporary Women", 
    "notation": "FIC044000", 
    "alt_label": []
  }, 
  "Travel / Canada / Western Provinces (ab, Bc)": {
    "related": [], 
    "pref_label": "Travel / Canada / Western Provinces (ab, Bc)", 
    "notation": "TRV006050", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Appetizers": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Appetizers", 
    "notation": "CKB003000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Horticulture": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Horticulture", 
    "notation": "SCI073000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Chinese": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Chinese", 
    "notation": "CKB017000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Dinosaurs & Prehistoric Creatures": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Dinosaurs & Prehistoric Creatures", 
    "notation": "JUV002060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / General", 
    "notation": "JNF003000", 
    "alt_label": []
  }, 
  "History / Military / Nuclear Warfare": {
    "related": [], 
    "pref_label": "History / Military / Nuclear Warfare", 
    "notation": "HIS027030", 
    "alt_label": []
  }, 
  "Bibles / Today's New International Version / Devotional": {
    "related": [], 
    "pref_label": "Bibles / Today's New International Version / Devotional", 
    "notation": "BIB021020", 
    "alt_label": []
  }, 
  "History / Expeditions & Discoveries": {
    "related": [], 
    "pref_label": "History / Expeditions & Discoveries", 
    "notation": "HIS051000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Civil / Earthquake": {
    "related": [], 
    "pref_label": "Technology & Engineering / Civil / Earthquake", 
    "notation": "TEC009120", 
    "alt_label": []
  }, 
  "Pets / General": {
    "related": [], 
    "pref_label": "Pets / General", 
    "notation": "PET000000", 
    "alt_label": []
  }, 
  "Medical / Veterinary Medicine / Small Animal": {
    "related": [], 
    "pref_label": "Medical / Veterinary Medicine / Small Animal", 
    "notation": "MED089030", 
    "alt_label": []
  }, 
  "Technology & Engineering / Power Resources / Electrical": {
    "related": [], 
    "pref_label": "Technology & Engineering / Power Resources / Electrical", 
    "notation": "TEC031020", 
    "alt_label": []
  }, 
  "Medical / Nursing / Psychiatric": {
    "related": [], 
    "pref_label": "Medical / Nursing / Psychiatric", 
    "notation": "MED058180", 
    "alt_label": []
  }, 
  "Drama / General": {
    "related": [], 
    "pref_label": "Drama / General", 
    "notation": "DRA000000", 
    "alt_label": []
  }, 
  "Law / Forensic Science": {
    "related": [], 
    "pref_label": "Law / Forensic Science", 
    "notation": "LAW041000", 
    "alt_label": []
  }, 
  "Medical / Urology": {
    "related": [], 
    "pref_label": "Medical / Urology", 
    "notation": "MED088000", 
    "alt_label": [
      "Medical / Diseases / Genitourinary"
    ]
  }, 
  "Law / Communications": {
    "related": [], 
    "pref_label": "Law / Communications", 
    "notation": "LAW015000", 
    "alt_label": []
  }, 
  "Religion / Gnosticism": {
    "related": [], 
    "pref_label": "Religion / Gnosticism", 
    "notation": "REL112000", 
    "alt_label": []
  }, 
  "Medical / Nursing / Mental Health": {
    "related": [], 
    "pref_label": "Medical / Nursing / Mental Health", 
    "notation": "MED058130", 
    "alt_label": []
  }, 
  "History / Latin America / Central America": {
    "related": [], 
    "pref_label": "History / Latin America / Central America", 
    "notation": "HIS007000", 
    "alt_label": []
  }, 
  "Travel / Asia / Southeast": {
    "related": [], 
    "pref_label": "Travel / Asia / Southeast", 
    "notation": "TRV003060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Alphabet": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Alphabet", 
    "notation": "JNF013010", 
    "alt_label": [
      "Juvenile Nonfiction / Alphabet", 
      "Juvenile Nonfiction / Language Arts / Alphabet"
    ]
  }, 
  "Bibles / New Revised Standard Version / Reference": {
    "related": [], 
    "pref_label": "Bibles / New Revised Standard Version / Reference", 
    "notation": "BIB016040", 
    "alt_label": []
  }, 
  "Performing Arts / Dance / Folk": {
    "related": [], 
    "pref_label": "Performing Arts / Dance / Folk", 
    "notation": "PER003020", 
    "alt_label": []
  }, 
  "Political Science / Political Ideologies / Democracy": {
    "related": [], 
    "pref_label": "Political Science / Political Ideologies / Democracy", 
    "notation": "POL007000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Action & Adventure": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Action & Adventure", 
    "notation": "JUV033040", 
    "alt_label": []
  }, 
  "Bibles / New Revised Standard Version / Devotional": {
    "related": [], 
    "pref_label": "Bibles / New Revised Standard Version / Devotional", 
    "notation": "BIB016020", 
    "alt_label": []
  }, 
  "Mathematics / Functional Analysis": {
    "related": [], 
    "pref_label": "Mathematics / Functional Analysis", 
    "notation": "MAT037000", 
    "alt_label": []
  }, 
  "Political Science / Intelligence & Espionage": {
    "related": [], 
    "pref_label": "Political Science / Intelligence & Espionage", 
    "notation": "POL036000", 
    "alt_label": []
  }, 
  "Business & Economics / Franchises": {
    "related": [], 
    "pref_label": "Business & Economics / Franchises", 
    "notation": "BUS105000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Dating & Sex": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Dating & Sex", 
    "notation": "JNF053020", 
    "alt_label": [
      "Juvenile Nonfiction / Social Issues / Sexuality"
    ]
  }, 
  "Foreign Language Study / Latin": {
    "related": [], 
    "pref_label": "Foreign Language Study / Latin", 
    "notation": "FOR016000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Style Manuals": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Style Manuals", 
    "notation": "LAN028000", 
    "alt_label": []
  }, 
  "Law / Air & Space": {
    "related": [], 
    "pref_label": "Law / Air & Space", 
    "notation": "LAW002000", 
    "alt_label": []
  }, 
  "Family & Relationships / Parenting / Parent & Adult Child": {
    "related": [], 
    "pref_label": "Family & Relationships / Parenting / Parent & Adult Child", 
    "notation": "FAM033000", 
    "alt_label": []
  }, 
  "Religion / Christian Church / History": {
    "related": [], 
    "pref_label": "Religion / Christian Church / History", 
    "notation": "REL108020", 
    "alt_label": []
  }, 
  "Medical / Perinatology & Neonatology": {
    "related": [], 
    "pref_label": "Medical / Perinatology & Neonatology", 
    "notation": "MED070000", 
    "alt_label": [
      "Medical / Neonatology"
    ]
  }, 
  "Psychology / Movements / General": {
    "related": [], 
    "pref_label": "Psychology / Movements / General", 
    "notation": "PSY045000", 
    "alt_label": []
  }, 
  "Religion / Judaism / General": {
    "related": [], 
    "pref_label": "Religion / Judaism / General", 
    "notation": "REL040000", 
    "alt_label": []
  }, 
  "Business & Economics / Structural Adjustment": {
    "related": [], 
    "pref_label": "Business & Economics / Structural Adjustment", 
    "notation": "BUS062000", 
    "alt_label": []
  }, 
  "Psychology / Human Sexuality": {
    "related": [], 
    "pref_label": "Psychology / Human Sexuality", 
    "notation": "PSY016000", 
    "alt_label": [
      "Psychology / Sexuality"
    ]
  }, 
  "Health & Fitness / Diseases / Heart": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Heart", 
    "notation": "HEA039080", 
    "alt_label": []
  }, 
  "Philosophy / Free Will & Determinism": {
    "related": [], 
    "pref_label": "Philosophy / Free Will & Determinism", 
    "notation": "PHI007000", 
    "alt_label": []
  }, 
  "Medical / Neuroscience": {
    "related": [], 
    "pref_label": "Medical / Neuroscience", 
    "notation": "MED057000", 
    "alt_label": []
  }, 
  "Mathematics / Geometry / Differential": {
    "related": [], 
    "pref_label": "Mathematics / Geometry / Differential", 
    "notation": "MAT012030", 
    "alt_label": []
  }, 
  "Social Science / Anthropology / Physical": {
    "related": [], 
    "pref_label": "Social Science / Anthropology / Physical", 
    "notation": "SOC002020", 
    "alt_label": []
  }, 
  "Cooking / Methods / Raw Food": {
    "related": [], 
    "pref_label": "Cooking / Methods / Raw Food", 
    "notation": "CKB110000", 
    "alt_label": []
  }, 
  "Computers / Hardware / Network Hardware": {
    "related": [], 
    "pref_label": "Computers / Hardware / Network Hardware", 
    "notation": "COM075000", 
    "alt_label": [
      "Computers / Internet / Server Maintenance"
    ]
  }, 
  "History / United States / Revolutionary Period (1775-1800)": {
    "related": [], 
    "pref_label": "History / United States / Revolutionary Period (1775-1800)", 
    "notation": "HIS036030", 
    "alt_label": []
  }, 
  "Bibles / Common English Bible / General": {
    "related": [], 
    "pref_label": "Bibles / Common English Bible / General", 
    "notation": "BIB022000", 
    "alt_label": []
  }, 
  "Art / Collections, Catalogs, Exhibitions / Permanent Collections": {
    "related": [], 
    "pref_label": "Art / Collections, Catalogs, Exhibitions / Permanent Collections", 
    "notation": "ART006020", 
    "alt_label": []
  }, 
  "Bibles / International Children's Bible / Devotional": {
    "related": [], 
    "pref_label": "Bibles / International Children's Bible / Devotional", 
    "notation": "BIB005020", 
    "alt_label": []
  }, 
  "Computers / Buyer's Guides": {
    "related": [], 
    "pref_label": "Computers / Buyer's Guides", 
    "notation": "COM006000", 
    "alt_label": []
  }, 
  "Self-help / Sexual Instruction": {
    "related": [], 
    "pref_label": "Self-help / Sexual Instruction", 
    "notation": "SEL034000", 
    "alt_label": []
  }, 
  "Nature / Animals / Birds": {
    "related": [], 
    "pref_label": "Nature / Animals / Birds", 
    "notation": "NAT043000", 
    "alt_label": []
  }, 
  "Foreign Language Study / German": {
    "related": [], 
    "pref_label": "Foreign Language Study / German", 
    "notation": "FOR009000", 
    "alt_label": []
  }, 
  "Medical / Drug Guides": {
    "related": [], 
    "pref_label": "Medical / Drug Guides", 
    "notation": "MED023000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Depression & Mental Illness": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Depression & Mental Illness", 
    "notation": "JNF053230", 
    "alt_label": [
      "Juvenile Nonfiction / Health & Daily Living / Depression & Mental Illness"
    ]
  }, 
  "Medical / History": {
    "related": [], 
    "pref_label": "Medical / History", 
    "notation": "MED039000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Biomedical": {
    "related": [], 
    "pref_label": "Technology & Engineering / Biomedical", 
    "notation": "TEC059000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Biography & Autobiography / Social Activists": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Biography & Autobiography / Social Activists", 
    "notation": "JNF007110", 
    "alt_label": []
  }, 
  "Law / Public": {
    "related": [], 
    "pref_label": "Law / Public", 
    "notation": "LAW075000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Racquetball": {
    "related": [], 
    "pref_label": "Sports & Recreation / Racquetball", 
    "notation": "SPO032000", 
    "alt_label": []
  }, 
  "Medical / Health Care Delivery": {
    "related": [], 
    "pref_label": "Medical / Health Care Delivery", 
    "notation": "MED035000", 
    "alt_label": []
  }, 
  "Drama / European / Italian": {
    "related": [], 
    "pref_label": "Drama / European / Italian", 
    "notation": "DRA004030", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Senior": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Senior", 
    "notation": "TRV026050", 
    "alt_label": []
  }, 
  "Fiction / Short Stories (single Author)": {
    "related": [], 
    "pref_label": "Fiction / Short Stories (single Author)", 
    "notation": "FIC029000", 
    "alt_label": []
  }, 
  "Medical / Diagnosis": {
    "related": [], 
    "pref_label": "Medical / Diagnosis", 
    "notation": "MED018000", 
    "alt_label": []
  }, 
  "Performing Arts / Theater / Miming": {
    "related": [], 
    "pref_label": "Performing Arts / Theater / Miming", 
    "notation": "PER006000", 
    "alt_label": [
      "Performing Arts / Miming"
    ]
  }, 
  "Transportation / Aviation / Piloting & Flight Instruction": {
    "related": [], 
    "pref_label": "Transportation / Aviation / Piloting & Flight Instruction", 
    "notation": "TRA002050", 
    "alt_label": []
  }, 
  "Medical / Histology": {
    "related": [], 
    "pref_label": "Medical / Histology", 
    "notation": "MED110000", 
    "alt_label": []
  }, 
  "History / Asia / Central Asia": {
    "related": [], 
    "pref_label": "History / Asia / Central Asia", 
    "notation": "HIS050000", 
    "alt_label": []
  }, 
  "Education / Parent Participation": {
    "related": [], 
    "pref_label": "Education / Parent Participation", 
    "notation": "EDU022000", 
    "alt_label": []
  }, 
  "Computers / Electronic Publishing": {
    "related": [], 
    "pref_label": "Computers / Electronic Publishing", 
    "notation": "COM065000", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Natural Foods": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Natural Foods", 
    "notation": "CKB059000", 
    "alt_label": []
  }, 
  "Political Science / World / European": {
    "related": [], 
    "pref_label": "Political Science / World / European", 
    "notation": "POL058000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Christianity": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Christianity", 
    "notation": "JNF049080", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Javascript": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Javascript", 
    "notation": "COM051260", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Russian": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Russian", 
    "notation": "CKB072000", 
    "alt_label": []
  }, 
  "Music / Printed Music / General": {
    "related": [], 
    "pref_label": "Music / Printed Music / General", 
    "notation": "MUS037000", 
    "alt_label": []
  }, 
  "Business & Economics / Consumer Behavior": {
    "related": [], 
    "pref_label": "Business & Economics / Consumer Behavior", 
    "notation": "BUS016000", 
    "alt_label": []
  }, 
  "Reference / Writing Skills": {
    "related": [], 
    "pref_label": "Reference / Writing Skills", 
    "notation": "REF026000", 
    "alt_label": []
  }, 
  "Computers / Computerized Home & Entertainment": {
    "related": [], 
    "pref_label": "Computers / Computerized Home & Entertainment", 
    "notation": "COM086000", 
    "alt_label": []
  }, 
  "Bibles / New International Version / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / New International Version / New Testament & Portions", 
    "notation": "BIB013030", 
    "alt_label": []
  }, 
  "Cooking / Methods / Garnishing": {
    "related": [], 
    "pref_label": "Cooking / Methods / Garnishing", 
    "notation": "CKB033000", 
    "alt_label": []
  }, 
  "Business & Economics / Project Management": {
    "related": [], 
    "pref_label": "Business & Economics / Project Management", 
    "notation": "BUS101000", 
    "alt_label": []
  }, 
  "Poetry / Asian / General": {
    "related": [], 
    "pref_label": "Poetry / Asian / General", 
    "notation": "POE009000", 
    "alt_label": []
  }, 
  "Fiction / Romance / Paranormal": {
    "related": [], 
    "pref_label": "Fiction / Romance / Paranormal", 
    "notation": "FIC027120", 
    "alt_label": []
  }, 
  "Technology & Engineering / Military Science": {
    "related": [], 
    "pref_label": "Technology & Engineering / Military Science", 
    "notation": "TEC025000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Automation": {
    "related": [], 
    "pref_label": "Technology & Engineering / Automation", 
    "notation": "TEC004000", 
    "alt_label": []
  }, 
  "Travel / Europe / Great Britain": {
    "related": [], 
    "pref_label": "Travel / Europe / Great Britain", 
    "notation": "TRV009070", 
    "alt_label": []
  }, 
  "Travel / Africa / East": {
    "related": [], 
    "pref_label": "Travel / Africa / East", 
    "notation": "TRV002020", 
    "alt_label": []
  }, 
  "Business & Economics / Real Estate / Buying & Selling Homes": {
    "related": [], 
    "pref_label": "Business & Economics / Real Estate / Buying & Selling Homes", 
    "notation": "BUS054010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Historical": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Historical", 
    "notation": "JUV033140", 
    "alt_label": []
  }, 
  "Travel / Middle East / General": {
    "related": [], 
    "pref_label": "Travel / Middle East / General", 
    "notation": "TRV015000", 
    "alt_label": []
  }, 
  "Self-help / Depression": {
    "related": [], 
    "pref_label": "Self-help / Depression", 
    "notation": "SEL011000", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Sports": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Sports", 
    "notation": "PHO023060", 
    "alt_label": []
  }, 
  "Law / Judicial Power": {
    "related": [], 
    "pref_label": "Law / Judicial Power", 
    "notation": "LAW111000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Cycling": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Cycling", 
    "notation": "JNF054040", 
    "alt_label": []
  }, 
  "Art / American / Asian American": {
    "related": [], 
    "pref_label": "Art / American / Asian American", 
    "notation": "ART039000", 
    "alt_label": []
  }, 
  "Business & Economics / Organizational Development": {
    "related": [], 
    "pref_label": "Business & Economics / Organizational Development", 
    "notation": "BUS103000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Erotica": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Erotica", 
    "notation": "CGN004020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / United States / Asian American": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / United States / Asian American", 
    "notation": "JUV011020", 
    "alt_label": []
  }, 
  "Cooking / Methods / Quantity": {
    "related": [], 
    "pref_label": "Cooking / Methods / Quantity", 
    "notation": "CKB069000", 
    "alt_label": []
  }, 
  "Bibles / Other Translations / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / Other Translations / Youth & Teen", 
    "notation": "BIB018070", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Business": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Business", 
    "notation": "TRV026010", 
    "alt_label": []
  }, 
  "Social Science / Media Studies": {
    "related": [], 
    "pref_label": "Social Science / Media Studies", 
    "notation": "SOC052000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Service": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Service", 
    "notation": "BUS070080", 
    "alt_label": []
  }, 
  "Music / Religious / General": {
    "related": [], 
    "pref_label": "Music / Religious / General", 
    "notation": "MUS048000", 
    "alt_label": []
  }, 
  "Science / Physics / Optics & Light": {
    "related": [], 
    "pref_label": "Science / Physics / Optics & Light", 
    "notation": "SCI053000", 
    "alt_label": [
      "Science / Light"
    ]
  }, 
  "Photography / Criticism": {
    "related": [], 
    "pref_label": "Photography / Criticism", 
    "notation": "PHO005000", 
    "alt_label": []
  }, 
  "Performing Arts / Television / Reference": {
    "related": [], 
    "pref_label": "Performing Arts / Television / Reference", 
    "notation": "PER010040", 
    "alt_label": []
  }, 
  "Foreign Language Study / Miscellaneous": {
    "related": [], 
    "pref_label": "Foreign Language Study / Miscellaneous", 
    "notation": "FOR017000", 
    "alt_label": []
  }, 
  "Foreign Language Study / French": {
    "related": [], 
    "pref_label": "Foreign Language Study / French", 
    "notation": "FOR008000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Wolves & Coyotes": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Wolves & Coyotes", 
    "notation": "JNF003240", 
    "alt_label": []
  }, 
  "Technology & Engineering / Operations Research": {
    "related": [], 
    "pref_label": "Technology & Engineering / Operations Research", 
    "notation": "TEC029000", 
    "alt_label": []
  }, 
  "Business & Economics / Budgeting": {
    "related": [], 
    "pref_label": "Business & Economics / Budgeting", 
    "notation": "BUS006000", 
    "alt_label": []
  }, 
  "Law / Military": {
    "related": [], 
    "pref_label": "Law / Military", 
    "notation": "LAW068000", 
    "alt_label": []
  }, 
  "Education / Computers & Technology": {
    "related": [], 
    "pref_label": "Education / Computers & Technology", 
    "notation": "EDU039000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Basketball": {
    "related": [], 
    "pref_label": "Sports & Recreation / Basketball", 
    "notation": "SPO004000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Family & Relationships": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Family & Relationships", 
    "notation": "JNF049210", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / Allergy": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / Allergy", 
    "notation": "CKB106000", 
    "alt_label": []
  }, 
  "Computers / Networking / Security": {
    "related": [], 
    "pref_label": "Computers / Networking / Security", 
    "notation": "COM043050", 
    "alt_label": [
      "Computers / Security / Networking"
    ]
  }, 
  "Juvenile Fiction / Nature & The Natural World / Environment": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Nature & The Natural World / Environment", 
    "notation": "JUV029010", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Fashion": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Fashion", 
    "notation": "CRA009000", 
    "alt_label": []
  }, 
  "Poetry / Subjects & Themes / Love": {
    "related": [], 
    "pref_label": "Poetry / Subjects & Themes / Love", 
    "notation": "POE023020", 
    "alt_label": []
  }, 
  "Science / Mechanics / Aerodynamics": {
    "related": [], 
    "pref_label": "Science / Mechanics / Aerodynamics", 
    "notation": "SCI084000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Reference / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Reference / General", 
    "notation": "JNF048000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Cooking & Food": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Cooking & Food", 
    "notation": "JNF014000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Roller & In-line Skating": {
    "related": [], 
    "pref_label": "Sports & Recreation / Roller & In-line Skating", 
    "notation": "SPO034000", 
    "alt_label": [
      "Sports & Recreation / In-line Skating"
    ]
  }, 
  "Religion / Christian Ministry / Adult": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / Adult", 
    "notation": "REL109010", 
    "alt_label": []
  }, 
  "Bibles / Reina Valera / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / Reina Valera / Youth & Teen", 
    "notation": "BIB019070", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Horror": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Horror", 
    "notation": "CGN004040", 
    "alt_label": []
  }, 
  "Health & Fitness / Work-related Health": {
    "related": [], 
    "pref_label": "Health & Fitness / Work-related Health", 
    "notation": "HEA038000", 
    "alt_label": []
  }, 
  "Business & Economics / Personal Success": {
    "related": [], 
    "pref_label": "Business & Economics / Personal Success", 
    "notation": "BUS107000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Gay & Lesbian": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Gay & Lesbian", 
    "notation": "CGN009000", 
    "alt_label": []
  }, 
  "Political Science / Colonialism & Post-colonialism": {
    "related": [], 
    "pref_label": "Political Science / Colonialism & Post-colonialism", 
    "notation": "POL045000", 
    "alt_label": []
  }, 
  "Political Science / International Relations / General": {
    "related": [], 
    "pref_label": "Political Science / International Relations / General", 
    "notation": "POL011000", 
    "alt_label": []
  }, 
  "Philosophy / Epistemology": {
    "related": [], 
    "pref_label": "Philosophy / Epistemology", 
    "notation": "PHI004000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Stamps": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Stamps", 
    "notation": "ANT044000", 
    "alt_label": []
  }, 
  "Education / Professional Development": {
    "related": [], 
    "pref_label": "Education / Professional Development", 
    "notation": "EDU046000", 
    "alt_label": []
  }, 
  "Medical / Nursing / General": {
    "related": [], 
    "pref_label": "Medical / Nursing / General", 
    "notation": "MED058000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Military & Wars": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Military & Wars", 
    "notation": "JUV016080", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / African": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / African", 
    "notation": "CKB001000", 
    "alt_label": []
  }, 
  "Psychology / Movements / Behaviorism": {
    "related": [], 
    "pref_label": "Psychology / Movements / Behaviorism", 
    "notation": "PSY045010", 
    "alt_label": []
  }, 
  "Games / Gambling / Table": {
    "related": [], 
    "pref_label": "Games / Gambling / Table", 
    "notation": "GAM004030", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Canada / Post-confederation (1867-)": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Canada / Post-confederation (1867-)", 
    "notation": "JUV016180", 
    "alt_label": []
  }, 
  "Computers / Programming / Games": {
    "related": [], 
    "pref_label": "Computers / Programming / Games", 
    "notation": "COM012040", 
    "alt_label": []
  }, 
  "Travel / South America / Peru": {
    "related": [], 
    "pref_label": "Travel / South America / Peru", 
    "notation": "TRV024050", 
    "alt_label": []
  }, 
  "Nature / Seashells": {
    "related": [], 
    "pref_label": "Nature / Seashells", 
    "notation": "NAT031000", 
    "alt_label": []
  }, 
  "Music / Printed Music / Artist Specific": {
    "related": [], 
    "pref_label": "Music / Printed Music / Artist Specific", 
    "notation": "MUS037010", 
    "alt_label": []
  }, 
  "Family & Relationships / Peer Pressure": {
    "related": [], 
    "pref_label": "Family & Relationships / Peer Pressure", 
    "notation": "FAM035000", 
    "alt_label": []
  }, 
  "Bibles / The Message / Text": {
    "related": [], 
    "pref_label": "Bibles / The Message / Text", 
    "notation": "BIB020060", 
    "alt_label": []
  }, 
  "Art / Techniques / Watercolor Painting": {
    "related": [], 
    "pref_label": "Art / Techniques / Watercolor Painting", 
    "notation": "ART029000", 
    "alt_label": []
  }, 
  "Study Aids / Clep (college-level Examination Program)": {
    "related": [], 
    "pref_label": "Study Aids / Clep (college-level Examination Program)", 
    "notation": "STU008000", 
    "alt_label": []
  }, 
  "Law / Housing & Urban Development": {
    "related": [], 
    "pref_label": "Law / Housing & Urban Development", 
    "notation": "LAW047000", 
    "alt_label": [
      "Law / Urban Development"
    ]
  }, 
  "Humor / Topic / Adult": {
    "related": [], 
    "pref_label": "Humor / Topic / Adult", 
    "notation": "HUM008000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Journalism": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Journalism", 
    "notation": "LAN008000", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Women's Issues": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Women's Issues", 
    "notation": "REL012130", 
    "alt_label": []
  }, 
  "Foreign Language Study / Vietnamese": {
    "related": [], 
    "pref_label": "Foreign Language Study / Vietnamese", 
    "notation": "FOR044000", 
    "alt_label": []
  }, 
  "History / Middle East / General": {
    "related": [], 
    "pref_label": "History / Middle East / General", 
    "notation": "HIS026000", 
    "alt_label": []
  }, 
  "Law / Constitutional": {
    "related": [], 
    "pref_label": "Law / Constitutional", 
    "notation": "LAW018000", 
    "alt_label": []
  }, 
  "History / Military / Special Forces": {
    "related": [], 
    "pref_label": "History / Military / Special Forces", 
    "notation": "HIS027180", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Pets": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Pets", 
    "notation": "JNF003170", 
    "alt_label": [
      "Juvenile Nonfiction / Pets"
    ]
  }, 
  "Juvenile Fiction / Historical / Renaissance": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Renaissance", 
    "notation": "JUV016100", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Environmental Conservation & Protection": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Environmental Conservation & Protection", 
    "notation": "JNF037020", 
    "alt_label": []
  }, 
  "Music / Reference": {
    "related": [], 
    "pref_label": "Music / Reference", 
    "notation": "MUS033000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Equestrian": {
    "related": [], 
    "pref_label": "Sports & Recreation / Equestrian", 
    "notation": "SPO057000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Biblical Biography": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Biblical Biography", 
    "notation": "JNF049020", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Asian": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Asian", 
    "notation": "CKB090000", 
    "alt_label": []
  }, 
  "Literary Criticism / Asian / Indic": {
    "related": [], 
    "pref_label": "Literary Criticism / Asian / Indic", 
    "notation": "LIT008020", 
    "alt_label": []
  }, 
  "Education / Special Education / Communicative Disorders": {
    "related": [], 
    "pref_label": "Education / Special Education / Communicative Disorders", 
    "notation": "EDU026010", 
    "alt_label": []
  }, 
  "Cooking / Holiday": {
    "related": [], 
    "pref_label": "Cooking / Holiday", 
    "notation": "CKB042000", 
    "alt_label": []
  }, 
  "Political Science / Ngos (non-governmental Organizations)": {
    "related": [], 
    "pref_label": "Political Science / Ngos (non-governmental Organizations)", 
    "notation": "POL041000", 
    "alt_label": []
  }, 
  "Fiction / Alternative History": {
    "related": [], 
    "pref_label": "Fiction / Alternative History", 
    "notation": "FIC040000", 
    "alt_label": [
      "Fiction / Science Fiction / Alternative History"
    ]
  }, 
  "Science / Physics / Polymer": {
    "related": [], 
    "pref_label": "Science / Physics / Polymer", 
    "notation": "SCI097000", 
    "alt_label": []
  }, 
  "Law / Estates & Trusts": {
    "related": [], 
    "pref_label": "Law / Estates & Trusts", 
    "notation": "LAW035000", 
    "alt_label": []
  }, 
  "Law / Environmental": {
    "related": [], 
    "pref_label": "Law / Environmental", 
    "notation": "LAW034000", 
    "alt_label": []
  }, 
  "Travel / Special Interest / General": {
    "related": [], 
    "pref_label": "Travel / Special Interest / General", 
    "notation": "TRV026000", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Marine Biology": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Marine Biology", 
    "notation": "SCI039000", 
    "alt_label": []
  }, 
  "Bibles / Other Translations / Study": {
    "related": [], 
    "pref_label": "Bibles / Other Translations / Study", 
    "notation": "BIB018050", 
    "alt_label": []
  }, 
  "Law / Intellectual Property / General": {
    "related": [], 
    "pref_label": "Law / Intellectual Property / General", 
    "notation": "LAW050000", 
    "alt_label": []
  }, 
  "Study Aids / Citizenship": {
    "related": [], 
    "pref_label": "Study Aids / Citizenship", 
    "notation": "STU006000", 
    "alt_label": []
  }, 
  "Humor / Topic / Sports": {
    "related": [], 
    "pref_label": "Humor / Topic / Sports", 
    "notation": "HUM013000", 
    "alt_label": []
  }, 
  "Philosophy / Religious": {
    "related": [], 
    "pref_label": "Philosophy / Religious", 
    "notation": "PHI022000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Construction / Heating, Ventilation & Air Conditioning": {
    "related": [], 
    "pref_label": "Technology & Engineering / Construction / Heating, Ventilation & Air Conditioning", 
    "notation": "TEC005050", 
    "alt_label": []
  }, 
  "Technology & Engineering / Civil / Dams & Reservoirs": {
    "related": [], 
    "pref_label": "Technology & Engineering / Civil / Dams & Reservoirs", 
    "notation": "TEC009110", 
    "alt_label": []
  }, 
  "Business & Economics / Taxation / Corporate": {
    "related": [], 
    "pref_label": "Business & Economics / Taxation / Corporate", 
    "notation": "BUS064010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Canada / Native Canadian": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Canada / Native Canadian", 
    "notation": "JNF038120", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Technology / How Things Work-are Made": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Technology / How Things Work-are Made", 
    "notation": "JNF051120", 
    "alt_label": []
  }, 
  "Medical / Emergency Medicine": {
    "related": [], 
    "pref_label": "Medical / Emergency Medicine", 
    "notation": "MED026000", 
    "alt_label": []
  }, 
  "Self-help / Personal Growth / Happiness": {
    "related": [], 
    "pref_label": "Self-help / Personal Growth / Happiness", 
    "notation": "SEL016000", 
    "alt_label": []
  }, 
  "Computers / Security / Viruses": {
    "related": [], 
    "pref_label": "Computers / Security / Viruses", 
    "notation": "COM015000", 
    "alt_label": [
      "Computers / Computer Viruses", 
      "Computers / Viruses"
    ]
  }, 
  "Juvenile Nonfiction / Family / Stepfamilies": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Family / Stepfamilies", 
    "notation": "JNF019080", 
    "alt_label": []
  }, 
  "Psychology / Experimental Psychology": {
    "related": [], 
    "pref_label": "Psychology / Experimental Psychology", 
    "notation": "PSY040000", 
    "alt_label": []
  }, 
  "Medical / Toxicology": {
    "related": [], 
    "pref_label": "Medical / Toxicology", 
    "notation": "MED096000", 
    "alt_label": []
  }, 
  "Performing Arts / Dance / Tap": {
    "related": [], 
    "pref_label": "Performing Arts / Dance / Tap", 
    "notation": "PER003080", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Evolution": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Evolution", 
    "notation": "SCI027000", 
    "alt_label": []
  }, 
  "Medical / Surgery / General": {
    "related": [], 
    "pref_label": "Medical / Surgery / General", 
    "notation": "MED085000", 
    "alt_label": []
  }, 
  "Medical / Veterinary Medicine / Food Animal": {
    "related": [], 
    "pref_label": "Medical / Veterinary Medicine / Food Animal", 
    "notation": "MED089020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Technology / Electricity & Electronics": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Technology / Electricity & Electronics", 
    "notation": "JNF051090", 
    "alt_label": []
  }, 
  "Bibles / New Living Translation / Reference": {
    "related": [], 
    "pref_label": "Bibles / New Living Translation / Reference", 
    "notation": "BIB015040", 
    "alt_label": []
  }, 
  "Performing Arts / Theater / Direction & Production": {
    "related": [], 
    "pref_label": "Performing Arts / Theater / Direction & Production", 
    "notation": "PER011010", 
    "alt_label": []
  }, 
  "History / Military / Korean War": {
    "related": [], 
    "pref_label": "History / Military / Korean War", 
    "notation": "HIS027020", 
    "alt_label": []
  }, 
  "Psychology / Developmental / General": {
    "related": [], 
    "pref_label": "Psychology / Developmental / General", 
    "notation": "PSY039000", 
    "alt_label": []
  }, 
  "Gardening / Regional / New England (ct, Ma, Me, Nh, Ri, Vt)": {
    "related": [], 
    "pref_label": "Gardening / Regional / New England (ct, Ma, Me, Nh, Ri, Vt)", 
    "notation": "GAR019040", 
    "alt_label": []
  }, 
  "Psychology / Psychotherapy / Group": {
    "related": [], 
    "pref_label": "Psychology / Psychotherapy / Group", 
    "notation": "PSY048000", 
    "alt_label": []
  }, 
  "History / United States / 21st Century": {
    "related": [], 
    "pref_label": "History / United States / 21st Century", 
    "notation": "HIS036070", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Rhetoric": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Rhetoric", 
    "notation": "LAN015000", 
    "alt_label": []
  }, 
  "Fiction / Thrillers": {
    "related": [], 
    "pref_label": "Fiction / Thrillers", 
    "notation": "FIC031000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Prophecy": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Prophecy", 
    "notation": "OCC020000", 
    "alt_label": []
  }, 
  "Psychology / Developmental / Adolescent": {
    "related": [], 
    "pref_label": "Psychology / Developmental / Adolescent", 
    "notation": "PSY002000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Seasons": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Seasons", 
    "notation": "JNF013090", 
    "alt_label": []
  }, 
  "Political Science / International Relations / Diplomacy": {
    "related": [], 
    "pref_label": "Political Science / International Relations / Diplomacy", 
    "notation": "POL011010", 
    "alt_label": []
  }, 
  "Psychology / Statistics": {
    "related": [], 
    "pref_label": "Psychology / Statistics", 
    "notation": "PSY032000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Skin": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Skin", 
    "notation": "HEA039130", 
    "alt_label": []
  }, 
  "Computers / Hardware / Peripherals": {
    "related": [], 
    "pref_label": "Computers / Hardware / Peripherals", 
    "notation": "COM049000", 
    "alt_label": [
      "Computers / Peripherals"
    ]
  }, 
  "Computers / Documentation & Technical Writing": {
    "related": [], 
    "pref_label": "Computers / Documentation & Technical Writing", 
    "notation": "COM085000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Emotions & Feelings": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Emotions & Feelings", 
    "notation": "JUV033090", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Readers": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Readers", 
    "notation": "LAN012000", 
    "alt_label": []
  }, 
  "Medical / Dentistry / Oral Surgery": {
    "related": [], 
    "pref_label": "Medical / Dentistry / Oral Surgery", 
    "notation": "MED016050", 
    "alt_label": []
  }, 
  "Bibles / La Biblia De Las Americas / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / La Biblia De Las Americas / Youth & Teen", 
    "notation": "BIB007070", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Toilet Training": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Toilet Training", 
    "notation": "JNF024110", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Hippos & Rhinos": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Hippos & Rhinos", 
    "notation": "JNF003290", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Middle East": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Middle East", 
    "notation": "JUV016210", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Prehistoric": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Prehistoric", 
    "notation": "JNF025150", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Health & Daily Living / Daily Activities": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Health & Daily Living / Daily Activities", 
    "notation": "JUV015010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Money": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Money", 
    "notation": "JNF013040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / General", 
    "notation": "JUV002000", 
    "alt_label": []
  }, 
  "Law / Mental Health": {
    "related": [], 
    "pref_label": "Law / Mental Health", 
    "notation": "LAW067000", 
    "alt_label": []
  }, 
  "Literary Criticism / European / English, Irish, Scottish, Welsh": {
    "related": [], 
    "pref_label": "Literary Criticism / European / English, Irish, Scottish, Welsh", 
    "notation": "LIT004120", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / Canada / Native Canadian": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Canada / Native Canadian", 
    "notation": "JUV030090", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Empiricism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Empiricism", 
    "notation": "PHI041000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / New Age": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / New Age", 
    "notation": "MUS027000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Other": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Other", 
    "notation": "JNF038110", 
    "alt_label": []
  }, 
  "Social Science / Black Studies (global)": {
    "related": [], 
    "pref_label": "Social Science / Black Studies (global)", 
    "notation": "SOC056000", 
    "alt_label": []
  }, 
  "Gardening / Fruit": {
    "related": [], 
    "pref_label": "Gardening / Fruit", 
    "notation": "GAR005000", 
    "alt_label": []
  }, 
  "Fiction / Urban Life": {
    "related": [], 
    "pref_label": "Fiction / Urban Life", 
    "notation": "FIC048000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Comics": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Comics", 
    "notation": "ANT012000", 
    "alt_label": []
  }, 
  "Art / Techniques / Cartooning": {
    "related": [], 
    "pref_label": "Art / Techniques / Cartooning", 
    "notation": "ART004000", 
    "alt_label": []
  }, 
  "Architecture / History / Renaissance": {
    "related": [], 
    "pref_label": "Architecture / History / Renaissance", 
    "notation": "ARC005040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Medieval": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Medieval", 
    "notation": "JUV016070", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Military & Wars": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Military & Wars", 
    "notation": "JNF025130", 
    "alt_label": []
  }, 
  "Bibles / New Revised Standard Version / Children": {
    "related": [], 
    "pref_label": "Bibles / New Revised Standard Version / Children", 
    "notation": "BIB016010", 
    "alt_label": []
  }, 
  "Travel / Polar Regions": {
    "related": [], 
    "pref_label": "Travel / Polar Regions", 
    "notation": "TRV020000", 
    "alt_label": [
      "Travel / Antarctica"
    ]
  }, 
  "Mathematics / Linear & Nonlinear Programming": {
    "related": [], 
    "pref_label": "Mathematics / Linear & Nonlinear Programming", 
    "notation": "MAT017000", 
    "alt_label": []
  }, 
  "Bibles / New American Bible / Devotional": {
    "related": [], 
    "pref_label": "Bibles / New American Bible / Devotional", 
    "notation": "BIB009020", 
    "alt_label": []
  }, 
  "Foreign Language Study / Swedish": {
    "related": [], 
    "pref_label": "Foreign Language Study / Swedish", 
    "notation": "FOR043000", 
    "alt_label": []
  }, 
  "History / Europe / Baltic States": {
    "related": [], 
    "pref_label": "History / Europe / Baltic States", 
    "notation": "HIS005000", 
    "alt_label": []
  }, 
  "Cooking / Methods / Canning & Preserving": {
    "related": [], 
    "pref_label": "Cooking / Methods / Canning & Preserving", 
    "notation": "CKB015000", 
    "alt_label": []
  }, 
  "Political Science / Political Process / Leadership": {
    "related": [], 
    "pref_label": "Political Science / Political Process / Leadership", 
    "notation": "POL025000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Numerology": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Numerology", 
    "notation": "OCC015000", 
    "alt_label": []
  }, 
  "Family & Relationships / Siblings": {
    "related": [], 
    "pref_label": "Family & Relationships / Siblings", 
    "notation": "FAM041000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Relationships": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Relationships", 
    "notation": "JUV033200", 
    "alt_label": []
  }, 
  "Sports & Recreation / Skiing": {
    "related": [], 
    "pref_label": "Sports & Recreation / Skiing", 
    "notation": "SPO039000", 
    "alt_label": []
  }, 
  "Social Science / General": {
    "related": [], 
    "pref_label": "Social Science / General", 
    "notation": "SOC000000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Computers / Entertainment & Games": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Computers / Entertainment & Games", 
    "notation": "JNF012010", 
    "alt_label": []
  }, 
  "Business & Economics / Training": {
    "related": [], 
    "pref_label": "Business & Economics / Training", 
    "notation": "BUS066000", 
    "alt_label": []
  }, 
  "Photography / Collections, Catalogs, Exhibitions / Group Shows": {
    "related": [], 
    "pref_label": "Photography / Collections, Catalogs, Exhibitions / Group Shows", 
    "notation": "PHO004010", 
    "alt_label": []
  }, 
  "Religion / Hinduism / Theology": {
    "related": [], 
    "pref_label": "Religion / Hinduism / Theology", 
    "notation": "REL032040", 
    "alt_label": []
  }, 
  "Political Science / Political Ideologies / Conservatism & Liberalism": {
    "related": [], 
    "pref_label": "Political Science / Political Ideologies / Conservatism & Liberalism", 
    "notation": "POL042020", 
    "alt_label": []
  }, 
  "Transportation / Aviation / Repair & Maintenance": {
    "related": [], 
    "pref_label": "Transportation / Aviation / Repair & Maintenance", 
    "notation": "TRA002030", 
    "alt_label": []
  }, 
  "Architecture / Buildings / General": {
    "related": [], 
    "pref_label": "Architecture / Buildings / General", 
    "notation": "ARC024000", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Dissociative Identity Disorder": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Dissociative Identity Disorder", 
    "notation": "PSY022070", 
    "alt_label": []
  }, 
  "Mathematics / Algebra / General": {
    "related": [], 
    "pref_label": "Mathematics / Algebra / General", 
    "notation": "MAT002000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Poetry / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Poetry / General", 
    "notation": "JNF042000", 
    "alt_label": []
  }, 
  "Literary Collections / Asian / General": {
    "related": [], 
    "pref_label": "Literary Collections / Asian / General", 
    "notation": "LCO004000", 
    "alt_label": []
  }, 
  "Religion / Judaism / Orthodox": {
    "related": [], 
    "pref_label": "Religion / Judaism / Orthodox", 
    "notation": "REL040070", 
    "alt_label": []
  }, 
  "Education / Collaborative & Team Teaching": {
    "related": [], 
    "pref_label": "Education / Collaborative & Team Teaching", 
    "notation": "EDU050000", 
    "alt_label": []
  }, 
  "Cooking / Beverages / Bartending": {
    "related": [], 
    "pref_label": "Cooking / Beverages / Bartending", 
    "notation": "CKB006000", 
    "alt_label": []
  }, 
  "Computers / Software Development & Engineering / General": {
    "related": [], 
    "pref_label": "Computers / Software Development & Engineering / General", 
    "notation": "COM051230", 
    "alt_label": []
  }, 
  "Computers / Reference": {
    "related": [], 
    "pref_label": "Computers / Reference", 
    "notation": "COM052000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Legends, Myths, Fables / Other": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Legends, Myths, Fables / Other", 
    "notation": "JUV022040", 
    "alt_label": []
  }, 
  "Technology & Engineering / Radio": {
    "related": [], 
    "pref_label": "Technology & Engineering / Radio", 
    "notation": "TEC034000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Editors, Journalists, Publishers": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Editors, Journalists, Publishers", 
    "notation": "BIO025000", 
    "alt_label": []
  }, 
  "Music / Musical Instruments / Woodwinds": {
    "related": [], 
    "pref_label": "Music / Musical Instruments / Woodwinds", 
    "notation": "MUS023050", 
    "alt_label": []
  }, 
  "Transportation / Railroads / History": {
    "related": [], 
    "pref_label": "Transportation / Railroads / History", 
    "notation": "TRA004010", 
    "alt_label": []
  }, 
  "Humor / Topic / Relationships": {
    "related": [], 
    "pref_label": "Humor / Topic / Relationships", 
    "notation": "HUM012000", 
    "alt_label": []
  }, 
  "Religion / Institutions & Organizations": {
    "related": [], 
    "pref_label": "Religion / Institutions & Organizations", 
    "notation": "REL016000", 
    "alt_label": [
      "Religion / Church Institutions & Organizations"
    ]
  }, 
  "Bibles / New International Version / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / New International Version / Youth & Teen", 
    "notation": "BIB013070", 
    "alt_label": []
  }, 
  "Bibles / English Standard Version / Devotional": {
    "related": [], 
    "pref_label": "Bibles / English Standard Version / Devotional", 
    "notation": "BIB003020", 
    "alt_label": []
  }, 
  "Bibles / Other Translations / Children": {
    "related": [], 
    "pref_label": "Bibles / Other Translations / Children", 
    "notation": "BIB018010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Family / Alternative Family": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Family / Alternative Family", 
    "notation": "JUV013090", 
    "alt_label": []
  }, 
  "Literary Collections / General": {
    "related": [], 
    "pref_label": "Literary Collections / General", 
    "notation": "LCO000000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Air Sports": {
    "related": [], 
    "pref_label": "Sports & Recreation / Air Sports", 
    "notation": "SPO001000", 
    "alt_label": []
  }, 
  "Computers / Management Information Systems": {
    "related": [], 
    "pref_label": "Computers / Management Information Systems", 
    "notation": "COM039000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Holidays & Celebrations / Christmas & Advent": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Holidays & Celebrations / Christmas & Advent", 
    "notation": "JNF026010", 
    "alt_label": []
  }, 
  "Computers / Enterprise Applications / Business Intelligence Tools": {
    "related": [], 
    "pref_label": "Computers / Enterprise Applications / Business Intelligence Tools", 
    "notation": "COM005030", 
    "alt_label": [
      "Computers / Business Software"
    ]
  }, 
  "Sports & Recreation / Winter Sports": {
    "related": [], 
    "pref_label": "Sports & Recreation / Winter Sports", 
    "notation": "SPO052000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Social Issues": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Social Issues", 
    "notation": "JUV033220", 
    "alt_label": []
  }, 
  "Religion / Biblical Reference / Quotations": {
    "related": [], 
    "pref_label": "Religion / Biblical Reference / Quotations", 
    "notation": "REL006150", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Daily Activities": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Daily Activities", 
    "notation": "JNF024120", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Law Enforcement": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Law Enforcement", 
    "notation": "BIO027000", 
    "alt_label": []
  }, 
  "House & Home / Do-it-yourself / Electrical": {
    "related": [], 
    "pref_label": "House & Home / Do-it-yourself / Electrical", 
    "notation": "HOM006000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Mammals": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Mammals", 
    "notation": "JUV002160", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Parapsychology / Near-death Experience": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Parapsychology / Near-death Experience", 
    "notation": "OCC034000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Chamber": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Chamber", 
    "notation": "MUS005000", 
    "alt_label": []
  }, 
  "Humor / Topic / Religion": {
    "related": [], 
    "pref_label": "Humor / Topic / Religion", 
    "notation": "HUM014000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Greek": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Greek", 
    "notation": "CKB038000", 
    "alt_label": []
  }, 
  "Mathematics / Numerical Analysis": {
    "related": [], 
    "pref_label": "Mathematics / Numerical Analysis", 
    "notation": "MAT041000", 
    "alt_label": []
  }, 
  "Political Science / American Government / Local": {
    "related": [], 
    "pref_label": "Political Science / American Government / Local", 
    "notation": "POL040040", 
    "alt_label": [
      "Political Science / State & Local Government"
    ]
  }, 
  "Religion / Biblical Reference / General": {
    "related": [], 
    "pref_label": "Religion / Biblical Reference / General", 
    "notation": "REL006160", 
    "alt_label": []
  }, 
  "Political Science / Political Process / Elections": {
    "related": [], 
    "pref_label": "Political Science / Political Process / Elections", 
    "notation": "POL008000", 
    "alt_label": []
  }, 
  "Music / Printed Music / Choral": {
    "related": [], 
    "pref_label": "Music / Printed Music / Choral", 
    "notation": "MUS037030", 
    "alt_label": []
  }, 
  "Fiction / African American / Contemporary Women": {
    "related": [], 
    "pref_label": "Fiction / African American / Contemporary Women", 
    "notation": "FIC049020", 
    "alt_label": []
  }, 
  "Transportation / Navigation": {
    "related": [], 
    "pref_label": "Transportation / Navigation", 
    "notation": "TRA008000", 
    "alt_label": []
  }, 
  "Bibles / Contemporary English Version / Children": {
    "related": [], 
    "pref_label": "Bibles / Contemporary English Version / Children", 
    "notation": "BIB002010", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Compulsive Behavior": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Compulsive Behavior", 
    "notation": "PSY009000", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Pets": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Pets", 
    "notation": "TRV026040", 
    "alt_label": []
  }, 
  "Foreign Language Study / Persian": {
    "related": [], 
    "pref_label": "Foreign Language Study / Persian", 
    "notation": "FOR040000", 
    "alt_label": []
  }, 
  "Fiction / African American / Christian": {
    "related": [], 
    "pref_label": "Fiction / African American / Christian", 
    "notation": "FIC049010", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Respiratory": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Respiratory", 
    "notation": "HEA039120", 
    "alt_label": []
  }, 
  "Bibles / Christian Standard Bible / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / Christian Standard Bible / New Testament & Portions", 
    "notation": "BIB001030", 
    "alt_label": []
  }, 
  "Sports & Recreation / Bowling": {
    "related": [], 
    "pref_label": "Sports & Recreation / Bowling", 
    "notation": "SPO007000", 
    "alt_label": []
  }, 
  "Mathematics / Study & Teaching": {
    "related": [], 
    "pref_label": "Mathematics / Study & Teaching", 
    "notation": "MAT030000", 
    "alt_label": []
  }, 
  "Law / Land Use": {
    "related": [], 
    "pref_label": "Law / Land Use", 
    "notation": "LAW055000", 
    "alt_label": []
  }, 
  "Business & Economics / Economics / Comparative": {
    "related": [], 
    "pref_label": "Business & Economics / Economics / Comparative", 
    "notation": "BUS069010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Family / Multigenerational": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Family / Multigenerational", 
    "notation": "JNF019030", 
    "alt_label": []
  }, 
  "Transportation / General": {
    "related": [], 
    "pref_label": "Transportation / General", 
    "notation": "TRA000000", 
    "alt_label": []
  }, 
  "Poetry / Subjects & Themes / Nature": {
    "related": [], 
    "pref_label": "Poetry / Subjects & Themes / Nature", 
    "notation": "POE023030", 
    "alt_label": []
  }, 
  "Design / Graphic Arts / General": {
    "related": [], 
    "pref_label": "Design / Graphic Arts / General", 
    "notation": "DES007000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Football": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Football", 
    "notation": "JNF054050", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Marine Life": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Marine Life", 
    "notation": "JNF003150", 
    "alt_label": []
  }, 
  "Computers / Programming / Parallel": {
    "related": [], 
    "pref_label": "Computers / Programming / Parallel", 
    "notation": "COM051220", 
    "alt_label": []
  }, 
  "Performing Arts / Television / Guides & Reviews": {
    "related": [], 
    "pref_label": "Performing Arts / Television / Guides & Reviews", 
    "notation": "PER010020", 
    "alt_label": []
  }, 
  "Computers / Operating Systems / Windows Server & Nt": {
    "related": [], 
    "pref_label": "Computers / Operating Systems / Windows Server & Nt", 
    "notation": "COM046050", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Romance": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Romance", 
    "notation": "CGN004180", 
    "alt_label": []
  }, 
  "Art / History / Modern (late 19th Century To 1945)": {
    "related": [], 
    "pref_label": "Art / History / Modern (late 19th Century To 1945)", 
    "notation": "ART015100", 
    "alt_label": []
  }, 
  "Bibles / The Message / Devotional": {
    "related": [], 
    "pref_label": "Bibles / The Message / Devotional", 
    "notation": "BIB020020", 
    "alt_label": []
  }, 
  "Cooking / Methods / Microwave": {
    "related": [], 
    "pref_label": "Cooking / Methods / Microwave", 
    "notation": "CKB057000", 
    "alt_label": []
  }, 
  "Travel / United States / General": {
    "related": [], 
    "pref_label": "Travel / United States / General", 
    "notation": "TRV025000", 
    "alt_label": []
  }, 
  "Political Science / Political Ideologies / Fascism & Totalitarianism": {
    "related": [], 
    "pref_label": "Political Science / Political Ideologies / Fascism & Totalitarianism", 
    "notation": "POL042030", 
    "alt_label": []
  }, 
  "Religion / Philosophy": {
    "related": [], 
    "pref_label": "Religion / Philosophy", 
    "notation": "REL051000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Indic Languages": {
    "related": [], 
    "pref_label": "Foreign Language Study / Indic Languages", 
    "notation": "FOR030000", 
    "alt_label": []
  }, 
  "Poetry / Anthologies (multiple Authors)": {
    "related": [], 
    "pref_label": "Poetry / Anthologies (multiple Authors)", 
    "notation": "POE001000", 
    "alt_label": []
  }, 
  "Music / Instruction & Study / Techniques": {
    "related": [], 
    "pref_label": "Music / Instruction & Study / Techniques", 
    "notation": "MUS040000", 
    "alt_label": []
  }, 
  "Performing Arts / Theater / Stagecraft": {
    "related": [], 
    "pref_label": "Performing Arts / Theater / Stagecraft", 
    "notation": "PER011040", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Inspirational": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Inspirational", 
    "notation": "REL012040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Violence": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Violence", 
    "notation": "JNF053210", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / School & Education": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / School & Education", 
    "notation": "JNF050000", 
    "alt_label": [
      "Juvenile Nonfiction / Education"
    ]
  }, 
  "Games / Checkers": {
    "related": [], 
    "pref_label": "Games / Checkers", 
    "notation": "GAM001020", 
    "alt_label": [
      "Games / Board / Checkers"
    ]
  }, 
  "Sports & Recreation / Coaching / General": {
    "related": [], 
    "pref_label": "Sports & Recreation / Coaching / General", 
    "notation": "SPO061000", 
    "alt_label": []
  }, 
  "Bibles / English Standard Version / Reference": {
    "related": [], 
    "pref_label": "Bibles / English Standard Version / Reference", 
    "notation": "BIB003040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Hockey": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Hockey", 
    "notation": "JNF054070", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Aerial": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Aerial", 
    "notation": "PHO023010", 
    "alt_label": []
  }, 
  "Medical / Genetics": {
    "related": [], 
    "pref_label": "Medical / Genetics", 
    "notation": "MED107000", 
    "alt_label": [
      "Medical / Diseases / Genetic"
    ]
  }, 
  "Business & Economics / Industries / Fashion & Textile Industry": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Fashion & Textile Industry", 
    "notation": "BUS070090", 
    "alt_label": []
  }, 
  "Health & Fitness / Beauty & Grooming": {
    "related": [], 
    "pref_label": "Health & Fitness / Beauty & Grooming", 
    "notation": "HEA003000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Native American Languages": {
    "related": [], 
    "pref_label": "Foreign Language Study / Native American Languages", 
    "notation": "FOR031000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Polo": {
    "related": [], 
    "pref_label": "Sports & Recreation / Polo", 
    "notation": "SPO055000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Cajun & Creole": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Cajun & Creole", 
    "notation": "CKB013000", 
    "alt_label": [
      "Cooking / Regional & Ethnic / Creole"
    ]
  }, 
  "Social Science / Sexual Abuse & Harassment": {
    "related": [], 
    "pref_label": "Social Science / Sexual Abuse & Harassment", 
    "notation": "SOC060000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Arabic": {
    "related": [], 
    "pref_label": "Foreign Language Study / Arabic", 
    "notation": "FOR002000", 
    "alt_label": []
  }, 
  "Medical / Dermatology": {
    "related": [], 
    "pref_label": "Medical / Dermatology", 
    "notation": "MED017000", 
    "alt_label": [
      "Medical / Diseases / Cutaneous"
    ]
  }, 
  "Bibles / New American Standard Bible / Reference": {
    "related": [], 
    "pref_label": "Bibles / New American Standard Bible / Reference", 
    "notation": "BIB010040", 
    "alt_label": []
  }, 
  "Religion / Islam / Koran & Sacred Writings": {
    "related": [], 
    "pref_label": "Religion / Islam / Koran & Sacred Writings", 
    "notation": "REL041000", 
    "alt_label": [
      "Religion / Koran"
    ]
  }, 
  "Sports & Recreation / Water Sports": {
    "related": [], 
    "pref_label": "Sports & Recreation / Water Sports", 
    "notation": "SPO051000", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Breakfast": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Breakfast", 
    "notation": "CKB010000", 
    "alt_label": []
  }, 
  "Humor / Topic / Animals": {
    "related": [], 
    "pref_label": "Humor / Topic / Animals", 
    "notation": "HUM009000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Electronics / Circuits / Vlsi & Ulsi": {
    "related": [], 
    "pref_label": "Technology & Engineering / Electronics / Circuits / Vlsi & Ulsi", 
    "notation": "TEC008050", 
    "alt_label": []
  }, 
  "Medical / Administration": {
    "related": [], 
    "pref_label": "Medical / Administration", 
    "notation": "MED002000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / European": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / European", 
    "notation": "CKB092000", 
    "alt_label": [
      "Cooking / Regional & Ethnic / Eastern European"
    ]
  }, 
  "True Crime / Murder / General": {
    "related": [], 
    "pref_label": "True Crime / Murder / General", 
    "notation": "TRU002000", 
    "alt_label": []
  }, 
  "Photography / Individual Photographers / Monographs": {
    "related": [], 
    "pref_label": "Photography / Individual Photographers / Monographs", 
    "notation": "PHO011030", 
    "alt_label": []
  }, 
  "Art / Subjects & Themes / Landscapes & Seascapes": {
    "related": [], 
    "pref_label": "Art / Subjects & Themes / Landscapes & Seascapes", 
    "notation": "ART050020", 
    "alt_label": []
  }, 
  "Family & Relationships / Parenting / Child Rearing": {
    "related": [], 
    "pref_label": "Family & Relationships / Parenting / Child Rearing", 
    "notation": "FAM010000", 
    "alt_label": []
  }, 
  "Social Science / Conspiracy Theories": {
    "related": [], 
    "pref_label": "Social Science / Conspiracy Theories", 
    "notation": "SOC058000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / Sustainable Agriculture": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / Sustainable Agriculture", 
    "notation": "TEC003070", 
    "alt_label": []
  }, 
  "Medical / Dentistry / General": {
    "related": [], 
    "pref_label": "Medical / Dentistry / General", 
    "notation": "MED016000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Family / Stepfamilies": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Family / Stepfamilies", 
    "notation": "JUV013080", 
    "alt_label": []
  }, 
  "Family & Relationships / Baby Names": {
    "related": [], 
    "pref_label": "Family & Relationships / Baby Names", 
    "notation": "FAM008000", 
    "alt_label": []
  }, 
  "Fiction / Hispanic & Latino": {
    "related": [], 
    "pref_label": "Fiction / Hispanic & Latino", 
    "notation": "FIC05600", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / United States / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / United States / General", 
    "notation": "JUV030060", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Parapsychology / General": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Parapsychology / General", 
    "notation": "OCC018000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Art & Architecture": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Art & Architecture", 
    "notation": "JUV003000", 
    "alt_label": []
  }, 
  "Law / Computer & Internet": {
    "related": [], 
    "pref_label": "Law / Computer & Internet", 
    "notation": "LAW104000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Painting": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Painting", 
    "notation": "CRA024000", 
    "alt_label": []
  }, 
  "Computers / Computer Engineering": {
    "related": [], 
    "pref_label": "Computers / Computer Engineering", 
    "notation": "COM059000", 
    "alt_label": []
  }, 
  "History / Africa / General": {
    "related": [], 
    "pref_label": "History / Africa / General", 
    "notation": "HIS001000", 
    "alt_label": []
  }, 
  "Drama / Religious & Liturgical": {
    "related": [], 
    "pref_label": "Drama / Religious & Liturgical", 
    "notation": "DRA008000", 
    "alt_label": []
  }, 
  "Art / Techniques / Pencil Drawing": {
    "related": [], 
    "pref_label": "Art / Techniques / Pencil Drawing", 
    "notation": "ART034000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Supernatural": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Supernatural", 
    "notation": "OCC023000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Olympics": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Olympics", 
    "notation": "JNF054110", 
    "alt_label": []
  }, 
  "Business & Economics / Economics / Macroeconomics": {
    "related": [], 
    "pref_label": "Business & Economics / Economics / Macroeconomics", 
    "notation": "BUS039000", 
    "alt_label": [
      "Business & Economics / Macroeconomics"
    ]
  }, 
  "Juvenile Fiction / Sports & Recreation / Camping & Outdoor Activities": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Camping & Outdoor Activities", 
    "notation": "JUV032170", 
    "alt_label": []
  }, 
  "Family & Relationships / Parenting / Single Parent": {
    "related": [], 
    "pref_label": "Family & Relationships / Parenting / Single Parent", 
    "notation": "FAM034010", 
    "alt_label": []
  }, 
  "Medical / Medical History & Records": {
    "related": [], 
    "pref_label": "Medical / Medical History & Records", 
    "notation": "MED051000", 
    "alt_label": []
  }, 
  "Fiction / Christian / Suspense": {
    "related": [], 
    "pref_label": "Fiction / Christian / Suspense", 
    "notation": "FIC042060", 
    "alt_label": []
  }, 
  "Health & Fitness / Oral Health": {
    "related": [], 
    "pref_label": "Health & Fitness / Oral Health", 
    "notation": "HEA040000", 
    "alt_label": []
  }, 
  "Art / Techniques / General": {
    "related": [], 
    "pref_label": "Art / Techniques / General", 
    "notation": "ART028000", 
    "alt_label": []
  }, 
  "Religion / Biblical Reference / Dictionaries & Encyclopedias": {
    "related": [], 
    "pref_label": "Religion / Biblical Reference / Dictionaries & Encyclopedias", 
    "notation": "REL006670", 
    "alt_label": []
  }, 
  "Medical / General": {
    "related": [], 
    "pref_label": "Medical / General", 
    "notation": "MED000000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Computer Industry": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Computer Industry", 
    "notation": "BUS070030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Reference / Thesauri": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Reference / Thesauri", 
    "notation": "JNF048050", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / American / Western States": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / American / Western States", 
    "notation": "CKB002080", 
    "alt_label": []
  }, 
  "Law / Wills": {
    "related": [], 
    "pref_label": "Law / Wills", 
    "notation": "LAW090000", 
    "alt_label": []
  }, 
  "Law / Indigenous Peoples": {
    "related": [], 
    "pref_label": "Law / Indigenous Peoples", 
    "notation": "LAW110000", 
    "alt_label": []
  }, 
  "History / Europe / Germany": {
    "related": [], 
    "pref_label": "History / Europe / Germany", 
    "notation": "HIS014000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Homosexuality": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Homosexuality", 
    "notation": "JUV039080", 
    "alt_label": []
  }, 
  "Foreign Language Study / Japanese": {
    "related": [], 
    "pref_label": "Foreign Language Study / Japanese", 
    "notation": "FOR014000", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Polar Regions": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Polar Regions", 
    "notation": "NAT045030", 
    "alt_label": []
  }, 
  "Political Science / World / General": {
    "related": [], 
    "pref_label": "Political Science / World / General", 
    "notation": "POL040020", 
    "alt_label": []
  }, 
  "Religion / Sermons / Christian": {
    "related": [], 
    "pref_label": "Religion / Sermons / Christian", 
    "notation": "REL058010", 
    "alt_label": [
      "Religion / Christianity / Sermons"
    ]
  }, 
  "Antiques & Collectibles / Pottery & Ceramics": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Pottery & Ceramics", 
    "notation": "ANT035000", 
    "alt_label": [
      "Antiques & Collectibles / Ceramics"
    ]
  }, 
  "Architecture / Study & Teaching": {
    "related": [], 
    "pref_label": "Architecture / Study & Teaching", 
    "notation": "ARC013000", 
    "alt_label": []
  }, 
  "Bibles / New International Version / Text": {
    "related": [], 
    "pref_label": "Bibles / New International Version / Text", 
    "notation": "BIB013060", 
    "alt_label": []
  }, 
  "Travel / Africa / South": {
    "related": [], 
    "pref_label": "Travel / Africa / South", 
    "notation": "TRV002070", 
    "alt_label": []
  }, 
  "Architecture / Individual Architects & Firms / Monographs": {
    "related": [], 
    "pref_label": "Architecture / Individual Architects & Firms / Monographs", 
    "notation": "ARC006020", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Popular Culture": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Popular Culture", 
    "notation": "ANT052000", 
    "alt_label": [
      "Antiques & Collectibles / Hummels", 
      "Antiques & Collectibles / Royalty"
    ]
  }, 
  "Travel / United States / Midwest / General": {
    "related": [], 
    "pref_label": "Travel / United States / Midwest / General", 
    "notation": "TRV025010", 
    "alt_label": []
  }, 
  "Religion / Buddhism / Rituals & Practice": {
    "related": [], 
    "pref_label": "Religion / Buddhism / Rituals & Practice", 
    "notation": "REL007020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Manners & Etiquette": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Manners & Etiquette", 
    "notation": "JNF053090", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / United States / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / United States / General", 
    "notation": "JNF025170", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Language Arts / Sign Language": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Language Arts / Sign Language", 
    "notation": "JNF029050", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / General", 
    "notation": "JUV009000", 
    "alt_label": []
  }, 
  "Religion / Essays": {
    "related": [], 
    "pref_label": "Religion / Essays", 
    "notation": "REL113000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Bodybuilding & Weight Training": {
    "related": [], 
    "pref_label": "Sports & Recreation / Bodybuilding & Weight Training", 
    "notation": "SPO006000", 
    "alt_label": [
      "Sports & Recreation / Weight Training"
    ]
  }, 
  "Business & Economics / International / Marketing": {
    "related": [], 
    "pref_label": "Business & Economics / International / Marketing", 
    "notation": "BUS043030", 
    "alt_label": [
      "Business & Economics / Marketing / International"
    ]
  }, 
  "History / Ancient / General": {
    "related": [], 
    "pref_label": "History / Ancient / General", 
    "notation": "HIS002000", 
    "alt_label": []
  }, 
  "History / Modern / 21st Century": {
    "related": [], 
    "pref_label": "History / Modern / 21st Century", 
    "notation": "HIS037080", 
    "alt_label": []
  }, 
  "Religion / Prayer": {
    "related": [], 
    "pref_label": "Religion / Prayer", 
    "notation": "REL087000", 
    "alt_label": []
  }, 
  "Travel / Reference": {
    "related": [], 
    "pref_label": "Travel / Reference", 
    "notation": "TRV021000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Games & Activities / Board Games": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Games & Activities / Board Games", 
    "notation": "JNF021010", 
    "alt_label": []
  }, 
  "Law / Government / Federal": {
    "related": [], 
    "pref_label": "Law / Government / Federal", 
    "notation": "LAW039000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Baseball / Essays & Writings": {
    "related": [], 
    "pref_label": "Sports & Recreation / Baseball / Essays & Writings", 
    "notation": "SPO003020", 
    "alt_label": []
  }, 
  "Reference / Catalogs": {
    "related": [], 
    "pref_label": "Reference / Catalogs", 
    "notation": "REF006000", 
    "alt_label": []
  }, 
  "Drama / Ancient & Classical": {
    "related": [], 
    "pref_label": "Drama / Ancient & Classical", 
    "notation": "DRA006000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Horse Racing": {
    "related": [], 
    "pref_label": "Sports & Recreation / Horse Racing", 
    "notation": "SPO021000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Emigration & Immigration": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Emigration & Immigration", 
    "notation": "JUV039250", 
    "alt_label": []
  }, 
  "Medical / Health Risk Assessment": {
    "related": [], 
    "pref_label": "Medical / Health Risk Assessment", 
    "notation": "MED037000", 
    "alt_label": []
  }, 
  "Bibles / General": {
    "related": [], 
    "pref_label": "Bibles / General", 
    "notation": "BIB000000", 
    "alt_label": []
  }, 
  "Medical / Surgery / Thoracic": {
    "related": [], 
    "pref_label": "Medical / Surgery / Thoracic", 
    "notation": "MED085040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Computers / Software": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Computers / Software", 
    "notation": "JNF012050", 
    "alt_label": []
  }, 
  "Music / Musical Instruments / Percussion": {
    "related": [], 
    "pref_label": "Music / Musical Instruments / Percussion", 
    "notation": "MUS023020", 
    "alt_label": []
  }, 
  "Architecture / History / Romanticism": {
    "related": [], 
    "pref_label": "Architecture / History / Romanticism", 
    "notation": "ARC005060", 
    "alt_label": []
  }, 
  "Art / American / Hispanic American": {
    "related": [], 
    "pref_label": "Art / American / Hispanic American", 
    "notation": "ART040000", 
    "alt_label": []
  }, 
  "Cooking / Health & Healing / Low Fat": {
    "related": [], 
    "pref_label": "Cooking / Health & Healing / Low Fat", 
    "notation": "CKB051000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Reference / Atlases": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Reference / Atlases", 
    "notation": "JNF048020", 
    "alt_label": []
  }, 
  "Travel / Essays & Travelogues": {
    "related": [], 
    "pref_label": "Travel / Essays & Travelogues", 
    "notation": "TRV010000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Alzheimer's & Dementia": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Alzheimer's & Dementia", 
    "notation": "HEA039140", 
    "alt_label": []
  }, 
  "Nature / Animals / Big Cats": {
    "related": [], 
    "pref_label": "Nature / Animals / Big Cats", 
    "notation": "NAT042000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diets": {
    "related": [], 
    "pref_label": "Health & Fitness / Diets", 
    "notation": "HEA006000", 
    "alt_label": []
  }, 
  "Religion / Christian Education / Adult": {
    "related": [], 
    "pref_label": "Religion / Christian Education / Adult", 
    "notation": "REL095000", 
    "alt_label": []
  }, 
  "Social Science / Death & Dying": {
    "related": [], 
    "pref_label": "Social Science / Death & Dying", 
    "notation": "SOC036000", 
    "alt_label": [
      "Social Science / Thanatology"
    ]
  }, 
  "Juvenile Nonfiction / History / Canada / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Canada / General", 
    "notation": "JNF025050", 
    "alt_label": []
  }, 
  "Travel / South America / Ecuador & Galapagos Islands": {
    "related": [], 
    "pref_label": "Travel / South America / Ecuador & Galapagos Islands", 
    "notation": "TRV024040", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / American / Middle Western States": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / American / Middle Western States", 
    "notation": "CKB002030", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Water Sports": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Water Sports", 
    "notation": "JUV032060", 
    "alt_label": []
  }, 
  "Literary Criticism / American / African American": {
    "related": [], 
    "pref_label": "Literary Criticism / American / African American", 
    "notation": "LIT004040", 
    "alt_label": []
  }, 
  "Literary Collections / Caribbean & Latin American": {
    "related": [], 
    "pref_label": "Literary Collections / Caribbean & Latin American", 
    "notation": "LCO007000", 
    "alt_label": []
  }, 
  "Fiction / Jewish": {
    "related": [], 
    "pref_label": "Fiction / Jewish", 
    "notation": "FIC046000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Racket Sports": {
    "related": [], 
    "pref_label": "Sports & Recreation / Racket Sports", 
    "notation": "SPO031000", 
    "alt_label": []
  }, 
  "Computers / Cad-cam": {
    "related": [], 
    "pref_label": "Computers / Cad-cam", 
    "notation": "COM007000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Family / Alternative Family": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Family / Alternative Family", 
    "notation": "JNF019090", 
    "alt_label": []
  }, 
  "Transportation / Ships & Shipbuilding / History": {
    "related": [], 
    "pref_label": "Transportation / Ships & Shipbuilding / History", 
    "notation": "TRA006010", 
    "alt_label": []
  }, 
  "Religion / Christian Education / General": {
    "related": [], 
    "pref_label": "Religion / Christian Education / General", 
    "notation": "REL011000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Cheerleading": {
    "related": [], 
    "pref_label": "Sports & Recreation / Cheerleading", 
    "notation": "SPO070000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Systematic": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Systematic", 
    "notation": "REL067110", 
    "alt_label": [
      "Religion / Christian Theology / Doctrinal"
    ]
  }, 
  "Transportation / Motorcycles / Pictorial": {
    "related": [], 
    "pref_label": "Transportation / Motorcycles / Pictorial", 
    "notation": "TRA003020", 
    "alt_label": []
  }, 
  "Religion / Scientology": {
    "related": [], 
    "pref_label": "Religion / Scientology", 
    "notation": "REL089000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Ada": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Ada", 
    "notation": "COM051020", 
    "alt_label": []
  }, 
  "Nature / Seasons": {
    "related": [], 
    "pref_label": "Nature / Seasons", 
    "notation": "NAT032000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Czech": {
    "related": [], 
    "pref_label": "Foreign Language Study / Czech", 
    "notation": "FOR036000", 
    "alt_label": []
  }, 
  "Fiction / Medical": {
    "related": [], 
    "pref_label": "Fiction / Medical", 
    "notation": "FIC035000", 
    "alt_label": []
  }, 
  "Literary Criticism / Native American": {
    "related": [], 
    "pref_label": "Literary Criticism / Native American", 
    "notation": "LIT004060", 
    "alt_label": []
  }, 
  "Psychology / Physiological Psychology": {
    "related": [], 
    "pref_label": "Psychology / Physiological Psychology", 
    "notation": "PSY024000", 
    "alt_label": []
  }, 
  "Medical / Education & Training": {
    "related": [], 
    "pref_label": "Medical / Education & Training", 
    "notation": "MED024000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Patriotic Holidays": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Patriotic Holidays", 
    "notation": "JUV017130", 
    "alt_label": []
  }, 
  "Technology & Engineering / Acoustics & Sound": {
    "related": [], 
    "pref_label": "Technology & Engineering / Acoustics & Sound", 
    "notation": "TEC001000", 
    "alt_label": [
      "Technology & Engineering / Sound"
    ]
  }, 
  "Law / Family Law / Marriage": {
    "related": [], 
    "pref_label": "Law / Family Law / Marriage", 
    "notation": "LAW038030", 
    "alt_label": [
      "Law / Marriage"
    ]
  }, 
  "Juvenile Fiction / Toys, Dolls, Puppets": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Toys, Dolls, Puppets", 
    "notation": "JUV040000", 
    "alt_label": [
      "Juvenile Fiction / Dolls", 
      "Juvenile Fiction / Puppets"
    ]
  }, 
  "Medical / Anatomy": {
    "related": [], 
    "pref_label": "Medical / Anatomy", 
    "notation": "MED005000", 
    "alt_label": [
      "Medical / Diseases / Neuromuscular"
    ]
  }, 
  "Bibles / New Revised Standard Version / Study": {
    "related": [], 
    "pref_label": "Bibles / New Revised Standard Version / Study", 
    "notation": "BIB016050", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Computers / Hardware": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Computers / Hardware", 
    "notation": "JNF012020", 
    "alt_label": []
  }, 
  "Sports & Recreation / Baseball / General": {
    "related": [], 
    "pref_label": "Sports & Recreation / Baseball / General", 
    "notation": "SPO003000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Language Arts / Composition & Creative Writing": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Language Arts / Composition & Creative Writing", 
    "notation": "JNF029010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Alphabet": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Alphabet", 
    "notation": "JUV009010", 
    "alt_label": []
  }, 
  "Computers / System Administration / Email Administration": {
    "related": [], 
    "pref_label": "Computers / System Administration / Email Administration", 
    "notation": "COM020020", 
    "alt_label": []
  }, 
  "Computers / System Administration / Storage & Retrieval": {
    "related": [], 
    "pref_label": "Computers / System Administration / Storage & Retrieval", 
    "notation": "COM030000", 
    "alt_label": [
      "Computers / Information Storage & Retrieval"
    ]
  }, 
  "Juvenile Nonfiction / Mathematics / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Mathematics / General", 
    "notation": "JNF035000", 
    "alt_label": []
  }, 
  "Music / Musical Instruments / Piano & Keyboard": {
    "related": [], 
    "pref_label": "Music / Musical Instruments / Piano & Keyboard", 
    "notation": "MUS023030", 
    "alt_label": []
  }, 
  "Bibles / Other Translations / Text": {
    "related": [], 
    "pref_label": "Bibles / Other Translations / Text", 
    "notation": "BIB018060", 
    "alt_label": []
  }, 
  "Health & Fitness / Sexuality": {
    "related": [], 
    "pref_label": "Health & Fitness / Sexuality", 
    "notation": "HEA042000", 
    "alt_label": []
  }, 
  "Business & Economics / Accounting / Standards (gaap, Ifrs, Etc.)": {
    "related": [], 
    "pref_label": "Business & Economics / Accounting / Standards (gaap, Ifrs, Etc.)", 
    "notation": "BUS001050", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Rock": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Rock", 
    "notation": "MUS035000", 
    "alt_label": []
  }, 
  "History / Caribbean & West Indies / General": {
    "related": [], 
    "pref_label": "History / Caribbean & West Indies / General", 
    "notation": "HIS041000", 
    "alt_label": []
  }, 
  "Bibles / Other Translations / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / Other Translations / New Testament & Portions", 
    "notation": "BIB018030", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Posters": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Posters", 
    "notation": "ANT034000", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Religious": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Religious", 
    "notation": "TRV026060", 
    "alt_label": []
  }, 
  "Computers / Software Development & Engineering / Systems Analysis & Design": {
    "related": [], 
    "pref_label": "Computers / Software Development & Engineering / Systems Analysis & Design", 
    "notation": "COM051240", 
    "alt_label": [
      "Computers / Systems Analysis"
    ]
  }, 
  "Cooking / Regional & Ethnic / Thai": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Thai", 
    "notation": "CKB083000", 
    "alt_label": []
  }, 
  "Medical / Bariatrics": {
    "related": [], 
    "pref_label": "Medical / Bariatrics", 
    "notation": "MED111000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Beadwork": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Beadwork", 
    "notation": "CRA048000", 
    "alt_label": []
  }, 
  "Fiction / Christian / Fantasy": {
    "related": [], 
    "pref_label": "Fiction / Christian / Fantasy", 
    "notation": "FIC042080", 
    "alt_label": []
  }, 
  "Self-help / Creativity": {
    "related": [], 
    "pref_label": "Self-help / Creativity", 
    "notation": "SEL009000", 
    "alt_label": []
  }, 
  "Travel / Asia / Japan": {
    "related": [], 
    "pref_label": "Travel / Asia / Japan", 
    "notation": "TRV003050", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Astrology / General": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Astrology / General", 
    "notation": "OCC002000", 
    "alt_label": []
  }, 
  "Fiction / Science Fiction / Adventure": {
    "related": [], 
    "pref_label": "Fiction / Science Fiction / Adventure", 
    "notation": "FIC028010", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / General": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / General", 
    "notation": "CGN004050", 
    "alt_label": []
  }, 
  "Art / History / Medieval": {
    "related": [], 
    "pref_label": "Art / History / Medieval", 
    "notation": "ART015070", 
    "alt_label": []
  }, 
  "Religion / Hinduism / General": {
    "related": [], 
    "pref_label": "Religion / Hinduism / General", 
    "notation": "REL032000", 
    "alt_label": []
  }, 
  "Philosophy / Buddhist": {
    "related": [], 
    "pref_label": "Philosophy / Buddhist", 
    "notation": "PHI028000", 
    "alt_label": []
  }, 
  "Bibles / New International Reader's Version / Children": {
    "related": [], 
    "pref_label": "Bibles / New International Reader's Version / Children", 
    "notation": "BIB012010", 
    "alt_label": []
  }, 
  "Bibles / Christian Standard Bible / Reference": {
    "related": [], 
    "pref_label": "Bibles / Christian Standard Bible / Reference", 
    "notation": "BIB001040", 
    "alt_label": []
  }, 
  "Music / Religious / Hymns": {
    "related": [], 
    "pref_label": "Music / Religious / Hymns", 
    "notation": "MUS021000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Hippos & Rhinos": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Hippos & Rhinos", 
    "notation": "JUV002330", 
    "alt_label": []
  }, 
  "Performing Arts / Dance / Popular": {
    "related": [], 
    "pref_label": "Performing Arts / Dance / Popular", 
    "notation": "PER003060", 
    "alt_label": []
  }, 
  "Fiction / African American / Historical": {
    "related": [], 
    "pref_label": "Fiction / African American / Historical", 
    "notation": "FIC049040", 
    "alt_label": []
  }, 
  "Law / Court Rules": {
    "related": [], 
    "pref_label": "Law / Court Rules", 
    "notation": "LAW024000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Marine Life": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Marine Life", 
    "notation": "JUV002170", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Jewish": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Jewish", 
    "notation": "JUV033020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / General", 
    "notation": "JNF013000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Surfing": {
    "related": [], 
    "pref_label": "Sports & Recreation / Surfing", 
    "notation": "SPO069000", 
    "alt_label": []
  }, 
  "Gardening / Reference": {
    "related": [], 
    "pref_label": "Gardening / Reference", 
    "notation": "GAR018000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / Forestry": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / Forestry", 
    "notation": "TEC003040", 
    "alt_label": []
  }, 
  "Music / Printed Music / Band & Orchestra": {
    "related": [], 
    "pref_label": "Music / Printed Music / Band & Orchestra", 
    "notation": "MUS037020", 
    "alt_label": []
  }, 
  "Humor / Form / Comic Strips & Cartoons": {
    "related": [], 
    "pref_label": "Humor / Form / Comic Strips & Cartoons", 
    "notation": "HUM001000", 
    "alt_label": []
  }, 
  "Literary Criticism / Gothic & Romance": {
    "related": [], 
    "pref_label": "Literary Criticism / Gothic & Romance", 
    "notation": "LIT004180", 
    "alt_label": []
  }, 
  "Literary Criticism / Middle Eastern": {
    "related": [], 
    "pref_label": "Literary Criticism / Middle Eastern", 
    "notation": "LIT004220", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Sql": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Sql", 
    "notation": "COM051170", 
    "alt_label": []
  }, 
  "History / Modern / 18th Century": {
    "related": [], 
    "pref_label": "History / Modern / 18th Century", 
    "notation": "HIS037050", 
    "alt_label": []
  }, 
  "Religion / Christian Church / General": {
    "related": [], 
    "pref_label": "Religion / Christian Church / General", 
    "notation": "REL108000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Latin": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Latin", 
    "notation": "MUS036000", 
    "alt_label": [
      "Music / Genres & Styles / Salsa"
    ]
  }, 
  "Social Science / Popular Culture": {
    "related": [], 
    "pref_label": "Social Science / Popular Culture", 
    "notation": "SOC022000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Opposites": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Opposites", 
    "notation": "JUV009040", 
    "alt_label": []
  }, 
  "Gardening / Flowers / Orchids": {
    "related": [], 
    "pref_label": "Gardening / Flowers / Orchids", 
    "notation": "GAR004040", 
    "alt_label": []
  }, 
  "Education / Language Experience Approach": {
    "related": [], 
    "pref_label": "Education / Language Experience Approach", 
    "notation": "EDU018000", 
    "alt_label": []
  }, 
  "Psychology / Hypnotism": {
    "related": [], 
    "pref_label": "Psychology / Hypnotism", 
    "notation": "PSY035000", 
    "alt_label": []
  }, 
  "Computers / Operating Systems / Mainframe & Midrange": {
    "related": [], 
    "pref_label": "Computers / Operating Systems / Mainframe & Midrange", 
    "notation": "COM046080", 
    "alt_label": []
  }, 
  "Travel / Budget": {
    "related": [], 
    "pref_label": "Travel / Budget", 
    "notation": "TRV033000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / Agronomy / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / Agronomy / General", 
    "notation": "TEC003080", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Family / Marriage & Divorce": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Family / Marriage & Divorce", 
    "notation": "JUV013020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Dogs": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Dogs", 
    "notation": "JNF003060", 
    "alt_label": []
  }, 
  "Science / Philosophy & Social Aspects": {
    "related": [], 
    "pref_label": "Science / Philosophy & Social Aspects", 
    "notation": "SCI075000", 
    "alt_label": [
      "Science / Social Aspects"
    ]
  }, 
  "Law / Taxation": {
    "related": [], 
    "pref_label": "Law / Taxation", 
    "notation": "LAW086000", 
    "alt_label": []
  }, 
  "History / Asia / Japan": {
    "related": [], 
    "pref_label": "History / Asia / Japan", 
    "notation": "HIS021000", 
    "alt_label": []
  }, 
  "Medical / Instruments & Supplies": {
    "related": [], 
    "pref_label": "Medical / Instruments & Supplies", 
    "notation": "MED108000", 
    "alt_label": [
      "Medical / Equipment", 
      "Medical / Supplies"
    ]
  }, 
  "Travel / Africa / Central": {
    "related": [], 
    "pref_label": "Travel / Africa / Central", 
    "notation": "TRV002010", 
    "alt_label": []
  }, 
  "Architecture / Professional Practice": {
    "related": [], 
    "pref_label": "Architecture / Professional Practice", 
    "notation": "ARC015000", 
    "alt_label": []
  }, 
  "Medical / Nursing / Fundamentals & Skills": {
    "related": [], 
    "pref_label": "Medical / Nursing / Fundamentals & Skills", 
    "notation": "MED058050", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Alphabets & Writing Systems": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Alphabets & Writing Systems", 
    "notation": "LAN001000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Trees & Forests": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Trees & Forests", 
    "notation": "JNF037040", 
    "alt_label": []
  }, 
  "Medical / Hospital Administration & Care": {
    "related": [], 
    "pref_label": "Medical / Hospital Administration & Care", 
    "notation": "MED043000", 
    "alt_label": []
  }, 
  "Architecture / Landscape": {
    "related": [], 
    "pref_label": "Architecture / Landscape", 
    "notation": "ARC008000", 
    "alt_label": []
  }, 
  "Religion / Christian Ministry / Missions": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / Missions", 
    "notation": "REL045000", 
    "alt_label": []
  }, 
  "Education / Counseling / General": {
    "related": [], 
    "pref_label": "Education / Counseling / General", 
    "notation": "EDU006000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Lutheran": {
    "related": [], 
    "pref_label": "Religion / Christianity / Lutheran", 
    "notation": "REL082000", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Oceans & Seas": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Oceans & Seas", 
    "notation": "NAT025000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Dance": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Dance", 
    "notation": "MUS011000", 
    "alt_label": []
  }, 
  "Religion / Atheism": {
    "related": [], 
    "pref_label": "Religion / Atheism", 
    "notation": "REL004000", 
    "alt_label": []
  }, 
  "Mathematics / Reference": {
    "related": [], 
    "pref_label": "Mathematics / Reference", 
    "notation": "MAT026000", 
    "alt_label": []
  }, 
  "Religion / Devotional": {
    "related": [], 
    "pref_label": "Religion / Devotional", 
    "notation": "REL022000", 
    "alt_label": []
  }, 
  "Bibles / Common English Bible / Text": {
    "related": [], 
    "pref_label": "Bibles / Common English Bible / Text", 
    "notation": "BIB022060", 
    "alt_label": []
  }, 
  "History / Military / General": {
    "related": [], 
    "pref_label": "History / Military / General", 
    "notation": "HIS027000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Sounds": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Sounds", 
    "notation": "JUV009110", 
    "alt_label": []
  }, 
  "Education / Behavioral Management": {
    "related": [], 
    "pref_label": "Education / Behavioral Management", 
    "notation": "EDU049000", 
    "alt_label": []
  }, 
  "Fiction / Fantasy / Urban Life": {
    "related": [], 
    "pref_label": "Fiction / Fantasy / Urban Life", 
    "notation": "FIC009060", 
    "alt_label": []
  }, 
  "Technology & Engineering / Superconductors & Superconductivity": {
    "related": [], 
    "pref_label": "Technology & Engineering / Superconductors & Superconductivity", 
    "notation": "TEC039000", 
    "alt_label": []
  }, 
  "Fiction / Gothic": {
    "related": [], 
    "pref_label": "Fiction / Gothic", 
    "notation": "FIC027040", 
    "alt_label": []
  }, 
  "Bibles / The Message / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / The Message / New Testament & Portions", 
    "notation": "BIB020030", 
    "alt_label": []
  }, 
  "Bibles / New International Reader's Version / Devotional": {
    "related": [], 
    "pref_label": "Bibles / New International Reader's Version / Devotional", 
    "notation": "BIB012020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Exploration & Discovery": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Exploration & Discovery", 
    "notation": "JUV016050", 
    "alt_label": []
  }, 
  "Business & Economics / Research & Development": {
    "related": [], 
    "pref_label": "Business & Economics / Research & Development", 
    "notation": "BUS108000", 
    "alt_label": []
  }, 
  "Law / Government / State, Provincial & Municipal": {
    "related": [], 
    "pref_label": "Law / Government / State, Provincial & Municipal", 
    "notation": "LAW089000", 
    "alt_label": []
  }, 
  "Performing Arts / Film & Video / History & Criticism": {
    "related": [], 
    "pref_label": "Performing Arts / Film & Video / History & Criticism", 
    "notation": "PER004030", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Personal Growth": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Personal Growth", 
    "notation": "REL012070", 
    "alt_label": []
  }, 
  "Business & Economics / Economics / Microeconomics": {
    "related": [], 
    "pref_label": "Business & Economics / Economics / Microeconomics", 
    "notation": "BUS044000", 
    "alt_label": [
      "Business & Economics / Microeconomics"
    ]
  }, 
  "Antiques & Collectibles / Bottles": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Bottles", 
    "notation": "ANT006000", 
    "alt_label": []
  }, 
  "Law / Maritime": {
    "related": [], 
    "pref_label": "Law / Maritime", 
    "notation": "LAW066000", 
    "alt_label": [
      "Law / Admiralty"
    ]
  }, 
  "Self-help / Substance Abuse & Addictions / Alcoholism": {
    "related": [], 
    "pref_label": "Self-help / Substance Abuse & Addictions / Alcoholism", 
    "notation": "SEL006000", 
    "alt_label": []
  }, 
  "Science / Earth Sciences / Geography": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / Geography", 
    "notation": "SCI030000", 
    "alt_label": []
  }, 
  "Poetry / General": {
    "related": [], 
    "pref_label": "Poetry / General", 
    "notation": "POE000000", 
    "alt_label": []
  }, 
  "Performing Arts / Film & Video / Direction & Production": {
    "related": [], 
    "pref_label": "Performing Arts / Film & Video / Direction & Production", 
    "notation": "PER004010", 
    "alt_label": []
  }, 
  "Religion / Biblical Meditations / Old Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Meditations / Old Testament", 
    "notation": "REL006120", 
    "alt_label": []
  }, 
  "Foreign Language Study / English As A Second Language": {
    "related": [], 
    "pref_label": "Foreign Language Study / English As A Second Language", 
    "notation": "FOR007000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Jewelry": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Jewelry", 
    "notation": "ANT021000", 
    "alt_label": []
  }, 
  "Law / Discrimination": {
    "related": [], 
    "pref_label": "Law / Discrimination", 
    "notation": "LAW094000", 
    "alt_label": []
  }, 
  "Bibles / New Century Version / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / New Century Version / Youth & Teen", 
    "notation": "BIB011070", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Musicals": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Musicals", 
    "notation": "MUS046000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Angels & Spirit Guides": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Angels & Spirit Guides", 
    "notation": "OCC032000", 
    "alt_label": []
  }, 
  "Religion / Buddhism / Theravada": {
    "related": [], 
    "pref_label": "Religion / Buddhism / Theravada", 
    "notation": "REL007040", 
    "alt_label": []
  }, 
  "Technology & Engineering / Civil / Bridges": {
    "related": [], 
    "pref_label": "Technology & Engineering / Civil / Bridges", 
    "notation": "TEC009100", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Extreme Sports": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Extreme Sports", 
    "notation": "JNF054180", 
    "alt_label": []
  }, 
  "Science / Physics / Nuclear": {
    "related": [], 
    "pref_label": "Science / Physics / Nuclear", 
    "notation": "SCI051000", 
    "alt_label": []
  }, 
  "Art / Techniques / Airbrush": {
    "related": [], 
    "pref_label": "Art / Techniques / Airbrush", 
    "notation": "ART002000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Martial Arts": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Martial Arts", 
    "notation": "JNF054080", 
    "alt_label": []
  }, 
  "Psychology / Industrial & Organizational Psychology": {
    "related": [], 
    "pref_label": "Psychology / Industrial & Organizational Psychology", 
    "notation": "PSY021000", 
    "alt_label": [
      "Psychology / Occupational Psychology"
    ]
  }, 
  "Law / Educational Law & Legislation": {
    "related": [], 
    "pref_label": "Law / Educational Law & Legislation", 
    "notation": "LAW092000", 
    "alt_label": []
  }, 
  "Social Science / Ethnic Studies / Hispanic American Studies": {
    "related": [], 
    "pref_label": "Social Science / Ethnic Studies / Hispanic American Studies", 
    "notation": "SOC044000", 
    "alt_label": []
  }, 
  "Literary Criticism / European / Scandinavian": {
    "related": [], 
    "pref_label": "Literary Criticism / European / Scandinavian", 
    "notation": "LIT004250", 
    "alt_label": []
  }, 
  "Nature / Animals / Wolves": {
    "related": [], 
    "pref_label": "Nature / Animals / Wolves", 
    "notation": "NAT044000", 
    "alt_label": []
  }, 
  "Law / Annotations & Citations": {
    "related": [], 
    "pref_label": "Law / Annotations & Citations", 
    "notation": "LAW004000", 
    "alt_label": []
  }, 
  "Bibles / Multiple Translations / General": {
    "related": [], 
    "pref_label": "Bibles / Multiple Translations / General", 
    "notation": "BIB008000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / Europe": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Europe", 
    "notation": "JUV030050", 
    "alt_label": []
  }, 
  "Bibles / New Century Version / Text": {
    "related": [], 
    "pref_label": "Bibles / New Century Version / Text", 
    "notation": "BIB011060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Social Issues": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Social Issues", 
    "notation": "JNF049290", 
    "alt_label": []
  }, 
  "Sports & Recreation / Fencing": {
    "related": [], 
    "pref_label": "Sports & Recreation / Fencing", 
    "notation": "SPO071000", 
    "alt_label": []
  }, 
  "Social Science / Feminism & Feminist Theory": {
    "related": [], 
    "pref_label": "Social Science / Feminism & Feminist Theory", 
    "notation": "SOC010000", 
    "alt_label": []
  }, 
  "Poetry / Subjects & Themes / Places": {
    "related": [], 
    "pref_label": "Poetry / Subjects & Themes / Places", 
    "notation": "POE023040", 
    "alt_label": []
  }, 
  "Technology & Engineering / Holography": {
    "related": [], 
    "pref_label": "Technology & Engineering / Holography", 
    "notation": "TEC050000", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Autism Spectrum Disorders": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Autism Spectrum Disorders", 
    "notation": "PSY022020", 
    "alt_label": []
  }, 
  "Performing Arts / Theater / General": {
    "related": [], 
    "pref_label": "Performing Arts / Theater / General", 
    "notation": "PER011000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / General", 
    "notation": "JNF024000", 
    "alt_label": []
  }, 
  "Religion / Christian Church / Growth": {
    "related": [], 
    "pref_label": "Religion / Christian Church / Growth", 
    "notation": "REL108010", 
    "alt_label": []
  }, 
  "Law / Jurisprudence": {
    "related": [], 
    "pref_label": "Law / Jurisprudence", 
    "notation": "LAW052000", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Energy": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Energy", 
    "notation": "BUS070040", 
    "alt_label": []
  }, 
  "Self-help / Personal Growth / General": {
    "related": [], 
    "pref_label": "Self-help / Personal Growth / General", 
    "notation": "SEL031000", 
    "alt_label": []
  }, 
  "History / Medieval": {
    "related": [], 
    "pref_label": "History / Medieval", 
    "notation": "HIS037010", 
    "alt_label": [
      "History / World / Medieval"
    ]
  }, 
  "Sports & Recreation / Boating": {
    "related": [], 
    "pref_label": "Sports & Recreation / Boating", 
    "notation": "SPO005000", 
    "alt_label": []
  }, 
  "Bibles / New King James Version / Children": {
    "related": [], 
    "pref_label": "Bibles / New King James Version / Children", 
    "notation": "BIB014010", 
    "alt_label": []
  }, 
  "Medical / Health Policy": {
    "related": [], 
    "pref_label": "Medical / Health Policy", 
    "notation": "MED036000", 
    "alt_label": []
  }, 
  "Education / Philosophy & Social Aspects": {
    "related": [], 
    "pref_label": "Education / Philosophy & Social Aspects", 
    "notation": "EDU040000", 
    "alt_label": [
      "Education / Social Aspects"
    ]
  }, 
  "Medical / Osteopathy": {
    "related": [], 
    "pref_label": "Medical / Osteopathy", 
    "notation": "MED092000", 
    "alt_label": []
  }, 
  "History / Military / Strategy": {
    "related": [], 
    "pref_label": "History / Military / Strategy", 
    "notation": "HIS027060", 
    "alt_label": []
  }, 
  "Music / Printed Music / Piano-vocal-guitar": {
    "related": [], 
    "pref_label": "Music / Printed Music / Piano-vocal-guitar", 
    "notation": "MUS037100", 
    "alt_label": []
  }, 
  "Technology & Engineering / Power Resources / Nuclear": {
    "related": [], 
    "pref_label": "Technology & Engineering / Power Resources / Nuclear", 
    "notation": "TEC028000", 
    "alt_label": []
  }, 
  "Literary Collections / Asian / Indic": {
    "related": [], 
    "pref_label": "Literary Collections / Asian / Indic", 
    "notation": "LCO004020", 
    "alt_label": []
  }, 
  "Business & Economics / Outsourcing": {
    "related": [], 
    "pref_label": "Business & Economics / Outsourcing", 
    "notation": "BUS102000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Extreme Sports": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Extreme Sports", 
    "notation": "JUV032100", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Historical": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Historical", 
    "notation": "BIO006000", 
    "alt_label": []
  }, 
  "Family & Relationships / Divorce & Separation": {
    "related": [], 
    "pref_label": "Family & Relationships / Divorce & Separation", 
    "notation": "FAM015000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Family / Marriage & Divorce": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Family / Marriage & Divorce", 
    "notation": "JNF019020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Birds": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Birds", 
    "notation": "JUV002040", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / Animal Husbandry": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / Animal Husbandry", 
    "notation": "TEC003020", 
    "alt_label": []
  }, 
  "Business & Economics / Business Writing": {
    "related": [], 
    "pref_label": "Business & Economics / Business Writing", 
    "notation": "BUS011000", 
    "alt_label": []
  }, 
  "Science / Waves & Wave Mechanics": {
    "related": [], 
    "pref_label": "Science / Waves & Wave Mechanics", 
    "notation": "SCI067000", 
    "alt_label": []
  }, 
  "Health & Fitness / Aerobics": {
    "related": [], 
    "pref_label": "Health & Fitness / Aerobics", 
    "notation": "HEA002000", 
    "alt_label": []
  }, 
  "Education / Student Life & Student Affairs": {
    "related": [], 
    "pref_label": "Education / Student Life & Student Affairs", 
    "notation": "EDU038000", 
    "alt_label": []
  }, 
  "Fiction / Asian American": {
    "related": [], 
    "pref_label": "Fiction / Asian American", 
    "notation": "FIC054000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Foreign Language Study / Spanish": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Foreign Language Study / Spanish", 
    "notation": "JNF020030", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Love & Marriage": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Love & Marriage", 
    "notation": "REL012050", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Computers / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Computers / General", 
    "notation": "JNF012000", 
    "alt_label": []
  }, 
  "Religion / Fundamentalism": {
    "related": [], 
    "pref_label": "Religion / Fundamentalism", 
    "notation": "REL078000", 
    "alt_label": []
  }, 
  "Religion / Biblical Reference / Concordances": {
    "related": [], 
    "pref_label": "Religion / Biblical Reference / Concordances", 
    "notation": "REL006660", 
    "alt_label": []
  }, 
  "Art / American / General": {
    "related": [], 
    "pref_label": "Art / American / General", 
    "notation": "ART015020", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Coins, Currency & Medals": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Coins, Currency & Medals", 
    "notation": "ANT011000", 
    "alt_label": [
      "Antiques & Collectibles / Medals"
    ]
  }, 
  "Medical / Prosthesis": {
    "related": [], 
    "pref_label": "Medical / Prosthesis", 
    "notation": "MED077000", 
    "alt_label": []
  }, 
  "Bibles / English Standard Version / Children": {
    "related": [], 
    "pref_label": "Bibles / English Standard Version / Children", 
    "notation": "BIB003010", 
    "alt_label": []
  }, 
  "Cooking / Methods / Outdoor": {
    "related": [], 
    "pref_label": "Cooking / Methods / Outdoor", 
    "notation": "CKB060000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Fire Science": {
    "related": [], 
    "pref_label": "Technology & Engineering / Fire Science", 
    "notation": "TEC045000", 
    "alt_label": []
  }, 
  "Medical / Reference": {
    "related": [], 
    "pref_label": "Medical / Reference", 
    "notation": "MED081000", 
    "alt_label": []
  }, 
  "Political Science / Commentary & Opinion": {
    "related": [], 
    "pref_label": "Political Science / Commentary & Opinion", 
    "notation": "POL046000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Language Arts / Handwriting": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Language Arts / Handwriting", 
    "notation": "JNF029030", 
    "alt_label": []
  }, 
  "Nature / Plants / Cacti & Succulents": {
    "related": [], 
    "pref_label": "Nature / Plants / Cacti & Succulents", 
    "notation": "NAT048000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Publishing": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Publishing", 
    "notation": "LAN027000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / New Experience": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / New Experience", 
    "notation": "JNF053100", 
    "alt_label": []
  }, 
  "Design / Graphic Arts / Advertising": {
    "related": [], 
    "pref_label": "Design / Graphic Arts / Advertising", 
    "notation": "DES007010", 
    "alt_label": []
  }, 
  "History / World": {
    "related": [], 
    "pref_label": "History / World", 
    "notation": "HIS037000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / Organic": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / Organic", 
    "notation": "TEC003090", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Art / Sculpture": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Art / Sculpture", 
    "notation": "JNF006060", 
    "alt_label": []
  }, 
  "Business & Economics / Museum Administration & Museology": {
    "related": [], 
    "pref_label": "Business & Economics / Museum Administration & Museology", 
    "notation": "BUS100000", 
    "alt_label": []
  }, 
  "Religion / Deism": {
    "related": [], 
    "pref_label": "Religion / Deism", 
    "notation": "REL021000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Needlework / Needlepoint": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Needlework / Needlepoint", 
    "notation": "CRA021000", 
    "alt_label": []
  }, 
  "Bibles / New Living Translation / Text": {
    "related": [], 
    "pref_label": "Bibles / New Living Translation / Text", 
    "notation": "BIB015060", 
    "alt_label": []
  }, 
  "Performing Arts / Monologues & Scenes": {
    "related": [], 
    "pref_label": "Performing Arts / Monologues & Scenes", 
    "notation": "PER020000", 
    "alt_label": []
  }, 
  "Medical / Cardiology": {
    "related": [], 
    "pref_label": "Medical / Cardiology", 
    "notation": "MED010000", 
    "alt_label": [
      "Medical / Diseases / Cardiopulmonary", 
      "Medical / Diseases / Cardiovascular"
    ]
  }, 
  "Medical / Allied Health Services / Emergency Medical Services": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / Emergency Medical Services", 
    "notation": "MED003010", 
    "alt_label": []
  }, 
  "Photography / Techniques / Equipment": {
    "related": [], 
    "pref_label": "Photography / Techniques / Equipment", 
    "notation": "PHO007000", 
    "alt_label": [
      "Photography / Camera Specific"
    ]
  }, 
  "Law / Customary": {
    "related": [], 
    "pref_label": "Law / Customary", 
    "notation": "LAW028000", 
    "alt_label": []
  }, 
  "Games / Card Games / Bridge": {
    "related": [], 
    "pref_label": "Games / Card Games / Bridge", 
    "notation": "GAM002010", 
    "alt_label": [
      "Games / Bridge"
    ]
  }, 
  "Drama / European / French": {
    "related": [], 
    "pref_label": "Drama / European / French", 
    "notation": "DRA004010", 
    "alt_label": []
  }, 
  "Education / Physical Education": {
    "related": [], 
    "pref_label": "Education / Physical Education", 
    "notation": "EDU033000", 
    "alt_label": []
  }, 
  "Education / Educational Policy & Reform / General": {
    "related": [], 
    "pref_label": "Education / Educational Policy & Reform / General", 
    "notation": "EDU034000", 
    "alt_label": []
  }, 
  "Philosophy / Political": {
    "related": [], 
    "pref_label": "Philosophy / Political", 
    "notation": "PHI019000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Polish": {
    "related": [], 
    "pref_label": "Foreign Language Study / Polish", 
    "notation": "FOR019000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Prejudice & Racism": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Prejudice & Racism", 
    "notation": "JNF053140", 
    "alt_label": []
  }, 
  "Fiction / Christian / Futuristic": {
    "related": [], 
    "pref_label": "Fiction / Christian / Futuristic", 
    "notation": "FIC042020", 
    "alt_label": []
  }, 
  "Medical / Allied Health Services / Massage Therapy": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / Massage Therapy", 
    "notation": "MED003090", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Self-esteem & Self-reliance": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Self-esteem & Self-reliance", 
    "notation": "JUV039140", 
    "alt_label": []
  }, 
  "Medical / Pharmacology": {
    "related": [], 
    "pref_label": "Medical / Pharmacology", 
    "notation": "MED071000", 
    "alt_label": []
  }, 
  "Computers / Data Modeling & Design": {
    "related": [], 
    "pref_label": "Computers / Data Modeling & Design", 
    "notation": "COM062000", 
    "alt_label": []
  }, 
  "Mathematics / General": {
    "related": [], 
    "pref_label": "Mathematics / General", 
    "notation": "MAT000000", 
    "alt_label": []
  }, 
  "Bibles / Nueva Version International / Reference": {
    "related": [], 
    "pref_label": "Bibles / Nueva Version International / Reference", 
    "notation": "BIB017040", 
    "alt_label": []
  }, 
  "Education / Teaching Methods & Materials / Reading & Phonics": {
    "related": [], 
    "pref_label": "Education / Teaching Methods & Materials / Reading & Phonics", 
    "notation": "EDU029020", 
    "alt_label": []
  }, 
  "Bibles / Christian Standard Bible / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / Christian Standard Bible / Youth & Teen", 
    "notation": "BIB001070", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Genitourinary & Stds": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Genitourinary & Stds", 
    "notation": "HEA039070", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / Mountains": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / Mountains", 
    "notation": "NAT041000", 
    "alt_label": []
  }, 
  "Literary Criticism / Drama": {
    "related": [], 
    "pref_label": "Literary Criticism / Drama", 
    "notation": "LIT013000", 
    "alt_label": []
  }, 
  "Medical / Nursing / Gerontology": {
    "related": [], 
    "pref_label": "Medical / Nursing / Gerontology", 
    "notation": "MED058060", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Portuguese": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Portuguese", 
    "notation": "CKB066000", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / Prophets": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / Prophets", 
    "notation": "REL006730", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Flowers & Plants": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Flowers & Plants", 
    "notation": "JNF037030", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Prayer": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Prayer", 
    "notation": "REL012080", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Cats": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Cats", 
    "notation": "JUV002050", 
    "alt_label": []
  }, 
  "Drama / Australian & Oceanian": {
    "related": [], 
    "pref_label": "Drama / Australian & Oceanian", 
    "notation": "DRA012000", 
    "alt_label": []
  }, 
  "Fiction / Science Fiction / High Tech": {
    "related": [], 
    "pref_label": "Fiction / Science Fiction / High Tech", 
    "notation": "FIC028020", 
    "alt_label": []
  }, 
  "Religion / Christianity / Shaker": {
    "related": [], 
    "pref_label": "Religion / Christianity / Shaker", 
    "notation": "REL059000", 
    "alt_label": []
  }, 
  "Transportation / Aviation / Commercial": {
    "related": [], 
    "pref_label": "Transportation / Aviation / Commercial", 
    "notation": "TRA002040", 
    "alt_label": []
  }, 
  "Nature / Animals / Butterflies & Moths": {
    "related": [], 
    "pref_label": "Nature / Animals / Butterflies & Moths", 
    "notation": "NAT005000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Baseball / Statistics": {
    "related": [], 
    "pref_label": "Sports & Recreation / Baseball / Statistics", 
    "notation": "SPO003040", 
    "alt_label": []
  }, 
  "Computers / Computer Science": {
    "related": [], 
    "pref_label": "Computers / Computer Science", 
    "notation": "COM014000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Apes, Monkeys, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Apes, Monkeys, Etc.", 
    "notation": "JNF003010", 
    "alt_label": []
  }, 
  "Literary Collections / European / General": {
    "related": [], 
    "pref_label": "Literary Collections / European / General", 
    "notation": "LCO008000", 
    "alt_label": []
  }, 
  "Architecture / History / Contemporary (1945-)": {
    "related": [], 
    "pref_label": "Architecture / History / Contemporary (1945-)", 
    "notation": "ARC005080", 
    "alt_label": []
  }, 
  "Religion / Christianity / Saints & Sainthood": {
    "related": [], 
    "pref_label": "Religion / Christianity / Saints & Sainthood", 
    "notation": "REL110000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / General": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / General", 
    "notation": "HEA039000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Rabbits": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Rabbits", 
    "notation": "JNF003180", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Suicide": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Suicide", 
    "notation": "JUV039160", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Reference": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Reference", 
    "notation": "BIO012000", 
    "alt_label": []
  }, 
  "Transportation / Automotive / General": {
    "related": [], 
    "pref_label": "Transportation / Automotive / General", 
    "notation": "TRA001000", 
    "alt_label": []
  }, 
  "History / United States / General": {
    "related": [], 
    "pref_label": "History / United States / General", 
    "notation": "HIS036000", 
    "alt_label": []
  }, 
  "Family & Relationships / Attention Deficit Disorder (add-adhd)": {
    "related": [], 
    "pref_label": "Family & Relationships / Attention Deficit Disorder (add-adhd)", 
    "notation": "FAM047000", 
    "alt_label": []
  }, 
  "Transportation / Automotive / Antique & Classic": {
    "related": [], 
    "pref_label": "Transportation / Automotive / Antique & Classic", 
    "notation": "TRA001010", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Historical Fiction": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Historical Fiction", 
    "notation": "CGN010000", 
    "alt_label": []
  }, 
  "Computers / Interactive & Multimedia": {
    "related": [], 
    "pref_label": "Computers / Interactive & Multimedia", 
    "notation": "COM034000", 
    "alt_label": [
      "Computers / Multimedia"
    ]
  }, 
  "Comics & Graphic Novels / Media Tie-in": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Media Tie-in", 
    "notation": "CGN004060", 
    "alt_label": []
  }, 
  "Science / Life Sciences / Biological Diversity": {
    "related": [], 
    "pref_label": "Science / Life Sciences / Biological Diversity", 
    "notation": "SCI088000", 
    "alt_label": []
  }, 
  "Computers / Web / Site Design": {
    "related": [], 
    "pref_label": "Computers / Web / Site Design", 
    "notation": "COM060130", 
    "alt_label": []
  }, 
  "Education / Teaching Methods & Materials / Library Skills": {
    "related": [], 
    "pref_label": "Education / Teaching Methods & Materials / Library Skills", 
    "notation": "EDU029060", 
    "alt_label": []
  }, 
  "Travel / Special Interest / Handicapped": {
    "related": [], 
    "pref_label": "Travel / Special Interest / Handicapped", 
    "notation": "TRV026030", 
    "alt_label": []
  }, 
  "Performing Arts / Radio / History & Criticism": {
    "related": [], 
    "pref_label": "Performing Arts / Radio / History & Criticism", 
    "notation": "PER008010", 
    "alt_label": []
  }, 
  "Religion / Biblical Reference / Language Study": {
    "related": [], 
    "pref_label": "Religion / Biblical Reference / Language Study", 
    "notation": "REL006410", 
    "alt_label": []
  }, 
  "Self-help / Anxieties & Phobias": {
    "related": [], 
    "pref_label": "Self-help / Anxieties & Phobias", 
    "notation": "SEL036000", 
    "alt_label": []
  }, 
  "Philosophy / Eastern": {
    "related": [], 
    "pref_label": "Philosophy / Eastern", 
    "notation": "PHI003000", 
    "alt_label": []
  }, 
  "Self-help / Stress Management": {
    "related": [], 
    "pref_label": "Self-help / Stress Management", 
    "notation": "SEL024000", 
    "alt_label": [
      "Self-help / Relaxation"
    ]
  }, 
  "Performing Arts / General": {
    "related": [], 
    "pref_label": "Performing Arts / General", 
    "notation": "PER000000", 
    "alt_label": []
  }, 
  "Computers / Data Transmission Systems / General": {
    "related": [], 
    "pref_label": "Computers / Data Transmission Systems / General", 
    "notation": "COM020000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Buttons & Pins": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Buttons & Pins", 
    "notation": "ANT007000", 
    "alt_label": []
  }, 
  "Fiction / Visionary & Metaphysical": {
    "related": [], 
    "pref_label": "Fiction / Visionary & Metaphysical", 
    "notation": "FIC039000", 
    "alt_label": [
      "Fiction / Metaphysical"
    ]
  }, 
  "Political Science / World / Australian & Oceanian": {
    "related": [], 
    "pref_label": "Political Science / World / Australian & Oceanian", 
    "notation": "POL055000", 
    "alt_label": []
  }, 
  "Bibles / New International Reader's Version / Reference": {
    "related": [], 
    "pref_label": "Bibles / New International Reader's Version / Reference", 
    "notation": "BIB012040", 
    "alt_label": []
  }, 
  "Business & Economics / Distribution": {
    "related": [], 
    "pref_label": "Business & Economics / Distribution", 
    "notation": "BUS078000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Insects, Spiders, Etc.": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Insects, Spiders, Etc.", 
    "notation": "JNF003120", 
    "alt_label": []
  }, 
  "Computers / Systems Architecture / Distributed Systems & Computing": {
    "related": [], 
    "pref_label": "Computers / Systems Architecture / Distributed Systems & Computing", 
    "notation": "COM048000", 
    "alt_label": [
      "Computers / Parallel Processing"
    ]
  }, 
  "Art / Individual Artists / Artists' Books": {
    "related": [], 
    "pref_label": "Art / Individual Artists / Artists' Books", 
    "notation": "ART016010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Biblical History": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Biblical History", 
    "notation": "JNF049160", 
    "alt_label": []
  }, 
  "Drama / Asian / General": {
    "related": [], 
    "pref_label": "Drama / Asian / General", 
    "notation": "DRA005000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Hungarian": {
    "related": [], 
    "pref_label": "Foreign Language Study / Hungarian", 
    "notation": "FOR012000", 
    "alt_label": []
  }, 
  "Religion / Leadership": {
    "related": [], 
    "pref_label": "Religion / Leadership", 
    "notation": "REL071000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Spirituality / Shamanism": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Spirituality / Shamanism", 
    "notation": "OCC036030", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Salads": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Salads", 
    "notation": "CKB073000", 
    "alt_label": []
  }, 
  "Travel / Africa / Kenya": {
    "related": [], 
    "pref_label": "Travel / Africa / Kenya", 
    "notation": "TRV002030", 
    "alt_label": []
  }, 
  "Computers / Calculators": {
    "related": [], 
    "pref_label": "Computers / Calculators", 
    "notation": "COM008000", 
    "alt_label": []
  }, 
  "Travel / Asia / India": {
    "related": [], 
    "pref_label": "Travel / Asia / India", 
    "notation": "TRV003040", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Poetry / Humorous": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Poetry / Humorous", 
    "notation": "JNF042010", 
    "alt_label": []
  }, 
  "Education / Teaching Methods & Materials / Social Science": {
    "related": [], 
    "pref_label": "Education / Teaching Methods & Materials / Social Science", 
    "notation": "EDU029040", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Printmaking": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Printmaking", 
    "notation": "CRA029000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Porcelain & China": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Porcelain & China", 
    "notation": "ANT032000", 
    "alt_label": [
      "Antiques & Collectibles / China"
    ]
  }, 
  "Mathematics / Probability & Statistics / General": {
    "related": [], 
    "pref_label": "Mathematics / Probability & Statistics / General", 
    "notation": "MAT029000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / United States / Native American": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / United States / Native American", 
    "notation": "JNF018040", 
    "alt_label": []
  }, 
  "Self-help / Twelve-step Programs": {
    "related": [], 
    "pref_label": "Self-help / Twelve-step Programs", 
    "notation": "SEL029000", 
    "alt_label": []
  }, 
  "Computers / Image Processing": {
    "related": [], 
    "pref_label": "Computers / Image Processing", 
    "notation": "COM012050", 
    "alt_label": []
  }, 
  "Health & Fitness / Hearing & Speech": {
    "related": [], 
    "pref_label": "Health & Fitness / Hearing & Speech", 
    "notation": "HEA035000", 
    "alt_label": []
  }, 
  "Bibles / English Standard Version / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / English Standard Version / New Testament & Portions", 
    "notation": "BIB003030", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Library & Information Science / School Media": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Library & Information Science / School Media", 
    "notation": "LAN025050", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / United States / 19th Century": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / United States / 19th Century", 
    "notation": "JNF025200", 
    "alt_label": []
  }, 
  "Mathematics / Mathematical Analysis": {
    "related": [], 
    "pref_label": "Mathematics / Mathematical Analysis", 
    "notation": "MAT034000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Runaways": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Runaways", 
    "notation": "JNF053150", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Genetic": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Genetic", 
    "notation": "HEA039060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Homosexuality": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Homosexuality", 
    "notation": "JNF053080", 
    "alt_label": []
  }, 
  "Bibles / Today's New International Version / Study": {
    "related": [], 
    "pref_label": "Bibles / Today's New International Version / Study", 
    "notation": "BIB021050", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Applique": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Applique", 
    "notation": "CRA001000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Roller & In-line Skating": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Roller & In-line Skating", 
    "notation": "JUV032130", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Spanish": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Spanish", 
    "notation": "CKB080000", 
    "alt_label": []
  }, 
  "Reference / Atlases & Gazetteers": {
    "related": [], 
    "pref_label": "Reference / Atlases & Gazetteers", 
    "notation": "REF002000", 
    "alt_label": []
  }, 
  "Science / Earth Sciences / Seismology & Volcanism": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / Seismology & Volcanism", 
    "notation": "SCI082000", 
    "alt_label": []
  }, 
  "Computers / Information Technology": {
    "related": [], 
    "pref_label": "Computers / Information Technology", 
    "notation": "COM032000", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Country & Bluegrass": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Country & Bluegrass", 
    "notation": "MUS010000", 
    "alt_label": []
  }, 
  "Business & Economics / Skills": {
    "related": [], 
    "pref_label": "Business & Economics / Skills", 
    "notation": "BUS059000", 
    "alt_label": []
  }, 
  "Psychology / Social Psychology": {
    "related": [], 
    "pref_label": "Psychology / Social Psychology", 
    "notation": "PSY031000", 
    "alt_label": [
      "Psychology / Group Psychology"
    ]
  }, 
  "Juvenile Nonfiction / Science & Nature / Physics": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Physics", 
    "notation": "JNF051140", 
    "alt_label": []
  }, 
  "Medical / Microbiology": {
    "related": [], 
    "pref_label": "Medical / Microbiology", 
    "notation": "MED052000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Canadian": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Canadian", 
    "notation": "CKB091000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Central & South America": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Central & South America", 
    "notation": "JNF025060", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Birthdays": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Birthdays", 
    "notation": "JUV017100", 
    "alt_label": []
  }, 
  "Psychology / Research & Methodology": {
    "related": [], 
    "pref_label": "Psychology / Research & Methodology", 
    "notation": "PSY030000", 
    "alt_label": [
      "Psychology / Methodology"
    ]
  }, 
  "Music / Instruction & Study / Voice": {
    "related": [], 
    "pref_label": "Music / Instruction & Study / Voice", 
    "notation": "MUS042000", 
    "alt_label": []
  }, 
  "Medical / Dictionaries & Terminology": {
    "related": [], 
    "pref_label": "Medical / Dictionaries & Terminology", 
    "notation": "MED020000", 
    "alt_label": []
  }, 
  "History / United States / State & Local / Midwest (ia, Il, In, Ks, Mi, Mn, Mo, Nd, Ne, Oh, Sd, Wi)": {
    "related": [], 
    "pref_label": "History / United States / State & Local / Midwest (ia, Il, In, Ks, Mi, Mn, Mo, Nd, Ne, Oh, Sd, Wi)", 
    "notation": "HIS036090", 
    "alt_label": []
  }, 
  "Gardening / Flowers / Wildflowers": {
    "related": [], 
    "pref_label": "Gardening / Flowers / Wildflowers", 
    "notation": "GAR004080", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Substance Abuse": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Substance Abuse", 
    "notation": "JNF024100", 
    "alt_label": []
  }, 
  "Business & Economics / Free Enterprise": {
    "related": [], 
    "pref_label": "Business & Economics / Free Enterprise", 
    "notation": "BUS029000", 
    "alt_label": []
  }, 
  "Law / Law Office Management": {
    "related": [], 
    "pref_label": "Law / Law Office Management", 
    "notation": "LAW056000", 
    "alt_label": []
  }, 
  "Political Science / World / Asian": {
    "related": [], 
    "pref_label": "Political Science / World / Asian", 
    "notation": "POL054000", 
    "alt_label": []
  }, 
  "Business & Economics / Real Estate / Commercial": {
    "related": [], 
    "pref_label": "Business & Economics / Real Estate / Commercial", 
    "notation": "BUS054020", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Rpg": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Rpg", 
    "notation": "COM051290", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Speech": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Speech", 
    "notation": "LAN018000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Chinese": {
    "related": [], 
    "pref_label": "Foreign Language Study / Chinese", 
    "notation": "FOR003000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Family / Adoption": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Family / Adoption", 
    "notation": "JNF019010", 
    "alt_label": []
  }, 
  "Travel / Canada / Ontario (on)": {
    "related": [], 
    "pref_label": "Travel / Canada / Ontario (on)", 
    "notation": "TRV006020", 
    "alt_label": []
  }, 
  "Sports & Recreation / Soccer": {
    "related": [], 
    "pref_label": "Sports & Recreation / Soccer", 
    "notation": "SPO040000", 
    "alt_label": []
  }, 
  "Business & Economics / Insurance / Casualty": {
    "related": [], 
    "pref_label": "Business & Economics / Insurance / Casualty", 
    "notation": "BUS033020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Bedtime & Dreams": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Bedtime & Dreams", 
    "notation": "JUV010000", 
    "alt_label": [
      "Juvenile Fiction / Dreams", 
      "Juvenile Fiction / Night", 
      "Juvenile Fiction / Sleeping"
    ]
  }, 
  "Family & Relationships / Children With Special Needs": {
    "related": [], 
    "pref_label": "Family & Relationships / Children With Special Needs", 
    "notation": "FAM012000", 
    "alt_label": []
  }, 
  "Bibles / New King James Version / Reference": {
    "related": [], 
    "pref_label": "Bibles / New King James Version / Reference", 
    "notation": "BIB014040", 
    "alt_label": []
  }, 
  "Travel / Central America": {
    "related": [], 
    "pref_label": "Travel / Central America", 
    "notation": "TRV008000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Fairy Tales & Folklore / Country & Ethnic": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Fairy Tales & Folklore / Country & Ethnic", 
    "notation": "JUV012020", 
    "alt_label": []
  }, 
  "Social Science / Prostitution & Sex Trade": {
    "related": [], 
    "pref_label": "Social Science / Prostitution & Sex Trade", 
    "notation": "SOC059000", 
    "alt_label": []
  }, 
  "Business & Economics / Personal Finance / Budgeting": {
    "related": [], 
    "pref_label": "Business & Economics / Personal Finance / Budgeting", 
    "notation": "BUS050010", 
    "alt_label": []
  }, 
  "Drama / Middle Eastern": {
    "related": [], 
    "pref_label": "Drama / Middle Eastern", 
    "notation": "DRA015000", 
    "alt_label": []
  }, 
  "Science / Applied Sciences": {
    "related": [], 
    "pref_label": "Science / Applied Sciences", 
    "notation": "SCI003000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Biblical Studies": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Biblical Studies", 
    "notation": "JNF049010", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Meat": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Meat", 
    "notation": "CKB054000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / General", 
    "notation": "JNF038000", 
    "alt_label": []
  }, 
  "Computers / Operating Systems / Dos": {
    "related": [], 
    "pref_label": "Computers / Operating Systems / Dos", 
    "notation": "COM046060", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Comics & Graphic Novels / Manga": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Comics & Graphic Novels / Manga", 
    "notation": "JUV008010", 
    "alt_label": []
  }, 
  "Literary Criticism / Canadian": {
    "related": [], 
    "pref_label": "Literary Criticism / Canadian", 
    "notation": "LIT004080", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Science & Technology": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Science & Technology", 
    "notation": "BIO015000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / History": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / History", 
    "notation": "REL067080", 
    "alt_label": []
  }, 
  "Psychology / Emotions": {
    "related": [], 
    "pref_label": "Psychology / Emotions", 
    "notation": "PSY013000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Agriculture / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / Agriculture / General", 
    "notation": "TEC003000", 
    "alt_label": []
  }, 
  "History / Reference": {
    "related": [], 
    "pref_label": "History / Reference", 
    "notation": "HIS030000", 
    "alt_label": []
  }, 
  "Bibles / International Children's Bible / Reference": {
    "related": [], 
    "pref_label": "Bibles / International Children's Bible / Reference", 
    "notation": "BIB005040", 
    "alt_label": []
  }, 
  "Law / Conflict Of Laws": {
    "related": [], 
    "pref_label": "Law / Conflict Of Laws", 
    "notation": "LAW017000", 
    "alt_label": []
  }, 
  "Poetry / American / Asian American": {
    "related": [], 
    "pref_label": "Poetry / American / Asian American", 
    "notation": "POE005060", 
    "alt_label": []
  }, 
  "Travel / Europe / General": {
    "related": [], 
    "pref_label": "Travel / Europe / General", 
    "notation": "TRV009000", 
    "alt_label": []
  }, 
  "Law / Corporate": {
    "related": [], 
    "pref_label": "Law / Corporate", 
    "notation": "LAW022000", 
    "alt_label": [
      "Law / Corporate Governance"
    ]
  }, 
  "Poetry / American / General": {
    "related": [], 
    "pref_label": "Poetry / American / General", 
    "notation": "POE005010", 
    "alt_label": []
  }, 
  "Social Science / Developing & Emerging Countries": {
    "related": [], 
    "pref_label": "Social Science / Developing & Emerging Countries", 
    "notation": "SOC042000", 
    "alt_label": []
  }, 
  "Study Aids / Cpa (certified Public Accountant)": {
    "related": [], 
    "pref_label": "Study Aids / Cpa (certified Public Accountant)", 
    "notation": "STU011000", 
    "alt_label": []
  }, 
  "Music / Printed Music / Mixed Collections": {
    "related": [], 
    "pref_label": "Music / Printed Music / Mixed Collections", 
    "notation": "MUS037050", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Agribusiness": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Agribusiness", 
    "notation": "BUS070010", 
    "alt_label": []
  }, 
  "Law / Health": {
    "related": [], 
    "pref_label": "Law / Health", 
    "notation": "LAW046000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Africa": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Africa", 
    "notation": "JUV016010", 
    "alt_label": []
  }, 
  "Mathematics / Discrete Mathematics": {
    "related": [], 
    "pref_label": "Mathematics / Discrete Mathematics", 
    "notation": "MAT008000", 
    "alt_label": [
      "Mathematics / Computer Mathematics"
    ]
  }, 
  "Juvenile Nonfiction / Sports & Recreation / Golf": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Sports & Recreation / Golf", 
    "notation": "JNF054230", 
    "alt_label": []
  }, 
  "Business & Economics / Human Resources & Personnel Management": {
    "related": [], 
    "pref_label": "Business & Economics / Human Resources & Personnel Management", 
    "notation": "BUS030000", 
    "alt_label": [
      "Business & Economics / Personnel Management"
    ]
  }, 
  "Cooking / Courses & Dishes / Bread": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Bread", 
    "notation": "CKB009000", 
    "alt_label": []
  }, 
  "Medical / Geriatrics": {
    "related": [], 
    "pref_label": "Medical / Geriatrics", 
    "notation": "MED032000", 
    "alt_label": []
  }, 
  "Medical / Dentistry / Dental Hygiene": {
    "related": [], 
    "pref_label": "Medical / Dentistry / Dental Hygiene", 
    "notation": "MED016020", 
    "alt_label": []
  }, 
  "Business & Economics / Consulting": {
    "related": [], 
    "pref_label": "Business & Economics / Consulting", 
    "notation": "BUS075000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Old & Middle English": {
    "related": [], 
    "pref_label": "Foreign Language Study / Old & Middle English", 
    "notation": "FOR045000", 
    "alt_label": []
  }, 
  "Religion / General": {
    "related": [], 
    "pref_label": "Religion / General", 
    "notation": "REL000000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Inventions": {
    "related": [], 
    "pref_label": "Technology & Engineering / Inventions", 
    "notation": "TEC057000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Words": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Words", 
    "notation": "JUV009080", 
    "alt_label": []
  }, 
  "Law / Criminal Law / Sentencing": {
    "related": [], 
    "pref_label": "Law / Criminal Law / Sentencing", 
    "notation": "LAW026020", 
    "alt_label": []
  }, 
  "Literary Collections / Native American": {
    "related": [], 
    "pref_label": "Literary Collections / Native American", 
    "notation": "LCO013000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Martial Arts": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Martial Arts", 
    "notation": "JUV032070", 
    "alt_label": []
  }, 
  "Travel / Shopping": {
    "related": [], 
    "pref_label": "Travel / Shopping", 
    "notation": "TRV032000", 
    "alt_label": []
  }, 
  "Cooking / General": {
    "related": [], 
    "pref_label": "Cooking / General", 
    "notation": "CKB000000", 
    "alt_label": []
  }, 
  "Study Aids / General": {
    "related": [], 
    "pref_label": "Study Aids / General", 
    "notation": "STU000000", 
    "alt_label": []
  }, 
  "Family & Relationships / Abuse / Child Abuse": {
    "related": [], 
    "pref_label": "Family & Relationships / Abuse / Child Abuse", 
    "notation": "FAM001010", 
    "alt_label": []
  }, 
  "Family & Relationships / Life Stages / Adolescence": {
    "related": [], 
    "pref_label": "Family & Relationships / Life Stages / Adolescence", 
    "notation": "FAM003000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Concepts / Money": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Concepts / Money", 
    "notation": "JUV009090", 
    "alt_label": []
  }, 
  "Religion / Christianity / Episcopalian": {
    "related": [], 
    "pref_label": "Religion / Christianity / Episcopalian", 
    "notation": "REL027000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Divination / Palmistry": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Divination / Palmistry", 
    "notation": "OCC017000", 
    "alt_label": []
  }, 
  "Family & Relationships / Parenting / General": {
    "related": [], 
    "pref_label": "Family & Relationships / Parenting / General", 
    "notation": "FAM034000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Linguistics / Pragmatics": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Linguistics / Pragmatics", 
    "notation": "LAN009030", 
    "alt_label": []
  }, 
  "Fiction / Mystery & Detective / Hard-boiled": {
    "related": [], 
    "pref_label": "Fiction / Mystery & Detective / Hard-boiled", 
    "notation": "FIC022010", 
    "alt_label": []
  }, 
  "Business & Economics / Real Estate / General": {
    "related": [], 
    "pref_label": "Business & Economics / Real Estate / General", 
    "notation": "BUS054000", 
    "alt_label": []
  }, 
  "Psychology / Psychotherapy / Child & Adolescent": {
    "related": [], 
    "pref_label": "Psychology / Psychotherapy / Child & Adolescent", 
    "notation": "PSY006000", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Relationships": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Relationships", 
    "notation": "REL012100", 
    "alt_label": []
  }, 
  "Bibles / Nueva Version International / Study": {
    "related": [], 
    "pref_label": "Bibles / Nueva Version International / Study", 
    "notation": "BIB017050", 
    "alt_label": []
  }, 
  "Performing Arts / Theater / Broadway & Musical Revue": {
    "related": [], 
    "pref_label": "Performing Arts / Theater / Broadway & Musical Revue", 
    "notation": "PER013000", 
    "alt_label": [
      "Performing Arts / Broadway & Musical Revue"
    ]
  }, 
  "Business & Economics / Accounting / Managerial": {
    "related": [], 
    "pref_label": "Business & Economics / Accounting / Managerial", 
    "notation": "BUS001040", 
    "alt_label": []
  }, 
  "Bibles / New King James Version / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / New King James Version / New Testament & Portions", 
    "notation": "BIB014030", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Italian": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Italian", 
    "notation": "CKB047000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Glass & Glassware": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Glass & Glassware", 
    "notation": "ANT018000", 
    "alt_label": [
      "Antiques & Collectibles / Stained Glass"
    ]
  }, 
  "Education / Teaching Methods & Materials / Health & Sexuality": {
    "related": [], 
    "pref_label": "Education / Teaching Methods & Materials / Health & Sexuality", 
    "notation": "EDU029070", 
    "alt_label": []
  }, 
  "Bibles / Common English Bible / Study": {
    "related": [], 
    "pref_label": "Bibles / Common English Bible / Study", 
    "notation": "BIB022050", 
    "alt_label": []
  }, 
  "Technology & Engineering / Construction / Carpentry": {
    "related": [], 
    "pref_label": "Technology & Engineering / Construction / Carpentry", 
    "notation": "TEC005010", 
    "alt_label": []
  }, 
  "History / Holocaust": {
    "related": [], 
    "pref_label": "History / Holocaust", 
    "notation": "HIS043000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / United States / Colonial & Revolutionary Periods": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / United States / Colonial & Revolutionary Periods", 
    "notation": "JNF025190", 
    "alt_label": []
  }, 
  "Business & Economics / Investments & Securities / Bonds": {
    "related": [], 
    "pref_label": "Business & Economics / Investments & Securities / Bonds", 
    "notation": "BUS036010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Toys, Dolls & Puppets": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Toys, Dolls & Puppets", 
    "notation": "JNF056000", 
    "alt_label": [
      "Juvenile Nonfiction / Dolls", 
      "Juvenile Nonfiction / Puppets"
    ]
  }, 
  "Computers / Certification Guides / Mcse": {
    "related": [], 
    "pref_label": "Computers / Certification Guides / Mcse", 
    "notation": "COM055020", 
    "alt_label": []
  }, 
  "Architecture / Design, Drafting, Drawing & Presentation": {
    "related": [], 
    "pref_label": "Architecture / Design, Drafting, Drawing & Presentation", 
    "notation": "ARC004000", 
    "alt_label": [
      "Architecture / Cad (computer Aided Design)"
    ]
  }, 
  "Juvenile Fiction / People & Places / Canada / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Canada / General", 
    "notation": "JUV030030", 
    "alt_label": []
  }, 
  "Computers / Web / Page Design": {
    "related": [], 
    "pref_label": "Computers / Web / Page Design", 
    "notation": "COM060060", 
    "alt_label": []
  }, 
  "Family & Relationships / Death, Grief, Bereavement": {
    "related": [], 
    "pref_label": "Family & Relationships / Death, Grief, Bereavement", 
    "notation": "FAM014000", 
    "alt_label": [
      "Family & Relationships / Bereavement", 
      "Family & Relationships / Grief"
    ]
  }, 
  "Travel / Middle East / Egypt": {
    "related": [], 
    "pref_label": "Travel / Middle East / Egypt", 
    "notation": "TRV015010", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Baby Animals": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Baby Animals", 
    "notation": "JNF003330", 
    "alt_label": []
  }, 
  "Gardening / Climatic / Desert": {
    "related": [], 
    "pref_label": "Gardening / Climatic / Desert", 
    "notation": "GAR027010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / General", 
    "notation": "JUV000000", 
    "alt_label": []
  }, 
  "Computers / Microprocessors": {
    "related": [], 
    "pref_label": "Computers / Microprocessors", 
    "notation": "COM041000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Humorous Stories": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Humorous Stories", 
    "notation": "JUV019000", 
    "alt_label": []
  }, 
  "Photography / Individual Photographers / Essays": {
    "related": [], 
    "pref_label": "Photography / Individual Photographers / Essays", 
    "notation": "PHO011020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Drugs, Alcohol, Substance Abuse": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Drugs, Alcohol, Substance Abuse", 
    "notation": "JUV039040", 
    "alt_label": [
      "Juvenile Fiction / Social Issues / Substance Abuse"
    ]
  }, 
  "Political Science / Public Policy / Communication Policy": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Communication Policy", 
    "notation": "POL050000", 
    "alt_label": []
  }, 
  "Law / Contracts": {
    "related": [], 
    "pref_label": "Law / Contracts", 
    "notation": "LAW021000", 
    "alt_label": []
  }, 
  "Science / Earth Sciences / Sedimentology & Stratigraphy": {
    "related": [], 
    "pref_label": "Science / Earth Sciences / Sedimentology & Stratigraphy", 
    "notation": "SCI091000", 
    "alt_label": []
  }, 
  "Nature / Animals / Mammals": {
    "related": [], 
    "pref_label": "Nature / Animals / Mammals", 
    "notation": "NAT019000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Mechanical": {
    "related": [], 
    "pref_label": "Technology & Engineering / Mechanical", 
    "notation": "TEC009070", 
    "alt_label": []
  }, 
  "Nature / Ecosystems & Habitats / General": {
    "related": [], 
    "pref_label": "Nature / Ecosystems & Habitats / General", 
    "notation": "NAT045000", 
    "alt_label": []
  }, 
  "Science / Chemistry / Computational & Molecular Modeling": {
    "related": [], 
    "pref_label": "Science / Chemistry / Computational & Molecular Modeling", 
    "notation": "SCI013070", 
    "alt_label": []
  }, 
  "Sports & Recreation / Rugby": {
    "related": [], 
    "pref_label": "Sports & Recreation / Rugby", 
    "notation": "SPO056000", 
    "alt_label": []
  }, 
  "Business & Economics / Personal Finance / Retirement Planning": {
    "related": [], 
    "pref_label": "Business & Economics / Personal Finance / Retirement Planning", 
    "notation": "BUS050040", 
    "alt_label": []
  }, 
  "Computers / Bioinformatics": {
    "related": [], 
    "pref_label": "Computers / Bioinformatics", 
    "notation": "COM082000", 
    "alt_label": []
  }, 
  "Education / Special Education / Social Disabilities": {
    "related": [], 
    "pref_label": "Education / Special Education / Social Disabilities", 
    "notation": "EDU026050", 
    "alt_label": []
  }, 
  "Nature / Animals / Insects & Spiders": {
    "related": [], 
    "pref_label": "Nature / Animals / Insects & Spiders", 
    "notation": "NAT017000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Mobiles": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Mobiles", 
    "notation": "CRA019000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Holocaust": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Holocaust", 
    "notation": "JNF025090", 
    "alt_label": []
  }, 
  "Travel / Asia / Far East": {
    "related": [], 
    "pref_label": "Travel / Asia / Far East", 
    "notation": "TRV003030", 
    "alt_label": []
  }, 
  "Fiction / Fairy Tales, Folk Tales, Legends & Mythology": {
    "related": [], 
    "pref_label": "Fiction / Fairy Tales, Folk Tales, Legends & Mythology", 
    "notation": "FIC010000", 
    "alt_label": [
      "Fiction / Folklore", 
      "Fiction / Mythology"
    ]
  }, 
  "Antiques & Collectibles / Sports Cards / Basketball": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Sports Cards / Basketball", 
    "notation": "ANT042020", 
    "alt_label": []
  }, 
  "Psychology / Developmental / Child": {
    "related": [], 
    "pref_label": "Psychology / Developmental / Child", 
    "notation": "PSY004000", 
    "alt_label": []
  }, 
  "Medical / Allied Health Services / Physical Therapy": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / Physical Therapy", 
    "notation": "MED003060", 
    "alt_label": []
  }, 
  "Sports & Recreation / Canoeing": {
    "related": [], 
    "pref_label": "Sports & Recreation / Canoeing", 
    "notation": "SPO010000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Family / Orphans & Foster Homes": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Family / Orphans & Foster Homes", 
    "notation": "JNF019050", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Halloween": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Halloween", 
    "notation": "JUV017030", 
    "alt_label": []
  }, 
  "Mathematics / Geometry / Analytic": {
    "related": [], 
    "pref_label": "Mathematics / Geometry / Analytic", 
    "notation": "MAT012020", 
    "alt_label": []
  }, 
  "Technology & Engineering / Pest Control": {
    "related": [], 
    "pref_label": "Technology & Engineering / Pest Control", 
    "notation": "TEC058000", 
    "alt_label": [
      "Technology & Engineering / Agriculture / Pest Control"
    ]
  }, 
  "Crafts & Hobbies / Jewelry": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Jewelry", 
    "notation": "CRA014000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Mysteries & Detective Stories": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Mysteries & Detective Stories", 
    "notation": "JUV033180", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Reference / Dictionaries": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Reference / Dictionaries", 
    "notation": "JNF048030", 
    "alt_label": []
  }, 
  "Games / Gambling / Track Betting": {
    "related": [], 
    "pref_label": "Games / Gambling / Track Betting", 
    "notation": "GAM004040", 
    "alt_label": []
  }, 
  "Pets / Fish & Aquariums": {
    "related": [], 
    "pref_label": "Pets / Fish & Aquariums", 
    "notation": "PET005000", 
    "alt_label": [
      "Pets / Aquarium"
    ]
  }, 
  "Games / Crosswords / General": {
    "related": [], 
    "pref_label": "Games / Crosswords / General", 
    "notation": "GAM003000", 
    "alt_label": []
  }, 
  "Games / Gambling / Lotteries": {
    "related": [], 
    "pref_label": "Games / Gambling / Lotteries", 
    "notation": "GAM004020", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Fruit": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Fruit", 
    "notation": "CKB035000", 
    "alt_label": []
  }, 
  "Law / Legal Writing": {
    "related": [], 
    "pref_label": "Law / Legal Writing", 
    "notation": "LAW063000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Art": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Art", 
    "notation": "ANT002000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Civil / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / Civil / General", 
    "notation": "TEC009020", 
    "alt_label": []
  }, 
  "Music / Instruction & Study / Appreciation": {
    "related": [], 
    "pref_label": "Music / Instruction & Study / Appreciation", 
    "notation": "MUS001000", 
    "alt_label": []
  }, 
  "Literary Collections / American / General": {
    "related": [], 
    "pref_label": "Literary Collections / American / General", 
    "notation": "LCO002000", 
    "alt_label": []
  }, 
  "Self-help / Inner Child": {
    "related": [], 
    "pref_label": "Self-help / Inner Child", 
    "notation": "SEL018000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Gardening": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Gardening", 
    "notation": "JNF022000", 
    "alt_label": []
  }, 
  "Travel / Maps & Road Atlases": {
    "related": [], 
    "pref_label": "Travel / Maps & Road Atlases", 
    "notation": "TRV027000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Baltic Languages": {
    "related": [], 
    "pref_label": "Foreign Language Study / Baltic Languages", 
    "notation": "FOR034000", 
    "alt_label": []
  }, 
  "Music / Lyrics": {
    "related": [], 
    "pref_label": "Music / Lyrics", 
    "notation": "MUS052000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Action & Adventure / Survival Stories": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Action & Adventure / Survival Stories", 
    "notation": "JUV001010", 
    "alt_label": []
  }, 
  "Law / Court Records": {
    "related": [], 
    "pref_label": "Law / Court Records", 
    "notation": "LAW023000", 
    "alt_label": []
  }, 
  "Science / Space Science": {
    "related": [], 
    "pref_label": "Science / Space Science", 
    "notation": "SCI098000", 
    "alt_label": []
  }, 
  "Social Science / Demography": {
    "related": [], 
    "pref_label": "Social Science / Demography", 
    "notation": "SOC006000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Linguistics / General": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Linguistics / General", 
    "notation": "LAN009000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Baseball & Softball": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Baseball & Softball", 
    "notation": "JUV032010", 
    "alt_label": []
  }, 
  "Law / Intellectual Property / Trademark": {
    "related": [], 
    "pref_label": "Law / Intellectual Property / Trademark", 
    "notation": "LAW050030", 
    "alt_label": [
      "Law / Trademark"
    ]
  }, 
  "Cooking / Beverages / General": {
    "related": [], 
    "pref_label": "Cooking / Beverages / General", 
    "notation": "CKB100000", 
    "alt_label": []
  }, 
  "Nature / Ecology": {
    "related": [], 
    "pref_label": "Nature / Ecology", 
    "notation": "NAT010000", 
    "alt_label": []
  }, 
  "Religion / Christian Life / General": {
    "related": [], 
    "pref_label": "Religion / Christian Life / General", 
    "notation": "REL012000", 
    "alt_label": []
  }, 
  "Art / Individual Artists / General": {
    "related": [], 
    "pref_label": "Art / Individual Artists / General", 
    "notation": "ART016000", 
    "alt_label": []
  }, 
  "Mathematics / Probability & Statistics / Time Series": {
    "related": [], 
    "pref_label": "Mathematics / Probability & Statistics / Time Series", 
    "notation": "MAT029050", 
    "alt_label": []
  }, 
  "Design / Clip Art": {
    "related": [], 
    "pref_label": "Design / Clip Art", 
    "notation": "DES002000", 
    "alt_label": []
  }, 
  "Religion / Biblical Meditations / New Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Meditations / New Testament", 
    "notation": "REL006130", 
    "alt_label": []
  }, 
  "Literary Collections / Speeches": {
    "related": [], 
    "pref_label": "Literary Collections / Speeches", 
    "notation": "LCO018000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / American / Northwestern States": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / American / Northwestern States", 
    "notation": "CKB002050", 
    "alt_label": []
  }, 
  "Religion / Judaism / Reform": {
    "related": [], 
    "pref_label": "Religion / Judaism / Reform", 
    "notation": "REL040080", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Nature & The Natural World / Weather": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Nature & The Natural World / Weather", 
    "notation": "JUV029020", 
    "alt_label": []
  }, 
  "Philosophy / History & Surveys / General": {
    "related": [], 
    "pref_label": "Philosophy / History & Surveys / General", 
    "notation": "PHI009000", 
    "alt_label": []
  }, 
  "History / United States / 20th Century": {
    "related": [], 
    "pref_label": "History / United States / 20th Century", 
    "notation": "HIS036060", 
    "alt_label": []
  }, 
  "Performing Arts / Business Aspects": {
    "related": [], 
    "pref_label": "Performing Arts / Business Aspects", 
    "notation": "PER014000", 
    "alt_label": []
  }, 
  "True Crime / Espionage": {
    "related": [], 
    "pref_label": "True Crime / Espionage", 
    "notation": "TRU001000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religious / Christian / Science & Nature": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religious / Christian / Science & Nature", 
    "notation": "JNF049280", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Transportation / Cars & Trucks": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Transportation / Cars & Trucks", 
    "notation": "JNF057030", 
    "alt_label": []
  }, 
  "Social Science / Social Classes": {
    "related": [], 
    "pref_label": "Social Science / Social Classes", 
    "notation": "SOC050000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Afterlife & Reincarnation": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Afterlife & Reincarnation", 
    "notation": "OCC022000", 
    "alt_label": []
  }, 
  "Fiction / Lesbian": {
    "related": [], 
    "pref_label": "Fiction / Lesbian", 
    "notation": "FIC018000", 
    "alt_label": []
  }, 
  "Business & Economics / Facility Management": {
    "related": [], 
    "pref_label": "Business & Economics / Facility Management", 
    "notation": "BUS093000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Fantasy": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Fantasy", 
    "notation": "CGN004030", 
    "alt_label": []
  }, 
  "Games / Puzzles": {
    "related": [], 
    "pref_label": "Games / Puzzles", 
    "notation": "GAM007000", 
    "alt_label": []
  }, 
  "Games / Chess": {
    "related": [], 
    "pref_label": "Games / Chess", 
    "notation": "GAM001030", 
    "alt_label": [
      "Games / Board / Chess"
    ]
  }, 
  "Social Science / Violence In Society": {
    "related": [], 
    "pref_label": "Social Science / Violence In Society", 
    "notation": "SOC051000", 
    "alt_label": []
  }, 
  "Games / Magic": {
    "related": [], 
    "pref_label": "Games / Magic", 
    "notation": "GAM006000", 
    "alt_label": []
  }, 
  "Health & Fitness / Children's Health": {
    "related": [], 
    "pref_label": "Health & Fitness / Children's Health", 
    "notation": "HEA046000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Rugs": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Rugs", 
    "notation": "CRA033000", 
    "alt_label": []
  }, 
  "Bibles / King James Version / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / King James Version / Youth & Teen", 
    "notation": "BIB006070", 
    "alt_label": []
  }, 
  "Business & Economics / New Business Enterprises": {
    "related": [], 
    "pref_label": "Business & Economics / New Business Enterprises", 
    "notation": "BUS048000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / Holocaust": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / Holocaust", 
    "notation": "JUV016060", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Values & Virtues": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Values & Virtues", 
    "notation": "JUV039220", 
    "alt_label": []
  }, 
  "Education / Special Education / Physical Disabilities": {
    "related": [], 
    "pref_label": "Education / Special Education / Physical Disabilities", 
    "notation": "EDU026040", 
    "alt_label": []
  }, 
  "Education / Comparative": {
    "related": [], 
    "pref_label": "Education / Comparative", 
    "notation": "EDU043000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Homelessness & Poverty": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Homelessness & Poverty", 
    "notation": "JUV039070", 
    "alt_label": []
  }, 
  "Mathematics / Finite Mathematics": {
    "related": [], 
    "pref_label": "Mathematics / Finite Mathematics", 
    "notation": "MAT009000", 
    "alt_label": []
  }, 
  "Literary Collections / Medieval": {
    "related": [], 
    "pref_label": "Literary Collections / Medieval", 
    "notation": "LCO017000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Adolescence": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Adolescence", 
    "notation": "JUV039020", 
    "alt_label": []
  }, 
  "Medical / Allied Health Services / Occupational Therapy": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / Occupational Therapy", 
    "notation": "MED003050", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Sports & Recreation / Games": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Sports & Recreation / Games", 
    "notation": "JUV032040", 
    "alt_label": [
      "Juvenile Fiction / Games"
    ]
  }, 
  "Computers / System Administration / Disaster & Recovery": {
    "related": [], 
    "pref_label": "Computers / System Administration / Disaster & Recovery", 
    "notation": "COM019000", 
    "alt_label": [
      "Computers / Data Recovery"
    ]
  }, 
  "Religion / Sermons / Jewish": {
    "related": [], 
    "pref_label": "Religion / Sermons / Jewish", 
    "notation": "REL058020", 
    "alt_label": []
  }, 
  "Medical / Otorhinolaryngology": {
    "related": [], 
    "pref_label": "Medical / Otorhinolaryngology", 
    "notation": "MED066000", 
    "alt_label": []
  }, 
  "Transportation / Motorcycles / History": {
    "related": [], 
    "pref_label": "Transportation / Motorcycles / History", 
    "notation": "TRA003010", 
    "alt_label": []
  }, 
  "Travel / Europe / Spain & Portugal": {
    "related": [], 
    "pref_label": "Travel / Europe / Spain & Portugal", 
    "notation": "TRV009130", 
    "alt_label": []
  }, 
  "Computers / Operating Systems / Windows Workstation": {
    "related": [], 
    "pref_label": "Computers / Operating Systems / Windows Workstation", 
    "notation": "COM046040", 
    "alt_label": []
  }, 
  "Business & Economics / Investments & Securities / Real Estate": {
    "related": [], 
    "pref_label": "Business & Economics / Investments & Securities / Real Estate", 
    "notation": "BUS036050", 
    "alt_label": []
  }, 
  "Computers / Desktop Applications / Personal Finance Applications": {
    "related": [], 
    "pref_label": "Computers / Desktop Applications / Personal Finance Applications", 
    "notation": "COM027000", 
    "alt_label": []
  }, 
  "Law / Intellectual Property / Patent": {
    "related": [], 
    "pref_label": "Law / Intellectual Property / Patent", 
    "notation": "LAW050020", 
    "alt_label": [
      "Law / Patent"
    ]
  }, 
  "Technology & Engineering / Electronics / Circuits / Logic": {
    "related": [], 
    "pref_label": "Technology & Engineering / Electronics / Circuits / Logic", 
    "notation": "TEC008030", 
    "alt_label": []
  }, 
  "Science / Essays": {
    "related": [], 
    "pref_label": "Science / Essays", 
    "notation": "SCI080000", 
    "alt_label": []
  }, 
  "Gardening / Flowers / Annuals": {
    "related": [], 
    "pref_label": "Gardening / Flowers / Annuals", 
    "notation": "GAR004010", 
    "alt_label": [
      "Gardening / Flowers / Violets"
    ]
  }, 
  "Bibles / International Children's Bible / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / International Children's Bible / New Testament & Portions", 
    "notation": "BIB005030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Strangers": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Strangers", 
    "notation": "JNF053260", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / United States / 21st Century": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / United States / 21st Century", 
    "notation": "JUV016190", 
    "alt_label": []
  }, 
  "Philosophy / Taoist": {
    "related": [], 
    "pref_label": "Philosophy / Taoist", 
    "notation": "PHI023000", 
    "alt_label": []
  }, 
  "Medical / Allied Health Services / General": {
    "related": [], 
    "pref_label": "Medical / Allied Health Services / General", 
    "notation": "MED003000", 
    "alt_label": []
  }, 
  "Family & Relationships / Ethics & Morals": {
    "related": [], 
    "pref_label": "Family & Relationships / Ethics & Morals", 
    "notation": "FAM031000", 
    "alt_label": []
  }, 
  "Foreign Language Study / Creole Languages": {
    "related": [], 
    "pref_label": "Foreign Language Study / Creole Languages", 
    "notation": "FOR035000", 
    "alt_label": []
  }, 
  "Transportation / Automotive / Buyer's Guides": {
    "related": [], 
    "pref_label": "Transportation / Automotive / Buyer's Guides", 
    "notation": "TRA001020", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Holidays & Celebrations / Valentine's Day": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Holidays & Celebrations / Valentine's Day", 
    "notation": "JUV017070", 
    "alt_label": []
  }, 
  "Nature / Environmental Conservation & Protection": {
    "related": [], 
    "pref_label": "Nature / Environmental Conservation & Protection", 
    "notation": "NAT011000", 
    "alt_label": []
  }, 
  "Art / Art & Politics": {
    "related": [], 
    "pref_label": "Art / Art & Politics", 
    "notation": "ART037000", 
    "alt_label": []
  }, 
  "Religion / Spirituality": {
    "related": [], 
    "pref_label": "Religion / Spirituality", 
    "notation": "REL062000", 
    "alt_label": []
  }, 
  "Health & Fitness / Diseases / Immune System": {
    "related": [], 
    "pref_label": "Health & Fitness / Diseases / Immune System", 
    "notation": "HEA039090", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / New Experience": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / New Experience", 
    "notation": "JUV039090", 
    "alt_label": []
  }, 
  "Computers / Digital Media / Graphics Applications": {
    "related": [], 
    "pref_label": "Computers / Digital Media / Graphics Applications", 
    "notation": "COM087020", 
    "alt_label": []
  }, 
  "Religion / Hinduism / Rituals & Practice": {
    "related": [], 
    "pref_label": "Religion / Hinduism / Rituals & Practice", 
    "notation": "REL032020", 
    "alt_label": []
  }, 
  "Religion / Christian Rituals & Practice / Sacraments": {
    "related": [], 
    "pref_label": "Religion / Christian Rituals & Practice / Sacraments", 
    "notation": "REL055010", 
    "alt_label": []
  }, 
  "Fiction / Amish & Mennonite": {
    "related": [], 
    "pref_label": "Fiction / Amish & Mennonite", 
    "notation": "FIC053000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Pool, Billiards, Snooker": {
    "related": [], 
    "pref_label": "Sports & Recreation / Pool, Billiards, Snooker", 
    "notation": "SPO060000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / C++": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / C++", 
    "notation": "COM051070", 
    "alt_label": []
  }, 
  "Family & Relationships / Parenting / Motherhood": {
    "related": [], 
    "pref_label": "Family & Relationships / Parenting / Motherhood", 
    "notation": "FAM032000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Lacrosse": {
    "related": [], 
    "pref_label": "Sports & Recreation / Lacrosse", 
    "notation": "SPO026000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Astrology / Horoscopes": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Astrology / Horoscopes", 
    "notation": "OCC009000", 
    "alt_label": []
  }, 
  "Science / Global Warming & Climate Change": {
    "related": [], 
    "pref_label": "Science / Global Warming & Climate Change", 
    "notation": "SCI092000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Orthodox": {
    "related": [], 
    "pref_label": "Religion / Christianity / Orthodox", 
    "notation": "REL049000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Holidays & Celebrations / Other, Religious": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Holidays & Celebrations / Other, Religious", 
    "notation": "JNF026090", 
    "alt_label": []
  }, 
  "Science / Cosmology": {
    "related": [], 
    "pref_label": "Science / Cosmology", 
    "notation": "SCI015000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Comics & Graphic Novels / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Comics & Graphic Novels / General", 
    "notation": "JNF062000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Literary Criticism & Collections": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Literary Criticism & Collections", 
    "notation": "JNF034000", 
    "alt_label": []
  }, 
  "History / Africa / North": {
    "related": [], 
    "pref_label": "History / Africa / North", 
    "notation": "HIS001030", 
    "alt_label": []
  }, 
  "History / Military / Veterans": {
    "related": [], 
    "pref_label": "History / Military / Veterans", 
    "notation": "HIS027120", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Body, Mind & Spirit": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Body, Mind & Spirit", 
    "notation": "JNF008000", 
    "alt_label": [
      "Juvenile Nonfiction / Metaphysical"
    ]
  }, 
  "Biography & Autobiography / Literary": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Literary", 
    "notation": "BIO007000", 
    "alt_label": []
  }, 
  "Computers / Programming / Object Oriented": {
    "related": [], 
    "pref_label": "Computers / Programming / Object Oriented", 
    "notation": "COM051210", 
    "alt_label": []
  }, 
  "Religion / Judaism / Rituals & Practice": {
    "related": [], 
    "pref_label": "Religion / Judaism / Rituals & Practice", 
    "notation": "REL040010", 
    "alt_label": [
      "Religion / Jewish Life"
    ]
  }, 
  "Juvenile Nonfiction / History / Europe": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Europe", 
    "notation": "JNF025070", 
    "alt_label": []
  }, 
  "Sports & Recreation / Scuba & Snorkeling": {
    "related": [], 
    "pref_label": "Sports & Recreation / Scuba & Snorkeling", 
    "notation": "SPO059000", 
    "alt_label": [
      "Sports & Recreation / Snorkeling"
    ]
  }, 
  "Fiction / Romance / Science Fiction": {
    "related": [], 
    "pref_label": "Fiction / Romance / Science Fiction", 
    "notation": "FIC027130", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Adventure & Adventurers": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Adventure & Adventurers", 
    "notation": "JNF002000", 
    "alt_label": []
  }, 
  "Art / Middle Eastern": {
    "related": [], 
    "pref_label": "Art / Middle Eastern", 
    "notation": "ART047000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Bullying": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Bullying", 
    "notation": "JNF053220", 
    "alt_label": []
  }, 
  "Fiction / Mystery & Detective / Historical": {
    "related": [], 
    "pref_label": "Fiction / Mystery & Detective / Historical", 
    "notation": "FIC022060", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Performing Arts / Circus": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Performing Arts / Circus", 
    "notation": "JUV031010", 
    "alt_label": [
      "Juvenile Fiction / Circus"
    ]
  }, 
  "Science / Cognitive Science": {
    "related": [], 
    "pref_label": "Science / Cognitive Science", 
    "notation": "SCI090000", 
    "alt_label": []
  }, 
  "Religion / Islam / Sunni": {
    "related": [], 
    "pref_label": "Religion / Islam / Sunni", 
    "notation": "REL037050", 
    "alt_label": []
  }, 
  "Religion / History": {
    "related": [], 
    "pref_label": "Religion / History", 
    "notation": "REL033000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Papercrafts": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Papercrafts", 
    "notation": "CRA025000", 
    "alt_label": []
  }, 
  "Political Science / International Relations / Treaties": {
    "related": [], 
    "pref_label": "Political Science / International Relations / Treaties", 
    "notation": "POL021000", 
    "alt_label": []
  }, 
  "Law / Ethics & Professional Responsibility": {
    "related": [], 
    "pref_label": "Law / Ethics & Professional Responsibility", 
    "notation": "LAW036000", 
    "alt_label": [
      "Law / Professional Responsibility"
    ]
  }, 
  "Cooking / Regional & Ethnic / Central American & South American": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Central American & South American", 
    "notation": "CKB099000", 
    "alt_label": [
      "Cooking / Regional & Ethnic / Latin American", 
      "Cooking / Regional & Ethnic / South American"
    ]
  }, 
  "Juvenile Nonfiction / Business & Economics": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Business & Economics", 
    "notation": "JNF010000", 
    "alt_label": [
      "Juvenile Nonfiction / Economics"
    ]
  }, 
  "Language Arts & Disciplines / Reading Skills": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Reading Skills", 
    "notation": "LAN013000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Kayaking": {
    "related": [], 
    "pref_label": "Sports & Recreation / Kayaking", 
    "notation": "SPO025000", 
    "alt_label": []
  }, 
  "Nature / General": {
    "related": [], 
    "pref_label": "Nature / General", 
    "notation": "NAT000000", 
    "alt_label": []
  }, 
  "Drama / Gay & Lesbian": {
    "related": [], 
    "pref_label": "Drama / Gay & Lesbian", 
    "notation": "DRA017000", 
    "alt_label": []
  }, 
  "Law / Criminal Law / Juvenile Offenders": {
    "related": [], 
    "pref_label": "Law / Criminal Law / Juvenile Offenders", 
    "notation": "LAW026010", 
    "alt_label": []
  }, 
  "Bibles / New Living Translation / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / New Living Translation / New Testament & Portions", 
    "notation": "BIB015030", 
    "alt_label": []
  }, 
  "Bibles / International Children's Bible / Children": {
    "related": [], 
    "pref_label": "Bibles / International Children's Bible / Children", 
    "notation": "BIB005010", 
    "alt_label": []
  }, 
  "Literary Criticism / Shakespeare": {
    "related": [], 
    "pref_label": "Literary Criticism / Shakespeare", 
    "notation": "LIT015000", 
    "alt_label": [
      "Literary Criticism / European / English, Irish, Scottish, Welsh / Shakespeare"
    ]
  }, 
  "Pets / Birds": {
    "related": [], 
    "pref_label": "Pets / Birds", 
    "notation": "PET002000", 
    "alt_label": []
  }, 
  "Photography / Subjects & Themes / Celebrations & Events": {
    "related": [], 
    "pref_label": "Photography / Subjects & Themes / Celebrations & Events", 
    "notation": "PHO023070", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Middle East": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Middle East", 
    "notation": "JNF025120", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Health & Daily Living / Maturing": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Health & Daily Living / Maturing", 
    "notation": "JNF024050", 
    "alt_label": []
  }, 
  "Literary Criticism / Asian / Japanese": {
    "related": [], 
    "pref_label": "Literary Criticism / Asian / Japanese", 
    "notation": "LIT008030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Curiosities & Wonders": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Curiosities & Wonders", 
    "notation": "JNF016000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Art / History": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Art / History", 
    "notation": "JNF006040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Health & Daily Living / Diseases, Illnesses & Injuries": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Health & Daily Living / Diseases, Illnesses & Injuries", 
    "notation": "JUV015020", 
    "alt_label": []
  }, 
  "Education / Special Education / Gifted": {
    "related": [], 
    "pref_label": "Education / Special Education / Gifted", 
    "notation": "EDU026060", 
    "alt_label": []
  }, 
  "Medical / Nursing / Issues": {
    "related": [], 
    "pref_label": "Medical / Nursing / Issues", 
    "notation": "MED058090", 
    "alt_label": []
  }, 
  "Religion / Christian Education / Children & Youth": {
    "related": [], 
    "pref_label": "Religion / Christian Education / Children & Youth", 
    "notation": "REL091000", 
    "alt_label": []
  }, 
  "Gardening / Vegetables": {
    "related": [], 
    "pref_label": "Gardening / Vegetables", 
    "notation": "GAR025000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Transportation / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Transportation / General", 
    "notation": "JNF057000", 
    "alt_label": []
  }, 
  "Business & Economics / Careers / Job Hunting": {
    "related": [], 
    "pref_label": "Business & Economics / Careers / Job Hunting", 
    "notation": "BUS037020", 
    "alt_label": [
      "Business & Economics / Job Hunting"
    ]
  }, 
  "History / Latin America / General": {
    "related": [], 
    "pref_label": "History / Latin America / General", 
    "notation": "HIS024000", 
    "alt_label": []
  }, 
  "Bibles / Nueva Version International / General": {
    "related": [], 
    "pref_label": "Bibles / Nueva Version International / General", 
    "notation": "BIB017000", 
    "alt_label": []
  }, 
  "Music / Instruction & Study / General": {
    "related": [], 
    "pref_label": "Music / Instruction & Study / General", 
    "notation": "MUS022000", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / General": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / General", 
    "notation": "CKB105000", 
    "alt_label": []
  }, 
  "Fiction / Romance / Regency": {
    "related": [], 
    "pref_label": "Fiction / Romance / Regency", 
    "notation": "FIC027070", 
    "alt_label": []
  }, 
  "Law / Right To Die": {
    "related": [], 
    "pref_label": "Law / Right To Die", 
    "notation": "LAW082000", 
    "alt_label": [
      "Law / Living Wills"
    ]
  }, 
  "Philosophy / History & Surveys / Renaissance": {
    "related": [], 
    "pref_label": "Philosophy / History & Surveys / Renaissance", 
    "notation": "PHI037000", 
    "alt_label": []
  }, 
  "Education / General": {
    "related": [], 
    "pref_label": "Education / General", 
    "notation": "EDU000000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Concepts / Sense & Sensation": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Concepts / Sense & Sensation", 
    "notation": "JNF013060", 
    "alt_label": []
  }, 
  "Bibles / Nueva Version International / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / Nueva Version International / New Testament & Portions", 
    "notation": "BIB017030", 
    "alt_label": []
  }, 
  "Computers / Database Management / Data Mining": {
    "related": [], 
    "pref_label": "Computers / Database Management / Data Mining", 
    "notation": "COM021030", 
    "alt_label": []
  }, 
  "Technology & Engineering / Construction / Estimating": {
    "related": [], 
    "pref_label": "Technology & Engineering / Construction / Estimating", 
    "notation": "TEC005040", 
    "alt_label": []
  }, 
  "Education / Urban": {
    "related": [], 
    "pref_label": "Education / Urban", 
    "notation": "EDU054000", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Weaving": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Weaving", 
    "notation": "CRA040000", 
    "alt_label": []
  }, 
  "Art / Graffiti & Street Art": {
    "related": [], 
    "pref_label": "Art / Graffiti & Street Art", 
    "notation": "ART058000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Vocabulary": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Vocabulary", 
    "notation": "LAN021000", 
    "alt_label": []
  }, 
  "Political Science / World / African": {
    "related": [], 
    "pref_label": "Political Science / World / African", 
    "notation": "POL053000", 
    "alt_label": []
  }, 
  "Gardening / Lawns": {
    "related": [], 
    "pref_label": "Gardening / Lawns", 
    "notation": "GAR015000", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Perl": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Perl", 
    "notation": "COM051350", 
    "alt_label": []
  }, 
  "Sports & Recreation / Rodeos": {
    "related": [], 
    "pref_label": "Sports & Recreation / Rodeos", 
    "notation": "SPO065000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / International": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / International", 
    "notation": "CKB045000", 
    "alt_label": []
  }, 
  "Education / Essays": {
    "related": [], 
    "pref_label": "Education / Essays", 
    "notation": "EDU042000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Religious": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Religious", 
    "notation": "BIO018000", 
    "alt_label": []
  }, 
  "Literary Collections / Essays": {
    "related": [], 
    "pref_label": "Literary Collections / Essays", 
    "notation": "LCO010000", 
    "alt_label": []
  }, 
  "Performing Arts / Storytelling": {
    "related": [], 
    "pref_label": "Performing Arts / Storytelling", 
    "notation": "PER019000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Africa": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Africa", 
    "notation": "JNF025010", 
    "alt_label": []
  }, 
  "Business & Economics / Industries / Retailing": {
    "related": [], 
    "pref_label": "Business & Economics / Industries / Retailing", 
    "notation": "BUS057000", 
    "alt_label": [
      "Business & Economics / Retailing"
    ]
  }, 
  "Performing Arts / Dance / Classical & Ballet": {
    "related": [], 
    "pref_label": "Performing Arts / Dance / Classical & Ballet", 
    "notation": "PER003010", 
    "alt_label": []
  }, 
  "Mathematics / Optimization": {
    "related": [], 
    "pref_label": "Mathematics / Optimization", 
    "notation": "MAT042000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / People & Places / Caribbean & Latin America": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / People & Places / Caribbean & Latin America", 
    "notation": "JNF038050", 
    "alt_label": []
  }, 
  "Law / Government / General": {
    "related": [], 
    "pref_label": "Law / Government / General", 
    "notation": "LAW109000", 
    "alt_label": []
  }, 
  "Business & Economics / Corporate & Business History": {
    "related": [], 
    "pref_label": "Business & Economics / Corporate & Business History", 
    "notation": "BUS077000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Jungle Animals": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Jungle Animals", 
    "notation": "JNF003300", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Chemistry": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Chemistry", 
    "notation": "JNF051070", 
    "alt_label": []
  }, 
  "Sports & Recreation / Extreme Sports": {
    "related": [], 
    "pref_label": "Sports & Recreation / Extreme Sports", 
    "notation": "SPO064000", 
    "alt_label": []
  }, 
  "Business & Economics / Marketing / Direct": {
    "related": [], 
    "pref_label": "Business & Economics / Marketing / Direct", 
    "notation": "BUS043010", 
    "alt_label": []
  }, 
  "Law / Criminal Law / General": {
    "related": [], 
    "pref_label": "Law / Criminal Law / General", 
    "notation": "LAW026000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Machinery": {
    "related": [], 
    "pref_label": "Technology & Engineering / Machinery", 
    "notation": "TEC046000", 
    "alt_label": []
  }, 
  "Bibles / New American Bible / Reference": {
    "related": [], 
    "pref_label": "Bibles / New American Bible / Reference", 
    "notation": "BIB009040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Early Readers": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Early Readers", 
    "notation": "JUV033080", 
    "alt_label": []
  }, 
  "Religion / Christian Rituals & Practice / Worship & Liturgy": {
    "related": [], 
    "pref_label": "Religion / Christian Rituals & Practice / Worship & Liturgy", 
    "notation": "REL055020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Biblical Reference": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Biblical Reference", 
    "notation": "JNF049170", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Scrapbooking": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Scrapbooking", 
    "notation": "CRA052000", 
    "alt_label": []
  }, 
  "History / Modern / 20th Century": {
    "related": [], 
    "pref_label": "History / Modern / 20th Century", 
    "notation": "HIS037070", 
    "alt_label": []
  }, 
  "Gardening / Flowers / Bulbs": {
    "related": [], 
    "pref_label": "Gardening / Flowers / Bulbs", 
    "notation": "GAR004030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Language Arts / Grammar": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Language Arts / Grammar", 
    "notation": "JNF029020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Photography": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Photography", 
    "notation": "JNF041000", 
    "alt_label": []
  }, 
  "Games / Logic & Brain Teasers": {
    "related": [], 
    "pref_label": "Games / Logic & Brain Teasers", 
    "notation": "GAM005000", 
    "alt_label": []
  }, 
  "Architecture / History / Modern (late 19th Century To 1945)": {
    "related": [], 
    "pref_label": "Architecture / History / Modern (late 19th Century To 1945)", 
    "notation": "ARC005070", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Music / Rap & Hip Hop": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Music / Rap & Hip Hop", 
    "notation": "JNF036060", 
    "alt_label": []
  }, 
  "Music / Religious / Christian": {
    "related": [], 
    "pref_label": "Music / Religious / Christian", 
    "notation": "MUS048010", 
    "alt_label": []
  }, 
  "Technology & Engineering / Technical & Manufacturing Industries & Trades": {
    "related": [], 
    "pref_label": "Technology & Engineering / Technical & Manufacturing Industries & Trades", 
    "notation": "TEC040000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Media Tie-in": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Media Tie-in", 
    "notation": "CGN004160", 
    "alt_label": []
  }, 
  "Self-help / Eating Disorders": {
    "related": [], 
    "pref_label": "Self-help / Eating Disorders", 
    "notation": "SEL014000", 
    "alt_label": []
  }, 
  "House & Home / Security": {
    "related": [], 
    "pref_label": "House & Home / Security", 
    "notation": "HOM021000", 
    "alt_label": []
  }, 
  "Technology & Engineering / History": {
    "related": [], 
    "pref_label": "Technology & Engineering / History", 
    "notation": "TEC056000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Games & Activities / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Games & Activities / General", 
    "notation": "JNF021000", 
    "alt_label": []
  }, 
  "Bibles / International Children's Bible / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / International Children's Bible / Youth & Teen", 
    "notation": "BIB005070", 
    "alt_label": []
  }, 
  "Self-help / Self-hypnosis": {
    "related": [], 
    "pref_label": "Self-help / Self-hypnosis", 
    "notation": "SEL017000", 
    "alt_label": [
      "Self-help / Hypnotism"
    ]
  }, 
  "Reference / Trivia": {
    "related": [], 
    "pref_label": "Reference / Trivia", 
    "notation": "REF023000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Animals / Animal Welfare": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Animals / Animal Welfare", 
    "notation": "JNF003220", 
    "alt_label": []
  }, 
  "Medical / Nursing / Lpn & Lvn": {
    "related": [], 
    "pref_label": "Medical / Nursing / Lpn & Lvn", 
    "notation": "MED058100", 
    "alt_label": []
  }, 
  "Travel / Europe / Austria": {
    "related": [], 
    "pref_label": "Travel / Europe / Austria", 
    "notation": "TRV009010", 
    "alt_label": []
  }, 
  "Reference / Thesauri": {
    "related": [], 
    "pref_label": "Reference / Thesauri", 
    "notation": "REF022000", 
    "alt_label": [
      "Reference / Synonyms & Antonyms"
    ]
  }, 
  "Computers / Programming / Microsoft Programming": {
    "related": [], 
    "pref_label": "Computers / Programming / Microsoft Programming", 
    "notation": "COM051380", 
    "alt_label": []
  }, 
  "Philosophy / Movements / Idealism": {
    "related": [], 
    "pref_label": "Philosophy / Movements / Idealism", 
    "notation": "PHI042000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Australia & Oceania": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Australia & Oceania", 
    "notation": "JNF025040", 
    "alt_label": []
  }, 
  "Social Science / Philanthropy & Charity": {
    "related": [], 
    "pref_label": "Social Science / Philanthropy & Charity", 
    "notation": "SOC033000", 
    "alt_label": [
      "Social Science / Charity"
    ]
  }, 
  "Poetry / Ancient & Classical": {
    "related": [], 
    "pref_label": "Poetry / Ancient & Classical", 
    "notation": "POE008000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Industrial Design / Product": {
    "related": [], 
    "pref_label": "Technology & Engineering / Industrial Design / Product", 
    "notation": "TEC016020", 
    "alt_label": []
  }, 
  "History / Canada / General": {
    "related": [], 
    "pref_label": "History / Canada / General", 
    "notation": "HIS006000", 
    "alt_label": []
  }, 
  "Bibles / Nueva Version International / Children": {
    "related": [], 
    "pref_label": "Bibles / Nueva Version International / Children", 
    "notation": "BIB017010", 
    "alt_label": []
  }, 
  "Pets / Dogs / General": {
    "related": [], 
    "pref_label": "Pets / Dogs / General", 
    "notation": "PET004000", 
    "alt_label": []
  }, 
  "Bibles / New International Reader's Version / General": {
    "related": [], 
    "pref_label": "Bibles / New International Reader's Version / General", 
    "notation": "BIB012000", 
    "alt_label": []
  }, 
  "Religion / Christian Ministry / Preaching": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / Preaching", 
    "notation": "REL080000", 
    "alt_label": []
  }, 
  "Law / Agricultural": {
    "related": [], 
    "pref_label": "Law / Agricultural", 
    "notation": "LAW102000", 
    "alt_label": []
  }, 
  "Fiction / Sagas": {
    "related": [], 
    "pref_label": "Fiction / Sagas", 
    "notation": "FIC008000", 
    "alt_label": [
      "Fiction / Family Saga"
    ]
  }, 
  "Business & Economics / Mentoring & Coaching": {
    "related": [], 
    "pref_label": "Business & Economics / Mentoring & Coaching", 
    "notation": "BUS106000", 
    "alt_label": []
  }, 
  "Business & Economics / Time Management": {
    "related": [], 
    "pref_label": "Business & Economics / Time Management", 
    "notation": "BUS088000", 
    "alt_label": []
  }, 
  "Gardening / Flowers / General": {
    "related": [], 
    "pref_label": "Gardening / Flowers / General", 
    "notation": "GAR004000", 
    "alt_label": []
  }, 
  "Transportation / Automotive / Trucks": {
    "related": [], 
    "pref_label": "Transportation / Automotive / Trucks", 
    "notation": "TRA001150", 
    "alt_label": []
  }, 
  "Computers / System Administration / General": {
    "related": [], 
    "pref_label": "Computers / System Administration / General", 
    "notation": "COM088000", 
    "alt_label": []
  }, 
  "Religion / Buddhism / History": {
    "related": [], 
    "pref_label": "Religion / Buddhism / History", 
    "notation": "REL007010", 
    "alt_label": []
  }, 
  "Travel / Asia / Southwest": {
    "related": [], 
    "pref_label": "Travel / Asia / Southwest", 
    "notation": "TRV003070", 
    "alt_label": []
  }, 
  "Architecture / Security Design": {
    "related": [], 
    "pref_label": "Architecture / Security Design", 
    "notation": "ARC021000", 
    "alt_label": []
  }, 
  "Law / Remedies & Damages": {
    "related": [], 
    "pref_label": "Law / Remedies & Damages", 
    "notation": "LAW080000", 
    "alt_label": []
  }, 
  "Cooking / Courses & Dishes / Brunch": {
    "related": [], 
    "pref_label": "Cooking / Courses & Dishes / Brunch", 
    "notation": "CKB012000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Performing Arts / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Performing Arts / General", 
    "notation": "JNF039000", 
    "alt_label": []
  }, 
  "Social Science / Pornography": {
    "related": [], 
    "pref_label": "Social Science / Pornography", 
    "notation": "SOC034000", 
    "alt_label": []
  }, 
  "Religion / Holidays / General": {
    "related": [], 
    "pref_label": "Religion / Holidays / General", 
    "notation": "REL034000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Turkish": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Turkish", 
    "notation": "CKB084000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Family / Orphans & Foster Homes": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Family / Orphans & Foster Homes", 
    "notation": "JUV013050", 
    "alt_label": []
  }, 
  "Business & Economics / Negotiating": {
    "related": [], 
    "pref_label": "Business & Economics / Negotiating", 
    "notation": "BUS047000", 
    "alt_label": []
  }, 
  "Poetry / European / Spanish & Portuguese": {
    "related": [], 
    "pref_label": "Poetry / European / Spanish & Portuguese", 
    "notation": "POE020000", 
    "alt_label": []
  }, 
  "Science / Nanoscience": {
    "related": [], 
    "pref_label": "Science / Nanoscience", 
    "notation": "SCI050000", 
    "alt_label": []
  }, 
  "Performing Arts / Acting & Auditioning": {
    "related": [], 
    "pref_label": "Performing Arts / Acting & Auditioning", 
    "notation": "PER001000", 
    "alt_label": []
  }, 
  "Medical / Atlases": {
    "related": [], 
    "pref_label": "Medical / Atlases", 
    "notation": "MED101000", 
    "alt_label": []
  }, 
  "Health & Fitness / Sleep & Sleep Disorders": {
    "related": [], 
    "pref_label": "Health & Fitness / Sleep & Sleep Disorders", 
    "notation": "HEA043000", 
    "alt_label": []
  }, 
  "Travel / South America / Argentina": {
    "related": [], 
    "pref_label": "Travel / South America / Argentina", 
    "notation": "TRV024010", 
    "alt_label": []
  }, 
  "Religion / Judaism / History": {
    "related": [], 
    "pref_label": "Religion / Judaism / History", 
    "notation": "REL040030", 
    "alt_label": []
  }, 
  "Education / Special Education / Learning Disabilities": {
    "related": [], 
    "pref_label": "Education / Special Education / Learning Disabilities", 
    "notation": "EDU026020", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / General": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / General", 
    "notation": "LAN000000", 
    "alt_label": []
  }, 
  "Religion / Christian Theology / Liberation": {
    "related": [], 
    "pref_label": "Religion / Christian Theology / Liberation", 
    "notation": "REL067120", 
    "alt_label": []
  }, 
  "Philosophy / Criticism": {
    "related": [], 
    "pref_label": "Philosophy / Criticism", 
    "notation": "PHI026000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Squash": {
    "related": [], 
    "pref_label": "Sports & Recreation / Squash", 
    "notation": "SPO042000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / History / Medieval": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / History / Medieval", 
    "notation": "JNF025100", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Toymaking": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Toymaking", 
    "notation": "CRA039000", 
    "alt_label": []
  }, 
  "Pets / Cats / Breeds": {
    "related": [], 
    "pref_label": "Pets / Cats / Breeds", 
    "notation": "PET003010", 
    "alt_label": []
  }, 
  "Religion / Confucianism": {
    "related": [], 
    "pref_label": "Religion / Confucianism", 
    "notation": "REL018000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Military": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Military", 
    "notation": "BIO008000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Political": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Political", 
    "notation": "ANT031000", 
    "alt_label": []
  }, 
  "Literary Criticism / Semiotics & Theory": {
    "related": [], 
    "pref_label": "Literary Criticism / Semiotics & Theory", 
    "notation": "LIT006000", 
    "alt_label": [
      "Literary Criticism / Theory"
    ]
  }, 
  "Law / Personal Injury": {
    "related": [], 
    "pref_label": "Law / Personal Injury", 
    "notation": "LAW097000", 
    "alt_label": []
  }, 
  "Nature / Endangered Species": {
    "related": [], 
    "pref_label": "Nature / Endangered Species", 
    "notation": "NAT046000", 
    "alt_label": []
  }, 
  "Political Science / American Government / Executive Branch": {
    "related": [], 
    "pref_label": "Political Science / American Government / Executive Branch", 
    "notation": "POL040010", 
    "alt_label": []
  }, 
  "Law / Civil Procedure": {
    "related": [], 
    "pref_label": "Law / Civil Procedure", 
    "notation": "LAW012000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Depression & Mental Illness": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Depression & Mental Illness", 
    "notation": "JUV039240", 
    "alt_label": [
      "Juvenile Fiction / Health & Daily Living / Depression & Mental Illness"
    ]
  }, 
  "Science / Chemistry / Analytic": {
    "related": [], 
    "pref_label": "Science / Chemistry / Analytic", 
    "notation": "SCI013010", 
    "alt_label": []
  }, 
  "Political Science / History & Theory": {
    "related": [], 
    "pref_label": "Political Science / History & Theory", 
    "notation": "POL010000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Holidays & Celebrations / Easter & Lent": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Holidays & Celebrations / Easter & Lent", 
    "notation": "JNF026020", 
    "alt_label": []
  }, 
  "Religion / Eastern": {
    "related": [], 
    "pref_label": "Religion / Eastern", 
    "notation": "REL024000", 
    "alt_label": []
  }, 
  "History / Revolutionary": {
    "related": [], 
    "pref_label": "History / Revolutionary", 
    "notation": "HIS031000", 
    "alt_label": []
  }, 
  "Literary Criticism / Poetry": {
    "related": [], 
    "pref_label": "Literary Criticism / Poetry", 
    "notation": "LIT014000", 
    "alt_label": []
  }, 
  "Bibles / New International Version / General": {
    "related": [], 
    "pref_label": "Bibles / New International Version / General", 
    "notation": "BIB013000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Self-mutilation": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Self-mutilation", 
    "notation": "JUV039260", 
    "alt_label": []
  }, 
  "Computers / Compilers": {
    "related": [], 
    "pref_label": "Computers / Compilers", 
    "notation": "COM010000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Engineering (general)": {
    "related": [], 
    "pref_label": "Technology & Engineering / Engineering (general)", 
    "notation": "TEC009000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Fairy Tales & Folklore / Adaptations": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Fairy Tales & Folklore / Adaptations", 
    "notation": "JUV012040", 
    "alt_label": []
  }, 
  "Travel / Restaurants": {
    "related": [], 
    "pref_label": "Travel / Restaurants", 
    "notation": "TRV022000", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / General": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / General", 
    "notation": "REL006000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Foreign Language Study / General": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Foreign Language Study / General", 
    "notation": "JNF020000", 
    "alt_label": []
  }, 
  "Cooking / Methods / Gourmet": {
    "related": [], 
    "pref_label": "Cooking / Methods / Gourmet", 
    "notation": "CKB037000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Performing Arts / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Performing Arts / General", 
    "notation": "JUV031000", 
    "alt_label": []
  }, 
  "Religion / Biblical Biography / New Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Biography / New Testament", 
    "notation": "REL006040", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / American / Middle Atlantic States": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / American / Middle Atlantic States", 
    "notation": "CKB002020", 
    "alt_label": []
  }, 
  "Political Science / Public Policy / Economic Policy": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Economic Policy", 
    "notation": "POL024000", 
    "alt_label": []
  }, 
  "History / Oceania": {
    "related": [], 
    "pref_label": "History / Oceania", 
    "notation": "HIS053000", 
    "alt_label": []
  }, 
  "Transportation / Railroads / Pictorial": {
    "related": [], 
    "pref_label": "Transportation / Railroads / Pictorial", 
    "notation": "TRA004020", 
    "alt_label": []
  }, 
  "Business & Economics / Sales & Selling / Management": {
    "related": [], 
    "pref_label": "Business & Economics / Sales & Selling / Management", 
    "notation": "BUS058010", 
    "alt_label": []
  }, 
  "Psychology / General": {
    "related": [], 
    "pref_label": "Psychology / General", 
    "notation": "PSY000000", 
    "alt_label": []
  }, 
  "Religion / Christian Ministry / Discipleship": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / Discipleship", 
    "notation": "REL023000", 
    "alt_label": [
      "Religion / Discipleship"
    ]
  }, 
  "Poetry / American / Hispanic American": {
    "related": [], 
    "pref_label": "Poetry / American / Hispanic American", 
    "notation": "POE005070", 
    "alt_label": []
  }, 
  "Science / Mechanics / Fluids": {
    "related": [], 
    "pref_label": "Science / Mechanics / Fluids", 
    "notation": "SCI085000", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / History & Culture": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / History & Culture", 
    "notation": "REL006630", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Religious": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Religious", 
    "notation": "CGN011000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Historical / United States / 20th Century": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Historical / United States / 20th Century", 
    "notation": "JUV016150", 
    "alt_label": []
  }, 
  "Reference / Directories": {
    "related": [], 
    "pref_label": "Reference / Directories", 
    "notation": "REF009000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Archery": {
    "related": [], 
    "pref_label": "Sports & Recreation / Archery", 
    "notation": "SPO002000", 
    "alt_label": []
  }, 
  "Social Science / Folklore & Mythology": {
    "related": [], 
    "pref_label": "Social Science / Folklore & Mythology", 
    "notation": "SOC011000", 
    "alt_label": []
  }, 
  "Medical / Reproductive Medicine & Technology": {
    "related": [], 
    "pref_label": "Medical / Reproductive Medicine & Technology", 
    "notation": "MED082000", 
    "alt_label": []
  }, 
  "Bibles / La Biblia De Las Americas / Devotional": {
    "related": [], 
    "pref_label": "Bibles / La Biblia De Las Americas / Devotional", 
    "notation": "BIB007020", 
    "alt_label": []
  }, 
  "Medical / Hepatology": {
    "related": [], 
    "pref_label": "Medical / Hepatology", 
    "notation": "MED114000", 
    "alt_label": []
  }, 
  "Computers / User Interfaces": {
    "related": [], 
    "pref_label": "Computers / User Interfaces", 
    "notation": "COM070000", 
    "alt_label": []
  }, 
  "Cooking / Beverages / Wine & Spirits": {
    "related": [], 
    "pref_label": "Cooking / Beverages / Wine & Spirits", 
    "notation": "CKB088000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Family / New Baby": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Family / New Baby", 
    "notation": "JNF019040", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Ballet": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Ballet", 
    "notation": "MUS002000", 
    "alt_label": []
  }, 
  "Bibles / New American Bible / New Testament & Portions": {
    "related": [], 
    "pref_label": "Bibles / New American Bible / New Testament & Portions", 
    "notation": "BIB009030", 
    "alt_label": []
  }, 
  "Computers / Operating Systems / Linux": {
    "related": [], 
    "pref_label": "Computers / Operating Systems / Linux", 
    "notation": "COM046070", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Values & Virtues": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Values & Virtues", 
    "notation": "JUV033240", 
    "alt_label": []
  }, 
  "Psychology / Psychopathology / Schizophrenia": {
    "related": [], 
    "pref_label": "Psychology / Psychopathology / Schizophrenia", 
    "notation": "PSY022050", 
    "alt_label": []
  }, 
  "Medical / Long-term Care": {
    "related": [], 
    "pref_label": "Medical / Long-term Care", 
    "notation": "MED113000", 
    "alt_label": []
  }, 
  "Family & Relationships / Learning Disabilities": {
    "related": [], 
    "pref_label": "Family & Relationships / Learning Disabilities", 
    "notation": "FAM028000", 
    "alt_label": []
  }, 
  "Social Science / Essays": {
    "related": [], 
    "pref_label": "Social Science / Essays", 
    "notation": "SOC041000", 
    "alt_label": []
  }, 
  "Education / Teaching Methods & Materials / Science & Technology": {
    "related": [], 
    "pref_label": "Education / Teaching Methods & Materials / Science & Technology", 
    "notation": "EDU029030", 
    "alt_label": []
  }, 
  "Family & Relationships / Life Stages / Infants & Toddlers": {
    "related": [], 
    "pref_label": "Family & Relationships / Life Stages / Infants & Toddlers", 
    "notation": "FAM025000", 
    "alt_label": []
  }, 
  "Performing Arts / Reference": {
    "related": [], 
    "pref_label": "Performing Arts / Reference", 
    "notation": "PER009000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Crystals": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Crystals", 
    "notation": "OCC004000", 
    "alt_label": []
  }, 
  "Medical / Nursing / Nutrition": {
    "related": [], 
    "pref_label": "Medical / Nursing / Nutrition", 
    "notation": "MED058150", 
    "alt_label": []
  }, 
  "Sports & Recreation / Skateboarding": {
    "related": [], 
    "pref_label": "Sports & Recreation / Skateboarding", 
    "notation": "SPO038000", 
    "alt_label": []
  }, 
  "House & Home / Outdoor & Recreational Areas": {
    "related": [], 
    "pref_label": "House & Home / Outdoor & Recreational Areas", 
    "notation": "HOM013000", 
    "alt_label": []
  }, 
  "Self-help / Affirmations": {
    "related": [], 
    "pref_label": "Self-help / Affirmations", 
    "notation": "SEL004000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Science / Politics & Government": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Science / Politics & Government", 
    "notation": "JNF043000", 
    "alt_label": [
      "Juvenile Nonfiction / Politics & Government"
    ]
  }, 
  "Art / Individual Artists / Essays": {
    "related": [], 
    "pref_label": "Art / Individual Artists / Essays", 
    "notation": "ART016020", 
    "alt_label": []
  }, 
  "Computers / Programming Languages / Ruby": {
    "related": [], 
    "pref_label": "Computers / Programming Languages / Ruby", 
    "notation": "COM051410", 
    "alt_label": []
  }, 
  "Bibles / The Message / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / The Message / Youth & Teen", 
    "notation": "BIB020070", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Linguistics / Historical & Comparative": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Linguistics / Historical & Comparative", 
    "notation": "LAN009010", 
    "alt_label": []
  }, 
  "Computers / Programming / Apple Programming": {
    "related": [], 
    "pref_label": "Computers / Programming / Apple Programming", 
    "notation": "COM051370", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Death, Grief, Bereavement": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Death, Grief, Bereavement", 
    "notation": "REL012010", 
    "alt_label": []
  }, 
  "Religion / Sexuality & Gender Studies": {
    "related": [], 
    "pref_label": "Religion / Sexuality & Gender Studies", 
    "notation": "REL105000", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Translating & Interpreting": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Translating & Interpreting", 
    "notation": "LAN023000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / Christian / Science Fiction": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / Christian / Science Fiction", 
    "notation": "JUV033210", 
    "alt_label": []
  }, 
  "History / Military / Aviation": {
    "related": [], 
    "pref_label": "History / Military / Aviation", 
    "notation": "HIS027140", 
    "alt_label": []
  }, 
  "Design / Essays": {
    "related": [], 
    "pref_label": "Design / Essays", 
    "notation": "DES004000", 
    "alt_label": []
  }, 
  "Science / Biotechnology": {
    "related": [], 
    "pref_label": "Science / Biotechnology", 
    "notation": "SCI010000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Foxes": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Foxes", 
    "notation": "JUV002110", 
    "alt_label": []
  }, 
  "Music / Musical Instruments / Brass": {
    "related": [], 
    "pref_label": "Music / Musical Instruments / Brass", 
    "notation": "MUS023010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Social Issues / Manners & Etiquette": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Social Issues / Manners & Etiquette", 
    "notation": "JUV039200", 
    "alt_label": []
  }, 
  "Social Science / Men's Studies": {
    "related": [], 
    "pref_label": "Social Science / Men's Studies", 
    "notation": "SOC018000", 
    "alt_label": []
  }, 
  "Technology & Engineering / Civil / Soil & Rock": {
    "related": [], 
    "pref_label": "Technology & Engineering / Civil / Soil & Rock", 
    "notation": "TEC009150", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Kangaroos": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Kangaroos", 
    "notation": "JUV002350", 
    "alt_label": []
  }, 
  "Literary Criticism / European / Italian": {
    "related": [], 
    "pref_label": "Literary Criticism / European / Italian", 
    "notation": "LIT004200", 
    "alt_label": []
  }, 
  "Computers / Computer Simulation": {
    "related": [], 
    "pref_label": "Computers / Computer Simulation", 
    "notation": "COM072000", 
    "alt_label": []
  }, 
  "Health & Fitness / Homeopathy": {
    "related": [], 
    "pref_label": "Health & Fitness / Homeopathy", 
    "notation": "HEA030000", 
    "alt_label": []
  }, 
  "Religion / Christian Life / Devotional": {
    "related": [], 
    "pref_label": "Religion / Christian Life / Devotional", 
    "notation": "REL012020", 
    "alt_label": []
  }, 
  "Mathematics / Complex Analysis": {
    "related": [], 
    "pref_label": "Mathematics / Complex Analysis", 
    "notation": "MAT040000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Botany": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Botany", 
    "notation": "JNF051060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Art / Cartooning": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Art / Cartooning", 
    "notation": "JNF006010", 
    "alt_label": []
  }, 
  "Pets / Cats / General": {
    "related": [], 
    "pref_label": "Pets / Cats / General", 
    "notation": "PET003000", 
    "alt_label": []
  }, 
  "Travel / Europe / France": {
    "related": [], 
    "pref_label": "Travel / Europe / France", 
    "notation": "TRV009050", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Sign Language": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Sign Language", 
    "notation": "LAN017000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Fantasy & Magic": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Fantasy & Magic", 
    "notation": "JUV037000", 
    "alt_label": [
      "Juvenile Fiction / Magic"
    ]
  }, 
  "Bibles / New King James Version / Devotional": {
    "related": [], 
    "pref_label": "Bibles / New King James Version / Devotional", 
    "notation": "BIB014020", 
    "alt_label": []
  }, 
  "Religion / Christian Ministry / Evangelism": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / Evangelism", 
    "notation": "REL030000", 
    "alt_label": [
      "Religion / Evangelism"
    ]
  }, 
  "Juvenile Fiction / People & Places / Asia": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Asia", 
    "notation": "JUV030020", 
    "alt_label": []
  }, 
  "Health & Fitness / Breastfeeding": {
    "related": [], 
    "pref_label": "Health & Fitness / Breastfeeding", 
    "notation": "HEA044000", 
    "alt_label": []
  }, 
  "Bibles / Contemporary English Version / General": {
    "related": [], 
    "pref_label": "Bibles / Contemporary English Version / General", 
    "notation": "BIB002000", 
    "alt_label": []
  }, 
  "Religion / Prayerbooks / Jewish": {
    "related": [], 
    "pref_label": "Religion / Prayerbooks / Jewish", 
    "notation": "REL052020", 
    "alt_label": [
      "Religion / Judaism / Prayerbooks, Prayers, Liturgy"
    ]
  }, 
  "Computers / Social Aspects / General": {
    "related": [], 
    "pref_label": "Computers / Social Aspects / General", 
    "notation": "COM079000", 
    "alt_label": []
  }, 
  "Cooking / Reference": {
    "related": [], 
    "pref_label": "Cooking / Reference", 
    "notation": "CKB071000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Performing Arts / Theater": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Performing Arts / Theater", 
    "notation": "JUV031060", 
    "alt_label": []
  }, 
  "Medical / Dentistry / Orthodontics": {
    "related": [], 
    "pref_label": "Medical / Dentistry / Orthodontics", 
    "notation": "MED016030", 
    "alt_label": []
  }, 
  "Sports & Recreation / Hiking": {
    "related": [], 
    "pref_label": "Sports & Recreation / Hiking", 
    "notation": "SPO018000", 
    "alt_label": []
  }, 
  "Music / Printed Music / Percussion": {
    "related": [], 
    "pref_label": "Music / Printed Music / Percussion", 
    "notation": "MUS037080", 
    "alt_label": []
  }, 
  "Travel / Cruises": {
    "related": [], 
    "pref_label": "Travel / Cruises", 
    "notation": "TRV028000", 
    "alt_label": []
  }, 
  "Computers / Data Transmission Systems / Broadband": {
    "related": [], 
    "pref_label": "Computers / Data Transmission Systems / Broadband", 
    "notation": "COM020050", 
    "alt_label": []
  }, 
  "Religion / Biblical Studies / New Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Studies / New Testament", 
    "notation": "REL006220", 
    "alt_label": []
  }, 
  "Foreign Language Study / Oceanic & Australian Languages": {
    "related": [], 
    "pref_label": "Foreign Language Study / Oceanic & Australian Languages", 
    "notation": "FOR032000", 
    "alt_label": [
      "Foreign Language Study / Australian Languages"
    ]
  }, 
  "Travel / Museums, Tours, Points Of Interest": {
    "related": [], 
    "pref_label": "Travel / Museums, Tours, Points Of Interest", 
    "notation": "TRV016000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Performing Arts / Film": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Performing Arts / Film", 
    "notation": "JNF039030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Religion / Bible Stories / New Testament": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Religion / Bible Stories / New Testament", 
    "notation": "JNF049150", 
    "alt_label": []
  }, 
  "Mathematics / Probability & Statistics / Bayesian Analysis": {
    "related": [], 
    "pref_label": "Mathematics / Probability & Statistics / Bayesian Analysis", 
    "notation": "MAT029010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Imagination & Play": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Imagination & Play", 
    "notation": "JUV051000", 
    "alt_label": [
      "Juvenile Fiction / Play"
    ]
  }, 
  "Travel / Asia / Central": {
    "related": [], 
    "pref_label": "Travel / Asia / Central", 
    "notation": "TRV003010", 
    "alt_label": []
  }, 
  "Bibles / New Century Version / Study": {
    "related": [], 
    "pref_label": "Bibles / New Century Version / Study", 
    "notation": "BIB011050", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Linguistics / Etymology": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Linguistics / Etymology", 
    "notation": "LAN024000", 
    "alt_label": []
  }, 
  "Study Aids / Tests": {
    "related": [], 
    "pref_label": "Study Aids / Tests", 
    "notation": "STU027000", 
    "alt_label": []
  }, 
  "Psychology / Education & Training": {
    "related": [], 
    "pref_label": "Psychology / Education & Training", 
    "notation": "PSY012000", 
    "alt_label": []
  }, 
  "Drama / Anthologies (multiple Authors)": {
    "related": [], 
    "pref_label": "Drama / Anthologies (multiple Authors)", 
    "notation": "DRA002000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Adventurers & Explorers": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Adventurers & Explorers", 
    "notation": "BIO023000", 
    "alt_label": []
  }, 
  "Medical / Veterinary Medicine / Equine": {
    "related": [], 
    "pref_label": "Medical / Veterinary Medicine / Equine", 
    "notation": "MED089010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / Caribbean & Latin America": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Caribbean & Latin America", 
    "notation": "JUV030040", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / German": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / German", 
    "notation": "CKB036000", 
    "alt_label": []
  }, 
  "History / Middle East / Turkey & Ottoman Empire": {
    "related": [], 
    "pref_label": "History / Middle East / Turkey & Ottoman Empire", 
    "notation": "HIS055000", 
    "alt_label": []
  }, 
  "Law / Evidence": {
    "related": [], 
    "pref_label": "Law / Evidence", 
    "notation": "LAW037000", 
    "alt_label": []
  }, 
  "Social Science / Methodology": {
    "related": [], 
    "pref_label": "Social Science / Methodology", 
    "notation": "SOC019000", 
    "alt_label": []
  }, 
  "Fiction / Cultural Heritage": {
    "related": [], 
    "pref_label": "Fiction / Cultural Heritage", 
    "notation": "FIC051000", 
    "alt_label": []
  }, 
  "Religion / Biblical Commentary / General": {
    "related": [], 
    "pref_label": "Religion / Biblical Commentary / General", 
    "notation": "REL006050", 
    "alt_label": []
  }, 
  "Fiction / Occult & Supernatural": {
    "related": [], 
    "pref_label": "Fiction / Occult & Supernatural", 
    "notation": "FIC024000", 
    "alt_label": []
  }, 
  "Law / Paralegals & Paralegalism": {
    "related": [], 
    "pref_label": "Law / Paralegals & Paralegalism", 
    "notation": "LAW071000", 
    "alt_label": [
      "Law / Legal Assistants"
    ]
  }, 
  "Cooking / Regional & Ethnic / Vietnamese": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Vietnamese", 
    "notation": "CKB094000", 
    "alt_label": []
  }, 
  "Computers / Web / Web Programming": {
    "related": [], 
    "pref_label": "Computers / Web / Web Programming", 
    "notation": "COM060160", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Decorating": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Decorating", 
    "notation": "CRA005000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Erotica": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Erotica", 
    "notation": "CGN004110", 
    "alt_label": []
  }, 
  "Business & Economics / Business Mathematics": {
    "related": [], 
    "pref_label": "Business & Economics / Business Mathematics", 
    "notation": "BUS091000", 
    "alt_label": []
  }, 
  "Political Science / World / Canadian": {
    "related": [], 
    "pref_label": "Political Science / World / Canadian", 
    "notation": "POL056000", 
    "alt_label": []
  }, 
  "Literary Collections / European / Spanish & Portuguese": {
    "related": [], 
    "pref_label": "Literary Collections / European / Spanish & Portuguese", 
    "notation": "LCO008060", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Animals / Turtles": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Animals / Turtles", 
    "notation": "JUV002240", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Editing & Proofreading": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Editing & Proofreading", 
    "notation": "LAN022000", 
    "alt_label": [
      "Language Arts & Disciplines / Proofreading"
    ]
  }, 
  "Music / Genres & Styles / Children's": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Children's", 
    "notation": "MUS026000", 
    "alt_label": []
  }, 
  "Literary Criticism / Books & Reading": {
    "related": [], 
    "pref_label": "Literary Criticism / Books & Reading", 
    "notation": "LIT007000", 
    "alt_label": []
  }, 
  "Religion / Christianity / United Church Of Christ": {
    "related": [], 
    "pref_label": "Religion / Christianity / United Church Of Christ", 
    "notation": "REL111000", 
    "alt_label": [
      "Religion / Christianity / Congregational"
    ]
  }, 
  "Bibles / Christian Standard Bible / Text": {
    "related": [], 
    "pref_label": "Bibles / Christian Standard Bible / Text", 
    "notation": "BIB001060", 
    "alt_label": []
  }, 
  "Bibles / Contemporary English Version / Youth & Teen": {
    "related": [], 
    "pref_label": "Bibles / Contemporary English Version / Youth & Teen", 
    "notation": "BIB002070", 
    "alt_label": []
  }, 
  "Crafts & Hobbies / Framing": {
    "related": [], 
    "pref_label": "Crafts & Hobbies / Framing", 
    "notation": "CRA011000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Action & Adventure / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Action & Adventure / General", 
    "notation": "JUV001000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Drama": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Drama", 
    "notation": "JNF017000", 
    "alt_label": []
  }, 
  "Medical / Pulmonary & Thoracic Medicine": {
    "related": [], 
    "pref_label": "Medical / Pulmonary & Thoracic Medicine", 
    "notation": "MED079000", 
    "alt_label": [
      "Medical / Diseases / Respiratory", 
      "Medical / Thoracic Medicine"
    ]
  }, 
  "Photography / Techniques / Cinematography & Videography": {
    "related": [], 
    "pref_label": "Photography / Techniques / Cinematography & Videography", 
    "notation": "PHO022000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Religious / General": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Religious / General", 
    "notation": "JUV033000", 
    "alt_label": []
  }, 
  "Family & Relationships / Parenting / Grandparenting": {
    "related": [], 
    "pref_label": "Family & Relationships / Parenting / Grandparenting", 
    "notation": "FAM022000", 
    "alt_label": []
  }, 
  "Sports & Recreation / Juggling": {
    "related": [], 
    "pref_label": "Sports & Recreation / Juggling", 
    "notation": "SPO024000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Toys": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Toys", 
    "notation": "ANT050000", 
    "alt_label": []
  }, 
  "Medical / Diagnostic Imaging": {
    "related": [], 
    "pref_label": "Medical / Diagnostic Imaging", 
    "notation": "MED019000", 
    "alt_label": []
  }, 
  "Education / Adult & Continuing Education": {
    "related": [], 
    "pref_label": "Education / Adult & Continuing Education", 
    "notation": "EDU002000", 
    "alt_label": []
  }, 
  "Fiction / Crime": {
    "related": [], 
    "pref_label": "Fiction / Crime", 
    "notation": "FIC050000", 
    "alt_label": []
  }, 
  "Biography & Autobiography / Artists, Architects, Photographers": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Artists, Architects, Photographers", 
    "notation": "BIO001000", 
    "alt_label": [
      "Biography & Autobiography / Photographers"
    ]
  }, 
  "Bibles / Common English Bible / Reference": {
    "related": [], 
    "pref_label": "Bibles / Common English Bible / Reference", 
    "notation": "BIB022040", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Transportation / Motorcycles": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Transportation / Motorcycles", 
    "notation": "JUV041040", 
    "alt_label": []
  }, 
  "History / United States / State & Local / Pacific Northwest (or, Wa)": {
    "related": [], 
    "pref_label": "History / United States / State & Local / Pacific Northwest (or, Wa)", 
    "notation": "HIS036110", 
    "alt_label": []
  }, 
  "Language Arts & Disciplines / Linguistics / Phonetics & Phonology": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Linguistics / Phonetics & Phonology", 
    "notation": "LAN011000", 
    "alt_label": []
  }, 
  "Religion / Holidays / Christian": {
    "related": [], 
    "pref_label": "Religion / Holidays / Christian", 
    "notation": "REL034010", 
    "alt_label": []
  }, 
  "Juvenile Fiction / People & Places / Polar Regions": {
    "related": [], 
    "pref_label": "Juvenile Fiction / People & Places / Polar Regions", 
    "notation": "JUV030120", 
    "alt_label": []
  }, 
  "Travel / United States / Midwest / East North Central (il, In, Mi, Oh, Wi)": {
    "related": [], 
    "pref_label": "Travel / United States / Midwest / East North Central (il, In, Mi, Oh, Wi)", 
    "notation": "TRV025020", 
    "alt_label": []
  }, 
  "Literary Criticism / Asian / General": {
    "related": [], 
    "pref_label": "Literary Criticism / Asian / General", 
    "notation": "LIT008000", 
    "alt_label": []
  }, 
  "Political Science / Public Policy / City Planning & Urban Development": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / City Planning & Urban Development", 
    "notation": "POL002000", 
    "alt_label": []
  }, 
  "Art / Prints": {
    "related": [], 
    "pref_label": "Art / Prints", 
    "notation": "ART048000", 
    "alt_label": []
  }, 
  "Body, Mind & Spirit / Magick Studies": {
    "related": [], 
    "pref_label": "Body, Mind & Spirit / Magick Studies", 
    "notation": "OCC028000", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / Soul Food": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / Soul Food", 
    "notation": "CKB078000", 
    "alt_label": []
  }, 
  "Business & Economics / Corporate Finance": {
    "related": [], 
    "pref_label": "Business & Economics / Corporate Finance", 
    "notation": "BUS017000", 
    "alt_label": []
  }, 
  "Art / Sculpture & Installation": {
    "related": [], 
    "pref_label": "Art / Sculpture & Installation", 
    "notation": "ART026000", 
    "alt_label": []
  }, 
  "Literary Collections / European / French": {
    "related": [], 
    "pref_label": "Literary Collections / European / French", 
    "notation": "LCO008020", 
    "alt_label": []
  }, 
  "Business & Economics / Banks & Banking": {
    "related": [], 
    "pref_label": "Business & Economics / Banks & Banking", 
    "notation": "BUS004000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Experiments & Projects": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Experiments & Projects", 
    "notation": "JNF051110", 
    "alt_label": []
  }, 
  "Bibles / Christian Standard Bible / Study": {
    "related": [], 
    "pref_label": "Bibles / Christian Standard Bible / Study", 
    "notation": "BIB001050", 
    "alt_label": []
  }, 
  "Music / Genres & Styles / Opera": {
    "related": [], 
    "pref_label": "Music / Genres & Styles / Opera", 
    "notation": "MUS028000", 
    "alt_label": []
  }, 
  "Political Science / Public Policy / Environmental Policy": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Environmental Policy", 
    "notation": "POL044000", 
    "alt_label": []
  }, 
  "Religion / Christianity / Christian Science": {
    "related": [], 
    "pref_label": "Religion / Christianity / Christian Science", 
    "notation": "REL083000", 
    "alt_label": []
  }, 
  "Literary Criticism / Women Authors": {
    "related": [], 
    "pref_label": "Literary Criticism / Women Authors", 
    "notation": "LIT004290", 
    "alt_label": []
  }, 
  "Travel / Canada / Prairie Provinces (mb, Sk)": {
    "related": [], 
    "pref_label": "Travel / Canada / Prairie Provinces (mb, Sk)", 
    "notation": "TRV006030", 
    "alt_label": []
  }, 
  "Family & Relationships / Life Stages / School Age": {
    "related": [], 
    "pref_label": "Family & Relationships / Life Stages / School Age", 
    "notation": "FAM039000", 
    "alt_label": []
  }, 
  "Juvenile Fiction / Action & Adventure / Pirates": {
    "related": [], 
    "pref_label": "Juvenile Fiction / Action & Adventure / Pirates", 
    "notation": "JUV001020", 
    "alt_label": []
  }, 
  "Health & Fitness / General": {
    "related": [], 
    "pref_label": "Health & Fitness / General", 
    "notation": "HEA000000", 
    "alt_label": []
  }, 
  "Literary Criticism / Caribbean & Latin American": {
    "related": [], 
    "pref_label": "Literary Criticism / Caribbean & Latin American", 
    "notation": "LIT004100", 
    "alt_label": [
      "Literary Criticism / Central American & South American"
    ]
  }, 
  "Bibles / Today's New International Version / Text": {
    "related": [], 
    "pref_label": "Bibles / Today's New International Version / Text", 
    "notation": "BIB021060", 
    "alt_label": []
  }, 
  "Business & Economics / Leadership": {
    "related": [], 
    "pref_label": "Business & Economics / Leadership", 
    "notation": "BUS071000", 
    "alt_label": []
  }, 
  "Music / Ethnic": {
    "related": [], 
    "pref_label": "Music / Ethnic", 
    "notation": "MUS014000", 
    "alt_label": []
  }, 
  "Social Science / Human Services": {
    "related": [], 
    "pref_label": "Social Science / Human Services", 
    "notation": "SOC016000", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Yaoi": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Yaoi", 
    "notation": "CGN004210", 
    "alt_label": []
  }, 
  "Mathematics / Applied": {
    "related": [], 
    "pref_label": "Mathematics / Applied", 
    "notation": "MAT003000", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Science / Psychology": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Science / Psychology", 
    "notation": "JNF044000", 
    "alt_label": []
  }, 
  "Computers / Desktop Applications / Databases": {
    "related": [], 
    "pref_label": "Computers / Desktop Applications / Databases", 
    "notation": "COM084010", 
    "alt_label": []
  }, 
  "Literary Criticism / Asian / Chinese": {
    "related": [], 
    "pref_label": "Literary Criticism / Asian / Chinese", 
    "notation": "LIT008010", 
    "alt_label": []
  }, 
  "Photography / Techniques / General": {
    "related": [], 
    "pref_label": "Photography / Techniques / General", 
    "notation": "PHO018000", 
    "alt_label": []
  }, 
  "Antiques & Collectibles / Military": {
    "related": [], 
    "pref_label": "Antiques & Collectibles / Military", 
    "notation": "ANT024000", 
    "alt_label": []
  }, 
  "Fiction / Fantasy / Epic": {
    "related": [], 
    "pref_label": "Fiction / Fantasy / Epic", 
    "notation": "FIC009020", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Transportation / Aviation": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Transportation / Aviation", 
    "notation": "JNF057010", 
    "alt_label": []
  }, 
  "Cooking / Regional & Ethnic / American / Southern States": {
    "related": [], 
    "pref_label": "Cooking / Regional & Ethnic / American / Southern States", 
    "notation": "CKB002060", 
    "alt_label": []
  }, 
  "Mathematics / Algebra / Intermediate": {
    "related": [], 
    "pref_label": "Mathematics / Algebra / Intermediate", 
    "notation": "MAT002040", 
    "alt_label": []
  }, 
  "Medical / Oncology": {
    "related": [], 
    "pref_label": "Medical / Oncology", 
    "notation": "MED062000", 
    "alt_label": [
      "Medical / Cancer", 
      "Medical / Diseases / Cancer"
    ]
  }, 
  "Medical / Healing": {
    "related": [], 
    "pref_label": "Medical / Healing", 
    "notation": "MED034000", 
    "alt_label": []
  }, 
  "Religion / Christian Ministry / Children": {
    "related": [], 
    "pref_label": "Religion / Christian Ministry / Children", 
    "notation": "REL109020", 
    "alt_label": []
  }, 
  "Cooking / Specific Ingredients / Rice & Grains": {
    "related": [], 
    "pref_label": "Cooking / Specific Ingredients / Rice & Grains", 
    "notation": "CKB098000", 
    "alt_label": []
  }, 
  "Religion / Biblical Criticism & Interpretation / New Testament": {
    "related": [], 
    "pref_label": "Religion / Biblical Criticism & Interpretation / New Testament", 
    "notation": "REL006100", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Mathematics / Arithmetic": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Mathematics / Arithmetic", 
    "notation": "JNF035030", 
    "alt_label": []
  }, 
  "Music / Instruction & Study / Conducting": {
    "related": [], 
    "pref_label": "Music / Instruction & Study / Conducting", 
    "notation": "MUS008000", 
    "alt_label": []
  }, 
  "Bibles / King James Version / Devotional": {
    "related": [], 
    "pref_label": "Bibles / King James Version / Devotional", 
    "notation": "BIB006020", 
    "alt_label": []
  }, 
  "Medical / Gastroenterology": {
    "related": [], 
    "pref_label": "Medical / Gastroenterology", 
    "notation": "MED031000", 
    "alt_label": [
      "Medical / Diseases / Abdominal", 
      "Medical / Diseases / Digestive Organs", 
      "Medical / Diseases / Gastrointestinal"
    ]
  }, 
  "Photography / Photoessays & Documentaries": {
    "related": [], 
    "pref_label": "Photography / Photoessays & Documentaries", 
    "notation": "PHO014000", 
    "alt_label": []
  }, 
  "Bibles / King James Version / General": {
    "related": [], 
    "pref_label": "Bibles / King James Version / General", 
    "notation": "BIB006000", 
    "alt_label": []
  }, 
  "Political Science / Constitutions": {
    "related": [], 
    "pref_label": "Political Science / Constitutions", 
    "notation": "POL022000", 
    "alt_label": []
  }, 
  "Religion / Prayerbooks / Christian": {
    "related": [], 
    "pref_label": "Religion / Prayerbooks / Christian", 
    "notation": "REL052010", 
    "alt_label": []
  }, 
  "Humor / Form / Trivia": {
    "related": [], 
    "pref_label": "Humor / Form / Trivia", 
    "notation": "HUM016000", 
    "alt_label": []
  }, 
  "Health & Fitness / Holism": {
    "related": [], 
    "pref_label": "Health & Fitness / Holism", 
    "notation": "HEA012000", 
    "alt_label": []
  }, 
  "Business & Economics / Taxation / Small Business": {
    "related": [], 
    "pref_label": "Business & Economics / Taxation / Small Business", 
    "notation": "BUS064030", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Science & Nature / Biology": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Science & Nature / Biology", 
    "notation": "JNF051050", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Social Issues / Friendship": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Social Issues / Friendship", 
    "notation": "JNF053060", 
    "alt_label": []
  }, 
  "Technology & Engineering / Electronics / Digital": {
    "related": [], 
    "pref_label": "Technology & Engineering / Electronics / Digital", 
    "notation": "TEC008060", 
    "alt_label": []
  }, 
  "Juvenile Nonfiction / Art / Techniques": {
    "related": [], 
    "pref_label": "Juvenile Nonfiction / Art / Techniques", 
    "notation": "JNF006070", 
    "alt_label": []
  }, 
  "Political Science / Political Ideologies / Anarchism": {
    "related": [], 
    "pref_label": "Political Science / Political Ideologies / Anarchism", 
    "notation": "POL042010", 
    "alt_label": []
  }, 
  "Gardening / Garden Design": {
    "related": [], 
    "pref_label": "Gardening / Garden Design", 
    "notation": "GAR006000", 
    "alt_label": []
  }, 
  "Poetry / European / English, Irish, Scottish, Welsh": {
    "related": [], 
    "pref_label": "Poetry / European / English, Irish, Scottish, Welsh", 
    "notation": "POE005020", 
    "alt_label": []
  }, 
  "Comics & Graphic Novels / Manga / Horror": {
    "related": [], 
    "pref_label": "Comics & Graphic Novels / Manga / Horror", 
    "notation": "CGN004150", 
    "alt_label": []
  }, 
  "Political Science / Terrorism": {
    "related": [], 
    "pref_label": "Political Science / Terrorism", 
    "notation": "POL037000", 
    "alt_label": []
  },
  "History / Europe / Greece": {
    "related": [], 
    "pref_label": "History / Europe / Greece", 
    "notation": "HIS042000", 
    "alt_label": []
  },
  "Political Science / Public Policy / Economic Policy": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Economic Policy", 
    "notation": "POL024000", 
    "alt_label": []
  },
  "Biography & Autobiography / Science & Technology": {
    "related": [], 
    "pref_label": "Biography & Autobiography / Science & Technology", 
    "notation": "BIO015000", 
    "alt_label": []
  },
  "History / Middle East / Iran": {
    "related": [], 
    "pref_label": "History / Middle East / Iran", 
    "notation": "HIS026020", 
    "alt_label": []
  },
  "History / Europe / Spain & Portugal": {
    "related": [], 
    "pref_label": "History / Europe / Spain & Portugal", 
    "notation": "HIS045000", 
    "alt_label": []
  },
  "History / African American": {
    "related": [], 
    "pref_label": "History / African American", 
    "notation": "HIS056000", 
    "alt_label": []
  },
  "History / Women": {
    "related": [], 
    "pref_label": "History / Women", 
    "notation": "HIS058000", 
    "alt_label": []
  },
  "History / Europe / Poland": {
    "related": [], 
    "pref_label": "History / Europe / Poland", 
    "notation": "HIS060000", 
    "alt_label": []
  },
  "Language Arts & Disciplines / Literacy": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Literacy", 
    "notation": "LAN010000", 
    "alt_label": []
  },
  "Language Arts & Disciplines / Linguistics / Sociolinguistics": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Linguistics / Sociolinguistics", 
    "notation": "LAN009050", 
    "alt_label": []
  },
  "Language Arts & Disciplines / Library & Information Science / Digital & Online Resources": {
    "related": [], 
    "pref_label": "Language Arts & Disciplines / Library & Information Science / Digital & Online Resources", 
    "notation": "LAN025060", 
    "alt_label": []
  },
  "Literary Criticism / European / Eastern": {
    "related": [], 
    "pref_label": "Literary Criticism / European / Eastern", 
    "notation": "LIT004110", 
    "alt_label": []
  },
  "Literary Criticism / Comparative Literature": {
    "related": [], 
    "pref_label": "Literary Criticism / Comparative Literature", 
    "notation": "LIT020000", 
    "alt_label": []
  },
  "Literary Criticism / Modern / General": {
    "related": [], 
    "pref_label": "Literary Criticism / Modern / General", 
    "notation": "LIT024000", 
    "alt_label": []
  },
  "Literary Criticism / Modern / 16th Century": {
    "related": [], 
    "pref_label": "Literary Criticism / Modern / 16th Century", 
    "notation": "LIT024010", 
    "alt_label": []
  },
  "Literary Criticism / Modern / 17th Century": {
    "related": [], 
    "pref_label": "Literary Criticism / Modern / 17th Century", 
    "notation": "LIT024020", 
    "alt_label": []
  },
  "Literary Criticism / Modern / 18th Century": {
    "related": [], 
    "pref_label": "Literary Criticism / Modern / 18th Century", 
    "notation": "LIT024030", 
    "alt_label": []
  },
  "Literary Criticism / Modern / 19th Century": {
    "related": [], 
    "pref_label": "Literary Criticism / Modern / 19th Century", 
    "notation": "LIT024040", 
    "alt_label": []
  },
  "Literary Criticism / Modern / 20th Century": {
    "related": [], 
    "pref_label": "Literary Criticism / Modern / 20th Century", 
    "notation": "LIT024050", 
    "alt_label": []
  },
  "Literary Criticism / Modern / 21st Century": {
    "related": [], 
    "pref_label": "Literary Criticism / Modern / 21st Century", 
    "notation": "LIT024060", 
    "alt_label": []
  },
  "Political Science / Security (National & International)": {
    "related": [], 
    "pref_label": "Political Science / Security (National & International)", 
    "notation": "POL012000", 
    "alt_label": []
  },
  "Political Science / Intergovernmental Organizations": {
    "related": [], 
    "pref_label": "Political Science / Intergovernmental Organizations", 
    "notation": "POL048000", 
    "alt_label": []
  },
  "Political Science / Genocide & War Crimes": {
    "related": [], 
    "pref_label": "Political Science / Genocide & War Crimes", 
    "notation": "POL061000", 
    "alt_label": []
  },
  "Political Science / Geopolitics": {
    "related": [], 
    "pref_label": "Political Science / Geopolitics", 
    "notation": "POL062000", 
    "alt_label": []
  },
  "Political Science / Political Process / Media & Internet": {
    "related": [], 
    "pref_label": "Political Science / Political Process / Media & Internet", 
    "notation": "POL065000", 
    "alt_label": []
  },
  "Political Science / Public Policy / Military Policy": {
    "related": [], 
    "pref_label": "Political Science / Public Policy / Military Policy", 
    "notation": "POL069000", 
    "alt_label": []
  },
  "Psychology / Animal & Comparative Psychology": {
    "related": [], 
    "pref_label": "Psychology / Animal & Comparative Psychology", 
    "notation": "PSY054000", 
    "alt_label": []
  },
  "Religion / Buddhism / General": {
    "related": [], 
    "pref_label": "Religion / Buddhism / General", 
    "notation": "REL007000", 
    "alt_label": []
  },
  "Science / Environmental Science": {
    "related": [], 
    "pref_label": "Science / Environmental Science", 
    "notation": "SCI026000", 
    "alt_label": []
  },
  "Science / Ethics": {
    "related": [], 
    "pref_label": "Science / Ethics", 
    "notation": "SCI101000", 
    "alt_label": []
  },
  "Social Science / Sociology / Social Theory": {
    "related": [], 
    "pref_label": "Social Science / Sociology / Social Theory", 
    "notation": "SOC026040", 
    "alt_label": []
  },
  "Social Science / Indigenous Studies": {
    "related": [], 
    "pref_label": "Social Science / Indigenous Studies", 
    "notation": "SOC062000", 
    "alt_label": []
  },
  "Technology & Engineering / Electronics / Circuits / General": {
    "related": [], 
    "pref_label": "Technology & Engineering / Electronics / Circuits / General", 
    "notation": "TEC008010", 
    "alt_label": []
  },
  "History / Modern / 19th Century": {
    "related": [], 
    "pref_label": "History / Modern / 19th Century", 
    "notation": "HIS037060", 
    "alt_label": []
  },
  "History / Europe / Greece": {
    "related": [], 
    "pref_label": "History / Europe / Greece", 
    "notation": "HIS042000", 
    "alt_label": []
  },
  "History / Social History": {
    "related": [], 
    "pref_label": "History / Social History", 
    "notation": "HIS054000", 
    "alt_label": []
  },

}