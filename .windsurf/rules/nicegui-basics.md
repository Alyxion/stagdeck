---
trigger: always_on
---

- Use poetry to run projects. If 8080 is blocked kill the server.
- The project docs are stored in Docs
- NiceGUI hot reloads changes. if the server is running no restart required after changes usually.
- Use nice-vibes to investigate NiceGUI details
- Goal of this project is to build slides using NiceGUI and using Markdown as foramt or customized Python slides with interactive content.
- When starting the server do not change the workdir, always start from the project root to enable NiceGUI to also track changes in the stackdeck source code.
- The stagdeck server has a render function which lets you render the slides so you can investigate changes.