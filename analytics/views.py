from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.gis.geoip2 import GeoIP2
from ipware import get_client_ip
from .models import PageView,GeoLocation
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.db.models import Count
import datetime

def Pagedata(request):
    pass

@api_view(['GET', 'POST'])
def track_page_view(request):
    if request.method == 'POST':
        request.session['uuid'] = request.data.get('uuid',uuid.uuid4)
        is_gloc = True
        data = request.data
        geodata = data.get('geoLocation')
        if geodata:
            is_gloc = True
            print("----------------true---------------")
        print(data)
        print(geodata)
        page_view = PageView.objects.create(
            uuid = data.get('uuid',uuid.uuid4),
            url = data.get('url',None),
            title = data.get('title',None),
            duration = data.get('duration',0),
            timestamp = parse_datetime(data.get('timestamp',None)),
            devicetype = data.get('deviceType',None),
            useragent = data.get('userAgent',None),
            ipaddress = data.get('ipAddress',None),
            is_geolocation = is_gloc
        )
        if geodata:
            GeoLocation.objects.create(
                page = page_view,
                city = geodata['city'],
                continent_code = geodata['continent_code'],
                continent_name = geodata['continent_name'],
                country_code = geodata['country_code'],
                country_name = geodata['country_name'],
                dma_code = geodata['dma_code'],
                is_in_european_union = geodata['is_in_european_union'],
                postal_code = geodata['postal_code'],
                region = geodata['region'],
                time_zone = geodata['time_zone'],
                latitude = geodata['latitude'],
                longitude = geodata['longitude']
            )
        else:
            GeoLocation.objects.create(
                page = page_view
            )
        response =  Response({"message": page_view.pk})
        response.set_cookie('name', 'jujule')
        return response
    return Response({"message": "Hello, world!"})

@api_view(['GET'])
def get_user_ip_address(request):
    client_ip, re_te = get_client_ip(request)
    print(client_ip,re_te)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return Response({'ip':ip_address})



def get_ip_geolocation(ip_address):
    g = GeoIP2()
    try:
        geolocation = g.city(ip_address)
        return geolocation
    except Exception as e:
        print(f'Error retrieving geolocation: {e}')
        return False
    return None

@csrf_exempt
@api_view(['GET','POST'])
def get_user_ip_geolocation(request):
    if request.method == 'POST':
        print(request.data)
        ip_address = request.data['ip_address']
    else:
        ip_address = '106.216.230.181'
    geolocation = get_ip_geolocation(ip_address)
    return Response({"message": geolocation})

def Homepage(request):
    return render(request,'analytics/index.html')

@api_view(['GET'])
def get_cou_ln_lo(request):
    today_date = datetime.date.today()
    today_date_1 = datetime.date.today()+datetime.timedelta(days=1)
    last_months_ago =today_date - datetime.timedelta(days=30)
    data = GeoLocation.objects.filter(page__timestamp__gte=last_months_ago, page__timestamp__lte=today_date_1)
    count_data = GeoLocation.objects.filter(page__timestamp__gte=last_months_ago, page__timestamp__lte=today_date_1).values('city').annotate(count=Count('city'))
    geoData = []
    for i in data:
        # if i.city == None:
        #     break
        i_count = 1
        for entry in count_data:
            if entry['city'] == i.city:
                i_count = entry['count']
                break
        geoData.append({'city':i.city,
                        "country":i.country_name,
                        "country_code":i.country_code,
                        'visitors': i_count,
                        'lat': i.latitude,
                        'lng': i.longitude
                        })
    return Response(list(geoData))

@api_view(['GET'])
def get_country(request):
    today_date = datetime.date.today()
    last_months_ago =today_date - datetime.timedelta(days=30)
    today_date_1 = datetime.date.today()+datetime.timedelta(days=1)
    count_data = GeoLocation.objects.filter(page__timestamp__gte=last_months_ago, page__timestamp__lte=today_date_1).values('country_name').annotate(count=Count('country_name'))
    return Response(count_data)

@api_view(['GET'])
def get_device_type(request):
    count_data = GeoLocation.objects.values('page__devicetype').annotate(count=Count('page__devicetype'))
    return Response(count_data)

@api_view(['GET'])
def Realtime_Country(request):
    data = GeoLocation.objects.filter(page__is_active=True).values('country_name').annotate(count=Count('country_name'))
    return Response(data)