from django import template

register = template.Library()


@register.inclusion_tag('web/emails/button.html')
def email_button_link(link_href, link_text):
    return {'link_href': link_href, 'link_text': link_text}
