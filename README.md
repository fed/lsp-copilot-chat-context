# lsp-copilot-chat-context

A Sublime Text 4 plugin that prefills the [LSP-copilot](https://github.com/sublimelsp/LSP-copilot) chat input with the current file name, line number, and selected code, so you can ask questions about your code without any copying and pasting.

## Requirements

- [Sublime Text 4](https://www.sublimetext.com/)
- [LSP package](https://packagecontrol.io/packages/LSP)
- [LSP-copilot package](https://packagecontrol.io/packages/LSP-copilot) with an active GitHub Copilot subscription

## Installation

1. Open your Sublime Text packages folder via **Preferences → Browse Packages**
2. Copy `copilot_chat_context.py` into the `User/` folder
3. Add a keybinding (see below)

## Keyboard shortcut

Open **Preferences > Key Bindings** and add the following to the user pane:

```json
{ "keys": ["super+alt+i"], "command": "copilot_chat_context" }
```

Adjust the key combo to your preference. `super` is `Cmd` on macOS and `Win` on Windows/Linux.

## Usage

- **Single line**: place your cursor anywhere on the line and press the keybinding
- **Multiple lines**: select the block of code first, then press the keybinding

The plugin will:

1. Open the Copilot chat panel
2. Prefill the input with the file path (relative to your project root), line number(s), and a dedented code fence containing the selected code
3. Wait for you to type your question and press Enter

On first use, there is a short delay while Copilot establishes a new conversation. After that, the input panel opens immediately on every subsequent press.

## How it works

The plugin hooks into LSP-copilot's internal `copilot_conversation_chat` command, which accepts an `initial_text` argument for the chat input panel. A `sublime_plugin.EventListener` listens for the input panel to become active via `on_activated`, then inserts the context using `paste` (rather than `insert`) to preserve correct indentation. The user's clipboard is saved and restored transparently.

## Caveats

- Requires an active conversation to prefill instantly. On first use (no open conversation), there is a brief network delay while Copilot creates a new conversation session.
- The plugin does not send anything to Copilot automatically, it only prefills the input. You still press Enter to send.
