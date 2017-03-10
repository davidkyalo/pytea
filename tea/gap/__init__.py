from .core import ValidationError, DataSet
from tea.constants import NOT_PROVIDED
from tea.collections import stack, to_list
from tea import uzi
from tea.utils.encoding import force_text
from . import rules


def validate(rule_set, data):
	if callable(rule_set):
		rule_set = rule_set()

	errors = stack()
	data = DataSet(data)
	# passed = []
	# failed = []
	fields = _parse_fields(rule_set)

	for field in fields.default:
		error = _validate_field(field, data)
		if error:
			errors[field.attribute] = error
			# failed.append(field.attribute)
		# else:
		# 	passed.append(field.attribute)

	# for field in fields.if_fails:
	# 	condition = field.if_fails

	# 	error = _validate_field(field, data)
	# 	if error:
	# 		errors[field.attribute] = error
	# 		failed.append(field.attribute)
	# 	else:
	# 		passed.append(field.attribute)

	if len(errors) > 0:
		return ValidationError(errors)

def _validate_field(field, data):
	value = field.clean(data.get(field.attribute), field=field, data=data)
	for rule in field.rules:
		rule = rules._get_rule_instance(rule, field.display_name, field.error_message)
		try:
			rule(value, data)
		except ValidationError as error:
			field.passed = False
			return error
	field.passed = True


def _parse_fields(field_set):
	fields = stack()
	fields.all = stack()
	fields.default = []
	fields.if_passes = []
	fields.if_fails = []
	for f in field_set:
		if f.if_passes:
			fields.if_passes.append(f)
		elif f.if_fails:
			fields.if_fails.append(f)
		else:
			fields.default.append(f)
		fields.all[f.attribute] = f
	return fields


def field(attribute, *rules, display_name=None, error_message=None, if_passes=None, if_fails=None, clean=None):
	if display_name is None:
		display_name = uzi.humanize(attribute).title()
	if clean is None:
		clean = lambda v, **kwg: v

	field = stack()
	field.attribute = attribute
	field.rules = rules
	field.display_name = display_name
	field.error_message = error_message
	field.if_passes = to_list(if_passes, None) if if_passes != '*' else '*'
	field.if_fails = to_list(if_fails, None) if if_fails != '*' else '*'
	field.clean = clean
	return field

