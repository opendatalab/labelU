from alembic.command import upgrade

import alembic.config


def run_sqlite_migrations():
    alembicArgs = [
        "--raiseerr",
        "upgrade",
        "head",
    ]
    alembic.config.main(argv=alembicArgs)
