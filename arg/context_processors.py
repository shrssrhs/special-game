def arg_context(request):
    unlocked = set(request.session.get('arg_unlocked', []))
    # archive, about, contact — всегда доступны
    unlocked.update(['archive', 'about', 'contact'])

    nav = [
        {'key': 'archive',   'label': 'ARCHIVE',   'url': '/archive/'},
        {'key': 'cases',     'label': 'CASES',     'url': '/cases/'},
        {'key': 'protocols', 'label': 'PROTOCOLS', 'url': '/protocols/'},
        {'key': 'contact',   'label': 'CONTACT',   'url': '/contact/'},
        {'key': 'about',     'label': 'ABOUT',     'url': '/about/'},
    ]

    # OBSERVER появляется только после разблокировки
    if 'observer' in unlocked:
        nav.insert(3, {'key': 'observer', 'label': 'OBSERVER', 'url': '/observer/'})

    for item in nav:
        item['locked'] = item['key'] not in unlocked

    return {
        'arg_nav': nav,
        'arg_unlocked': unlocked,
    }
