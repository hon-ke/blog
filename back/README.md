

postgresql数据库初始化
```bash
# 安装后初始化向量
sudo -iu postgres initdb -D /var/lib/postgres/data

# 启动数据库
sudo systemctl start postgresql

# 连接数据库
sudo -iu postgres psql

CREATE DATABASE blog;

CREATE USER blog WITH ENCRYPTED PASSWORD '123456';

GRANT ALL PRIVILEGES ON DATABASE blog TO blog;

sudo nvim /var/lib/postgres/data/pg_hba.conf
local   all             blog                                    peer
```