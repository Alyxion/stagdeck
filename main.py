"""🎬 StagDeck Demo - Example presentation."""

from nicegui import ui
from stagdeck import SlideDeck, DeckViewer
from stagdeck.theme import Theme, LayoutStyle, ElementStyle


# =============================================================================
# 🎨 Theme & Master Layouts
# =============================================================================

THEME = Theme.from_reference('default:aurora.json')


def create_master() -> SlideDeck:
    """Create master deck with layout templates."""
    primary = THEME.variables.get('primary', '#667eea')
    secondary = THEME.variables.get('secondary', '#764ba2')
    accent = THEME.variables.get('accent', '#f5576c')
    
    master = SlideDeck(title='Master')
    
    # Title layout - gradient background
    title_style = LayoutStyle(
        name='title',
        background=f'linear-gradient(135deg, {primary} 0%, {secondary} 100%)',
        title=ElementStyle(color='#ffffff'),
        subtitle=ElementStyle(color='#ffffff', opacity=0.8),
        text=ElementStyle(color='#ffffff'),
    )
    master.add(
        name='title',
        builder=lambda: ui.element('div').classes('w-full h-full').style(title_style.background_style()),
        style=title_style,
    )
    
    # Content layout - light background
    content_style = LayoutStyle(
        name='content',
        background='#ffffff',
        title=ElementStyle(color=THEME.variables.get('heading', '#111827')),
        text=ElementStyle(color=THEME.variables.get('text', '#1f2937')),
    )
    master.add(name='content', style=content_style)
    
    # Code layout - pink gradient
    code_style = LayoutStyle(
        name='code',
        background=f'linear-gradient(135deg, #f093fb 0%, {accent} 100%)',
        title=ElementStyle(color='#ffffff'),
        text=ElementStyle(color='#ffffff'),
    )
    master.add(
        name='code',
        builder=lambda: ui.element('div').classes('w-full h-full').style(code_style.background_style()),
        style=code_style,
    )
    
    return master


# =============================================================================
# 📊 Presentation
# =============================================================================

deck = SlideDeck(
    title='StagDeck Demo',
    master=create_master(),
    default_layout='content',
)

# Slide 1: Title
deck.add(
    layout='title',
    title='Welcome to StagDeck',
    subtitle='A NiceGUI-based Presentation Tool',
    content='Create beautiful presentations with Python',
)

# Slide 2: Features
deck.add(
    title='Features',
    content='''
- **Markdown support** for rich content
- **Custom slide builders** for complex layouts  
- **Keyboard navigation** (arrow keys)
- **Fullscreen mode** (press F)
- **Responsive scaling** to fit any screen
    ''',
)

# Slide 3: Custom builder
def custom_slide():
    with ui.column().classes('w-full h-full items-center justify-center gap-8 p-12'):
        ui.label('Custom Layouts').classes('text-6xl font-bold')
        with ui.row().classes('gap-8 mt-8'):
            for name, icon, color in [('Charts', 'bar_chart', 'blue'), ('Tables', 'table_chart', 'green'), ('Images', 'image', 'purple')]:
                with ui.card().classes('p-6'):
                    ui.icon(icon, size='50px', color=color)
                    ui.label(name).classes('text-2xl font-bold mt-2')

deck.add(builder=custom_slide)

# Slide 4: Get Started
def code_slide():
    with ui.column().classes('w-full h-full items-center justify-center gap-8 p-12'):
        ui.label('Get Started').classes('text-6xl font-bold text-white')
        ui.code('''from stagdeck import SlideDeck, DeckViewer

deck = SlideDeck(title='My Talk')
deck.add(title='Hello', content='World!')
DeckViewer.run(deck)''', language='python').classes('text-xl w-full max-w-3xl')

deck.add(layout='code', builder=code_slide)


# =============================================================================
# 🚀 Run
# =============================================================================

if __name__ in {'__main__', '__mp_main__'}:
    DeckViewer.run(deck)
