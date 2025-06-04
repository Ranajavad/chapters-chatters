from django.contrib import admin
from . models import Book, MeetingPoll, MeetingPollOption, MeetingPollVote, Suggestion, Vote, DiscussionPost, Comment, Review, Schedule, BookClubGroup, Member, GroupMembership, Invitation,UserProfile


admin.site.register(Book)
admin.site.register(Suggestion)
admin.site.register(Vote)
admin.site.register(DiscussionPost)
admin.site.register(Comment)
admin.site.register(Review)
admin.site.register(Schedule)
admin.site.register(BookClubGroup)
admin.site.register(Member)
admin.site.register(GroupMembership)
admin.site.register(Invitation)
admin.site.register(UserProfile)
admin.site.register(MeetingPoll)
admin.site.register(MeetingPollOption)
admin.site.register(MeetingPollVote)
