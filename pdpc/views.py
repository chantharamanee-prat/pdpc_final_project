from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import MstPdpcCategory, MstPdpcQuestion, MstPdpcAnswer, TnxPdpcResult
import uuid

def validate_session(request):
    pre_session_id = str(uuid.uuid4())
    if 'session_id' in request.session:
        session_id = request.session['session_id']
        if session_id is None:
            request.session['session_id'] = pre_session_id
        else:
            return session_id
    else:
        request.session['session_id'] = pre_session_id

    return pre_session_id

def clear_old_session(request):
    if 'session_id' in request.session:
        request.session['session_id'] = None
    

def pdpc_main(request):
    session_id = validate_session(request)

    template = loader.get_template("main.html")
    all_cat = MstPdpcCategory.objects.all().order_by("sequence").values()
    context = {
        'session_id': session_id,
        'all_cat': all_cat
    }
    return HttpResponse(template.render(context, request))

def pdpc_question(request, id):
    session_id = validate_session(request)
    question_template = loader.get_template("question.html")
    question_id_get = request.GET.get("question_id")
    session = request.GET.get("session") 
    question = None

    all_question = MstPdpcQuestion.objects.select_related().filter(category=id).order_by("sequence").values()

    if request.method == "POST":
        category_id = int(request.POST.get("category",""))
        question_id = int(request.POST.get("question", ""))
        answer_id = int(request.POST.get("answer", ""))
        text_measurement = request.POST.get("text_measurement")

        relate_question = MstPdpcQuestion.objects.get(pk = question_id)
        relate_answer = MstPdpcAnswer.objects.get(pk = answer_id)

        # save answer to DB
        tnx_answer = TnxPdpcResult(
            session = session_id, 
            question = relate_question,
            answer = relate_answer,
            text_measurement = text_measurement
        )

        tnx_answer.save()

        # find next question
        counter = 0
        for a in all_question.iterator():
            print(f'id = {a["id"]}')
            print(f"counter = {counter}")
            if int(a['id']) == question_id:
                break
            counter +=1

        if counter < all_question.count() -1:
            return redirect(f"/cat/{category_id}/question/?question_id={all_question[counter + 1]['id']}&session={session_id}")
        
        else:
            return redirect(f"/cat/{id}/result/?session={session_id}")



    else:
        if question_id_get is None:
            question = MstPdpcQuestion.objects.select_related().filter(category=id).order_by("sequence").first()
        else:
            question = MstPdpcQuestion.objects.get(pk = question_id_get)
 
        if question is None:
            return redirect("/404.html")

        category = MstPdpcCategory.objects.get(pk=id)
        
        answer = MstPdpcAnswer.objects.all().order_by("sequence").values()

        display_question_number = f"0{question.sequence}" if question.sequence < 10 else question.sequence
        
        progress = []

        for i in range(0,all_question.count()):
            progress.append({
                "number": i + 1,
                "class": "active" if i + 1 == question.sequence else "inactive"
            })

        question_context = {
            'category': category,
            'question_sequence': question.sequence,
            'all_question': all_question.count(),
            'display_question_number': display_question_number,
            'question': question,
            'answer': answer,
            'is_first': question.sequence == 1,
            'progress': progress,
            'session': session,
        }

        return HttpResponse(question_template.render(question_context, request))

def pdpc_result(request,id):
    # session_id = validate_session(request)
    session_id = request.GET.get("session") 

    # clear old session
    clear_old_session(request)

    template = loader.get_template("result.html")
    all_result = TnxPdpcResult.objects.all().filter(session= session_id)
    
    sum_score = 0
    for res in all_result:
        print(res.answer.score)
        sum_score += res.answer.score

    avg_score = sum_score/ all_result.count()

    

    context = {
        'first_res': all_result.first(),
        'response': all_result,
        'avg_score': avg_score
    }
    return HttpResponse(template.render(context, request))

def not_found(request):
    session_id = validate_session(request)
    template = loader.get_template("404.html")

    return HttpResponse(template.render())
