#!/usr/bin/python
# vim: set fileencoding=utf-8
import logging
import random
import re
import tempfile

from compat import commit_on_success, commit, rollback
from hashlib import md5
from uuid import uuid4

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic.base import TemplateView
from django.db import transaction
from django.conf import settings
from datetime import datetime
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from . import QuestionProcessors
from . import questionnaire_start, questionset_start, questionset_done, questionnaire_done
from . import AnswerException
from . import Processors
from . import profiler
from .models import *
from .parsers import *
from .parsers import BoolNot, BoolAnd, BoolOr, Checker
from .emails import _send_email, send_emails
from .utils import numal_sort, split_numal, UnicodeWriter
from .request_cache import request_cache
from .dependency_checker import dep_check


try:
    use_session = settings.QUESTIONNAIRE_USE_SESSION
except AttributeError:
    use_session = False

try:
    debug_questionnaire = settings.QUESTIONNAIRE_DEBUG
except AttributeError:
    debug_questionnaire = False


def r2r(tpl, request, **contextdict):
    "Shortcut to use RequestContext instead of Context in templates"
    contextdict['request'] = request
    return render(request, tpl, contextdict)


def get_runinfo(random):
    "Return the RunInfo entry with the provided random key"
    res = RunInfo.objects.filter(random=random.lower())
    return res and res[0] or None


def get_question(number, questionset):
    "Return the specified Question (by number) from the specified Questionset"
    res = Question.objects.filter(number=number, questionset=questionset)
    return res and res[0] or None


def delete_answer(question, subject, run):
    "Delete the specified question/subject/run combination from the Answer table"
    Answer.objects.filter(subject=subject, run=run, question=question).delete()


def add_answer(runinfo, question, answer_dict):
    """
    Add an Answer to a Question for RunInfo, given the relevant form input

    answer_dict contains the POST'd elements for this question, minus the
    question_{number} prefix.  The question_{number} form value is accessible
    with the ANSWER key.
    """
    answer = Answer()
    answer.question = question
    answer.subject = runinfo.subject
    answer.run = runinfo.run

    type = question.get_type()

    if "ANSWER" not in answer_dict:
        answer_dict['ANSWER'] = None

    if type in Processors:
        answer.answer = Processors[type](question, answer_dict) or ''
    else:
        raise AnswerException("No Processor defined for question type %s" % type)

    # first, delete all existing answers to this question for this particular user+run
    delete_answer(question, runinfo.subject, runinfo.run)

    # then save the new answer to the database
    answer.save(runinfo)

    return True


def check_parser(runinfo, exclude=[]):
    depparser = BooleanParser(dep_check, runinfo, {})
    tagparser = BooleanParser(has_tag, runinfo)

    fnmap = {
        "maleonly": lambda v: runinfo.subject.gender == 'male',
        "femaleonly": lambda v: runinfo.subject.gender == 'female',
        "shownif": lambda v: v and depparser.parse(v),
        "iftag": lambda v: v and tagparser.parse(v)
    }

    for ex in exclude:
        del fnmap[ex]

    @request_cache()
    def satisfies_checks(checks):
        if not checks:
            return True

        checks = parse_checks(checks)

        for check, value in checks.items():
            if check in fnmap:
                value = value and value.strip()
                if not fnmap[check](value):
                    return False

        return True

    return satisfies_checks


@request_cache()
def skipped_questions(runinfo):
    if not runinfo.skipped:
        return []

    return [s.strip() for s in runinfo.skipped.split(',')]


@request_cache()
def question_satisfies_checks(question, runinfo, checkfn=None):
    if question.number in skipped_questions(runinfo):
        return False

    checkfn = checkfn or check_parser(runinfo)
    return checkfn(question.checks)


@request_cache(keyfn=lambda *args: args[0].id)
def questionset_satisfies_checks(questionset, runinfo, checks=None):
    """Return True if the runinfo passes the checks specified in the QuestionSet

    Checks is an optional dictionary with the keys being questionset.pk and the
    values being the checks of the contained questions.

    This, in conjunction with fetch_checks allows for fewer
    db roundtrips and greater performance.

    Sadly, checks cannot be hashed and therefore the request cache is useless
    here. Thankfully the benefits outweigh the costs in my tests.
    """

    passes = check_parser(runinfo)

    if not passes(questionset.checks):
        return False

    if not checks:
        checks = dict()
        checks[questionset.id] = []

        for q in questionset.questions():
            checks[questionset.id].append((q.checks, q.number))

    # questionsets that pass the checks but have no questions are shown
    # (comments, last page, etc.)
    if not checks[questionset.id]:
        return True

    # if there are questions at least one needs to be visible
    for check, number in checks[questionset.id]:
        if number in skipped_questions(runinfo):
            continue

        if passes(check):
            return True

    return False


