from django import template

register = template.Library()

@register.filter(name='censor')
def censor(value):
    bad_words = ['редиска', 'сарделька']
    new_content = value
    for w in bad_words:
        new_content = new_content.replace(w, '***')
    return new_content