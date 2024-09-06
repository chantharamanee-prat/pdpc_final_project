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
from django.db.models import Subquery
import paramiko


def validate_user(request):
    pre_user_id = None
    try :
        pre_user_id = request.user.id
    except: 
        print("An Exception occured")
        
    print(pre_user_id)

    return pre_user_id

def sign_up(request: HttpRequest):
    template = loader.get_template("sign_up.html")

    if request.method == 'POST':

        username = str(request.POST.get("username", ""))
        password = str(request.POST.get("password", ""))
        ssh_server = str(request.POST.get("ssh_server", ""))
        ssh_port = str(request.POST.get("ssh_port", ""))
        ssh_user = str(request.POST.get("ssh_user", ""))
        ssh_password = str(request.POST.get("ssh_password", ""))

        existing_user = TnxPdpaUser.objects.filter(username = username)

        if existing_user:
           return HttpResponse(template.render({
               "username_already_exist": "Username already exist."
           }, request))

        tnx_user = TnxPdpaUser(
            username = username,
            password = make_password(password),
            ssh_server = ssh_server,
            ssh_port = ssh_port,
            ssh_user = ssh_user,
            ssh_password = ssh_password,
        )

        tnx_user.save()

        return redirect("/sign-in")
    else:
        return HttpResponse(template.render({}, request))
    
def sign_in(request):
    template = loader.get_template("sign_in.html")
    session = validate_user(request)

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
    elif session is not None:
        return redirect("/")
    else:  
        form = CustomLoginForm()


    return HttpResponse(template.render({'form': form}, request))

@login_required
def pdpa_main(request):

    template = loader.get_template("main.html")
    all_cat = MstPdpaCategory.objects.all().order_by("sequence").values()
    context = {
        'all_cat': all_cat
    }
    return HttpResponse(template.render(context, request))

@login_required
def pdpa_question(request, id):
    user_id = validate_user(request)
    question_template = loader.get_template("question.html")
    question_id_get = request.GET.get("question_id")
    question = None

    all_question = MstPdpaQuestion.objects.select_related().filter(sub_category=id).order_by("sequence").values()

    if request.method == "POST":
        sub_category_id = int(request.POST.get("sub_category",""))
        question_id = int(request.POST.get("question", ""))
        answer_id = int(request.POST.get("answer", ""))
        text_measurement = request.POST.get("text_measurement")

        relate_question = MstPdpaQuestion.objects.get(pk = question_id)
        relate_answer = MstPdpaAnswer.objects.get(pk = answer_id)
        user = TnxPdpaUser.objects.get(pk = user_id)

        script_result = None

        if relate_answer.script:
            script_result = run_ssh_command(user.ssh_server, user.ssh_port, user.ssh_user, user.ssh_password, relate_answer.script)
            print(script_result)
            script_result = int(script_result)

        # check exist answer
        exist_answer = TnxPdpaResult.objects.filter(user = user_id, question = relate_question,).first()

        if exist_answer:
            exist_answer.answer = relate_answer
            exist_answer.script_result = script_result

            exist_answer.save()
        else:
            # save answer to DB
            tnx_answer = TnxPdpaResult(
                user = user, 
                question = relate_question,
                answer = relate_answer,
                text_measurement = text_measurement,
                script_result = script_result
            )
            tnx_answer.save()

        # find next question
        counter = 0
        for a in all_question.iterator():
            if int(a['id']) == question_id:
                break
            counter +=1

        if counter < all_question.count() -1:
            return redirect(f"/sub-cat/{sub_category_id}/question/?question_id={all_question[counter + 1]['id']}")
        
        else:
            return redirect(f"/sub-cat/{id}/result/")


    else:
        old_result = TnxPdpaResult.objects.select_related().filter(user = user_id, question__sub_category__id = id).values('question_id')

        # redirect if contain old result
        if old_result.count() == all_question.count() and all_question.count() > 0:
            return redirect(f"/sub-cat/{id}/result/")
        elif old_result and question_id_get is None:
            unanswered_question = MstPdpaQuestion.objects.exclude(id__in=Subquery(old_result)).first()
            if unanswered_question:
                question_id_get = unanswered_question.id
    
        if question_id_get is None:
            question = MstPdpaQuestion.objects.select_related().filter(sub_category=id).order_by("sequence").first()
        else:
            question = MstPdpaQuestion.objects.get(pk = question_id_get)
            
 
        if question is None:
            return redirect("/404.html")

        sub_category = MstPdpaSubCategory.objects.get(pk=id)
        
        answer = question.answers.all()

        display_question_number = f"0{question.sequence}" if question.sequence < 10 else question.sequence
        
        progress = []

        for i in range(0, all_question.count()):
            progress.append({
                "number": i + 1,
                "class": "active" if i + 1 == question.sequence else "inactive"
            })

        previous_q = MstPdpaQuestion.objects.select_related().filter(sub_category=id, sequence=question.sequence - 1).values()

        previous = None

        if previous_q:
            previous = previous_q[0]
        
        # check exist answer
        exist_answer = TnxPdpaResult.objects.filter(user = user_id, question = question).first()

        question_context = {
            'sub_category': sub_category,
            'question_sequence': question.sequence,
            'all_question': all_question.count(),
            'display_question_number': display_question_number,
            'question': question,
            'answer': answer,
            'previous_question': previous,
            'progress': progress,
            'exist_answer': exist_answer
        }

        return HttpResponse(question_template.render(question_context, request))

