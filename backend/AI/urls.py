from django.urls import path
from . import views

urlpatterns = [
    path('deepseek/', views.deepseek_chat, name='deepseek_chat'),
    path('recognize-image/', views.recognize_image, name='recognize_image'),
    path('train-models/', views.TrainModelsView.as_view(), name='train-models'),
    path('predict-length/', views.PredictLengthView.as_view(), name='predict-length'),
    path('species/', views.SpeciesListView.as_view(), name='species-list'),
    path('model-status/', views.ModelStatusView.as_view(), name='model-status'),
    path('load-local-model/', views.LoadLocalModelView.as_view(), name='load-local-model'),
]