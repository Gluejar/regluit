import ast
from json import dumps
from django.utils.translation import ugettext as _
from .. import add_type, question_proc, answer_proc, AnswerException
from ..utils import get_runid_from_request


#true if either 'required' or if 'requiredif' is satisfied
#def is_required

@question_proc('choice-yesno', 'choice-yesnocomment', 'choice-yesnodontknow','choice-yesno-optional', 'choice-yesnocomment-optional', 'choice-yesnodontknow-optional')
def question_yesno(request, question):
    key = "question_%s" % question.number
    key2 = "question_%s_comment" % question.number
    val = request.POST.get(key, None)
    cmt = request.POST.get(key2, '')
    qtype = question.get_type()
    cd = question.getcheckdict()
    jstriggers = []

    if qtype.startswith('choice-yesnocomment'):
        hascomment = True
    else:
        hascomment = False
    if qtype.startswith( 'choice-yesnodontknow') or 'dontknow' in cd:
        hasdontknow = True
    else:
        hasdontknow = False

    #try the database before reverting to default
    possiblevalue = question.get_value_for_run_question(get_runid_from_request(request))
    if not possiblevalue == None:
        #save process always listifies the answer so we unlistify it to put it back in the field
        valueaslist = ast.literal_eval(possiblevalue)
        if len(valueaslist) > 0:
            val = valueaslist[0]

    if not val:
        if cd.get('default', None):
            val = cd['default']

    checks = ''
    if hascomment:
        if cd.get('required-yes'):
            jstriggers = ['%s_comment' % question.number]
            checks = ' checks="dep_check(\'%s,yes\')"' % question.number
        elif cd.get('required-no'):
            checks = ' checks="dep_check(\'%s,no\')"' % question.number
        elif cd.get('required-dontknow'):
            checks = ' checks="dep_check(\'%s,dontknow\')"' % question.number

    return {
        'required': not qtype.endswith("-optional"),
        'checks': checks,
        'value': val,
        'qvalue': val,
        'hascomment': hascomment,
        'hasdontknow': hasdontknow,
        'comment': cmt,
        'jstriggers': jstriggers,
        'template': 'questionnaire/choice-yesnocomment.html',
    }


@question_proc('open', 'open-textfield')
def question_open(request, question):
    key = "question_%s" % question.number
    value = question.getcheckdict().get('default', '')
    if key in request.POST:
        value = request.POST[key]
    else:
        #also try to get it from the database so we can handle back/forward in which post has been cleared
        possiblevalue = question.get_value_for_run_question(get_runid_from_request(request))
        if not possiblevalue == None:
            #save process always listifies the answer so we unlistify it to put it back in the field
            valueaslist = ast.literal_eval(possiblevalue)
            if len(valueaslist) > 0:
                value = valueaslist[0]
    return {
        'required': question.getcheckdict().get('required', False),
        'value': value,
    }


@answer_proc('open', 'open-textfield', 'choice-yesno', 'choice-yesnocomment', 'choice-yesnodontknow','choice-yesno-optional', 'choice-yesnocomment-optional', 'choice-yesnodontknow-optional')
def process_simple(question, ansdict):
#    print 'process_simple has question, ansdict ', question, ',', ansdict
    checkdict = question.getcheckdict()
    ans = ansdict['ANSWER'] or ''
    qtype = question.get_type()
    if qtype.startswith('choice-yesno'):
        if ans not in ('yes', 'no', 'dontknow') and not qtype.endswith('-optional'):
            raise AnswerException(_(u'You must select an option'))
        if qtype == 'choice-yesnocomment' \
                and len(ansdict.get('comment', '').strip()) == 0:
            if checkdict.get('required', False):
                raise AnswerException(_(u'Field cannot be blank'))
            if checkdict.get('required-yes', False) and ans == 'yes':
                raise AnswerException(_(u'Field cannot be blank'))
            if checkdict.get('required-no', False) and ans == 'no':
                raise AnswerException(_(u'Field cannot be blank'))
    else:
        #the key here is to note that requiredif has already been evaluated or we wouldn't have reached this point, so we don't have to recheck
        if not ans.strip() and (checkdict.get('required', False) or checkdict.get('requiredif', False)):
            raise AnswerException(_(u'Field cannot be blank'))
        maxwords = checkdict.get('maxwords', False)
        if maxwords:
            maxwords = int(maxwords)
            answords = len(ans.split())
            if answords > maxwords:
                raise AnswerException(_(u'Answer is ' + str(answords) + ' words.  Please shorten answer to ' + str(maxwords) + ' words or less'))
    if ansdict.has_key('comment') and len(ansdict['comment']) > 0:
        return dumps([ans, [ansdict['comment']]])
    if ans:
        return dumps([ans])
    return dumps([])


add_type('open', 'Open Answer, single line [input]')
add_type('open-textfield', 'Open Answer, multi-line [textarea]')
add_type('choice-yesno', 'Yes/No Choice [radio]')
add_type('choice-yesnocomment', 'Yes/No Choice with optional comment [radio, input]')
add_type('choice-yesnodontknow', 'Yes/No/Don\'t know Choice [radio]')
add_type('choice-yesno-optional', 'Optional Yes/No Choice [radio]')
add_type('choice-yesnocomment-optional', 'Optional Yes/No Choice with optional comment [radio, input]')
add_type('choice-yesnodontknow-optional', 'Optional Yes/No/Don\'t know Choice [radio]')


@answer_proc('comment')
def process_comment(question, answer):
    pass


add_type('comment', 'Comment Only')