@login_required
def pdpa_result(request,id):
    user_id = validate_user(request)

    template = loader.get_template("result.html")
    all_question = MstPdpaQuestion.objects.select_related().filter(sub_category=id)
    all_result = TnxPdpaResult.objects.all().filter(user = user_id, question__sub_category__id = id)

    if not all_result or all_result.count() < all_question.count():
        return redirect(f"/sub-cat/{id}/question/")
    
    sum_score = 0
    for res in all_result:
        print(res.answer.score)
        sum_score += res.answer.score

    avg_score = sum_score / all_result.count()

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
    user_id = validate_user(request)
    all_sub_cat = MstPdpaSubCategory.objects.select_related().filter(category=id).order_by("sequence")

    completed_sub_categories = []

    for sub_category in all_sub_cat:
        # Get questions for the sub-category
        questions = MstPdpaQuestion.objects.filter(sub_category=sub_category.id)

        # Get count of questions
        total_questions = questions.count()

        # Get count of answered questions for the given user
        answered_questions_count = TnxPdpaResult.objects.filter(
            question__in=questions, user_id=user_id
        ).values('question').distinct().count()

        # Check if all questions are answered
        completed_sub_categories.append({
            'id': sub_category.id,
            'name': sub_category.name,
            'icon': sub_category.icon,
            'sequence': sub_category.sequence,
            'total_question': total_questions,
            'total_answer' :answered_questions_count,
        })

    print(completed_sub_categories)

    return JsonResponse(completed_sub_categories, safe=False)

def sign_out(request):
    # sign user out
    logout(request)

    # Redirect to sign-in page
    return redirect('/sign-in')

def sign_out_admin(request):
    # sign user out
    logout(request)

    # Redirect to admin page
    return redirect('/admin')

def not_found (request):
     template = loader.get_template("404.html")
     return HttpResponse(template.render())

def handler404(request, exception):
    template = loader.get_template("404.html")
    
    return HttpResponse(template.render({}, request))


def run_ssh_command(hostname, port, username, password, command):
    try:
        # Create an SSH client instance
        ssh = paramiko.SSHClient()
        
        # Automatically add the server's host key (dangerous in production)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the server
        ssh.connect(hostname, port, username, password)
        
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Print command output and errors
        output = stdout.read().decode()
        print("Output:")
        print(output)
        
        print("Errors:")
        print(stderr.read().decode())

        return output
        
    finally:
        # Close the SSH connection
        ssh.close()

