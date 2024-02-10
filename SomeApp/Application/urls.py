from django.urls import path
from Application import views

urlpatterns = [
    path("execute-job", views.ExecuteJobs.as_view(), name="execute-job"),
    path("list-jobs", views.ListJobs.as_view(), name="list-jobs"),
    path("delete-job", views.DeleteJob.as_view(), name="delete-job")
]
