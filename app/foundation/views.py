from django.shortcuts import render
from .forms import HumanForm, IntegerInputForm, SlugForm
from .models import Human, Question, Answer, Resource
from django.http import HttpResponseRedirect, HttpResponse
from .utils import foundation
import datetime
from django.core.exceptions import ObjectDoesNotExist

def get_leaderboard_question(context):
    # Get all answers for this question that are correct. Order by most recently submitted.
    question_answers = Answer.objects.filter(question=context["question"], correct=True).order_by('-score')

    # Get the top 10 scores for problem.
    question_top_answers = question_answers[:10]

    question_leaderboard = [
        {
            "rank": i+1,
            "human": x.human.slug,
            "score": x.score
        } for i, x in enumerate(question_top_answers)]

    context["question_leaderboard"] = question_leaderboard

    return context

def get_leaderboard_overall(context):
    humans = Human.objects.all()
    score_dict = {}

    for human in humans:
        answers = Answer.objects.filter(human=human, correct=True)
        score = sum([x.score for x in answers])
        if score > 0:
            score_dict[human.slug] = score
    
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

    context = {}

    if request.method == 'POST':
        # if slug form submitted
        if "slug" in request.POST:
            slug_form = SlugForm(request.POST)
            if slug_form.is_valid():
                slug = slug_form.cleaned_data['slug']
                return HttpResponseRedirect(f'{slug}')
            else:
                context["slug_form"] = slug_form
                context["form"] = HumanForm()
                return render(request, 'foundation/start.html', context)
        
        # if human form submitted
        form = HumanForm(request.POST)
        if form.is_valid():
            human = form.save()
            return HttpResponseRedirect(f'{human.slug}')
        else:
            context["form"] = form
            context["slug_form"] = SlugForm()
            return render(request, 'foundation/start.html', context)
        
    context["form"] = HumanForm()
    context["slug_form"] = SlugForm()
    
    return render(request, 'foundation/start.html', context)

def question(request, slug, question_id=None):

    context = {}
    try:
        human = Human.objects.get(slug=slug)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/foundation')
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
            return render(request, 'foundation/question.html', context)
    


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
                    return render(request, 'foundation/question.html', context)


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

                    context["message"] += f"Curiously, another human submitted the same answer and got it correct. What are the odds, eh?"

            render(request, 'foundation/question.html', context)

    # If there is no next question, then this is the last question.
    if question is None:
        previous_question = Answer.objects.filter(human=human).order_by('-time_submitted')[0].question
        context["previous_question"] = previous_question
        # TODO: Create Summary Page
        return render(request, 'foundation/finish.html', context)
    
    context["question"] = question
    context["resources"] = Resource.objects.filter(question=question).order_by('name')
    
    return render(request, 'foundation/question.html', context)

def input(request, slug, question_id):

    human = Human.objects.get(slug=slug)
    question = Question.objects.get(id=question_id)
    function_name = question.function_name

    # get function from function_name
    function = getattr(foundation, function_name)

    html = function(human)
    

    return HttpResponse(html, content_type='text/plain')
    

    

    
