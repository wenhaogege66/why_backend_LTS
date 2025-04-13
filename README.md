1. 创建并激活虚拟环境
```bash
python -m venv ./venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置数据库
- 创建 MySQL 数据库
```sql
CREATE DATABASE IF NOT EXISTS music_recommendation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. 配置环境变量
创建 `.env` 文件并配置以下内容：
```
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=music_recommendation
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306
```

5. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

6. 运行开发服务器
```bash
python manage.py runserver
```

7.管理员
email='admin@example.com',
password='admin123456',
nickname='admin'

8.音乐相关
先艺术家，再专辑，最后歌曲；专辑字段是可选的，如果只想创建歌曲而不关联专辑，可以省略 album 字段