# encoding: utf-8
import os
from inotify.constants import *
from inotify.adapters import Inotify
from utils import strings

class InotifyRecursive(object):
    def __init__(self, path, mask=IN_ALL_EVENTS, block_duration_s=1):

        self.__root_path = path

        # No matter what we actually received as the mask, make sure we have
        # the minimum that we require to curate our list of watches.
        self.__mask = mask | IN_ISDIR | IN_CREATE | IN_DELETE

        self.__i = Inotify(block_duration_s=block_duration_s)

        self.__load_tree(path)

    def __load_tree(self, path):
        q = [path]
        while q:
            current_path = q[0]
            del q[0]

            self.__i.add_watch(current_path, self.__mask)

            for filename in os.listdir(current_path):
                entry_filepath = os.path.join(current_path, filename)
                if os.path.isdir(entry_filepath) is False:
                    continue

                q.append(entry_filepath)

    def event_gen(self):
        for event in self.__i.event_gen():
            if event is not None:
                (header, type_names, path, filename) = event

                if header.mask & IN_ISDIR:
                    full_path = os.path.join(path, filename)
                    if header.mask & IN_CREATE:
                        self.__i.add_watch(full_path, self.__mask)

                        # solved minor situations that the inotify cannot discover the change
                        for root, dirs, files in os.walk(full_path):
                            for name in dirs:
                                self.__i.add_watch(os.path.join(root, name))

                    elif header.mask & IN_DELETE:
                        self.__i.remove_watch(full_path, superficial=True)
            yield event


class WatchEventHandler(object):
    _path_to_watch = None
    _inotify_adapter = None
    _stop_flag = False

    def __init__(self, path):
        self._path_to_watch = path

    def start(self):

        from os.path import sep
        self._inotify_adapter = InotifyRecursive(self._path_to_watch)
        cookie_cache = {}
        for event in self._inotify_adapter.event_gen():
            if self._stop_flag:
                break
            if event is not None:
                try:
                    (header, type_names, watch_path, filename) = event
                    full_path = strings.rtrim(watch_path, sep) + sep + filename
                    rela_path = strings.ltrim(full_path, strings.rtrim(self._path_to_watch, sep) + sep)
                    if header.mask & IN_ACCESS:
                        self.in_access(rela_path)
                    if header.mask & IN_MODIFY:
                        self.in_modify(rela_path)
                    if header.mask & IN_ATTRIB:
                        self.in_attrib(rela_path, header.mask & IN_ISDIR)
                    if header.mask & IN_CLOSE_WRITE:
                        self.in_close_write(rela_path)
                    if header.mask & IN_CLOSE_NOWRITE:
                        self.in_close_nowrite(rela_path, header.mask & IN_ISDIR)
                    if header.mask & IN_OPEN:
                        self.in_open(rela_path, header.mask & IN_ISDIR)
                    if header.mask & IN_MOVED_FROM:
                        cookie_cache[header.cookie] = event
                    if header.mask & IN_MOVED_TO:
                        _event = cookie_cache.get(header.cookie)
                        if _event is not None:
                            (_header, _type_names, _watch_path, _filename) = _event
                            from_path = strings.rtrim(_watch_path, sep) + sep + _filename
                            from_path = strings.ltrim(from_path, strings.rtrim(self._path_to_watch, sep) + sep)
                            self.in_move(from_path, rela_path, header.mask & IN_ISDIR)
                            cookie_cache.pop(header.cookie)
                    if header.mask & IN_CREATE:
                        self.in_create(rela_path, header.mask & IN_ISDIR)
                    if header.mask & IN_DELETE:
                        self.in_delete(rela_path, header.mask & IN_ISDIR)
                    if header.mask & IN_DELETE_SELF:
                        self.in_delete_self(rela_path)
                    if header.mask & IN_MOVE_SELF:
                        self.in_move_self(rela_path)
                except:
                    import traceback
                    print(traceback.format_exc())

    def stop(self):
        self._stop_flag = True

    # (+) File was accessed
    def in_access(self, filename):
        pass

    # (+) File was modified
    def in_modify(self, filename):
        pass

    # (*) Metadata changed—for example, permissions, and user/group ID
    def in_attrib(self, filename, is_dir):
        pass

    # (+) File opened for writing was closed.
    def in_close_write(self, filename):
        pass

    # (*) File or directory not opened for writing was closed.
    def in_close_nowrite(self, filename, is_dir):
        pass

    # (*) File or directory was opened.
    def in_open(self, filename, is_dir):
        pass

    # (+) move event
    def in_move(self, from_path, to_path, is_dir):
        pass

    # (+) File/directory created in watched directory
    def in_create(self, filename, is_dir):
        pass

    # (+) File/directory deleted from watched directory.
    def in_delete(self, filename, is_dir):
        pass

    # Watched file/directory was itself deleted.  In addition, an IN_IGNORED event will subsequently be generated for the watch descriptor.
    def in_delete_self(self, filename):
        pass

    # Watched file/directory was itself moved.
    def in_move_self(self, filename):
        pass