def get_progress(runinfo):
    position, total = 0, 0

    current = runinfo.questionset
    sets = current.questionnaire.questionsets()

    checks = fetch_checks(sets)

    # fetch the all question checks at once. This greatly improves the
    # performance of the questionset_satisfies_checks function as it
    # can avoid a roundtrip to the database for each question

    for qs in sets:
        if questionset_satisfies_checks(qs, runinfo, checks):
            total += 1

        if qs.id == current.id:
            position = total

    if not all((position, total)):
        progress = 1
    else:
        progress = float(position) / float(total) * 100.00

        # progress is always at least one percent
        progress = progress >= 1.0 and progress or 1

    return int(progress)


def get_async_progress(request, *args, **kwargs):
    """ Returns the progress as json for use with ajax """

    if 'runcode' in kwargs:
        runcode = kwargs['runcode']
    else:
        session_runcode = request.session.get('runcode', None)
        if session_runcode is not None:
            runcode = session_runcode

    runinfo = get_runinfo(runcode)
    response = dict(progress=get_progress(runinfo))

    cache.set('progress' + runinfo.random, response['progress'])
    response = HttpResponse(json.dumps(response),
                            content_type='application/javascript');
    response["Cache-Control"] = "no-cache"
    return response


def fetch_checks(questionsets):
    ids = [qs.pk for qs in questionsets]

    query = Question.objects.filter(questionset__pk__in=ids)
    query = query.values('questionset_id', 'checks', 'number')

    checks = dict()
    for qsid in ids:
        checks[qsid] = list()

    for result in (r for r in query):
        checks[result['questionset_id']].append(
            (result['checks'], result['number'])
        )

    return checks


def redirect_to_qs(runinfo, request=None):
    "Redirect to the correct and current questionset URL for this RunInfo"

    # cache current questionset
    qs = runinfo.questionset

    # skip questionsets that don't pass
    if not questionset_satisfies_checks(runinfo.questionset, runinfo):

        next = runinfo.questionset.next()

        while next and not questionset_satisfies_checks(next, runinfo):
            next = next.next()

        runinfo.questionset = next
        runinfo.save()

        hasquestionset = bool(next)
    else:
        hasquestionset = True

    # empty ?
    if not hasquestionset:
        logging.warn('no questionset in questionnaire which passes the check')
        return finish_questionnaire(request, runinfo, qs.questionnaire)

    if not use_session:
        args = [runinfo.random, runinfo.questionset.sortid]
        urlname = 'questionset'
    else:
        args = []
        request.session['qs'] = runinfo.questionset.sortid
        request.session['runcode'] = runinfo.random
        urlname = 'questionnaire'

    url = reverse(urlname, args=args)
    return HttpResponseRedirect(url)


def redirect_to_prev_questionnaire(request, runcode=None, qs=None):
    """
    Takes the questionnaire set in the session and redirects to the
    previous questionnaire if any. Used for linking to previous pages
    both when using sessions or not. 
    """
    if use_session:
        runcode = request.session.get('runcode', None)

    if runcode is not None:
        runinfo = get_runinfo(runcode)
        if qs:
            qs = get_object_or_404(QuestionSet, sortid=qs, questionnaire=runinfo.questionset.questionnaire)
            prev_qs = qs.prev()
        else:
            prev_qs = runinfo.questionset.prev()

        while prev_qs and not questionset_satisfies_checks(prev_qs, runinfo):
            prev_qs = prev_qs.prev()

        if runinfo and prev_qs:
            if use_session:
                request.session['runcode'] = runinfo.random
                request.session['qs'] = prev_qs.sortid
                return HttpResponseRedirect(reverse('questionnaire'))

            else:
                runinfo.questionset = prev_qs
                runinfo.save()
                return HttpResponseRedirect(reverse('questionnaire', args=[runinfo.random]))

    return HttpResponseRedirect('/')

