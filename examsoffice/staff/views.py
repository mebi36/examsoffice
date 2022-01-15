from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from results.models import Lecturer
from .forms import CreateStaffBioForm, StaffBioForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def menu(request):
    return render(request, 'staff/menu.html',{})

@login_required
def bios_main(request):
    staff = Lecturer.objects.all()
    return render(request, 'staff/bios_main.html',{'staff': staff})

@login_required
def edit_staff_bio(request, pk):
    context = {}
    template = 'bio_data.html'
    try:
        lecturer = Lecturer.objects.get(pk=pk)
    except:
        #add message that lecturer does not exist
        messages.add_message(request, messages.ERROR, 
                            "Staff not found. Please register the staff here.",
                            extra_tags='text-danger')
        return HttpResponseRedirect(reverse('staff:create'))
    else:
        if request.method == 'GET':
            #create form with instance set as the lecturer object
            form = StaffBioForm(instance=lecturer)
            context['form'] = form
            context['action_url'] = reverse('staff:edit', kwargs={'pk':lecturer.id})
            return render(request, template, context)
        elif request.method == 'POST':
            form = StaffBioForm(request.POST, instance=lecturer)
            if not form.is_valid():
                return render(request, template, {'form':form})
            
            form.save()
            messages.add_message(request, messages.SUCCESS, "Update successful", 
                                        extra_tags='text-success')
            return render(request, template, {'form':form})
 
@login_required
def create_staff_bio(request):
    context = {}
    template = 'bio_data.html'
    if request.method == 'GET':
        context['form'] = CreateStaffBioForm()
        context['action_url'] = reverse('staff:create')
        return render(request, template, context)
    elif request.method == 'POST':
        form = CreateStaffBioForm(request.POST)
        if not form.is_valid():
            context = {'form': form}
            return render(request, template, context)

        form.save()
        messages.add_message(request, messages.SUCCESS, "Staff Bio saved.",
                            extra_tags='text-success')
        return render(request, template, {'form':form})

def delete_staff(request, pk):
    pass