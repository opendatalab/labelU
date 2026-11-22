import json

from sqlalchemy.orm import Session

from labelu.internal.adapter.persistence import crud_sample
from labelu.internal.common.converter import converter
from labelu.internal.domain.models.sample import TaskSample


def test_get_by_ids_chunks_large_batches_and_scopes_by_task(db: Session):
    total = 1205
    task1_samples = [
        TaskSample(
            inner_id=i + 1,
            task_id=101,
            created_by=1,
            updated_by=1,
            data='{"result": "{}"}',
            state="DONE",
        )
        for i in range(total)
    ]
    other_task_sample = TaskSample(
        inner_id=1,
        task_id=102,
        created_by=1,
        updated_by=1,
        data='{"result": "{}"}',
        state="DONE",
    )
    db.bulk_save_objects(task1_samples + [other_task_sample], return_defaults=True)
    db.commit()

    all_ids = [s.id for s in task1_samples] + [other_task_sample.id, task1_samples[0].id]
    fetched = crud_sample.get_by_ids(db=db, sample_ids=all_ids, task_id=101)

    assert len(fetched) == total
    assert [s.id for s in fetched] == sorted(s.id for s in task1_samples)

    crud_sample.delete(db=db, sample_ids=[s.id for s in task1_samples])
    db.commit()
    assert crud_sample.get_by_ids(db=db, sample_ids=[s.id for s in task1_samples], task_id=101) == []


def test_convert_to_json_preserves_samples_with_empty_result(tmp_path):
    input_data = [
        {
            "id": 1,
            "state": "DONE",
            "data": json.dumps({"result": json.dumps({"width": 10, "height": 10})}),
            "file": {"filename": "a.png", "url": "/a.png"},
        },
        {
            "id": 2,
            "state": "NEW",
            "data": json.dumps({"result": ""}),
            "file": {"filename": "b.png", "url": "/b.png"},
        },
    ]

    out_path = converter.convert(
        config={"tools": []},
        input_data=input_data,
        out_data_dir=tmp_path,
        out_data_file_name_prefix="task",
        format="JSON",
    )
    exported = json.loads(out_path.read_text(encoding="utf-8"))
    assert [item["id"] for item in exported] == [1, 2]
