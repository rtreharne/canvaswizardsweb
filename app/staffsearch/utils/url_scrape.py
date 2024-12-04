
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from itertools import chain
import json
import requests


# These are the urls for all directives in HLS
root_links = [
              #"https://www.liverpool.ac.uk/life-course-and-medical-sciences/",
              #"https://www.liverpool.ac.uk/population-health/",
              #"https://www.liverpool.ac.uk/infection-veterinary-and-ecological-sciences/",
              #"https://www.liverpool.ac.uk/systems-molecular-and-integrative-biology/staff/",
              #"https://www.liverpool.ac.uk/systems-molecular-and-integrative-biology/staff/life-sciences/",
              "https://www.liverpool.ac.uk/systems-molecular-and-integrative-biology/staff/life-sciences/",
               #"https://www.liverpool.ac.uk/systems-molecular-and-integrative-biology/staff/molecular-and-clinical-cancer-medicine/",
              # "https://www.liverpool.ac.uk/clinical-directorate/"
              ]

class URLScrape:
    def __init__(self, root_links):
        self.root_links = root_links
        self.staff = []

        for root in self.root_links:
            self.staff.append(self.get_staff_spider(root))

        self.all_staff = list(chain.from_iterable(self.staff))

    def get_soup_from_url(self, url):
        req = Request(url)
        html_page = urlopen(req)
        return BeautifulSoup(html_page)

    def get_links_from_soup(self, soup):
        new_links = []
        links = [x.get('href') for x in soup.findAll('a') if x.get('href')]
        return links

    def get_links_from_url(self, url, domain="https://liverpool.ac.uk"):
        try:
            links = self.get_links_from_soup(self.get_soup_from_url(url))
        except ValueError:
            links = self.get_links_from_soup(self.get_soup_from_url(domain + url))
        return links

    def get_staff_urls(self, root):
        urls = [x for x in self.get_links_from_url(root) if "/staff/" in x or "/people/" in x]
        return urls

    def get_staff_spider(self, root, save=[]):

        staff_urls = self.get_staff_urls(root)

        for url in staff_urls:

            if url not in save:

                save.append(url)

                if len(url.split("/staff/")[-1].split("-")) != 2:
                    try:
                        self.get_staff_spider(url, save=save)
                    except:
                        continue

        return save



class Staff:

    def __init__(self, url):
        self.url = url
        self.get_redirected_url(url)

        

        self.soup = self.get_soup_from_url(self.url)

        if self.check_if_staff():
            self.basic_info = self.get_basic_info()
            self.department, self.institute, self.faculty = self.get_department_institute_faculty()
            self.profile = self.get_profile_info()

            self.data = self.basic_info | self.profile
        
    
    def get_basic_info(self):
        script_tag = self.soup.find('script', type='application/ld+json')

        if script_tag:
            # Extract the JSON content as a string
            json_content = script_tag.string

            # Convert JSON string to a Python dictionary
            data_dict = json.loads(json_content)

            return data_dict
        else:
            return None
        
    def get_department_institute_faculty(self):

        # Find the parent div with class 'rb-people__header__card__content__column'
        parent_div = self.soup.find('div', class_='rb-people__header__card__content__column')

        # Get all child divs
        child_divs = parent_div.find_all('div') if parent_div else []

        # Extract the department: text immediately after first <br>, handling plain text or link
        department = None
        if len(child_divs) > 0:
            first_div = child_divs[0]
            br_tag = first_div.find('br')
            if br_tag:
                # Check if the text after <br> is in an <a> tag
                next_sibling = br_tag.find_next()
                if next_sibling and next_sibling.name == 'a':  # If it's an <a> tag
                    department = next_sibling.get_text(strip=True)
                elif next_sibling:  # If it's plain text
                    department = br_tag.next_sibling.strip()

        # Extract the institute (if present): text of the first <a> tag in the second <div>
        institute = None
        if len(child_divs) > 1:
            second_div = child_divs[1]
            first_a = second_div.find('a')
            if first_a:
                institute = first_a.get_text(strip=True)

        # Extract the faculty: text of the second <a> tag in the second <div>
        faculty = None
        if len(child_divs) > 1:
            second_div = child_divs[1]
            a_tags = second_div.find_all('a')
            if len(a_tags) > 1:
                faculty = a_tags[1].get_text(strip=True)

        return [department, institute, faculty]

    def get_redirected_url(self,url):
        try:

            if not url.startswith("https://www.liverpool.ac.uk"):
                url = f"https://www.liverpool.ac.uk{url}"
                
            # Make the request with redirection enabled (default behavior)
            response = requests.get(url, allow_redirects=True)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Save the final URL after redirection
                self.url = response.url  # Update the object's URL attribute to the redirected URL
                return BeautifulSoup(response.text)
            else:
                print(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error occurred while fetching URL: {url}. Error: {e}")
        return None

    def get_soup_from_url(self, url):
        try:
            # Make the request with redirection enabled (default behavior)
            response = requests.get(url, allow_redirects=True)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Save the final URL after redirection
                #self.url = response.url  # Update the object's URL attribute to the redirected URL
                return BeautifulSoup(response.text)
            else:
                print(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error occurred while fetching URL: {url}. Error: {e}")
        return None

    def check_if_staff(self):
        try:
            name_role = self.soup.find("section", {"class": "rb-people__header__card"})
            return name_role
        except:
            return None

    def get_profile_info(self):
        url_map = {
            "about": {"url_suffix": "", "search": ["section", {"class": "rb-content-flow"}]},
            "research": {"url_suffix": "research", "search": ["article", {"id": "research"}]},
            "publications": {"url_suffix": "publications", "search": ["article", {"id": "publications"}]},
            "teaching": {"url_suffix": "teaching", "search": ["article", {"id": "teaching"}]},
            "professional_activities": {"url_suffix": "professional",
                                        "search": ["article", {"id": "professional"}]},
        }

        data = {}   

        for key in url_map:
            try:
                url = self.append_slash(self.url)
                page = self.get_soup_from_url(url + url_map[key]["url_suffix"])

                tag, tag_marks = url_map[key]["search"]

                t = page.find(tag, tag_marks).text

                data[key] = t
            except:
                data[key] = None
        return data

    def append_slash(self, url):
        if str(url)[-1] != "/":
            return url + "/"
        else:
            return url
        
if __name__ == "__main__":
    urls = URLScrape(root_links)
    for x in urls.all_staff:
        print(x)



