# inotiftpsync

- Author: major1201
- Current version: 0.1
- Platform: Linux (kernel >= 2.6.13)

## Summary

This tool is used for linux system administrators to synchronize files concurrently from Linux system to an FTP server using inotify module.

## Usage

1. Configure
The config file is `conf.yaml`  
sample:
```
inotiftpsync:
  watch_path: "/tmp"
  ftp_server: "127.0.0.1"
  ftp_username: "anonymous"
  ftp_password: ""
  ftp_use_ssl: 0
  ftp_port: 21
  ftp_root: "/"
```
2. Enlarge sysctl for inotify
```
$ sudo sysctl fs.inotify.max_user_watches=50000000
$ sudo sysctl fs.inotify.max_queued_events=327679
$ sudo sysctl fs.inotify.max_user_instances=128
$ sudo sysctl -p
```
3. Run
```
$ python inotiftpsync.py
```

## Requirements

- Python >= 2.6
- inotify
- PyYAML
- six

## Known issues

- If you use a command like `mkdir -p dir1/dir2`, you wouldn't get an `IN_CREATE` event for the `dir2`, the `inotify-tools` on Linux is encountering the same issue.

## License

This project follows GNU General Public License v3.0.
