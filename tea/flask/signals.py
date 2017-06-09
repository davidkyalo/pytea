from flask.signals import Namespace


signals = Namespace()

app_created = signals.signal('app-created')
app_booting = signals.signal('app-booting')
app_booted = signals.signal('app-booted')

# app_registering_blueprint = signals.signal('app-registering-blueprint')
# app_registered_blueprint = signals.signal('app-registered-blueprint')

app_starting = signals.signal('app-started')
app_started = signals.signal('app-started')

blueprint_registering = signals.signal('blueprint-registering')
blueprint_registered = signals.signal('blueprint-registered')


session_starting = signals.signal('session-starting')
session_started = signals.signal('session-started')
session_ending = signals.signal('session-ending')
session_ended = signals.signal('session-ended')
