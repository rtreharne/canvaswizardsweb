from celery import shared_task
#from .processes.url_scrape import URLScrape
from .utils import url_scrape
from .models import Profile, Department
from datetime import datetime
from django.utils.timezone import make_aware

def create_update(data):
    # check for existing record

    email = data.data["email"]
    try:
        email = email.replace("mailto:", "")
    except:
        pass


    try:
        record = Profile.objects.get(email=data.data["email"])
    except:
        record = False

    if record:
        print(f"Updating staff profile: {data.data['familyName']}, {data.data['givenName']}")
        update_string = ""

        for key in data.profile:
            if record.__dict__[key] != data.profile[key]:
                update_string += key + ", "
                record.__dict__["last_updated"] = make_aware(datetime.now())
                record.__dict__[key] = data.profile[key]
        return record

    else:

        

        print(f"Creating new staff profile: {data.data['familyName']}, {data.data['givenName']}")
        new_staff = Profile(
            first_name = data.data["givenName"],
            last_name = data.data["familyName"],
            role = data.data["jobTitle"],
            email = email,
            url = data.url,
            department = add_department(data),
            #last_updated = data.last_updated,
            about = data.profile["about"],
            research = data.profile["research"],
            publications = data.profile["publications"],
            teaching = data.profile["teaching"],
            professional_activities = data.profile["professional_activities"]
        )
        print(f"Saving profile for: {new_staff.last_name}, {new_staff.first_name}")
        new_staff.save()

def add_department(data):
    try:
        department = Department.objects.get(name=data.department)
        return department
    except:
        new_department = Department(name=data.department)
        new_department.save()
        return new_department


@shared_task
def get_profiles(url):
    print(f"Scraping staff URLs from root: {url}")
    urls = url_scrape.URLScrape([url])

    
    for x in urls.all_staff:

        result = url_scrape.Staff(x)

        try:
            print("Updating Staff ...")
            create_update(result)
        except:
            continue
    return None