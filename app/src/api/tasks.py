from django.utils import timezone

from words.tools import group_names
from .models import GroupingTask


# Note: In a real project this would be run in a separate worker process,
# using asynchronous task queue (e.g. Celery)
def process_grouping_task_async(grouping_task_id: int) -> None:
    """Process the uncompleted grouping task with the given ID."""
    try:
        grouping_task = GroupingTask.objects.get(
            id=grouping_task_id,
            result={},
            completed_at=None,
        )
    except GroupingTask.DoesNotExist:
        # TODO: Logging
        return

    grouping_task.result = group_names(
        names=grouping_task.input_data["names"],
        word_delimiter=grouping_task.input_data["word_delimiter"],
    )
    grouping_task.completed_at = timezone.now()
    grouping_task.save()
