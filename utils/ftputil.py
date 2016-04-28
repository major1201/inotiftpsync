# encoding: utf-8

from utils import num, strings

class FtpFile(object):

    def __init__(self, item):
        assert isinstance(item, str)
        item_arr = item.split()
        self.permission = item_arr[0]
        self.hard_link_count = num.safe_int(item_arr[1])
        self.owner = item_arr[2]
        self.group = item_arr[3]
        self.size = num.safe_int(item_arr[4])

        # process date time
        from datetime import datetime
        if " ".join(item_arr[5:8]).index(":") > 0:
            # this year
            self.date = datetime.strptime(" ".join(item_arr[5:8]) + " " + str(datetime.now().year), "%b %d %H:%M %Y")
        else:
            # not this year
            self.date = datetime.strptime(" ".join(item_arr[5:8]), "%b %d %Y")
        temp = item
        for field in item_arr[:7]:
            temp = temp.lstrip(field)
            temp = temp.lstrip()
        temp = temp.lstrip(item_arr[7])[1:]
        self.filename = temp

        # set helper attributes
        self.is_dir = self.permission[0] == "d"
        self.is_file = self.permission[0] == "-"

    def __repr__(self):
        return " ".join(str(attr) for attr in [
            self.permission,
            self.hard_link_count,
            self.owner,
            self.group,
            self.size,
            self.date,
            self.filename
        ])

    def __str__(self):
        return self.__repr__()

class FtpUtil(object):

    def __init__(self, server, port=21, username="anonymous", password ="", use_ssl=False):
        self._server = server
        self._port = port
        self._username = username
        self._password = password
        self._use_ssl = use_ssl
        if use_ssl:
            from ftplib import FTP_TLS
            self._ftp = FTP_TLS()
        else:
            from ftplib import FTP
            self._ftp = FTP()

    def __enter__(self):
        self._ftp.connect(self._server, self._port)
        self._ftp.login(self._username, self._password)
        self._ftp.sendcmd("OPTS UTF8 ON")
        return self

    def __exit__(self, *exc_args):
        self._ftp.quit()

    def set_pasv(self, val):
        self._ftp.set_pasv(val)

    def cwd(self, dirname):
        self._ftp.cwd(dirname)

    def list(self, dirname=None):
        arr = self._ftp.nlst("-l", dirname)
        ret_arr = []
        for item in arr:
            ret_arr.append(FtpFile(item))
        return ret_arr

    def sendcmd(self, cmd):
        return self._ftp.sendcmd(cmd)

    def upload(self, local_file_path, ftp_file_path):
        with open(local_file_path, "rb") as f:
            self._ftp.storbinary("STOR " + ftp_file_path, f)

    def download(self, ftp_file_path, local_file_path):
        with open(local_file_path, "wb") as f:
            self._ftp.retrbinary("RETR " + ftp_file_path, f.write)

    def delete_file(self, file_path):
        self._ftp.delete(file_path)

    def mkdir(self, dirname):
        self._ftp.mkd(dirname)

    def mkdir_parent(self, dirname):
        from ftplib import error_perm
        from os.path import sep
        dirname = strings.rtrim(dirname, sep)
        dir_arr = dirname.split(sep)
        for i in range(2 if dirname.startswith("/") else 1, len(dir_arr) + 1):
            try:
                self.mkdir(sep.join(dir_arr[:i]))
            except error_perm:
                pass
            except:
                import traceback
                print(traceback.format_exc())

    def rmdir(self, dirname):
        self._ftp.rmd(dirname)

    def rename(self, fromname, toname):
        self._ftp.rename(fromname, toname)
