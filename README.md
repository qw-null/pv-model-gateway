# PV Model Gateway — 光伏模型网关

将光伏 Python 模型自动转化为 RESTful API 服务，支持在线编辑、校验、调试、组件/逆变器管理与模型关系管理。

---

## 环境要求

| 依赖 | 版本要求 |
|------|---------|
| Python | 3.10+ |
| Node.js | 18+ |
| MySQL | 8.0+ |
| Docker（可选） | 20.10+ |

---

## 环境变量配置

在 `backend/` 目录下创建 `.env` 文件：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=pv_gateway
```

Docker 模式下在 `docker-compose.yml` 中统一配置，无需单独创建 `.env`。

> **注意：​** `docker-compose.yml` 中挂载了 `./mysql/init.sql` 作为 MySQL 初始化脚本，如不需要可将该挂载行注释掉，或在项目根目录创建 `mysql/init.sql` 空文件。

---

## 运行方式

### 方式一：Docker 启动（推荐）

确保本机已安装 Docker 和 Docker Compose，然后在项目根目录执行：

```bash
# 1. 克隆项目
git clone https://github.com/qw-null/pv-model-gateway.git
cd pv-model-gateway

# 2. 一键构建并启动所有服务
docker-compose up -d --build

# 3. 查看启动日志确认无报错
docker-compose logs -f
```

启动成功后访问：

| 服务 | 地址 |
|------|------|
| 前端管理界面 | http://localhost:3000 |
| 后端 API 文档（Swagger） | http://localhost:8080/docs |
| 健康检查 | http://localhost:8080/ |

停止服务：

```bash
docker-compose down
```

---

### 方式二：本地手动启动

#### 第一步：准备数据库

确保 MySQL 已启动，并创建数据库：

```sql
CREATE DATABASE pv_gateway CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后在 `backend/` 目录下配置 `.env` 文件（见上方环境变量配置）。

#### 第二步：启动后端

```bash
# 进入后端目录
cd backend

# 创建并激活虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py

# 或使用 uvicorn 直接启动
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

后端启动后，终端会输出类似如下日志：

```
检查数据库连接...
初始化数据库表结构...
扫描并加载模型...
已加载模型: ['solar_position', 'irradiance_split', 'pv_conversion', 'reflection']
同步 panels_repo 组件文件...
同步 inverters_repo 逆变器文件...
初始化管理员账号...
默认管理员账号已创建（admin / admin123），请尽快修改密码
PV Model Gateway 启动完成 ✅
```

#### 第三步：启动前端

新开一个终端窗口：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后访问 http://localhost:3000 即可。

---

## 默认管理员账号

系统首次启动时会自动创建默认管理员账号：

| 用户名 | 密码 |
|--------|------|
| `admin` | `admin123` |

**请在首次登录后立即修改密码。​**

---

## 验证服务是否正常

后端启动后，可以用 curl 或 Postman 直接测试任意模型接口：

```bash
# 测试太阳位置模型
curl -X POST http://localhost:8080/api/run/solar_position \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 39.9,
    "longitude": 116.4,
    "datetime": "2024-06-21T12:00:00+08:00",
    "timezone": "Asia/Shanghai"
  }'