@commit_on_success
def questionnaire(request, runcode=None, qs=None):
    """
    Process submit answers (if present) and redirect to next page

    If this is a POST request, parse the submitted data in order to store
    all the submitted answers.  Then return to the next questionset or
    return a completed response.

    If this isn't a POST request, redirect to the main page.

    We only commit on success, to maintain consistency.  We also specifically
    rollback if there were errors processing the answers for this questionset.
    """
    if use_session:
        session_runcode = request.session.get('runcode', None)
        if session_runcode is not None:
            runcode = session_runcode

        session_qs = request.session.get('qs', None)
        if session_qs is not None:
            qs = session_qs

    # if runcode provided as query string, redirect to the proper page
    if not runcode:
        runcode = request.GET.get('runcode')
        if not runcode:
            return HttpResponseRedirect("/")
        else:
            if not use_session:
                args = [runcode, ]
            else:
                request.session['runcode'] = runcode
                args = []
            
            return HttpResponseRedirect(reverse("questionnaire", args=args))


    runinfo = get_runinfo(runcode)

    if not runinfo:
        commit()
        return HttpResponseRedirect('/')

    if runinfo.questionset.questionnaire.admin_access_only == 1:
        if not request.user.is_superuser:
            return HttpResponseRedirect(runinfo.questionset.questionnaire.redirect_url)

    # let the runinfo have a piggy back ride on the request
    # so we can easily use the runinfo in places like the question processor
    # without passing it around
    request.runinfo = runinfo

    if not qs:
        # Only change the language to the subjects choice for the initial
        # questionnaire page (may be a direct link from an email)
        if hasattr(request, 'session'):
            request.session['django_language'] = runinfo.subject.language
            translation.activate(runinfo.subject.language)

    if 'lang' in request.GET:
        return set_language(request, runinfo, request.path)

    # --------------------------------
    # --- Handle non-POST requests ---
    # --------------------------------

    if request.method != "POST":
        if qs is not None:
            qs = get_object_or_404(QuestionSet, sortid=qs, questionnaire=runinfo.questionset.questionnaire)
            if runinfo.random.startswith('test:'):
                pass  # ok for testing
            elif qs.sortid > runinfo.questionset.sortid:
                # you may jump back, but not forwards
                return redirect_to_qs(runinfo, request)
            runinfo.questionset = qs
            runinfo.save()
            commit()
        # no questionset id in URL, so redirect to the correct URL
        if qs is None:
            return redirect_to_qs(runinfo, request)
        questionset_start.send(sender=None, runinfo=runinfo, questionset=qs)
        return show_questionnaire(request, runinfo)

    # -------------------------------------
    # --- Process POST with QuestionSet ---
    # -------------------------------------

    # if the submitted page is different to what runinfo says, update runinfo
    # XXX - do we really want this?
    qs = request.POST.get('questionset_id', qs)
    try:
        qsobj = QuestionSet.objects.filter(pk=qs)[0]
        if qsobj.questionnaire == runinfo.questionset.questionnaire:
            if runinfo.questionset != qsobj:
                runinfo.questionset = qsobj
                runinfo.save()
    except:
        pass

    questionnaire = runinfo.questionset.questionnaire
    questionset = runinfo.questionset


    # to confirm that we have the correct answers
    expected = questionset.questions()

    items = request.POST.items()
    extra = {}  # question_object => { "ANSWER" : "123", ... }

    # this will ensure that each question will be processed, even if we did not receive
    # any fields for it. Also works to ensure the user doesn't add extra fields in
    for x in expected:
        items.append((u'question_%s_Trigger953' % x.number, None))

    # generate the answer_dict for each question, and place in extra
    for item in items:
        key, value = item[0], item[1]
        if key.startswith('question_'):
            answer = key.split("_", 2)
            question = get_question(answer[1], questionset)
            if not question:
                logging.warn("Unknown question when processing: %s" % answer[1])
                continue
            extra[question] = ans = extra.get(question, {})
            if (len(answer) == 2):
                ans['ANSWER'] = value
            elif (len(answer) == 3):
                ans[answer[2]] = value
            else:
                logging.warn("Poorly formed form element name: %r" % answer)
                continue
            extra[question] = ans

    errors = {}
    for question, ans in extra.items():
        if not question_satisfies_checks(question, runinfo):
            continue
        if u"Trigger953" not in ans:
            logging.warn("User attempted to insert extra question (or it's a bug)")
            continue
        try:
            cd = question.getcheckdict()
            # requiredif is the new way
            depon = cd.get('requiredif', None) or cd.get('dependent', None)
            if depon:
                depparser = BooleanParser(dep_check, runinfo, extra)
                if not depparser.parse(depon):
                    # if check is not the same as answer, then we don't care
                    # about this question plus we should delete it from the DB
                    delete_answer(question, runinfo.subject, runinfo.run)
                    if cd.get('store', False):
                        runinfo.set_cookie(question.number, None)
                    continue
            add_answer(runinfo, question, ans)
            if cd.get('store', False):
                runinfo.set_cookie(question.number, ans['ANSWER'])
        except AnswerException, e:
            errors[question.number] = e
        except Exception:
            logging.exception("Unexpected Exception")
            rollback()
            raise

    if len(errors) > 0:
        res = show_questionnaire(request, runinfo, errors=errors)
        rollback()
        return res

    questionset_done.send(sender=None, runinfo=runinfo, questionset=questionset)

    next = questionset.next()
    while next and not questionset_satisfies_checks(next, runinfo):
        next = next.next()
    runinfo.questionset = next
    runinfo.save()
    if use_session:
        request.session['prev_runcode'] = runinfo.random

    if next is None:  # we are finished
        return finish_questionnaire(request, runinfo, questionnaire)

    commit()
    return redirect_to_qs(runinfo, request)


