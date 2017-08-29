from django.template import Library

register = Library()

#@register.filter_function
#def order_by(queryset, args):
 #   args = [x.strip() for x in args.split(',')]
  #  return queryset.order_by(*args)

@register.filter
def order_by(lst, key_name):
    return lst.order_by(key_name)