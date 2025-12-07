# StagDeck Goals

## Vision

StagDeck aims to be a powerful, accessible presentation tool built on NiceGUI that enables anyone to create beautiful, interactive slide decks—whether they prefer writing Python, Markdown, or a combination of both.

## Core Goals

### 1. Accessible to Everyone
- **No Python knowledge required**: Create full presentations using just Markdown
- **Python optional**: Use Python only when you need dynamic or complex slides
- **Per-slide flexibility**: Mix Markdown and Python slides freely in the same deck

### 2. Multiple Authoring Modes
- **Markdown-only**: Simple, familiar syntax for text-focused presentations
- **Python builders**: Full control with NiceGUI components for complex layouts
- **Hybrid**: Markdown for content slides, Python for interactive or data-driven slides

### 3. Developer Experience
- Simple, intuitive API for creating slides
- Sensible defaults that produce professional-looking results
- Full customization when needed through builder functions

### 4. Interactive & Dynamic
- Support for multi-step slides with incremental reveals
- Real-time updates during development (hot reload)
- URL-based state persistence for seamless navigation

### 5. Presentation Mode
- Fullscreen presentation with keyboard navigation
- Responsive scaling to fit any screen size
- Clean, distraction-free viewing experience

### 6. Extensibility
- Custom slide builders for complex layouts
- Integration with NiceGUI's rich component library
- Support for charts, code highlighting, images, and more

### 7. Deterministic Timing & Export (Essential)
- **Bidirectional navigation**: Always possible to step forward and backward between steps and slides
- **Deterministic duration**: Each step has a defined execution/animation duration; non-animated slides use a configurable constant
- **Computable total duration**: The total presentation duration can be calculated at any time
- **Static export**: Render each step (post-animation) to export as PNG set or PPTX
- **Animated export**: Record step/slide transition animations as MP4 for animated PPTX export

### 8. Unique Identification (Essential)
- **Named slides**: Each slide has a unique name for identification and deep linking
- **Named steps**: Each step within a slide has a unique name
- **Auto-generated names**: Names are auto-generated if not provided (e.g., "slide_1", "step_0")
- **Deep linking**: Navigate directly to any slide/step via URL using names or indices
- **Code references**: Easily reference slides and steps by name in code

### 9. Multi-Deck Support (Essential)
- **Multiple decks**: Register multiple decks in the same application (e.g., master template, actual presentation)
- **URL-based deck selection**: Switch between decks via URL parameter (`?deck=master`)
- **Default deck**: When no deck parameter is provided, load the default deck (usually the main presentation)
- **Hot-switching**: Browse different decks without restarting the application
- **Deck registry**: Central registry to manage and access all available decks

### 10. Master Slides & Layouts (Essential)
- **Master deck**: Define reusable layouts with background images and design elements
- **Layout inheritance**: Presentation slides reference a master layout by name
- **Layered rendering**: Master layout renders first, then slide content layers on top
- **No background/foreground distinction**: All images are just layers; master provides the base, slide adds content
- **Separation of design and content**: Designers create master layouts, presenters focus on content

### 11. One Slide Per File (Essential)
- **Separation of concerns**: Each slide layout lives in its own Python file
- **Easy navigation**: Find and edit slides quickly in the file tree
- **Clean imports**: Import only the slides you need
- **Reusability**: Copy individual slide files between projects

## Non-Goals

- **Not a WYSIWYG editor**: StagDeck uses text-based authoring (Markdown or Python)
- **Not a PowerPoint replacement**: Focus is on technical and educational presentations

## Target Users

- **Non-programmers**: Anyone comfortable with Markdown can create presentations
- **Developers**: Full Python power when needed for dynamic content
- **Data scientists**: Integrate live data and visualizations
- **Educators**: Teach concepts with interactive, step-by-step reveals
- **Technical writers**: Document and present with familiar tools

## Success Criteria

- A non-programmer can create a presentation using only Markdown
- A developer can add Python-powered slides when needed
- Presentations look polished without extensive styling effort
- The learning curve is minimal—Markdown users need zero Python knowledge
- Hot reload enables rapid iteration during presentation creation