def finish_questionnaire(request, runinfo, questionnaire):
    hist = RunInfoHistory()
    hist.subject = runinfo.subject
    hist.run = runinfo.run
    hist.completed = datetime.now()
    hist.questionnaire = questionnaire
    hist.tags = runinfo.tags
    hist.skipped = runinfo.skipped
    hist.landing = runinfo.landing
    hist.save()

    questionnaire_done.send(sender=None, runinfo=runinfo,
                            questionnaire=questionnaire)
    lang=translation.get_language()
    redirect_url = questionnaire.redirect_url
    for x, y in (('$LANG', lang),
                 ('$SUBJECTID', runinfo.subject.id),
                 ('$RUNID', runinfo.run.runid),):
        redirect_url = redirect_url.replace(x, str(y))

    if runinfo.run.runid in ('12345', '54321') \
            or runinfo.run.runid.startswith('test:'):
        runinfo.questionset = QuestionSet.objects.filter(questionnaire=questionnaire).order_by('sortid')[0]
        runinfo.save()
    else:
        runinfo.delete()
    commit()
    if redirect_url:
        return HttpResponseRedirect(redirect_url)
    return r2r("questionnaire/complete.{}.html".format(lang), request, landing_object=hist.landing.content_object)


def recursivly_build_partially_evaluated_javascript_expression_for_shownif_check(treenode, runinfo, question):
    if isinstance(treenode, BoolNot):
        return "!( %s )" % recursivly_build_partially_evaluated_javascript_expression_for_shownif_check(treenode.arg, runinfo, question)
    elif isinstance(treenode, BoolAnd):
        return " && ".join( 
            "( %s )" % recursivly_build_partially_evaluated_javascript_expression_for_shownif_check(arg, runinfo, question)
            for arg in treenode.args )
    elif isinstance(treenode, BoolOr):
        return " || ".join( 
            "( %s )" % recursivly_build_partially_evaluated_javascript_expression_for_shownif_check(arg, runinfo, question)
            for arg in treenode.args )
    else:
        assert( isinstance(treenode, Checker) )
        # ouch, we're assuming the correct syntax is always found
        question_looksee_number = treenode.expr.split(",", 1)[0]
        if Question.objects.get(number=question_looksee_number).questionset \
           != question.questionset:
            return "true" if dep_check(treenode.expr, runinfo, {}) else "false"
        else:
            return str(treenode)

def make_partially_evaluated_javascript_expression_for_shownif_check(checkexpression, runinfo, question):
    depparser = BooleanParser(dep_check, runinfo, {})
    parsed_bool_expression_results = depparser.boolExpr.parseString(checkexpression)[0]
    return recursivly_build_partially_evaluated_javascript_expression_for_shownif_check(parsed_bool_expression_results, runinfo, question)
    
