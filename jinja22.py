from jinja2 import Environment, FileSystemLoader

def environment(**options):
    # Set a default loader if one is not provided
    options.setdefault('loader', FileSystemLoader('pharmacy/templates/pharmacy'))
    env = Environment(**options)
    return env
