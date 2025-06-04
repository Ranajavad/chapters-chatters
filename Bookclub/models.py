from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


from django.db import models
from django.conf import settings
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=255, blank=True)
    

    def __str__(self):
        return self.user.username
    
class BookClubGroup(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Group Name')
    description = models.TextField(blank=True, verbose_name='Description')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_groups', verbose_name='Owner')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='GroupMembership', related_name='book_club_groups', verbose_name='Members')
    current_read = models.ForeignKey('Book', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    is_public = models.BooleanField(default=True, verbose_name='Public Group')

    class Meta:
        verbose_name = 'Book Club Group'
        verbose_name_plural = 'Book Club Groups'
        ordering = ['name']

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    group = models.ForeignKey(BookClubGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    is_current_read=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.title} by {self.author or 'Unknown'}"



class Suggestion(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
    group = models.ForeignKey('BookClubGroup', on_delete=models.CASCADE, related_name='suggestions', null=True)
    suggested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='suggestions')
    book_cover = models.ImageField(upload_to='book_covers/', blank=True, null=True) 

    def __str__(self):
        return f"Suggestion: {self.title} by {self.author or 'Unknown'}"


class Vote(models.Model):
    """Represents a 'thumbs up' vote for a suggested book."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_votes')
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='votes')
    vote_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'suggestion')

    def __str__(self):
        return f"{self.user.username} voted for '{self.suggestion.title}'"


class DiscussionPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_posts', blank=True)

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

class Comment(models.Model):
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    """Represents a review of a book by a user, including a star rating."""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')])
    text = models.TextField(blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')  

    def __str__(self):
        return f"Review of '{self.book.title}' by {self.user.username}"


class Schedule(models.Model):
    group = models.ForeignKey('BookClubGroup', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.title} - {self.date}"
    
class Member(models.Model):
  firstname = models.CharField(max_length=255)
  lastname = models.CharField(max_length=255)
  phone = models.IntegerField(null=True)
  joined_date = models.DateField(null=True)
  slug = models.SlugField(default="", null=False)

  def __str__(self):
    return f"{self.firstname} {self.lastname}"
  
class GroupMembership(models.Model):
    group = models.ForeignKey(BookClubGroup, on_delete=models.CASCADE, verbose_name='Group')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Joined Date')
    role = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('member', 'Member'),
            ('admin', 'Admin'),
            ('moderator', 'Moderator'),
        ],
        default='member',
        verbose_name='Role'
    )

    class Meta:
        verbose_name = 'Group Membership'
        verbose_name_plural = 'Group Memberships'
        unique_together = ('group', 'user')
        ordering = ['date_joined']

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"
 

class Invitation(models.Model):
    group = models.ForeignKey(BookClubGroup, on_delete=models.CASCADE, related_name='invitations', verbose_name='Group')
    invited_user_email = models.EmailField(verbose_name='Invited Email')
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations', verbose_name='Invited By')
    invite_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Invite Code')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Sent At')
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name='Accepted At')

    class Meta:
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'
        unique_together = ('group', 'invited_user_email')
        ordering = ['sent_at']

    def __str__(self):
        return f"Invitation to {self.invited_user_email} for {self.group.name}"
    

class MeetingPoll(models.Model):
    group = models.ForeignKey('BookClubGroup', on_delete=models.CASCADE, related_name='polls')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting Poll for {self.group.name}"

class MeetingPollOption(models.Model):
    poll = models.ForeignKey(MeetingPoll, on_delete=models.CASCADE, related_name='options')
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.date} {self.time or ''}"

class MeetingPollVote(models.Model):
    option = models.ForeignKey(MeetingPollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('option', 'user') 

    def __str__(self):
        return f"{self.user} voted on {self.option}"