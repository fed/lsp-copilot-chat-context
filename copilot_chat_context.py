import os
import textwrap

import sublime
import sublime_plugin


_state = {"pending_context": None}


def _build_context(view):
    window = view.window()

    file_path = view.file_name() or "<unsaved file>"
    if window and file_path != "<unsaved file>":
        for folder in window.folders():
            if file_path.startswith(folder):
                file_path = os.path.relpath(file_path, folder)
                break

    region = view.sel()[0]
    if not region.empty():
        start_row, _ = view.rowcol(region.begin())
        end_row, _   = view.rowcol(region.end())

        # Expand to full lines so textwrap.dedent sees consistent leading
        # whitespace across all lines (not just from the cursor position).
        start_pos = view.text_point(start_row, 0)
        end_pos   = view.line(view.text_point(end_row, 0)).end()
        full_region = sublime.Region(start_pos, end_pos)

        text = textwrap.dedent(view.substr(full_region)).strip()
        location = "line {}".format(start_row + 1) if start_row == end_row \
                   else "lines {}–{}".format(start_row + 1, end_row + 1)
    else:
        row, _ = view.rowcol(region.begin())
        text   = view.substr(view.line(view.text_point(row, 0))).strip()
        location = "line {}".format(row + 1)

    context = "`{}` {}:\n```\n{}\n```\n".format(file_path, location, text)
    return context, file_path, location


class CopilotChatContextListener(sublime_plugin.EventListener):

    def on_activated(self, view):
        context = _state["pending_context"]
        if context is None:
            return

        window = view.window() or sublime.active_window()
        if not window:
            return

        if window.active_panel() != "input":
            return

        _state["pending_context"] = None

        def do_insert():
            # Save the user's current clipboard so we can restore it
            # immediately after pasting — no lasting clipboard pollution.
            try:
                original = sublime.get_clipboard()
            except Exception:
                original = None

            sublime.set_clipboard(context)
            view.run_command("select_all")
            # Use paste rather than insert to avoid ST's auto-indentation
            # compounding the indentation on each line.
            view.run_command("paste")

            if original is not None:
                sublime.set_timeout(lambda: sublime.set_clipboard(original), 200)

        sublime.set_timeout(do_insert, 50)


class CopilotChatContextCommand(sublime_plugin.TextCommand):
    """
    Opens the LSP-copilot chat and pre-fills the input panel with the
    current file/line context.

    Keybinding suggestion:
        { "keys": ["super+alt+i"], "command": "copilot_chat_context" }
    """

    def run(self, edit):
        context, file_path, location = _build_context(self.view)

        _state["pending_context"] = context

        def clear_pending():
            if _state["pending_context"] == context:
                _state["pending_context"] = None

        sublime.set_timeout(clear_pending, 30000)

        self.view.run_command("copilot_conversation_chat", {"message": ""})

        sublime.status_message("Copilot chat — {} {}".format(file_path, location))
