#! /usr/bin/env python
# encoding: utf-8
import os
import sys
from utils import filewatcher, strings


class _Sync(filewatcher.WatchEventHandler):

    def __init__(self, path, ftp_server, ftp_username="anonymous", ftp_password ="", ftp_use_ssl=False, ftp_port=21, ftp_root="/"):
        super(_Sync, self).__init__(path)

        from utils.ftputil import FtpUtil
        self.ftp = FtpUtil(ftp_server, ftp_port, ftp_username, ftp_password, ftp_use_ssl)

        self._ftp_root = ftp_root

    def in_attrib(self, filename, is_dir):
        pass

    def in_close_write(self, filename):
        from os.path import sep, dirname
        absolute_local_path = strings.rtrim(self._path_to_watch, sep) + sep + strings.ltrim(filename, sep)
        with self.ftp as ftp:
            ftp.cwd(self._ftp_root)
            ftp.mkdir_parent(dirname(filename))
            ftp.upload(absolute_local_path, filename)

    def in_move(self, from_path, to_path, is_dir):
        with self.ftp as ftp:
            ftp.cwd(self._ftp_root)
            ftp.rename(from_path, to_path)

    def in_create(self, filename, is_dir):
        if is_dir:
            with self.ftp as ftp:
                ftp.cwd(self._ftp_root)
                ftp.mkdir_parent(filename)

    def in_delete(self, filename, is_dir):
        with self.ftp as ftp:
            ftp.cwd(self._ftp_root)
            if is_dir:
                ftp.rmdir(filename)
            else:
                ftp.delete_file(filename)


def main():
    reload(sys)
    sys.setdefaultencoding("utf-8")

    # init setting
    from utils import setting, num
    setting.load(file(os.path.join(os.path.dirname(__file__), "conf.yaml")))

    # pid file
    with open(os.path.join(os.path.dirname(__file__), setting.conf.get("system").get("project_name") + ".pid"), 'wb') as pid:
        pid.write(str(os.getpid()))

    conf = setting.conf.get("inotiftpsync")
    _Sync(
        path=conf.get("watch_path"),
        ftp_server=conf.get("ftp_server"),
        ftp_username=conf.get("ftp_username"),
        ftp_password=conf.get("ftp_password"),
        ftp_use_ssl=num.safe_int(conf.get("ftp_use_ssl")) == 1,
        ftp_port=conf.get("ftp_port"),
        ftp_root=conf.get("ftp_root")
    ).start()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Program Stopped Manually...")
    finally:
        # delete pid file
        try:
            import os
            from utils import setting
            os.remove(os.path.join(os.path.dirname(__file__), setting.conf.get("system").get("project_name") + ".pid"))
        except: pass
