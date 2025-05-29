# myapp/context_processors.py
# Create this file in your app directory

def search_context(request):
    """
    Add search query to all template contexts
    This makes search_query available in all templates
    """
    return {
        'search_query': request.GET.get('search', ''),
    }

def global_context(request):
    """
    Add other global context variables here if needed
    """
    context = {
        'search_query': request.GET.get('search', ''),
        'current_page': request.resolver_match.url_name if request.resolver_match else None,
        # Add other global variables here as needed
        # 'site_name': 'TailorTrack',
        # 'user_notifications_count': get_user_notifications_count(request.user) if request.user.is_authenticated else 0,
    }
    return context