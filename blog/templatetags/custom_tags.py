from django import template

register = template.Library()

@register.filter
def get_range(total_pages, args):
    """
    Generate a range of page numbers for pagination
    Usage: {{ total_pages|get_range:5:current_page }}
    """
    args_list = args.split(':')
    display_count = int(args_list[0])
    current_page = int(args_list[1])
    
    # Calculate the start and end page numbers to display
    half = display_count // 2
    if total_pages <= display_count:
        # If we have fewer pages than we want to display, show all
        start = 0
        end = total_pages
    elif current_page <= half:
        # Near the beginning
        start = 0
        end = display_count
    elif current_page >= total_pages - half - 1:
        # Near the end
        start = total_pages - display_count
        end = total_pages
    else:
        # In the middle
        start = current_page - half
        end = current_page + half + 1
    
    return range(max(0, start), min(total_pages, end))