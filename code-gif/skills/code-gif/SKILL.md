---
name: code-gif
description: Generates animated terminal GIFs with a Mac window layout and custom terminal text frames using Python and Pillow.
---

# code-gif Skill

This skill allows the AI agent to generate beautiful Mac-styled terminal GIFs directly from text inputs.

## Prerequisites
- The system must have `python3` and `Pillow` installed.
- The `code_gif_generator.py` script is deployed in your installation path.

## How to use
When the user asks you to create a GIF of a terminal execution:

1. Create a text file containing the slides/frames. Each frame must be separated by the literal string `---SLIDE---` on its own line.
2. Run the `code_gif_generator.py` script passing the input file and the output GIF path.

Example input file (`frames.txt`):
```text
$ echo "Hello"
---SLIDE---
$ echo "Hello"
Hello
```

Example Execution:
```bash
python3 ~/.local/share/aicockpit/packages/code-gif/scripts/code_gif_generator.py frames.txt output.gif
```

## Styling
The generator automatically draws a dark Mac window (with red, yellow, and green buttons on the top left) and writes the text in a monospace font with light gray color on a dark background.
