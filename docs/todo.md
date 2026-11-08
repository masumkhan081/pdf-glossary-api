2. Register the app

In config/settings.py, add this entry to the existing INSTALLED_APPS list:
"glossary.apps.GlossaryConfig",

3. Create the form

Create glossary/forms.py:
from django import formsclass TextAnalysisForm(forms.Form):    text = forms.CharField(        label="Paste some text",        max_length=20000,        widget=forms.Textarea(attrs={"rows": 10}),    )


This defines both the input field and its server-side validation. Blank text and text exceeding the limit are rejected.

4. Connect the processing function

Keep text_processing.py beside manage.py. It should contain your count_words() function from step 8.

Replace glossary/views.py with:
from django.shortcuts import renderfrom text_processing import count_wordsfrom .forms import TextAnalysisFormdef home(request):    counts = None    if request.method == "POST":        form = TextAnalysisForm(request.POST)        if form.is_valid():            text = form.cleaned_data["text"]            counts = count_words(text)    else:        form = TextAnalysisForm()    return render(        request,        "glossary/home.html",        {"form": form, "counts": counts},    )


The view handles the request. GET displays an empty form; POST validates submitted text and processes it. render() combines the template with the supplied data to produce an HTML response. Django

5. Wire the URLs

Create glossary/urls.py:
from django.urls import pathfrom . import viewsapp_name = "glossary"urlpatterns = [    path("", views.home, name="home"),]


Replace config/urls.py with:
from django.contrib import adminfrom django.urls import include, pathurlpatterns = [    path("admin/", admin.site.urls),    path("", include("glossary.urls")),]


The project router delegates / to the glossary app, which calls home().

6. Create the template

Create these folders and file:

glossary/templates/glossary/home.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PDF Glossary</title>
</head>
<body>
    <h1>Text analyser</h1>
    <p>Our first step towards a pre-reading glossary.</p>

    <form method="post" action="{% url 'glossary:home' %}">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Analyse text</button>
    </form>

    {% if counts is not None %}
        <h2>Word counts</h2>
        <ul>
            {% for word, count in counts.items %}
                <li>{{ word }}: {{ count }}</li>
            {% empty %}
                <li>No matching words found.</li>
            {% endfor %}
        </ul>
    {% endif %}
</body>
</html>

- {{ ... }} outputs values; {% ... %} handles template instructions.
- form.as_p displays fields and validation errors.
- csrf_token works with Django’s middleware to protect form submissions against cross-site request forgery. Django
7. Run and verify
python manage.py migrate
python manage.py runserver

For this milestone, migrate creates Django’s built-in tables in the default local SQLite database. PostgreSQL remains our planned project database when we introduce stored documents and glossary results.