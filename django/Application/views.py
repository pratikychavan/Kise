from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from Application.models import VenvTracker
from Application.venv_controller import vp
from uuid import uuid4
# Create your views here.

class ExecuteJobs(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        data["task_id"] = str(uuid4())
        needed_fields = {"task_id", "params"}
        assert set(data.keys()).issubset(needed_fields), "Fields missing"
        job = vp.create_job(data)
        if job["status"] == "Created":
            return Response(data=job, status=status.HTTP_200_OK)
        return Response(data={"msg":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListJobs(APIView):
    def get(self, request, *args, **kwargs):
        return Response(data={"jobs":vp.list_jobs()}, status=status.HTTP_200_OK)

class DeleteJob(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        assert data.get("task_id") is not None, "Task ID cannot be None"
        job = vp.delete_job(data["task_id"])
        if job["status"] == "Deletion in progress":
            return Response(data=job, status=status.HTTP_200_OK)
        return Response(data={"msg":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)