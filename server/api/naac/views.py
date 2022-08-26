import os
from time import sleep
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user

from .models import *
from .forms import CreateUserForm, IiqaForm, SsrTextVerifyForm, SsrGeoForm, SsrPlotForm
import PyPDF2
from exif import Image
import pandas as pd
import numpy as np
import plotly.express as px


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
    form = IiqaForm()
    try:
        if request.user.iiqa:
            status = request.user.iiqa.status
    except:
        status = False
    try:
        if request.method == 'POST':
            form = IiqaForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                # request.user.iiqa.status = True
                form.status = True
                form.save()
                return redirect('ssrtxtverify')
    except Exception as e:
        messages.error(request, e)
        return redirect('iiqa')

    context = {'form': form, 'navbar': 'iiqa', 'status': status}

    return render(request, 'naac/iiqa.html', context)


# funciton for conerting pdf into text
def textpdfConvert(filename):
    pdfFileObj = filename.open(mode='rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    txt_extracted = []
    # printing number of pages in pdf file
    print(pdfReader.numPages)
    # creating a page object
    for page in range(0, pdfReader.getNumPages()):
        pageObj = pdfReader.getPage(page)

        # extracting text from page
        txt_extracted.append(pageObj.extractText())
    # closing the pdf file object

    txt_extracted = txt_extracted[0].split("\n")
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
                txt_extracted = list(map(lambda x: x.strip(' '), txt_extracted))
                while "" in txt_extracted:
                    txt_extracted.remove("")

                txt_extracted_numbers = []
                for item in txt_extracted:
                    for subitem in item.split():
                        if (subitem.isdigit()):
                            txt_extracted_numbers.append(int(subitem))

                txt_extracted += txt_extracted_numbers
                print(txt_extracted)

                progress_bar = 0

                if request.user.ssr_text_converter.college_name not in txt_extracted:
                    messages.error(request, "College Name doesn't match with the given PDF")
                else:
                    messages.success(request, "College Name matches with the given PDF")
                    progress_bar += 25

                if request.user.ssr_text_converter.university_name not in txt_extracted:
                    messages.error(request, "University Name doesn't match with the given PDF")
                else:
                    messages.success(request, "University Name matches with the given PDF")
                    progress_bar += 25

                if request.user.ssr_text_converter.courses_offered not in txt_extracted:
                    messages.error(request, "Courses offered doesn't match with the given PDF")
                else:
                    messages.success(request, "Courses offered matches with the given PDF")
                    progress_bar += 25

                if request.user.ssr_text_converter.total_no_of_students not in txt_extracted:
                    messages.error(request, "Total number of students doesn't match with the given PDF")
                else:
                    messages.success(request, "Total number of students matches with the given PDF")
                    progress_bar += 25

                messages.info(request, progress_bar)

                if (request.user.ssr_text_converter.college_name in txt_extracted) and \
                        (request.user.ssr_text_converter.university_name in txt_extracted) and \
                        (request.user.ssr_text_converter.courses_offered in txt_extracted) and \
                        (request.user.ssr_text_converter.total_no_of_students in txt_extracted):
                    form.status = 'success'
                    form.save()
                    pdfFileObj.close()
                    return redirect('ssrtxtverify')
                else:
                    messages.error(request, "Data verification Failed. Enter the data correctly")
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
        Ssr_Geo_Tag.objects.filter(user=request.user).delete()
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


@login_required(login_url='login')
def ssrPlot(request, **kwargs):
    form = SsrPlotForm()
    data_header = []
    data_values = []
    data_header_2 = []
    data_values_2 = []
    graph = None
    my_bar = 0

    try:
        if request.user.ssr_plot:
            status = request.user.ssr_plot.status
    except:
        status = False

    try:
        if request.method == 'POST':

            if not status:
                form = SsrPlotForm(request.POST, request.FILES)
                if form.is_valid():
                    form = form.save(commit=False)
                    form.status = True
                    form.user = request.user
                    form = form.save()
                    return redirect('ssrplot')

        filename = request.user.ssr_plot.excel
        df = pd.read_excel(filename, engine='openpyxl', header=1)
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)
        data_header = list(data[0].keys())

        for i in data:
            data_values.append(list(i.values()))

        if 'select_box' in request.POST:
            filename_2 = request.user.ssr_plot.excel
            df_2 = pd.read_excel(filename_2, engine='openpyxl', header=1)
            json_records_2 = df_2.reset_index().to_json(orient='records')
            data_2 = json.loads(json_records_2)
            data_header_2 = list(data_2[0].keys())

            for i in data_2:
                data_values_2.append(list(i.values()))

            output_columns = [data_header[3], data_header[4]]
            if request.POST['select_box'] == 'pgm_name':
                groupby_column = data_header_2[1]
                df_grouped_2 = df_2.groupby(by=[data_header[1]], as_index=False)[output_columns].sum()
                df_grouped_2.drop(df.tail(1).index,inplace=True)
            elif request.POST['select_box'] == 'pgm_code':
                groupby_column = data_header_2[2]
                df_grouped_2 = df_2.groupby(by=[data_header[2]], as_index=False)[output_columns].sum()


            fig = px.bar(
                df_grouped_2,
                x=groupby_column,
                y=data_header_2[3],
                color=data_header_2[4],
                color_continuous_scale=['red', 'yellow', 'green'],
                template='plotly_white',
                title=f'<b>Number of seats sanctioned &Number of Students admitted by{groupby_column}</b>'
            )

            graph = fig.to_html(full_html=False, default_height=950, default_width=950)

            # keywords
            courseList = df_grouped_2[groupby_column]

            total = len(courseList)
            print(total)

            #How many total programs have their seats filled
            seats_filled = df_grouped_2[df_grouped_2[data_header_2[3]] == df_grouped_2[data_header_2[4]]].count()
            print(seats_filled[1])

            my_bar = round((seats_filled[2]/total) * 100, 2)
            print(my_bar)

    except:
        status = False

    context = {'navbar': 'ssrplot', 'form': form, 'data_header': data_header,
               'data_values': data_values, 'status': status, 'graph': graph, 'my_bar': my_bar}
    return render(request, 'naac/ssr_plot.html', context)
