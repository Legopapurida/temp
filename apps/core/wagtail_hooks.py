from wagtail import hooks
from wagtailmenus.models import FlatMenu, MainMenu
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


@hooks.register('register_snippet')
def register_custom_menus():
    # Override FlatMenu panels
    FlatMenu.panels = [
        FieldPanel('site'),
        FieldPanel('title'),
        FieldPanel('handle'),
        MultiFieldPanel([
            FieldPanel('max_levels'),
            FieldPanel('use_specific'),
        ], heading="Settings"),
    ]
    
    # Override MainMenu panels  
    MainMenu.panels = [
        FieldPanel('site'),
        MultiFieldPanel([
            FieldPanel('max_levels'),
            FieldPanel('use_specific'),
        ], heading="Settings"),
    ]