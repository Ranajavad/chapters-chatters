from django.shortcuts import render,redirect, get_object_or_404
from django.utils.timezone import now
from . models import Book, Suggestion, Vote, Schedule, BookClubGroup, Invitation,Review,DiscussionPost,Comment, MeetingPoll, MeetingPollOption, MeetingPollVote
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse,HttpResponseForbidden
from .forms import ReviewForm, CommentForm, InvitationForm,DiscussionPost,CommentForm, ScheduleForm, SuggestionForm, DiscussionPostForm, MeetingPollOptionForm
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from .forms import CustomUserCreationForm,BookClubGroupForm, EditBookClubGroupForm 
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import make_aware, is_naive
from django.db.models import Count
from collections import defaultdict
from chatterbot import ChatBot 

def homepage(request):
    if request.user.is_authenticated:
        return render(request, 'Bookclub/homepage.html') 
    else:
        register_form = CustomUserCreationForm()
        login_form = AuthenticationForm()
        context = {
            'register_form': register_form,
            'login_form': login_form,
        }
        return render(request, 'Bookclub/homepage.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('mainpage')
    else:
        form = CustomUserCreationForm()
    return render(request, 'Bookclub/login_register/register.html', {'form': form})


def discussion_list(request):
    posts = DiscussionPost.objects.all().order_by('-created_at')
    return render(request, 'Bookclub/Discussions/discussion_list.html', {'posts': posts})

@login_required
def new_post(request):
    if request.method == 'POST':
        form = DiscussionPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('discussion_list')
    else:
        form = DiscussionPostForm()
    return render(request, 'Bookclub/Discussions/new_post.html', {'form': form})

def discussion_detail(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)
    comments = post.comments.all()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('discussion_detail', post_id=post_id)
    else:
        comment_form = CommentForm()
    return render(request, 'Bookclub/Discussions/discussion_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def like_post(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)
    post.likes.add(request.user)
    post.dislikes.remove(request.user)
    return redirect('discussions_page')

@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)
    post.dislikes.add(request.user)
    post.likes.remove(request.user)
    return redirect('discussions_page')


def log_in(request):
    if request.user.is_authenticated:
        return redirect('mainpage')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('mainpage')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'Bookclub/login_register/log_in.html', {'form': form})

def mainpage(request):
    if not request.user.is_authenticated:
        return redirect('homepage')

    my_groups = BookClubGroup.objects.filter(members=request.user)
    form = None
    invitations = Invitation.objects.filter(
        invited_user_email=request.user.email,
        accepted_at__isnull=True
    )
  
    if request.method == 'POST':
        form = BookClubGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            group.members.add(request.user)
            form = BookClubGroupForm()  
    else:
        form = BookClubGroupForm()
   
    context = {
        'my_groups': my_groups,
        'form': form,
        'invitations':invitations,
        
    }
    return render(request, 'Bookclub/Mainpage/mainpage.html', context)

@login_required
def add_comment(request, post_id):
    post = DiscussionPost.objects.get(id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
    return redirect('discussions_page')


@login_required
def discussions_page(request):
    posts = DiscussionPost.objects.all().order_by('-created_at')

    
    if request.method == 'POST' and 'new_post' in request.POST:
        post_form = DiscussionPostForm(request.POST)
        if post_form.is_valid():
            new_post = post_form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('discussions_page')
    else:
        post_form = DiscussionPostForm()

    
    comment_forms = {post.id: CommentForm() for post in posts}

    return render(request, 'Bookclub/Discussions/discussions_page.html', {
        'posts': posts,
        'post_form': post_form,
        'comment_forms': comment_forms,
    })

def groups(request):
    my_groups = BookClubGroup.objects.filter(members=request.user).prefetch_related('members')
    context = {
        'my_groups': my_groups,
    }
    return render(request,'Bookclub/Groups/groups.html',context)

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, "Book added successfully.")
            return redirect('mainpage')
    else:
        form = BookForm()
    return render(request, 'Bookclub/Book/add_book.html', {'form': form})


@login_required
def choose_book_to_review(request):
    
    user_groups = BookClubGroup.objects.filter(members=request.user)

    
    voted_suggestions = Suggestion.objects.filter(
        group__in=user_groups,
        votes__isnull=False  
    ).distinct()

    
    books = Book.objects.filter(
        group__in=user_groups,
        title__in=voted_suggestions.values_list('title', flat=True),
        author__in=voted_suggestions.values_list('author', flat=True)
    ).distinct()

    return render(request, 'Bookclub/Book/choose_book.html', {'books': books})




