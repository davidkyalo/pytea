from . import signals
from tea.importer import import_object
from flask import Flask as BaseFlask, Blueprint as BaseBlueprint
from flask.app import setupmethod


class Flask(BaseFlask):

	def __init__(self, import_name, static_path=None, static_url_path=None,
				static_folder='static', template_folder='templates',
				instance_path=None,	instance_relative_config=False,
				root_path=None):

		kwargs = dict(
			static_path=static_path, static_url_path=static_url_path,
			static_folder=static_folder,template_folder=template_folder,
			instance_path=instance_path, root_path=root_path,
			instance_relative_config=instance_relative_config
		)

		super(Flask, self).__init__(import_name, **kwargs)
		self._has_booted = False
		#Send signal: app_created
		signals.app_created.send(self, import_name=import_name, options=kwargs)

	@setupmethod
	def boot(self):
		if self._has_booted:
			return
		signals.app_booting.send(self)
		self.register_configured_blueprints()
		self._boot()
		self._has_booted = True
		signals.app_booted.send(self)

	def _boot(self):
		pass

	def register_configured_blueprints(self):
		for blueprint in self.config.get('BLUEPRINTS', []):
			if isinstance(blueprint, str):
				blueprint = import_object(blueprint)
			self.register_blueprint(blueprint)

	def run(self, host=None, port=None, debug=None, **options):
		signals.app_starting.send(self, host=host, port=port,
								debug=debug, options=options)
		# Calls super to run the app.
		super(Flask, self).run(host=host, port=port, debug=debug, **options)


Flask.__doc__ = BaseFlask.__doc__


class Blueprint(BaseBlueprint):

	def register(self, app, options, first_registration=False):
		signals.blueprint_registering.send(self, app=app, options=options,
									first_registration=first_registration)

		super(Blueprint, self).register(app, options, first_registration)

		signals.blueprint_registered.send(self, app=app, options=options,
									first_registration=first_registration)

Blueprint.__doc__ = BaseBlueprint.__doc__