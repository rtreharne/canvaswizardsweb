from django.shortcuts import render
from staffsearch.models import Institute, Profile, Department, Search
from staffsearch.forms import SearchForm
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from staffsearch.models import Profile, Department, Keyword, Banner

def search_profiles(profiles, vector, keywords):

    search_record = Search(
        keywords = keywords
    )

    search_record.save()
    

    tags = (" ").join([x for x in keywords.split(" ") if "#" in x])
    keywords = (" ").join([x for x in keywords.split(" ") if "#" not in x])

    print("tags: ", tags, "keywords: ", keywords)

    if len(tags.strip()) > 0:
        print("I have tags!", len(tags))
        tag_query = SearchQuery(tags)
        if len(keywords) == 0:
            keywords_query=tag_query
        else:
            keywords_query = SearchQuery(keywords)
        search = profiles.annotate(rank=SearchRank(vector, tag_query)).filter(rank__gte=0.01).order_by('-rank')
        search = search.annotate(rank=SearchRank(vector, keywords_query)).filter(rank__gte=0.01).order_by('-rank')
    else:
        print("No tags")
        query = SearchQuery(keywords)
        search = profiles.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.01).order_by('-rank')
    return search

def get_banner():
    banner = Banner.objects.order_by('?').first()
    return banner.url


def index(request):

    context = {"banner": get_banner()}

    vector = SearchVector("last_name",
                          "first_name",
                          "role",
                          "about",
                          "research",
                          "teaching",
                          "publications",
                          "professional_activities",
                          "additional_info")

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():

            keywords = form.cleaned_data["keyword"]
            print(keywords)

            department = Department.objects.filter(name=form.cleaned_data["department"])



            if len(department) > 0:
                profiles = Profile.objects.filter(department=department[0], visible=True)
            else:
                profiles = Profile.objects.filter(visible=True)

            search = search_profiles(profiles, vector, keywords)

            #profiles.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.01).order_by('-rank')

            #new_query = SearchQuery("health technology")

            #search = search.annotate(rank=SearchRank(vector, new_query)).filter(rank__gte=0.01).order_by('-rank')



            if len(search) > 0:
                max_value = max([x.rank for x in search])
                for item in search:
                    score = item.rank*100/max_value
                    item.rank = score



            context["results"] = search
            context["keyword"] = form.cleaned_data["keyword"]
            context["form"] = form
            return render(request, "index.html", context)
    else:
        form = SearchForm

    keywords = request.GET.get('keyword', None)

    if keywords:

        query = SearchQuery(keywords)
        profiles = Profile.objects.filter(visible=True)

        search = search_profiles(profiles, vector, keywords)


        if len(search) > 0:
            max_value = max([x.rank for x in search])
            for item in search:
                score = item.rank * 100 / max_value
                item.rank = score

        context["results"] = search
        context["keyword"] = keyword
        context["form"] = form

        return render(request, "index.html", context)

    context["form"] = form

    return render(request, "index.html", context)

def directory(request):
    # get institutes
    #institutes = Institute.objects.all().order_by('name')
    departments = Department.objects.all().order_by('name')
    profiles = Profile.objects.filter(visible=True).order_by('last_name')

    context = {#'institutes': institutes,
               'departments': departments,
               'profiles': profiles,
               'banner': get_banner()}

    return render(request, "directory.html", context)

def keyword_list(request):
    # get keywords
    keywords = Keyword.objects.filter(visible=True, frequency__gte=1).order_by('-frequency')

    context = {'keywords': keywords,
               'banner': get_banner()}


    return render(request, "keywords.html", context)