from os import stat
from pickle import NONE
from urllib import response
from httplib2 import Response
#Imports necesarios
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

# Importamos nuestros forms y modelos
from api import forms, models, serializers, constants, pagination, extractor
# Importamos el decorator
from rest_framework.decorators import api_view, permission_classes
# Importamos los permisos
from rest_framework.permissions import AllowAny, IsAuthenticated
#Importamos la clase Group
from django.contrib.auth.models import Group
#Importamos nuestro permiso
from api.permissions import IsAdmin, IsUser
#importamos las transacciones
from django.db import transaction, IntegrityError


# Create your views here.

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
    # Chequear que no sea anónimo
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # Extraemos el query param, ponemos None como default
    query = request.GET.get('q', None)
    # Extraemos los query de paginación, y si hay un error devolvemos eso
    page, page_size, err = extractor.extract_paging_from_request(
        request=request)
    if err != None:
        return err

    # Si hay query, agregamos el filtro, sino usa todos
    if query != None:
        # Hacemos icontains sobre el username, y ordenamos por id, el "-" indica que es descendiente
        queryset = models.User.objects.filter(
            username__icontains=query).order_by('-id')
    else:
        # Definimos el set como todos los usuarios
        queryset = models.User.objects.all().order_by('-id')

    # Usamos un try catch por si la página está vacía
    try:
        # Convertimos a Paginator
        query_paginator = Paginator(queryset, page_size)
        # Nos quedamos con la página que queremos
        query_data = query_paginator.page(page)
        # Serializamos a los usuarios
        serializer = serializers.UserSerializer(query_data, many=True)
        # Agregamos a los usuarios a la respuesta
        resp = Response(serializer.data)
        # Agregamos headers de paginación a la respuesta
        resp = pagination.add_paging_to_response(
            request, resp, query_data, page, query_paginator.num_pages)
        return resp
    except EmptyPage:
        return Response(status=status.HTTP_404_NOT_FOUND)

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
        # Hacemos que no esté activo en vez de borrado físico
        user.is_active = False
        user.save()
        #Devolvemos que no hay contenido porque lo pudimos borrar
        return Response(status=status.HTTP_204_NO_CONTENT)
    except models.User.DoesNotExist:
        #Si no existe devolvemos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST','GET'])
# @permission_classes([IsUser])
def action_transaction(request):
    if request.method == 'GET':
        return get_transaction(request)
    else:
        return create_transaction(request)

def get_transaction(request):
    page, page_size, err = extractor.extract_paging_from_request(
        request = request)
    if err != None:
        return err

    start,end,other = extractor.extract_limits_from_request(request)
    queryset = models.Transaction.objects.filter(
        Q(origen=request.user) | Q(destino=request.user),
        fecha_realizada__range=(start,end))
    transactions = serializers.TransactionSerializer(queryset, many=True).data

    try:
        query_paginator = Paginator(queryset, page_size)
        query_data = query_paginator.page(page)
        serializer = serializers.TransactionSerializer(query_data, many = True)
        resp = Response(serializer.data)
        resp= pagination.add_paging_to_response(request, resp,
        query_data, page, query_paginator.num_pages)
        return resp
    except EmptyPage:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # return Response(transactions, status= status.HTTP_200_OK)


def create_transaction(request):
    #Creamos el form
    form = forms.CreateTransactionForm(request.POST)
    #Vemos si es valido
    if form.is_valid():
        #Obteniendo el usuario destino y la cantidad
        destino = models.User.objects.get(id=form.cleaned_data['destino'])
        cantidad = form.cleaned_data['cantidad']
        #Usamos un bloque transaccional para evitar problemas
        try:
            with transaction.atomic():
                #Vemos que tenga plata suficiente
                if cantidad > request.user.account.balance:
                    return Response({"error":"Saldo insuficiente"}, status= status.HTTP_400_BAD_REQUEST)
                #Creamos la transaccion
                tx = models.Transaction(origen = request.user, destino = destino, cantidad = cantidad)
                #Actualizamos los balances
                request.user.account.balance -= cantidad
                destino.account.balance += cantidad
                #Guardamos los cambios
                tx.save()
                request.user.account.save()
                destino.account.save()
                #Nuestra respuesta             
                return Response(serializers.TransactionSerializer(tx, many=False).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "Error transfiriendo fondos"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

