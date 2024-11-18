from pathlib import Path
import random
from labelu.internal.common.config import settings
import string


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=16))


def random_username() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"

def empty_task_upload(task_id: int, input_filename: str):
    path_filename = input_filename.split("/")
    #  filename = str(uuid.uuid4())[0:8] + "-" + path_filename[-1]
    filename = path_filename[-1]
    path = "/".join(path_filename[:-1])
    # delete task 1 folder
    attachment_relative_base_dir = Path(settings.UPLOAD_DIR).joinpath(
        str(task_id), path
    )
    attachment_relative_path = str(attachment_relative_base_dir.joinpath(filename))

    attachment_full_path = Path(settings.MEDIA_ROOT).joinpath(
        attachment_relative_path
    )
    
    # remove folder
    if attachment_full_path.exists():
        attachment_full_path.unlink()
    
    return attachment_full_path