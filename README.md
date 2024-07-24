# ID Card Reader

## How to run
Download file [transformerocr.pth](https://download.thigiacmaytinh.com/pretrain/transformerocr.pth) and copy to dir:
prj8.1-id-card\\server\\module\\CCCD\\transformerocr.pth

Download file [seq2seqocr.pth](https://download.thigiacmaytinh.com/pretrain/seq2seqocr.pth) and copy to dir:
prj8.1-id-card\\server\\module\\CCCD\\seq2seqocr.pth

### Import default database

Create database by cmd
```
mongo
```

```
use idcard
```


```
db.createUser(
  {
    user: "vohungvi",
    pwd: "viscomsolution",
    roles: [ { role: "readWrite", db: "idcard" } ]
  })

```

Import database: run file **restore_db.bat**