from sqlalchemy.orm import Session

from labelu.internal.adapter.persistence import crud_sample
from labelu.internal.domain.models.sample import SampleState, TaskSample


def _seed_samples(db: Session, task_id: int = 201):
    specs = [
        (1, SampleState.DONE.value, 5),
        (2, SampleState.NEW.value, 0),
        (3, SampleState.SKIPPED.value, 0),
        (4, SampleState.NEW.value, 0),
        (5, SampleState.DONE.value, 2),
        (6, SampleState.NEW.value, 0),
    ]
    samples = [
        TaskSample(
            inner_id=inner_id,
            task_id=task_id,
            created_by=1,
            updated_by=1,
            data='{"result": "{}"}',
            state=state,
            annotated_count=count,
        )
        for inner_id, state, count in specs
    ]
    db.bulk_save_objects(samples, return_defaults=True)
    db.commit()
    return samples


def test_sorted_after_and_before_cursor_match_full_sorted_order(db: Session):
    _seed_samples(db, task_id=201)

    for sorting in ("state:asc", "state:desc", "annotated_count:desc", "inner_id:desc"):
        full_order = [
            s.id
            for s in crud_sample.list_by(
                db=db,
                task_id=201,
                after=None,
                before=None,
                page=0,
                size=100,
                sorting=sorting,
            )
        ]
        assert len(full_order) == 6

        # Stepping forward via `after` from the first item should match full_order[1:]
        walked_forward = [full_order[0]]
        cursor = full_order[0]
        while True:
            nxt = crud_sample.list_by(
                db=db,
                task_id=201,
                after=cursor,
                before=None,
                page=None,
                size=1,
                sorting=sorting,
            )
            if not nxt:
                break
            walked_forward.append(nxt[0].id)
            cursor = nxt[0].id
        assert walked_forward == full_order, f"after mismatch for {sorting}"

        # Stepping backward via `before` from the last item should match reversed(full_order)
        walked_backward = [full_order[-1]]
        cursor = full_order[-1]
        while True:
            prev = crud_sample.list_by(
                db=db,
                task_id=201,
                after=None,
                before=cursor,
                page=None,
                size=1,
                sorting=sorting,
            )
            if not prev:
                break
            walked_backward.append(prev[0].id)
            cursor = prev[0].id
        walked_backward.reverse()
        assert walked_backward == full_order, f"before mismatch for {sorting}"

        # Multi-item `before` window preserves forward order
        window = [
            s.id
            for s in crud_sample.list_by(
                db=db,
                task_id=201,
                after=None,
                before=full_order[4],
                page=None,
                size=3,
                sorting=sorting,
            )
        ]
        assert window == full_order[1:4], f"before window mismatch for {sorting}"
