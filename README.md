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

2. Run
```
$ python inotiftpsync.py
```

## Requirements

- Python >= 2.6
- inotify
- PyYAML

## Known issues

## License

This project follows GNU General Public License v3.0.