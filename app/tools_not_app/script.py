import os
import sys
import django
import pickle

# Add the parent directory of your Django project to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from choices.models import Module, Programme

def read_pickle(fname):
    with open(fname, 'rb') as f:
        data = pickle.load(f)
    return data


if __name__ == '__main__':

    # get fname from argv
    fname = sys.argv[1]

    print("Reading data from", fname)
    data = read_pickle(fname)

    # Get all programmes
    programmes = []
    for module in data:
        for programme in data[module]['programmes']:
            programmes.append(programme)

    programmes = list(set(programmes))


    print("Creating programmes")
    for programme in programmes:
        Programme.objects.get_or_create(title=programme)

    print("Creating modules")
    for module in data:
        try:
            m = Module.objects.get_or_create(
                code=module,
                title=data[module]['name'],
                semester=data[module]['semester'],
                level=data[module]['level'],
                credits=data[module]['credits'],
                #html=data[module]['html'],
                year=int(module[4])
            )[0]
            print(m, "created")


            for programme in data[module]['programmes']:
                p = Programme.objects.get(title=programme)
                m.in_programmes.add(p)
        except:
            continue
        

    print("Creating prerequisites")
    for module in data:
        m = Module.objects.get(code=module)
        for pre in data[module]['prerequisites']:
            try:
                p = Module.objects.get(code=pre)
                m.prerequisites.add(p)
            except:
                print("Could not find", pre)
    




        