def show_questionnaire(request, runinfo, errors={}):
    """
    Return the QuestionSet template

    Also add the javascript dependency code.
    """

    request.runinfo = runinfo

    if request.GET.get('show_all') == '1':  # for debugging purposes.
        questions = runinfo.questionset.questionnaire.questions()
    else:
        questions = runinfo.questionset.questions()

    show_all = request.GET.get('show_all') == '1'  # for debugging purposes in some cases we may want to show all questions on one screen.
    questionset = runinfo.questionset
    questions = questionset.questionnaire.questions() if show_all else questionset.questions()

    qlist = []
    jsinclude = []  # js files to include
    cssinclude = []  # css files to include
    jstriggers = []
    qvalues = {}

    # initialize qvalues
    cookiedict = runinfo.get_cookiedict()

    for k, v in cookiedict.items():
        qvalues[k] = v

    substitute_answer(qvalues, runinfo.questionset)

    #we make it clear to the user that we're going to sort by sort id then number, so why wasn't it doing that?
    questions = sorted(questions, key=lambda question: (question.sort_id, question.number))

    for question in questions:
        # if we got here the questionset will at least contain one question
        # which passes, so this is all we need to check for
        question_visible = question_satisfies_checks(question, runinfo) or show_all
        Type = question.get_type()
        _qnum, _qalpha = split_numal(question.number)

        qdict = {
            'css_style': '' if question_visible else 'display:none;',
            'template': 'questionnaire/%s.html' % (Type),
            'qnum': _qnum,
            'qalpha': _qalpha,
            'qtype': Type,
            'qnum_class': (_qnum % 2 == 0) and " qeven" or " qodd",
            'qalpha_class': _qalpha and (ord(_qalpha[-1]) % 2 \
                                         and ' alodd' or ' aleven') or '',
        }

        # substitute answer texts
        substitute_answer(qvalues, question)

        # add javascript dependency checks
        cd = question.getcheckdict()
        
        # Note: dep_check() is showing up on pages where questions rely on previous pages' questions -
        # this causes disappearance of questions, since there are no qvalues for questions on previous
        # pages. BUT depon will be false if the question is a SAMEAS of another question with no off-page
        # checks. This will make no bad dep_check()s appear for these SAMEAS questions, circumventing the 
        # problem. Eventually need to fix either getcheckdict() (to screen out questions on previous pages) 
        # or prevent JavaScript from hiding questions when check_dep() cannot find a key in qvalues.
        depon = cd.get('requiredif', None) or cd.get('dependent', None) or cd.get('shownif', None)
        if depon:
            willberequiredif = bool(cd.get("requiredif", None) )
            willbedependent = bool(cd.get("dependent", None) )
            willbe_shownif = (not willberequiredif) and (not willbedependent) and bool(cd.get("shownif", None))
        
            # jamie and mark funkyness to be only done if depon is shownif, some similar thought is due to requiredif
            # for shownon, we have to deal with the fact that only the answers from this page are available to the JS
            # so we do a partial parse to form the checks="" attribute 
            if willbe_shownif:
                qdict['checkstring'] = ' checks="%s"' % make_partially_evaluated_javascript_expression_for_shownif_check(
                    depon, runinfo, question
                )
                    
            else:
                # extra args to BooleanParser are not required for toString
                parser = BooleanParser(dep_check)
                qdict['checkstring'] = ' checks="%s"' % parser.toString(depon)
            jstriggers.append('qc_%s' % question.number)

        footerdep = cd.get('footerif', None)
        if footerdep:
            parser = BooleanParser(dep_check)
            qdict['footerchecks'] = ' checks="%s"' % parser.toString(footerdep)
            jstriggers.append('qc_%s_footer' % question.number)

        if 'default' in cd and not question.number in cookiedict:
            qvalues[question.number] = cd['default']
        if Type in QuestionProcessors:
            qdict.update(QuestionProcessors[Type](request, question))
            if 'jsinclude' in qdict:
                if qdict['jsinclude'] not in jsinclude:
                    jsinclude.extend(qdict['jsinclude'])
            if 'cssinclude' in qdict:
                if qdict['cssinclude'] not in cssinclude:
                    cssinclude.extend(qdict['jsinclude'])
            if 'jstriggers' in qdict:
                jstriggers.extend(qdict['jstriggers'])
            if 'qvalue' in qdict and not question.number in cookiedict:
                qvalues[question.number] = qdict['qvalue']
            if 'qvalues' in qdict:
            # for multiple selection
                for choice in qdict['qvalues']:
                    qvalues[choice] = 'true'

        qlist.append((question, qdict))

    try:
        has_progress = settings.QUESTIONNAIRE_PROGRESS in ('async', 'default')
        async_progress = settings.QUESTIONNAIRE_PROGRESS == 'async'
    except AttributeError:
        has_progress = True
        async_progress = False

    if has_progress:
        if async_progress:
            progress = cache.get('progress' + runinfo.random, 1)
        else:
            progress = get_progress(runinfo)
    else:
        progress = 0

    if request.POST:
        for k, v in request.POST.items():
            if k.startswith("question_"):
                s = k.split("_")
                if s[-1] == "value":    # multiple checkboxes with value boxes
                    qvalues["_".join(s[1:])] = v
                elif len(s) == 4:
                    qvalues[s[1] + '_' + v] = '1'  # evaluates true in JS
                elif len(s) == 3 and s[2] == 'comment':
                    qvalues[s[1] + '_' + s[2]] = v
                else:
                    qvalues[s[1]] = v

    if use_session:
        prev_url = reverse('redirect_to_prev_questionnaire')
    else:
        prev_url = reverse('redirect_to_prev_questionnaire', args=[runinfo.random, runinfo.questionset.sortid])
        
    current_answers = []
    if debug_questionnaire:
        current_answers = Answer.objects.filter(subject=runinfo.subject, run=runinfo.run).order_by('id')


    r = r2r("questionnaire/questionset.html", request,
            questionset=runinfo.questionset,
            runinfo=runinfo,
            errors=errors,
            qlist=qlist,
            progress=progress,
            triggers=jstriggers,
            qvalues=qvalues,
            jsinclude=jsinclude,
            cssinclude=cssinclude,
            async_progress=async_progress,
            async_url=reverse('progress', args=[runinfo.random]),
            prev_url=prev_url,
            current_answers=current_answers,
    )
    r['Cache-Control'] = 'no-cache'
    r['Expires'] = "Thu, 24 Jan 1980 00:00:00 GMT"
    r.set_cookie('questionset_id', str(questionset.id))    
    return r


