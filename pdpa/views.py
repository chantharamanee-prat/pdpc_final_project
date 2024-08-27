from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, Http404, FileResponse, JsonResponse
from django.template import loader
from .models import MstPdpaCategory, MstPdpaQuestion, MstPdpaAnswer, TnxPdpaResult, TnxPdpaUser, MstPdpaSubCategory
import uuid
from django.contrib.auth.hashers import make_password
from .forms import CustomLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

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


def sign_up(request: HttpRequest):
    template = loader.get_template("sign_up.html")

    if request.method == 'POST':
        username = str(request.POST.get("username", ""))
        password = str(request.POST.get("password", ""))
        server_url = str(request.POST.get("server_url", ""))
        ssh_user = str(request.POST.get("ssh_user", ""))
        ssh_password = str(request.POST.get("ssh_password", ""))

        tnx_user = TnxPdpaUser(
            username = username,
            password = make_password(password),
            server_url = server_url,
            ssh_user = ssh_user,
            ssh_password = ssh_password,
        )

        tnx_user.save()

        return redirect("/sign-in")
    else:
        return HttpResponse(template.render({}, request))
    
def sign_in(request):
    template = loader.get_template("sign_in.html")

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')  # Redirect to a home page or dashboard
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    return HttpResponse(template.render({'form': form}, request))

@login_required
def pdpa_main(request):
    session_id = validate_session(request)

    template = loader.get_template("main.html")
    all_cat = MstPdpaCategory.objects.all().order_by("sequence").values()
    context = {
        'session_id': session_id,
        'all_cat': all_cat
    }
    return HttpResponse(template.render(context, request))

@login_required
def pdpa_question(request, id):
    session_id = validate_session(request)
    question_template = loader.get_template("question.html")
    question_id_get = request.GET.get("question_id")
    session = request.GET.get("session") 
    question = None

    all_question = MstPdpaQuestion.objects.select_related().filter(sub_category=id).order_by("sequence").values()

    if request.method == "POST":
        category_id = int(request.POST.get("category",""))
        question_id = int(request.POST.get("question", ""))
        answer_id = int(request.POST.get("answer", ""))
        text_measurement = request.POST.get("text_measurement")

        relate_question = MstPdpaQuestion.objects.get(pk = question_id)
        relate_answer = MstPdpaAnswer.objects.get(pk = answer_id)

        # save answer to DB
        tnx_answer = TnxPdpaResult(
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
            question = MstPdpaQuestion.objects.select_related().filter(sub_category=id).order_by("sequence").first()
        else:
            question = MstPdpaQuestion.objects.get(pk = question_id_get)
 
        if question is None:
            return redirect("/404.html")

        category = MstPdpaCategory.objects.get(pk=id)
        
        answer = question.answers.all()

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

@login_required
def pdpa_result(request,id):
    # session_id = validate_session(request)
    session_id = request.GET.get("session") 

    # clear old session
    clear_old_session(request)

    template = loader.get_template("result.html")
    all_result = TnxPdpaResult.objects.all().filter(session= session_id)
    
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

@login_required
def download_file(request, filename):
    # Construct the full file path
    file_path = os.path.join(settings.BASE_DIR, 'uploads', filename)
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise Http404("File does not exist.")
    
    # Return the file response
    response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def fetch_sub_cat(request, id):
    all_sub_cat = MstPdpaSubCategory.objects.select_related().filter(category=id).order_by("sequence").values()

    return JsonResponse(list(all_sub_cat), safe=False)

def sign_out(request):
    # sign user out
    logout(request)

    # Redirect to sign-in page
    return redirect('/sign-in')

def handler404(request, exception):
    template = loader.get_template("404.html")
    
    return HttpResponse(template.render({}, request))

