from django import template
import re
register = template.Library()

@register.filter
def add_link(value):
	description = value.description 
	tags = value.tag_set.all() 

	for tag in tags:
		description = re.sub(r'\#'+tag.name+r'\b', '<a href="/result/?search='+tag.name+'">#'+tag.name+'</a>', description)
	return description 