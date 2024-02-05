from django.shortcuts import render
from .forms import HumanForm, IntegerInputForm
from .models import Human, Question, Answer, Resource
from django.http import HttpResponseRedirect, HttpResponse
from .utils import foundation
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from allauth.socialaccount.models import SocialAccount

def github_callback(request):
    # Handle the OAuth callback here...

    # Then return a HTML page with some JavaScript code to close the popup window and refresh the original page
    return HttpResponse("""
        <html><body>
        <script type="text/javascript">
            window.opener.location.reload(true);  // refresh the original page
            window.close();  // close the popup window
        </script>
        </body></html>
    """)

def logout_view(request):
    # Log out the user
    logout(request)

    # Get the next URL from the 'next' parameter, or default to the homepage
    next_url = request.GET.get('next', '/foundation2')

    # Redirect to the next URL
    return redirect(next_url)

def get_leaderboard_question(context):
    # Get all answers for this question that are correct. Order by most recently submitted.
    question_answers = Answer.objects.filter(question=context["question"], correct=True).order_by('-score')

    # Get the top 10 scores for problem.
    question_top_answers = question_answers[:10]

    question_leaderboard = []

    for i, x in enumerate(question_top_answers):
        if x.human.anonymous_user:
            human = "AnonUser"+str(x.human.id)
        else:
            human = x.human.slug
        
        question_leaderboard.append(
            {
                "rank": i+1,
                "human": human,
                "score": x.score
            }
        )

    context["question_leaderboard"] = question_leaderboard

    return context

def get_leaderboard_overall(context):
    humans = Human.objects.all()
    score_dict = {}

    for human in humans:
        answers = Answer.objects.filter(human=human, correct=True)
        score = sum([x.score for x in answers])
        if score > 0:
            if human.anonymous_user:
                score_dict["AnonUser"+str(human.id)] = score
            else:
                score_dict
    
    sorted_score_dict = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
    top_scores = sorted_score_dict[:10]

    overall_leaderboard = [
        {
            "rank": i+1,
            "human": x[0],
            "score": x[1]
        } for i, x in enumerate(top_scores)]
    
    context["overall_leaderboard"] = overall_leaderboard

    return context

def get_rank(human, question=None):

    humans = Human.objects.all()
    score_dict = {}

    if question:
        if len(Answer.objects.filter(human=human, correct=True, question=question)) == 0:
            return {"rank": "--", "score": "--", "mistakes": "--"}
        else:
            incorrect_answers = Answer.objects.filter(human=human, correct=False, question=question)
    else:
        if len(Answer.objects.filter(human=human, correct=True)) == 0:
            return {"rank": "--", "score": "--", "mistakes": "--"}
        else:
            incorrect_answers = Answer.objects.filter(human=human, correct=False)
    
    

    for h in humans:
        if question:
            answers = Answer.objects.filter(human=h, correct=True, question=question)
            
        else:
            answers = Answer.objects.filter(human=h, correct=True)
        score = sum([x.score for x in answers])

        if score > 0:
            score_dict[h.slug] = score
    

    sorted_score_dict = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

    # determine rank of human
    rank = 0

    for i, x in enumerate(sorted_score_dict):
        rank += 1
        if x[0] == human.slug:
            break  
    return {
        "rank": rank,
        "score": score_dict[human.slug],
        "mistakes": len(incorrect_answers)
    }


def start(request):

    # Get logged in user
    try:
        user = request.user
    
    except AttributeError:
        user = None

    human_form = None

    if request.method == 'POST':
            human_form = HumanForm(request.POST, user=user)
            if human_form.is_valid():
                print("form is valid")
                human = human_form.save()
                context = {"human_form": None}
                return render(request, 'foundation2/start.html', context)
            else:
                print("form is not valid")
                context = {"human_form": human_form, "errors": human_form.errors}
                return render(request, 'foundation2/start.html', context)

    #if user is not anonymous user
    if user is not None and user.is_authenticated:
        try:
            human = Human.objects.get(user=user)
 
        except:
            human = None
            human_form = HumanForm(initial={
                "user": user,
                "last_name": user.last_name, 
                "first_name": user.first_name
            })
            


    context = {"human_form": human_form}


    
    return render(request, 'foundation2/start.html', context)

