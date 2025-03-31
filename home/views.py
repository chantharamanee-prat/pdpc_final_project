from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from .models import PdpaCategory, PdpaSubCategory, PdpaQuestion, PdpaAnswer, TnxPdpaResult, TnxResultDocument, UserProfile, TnxAuditLog
from django.http import HttpResponse, HttpRequest, Http404, FileResponse, JsonResponse
from django.template import loader
import uuid
from django.contrib.auth.hashers import make_password
from .forms import CustomLoginForm
from django.contrib import messages
from django.conf import settings
import os
from django.db.models import Subquery
import paramiko
from .forms import TnxResultDocumentForm
import csv
from django.urls import reverse
import json
import logging

# Get the logger
logger = logging.getLogger(__name__)

# Get the current User model (will be your new accounts.User)
User = get_user_model()

# utility function to create audit logs
def create_audit_log(request, user, action, content_object=None, changes=None, status_code=None):
    """
    Creates an audit log entry.
    """
    try:
        content_type = None
        object_id = None
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            object_id = content_object.pk

        TnxAuditLog.objects.create(
                user=user,
            action=action,
            content_type=content_type,
            object_id=object_id,
            changes=changes,
            ip_address=request.META.get('REMOTE_ADDR'),
            request_path=request.path,
            status_code=status_code,
            )
    except Exception as e:
        logger.error(f"Error creating audit log: {e}")

# Replace all instances of TnxPdpaUser with User in your views

def validate_user(request):
    pre_user_id = None
    try:
        pre_user_id = request.user.id
    except:
        print("An Exception occurred")

    return pre_user_id

def sign_in(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            create_audit_log(request, user, 'sign_in', status_code=200)
            return redirect('/')  # Redirect to user dashboard
        else:
            create_audit_log(request, None, 'sign_in_failed', status_code=401)
            return render(request, 'sign-in.html', {'form': form, 'error': 'Invalid username or password'})

    else:
        form = CustomLoginForm()
    return render(request, 'sign-in.html', {'form': form})


def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # Check if user exists
        if User.objects.filter(username=username).exists():
            create_audit_log(request, None, 'sign_up_failed_username_exists', status_code=400)
            return render(request, 'sign-up.html', {'error': 'Username already exists'})
        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )
        
        UserProfile.objects.create(
            user=user,
            ssh_server='default-server',
            ssh_port=22,
            ssh_user='default-ssh-user',
            ssh_password='default-ssh-password'
        )

        login(request, user)
        create_audit_log(request, user, 'sign_up_success', status_code=201)
        return redirect('/')

    return render(request, 'sign-up.html')
@login_required
def get_user_data(request):
    user = request.user
    response_data = {
        'username': user.username,
        'email': user.email,
        'ssh_server': user.ssh_server,
        'ssh_port': user.ssh_port,
        'ssh_user': user.ssh_user,
    }
    create_audit_log(request, user, 'get_user_data', status_code=200)
    return JsonResponse(response_data)
