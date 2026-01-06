from django.shortcuts import render
from .models import Question

# Create your views here.

def questions_read(request, pk):
    question = Question.objects.get(id=pk)
    
    context = {
        "question" : question
    }
    return render(request, questions_read.html, context)