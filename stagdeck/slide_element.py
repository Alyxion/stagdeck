"""SlideElement - Named container component for slide layouts."""

from nicegui.element import Element


class SlideElement(Element, component='div'):
    """Named container for slide content. No padding/margin by default.
    
    SlideElements form a hierarchy using NiceGUI's context system.
    Child elements automatically register with their parent SlideElement.
    
    :ivar name: Unique identifier within parent hierarchy.
    :ivar style_ref: Reference to theme component style (colors, fonts).
    :ivar children_elements: Dict of child SlideElements by name.
    """
    
    def __init__(self, name: str, style: str = '', classes: str = ''):
        """Create a named SlideElement.
        
        :param name: Unique identifier for this element.
        :param style: Theme style reference (e.g., 'title', 'body_text').
        :param classes: Additional Tailwind classes for positioning/sizing.
        """
        super().__init__()
        self.name = name
        self.style_ref = style
        self.children_elements: dict[str, 'SlideElement'] = {}
        
        # No padding/margin by default
        base_classes = 'p-0 m-0'
        if classes:
            base_classes = f'{base_classes} {classes}'
        self.classes(base_classes)
        
        # Register with parent SlideElement (uses NiceGUI's context system)
        if self.parent_slot and self.parent_slot.parent:
            parent = self.parent_slot.parent
            if isinstance(parent, SlideElement):
                parent.children_elements[name] = self
    
    def find(self, name: str) -> 'SlideElement | None':
        """Find element by name in this element's hierarchy.
        
        :param name: Element name to find.
        :return: SlideElement if found, None otherwise.
        """
        if name in self.children_elements:
            return self.children_elements[name]
        # Search recursively in children
        for child in self.children_elements.values():
            found = child.find(name)
            if found:
                return found
        return None
    
    def __getitem__(self, name: str) -> 'SlideElement':
        """Shorthand for find(name). Raises KeyError if not found.
        
        :param name: Element name to find.
        :return: SlideElement.
        :raises KeyError: If element not found.
        """
        element = self.find(name)
        if element is None:
            raise KeyError(f"Element '{name}' not found")
        return element
