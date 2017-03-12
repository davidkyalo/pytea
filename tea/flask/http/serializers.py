from marshmallow import fields, Schema as BaseSchema, pre_load, post_load, post_dump, MarshalResult
from ..serializers import fields, Schema, sanitize

class JsonSchema(Schema):
	pass


class JSendSchema(JsonSchema):
	status = fields.String()
	data = fields.Raw()
	meta = fields.Dict()
	message = fields.String()
	code = fields.Integer()

	class Meta:
		ordered = True


class QueryOptionsSchema(Schema):
	filters = fields.List(fields.Raw, allow_none=True, default=[])
	filter_by = fields.Dict(allow_none=True, default={})
	order_by = fields.List(fields.Raw, allow_none=True, default=[])
	order = fields.String(allow_none=True, default=None, sanitize=sanitize.Strip)
	per_page = fields.Integer(allow_none=True, default=None)
	page = fields.Integer(allow_none=True, default=None)

