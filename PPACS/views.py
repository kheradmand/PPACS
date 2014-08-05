from django.http.response import HttpResponse
from django.shortcuts import render
import subprocess


def home(request):
    return render(request, 'home.html')

def log(request):
    p = subprocess.Popen("cat nohup.out", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return HttpResponse(output, content_type='text/plain')
