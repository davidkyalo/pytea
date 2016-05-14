
inst_attr = '__instance'		

def get_inst(cls):
	return getattr(cls, inst_attr, None)

def set_inst(cls, instance):
	setattr(cls, inst_attr, instance)


class SingleTone(object):
	
	def __new__(cls, *args, **kwargs):
		if not get_inst(cls):
			set_inst( cls, super(SingleTone, cls).__new__(*args, **kwargs) )
		return get_inst(cls)