from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import GroupingTask
from .serializers import (
    GroupingTaskCreateSerializer,
    GroupingTaskIdentitySerializer,
    GroupingTaskMoveNameSerializer,
    GroupingTaskSerializer,
)
from .tasks import process_grouping_task_async


class GroupingTaskViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """The ViewSet for creating, listing, retrieving and updating grouping tasks.

    Grouping tasks can be updated by moving names between different groups.
    For details, see the move_name method for a specific instance.
    """

    queryset = GroupingTask.objects.all()
    serializer_classes = {
        # For a list use a simple representation with a resource URL
        "list": GroupingTaskIdentitySerializer,
        "create": GroupingTaskCreateSerializer,
        "retrieve": GroupingTaskSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, GroupingTaskSerializer)

    def perform_create(self, serializer):
        super().perform_create(serializer)

        # Schedule processing of the created grouping task
        # Note: In a real project this would be run as an asynchronous task
        process_grouping_task_async(grouping_task_id=serializer.instance.id)

    @extend_schema(
        request=GroupingTaskMoveNameSerializer,
        responses={200: GroupingTaskSerializer},
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=str,
                description="ID of the GroupingTask",
            ),
        ],
        examples=[
            OpenApiExample(
                "Move the name 'example' from 'group1' to 'group2'.",
                value={
                    "name": "example",
                    "source_group": "group1",
                    "target_group": "group2",
                },
                request_only=True,
            )
        ],
        description="Move a name from one group to another.",
    )
    @action(detail=True, methods=["patch"], url_path="move-name")
    def move_name(self, request, pk=None):
        """Move the given name between two groups.

        If the target group does not exist, it will be created.
        Orphaned (empty) groups are deleted.
        """
        grouping_task = self.get_object()
        request_serializer = GroupingTaskMoveNameSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        name = request_serializer.validated_data["name"]
        source_group_name = request_serializer.validated_data["source_group"]
        target_group_name = request_serializer.validated_data["target_group"]

        try:
            source_group = grouping_task.result[source_group_name]
            # Remove the name from the current group
            source_group.remove(name)
        except KeyError:
            return Response(
                {"source_group": [f"Group not found: {source_group_name}."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError:
            return Response(
                {"name": [f"'{name}' not found in group '{source_group_name}'."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not source_group:
            # Remove the orphaned (empty) group
            del grouping_task.result[source_group_name]

        # Add the name to the new group
        if target_group_name not in grouping_task.result:
            grouping_task.result[target_group_name] = []
        grouping_task.result[target_group_name].append(name)

        grouping_task.save()

        # Return full representation of the updated resource
        response_serializer = GroupingTaskSerializer(
            grouping_task, context={"request": request}
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)
