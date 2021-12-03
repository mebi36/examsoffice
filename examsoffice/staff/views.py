from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from results.models import Lecturer
from .forms import StaffBioForm
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
            initial_form = StaffBioForm(instance=lecturer)
            if form.is_valid():
                for field in form.cleaned_data.keys():
                    # print(form[field].value(),':', field)
                    if form.cleaned_data[field] != initial_form[field].value():
                        if field == 'head_of_dept' and form.cleaned_data[field] == True:
                            try:
                                outgoing_hod = Lecturer.objects.get(head_of_dept=True)
                            except:
                                print("no hod for now")
                            else:
                                outgoing_hod.head_of_dept = False
                                outgoing_hod.save(update_fields=['head_of_dept'])
                        if field == 'staff_number' and Lecturer.is_valid_staff_no(form.cleaned_data[field]) == False:
                            continue
                        
                        # lecturer = Lecturer.objects.get(pk=pk)
                        Lecturer.objects.get(pk=pk).field = form.cleaned_data[field]
                        lecturer.save()
                messages.add_message(request, messages.SUCCESS, 
                                "Update Successful", extra_tags='text-success')
                return HttpResponseRedirect(reverse('staff:menu'))
            else:
                messages.add_message(request, messages.ERROR, "Error processing some entries",
                                                extra_tags='text-danger')
                return HttpResponseRedirect(reverse('staff:bios_main'))


@login_required
def create_staff_bio(request):
    context = {}
    if request.method == 'GET':
        context['form'] = StaffBioForm()
        context['action_url'] = reverse('staff:create')
        return render(request, 'bio_data.html', context)
    elif request.method == 'POST':
        staff_number = request.POST['staff_number'].upper() if request.POST['staff_number'] != None else None
        if Lecturer.is_valid_staff_no(staff_number):
            try:
                staff = Lecturer.objects.get(staff_number=request.POST['staff_number'])
            except:
                staff = Lecturer(staff_number=request.POST['staff_number'])
                staff.save()
            else:
                messages.add_message(request, messages.INFO,
                            "Staff already exists",
                            extra_tags='text-primary')
                return HttpResponseRedirect(reverse('staff:edit', kwargs={'pk':staff.pk}))

            form = StaffBioForm(request.POST, instance=staff)
            initial_form = StaffBioForm()

            if form.is_valid():
                for field in form.cleaned_data.keys():
                    if form.cleaned_data[field] != initial_form[field].value():
                        Lecturer.objects.get(pk=staff.pk).field = form.cleaned_data[field]
                        staff.save()
            
            messages.add_message(request, messages.SUCCESS, "Staff Bio saved.",
                                extra_tags='text-success')

        else:
            messages.add_message(request, messages.ERROR, 
                            '''Invalid Staff Number. Ensure your entry begins 
                            with 'SS.' followed by the actual number''',
                            extra_tags='text-danger')
            return HttpResponseRedirect(reverse('staff:create'))
        return HttpResponseRedirect(reverse('staff:menu'))

def delete_staff(request, pk):
    pass