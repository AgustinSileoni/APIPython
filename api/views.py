import imp
from statistics import mode
from unicodedata import name
from httplib2 import Response
#Imports necesarios
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Importamos nuestros forms y modelos
from api import forms, models, serializers, constants
# Importamos el decorator
from rest_framework.decorators import api_view, permission_classes
# Importamos los permisos
from rest_framework.permissions import AllowAny, IsAuthenticated
#Importamos la clase Group
from django.contrib.auth.models import Group
#Importamos nuestro permiso
from api.permissions import IsAdmin

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

# Juntamos las opciones de crear y pedir los usuarios dependiendo de si es una peticion POST(Crear) o GET(Obtener)
@api_view(['POST','GET'])
@permission_classes([AllowAny])
def accounts_view(request):
    # Hacemos el caso de un GET y el caso de un POST
    if request.method == 'GET':
        return get_accounts(request)
    else:
        return create_account(request)


def create_account(request):
    # Para usar las forms le pasamos el objeto "request.POST" porque esperamos que sea
    # un form que fue lanzado con un POST
    form = forms.CreateUserForm(request.POST)
    # Vemos si es válido, que acá verifica que el mail no exista ya
    if form.is_valid():

        # Guardamos el usuario que el form quiere crear, el .save() devuelve al usuario creado
        user = form.save()
        #Agregamos por default el grupo user a todos los usuarios
        user.groups.add(Group.objects.get(name= constants.GROUP_USER))
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo, y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

def get_accounts(request):
    # Chequear que no sea anónimo <-- AGREGAMOS ESTO
    # Si no está autenticado, devolvemos un 401
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # Obtenemos todos los usuarios y los serializamos
    users = serializers.UserSerializer(models.User.objects.all(), many=True).data
    # Agregamos los datos a la respuesta
    return Response(users, status=status.HTTP_200_OK)

#Especificamos un DELETE
@api_view(['DELETE'])
@permission_classes([IsAdmin]) #Definimos que tiene que ser un admin
def user_delete(request, id):
    # No dejamos que un usuario se borre a si mismo
    # Vemos si el ID del usuario de la request es igual al que se manda en la URL
    if(request.user.id==id):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    # Necesitamos un try-catch porque tal vez el usuario no existe
    try:
        # Buscamos al usuario por ID
        user = models.User.objects.get(pk=id)
        #Borramos al usuario
        user.delete()
        #Devolvemos que no hay contenido porque lo pudimos borrar
        return Response(status=status.HTTP_204_NO_CONTENT)
    except models.User.DoesNotExist:
        #Si no existe devolvemos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)

