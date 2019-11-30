import operator, random, string

from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import login, authenticate

from .forms import SignupForm, SigninForm, SubmitPromptForm, PromptForm, PromptSetForm, AccessCodeForm
from .models import PromptSet, Prompt, Profile, AccessCode

# MAIN
def index(request):
    if not check_auth(request):
        return redirect('signin')

    profile = get_profile(request)

    if not profile:
        return redirect('admin_dashboard')

    context = {
        'profile': profile,
        'f_prompt': get_featured_prompt(),
        'prompt_count': len(Prompt.objects.all()),
        'complete_count': profile.get_complete_count(),
        'leaderboard': get_leaderboard()
    }

    return render(request, 'index.html', context)

def view_set(request):
    if not check_auth(request):
        return redirect('signin')

    profile = get_profile(request)

    # Get Prompt Sets available
    sets = get_sets_available()
    set_select = get_set_select(request)

    prompts = Prompt.objects.filter(prompt_set=set_select)
    prompts = sorted(prompts, key=operator.attrgetter('ref'))

    completed = []

    if profile:
        for i in range(len(prompts)):
            if prompts[i] in profile.completed.all():
                completed.append(i)

    context = {
        'sets': sets,
        'set_select': set_select,
        'prompts': prompts,
        'completed': completed
    }

    return render(request, 'view_set.html', context)

def view_prompt(request, pk):
    prompt = get_object_or_404(Prompt, pk=pk)
    profile = get_profile(request)

    if request.method == "POST":
        form = SubmitPromptForm(request.POST)

        if form.is_valid():
            proccess_submit(profile, prompt, form)

            return redirect('/view_prompt/{}'.format(pk))
    else:
        other_prompts = Prompt.objects.filter(prompt_set=prompt.prompt_set)
        in_progress = profile and not(prompt in profile.completed.all())

        context = {
            'profile': profile,
            'prompt': prompt,
            'other_prompts': other_prompts,
            'in_progress': in_progress,
        }

        if in_progress:
            context['form'] = SubmitPromptForm()
        else:
            if prompt.rating >= 8:
                bg_color = "bg-success"
            elif prompt.rating >= 6:
                bg_color = "bg-info"
            elif prompt.rating >= 4:
                bg_color = "bg-warning"
            else:
                bg_color = "bg-danger"

            context['avg_satisfaction'] = "{}%".format((prompt.rating / 10) * 100)
            context['complete_count'] = prompt.complete_count
            context['bar_color'] = bg_color

    return render(request, 'view_prompt.html', context)

# Admin methods
def admin_dashboard(request):

    context = {
        'leaderboard': get_leaderboard(),
        'prompt_count': len(Prompt.objects.all()),
        'profile_count': len(Profile.objects.all())
    }

    return render(request, 'admin/admin_dash.html', context)

def manage(request):
    students = Profile.objects.all()
    std_pending = len(students.filter(status='Pending'))
    std_registered = len(students.filter(status='Registered'))

    a_codes = AccessCode.objects.all()
    codes_active = len(a_codes.filter(status='Active'))
    codes_inactive = len(a_codes.filter(status='Inactive'))

    context = {
        'students': students,
        'std_pending': std_pending,
        'std_registered': std_registered,

        'a_codes': a_codes,
        'codes_active': codes_active,
        'codes_inactive': codes_inactive,

        'prompt_count': len(Prompt.objects.all()),
    }

    return render(request, 'admin/manage.html', context)

def approve_student(request, pk):
    student = get_object_or_404(Profile, pk=pk)
    student.status = "Registered"
    student.save()

    return redirect('manage')

def reject_student(request, pk):
    student = get_object_or_404(Profile, pk=pk)

    query = AccessCode.objects.filter(profile=student)

    if len(query) != 0:
        access_code = query[0]
        access_code.status = 'Inactive'
        access_code.profile = None
        access_code.save()

    student.user.delete()
    student.delete()

    return redirect('manage')

def create_codes(request):
    if request.method == 'POST':
        form = AccessCodeForm(request.POST)

        if form.is_valid():
            qty = form.cleaned_data['quantity']
            code_len = form.cleaned_data['code_length']

            generate_codes(qty, code_len)

            return redirect('manage')
    else:
        form = AccessCodeForm()

    return render(request, 'admin/access_form.html', {'form': form})

def delete_codes(request):
    AccessCode.objects.all().delete()

    return redirect('manage')

# Create/Edit/Delete Form Methods
def create_prompt(request):
    if request.method == 'POST':
        form = PromptForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('view_set')
    else:
        form = PromptForm()

        context = {
            'title': 'Create Challenge',
            'type': 'create',
            'form': form,
        }

    return render(request, 'admin/prompt_form.html', context)

