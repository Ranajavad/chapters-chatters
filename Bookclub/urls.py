from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # 🏠 Homepage & Auth
    path("", views.homepage, name="homepage"),
    path("homepage/", views.homepage, name="homepage"),
    path("register/", views.register, name="register"),
    path("log_in/", views.log_in, name="log_in"),
    path("logout/", LogoutView.as_view(next_page='homepage'), name='logout'),

    # 📄 Main Dashboard
    path("mainpage/", views.mainpage, name="mainpage"),
    path("mainpage/groups/", views.groups, name="groups"),
    path("mainpage/chatbot/", views.chatbot, name="chatbot"),
    path("mainpage/chatbot/getResponse", views.getResponse, name="getResponse"),

    # 📚 Book Management
    path("books/add/", views.add_book, name="add_book"),
    path("bookvote/", views.bookvote, name="bookvote"),
    path("bookvote/suggest/", views.suggest_book, name="suggest_book"),
    path("vote/suggestion/<int:suggestion_id>/", views.vote_suggestion, name="vote_suggestion"),
    path("delete_suggestion/<int:suggestion_id>/", views.delete_suggestion, name="delete_suggestion"),

    # ✍️ Reviews
    path("reviews/", views.reviews, name="reviews"),
    path("reviews/select/", views.choose_book_to_review, name="choose_book_to_review"),
    path("reviews/write/<int:book_id>/", views.write_review, name="write_review"),
    path("reviews/delete/<int:review_id>/", views.delete_review, name="delete_review"),

    # 🗓️ Schedule & Polls
    path("schedule/", views.schedule, name="schedule"),
    path("group/<int:group_id>/add_meeting/", views.create_schedule, name='create_schedule'),
    path("schedule/<int:schedule_id>/delete/", views.delete_schedule, name='delete_schedule'),
    path("group/<int:group_id>/add_poll_option/", views.add_poll_option, name='add_poll_option'),
    path("poll_option/<int:option_id>/delete/", views.delete_poll_option, name='delete_poll_option'),
    path("poll/vote/<int:option_id>/", views.vote_poll_option, name='vote_poll_option'),
    path("poll/unvote/<int:option_id>/", views.unvote_poll_option, name='unvote_poll_option'),

    # 👥 Group Management
    path('send_invitation/', views.send_invitation, name='send_invitation'),
    path('accept_invitation/<uuid:invite_code>/', views.accept_invitation, name='accept_invitation'),
    path('decline_invitation/<uuid:invite_code>/', views.decline_invitation, name='decline_invitation'),
    path('groups/<int:group_id>/edit-current-read/', views.update_current_read, name='update_current_read'),
    path('groups/<int:group_id>/edit/', views.edit_group, name='edit_group'),
    path('groups/<int:group_id>/delete/', views.delete_group, name='delete_group'),

    # 💬 Discussions
    path('discussions', views.discussions_page, name='discussions_page'),
    path('discussions/<int:post_id>/', views.discussion_detail, name='discussion_detail'),
    path('<int:post_id>/like/', views.like_post, name='like_post'),
    path('<int:post_id>/dislike/', views.dislike_post, name='dislike_post'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
]
