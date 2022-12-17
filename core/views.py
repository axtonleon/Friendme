from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile,Posts,LikePost,FollowerCount,Messages
from itertools import chain


# Create your views here.
@login_required(login_url='login')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    all_profiles = Profile.objects.all()

    user_following_list = []
    user_not_following_list = []
    feed = []

    user_following = FollowerCount.objects.filter(follower=request.user.username)


    for users in user_following:
        user_following_list.append(users.user)
    user_following_list.append(user_profile.user.username)
    for username in user_following_list:
        feed_lists = Posts.objects.filter(user=username)
        feed.append(feed_lists)

    for user in all_profiles:
        if user.user == user_profile.user.username:
            print(user_profile.user.username)
            pass
        elif user.user in user_following_list:  
            pass
        else:   
            not_following_o = User.objects.get(username=user)
            not_following = Profile.objects.filter(user=not_following_o.id)
            user_not_following_list.append(not_following)
    not_following_list = list(chain(*user_not_following_list))


    feed_list = list(chain(*feed))
    posts = Posts.objects.all()

    return render(request, 'index.html', {'user_profile': user_profile, "posts": feed_list, 'not_following': not_following_list})

def signup(request):
    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']
        confirmepassword = request.POST['Confirm_Password']
        email = request.POST['Email']

        if password == confirmepassword:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already exists")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username already exists")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email ,password=password)
                user.save()
                
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username,)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Passwords Do not match')
            return redirect('signup')
    else:
        return render(request,'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username or password is incorrect')
            return redirect('login')
    else:
        return render(request,'login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required(login_url='login')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['Location']
            
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location

            user_profile.save()

        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['Location']
            
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location

            user_profile.save()

        return redirect('settings')
            
    return render(request,'settings.html', {'user_profile': user_profile})

@login_required(login_url='login')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        

        new_post = Posts.objects.create(user=user, caption=caption, image=image)
        new_post.save()

        return redirect('/')


        
    else:
        return render(request,'index.html')


@login_required(login_url='login')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Posts.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(username=username, post_id=post_id).first()

    if like_filter is None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')

    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')

@login_required(login_url='login')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Posts.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowerCount.objects.filter(follower=follower, user=user).first():
        button_text = 'unfollow'
    else:
        button_text = 'follow'

    user_followers = len(FollowerCount.objects.filter(user=pk))
    user_followings = len(FollowerCount.objects.filter(follower=pk))


    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_followings': user_followings,

    }
    return render(request,'profile.html', context )
    

@login_required(login_url='login')
def messages(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    user_following = FollowerCount.objects.filter(follower=request.user.username)
    list_of_following = []
    follower_profiles = []
    for users in user_following:
        list_of_following.append(users.user)
    for users in list_of_following:
        users_object = User.objects.get(username=users)
        follower_profile = Profile.objects.filter(user=users_object)
        follower_profiles.append(follower_profile)
    m_lists = list(chain(*follower_profiles))
 
    return render(request, 'Messages.html', {'user_profile': user_profile, 'messsagers': m_lists})

@login_required(login_url='login')
def text(request, pk):
    
    user_object = User.objects.get(username=request.user.username)
    messager_object = User.objects.get(username=pk)
    messager_profile = Profile.objects.get(user=messager_object)
    user_profile = Profile.objects.get(user=user_object)
    chat_view = Messages.objects.filter(messager=pk, user=request.user.username) | Messages.objects.filter(messager=request.user.username, user=pk)
        

    

    return render(request, 'text.html', {'user_profile': user_profile, 'messager_profile': messager_profile, 'messager_object': messager_object, 'user_object':user_object, 'messages1':chat_view})

@login_required(login_url='login')
def send_text(request): 
    print('working.....')
    if request.method == 'POST':
        messager = request.POST['messager']
        user = request.user.username
        
        message = request.POST['message']
        print(message,user,messager)
        new_message = Messages.objects.create(user=user, messager=messager, message=message)
        new_message.save()
        print(message,user,messager)
        return redirect('text/'+messager)


    else:
        return redirect('text')


@login_required(login_url='login')
def Search(request, ):

    if request.method == 'POST':
        search = request.POST['Search']
        profiles_object = User.objects.filter(username__icontains=search)
        username_profile = []
        username_profile_list = []
        for profile in profiles_object:
            username_profile.append(profile.id)

        
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
            username_profile_list = list(chain(*username_profile_list))
        

    return render(request,'Search.html', {'username_profile_list': username_profile_list, 'search': search})



@login_required(login_url='login')
def follow(request):
    if request.method == 'POST':
        follower =request.POST['follower']
        user = request.POST['user']

        if FollowerCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowerCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowerCount.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('/profile/'+user)

    else:
        return redirect('/')

    