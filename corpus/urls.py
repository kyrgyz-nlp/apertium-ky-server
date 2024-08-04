from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_text, name='upload_text'),
    path('text/<int:text_id>/', views.text_detail, name='text_detail'),
    path('text/<int:text_id>/process/', views.process_text, name='process_text'),
    path('batch/<int:batch_id>/check/', views.check_unknown_words, name='check_unknown_words'),
    path('batch/<int:batch_id>/update_apertium/', views.update_apertium, name='update_apertium'),
]
