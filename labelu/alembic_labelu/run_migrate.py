import os
from alembic.command import upgrade

from alembic.config import Config
from alembic.script import ScriptDirectory

from labelu.internal.common.config import settings


def run_db_migrations():
    migrations_dir = os.path.dirname(os.path.realpath(__file__))
    # assumes the alembic.ini is also contained in the current directory of this file
    config_file = os.path.join(migrations_dir, "alembic.ini")

    config = Config(file_=config_file)
    config.set_main_option("script_location", migrations_dir)
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    script = ScriptDirectory.from_config(config)

    # grab the latest revision
    revision = None
    for revision in script.walk_revisions():
        revision = revision.revision
        break

    # run the upgrade function
    if revision:
        upgrade(config, revision)
