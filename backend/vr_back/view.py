#!/usr/bin/python
#-*-coding:utf-8-*-

from django.shortcuts import render
from .forms import *

def index(request):
    return render(request, 'index.html')

def looklibao(request):
    index = request.GET.get('index')
    if index == None:
        items = LibaoItems(1)
    else:
        items = LibaoItems(int(index))

    return render(request, 'looklibao.html', {'items': items})

def clibao(request):
    if request.method == "POST":
        form = ClibaoForm(request.POST)
        form.items = MailItem()
        form.items.type1 = int(request.POST['reward1_1']);
        if form.items.type1 > 0:
            form.items.value11 = int(request.POST['reward1_2']);
            form.items.value12 = int(request.POST['reward1_3']);
        form.items.type2 = int(request.POST['reward2_1']);
        if form.items.type2 > 0:
            form.items.value21 = int(request.POST['reward2_2']);
            form.items.value22 = int(request.POST['reward2_3']);
        form.items.type3 = int(request.POST['reward3_1']);
        if form.items.type3 > 0:
            form.items.value31 = int(request.POST['reward3_2']);
            form.items.value32 = int(request.POST['reward3_3']);
        form.is_valid()
    else:
        form = ClibaoForm()

    return render(request, 'clibao.html', {'form': form})

def dlibao(request):
    if request.method == "POST":
        form = DlibaoForm(request.POST)
        form.is_valid()
    else:
        form = DlibaoForm()

    return render(request, 'dlibao.html', {'form': form})
