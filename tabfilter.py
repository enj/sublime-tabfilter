# Copyright (c) 2013 - 2016 Robin Malburn
# See the file license.txt for copying permission.

import sublime
import sublime_plugin
import os
try:
	#Python 3 / ST3 relative import within package.
	from . import tab
except ValueError:
	#Python 2 / ST2 fallback for relative import.
	import tab

class TabFilterCommand(sublime_plugin.WindowCommand):
	"""Provides a GoToAnything style interface for searching and selecting open tabs"""

	def run(self):
		"""Shows a quick panel to filter and select tabs from the active window"""

		tabs = []
		self.window = sublime.active_window()
		self.views = []
		self.prefix = ""
		self.settings = sublime.load_settings("tabfilter.sublime-settings")

		for view in self.window.views():
			self.views.append(view)
			tabs.append(self.make_tab(view))

		self.prefix = len(os.path.commonprefix([entity.name for entity in tabs if entity.is_file]))

		show_captions = self.settings.get("show_captions", True)
		include_path = self.settings.get("include_path", False)

		tabs = [entity.get_details(self.prefix, include_path, show_captions) for entity in tabs]

		self.window.show_quick_panel(tabs, self._on_done)

	def make_tab(self, view):
		"""Makes a new Tab entity relating to the given view.
		Args:
			view (sublime.View): Sublime View to build the Tab from
		Returns (Tab): Tab entity containing metadata about the view.

		"""
		name = view.file_name()
		is_file = True

		#If the name is not set, then we're dealing with a buffer
		#rather than a file, so deal with it accordingly.
		if name is None:
			is_file = False
			name = view.name()
			#set the view name to untitled if we get an empty name
			if len(name) == 0:
				name = "untitled"

		max_size = 200
		size = min(view.size(), max_size)
		contents = view.substr(sublime.Region(0, size))

		entity = tab.Tab(name, is_file, contents)

		if self.window.get_view_index(self.window.active_view()) == self.window.get_view_index(view):
			entity.add_caption("Current File")

		if view.file_name() is None:
			entity.add_caption("Unsaved File")
		elif view.is_dirty():
			entity.add_caption("Unsaved Changes")

		if view.is_read_only():
			entity.add_caption("Read Only")

		return entity

	def _on_done(self,index):
		"""Callback handler to move focus to the selected tab index"""
		if index > - 1:
			self.window.focus_view(self.views[index])