@login_required
def bookvote(request):
    user = request.user
    user_groups = BookClubGroup.objects.filter(members=user)

    
    selected_group_id = request.GET.get('group')
    if selected_group_id:
        selected_group = get_object_or_404(BookClubGroup, id=selected_group_id, members=user)
    else:
        selected_group = user_groups.first()

    
    suggestions = Suggestion.objects.filter(group=selected_group)
    voted_suggestions = Vote.objects.filter(user=user).values_list('suggestion_id', flat=True)

    context = {
        'suggestions': suggestions,
        'voted_suggestions': voted_suggestions,
        'user_groups': user_groups,
        'selected_group_id': int(selected_group_id) if selected_group_id else selected_group.id,
        'selected_group': selected_group,
    }
    return render(request, 'Bookclub/Book/bookvote.html', context)




@login_required
def vote_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion, pk=suggestion_id, group__members=request.user)


    if request.method == 'POST':
        
        existing_vote = Vote.objects.filter(user=request.user, suggestion=suggestion)
        if existing_vote.exists():
            existing_vote.delete()
        else:
            Vote.objects.create(user=request.user, suggestion=suggestion)

        
        group = suggestion.group
        from Bookclub.models import Book  
        Book.objects.filter(group=group, is_current_read=True).update(is_current_read=False)

        book, _ = Book.objects.get_or_create(
            title=suggestion.title,
            author=suggestion.author,
            group=group
        )
        book.is_current_read = True
        book.save()

        group.save()

    return HttpResponseRedirect(reverse('bookvote'))



@login_required
def suggest_book(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST, request.FILES, user=request.user)  
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.suggested_by = request.user
            suggestion.save()
            messages.success(request, "Your book suggestion has been submitted!")
            return redirect('bookvote')
    else:
        form = SuggestionForm(user=request.user)

    return render(request, 'Bookclub/Books/suggest_book.html', {'form': form})

    
@login_required
def reviews(request):
    reviews = Review.objects.filter(book__group__members=request.user).order_by('-date_posted')
    context = {
        'reviews': reviews,
        'form': ReviewForm(),  
    }
    return render(request, 'Bookclub/Book/reviews.html', context)

