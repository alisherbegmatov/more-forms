from flask import Flask, request, render_template
from PIL import Image, ImageFilter
from pprint import PrettyPrinter
import json
import os
import random
import requests

app = Flask(__name__)

@app.route('/')
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template('home.html')

################################################################################
# COMPLIMENTS ROUTES
################################################################################

list_of_compliments = [
    'awesome',
    'beatific',
    'blithesome',
    'conscientious',
    'coruscant',
    'erudite',
    'exquisite',
    'fabulous',
    'fantastic',
    'gorgeous',
    'indubitable',
    'ineffable',
    'magnificent',
    'outstanding',
    'propitioius',
    'remarkable',
    'spectacular',
    'splendiferous',
    'stupendous',
    'super',
    'upbeat',
    'wondrous',
    'zoetic'
]

# TODO: Enter your context variables here.  
@app.route('/compliments')
def compliments():
    """Shows the user a form to get compliments."""
    return render_template('compliments_form.html')

@app.route('/compliments_results')
def compliments_results():
    """Show the user some compliments."""
    name = request.args.get('users_name')
    compliments = request.args.get('wants_compliments')
    num = int(request.args.get('num_compliments'))
    
    listCompliments = []
    if compliments == 'yes':
        if num > 0:
            i = 0 
            listCompliments = random.sample(list_of_compliments, k=num)

    context = {
        'name' : name,
        'compliments' : compliments,
        'num' : num,
        'listCompliments' : listCompliments
    }

    return render_template('compliments_results.html', **context)


################################################################################
# ANIMAL FACTS ROUTE
################################################################################

animal_to_fact = {
    'koala': 'Koala fingerprints are so close to humans\' that they could taint crime scenes.',
    'parrot': 'Parrots will selflessly help each other out.',
    'mantis shrimp': 'The mantis shrimp has the world\'s fastest punch.',
    'lion': 'Female lions do 90 percent of the hunting.',
    'narwhal': 'Narwhal tusks are really an "inside out" tooth.',
    'raccoon': 'they are named for their unique hands.',
    'sabrina': 'The best cat out there.'
}

@app.route('/animal_facts')
def animal_facts():
    """Show a form to choose an animal and receive facts."""

    animal_facts = []
    selected_animals = request.args.getlist('animal')

    if selected_animals != []:
        selected_animals = selected_animals[0]
    else:
        selected_animals = "None"

    context = {
        'animal_to_fact' : animal_to_fact,
        'selected_animals' : selected_animals
    }
    return render_template('animal_facts.html', **context)

################################################################################
# IMAGE FILTER ROUTE
################################################################################

filter_types_dict = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR,
    'detail': ImageFilter.DETAIL,
    'edge enhance': ImageFilter.EDGE_ENHANCE,
    'emboss': ImageFilter.EMBOSS,
    'sharpen': ImageFilter.SHARPEN,
    'smooth': ImageFilter.SMOOTH
}

def save_image(image, filter_type):
    """Save the image, then return the full file path of the saved image."""
    # Append the filter type at the beginning (in case the user wants to 
    # apply multiple filters to 1 image, there won't be a name conflict)
    new_file_name = f"{filter_type}-{image.filename}"
    image.filename = new_file_name

    # Construct full file path
    file_path = os.path.join(app.root_path, 'static/images', new_file_name)
    
    # Save the image
    image.save(file_path)

    return file_path


def apply_filter(file_path, filter_name):
    """Apply a Pillow filter to a saved image."""
    i = Image.open(file_path)
    i.thumbnail((500, 500))

    if filter_name == 'grayscale':
        i = ImageOps.grayscale(i)
    elif filter_name == 'mirror':
        i = ImageOps.mirror(i)
    else:
        i = i.filter(filter_types_dict.get(filter_name))

    i.save(file_path)

    

@app.route('/image_filter', methods=['GET', 'POST'])
def image_filter():
    """Filter an image uploaded by the user, using the Pillow library."""

    if request.method == 'POST':
        
        filter_type = request.form.get('filter_type')
        
        # Get the image file submitted by the user
        image = request.files.get('users_image')

        file_path = save_image(image, filter_type)
        apply_filter(file_path, filter_type)
        image_url = f'/static/images/{image.filename}'

        context = {
            'filter_types' : filter_types_dict.keys(),
            'image_url' : image_url
        }

        return render_template('image_filter.html', **context)

    else: # if it's a GET request
        context = {
            'filter_types' : filter_types_dict.keys()
        }

        return render_template('image_filter.html', **context)


################################################################################
# GIF SEARCH ROUTE
################################################################################

API_KEY = 'LIVDSRZULELA'
TENOR_URL = 'https://api.tenor.com/v1/search'
pp = PrettyPrinter(indent=4)

@app.route('/gif_search', methods=['GET', 'POST'])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    if request.method == 'POST':

        # TODO: Get the search query & number of GIFs requested by the user, store each as a 
        # variable
        search_query = request.form.get('search_query')
        gif_num = request.form.get('quantity')

        response = requests.get(
            TENOR_URL,
            {

                # TODO: Add in key-value pairs for:
                # - 'q': the search query
                "q" : search_query,
                # - 'key': the API key (defined above)
                "key" : API_KEY,
                # - 'limit': the number of GIFs requested
                "limit" : gif_num
            })

        gifs = json.loads(response.content).get('results')

        context = {
            'gifs': gifs
        }

        # Uncomment me to see the result JSON!
        # pp.pprint(gifs)
        return render_template('gif_search.html', **context)
    else:
        return render_template('gif_search.html')

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
