from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import RoomForm, UserForm
from .models import Room, Theme, Comment
# Create your views here.
from .serializers import RoomSerializer


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User doesnt exist')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Incorrect username or password')
    context = {'page': page}
    return render(request, 'login_register.html', context)


@login_required
def logout(request):
    django_logout(request)
    return redirect('home')


def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, form.errors)
    return render(request, 'login_register.html', {'form': form})


def profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_comments = user.comment_set.all()
    themes = Theme.objects.all()

    context = {'user': user, 'rooms': rooms, 'comments': room_comments, 'themes': themes}
    return render(request, 'profile.html', context)


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=request.user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'update_user.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    rooms = Room.objects.filter(
        Q(theme__title__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    # В функции filter(моделька__по параметру__icontains) - позволяет искать объекты,
    # даже если их писать не до конца.
    # Либо по топику, либо по имени объекта.

    themes = Theme.objects.all()[0:5]
    room_count = rooms.count()
    room_comments = Comment.objects.filter(Q(room__theme__title__icontains=q))

    context = {'rooms': rooms, 'themes': themes,
               'room_count': room_count, 'room_comments': room_comments}
    return render(request, 'home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_comments = room.comment_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        comment = Comment.objects.create(
            author=request.user,
            room=room,
            text=request.POST.get('text')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_comments': room_comments, 'participants': participants}
    return render(request, 'room.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    themes = Theme.objects.all()
    if request.method == 'POST':
        theme_title = request.POST.get('theme')
        theme, created = Theme.objects.get_or_create(title=theme_title)

        Room.objects.create(
            author=request.user,
            theme=theme,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

    context = {'form': form, 'themes': themes}
    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    themes = Theme.objects.all()

    if request.user != room.author:
        return HttpResponse('You are not allowed')

    if request.method == 'POST':
        theme_title = request.POST.get('theme')
        theme, created = Theme.objects.get_or_create(title=theme_title)
        room.name = request.POST.get('name')
        room.theme = theme
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'themes': themes, 'room': room}
    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.author:
        return HttpResponse('Your are not allowed here!!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj': room})


@login_required(login_url='login')
def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)

    if request.user != comment.author:
        return HttpResponse('Your are not allowed here!!!')

    if request.method == 'POST':
        comment.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj': comment})


def ThemePage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    themes = Theme.objects.filter(title__icontains=q)
    return render(request, 'themes.html', {'themes': themes})


def activityPage(request):
    room_comment = Comment.objects.all()
    return render(request, 'activity.html', {'room_comments': room_comment})


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms/',
        'GET /api/rooms/:id'
    ]
    return Response(routes)


@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)