@login_required
def write_review(request, book_id):
    book = get_object_or_404(Book, pk=book_id, group__members=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('reviews')
    else:
        form = ReviewForm()  

    context = {
        'form': form,
        'book': book,
    }
    return render(request, 'Bookclub/Books/write_review.html', context)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        messages.error(request, "You are not authorized to delete this review.")
        return redirect('reviews')

    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted successfully.")
        return redirect('reviews')
   
@login_required
def schedule(request):
    user_groups = BookClubGroup.objects.filter(members=request.user)
    selected_group_id = request.GET.get('group')

    active_group = (
        user_groups.filter(id=selected_group_id).first()
        if selected_group_id else user_groups.first()
    )
    creator_group = user_groups.filter(owner=request.user).first()
    schedule_form = ScheduleForm(user=request.user) if creator_group else None

    upcoming_meetings = Schedule.objects.filter(group__in=user_groups).order_by('date', 'time')

    poll = None
    poll_options = []
    poll_form = None
    most_voted_option_id = None

    if active_group:
        poll = MeetingPoll.objects.filter(group=active_group).first()

        if poll:
            poll_options = poll.options.prefetch_related('votes')

            
            for option in poll_options:
                option.user_voted = option.votes.filter(user=request.user).exists()

            
            most_voted = max(poll_options, key=lambda opt: opt.votes.count(), default=None)
            if most_voted:
                most_voted_option_id = most_voted.id

        
        if active_group.owner == request.user:
            poll_form = MeetingPollOptionForm()

    context = {
        'user_groups': user_groups,
        'selected_group_id': int(selected_group_id) if selected_group_id else (active_group.id if active_group else None),
        'creator_group': creator_group,
        'schedule_form': schedule_form,
        'active_group': active_group,
        'poll': poll,
        'poll_options': poll_options,
        'poll_form': poll_form,
        'most_voted_option_id': most_voted_option_id,
        'upcoming_meetings': upcoming_meetings,
    }

    return render(request, 'Bookclub/Schedule/schedule.html', context)
 


@login_required
def create_schedule(request, group_id):
    group = get_object_or_404(BookClubGroup, id=group_id)

    if group.owner != request.user:
        return HttpResponseForbidden("Only the group creator can schedule meetings.")

    if request.method == 'POST':
        form = ScheduleForm(request.POST, user=request.user)  
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.group = group 
            schedule.save()
            messages.success(request, "Meeting created successfully.")
            return redirect('schedule')
        else:
            messages.error(request, "There was an error with the form.")
    else:
        form = ScheduleForm(user=request.user)  

    user_groups = BookClubGroup.objects.filter(members=request.user)
    upcoming_meetings = Schedule.objects.filter(group__in=user_groups).order_by('date', 'time')

    context = {
        'schedule_form': form,
        'creator_group': group,
        'upcoming_meetings': upcoming_meetings,
        'active_polls': active_polls,
    }
    return render(request, 'Bookclub/schedule.html', context)

@login_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    if request.user != schedule.group.owner:
        messages.error(request, "Only the group owner can delete this meeting.")
        return redirect('schedule')

    schedule.delete()
    messages.success(request, "Meeting deleted.")
    return redirect('schedule')

def chatbot(request):
    return render(request, "Bookclub/Chatbot/chatbot.html")

bot = ChatBot('chatbot',read_only=False,
              logic_adapters=[
                  {
                     "import_path":'chatterbot.logic.BestMatch',
                     
                  }
                  ])
list_to_train = [
    "hello",
    "Hi there! Welcome to Chapters & Chatters. How can I help you today?",
    
    "what's your name?",
    "I'm the Chapters & Chatters chatbot, created to help you with your book club experience.",

    "who made you?",
    "I was created by Rana as part of the Chapters & Chatters platform.",

    "what is the name of the book club?",
    "The name of the book club is Chapters & Chatters.",

    "how do I join a book club?",
    "You can join a book club by accepting an invitation sent to your email or username by the group owner.",

    "how can I create a new book club?",
    "Go to the main page and use the 'Create Group' form. You must be logged in to create a group.",

    "how do I suggest a book?",
    "Visit the 'Book Vote' page and fill out the suggestion form with your book title and author.",

    "how do I vote for a book?",
    "On the 'Book Vote' page, click the vote button next to the book you'd like to read.",

    "what happens when everyone has voted?",
    "Once all group members vote, the book with the most votes becomes the current read!",

    "how can I add a meeting?",
    "Only group owners can add meetings. Go to the 'Schedule' page and fill out the meeting form.",

    "how do I vote for a meeting date?",
    "On the 'Schedule' page, find your group's proposed dates and vote on any that work for you.",

    "can I unvote a meeting date?",
    "Yes! If you’ve already voted, just click the 'Unvote' button next to that date option.",

    "how can I write a book review?",
    "Go to the 'Reviews' section and click on 'Write Review' next to the book you'd like to review.",

    "can I comment on a discussion post?",
    "Yes! Just go to the 'Discussions' page and add your comment under any post you like.",

    "what is the goal of this book club?",
    "Chapters & Chatters brings book lovers together to read, discuss, and share ideas through fun and thoughtful interaction.",

    "can I leave a group?",
    "Currently, leaving a group is handled by the group admin. You can message them to remove you.",

    "how do I invite others to my group?",
    "If you're a group owner, go to the main page and use the invite form by entering their email or username.",

    "what are the top rated books?",
    "Here are some of the top-rated books in our club:\n- 'The Midnight Library' by Matt Haig ⭐️⭐️⭐️⭐️⭐️\n- 'Educated' by Tara Westover ⭐️⭐️⭐️⭐️½\n- 'Where the Crawdads Sing' by Delia Owens ⭐️⭐️⭐️⭐️⭐️",

    "give me the best reviewed books",
    "These are some of the most loved books in Chapters & Chatters:\n- 'The Night Circus' 🎪\n- 'Atomic Habits' 📘\n- 'The Book Thief' 📖",

    "which book has the most reviews?",
    "'The Seven Husbands of Evelyn Hugo' currently has the most reviews in our community!",
    
    "can you recommend a book?",
    "Sure! If you like mystery, try 'The Silent Patient'. If you love historical fiction, go for 'The Nightingale'.",

]


trainer = ListTrainer(bot)

trainer.train(list_to_train)

def getResponse(request):
    userMessage=request.GET.get('userMessage')
    chatResponse=str(bot.get_response(userMessage))
    return HttpResponse(chatResponse)



@login_required
def send_invitation(request):
    if request.method == 'POST':
        form = InvitationForm(request.POST, user=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']
            group = form.cleaned_data['group']

            
            existing_invitation = Invitation.objects.filter(group=group, invited_user_email=email).first()
            if existing_invitation:
                messages.warning(request, f"An invitation has already been sent to {email} for {group.name}.")
                return redirect('mainpage')

            
            invitation = Invitation(
                group=group,
                invited_user_email=email,
                invited_by=request.user,
            )
            invitation.save()

            
            subject = f"Invitation to join {group.name} on Chapters & Chatters"
            message = f"Please join our Book Club! Click here to accept: http://yourdomain.com/accept_invitation/{invitation.invite_code}"
            recipient_list = [email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)


            messages.success(request, f"Invitation sent to {email}.")
            return redirect('mainpage')

        else:
            user_groups = BookClubGroup.objects.filter(members=request.user)
            return render(request, 'Bookclub/Mainpage/mainpage.html', {'form': form, 'user_groups': user_groups})

    else:
        form = InvitationForm(user=request.user)
        user_groups = BookClubGroup.objects.filter(members=request.user)
        return render(request, 'Bookclub/Mainpage/mainpage.html', {'form': form, 'user_groups': user_groups})

              
@login_required
def accept_invitation(request, invite_code):
    invitation = get_object_or_404(Invitation, invite_code=invite_code)

    if invitation.invited_user_email != request.user.email:
        return HttpResponseForbidden("This invitation is not for your email.")

    if invitation.accepted_at is None:
        invitation.group.members.add(request.user)
        invitation.accepted_at = now()
        invitation.save()
        messages.success(request, f"You have joined the group {invitation.group.name}!")
    else:
        messages.info(request, "This invitation has already been accepted.")

    return redirect('mainpage')

@login_required
def decline_invitation(request, invite_code):
    invitation = get_object_or_404(Invitation, invite_code=invite_code)

    
    if invitation.invited_user_email == request.user.email:
        invitation.delete()
        messages.info(request, "You have declined the invitation.")
    else:
        messages.warning(request, "You are not authorized to decline this invitation.")

    return redirect('mainpage')


@login_required
def delete_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion, id=suggestion_id)

    
    if suggestion.suggested_by == request.user or request.user in suggestion.group.members.all():
        suggestion.delete()
        messages.success(request, "Suggestion deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this suggestion.")

    return redirect('bookvote')  


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        messages.error(request, "You are not allowed to delete this comment.")
        return redirect('discussions_page') 

    comment.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect('discussions_page')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)

    if post.author != request.user:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect('discussions_page')

    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('discussions_page')


