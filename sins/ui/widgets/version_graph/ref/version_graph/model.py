# -*- coding: utf-8 -*-


class VersionItem(object):

    def __init__(self, version=None):

        self._version = version
        self._parent = None
        self._children = []

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def name(self):
        return self._version.name

    @property
    def asset(self):
        return self._version.asset

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent
        parent.add_child(self)

    def add_child(self, child):
        self._children.append(child)
        child._parent = self

    def insert_child(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def remove_child(self, position):

        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    def child(self, row):
        if self._children:
            return self._children[row]
        else:
            return None

    def child_count(self):
        return len(self._children)

    def get_all_children(self, version_item=None):
        if not version_item:
            version_item = self

        for source in version_item.version.sources:
            item = VersionItem(version=source)
            item.parent = version_item
            VersionItem.get_all_children(item)

    def log(self, tab_level=-1):

        output = ""
        tab_level += 1

        for i in range(tab_level):
            output += "\t"

        output += "|--" + self.name + "\n"

        for child in self._children:
            output += child.log(tab_level)

        tab_level -= 1
        output += "\n"

        return output

    def __repr__(self):
        return self.log()
