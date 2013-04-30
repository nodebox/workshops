from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login
from django.template import RequestContext


def accounts_login(request):
    message = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(request.GET.get('next', '/'))
            else:
                return render_to_response('accounts/disabled.html')
        else:
            message = 'Invalid login or password.'
    return render_to_response('accounts/login.html', {message: message}, context_instance=RequestContext(request))
