from json import dumps
import ast
from django.utils.translation import ugettext as _, ungettext

from .. import add_type, question_proc, answer_proc, AnswerException
from ..utils import get_runid_from_request


@question_proc('choice', 'choice-freeform', 'dropdown', 'choice-optional', 'choice-freeform-optional')
def question_choice(request, question):
    choices = []
    jstriggers = []

    cd = question.getcheckdict()
    key = "question_%s" % question.number
    key2 = "question_%s_comment" % question.number
    val = None
    possibledbvalue = question.get_value_for_run_question(get_runid_from_request(request))
    if key in request.POST:
        val = request.POST[key]
    elif not possibledbvalue == None:
        valueaslist = ast.literal_eval(possibledbvalue)
        val = valueaslist[0]
    else:
        if 'default' in cd:
            val = cd['default']
    for choice in question.choices():
        choices.append( ( choice.value == val, choice, ) )

    if question.type in ( 'choice-freeform','choice-freeform-optional'):
        jstriggers.append('%s_comment' % question.number)
    template = question.type[:-9] if question.type.endswith('-optional') else question.type
    

    return {
        'choices'   : choices,
        'sel_entry' : val == '_entry_',
        'qvalue'    : val or '',
        "template"  : "questionnaire/{}.html".format(template),
        'required'  : not question.type in ( 'choice-optional', 'choice-freeform-optional'),
        'comment'   : request.POST.get(key2, ""),
        'jstriggers': jstriggers,
    }

@answer_proc('choice', 'choice-freeform', 'dropdown', 'choice-optional', 'choice-freeform-optional')
def process_choice(question, answer):
    opt = answer['ANSWER'] or ''
    if not opt and not question.type.endswith( '-optional'):
        raise AnswerException(_(u'You must select an option'))
    if opt == '_entry_' and question.type.startswith('choice-freeform'):
        opt = answer.get('comment','')
        if not opt:
            raise AnswerException(_(u'Field cannot be blank'))
        return dumps([[opt]])
    else:
        valid = [c.value for c in question.choices()]
        if opt and opt not in valid:
            raise AnswerException(_(u'Invalid option!'))
    return dumps([opt])
add_type('choice', 'Choice [radio]')
add_type('choice-freeform', 'Choice with a freeform option [radio]')
add_type('choice-optional', 'Optional choice [radio]')
add_type('choice-freeform-optional', 'Optional choice with a freeform option [radio]')
add_type('dropdown', 'Dropdown choice [select]')

@question_proc('choice-multiple', 'choice-multiple-freeform', 'choice-multiple-values')
def question_multiple(request, question):
    key = "question_%s" % question.number
    choices = []
    jstriggers = []
    counter = 0
    qvalues = []
    cd = question.getcheckdict()
    defaults = cd.get('default','').split(',')
    possibledbvalue = question.get_value_for_run_question(get_runid_from_request(request))
    possiblelist = []
    if not possibledbvalue == None:
        possiblelist = ast.literal_eval(possibledbvalue)
    prev_vals = {}
    if question.type == 'choice-multiple-values':
        pl = []
        for choice_value, prev_value in possiblelist:
            pl.append(choice_value)
            prev_vals[choice_value] = str(prev_value)
        possiblelist = pl

#    print 'possible value is ', possibledbvalue, ', possiblelist is ', possiblelist

    for choice in question.choices():
        counter += 1
        key = "question_%s_multiple_%d" % (question.number, choice.sortid)
        if question.type == "choice-multiple-values":
            jstriggers.append("q%s_%s_box" % (question.number, choice.value))
            # so that the number box will be activated when item is checked
            
        #try database first and only after that fall back to post choices
