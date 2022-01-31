from httplib2 import Response
#Imports necesarios
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Importamos nuestros forms y modelos
from api import forms, models, serializers


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

# Definimos a la función con un POST
@api_view(['POST'])
def create_account(request):
    # Para usar las forms le pasamos el objeto "request.POST" porque esperamos que sea
    # un form que fue lanzado con un POST
    form = forms.CreateUserForm(request.POST)
    # Vemos si es válido, que acá verifica que el mail no exista ya
    if form.is_valid():
        # Guardamos el usuario que el form quiere crear, el .save() devuelve al usuario creado
        user = form.save()
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo, y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)