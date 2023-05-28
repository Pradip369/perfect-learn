from jet.dashboard import dashboard
from quiz_app.views import admin_graph,show_quiz_ml_analysis,marks_analysis,all_students_marks
from django.urls.conf import path

# This method registers view's url
dashboard.urls.register_urls([
    path('show_quiz_graph/',admin_graph,name='admin_graph_show'),
    path('show_quiz_ml_analysis/<str:re_type>/',show_quiz_ml_analysis,name='show_quiz_ml_analysis'),
    path('marks_analysis/',marks_analysis,name='marks_analysis'),
    path('all_students_marks/',all_students_marks,name='all_students_marks'),
])