def substitute_answer(qvalues, obj):
    """Objects with a 'text/text_xx' attribute can contain magic strings
    referring to the answers of other questions. This function takes
    any such object, goes through the stored answers (qvalues) and replaces
    the magic string with the actual value. If this isn't possible the
    magic string is removed from the text.

    Only answers with 'store' in their check will work with this.

    """

    if qvalues and obj.text:
        magic = 'subst_with_ans_'
        regex = r'subst_with_ans_(\S+)'

        replacements = re.findall(regex, obj.text)
        text_attributes = [a for a in dir(obj) if a.startswith('text_')]

        for answerid in replacements:

            target = magic + answerid
            replacement = qvalues.get(answerid.lower(), '')

            for attr in text_attributes:
                oldtext = getattr(obj, attr)
                newtext = oldtext.replace(target, replacement)

                setattr(obj, attr, newtext)


def set_language(request, runinfo=None, next=None):
    """
    Change the language, save it to runinfo if provided, and
    redirect to the provided URL (or the last URL).
    Can also be used by a url handler, w/o runinfo & next.
    """
    if not next:
        next = request.GET.get('next', request.POST.get('next', None))
    if not next:
        next = request.META.get('HTTP_REFERER', None)
        if not next:
            next = '/'
    response = HttpResponseRedirect(next)
    response['Expires'] = "Thu, 24 Jan 1980 00:00:00 GMT"
    if request.method == 'GET':
        lang_code = request.GET.get('lang', None)
        if lang_code and translation.check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            if runinfo:
                runinfo.subject.language = lang_code
                runinfo.subject.save()
    return response


def _table_headers(questions):
    """
    Return the header labels for a set of questions as a list of strings.

    This will create separate columns for each multiple-choice possiblity
    and freeform options, to avoid mixing data types and make charting easier.
    """
    ql = list(questions)
    ql.sort(lambda x, y: numal_sort(x.number, y.number))
    columns = []
    for q in ql:
        if q.type.startswith('choice-yesnocomment'):
            columns.extend([q.number, q.number + "-freeform"])
        elif q.type.startswith('choice-freeform'):
            columns.extend([q.number, q.number + "-freeform"])
        elif q.type.startswith('choice-multiple'):
            cl = [c.value for c in q.choice_set.all()]
            cl.sort(numal_sort)
            columns.extend([q.number + '-' + value for value in cl])
            if q.type == 'choice-multiple-freeform':
                columns.append(q.number + '-freeform')
        else:
            columns.append(q.number)
    return columns