def edit_prompt(request, pk):
    prompt = get_object_or_404(Prompt, pk=pk)

    if request.method == 'POST':
        form = PromptForm(request.POST, instance=prompt)

        if form.is_valid():
            form.save()
            return redirect('view_set')
    else:
        form = PromptForm(instance=prompt)

        context = {
            'title': 'Edit Challenge',
            'type': 'edit',
            'form': form,
            'prompt': prompt
        }

    return render(request, 'admin/prompt_form.html', context)

def delete_prompt(request, pk):
    prompt = get_object_or_404(Prompt, pk=pk)
    prompt.delete()

    return redirect('view_set')

def create_set(request):
    if request.method == 'POST':
        form = PromptSetForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('view_set')
    else:
        form = PromptSetForm()

        context = {
            'title': 'Create Set',
            'type': 'create',
            'form': form,
        }

    return render(request, 'admin/set_form.html', context)

def edit_set(request, pk):
    set = get_object_or_404(PromptSet, pk=pk)

    if request.method == 'POST':
        form = PromptSetForm(request.POST, instance=set)

        if form.is_valid():
            form.save()
            return redirect('view_set')
    else:
        form = PromptSetForm(instance=set)

        context = {
            'title': 'Edit Set',
            'type': 'edit',
            'form': form,
            'set': set
        }

    return render(request, 'admin/set_form.html', context)

def delete_set(request, pk):
    set = get_object_or_404(PromptSet, pk=pk)
    set.delete()

    return redirect('index')

# Authentication Methods
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            access_code = form.cleaned_data['access_code']
            query = AccessCode.objects.filter(code=access_code)

            if (len(query) == 0) or (query[0].status == 'Active'):
                context = {
                    'form': form,
                    'msg_type': 'Error',
                    'msg': 'Sorry, the access code does not exist, or has already been used.'
                }

                return render(request, 'auth/signup.html', context)
            else:
                query[0].status = 'Active'
                query[0].save()

            user = form.save()

            profile = Profile()
            profile.user = user
            profile.usertag = form.cleaned_data['usertag']
            profile.save()

            query[0].profile = profile
            query[0].save()

            raw_password = form.cleaned_data['password1']
            user = authenticate(username=user.username, password=raw_password)

            context = {
                'form': SignupForm(),
                'msg_type': 'Pending',
                'msg': 'Your account has been created and is now pending admin approval.'
            }

            return render(request, 'auth/signup.html', context)
    else:
        form = SignupForm()

    return render(request, 'auth/signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = SigninForm(request.POST)

        if form.is_valid():
            raw_password = form.cleaned_data['password']
            raw_username = form.cleaned_data['username']
            user = authenticate(username=raw_username, password=raw_password)

            query = Profile.objects.filter(user=user)

            if len(query) != 0:
                if query[0].status == "Pending":
                    context = {
                        'form': form,
                        'msg_type': 'Error',
                        'msg': 'Sorry, your account is still pending admin approval.'
                    }

                    return render(request, 'auth/signin.html', context)

            login(request, user)

            return redirect('index')
    else:
        form = SigninForm()

    return render(request, 'auth/signin.html', {'form': form})

# HELPERS
def check_auth(request):
    if not request.user.is_authenticated:
        return False
    else:
        return True

def get_featured_prompt():
    prompts = []
    prompts += Prompt.objects.filter(prompt_set=random.choice(get_sets_available()))

    return random.choice(prompts)

def get_profile(request):
    query = Profile.objects.filter(user=request.user)

    try:
        profile = query[0]
    except IndexError:
        profile = False

    return profile

def get_leaderboard():
    profiles = []

    query = Profile.objects.all()
    if len(query) == 0:
        return profiles

    profiles += query
    profiles.sort(key=lambda x: x.get_complete_count(), reverse=True)

    if len(profiles) > 3:
        profiles = profiles[:3]

    return profiles

def proccess_submit(profile, prompt, form):
    new_entry = int(form.cleaned_data['satisfaction'])
    status = form.cleaned_data['status']

    if status == "Completed":
        rating_sum = (prompt.rating * prompt.complete_count) + new_entry
        new_rating = rating_sum / (prompt.complete_count + 1)

        prompt.rating = new_rating
        prompt.complete_count += 1
        prompt.save()

        profile.completed.add(prompt)
        profile.save()

# Prompt Set Filter Methods
def get_sets_available():
    sets = []

    query = PromptSet.objects.all()
    sets += query

    return sets

def get_sets_ref(request):
    if not('set_select' in request.session):
        request.session['set_select'] = -1

    ref = request.session['set_select']
    return ref

def get_set_select(request):
    sets = get_sets_available()
    ref = get_sets_ref(request)

    try:
        set_select = sets[ref]
    except IndexError:
        set_select = sets[0]
        request.session['set_select'] = 0

    return set_select

def set_sets_ref(request, id):
    request.session['set_select'] = int(id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Access Code Methods
def generate_codes(qty, code_length):
    for i in range(qty):
        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=code_length))
            query = AccessCode.objects.filter(code=code)

            if len(query) == 0:
                new_access_code = AccessCode(code=code, profile=None)
                new_access_code.save()

                break
