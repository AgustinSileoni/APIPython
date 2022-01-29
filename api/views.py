import imp
from django.shortcuts import render
from httplib2 import Response
#Imports necesarios
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
# Devolvemos el mapa hello world en forma de JSON (el response utiliza JSON) en la parte del body
# Devolvemos un codigo 200 de OK en el header
# status tiene los codigos que utlizamos para retornar
@api_view(['GET'])
def test_get(request):
    return Response({"hola": "mundo"}, status= status.HTTP_200_OK)

@api_view(["GET"])
def test_get_path_param(request, id):
    return Response({"hello":id}, status= status.HTTP_200_OK)

@api_view(["GET"])
def test_get_query_param(request):
    #Obtenemos el parametro q desde el link curl localhost:8000/api/test/query?q=hola y si no utiliza el valor por default 
    q = request.GET.get('q', 'default')
    return Response({"hello": q}, status = status.HTTP_200_OK)

@api_view(['POST'])
def test_post_body(request):
    #El body se encuentra en "request.data"
    return Response({"hello": request.data}, status= status.HTTP_200_OK)

@api_view(['GET'])
def test_get_suma(request):
    l = request.GET.get('l',0)
    r = request.GET.get('r',0)
    n = float(l) + float(r)
    return Response({"resultado": n}, status=status.HTTP_200_OK)
    
@api_view(['PUT'])
def test_get_suma_mas(request):
    total = 0
    nums = request.data["sums"]
    for numb in nums:
        total += numb
    return Response({"resultado": total}, status= status.HTTP_200_OK)

@api_view(['POST'])
def test_bueno_malo(request):
    limit = int(request.GET.get("limit",10))
    n = request.data["n"]
    if n>= limit:
        return Response( {"resuldato": "TRUE"},status= status.HTTP_200_OK)
    else :
        return Response( {"resuldato": "FALSE"},status= status.HTTP_400_BAD_REQUEST)