default_extra_headings = [u'subject', u'run id']

def default_extra_entries(subject, run):
    return ["%s/%s" % (subject.id, subject.ip_address), run.id]

@permission_required("questionnaire.export")
def export_csv(request, qid, 
        extra_headings=default_extra_headings,
        extra_entries=default_extra_entries,
        answer_filter=None,
        filecode=0,
    ):  
    """
    For a given questionnaire id, generate a CSV containing all the
    answers for all subjects.
    qid -- questionnaire_id
    extra_headings -- customize the headings for extra columns,
    extra_entries -- function returning a list of extra column entries,
    answer_filter -- custom filter for the answers
    filecode -- code for filename
    """
    fd = tempfile.TemporaryFile()

    questionnaire = get_object_or_404(Questionnaire, pk=int(qid))
    headings, answers = answer_export(questionnaire, answer_filter=answer_filter)

    writer = UnicodeWriter(fd)
    writer.writerow(extra_headings + headings)
    for subject, run, answer_row in answers:
        row = extra_entries(subject, run) + [
            a if a else '--' for a in answer_row]
        writer.writerow(row)
    fd.seek(0)

    response = HttpResponse(fd, content_type="text/csv")
    response['Content-Length'] = fd.tell()
    response['Content-Disposition'] = 'attachment; filename="answers-%s-%s.csv"' % (qid, filecode)
    return response


def answer_export(questionnaire, answers=None, answer_filter=None):
    """
    questionnaire -- questionnaire model for export
    answers -- query set of answers to include in export, defaults to all
    answer_filter -- filter for the answers

    Return a flat dump of column headings and all the answers for a
    questionnaire (in query set answers) in the form (headings, answers)
    where headings is:
        ['question1 number', ...]
    and answers is:
        [(subject1, 'runid1', ['answer1.1', ...]), ... ]

    The headings list might include items with labels like
    'questionnumber-freeform'.  Those columns will contain all the freeform
    answers for that question (separated from the other answer data).

    Multiple choice questions will have one column for each choice with
    labels like 'questionnumber-choice'.

    The items in the answers list are unicode strings or empty strings
    if no answer was given.  The number of elements in each answer list will
    always match the number of headings.
    """
    if answers is None:
        answers = Answer.objects.all()
    if answer_filter:
        answers = answer_filter(answers)
    answers = answers.filter(
        question__questionset__questionnaire=questionnaire).order_by(
        'subject', 'run__runid', 'question__questionset__sortid', 'question__number')
    answers = answers.select_related()
    questions = Question.objects.filter(
        questionset__questionnaire=questionnaire)
    headings = _table_headers(questions)

    coldict = {}
    for num, col in enumerate(headings):  # use coldict to find column indexes
        coldict[col] = num
    # collect choices for each question
    qchoicedict = {}
    for q in questions:
        qchoicedict[q.id] = [x[0] for x in q.choice_set.values_list('value')]

    runid = subject = None
    out = []
    row = []
    run = None
    for answer in answers:
        if answer.run != run or answer.subject != subject:
            if row:
                out.append((subject, run, row))
            run = answer.run
            subject = answer.subject
            row = [""] * len(headings)
        ans = answer.split_answer()
        if type(ans) == int:
            ans = str(ans)
        for choice in ans:
            col = None
            if type(choice) == list:
                # freeform choice
                choice = choice[0]
                col = coldict.get(answer.question.number + '-freeform', None)
            if col is None:  # look for enumerated choice column (multiple-choice)
                col = coldict.get(answer.question.number + '-' + unicode(choice), None)
            if col is None:  # single-choice items
                if ((not qchoicedict[answer.question.id]) or
                            choice in qchoicedict[answer.question.id]):
                    col = coldict.get(answer.question.number, None)
            if col is None:  # last ditch, if not found throw it in a freeform column
                col = coldict.get(answer.question.number + '-freeform', None)
            if col is not None:
                row[col] = choice
    # and don't forget about the last one
    if row:
        out.append((subject, run, row))
    return headings, out


