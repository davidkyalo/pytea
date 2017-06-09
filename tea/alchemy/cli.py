from tea.flask.cli import Manager, prompt_bool
from .utils import app_get_db_client
from flask import current_app

console = Manager(usage="Perform SQL database operations with SQLAlchemy.")


@console.command
def createdb(create_tables=True):
	"""Creates the configured database and tables from sqlalchemy models."""
	_dbclient().create_database(create_tables=create_tables)


@console.command
def dropdb(drop_tables=False):
	"""Drops the current sqlalchemy database."""
	if prompt_bool("Sure you want to drop the database?"):
		_dbclient().drop_database(drop_tables=drop_tables)


@console.command
def recreatedb(create_tables=True, drop_tables=False):
	"""Recreates the database and tables (same as issuing 'drop_db' and then 'create_db')."""
	dropdb(drop_tables)
	createdb(create_tables)


@console.command
def createtables():
	"""Creates the configured database and tables from sqlalchemy models."""
	_dbclient().create_all()


@console.command
def droptables():
	"""Drops the current sqlalchemy database."""
	if prompt_bool("Sure you want to drop all tables in the database?"):
		_dbclient().drop_all()


@console.command
def recreatetables():
	"""Recreates database tables (same as issuing 'drop_tables' and then 'create_tables')."""
	droptables()
	createtables()


def _dbclient(app=None):
	return app_get_db_client(app or current_app)