#        print 'choice multiple checking for match for choice ', choice
        checked = ' checked'
        prev_value = ''
        qvalue = "%s_%s" % (question.number, choice.value)
        if key in request.POST or \
          (request.method == 'GET' and choice.value in defaults):
            qvalues.append(qvalue)
            value_key = "question_%s_%s_value" % (question.number, choice.value)
            if value_key in request.POST:
                prev_value = request.POST[value_key]
        elif choice.value in possiblelist:
            qvalues.append(qvalue)
            # so that this choice being checked will trigger anything that depends on it -
            # for choice-multiple-values right now
            if choice.value in prev_vals.keys():
                prev_value = prev_vals[choice.value]
        else:
            checked = ''
        # bug: you can have one item checked from database and another from POST data

        choices.append( (choice, key, checked, prev_value,) )

    extracount = int(cd.get('extracount', 0))
    if not extracount and question.type == 'choice-multiple-freeform':
        extracount = 1
    extras = []
    for x in range(1, extracount+1):
        key = "question_%s_more%d" % (question.number, x)
        if key in request.POST:
            extras.append( (key, request.POST[key],) )
        else:
            extras.append( (key, '',) )
        # right now does not retrieve extra fields from database
    return {
        "choices": choices,
        "extras": extras,
        "type": question.type,
        "template"  : "questionnaire/choice-multiple-freeform.html",
        "required" : cd.get("required", False) and cd.get("required") != "0",
        "jstriggers": jstriggers,
        "qvalues": qvalues
    }

@answer_proc('choice-multiple', 'choice-multiple-freeform', 'choice-multiple-values')
def process_multiple(question, answer):
    multiple = []
    multiple_freeform = []

    #this is the same thing as a minimum count so use it for that..
    requiredcount = 0
    required = question.getcheckdict().get('required', 0)
    if required:
        try:
            requiredcount = int(required)
        except ValueError:
            requiredcount = 1
    if requiredcount and requiredcount > question.choices().count():
        requiredcount = question.choices().count()

    #added support for a max number of choices
    maxcount = 9999
    maxdict = question.getcheckdict().get('max', 0)
    if maxdict:
        try:
            maxcount = int(maxdict)
        except ValueError:
            pass #leave maxcount at 9999

    if maxcount and maxcount > question.choices().count():
        maxcount = question.choices().count()

    for k, v in answer.items():
        if k.startswith('multiple') and not k.endswith('value'):
            multiple.append(v)
        if k.startswith('more') and len(v.strip()) > 0:
            multiple_freeform.append(v)
    
    if question.type == 'choice-multiple-values':
    # check for associated values for choice-multiple-values
        total = 0
        floats = False
        notnumbers = False
        for k, v in answer.items():
            if k.endswith('value'):
                choice_text = k.rsplit("_", 2)[0]
                if choice_text in multiple:
                    val = v
                    multiple.remove(choice_text)
                    try:
                        val = int(v)
                        total += val
                    except ValueError:  # not an int
                        try:
                            val = float(v)
                            floats = True
                        except ValueError:  # not a float or int
                            notnumbers = True
                    multiple.append([choice_text, val])

        if floats:
            raise AnswerException(ungettext(u"Please enter a whole number - no decimal places", u"Please enter whole numbers - no decimal places", len(multiple)))

        if notnumbers:
            raise AnswerException(ungettext(u"Value must be a number (with no decimal places)", u"All values must be numbers (with no decimal places)", len(multiple)))

        if len(multiple) > 0 and total != 100:
            raise AnswerException(ungettext(u"Did you mean 100% for one choice? Please enter 100 or add other choices.", u"Values must add up to 100.", len(multiple)))

        
    if len(multiple) + len(multiple_freeform) < requiredcount:
        raise AnswerException(ungettext(u"You must select at least %d option",
                                        u"You must select at least %d options",
                                        requiredcount) % requiredcount)

    if len(multiple) + len(multiple_freeform) > maxcount:
        raise AnswerException(ungettext(u"You must select at most %d options",
                                        u"You must select at most %d options",
                                        maxcount) % maxcount)
    multiple.sort()
    if multiple_freeform:
        multiple.append(multiple_freeform)

    return dumps(multiple)
add_type('choice-multiple', 'Multiple-Choice, Multiple-Answers [checkbox]')
add_type('choice-multiple-freeform', 'Multiple-Choice, Multiple-Answers, plus freeform [checkbox, input]')
add_type('choice-multiple-values', 'Multiple-Choice, Multiple-Answers [checkboxes], plus value box [input] for each selected answer')


