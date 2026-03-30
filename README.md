# PV Model Gateway — 光伏模型网关

将光伏 Python 模型自动转化为 RESTful API 服务，支持在线编辑、校验与调试。

## 运行方式：
Docker 一键启动（推荐）或本地手动启动


### **方式一：Docker 启动（推荐）**

确保本机已安装 Docker 和 Docker Compose，然后在项目根目录执行：

```bash
# 1. 克隆项目
git clone <your-repo-url>
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

### **方式二：本地手动启动**

#### **第一步：启动后端**

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

后端启动后，终端会输出类似如下日志，说明模型已自动加载：

```
INFO  初始化数据库...
INFO  扫描并加载模型...
INFO  已加载模型: solar_position (太阳位置模型)
INFO  已加载模型: irradiance_split (辐照分离模型)
INFO  已加载模型: pv_conversion (光伏转换模型)
INFO  已加载模型: reflection (反射损失模型)
INFO  启动完成，已加载模型: ['solar_position', 'irradiance_split', 'pv_conversion', 'reflection']
```

#### **第二步：启动前端**

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



### **验证服务是否正常**

后端启动后，可以用 curl 或 Postman 直接测试任意模型接口：

```bash
# 测试太阳位置模型
curl -X POST http://localhost:8080/api/run/solar_position \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 39.9,
    "longitude": 116.4,
    "datetime": "2024-06-21T12:00:00",
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

### **常见问题排查**

**端口被占用：** 修改 `docker-compose.yml` 中的端口映射，或本地启动时修改 `app.py` 中的 `port` 参数。

**模型加载失败：** 检查 `backend/models_repo/` 下各模型目录是否同时存在 `meta.py` 和 `model.py`，缺少任意一个该模型会被跳过。

**前端代理不生效：** 本地开发时前端请求通过 `vite.config.js` 中的 proxy 转发到 `localhost:8080`，确保后端已先行启动。Docker 模式下由 nginx 负责转发，无需关心此问题。

**pvlib 安装慢：** 可以使用国内镜像源加速：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```


## 新增模型（3步）

1. 在前端点击「新增模型」，填写 `meta.py` 和 `model.py`
2. 点击「校验代码」通过后，点击「发布模型」
3. API 自动注册，立即可用：`POST /api/run/{model_name}`

## 模型编码规范

每个模型由两个文件组成，放置于 `backend/models_repo/{model_name}/` 目录：

| 文件 | 职责 |
|------|------|
| `meta.py` | 定义 `MODEL_META` 字典，描述输入输出 |
| `model.py` | 实现 `run(inputs: dict) -> dict` 函数 |

## 内置模型

| 模型 | API 路径 |
|------|---------|
| 太阳位置模型 | `POST /api/run/solar_position` |
| 辐照分离模型 | `POST /api/run/irradiance_split` |
| 光伏转换模型 | `POST /api/run/pv_conversion` |
| 反射损失模型 | `POST /api/run/reflection` |
