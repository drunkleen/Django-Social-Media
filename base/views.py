from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from base.models import Room, Topic, Message, User
from base.forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.


# Login User
def loginPage(request):
    page = "login"

    # if user is logged in, shouldn't able to login again
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        # try to find user in database
        try:
            user = User.objects.get(email=email)
        # if user is not registered
        except:
            messages.error(request, "Invalid login credentials")

        user = authenticate(request=request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

    context = {"page": page}
    return render(request, "base/login_register.html", context)


# Logout user
def logoutUser(request):
    logout(request)
    return redirect("home")


# Register user
def register(request):
    # create form object for user registration
    form = MyUserCreationForm()

    # register new user
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.username = user.username.lower()
            user = form.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occurred during registration")

    context = {"form": form}
    return render(request, "base/login_register.html", context)


# main page
def home(request):
    # looks if "q" exists, it search in all sections to find matches
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)
        | Q(room_name__icontains=q)
        | Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()

    recent_activities = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    ).order_by("-create_time")[0:4]

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "recent_activities": recent_activities,
    }

    return render(request, "base/home.html", context)


# room page
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by("create_time")
    participants = room.participants.all()

    # create new comment and add it to database
    if request.method == "POST":
        if request.user.is_authenticated:
            Message.objects.create(
                user=request.user,
                room=room,
                body=request.POST.get("body"),
            )
            if room.host != request.user:
                room.participants.add(request.user)
            return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }

    return render(request, "base/room.html", context)


# topic page
def topics(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)

    return render(request, "base/topics.html", {"topics": topics})


def activities(request):
    activities = Message.objects.filter().order_by("-create_time")

    return render(request, "base/activities.html", {"activities": activities})


@login_required(login_url="/login")
def userProfile(request, pk):
    user = User.objects.get(username=pk)
    rooms = user.room_set.all()
    recent_activities = user.message_set.all().order_by("-create_time")
    topics = Topic.objects.all()

    context = {
        "user": user,
        "rooms": rooms,
        "recent_activities": recent_activities,
        "topics": topics,
    }
    return render(request, "base/user_profile.html", context)


# user settings page
@login_required(login_url="login")
def userSettings(request):
    user = request.user

    # create object for user settings
    form = UserForm(instance=user)

    # update user credentials
    if request.method == "POST":
        # request.FILES.
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.username)

    # user validation and render setting page
    try:
        query = User.objects.filter(username=user.username).first()
        if query == user:
            context = {"form": form}
            return render(request, "base/user_settings.html", context)
        else:
            return HttpResponse("You are not allowed to edit this room")
    except:
        messages.error(request, "Error creating user settings")


@login_required(login_url="/login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        print("\n\n\n\n\n\n", created, "\n\n\n\n\n\n")
        if created:
            Room.objects.create(
                host=request.user,
                topic=topic,
                room_name=request.POST.get("room_name"),
                description=request.POST.get("description"),
            )
        else:
            Room.objects.create(
                host=request.user,
                topic=topic,
                room_name=request.POST.get("room_name"),
                description=request.POST.get("description"),
            )

        return redirect("home")

    context = {"form": form, "topics": topics}

    return render(request, "base/room_form.html", context)


@login_required(login_url="/login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    room_update = True
    if request.user != room.host:
        return HttpResponse("You are not allowed to edit this room")

    else:
        form = RoomForm(instance=room)

        if request.method == "POST":
            room.description = request.POST.get("description")

            room.save()

            return redirect("home")

    context = {"form": form, "room": room, "room_update": room_update}
    return render(request, "base/room_form.html", context)


@login_required(login_url="/login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed to delete this room")

    if request.method == "POST":
        room.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj": room})


@login_required(login_url="/login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed to delete this Message")

    if request.method == "POST":
        message.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj": message})