def answer_summary(questionnaire, answers=None):
    """
    questionnaire -- questionnaire model for summary
    answers -- query set of answers to include in summary, defaults to all

    Return a summary of the answer totals in answer_qs in the form:
    [('q1', 'question1 text',
        [('choice1', 'choice1 text', num), ...],
        ['freeform1', ...]), ...]

    questions are returned in questionnaire order
    choices are returned in question order
    freeform options are case-insensitive sorted
    """

    if answers is None:
        answers = Answer.objects.all()
    answers = answers.filter(question__questionset__questionnaire=questionnaire)
    questions = Question.objects.filter(
        questionset__questionnaire=questionnaire).order_by(
        'questionset__sortid', 'number')

    summary = []
    for question in questions:
        q_type = question.get_type()
        if q_type.startswith('choice-yesno'):
            choices = [('yes', _('Yes')), ('no', _('No'))]
            if 'dontknow' in q_type:
                choices.append(('dontknow', _("Don't Know")))
        elif q_type.startswith('choice'):
            choices = [(c.value, c.text) for c in question.choices()]
        else:
            choices = []
        choice_totals = dict([(k, 0) for k, v in choices])
        freeforms = []
        for a in answers.filter(question=question):
            ans = a.split_answer()
            for choice in ans:
                if type(choice) == list:
                    freeforms.extend(choice)
                elif choice in choice_totals:
                    choice_totals[choice] += 1
                else:
                    # be tolerant of improperly marked data
                    freeforms.append(choice)
        freeforms.sort(numal_sort)
        summary.append((question.number, question.text, [
            (n, t, choice_totals[n]) for (n, t) in choices], freeforms))
    return summary


def has_tag(tag, runinfo):
    """ Returns true if the given runinfo contains the given tag. """
    return tag in (t.strip() for t in runinfo.tags.split(','))


@permission_required("questionnaire.management")
def send_email(request, runinfo_id):
    if request.method != "POST":
        return HttpResponse("This page MUST be called as a POST request.")
    runinfo = get_object_or_404(RunInfo, pk=int(runinfo_id))
    successful = _send_email(runinfo)
    return r2r("emailsent.html", request, runinfo=runinfo, successful=successful)


def generate_run(request, questionnaire_id, subject_id=None, context={}):
    """
    A view that can generate a RunID instance anonymously,
    and then redirect to the questionnaire itself.

    It uses a Subject with the givenname of 'Anonymous' and the
    surname of 'User'.  If this Subject does not exist, it will
    be created.

    This can be used with a URL pattern like:
    (r'^take/(?P<questionnaire_id>[0-9]+)/$', 'questionnaire.views.generate_run'),
    """
    qu = get_object_or_404(Questionnaire, id=questionnaire_id)
    qs = qu.questionsets()[0]

    if subject_id is not None:
        su = get_object_or_404(Subject, pk=subject_id)
    else:
        su = Subject(anonymous=True, ip_address=request.META['REMOTE_ADDR'])
        su.save()

#    str_to_hash = "".join(map(lambda i: chr(random.randint(0, 255)), range(16)))
    str_to_hash = str(uuid4())
    str_to_hash += settings.SECRET_KEY
    key = md5(str_to_hash).hexdigest()
    landing = context.get('landing', None)
    r = Run.objects.create(runid=key)
    run = RunInfo.objects.create(subject=su, random=key, run=r, questionset=qs, landing=landing)
    if not use_session:
        kwargs = {'runcode': key}
    else:
        kwargs = {}
        request.session['runcode'] = key

    questionnaire_start.send(sender=None, runinfo=run, questionnaire=qu)
    response = HttpResponseRedirect(reverse('questionnaire', kwargs=kwargs))
    response.set_cookie('next', context.get('next',''))
    return response

def generate_error(request):
    return 400/0

class SurveyView(TemplateView):
    template_name = "pages/generic.html"

    def get_context_data(self, **kwargs):
        context = super(SurveyView, self).get_context_data(**kwargs)
        
        nonce = self.kwargs['nonce']
        landing = get_object_or_404(Landing, nonce=nonce)
        context["landing"] = landing
        context["next"] = self.request.GET.get('next', '')
        

        return context    

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context['landing'].questionnaire:
            return generate_run(request, context['landing'].questionnaire.id, context=context)
        return self.render_to_response(context)