```

正常返回示例：

```json
{
  "success": true,
  "model": "solar_position",
  "version": "1.0.0",
  "outputs": {
    "altitude": 73.5612,
    "azimuth": 178.2341,
    "zenith": 16.4388,
    "is_daytime": true
  },
  "execution_time_ms": 38.5
}
```

---

## 新增模型（3步）

1. 在前端点击「新增模型」，填写 `meta.py` 和 `model.py`
2. 点击「校验代码」通过后，点击「发布模型」
3. API 自动注册，立即可用：`POST /api/run/{model_name}`

---

## 模型编码规范

每个模型由两个文件组成，放置于 `backend/models_repo/{model_name}/` 目录：

| 文件 | 职责 |
|------|------|
| `meta.py` | 定义 `MODEL_META` 字典，描述输入输出与模型关系 |
| `model.py` | 实现 `run(inputs: dict) -> dict` 函数 |

### meta.py 结构示例

```python
MODEL_META = {
    "name": "solar_position",
    "title": "太阳位置模型",
    "version": "1.0.0",
    "description": "根据时间和地理坐标，计算太阳高度角、方位角与天顶角",
    "author": "PV Team",
    "category": "太阳位置",
    "inputs": [
        {
            "name": "latitude",
            "type": "float",
            "required": True,
            "min": -90.0,
            "max": 90.0,
            "description": "纬度 (°)"
        },
        {
            "name": "longitude",
            "type": "float",
            "required": True,
            "min": -180.0,
            "max": 180.0,
            "description": "经度 (°)"
        },
        {
            "name": "datetime",
            "type": "str",
            "format": "datetime",
            "required": True,
            "description": "ISO 格式时间，如 2024-06-21T12:00:00+08:00"
        },
        {
            "name": "timezone",
            "type": "str",
            "required": False,
            "default": "Asia/Shanghai",
            "description": "时区字符串，如 Asia/Shanghai"
        }
    ],
    "outputs": [
        {"name": "altitude", "type": "float", "unit": "°", "description": "太阳高度角"},
        {"name": "azimuth",  "type": "float", "unit": "°", "description": "太阳方位角"},
        {"name": "zenith",   "type": "float", "unit": "°", "description": "天顶角"},
        {"name": "is_daytime", "type": "bool", "unit": "", "description": "是否为白天"}
    ],
    "tags": ["solar", "position"],
    "execution": {
        "timeout": 30,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
```

### model.py 结构示例

```python
def run(inputs: dict) -> dict:
    latitude  = inputs["latitude"]
    longitude = inputs["longitude"]
    dt        = inputs["datetime"]
    timezone  = inputs.get("timezone", "Asia/Shanghai")
    # 计算逻辑...
    return {
        "altitude":   73.56,
        "azimuth":    178.23,
        "zenith":     16.44,
        "is_daytime": True
    }
```

---

## 组件与逆变器管理

系统支持导入光伏组件（`.pan` 文件）和逆变器（`.ond` 文件）：

- 将 `.pan` 文件放入 `backend/panels_repo/` 目录，启动时自动解析入库
- 将 `.ond` 文件放入 `backend/inverters_repo/` 目录，启动时自动解析入库
- 已入库的文件不会重复导入（按文件名去重）
- 可通过前端界面进行管理，对应后端接口分别为 `/api/panels/` 和 `/api/inverters/`

---

## 模型关系说明

系统支持在模型间定义四类关系，可在前端「模型统计」页面可视化管理：

| 关系类型 | 含义 |
|---------|------|
| `pre` | 上游模型（本模型依赖其输出） |
| `post` | 下游模型（本模型输出流向的模型） |
| `depends_on` | 运行依赖（必须先执行的模型） |
| `conflicts_with` | 冲突模型（不能同时运行） |

---

## 内置模型

| 模型 | API 路径 | 分类 |
|------|---------|------|
| 太阳位置模型 | `POST /api/run/solar_position` | 太阳位置 |
| 辐照分离模型 | `POST /api/run/irradiance_split` | 辐照分离 |
| 光伏转换模型 | `POST /api/run/pv_conversion` | 光伏转换 |
| 反射损失模型 | `POST /api/run/reflection` | 光学修正 |

---

## 数据库表结构

系统启动时自动创建以下数据表：

| 表名 | 用途 |
|------|------|
| `model_records` | 模型注册信息主表 |
| `model_relations` | 模型关系表（四类关系） |
| `execution_logs` | 模型执行日志表 |
| `pvpanel`（或对应表名） | 光伏组件信息表（来自 `.pan` 文件） |
| `inverter`（或对应表名） | 逆变器信息表（来自 `.ond` 文件） |
| `users` | 用户账号表 |

---

## 常见问题排查

**端口被占用：​**
修改 `docker-compose.yml` 中的端口映射，或本地启动时修改 `app.py` 中的 `port` 参数。

**数据库连接失败：​**
检查 `.env` 文件中的数据库配置是否正确，确认 MySQL 服务已启动，并确认数据库 `pv_gateway` 已创建。

**Docker 启动报错（init.sql 不存在）：​**
`docker-compose.yml` 中默认挂载了 `./mysql/init.sql`，若该文件不存在会导致 MySQL 容器启动失败。可在项目根目录执行：
```bash
mkdir -p mysql && touch mysql/init.sql
```
或直接注释掉 `docker-compose.yml` 中对应的 `volumes` 挂载行。

**模型加载失败：​**
检查 `backend/models_repo/` 下各模型目录是否同时存在 `meta.py` 和 `model.py`，缺少任意一个该模型会被跳过。

**前端代理不生效：​**
本地开发时前端请求通过 `vite.config.js` 中的 proxy 转发到 `localhost:8080`，确保后端已先行启动。Docker 模式下由 nginx 负责转发，无需关心此问题。

**pvlib 安装慢：​**
可以使用国内镜像源加速：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**datetime 格式错误：​**
时间参数需要包含时区信息，推荐格式为 `2024-06-21T12:00:00+08:00`。

---

## 项目结构

```
pv-model-gateway/
├── backend/
│   ├── api/
│   │   ├── auth_routes.py      # 用户认证接口
│   │   ├── model_routes.py     # 模型管理接口
│   │   ├── execute_routes.py   # 模型执行接口
│   │   ├── panel_routes.py     # 光伏组件接口
│   │   └── inverter_routes.py  # 逆变器接口
│   ├── core/
│   │   ├── registry.py         # 模型注册中心
│   │   ├── executor.py         # 模型执行引擎
│   │   ├── validator.py        # 代码校验器
│   │   ├── auth.py             # 认证工具（密码哈希等）
│   │   ├── sandbox.py          # 沙箱执行环境
│   │   ├── pan_parser.py       # .pan 文件解析器
│   │   ├── ond_parser.py       # .ond 文件解析器
│   │   └── iv_curve.py         # IV 曲线计算
│   ├── db/
│   │   ├── database.py         # 数据库连接与初始化
│   │   ├── models.py           # 模型 ORM
│   │   ├── panel.py            # 光伏组件 ORM
│   │   ├── inverter.py         # 逆变器 ORM
│   │   └── users.py            # 用户 ORM
│   ├── models_repo/            # 模型文件目录
│   │   └── {model_name}/
│   │       ├── meta.py
│   │       └── model.py
│   ├── panels_repo/            # 光伏组件 .pan 文件目录
│   ├── inverters_repo/         # 逆变器 .ond 文件目录
│   ├── app.py                  # 应用入口
│   ├── config.py               # 配置管理
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── components/         # 通用组件
│   │   └── api/                # API 封装
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── model_relations.sql
└── README.md
```