@login_required
def update_current_read(request, group_id):
    group = get_object_or_404(BookClubGroup, id=group_id)

    if request.user != group.owner:
        return redirect('mainpage')

    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        if book_id:
            group.current_read = get_object_or_404(Book, id=book_id)
        else:
            group.current_read = None
        group.save()
        return redirect('mainpage')

    group_books = Book.objects.filter(group=group)
    return render(request, 'Bookclub/Mainpage/edit_current_read.html', {
        'group': group,
        'books': group_books
    })

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(BookClubGroup, id=group_id)

    if group.owner != request.user:
        messages.error(request, "You don't have permission to delete this group.")
        return redirect('mainpage')

    group.delete()
    messages.success(request, "Book club deleted successfully.")
    return redirect('mainpage')

@login_required
def edit_group(request, group_id):
    group = get_object_or_404(BookClubGroup, id=group_id)

    if group.owner != request.user:
        return redirect('mainpage')

    if request.method == 'POST':
        form = EditBookClubGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('mainpage')
    else:
        form = EditBookClubGroupForm(instance=group)

    return render(request, 'Bookclub/Groups/edit_group.html', {'form': form, 'group': group})

@login_required
def add_poll_option(request, group_id):
    group = get_object_or_404(BookClubGroup, id=group_id)

    if request.user != group.owner:
        return HttpResponseForbidden("Only the group owner can create poll options.")

    poll, _ = MeetingPoll.objects.get_or_create(group=group)

    if request.method == 'POST':
        form = MeetingPollOptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.poll = poll
            option.save()
            messages.success(request, "Meeting date option added.")
            return redirect('schedule')  
    else:
        return redirect('schedule')  
@login_required
def delete_poll_option(request, option_id):
    option = get_object_or_404(MeetingPollOption, id=option_id)
    if option.poll.group.owner != request.user:
        return HttpResponseForbidden("Only the group owner can delete poll options.")
    
    option.delete()
    messages.success(request, "Poll option deleted.")
    return redirect('schedule')

@login_required
def vote_poll_option(request, option_id):
    option = get_object_or_404(MeetingPollOption, id=option_id)
    poll = option.poll
    user = request.user

  
    if MeetingPollVote.objects.filter(option=option, user=user).exists():
        messages.info(request, "You already voted for this option.")
    else:
        MeetingPollVote.objects.create(option=option, user=user)
        messages.success(request, "Vote recorded.")

    return redirect('schedule')

@login_required
def unvote_poll_option(request, option_id):
    option = get_object_or_404(MeetingPollOption, id=option_id)
    vote = MeetingPollVote.objects.filter(user=request.user, option=option).first()
    if vote:
        vote.delete()
        messages.success(request, "Vote removed.")
    else:
        messages.info(request, "You haven't voted for this option.")
    return redirect('schedule')
