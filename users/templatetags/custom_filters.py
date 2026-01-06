from django import template

register = template.Library()

@register.filter
def generation_format(value):
    """기수를 '_th' 형식으로 변환"""
    return f"{value}_th"
