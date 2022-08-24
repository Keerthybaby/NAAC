import os
from time import sleep

from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user

from .models import *
from .forms import CreateUserForm, IiqaForm, SsrTextVerifyForm, SsrGeoForm
import PyPDF2
from exif import Image


# Create your views here.

def home(request):
    return render(request, 'naac/home.html')


# @unauthenticated_user
def signup(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            # user = form.save()
            form.save()
            username = form.cleaned_data.get('username')
            # Iiqa.objects.create(
            #     user=user
            # )
            messages.success(request, "Account created for " + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'naac/signup.html', context)


# @unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, "Username or Password is incorrect")

    context = {}
    return render(request, 'naac/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashBoard(request):
    context = {'navbar': 'dashboard'}
    return render(request, 'naac/dashboard.html', context)


@login_required(login_url='login')
def iiqa(request):
    # form = IiqaForm(initial={'user': request.user})
    form = IiqaForm()
    # c = User.objects.get(id=pk)
    try:
        if request.method == 'POST':
            form = IiqaForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.save()
                return redirect('ssrtxtverify')
    except Exception as e:
        return HttpResponse(e)

    context = {'form': form, 'navbar': 'iiqa'}

    return render(request, 'naac/iiqa.html', context)


# funciton for conerting pdf into text
def textpdfConvert(filename):
    pdfFileObj = filename.open(mode='rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    # printing number of pages in pdf file
    print(pdfReader.numPages)
    # creating a page object
    for page in range(0, pdfReader.getNumPages()):
        pageObj = pdfReader.getPage(page)

        # extracting text from page
        txt_extracted = pageObj.extractText()

    # closing the pdf file object

    txt_extracted = txt_extracted.split("\n")
    return txt_extracted, pdfFileObj


@login_required(login_url='login')
def ssrTextVerify(request):
    form = SsrTextVerifyForm()
    try:
        if request.user.ssr_text_converter:
            status = request.user.ssr_text_converter.status
    except:
        status = "None"

    try:
        if request.method == 'POST':
            form = SsrTextVerifyForm(request.POST, request.FILES)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                filename = request.user.ssr_text_converter.pdf

                txt_extracted, pdfFileObj = textpdfConvert(filename)

                if (request.user.ssr_text_converter.clg_name in txt_extracted) and (
                        request.user.ssr_text_converter.uni_name) in txt_extracted:
                    form.status = 'success'
                    form.save()
                    pdfFileObj.close()
                    return redirect('ssrtxtverify')
                else:
                    messages.error(request, "Data does not match")
                    return redirect('ssrtxtverify')

    except Exception as e:
        messages.error(request, e)
        return redirect('ssrtxtverify')

    context = {'navbar': 'ssrtxtverify', 'form': form, 'status': status}
    return render(request, 'naac/ssr_txt_verify.html', context)


def gps_info(path):
    """
    Function returns latitude, longitude and altitude of an image
    """
    with path.open(mode='rb') as src:
        img = Image(src)

    latitude = img.gps_latitude
    longitude = img.gps_longitude
    altitude = img.gps_altitude

    latitude = ", ".join(list(map(str, list(latitude)))) + img.gps_latitude_ref
    longitude = ", ".join(list(map(str, list(longitude)))) + img.gps_longitude_ref

    return latitude, longitude


def convert_gps_decimal(tude):
    """
    Converts degrees, minutes, seconds to decimal degrees
    """

    multiplier = 1 if tude[-1] in ['N', 'E'] else -1
    return multiplier * sum(float(x) / 60 ** n for n, x in enumerate(tude[:-1].split(',')))


@login_required(login_url='login')
def ssrGeo(request):
    form = SsrGeoForm()
    latitude = 0
    longitude = 0
    lat_convert = 0
    long_convert = 0

    try:
        if request.method == 'POST':
            form = SsrGeoForm(request.POST, request.FILES)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.save()
                # return redirect('ssrgeo')
                path = request.user.ssr_geo_tag.img

                latitude, longitude = gps_info(path)

                lat_convert = convert_gps_decimal(latitude)
                long_convert = convert_gps_decimal(longitude)

                form.latitude = latitude
                form.longitude = longitude
                form.lat_convert = lat_convert
                form.long_convert = long_convert
                form.status = True

                form.save()

    except Exception as e:
        messages.error(request, e)
        return redirect('ssrgeo')

    try:
        if request.user.ssr_geo_tag:
            data = Ssr_Geo_Tag.objects.all().values()

            context = {'navbar': 'ssrgeo', 'form': form, 'latitude': data[0]['latitude'],
                       'longitude': data[0]['longitude'],
                       'lat_convert': data[0]['lat_convert'], 'long_convert': data[0]['long_convert'],
                       'status': data[0]['status']}
    except:
        status = False
        context = {'navbar': 'ssrgeo', 'form': form, 'latitude': latitude,
                   'longitude': longitude,
                   'lat_convert': lat_convert, 'long_convert': long_convert,
                   'status': status}

    return render(request, 'naac/ssr_geo.html', context)
