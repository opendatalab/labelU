from fastapi import status

from labelu.internal.common.error_code import ErrorCode, LabelUException


def assert_task_access(task, current_user) -> None:
    """Ensure current_user may access the given task's data.

    Access is granted to the task owner or any of its collaborators. Any other
    authenticated user is rejected with 403, closing IDOR/BOLA on task-scoped
    resources (samples, pre-annotations, exports, ...).
    """
    collaborator_ids = {c.id for c in task.collaborators}
    if task.created_by != current_user.id and current_user.id not in collaborator_ids:
        raise LabelUException(
            code=ErrorCode.CODE_30001_NO_PERMISSION,
            status_code=status.HTTP_403_FORBIDDEN,
        )