@login_required
def update_user_ssh(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        user = request.user
        old_data = {
            'ssh_server': user.ssh_server,
            'ssh_port': user.ssh_port,
            'ssh_user': user.ssh_user,
            'ssh_password': user.ssh_password,
        }

        user.ssh_server = data.get('ssh_server', user.ssh_server)
        user.ssh_port = data.get('ssh_port', user.ssh_port)
        user.ssh_user = data.get('ssh_user', user.ssh_user)
        user.ssh_password = data.get('ssh_password', user.ssh_password)
        user.save()

        new_data = {
            'ssh_server': user.ssh_server,
            'ssh_port': user.ssh_port,
            'ssh_user': user.ssh_user,
            'ssh_password': user.ssh_password,
        }

        changes = {}
        for key in old_data:
            if old_data[key] != new_data[key]:
                changes[key] = {'old': old_data[key], 'new': new_data[key]}

        create_audit_log(request, user, 'update_user_ssh', changes=changes, status_code=200)
        return JsonResponse({'status': 'success'})

    create_audit_log(request, request.user, 'update_user_ssh_failed', status_code=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# If you need to query users in any function:
def get_all_users(request):
    if request.user.is_superuser:
        users = User.objects.all().values('id', 'username', 'email')
        create_audit_log(request, request.user, 'get_all_users', status_code=200)
        return JsonResponse(list(users), safe=False)
    create_audit_log(request, request.user, 'get_all_users_unauthorized', status_code=403)
    return JsonResponse({'error': 'Unauthorized'}, status=403)
@login_required
def pdpa_main(request):
    template = loader.get_template("main.html")
    all_cat = PdpaCategory.objects.all().order_by("sequence").values()
    context = {
        'all_cat': all_cat
    }
    create_audit_log(request, request.user, 'pdpa_main', status_code=200)
    return HttpResponse(template.render(context, request))


@login_required
def pdpa_question(request, id):
    user_id = validate_user(request)
    question_template = loader.get_template("question.html")
    question_id_get = request.GET.get("question_id")
    question = None

    # Fetch all questions related to the subcategory
    all_question = PdpaQuestion.objects.select_related().filter(sub_category=id).order_by("sequence").values()

    if request.method == "POST":
        sub_category_id = int(request.POST.get("sub_category", ""))
        question_id = int(request.POST.get("question", ""))
        answer_id = int(request.POST.get("answer", ""))
        text_measurement = request.POST.get("text_measurement")

        relate_question = PdpaQuestion.objects.get(pk=question_id)
        relate_answer = PdpaAnswer.objects.get(pk=answer_id)
        user = request.user # Use the adjusted User model
        user_info = UserProfile.objects.get(user=user)

        doc = TnxResultDocumentForm(request.POST, request.FILES)

        script_result = None

        try:
            if relate_answer.script:
                script_result = run_ssh_command(
                    user_info.ssh_server, user_info.ssh_port, user_info.ssh_user, user_info.ssh_password, relate_answer.script
                )
                script_result = int(script_result)
        except:
            print("Some thing went wrong with ssh script")



        # Check if the answer already exists
        exist_answer = TnxPdpaResult.objects.filter(user=user, question=relate_question).first()

        if exist_answer:
            original_answer = exist_answer.answer
            exist_answer.answer = relate_answer
            exist_answer.script_result = script_result
            exist_answer.save()

            changes = {
                'answer': {'old': original_answer.id, 'new': relate_answer.id},
                'script_result': {'old': exist_answer.script_result, 'new': script_result},
            }
            content_object = exist_answer
            action = 'pdpa_question_answer_updated'
        else:
            # Save new answer
            tnx_answer = TnxPdpaResult(
                user=user,
                question=relate_question,
                answer=relate_answer,
                text_measurement=text_measurement,
                script_result=script_result
            )
            tnx_answer.save()

            changes = {
                'answer': relate_answer.id,
                'script_result': script_result,
            }
            content_object = tnx_answer
            action = 'pdpa_question_answered'

        if doc.is_valid():
            uploaded_file = doc.cleaned_data['file']
            new_doc = TnxResultDocument(result=content_object, file=uploaded_file)
            new_doc.save()
            action = action + '_with_document'

        create_audit_log(request, request.user, action, content_object=content_object, changes=changes, status_code=200)

        # Find next question after the current one
        counter = 0
        for a in all_question.iterator():
            counter += 1
            if int(a['id']) == question_id:
                break

        if counter < all_question.count():
            return redirect(f"/sub-cat/{sub_category_id}/question/?question_id={all_question[counter]['id']}")
        else:
            # return redirect(f"/sub-cat/{id}/result/")
            return redirect("/")

    else:
        # Get old results (answered questions)
        old_result = TnxPdpaResult.objects.select_related().filter(user=request.user, question__sub_category__id=id).values('question_id')

        # If all questions are answered, redirect to result
        if old_result.count() == all_question.count() and all_question.count() > 0:
            return redirect(f"/sub-cat/{id}/result/")

        # Find first unanswered question if user comes back and no question_id is provided
        if old_result and question_id_get is None:
            unanswered_question = PdpaQuestion.objects.filter(
                sub_category__id=id
            ).exclude(id__in=Subquery(old_result)).order_by("sequence").first()
            if unanswered_question:
                question_id_get = unanswered_question.id

        # If no unanswered question is found, get the first question in the sequence
        if question_id_get is None:
            unanswered_question = PdpaQuestion.objects.exclude(
                id__in=Subquery(TnxPdpaResult.objects.filter(user=request.user, question__sub_category__id=id).values('question_id'))
            ).filter(sub_category=id).order_by("sequence").first()

            # If no unanswered question is found, redirect to the result page
            if unanswered_question:
                question = unanswered_question
            else:
                create_audit_log(request, request.user, 'pdpa_question_redirect_to_result', content_object=PdpaSubCategory.objects.get(pk=id), status_code=302)
                return redirect(f"/sub-cat/{id}/result/")
        else:
            question = PdpaQuestion.objects.get(pk=question_id_get)

        if question is None:
            create_audit_log(request, request.user, 'pdpa_question_not_found', status_code=404)
            return redirect("/404.html")

        sub_category = PdpaSubCategory.objects.get(pk=id)
        answer = question.answers.all()

        display_question_number = f"0{question.sequence}" if question.sequence < 10 else question.sequence

        progress = [{"number": i + 1, "class": "active" if i + 1 == question.sequence else "inactive"} for i in range(all_question.count())]

        previous_q = PdpaQuestion.objects.select_related().filter(sub_category=id, sequence=question.sequence - 1).values()

        previous = previous_q[0] if previous_q else None

        # Check if there is an existing answer for the current question
        exist_answer = TnxPdpaResult.objects.filter(user=request.user, question=question).first()

        document_form = TnxResultDocumentForm()

        question_context = {
            'sub_category': sub_category,
            'question_sequence': question.sequence,
            'all_question': all_question.count(),
            'display_question_number': display_question_number,
            'question': question,
            'answer': answer,
            'previous_question': previous,
            'progress': progress,
            'exist_answer': exist_answer,
            'document_form': document_form,
        }
        create_audit_log(request, request.user, 'pdpa_question_page_view', content_object=question, status_code=200)
        return HttpResponse(question_template.render(question_context, request))


@login_required
def pdpa_result(request, id):
    user_id = validate_user(request)

    template = loader.get_template("result.html")
    all_question = PdpaQuestion.objects.select_related().filter(sub_category=id)
    all_result = TnxPdpaResult.objects.all().filter(user=request.user, question__sub_category__id=id)

    if not all_result or all_result.count() < all_question.count():
        create_audit_log(request, request.user, 'pdpa_result_redirect_to_question', content_object=PdpaSubCategory.objects.get(pk=id), status_code=302)
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
    create_audit_log(request, request.user, 'pdpa_result_page_view', content_object=PdpaSubCategory.objects.get(pk=id), status_code=200)
    return HttpResponse(template.render(context, request))


@login_required
def download_file(request, filename):
    # Construct the full file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)

    # Check if the file exists
    if not os.path.isfile(file_path):
        create_audit_log(request, request.user, 'download_file_not_found', status_code=404)
        raise Http404("File does not exist.")

    # Return the file response
    response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    create_audit_log(request, request.user, 'download_file', content_object=TnxResultDocument.objects.filter(file__icontains=filename).first(), status_code=200)
    return response


@login_required
def fetch_sub_cat(request, id):
    user_id = validate_user(request)
    all_sub_cat = PdpaSubCategory.objects.select_related().filter(category=id).order_by("sequence")

    completed_sub_categories = []

    for sub_category in all_sub_cat:
        # Get questions for the sub-category
        questions = PdpaQuestion.objects.filter(sub_category=sub_category.id)

        # Get count of questions
        total_questions = questions.count()

        # Get count of answered questions for the given user
        answered_questions_count = TnxPdpaResult.objects.filter(
            question__in=questions, user=request.user
        ).values('question').distinct().count()

        # Check if all questions are answered
        completed_sub_categories.append({
            'id': sub_category.id,
            'name': sub_category.name,
            'icon': sub_category.icon,
            'sequence': sub_category.sequence,
            'total_question': total_questions,
            'total_answer': answered_questions_count,
        })

    print(completed_sub_categories)

    create_audit_log(request, request.user, 'fetch_sub_cat', status_code=200)
    return JsonResponse(completed_sub_categories, safe=False)


@login_required
def pdpa_cat_result(request, id):
    user_id = validate_user(request)

    template = loader.get_template("result_cat.html")
    category = PdpaCategory.objects.get(id=id)
    all_result = TnxPdpaResult.objects.all().filter(user=request.user, question__sub_category__category__id=id)

    sum_score = 0
    all_result_list = []

    for res in all_result:
        sum_score += res.answer.score

        sub_cate_found = False
        for sub_cate in all_result_list:
            if sub_cate['sub_cate']['name'] == res.question.sub_category.name:
                # If subcategory is found, append the result to its res_list
                sub_cate['sub_cate']['res_list'].append(res)
                sub_cate_found = True
                break

        # If subcategory is not found, create a new subcategory
        if not sub_cate_found:
            new_sub_cate = {
                "sub_cate": {
                    "name": res.question.sub_category.name,
                    "res_list": [res]
                }
            }
            all_result_list.append(new_sub_cate)

    avg_score = 0
    if all_result.count() > 0:
        avg_score = sum_score / all_result.count()

    # print(list(all_result.values("question" , "answer")))
    print(all_result_list)

    context = {
        'category': category,
        'response': all_result,
        'avg_score': avg_score,
        "all_result_list": all_result_list
    }
    create_audit_log(request, request.user, 'pdpa_cat_result_page_view', content_object=category, status_code=200)
    return HttpResponse(template.render(context, request))


@login_required
def export_pdpa_report_csv(request, user_id):
    # Get the user object
    user = User.objects.get(id=user_id)

    # Create the HttpResponse object with CSV content type
    response = HttpResponse(content_type='text/csv')

    # Add a header to force the download of the file
    response['Content-Disposition'] = f'attachment; filename="pdpa_report_{user}.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['Category', 'Subcategory', 'Question', 'Answer', 'Score', 'Result Text', 'Attachment URL'])

    # Query results for the user
    results = TnxPdpaResult.objects.filter(user=user)

    # Write data rows
    for result in results:
        # Get the associated document, if any
        document = TnxResultDocument.objects.filter(result=result).first()
        document_url = ""
        # If a document exists, generate the download URL; otherwise, leave blank
        if document is not None:
            document_url = f"http://127.0.0.1:8000/file/{document.file.name}"

        # Write the result row with the document URL
        writer.writerow([
            result.get_category_name(),  # Category
            result.get_sub_category_name(),  # Subcategory
            result.question.question,  # Question
            result.answer.answer,  # Answer
            result.answer.score,  # Score
            result.answer.result_text,  # Result Text
            document_url  # Document URL (or 'No document')
        ])
    create_audit_log(request, request.user, 'export_pdpa_report_csv', status_code=200)
    # Return the response to the user, triggering the download
    return response
def sign_out(request):
    # sign user out
    user = request.user
    logout(request)
    create_audit_log(request, user, 'sign_out', status_code=200)

    # Redirect to sign-in page
    return redirect('/sign-in')

def sign_out_admin(request):
    # sign user out
    user = request.user
    logout(request)
    create_audit_log(request, user, 'sign_out_admin', status_code=200)

    # Redirect to admin page
    return redirect('/admin')


def not_found(request):
     template = loader.get_template("404.html")
     create_audit_log(request, None, 'not_found_page_view', status_code=404)
     return HttpResponse(template.render())


def handler404(request, exception):
    template = loader.get_template("404.html")
    create_audit_log(request, None, 'handler404', status_code=404)
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
