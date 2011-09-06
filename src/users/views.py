from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect


from barabasdjango.webserver import WebServer
from forms import PasswordLoginForm, PasswordBasedRegistrationForm, ProfileForm
from decorators import LoginRequired

def index(request):
    if request.method == "POST":
        loginForm = PasswordLoginForm(request.POST)
        if (loginForm.is_valid()):
            request.session['userid'] = loginForm.cleaned_data['passwordAuthentication'].userID
            return     HttpResponseRedirect('/')
    else:
        loginForm = PasswordLoginForm()
        
    return render_to_response('users/index.html',
                              {
                               'loginForm' : loginForm,
                              },
                              context_instance=RequestContext(request))

def logout(request):
    del request.session['userid']
    return HttpResponseRedirect('/')

def signup(request):
    if request.method == "POST":
        registrationForm = PasswordBasedRegistrationForm(request.POST)
        
        if (registrationForm.is_valid()):
            database = WebServer.database()
            user = registrationForm.cleaned_data['user']
            pa = registrationForm.cleaned_data['passwordAuth']
            
            database.add(user)
            database.commit()
    
            return HttpResponseRedirect('/')
    else:
        registrationForm = PasswordBasedRegistrationForm()
    
    return render_to_response('users/signup.html',
                              {
                               'registrationForm': registrationForm
                              },
                              context_instance=RequestContext(request))

@LoginRequired
def profile(request):
    profileForm = ProfileForm()
    return render_to_response('users/profile.html',
                              {
                               'profileForm' : profileForm
                              },
                              context_instance=RequestContext(request))
