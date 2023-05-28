from django.contrib import admin
from django.urls import path
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.home,name = 'home_page'),
    path('about/',TemplateView.as_view(template_name = 'quiz_app/about.html'),name = 'about'),
    
    path('user/login', views.LoginView.as_view(),name = 'user_login'),
    path('user/logout', views.logout_user,name = 'logout_user'),
    path('user/registration', views.RegistrationView.as_view(),name = 'user_registration'),
    path('forgot_password/',views.forgot_password,name = 'forgot_password'),
    path('user/user_profile', views.user_profile,name = 'user_profile'),
    
    path('start_quiz/pre/',views.start_pre_quiz,name = 'start_pre_quiz'),
    path('fetch_questions/<int:pk>/',views.fetch_pre_questions,name = 'fetch_questions'),
    path('fetch_post_questions/<int:pk>/',views.fetch_post_questions,name = 'fetch_post_questions'),
    path('start_quiz/post/',views.start_post_quiz,name = 'start_post_quiz'),
    path('checkAns/<int:pk>/<str:ans>/<str:q_type>/',views.checkAns,name = 'check__Ans'),
    
    path('all_done/<str:re_type>',views.alldone,name = 'all_done'),
    path('show_video/<str:cat_name>/',views.show_video,name = 'show_video'),

    path('show_my_graph/',views.show_my_graph,name = 'show_my_graph'),
    path('render_graph/<str:user_name>/',views.render_graph,name = 'render_graph'),
    
    
    path('show_all_quetion/',views.show_all_quetion,name = 'show_all_quetion'),
    path('ppt_pdf_video_seen/<int:pk>/<str:re_type>/',views.ppt_pdf_video_seen,name = 'ppt_pdf_video_seen'),
    
    path('feed_back_form/',views.feed_back_form,name = 'feed_back_form'),
    path('user_query/',views.user_query,name = 'user_query'),

    path('admin_graph_show/<str:re_type>/',views.admin_graph_show,name = 'admin_graph_show'),
    
    path('generate_marksheet/<str:re_type>/',views.generate_marksheet,name = 'generate_marksheet'),
    path('render_an_graph/<str:re_type>/<str:cat_name>/',views.render_an_graph,name = 'render_an_graph'),
]