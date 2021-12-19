from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError

from results.models import Session, Course, LevelOfStudy, ProgramRequirement
from programs.forms import prog_req_formset
# Create your views here.

# there could be a view for adding a single program requirement
# and another view for adding the entire program requirement of 
# for an entire level of study
# there could be a view for reviewing the program requirement of 
# the last session and agreeing that nothing has changed/adopting
# it for the new session.

def add_formset_bootstrap(formset):
    for form in formset:
        for my_field in form.fields:
            form.fields[my_field].widget.attrs['class'] = 'form-control w-75'
    return formset

def menu(request):
    template = 'programs/menu.html'
    return render(request, template, {})

def add_prog_requirement_form(request):
    context = {}
    if request.method == 'GET':
        template = 'programs/prog_requirement_form.html'
        session = Session.objects.all().order_by('-id')
        level_of_study = LevelOfStudy.objects.all().filter(level__lte=5)
        context = {'sessions': session, 'levels_of_study': level_of_study}
        return render(request, template, context)
    elif request.method == 'POST':
        # prog_req_qs = ProgramRequirement.objects.all().filter(
        #                         session=request.POST['session'],
        #                         level_of_study=request.POST['level_of_study'])
        # #start by checking if there are any existing prog req for the given 
        # #session/level_of_study. If there are, list them with links to edit them
        # #else just provide form for adding new prog req

        
        # #add prog_req_qs to the context
        # context['existing_prog_req'] = prog_req_qs if len(prog_req_qs)>0 else None
        return HttpResponseRedirect(reverse('programs:edit_prog_req', 
                                    kwargs={'session': request.POST['session'],
                                    'level_of_study': request.POST['level_of_study']}))


#there is nothing to edit about a single prog req entry 
#there should just be a simple option of removing and adding another one
#the editing view should be for handling the prog req entries that belong to
#particular session/level of study

def edit_prog_req(request, session, level_of_study):
    template = 'programs/edit_prog_req.html'
    context = {}
    session_title = Session.objects.get(id=session)
    level_title = LevelOfStudy.objects.get(level=level_of_study) 
    context['session_title'] = session_title
    context['level_title'] = level_title

    prog_req = ProgramRequirement.objects.all().filter(
                                session=session, level_of_study=level_of_study)
    formset = prog_req_formset(queryset=prog_req)
    # formset = add_formset_bootstrap(formset)
    
    if request.method == 'GET':
        context['formset'] = formset
        return render(request, template, context)
    elif request.method == 'POST':
        formset = prog_req_formset(request.POST)
        for form in formset:
            if form.is_valid():
                if form.cleaned_data != {}:
                    if form.cleaned_data.get('DELETE'):
                        print(form.cleaned_data.get('id').id)
                        try:
                            obj = ProgramRequirement.objects.get(
                                            pk=form.cleaned_data.get('id').id)
                        except:
                            print("problem fetching model instance")
                        else:
                            obj.delete()
                    else:
                        obj = form.save(commit=False)
                        obj.level_of_study = LevelOfStudy(level=level_of_study)
                        obj.session = Session(id=session)
                        try:
                            obj.save()
                        except IntegrityError:
                            messages.add_message(request, messages.ERROR,
                                        f"Course already exists as a program requirement",
                                        extra_tags='text-danger')
                            return HttpResponseRedirect(reverse('programs:edit_prog_req', 
                                    kwargs={'session': session,
                                    'level_of_study': level_of_study}))

                        
            else:
                print("invalid form found!!!")
        if request.POST['submit'] == 'Finish':
            return HttpResponse("Formset has been validated!")
        elif request.POST['submit'] == 'Save and Continue':
            return HttpResponseRedirect(reverse('programs:edit_prog_req', 
                                    kwargs={'session': session,
                                    'level_of_study': level_of_study}))