@login_required(login_url='/foundation2')
def question(request, question_id=None):

    context = {}
    social_account = SocialAccount.objects.filter(user=request.user).first()
    context["social_account"] = social_account

    
    try:
        human = Human.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/foundation2')
    context["human"] = human
    answer_form = IntegerInputForm()
    context["answer_form"] = answer_form
    context["stats"] = get_rank(human)
    

    
    if question_id:
        question = Question.objects.get(id=question_id)
        answers = Answer.objects.filter(human=human, question=question, correct=True)
        resources = Resource.objects.filter(question=question)

        if len(answers) > 0:
            context["complete"] = True
            context["question"] = question
            context["answer"] = answers[0]
            context = get_leaderboard_question(context)
            context = get_leaderboard_overall(context)
            context["stats_part"] = get_rank(human, question=context["question"])
            context["resources"] = resources
            return render(request, 'foundation2/question.html', context)
    


    # Get all answers for this human that are correct. Order by most recently submitted.
    answers = Answer.objects.filter(human=human).order_by('-time_submitted')

    # If there are no correct answers, then this is the first question.
    correct_answers = Answer.objects.filter(human=human, correct=True).order_by('-time_submitted')
    if len(correct_answers) == 0:
        question = Question.objects.first()
    else:
        # Get the most recent answer.
        answer = correct_answers[0]
        # Get the next question.
        question = answer.question.next

    context["question"] = question
    context["stats_part"] = get_rank(human, question=context["question"])
    context = get_leaderboard_question(context)
    context = get_leaderboard_overall(context)


    if request.method == 'POST':
        answer_form = IntegerInputForm(request.POST)
        if answer_form.is_valid():
            incorrect_answers = Answer.objects.filter(human=human, correct=False, question=question)
            # If datetime now - datetime of most recent answer is less than 3 minutes, then return error.
            if incorrect_answers and len(incorrect_answers) > 0:
                if datetime.datetime.now(datetime.timezone.utc) - answers[0].time_submitted < datetime.timedelta(minutes=1):
                    context["message"] = f"Sorry, you must wait 1 minute before answering this question again."
                    return render(request, 'foundation2/question.html', context)


            answer = Answer()
            answer.human = human
            answer.question = question
            
            answer.submitted = answer_form.cleaned_data['number']
            answer.save()

            # Get the function from the question.
            function_name = question.function_name
            function = getattr(foundation, function_name)

            # Run the function with the human as the argument.
            result = function(human, check=answer.submitted)

            # If the result is True, then the answer is correct.
            if result == True:
                answer.correct = True

                # Count correct answers to this question.
                correct_answers = Answer.objects.filter(question=question, correct=True)
                if len(correct_answers) < 100:
                    score = 100 - len(correct_answers)
                answer.score = score
                answer.save()

                context = get_leaderboard_question(context)
                context = get_leaderboard_overall(context)

                context["success"] = True

            else:
                answer.correct = False
                answer.save()

                context["message"] = f"Sorry, that is not the correct answer. Please wait 1 minute before trying again. "

                # Look for answers with the same submitted value.
                matching_answers = Answer.objects.filter(question=question, correct=True, submitted=answer.submitted)
                if len(matching_answers) > 0:

                    context["message"] += f"Curiously, the human <strong>{matching_answers[0].human.slug}</strong> submitted the same answer and got it correct. What are the odds, eh?"

            render(request, 'foundation2/question.html', context)

    # If there is no next question, then this is the last question.
    if question is None:
        previous_question = Answer.objects.filter(human=human).order_by('-time_submitted')[0].question
        context["previous_question"] = previous_question
        # TODO: Create Summary Page
        return render(request, 'foundation2/finish.html', context)
    
    context["question"] = question
    context["resources"] = Resource.objects.filter(question=question).order_by('name')
    
    return render(request, 'foundation2/question.html', context)

def input(request, question_id):

    human = Human.objects.get(user=request.user)
    question = Question.objects.get(id=question_id)
    function_name = question.function_name

    # get function from function_name
    function = getattr(foundation, function_name)

    html = function(human)
    

    return HttpResponse(html, content_type='text/plain')
    

    

    
