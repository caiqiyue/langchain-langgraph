# <center>第三阶段、 Agent Chat CLI 工具介绍


&emsp;&emsp;Agent Chat UI 是 LangGraph/LangChain 官方提供的多智能体前端对话面板，用于与后端 Agent（Graph 或 Chain）进行实时互动，支持上传文件、多工具协同、结构化输出、多轮对话、调试标注等功能。
* 项目主页：https://github.com/langchain-ai/agent-chat-ui

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251224102530349.png" width=90%></div>


### Step 1. Git克隆项目：



```bash
git clone https://github.com/langchain-ai/agent-chat-ui.git

cd agent-chat-ui
```

### Step 2. 安装npm、node.js


Windows系统升级Node.js：

1. 访问官网下载LTS版本（长期支持版本）：https://nodejs.org/en/download/

2. 运行安装程序并覆盖旧版本

3. 重启命令提示符后验证：bash复制

4. node.js官网：https://nodejs.org



```python
# 这里安装完成后查看一下node.js版本
!node -v
```

```python
# 查看npm的版本
!npm -v```

* 如果npm或者node.js版本太低，比如下面这张图中，显示npm和node.js的版本都比较低，这里需要升级一下，或者重新在官网上下载

* 推荐：使用nvm管理多个版本

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251224004018218.png" width=90%></div>


```bash

# 1. 安装nvm（如未安装）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc

# 2. 安装长期支持版(Node.js 22)
nvm install --lts

# 3. 设置为默认版本
nvm use --lts
nvm alias default lts/*

# 4. 验证升级
node -v  # 应显示 v22.x.x
npm -v   # 应显示 10.x.x

# 5. 如需安装最新npm
npm install -g npm@latest
```


### Step 3. 使用npm安装pnpm


```bash

npm install -g pnpm
pnpm -v
```


```python
# 安装完成后查看pnpm的版本
!pnpm -v```

### Step 4. 安装前端项目依赖

在项目根目录下（即包含 `package.json` 文件的目录 agent-chat-ui/）执行以下命令，安装前端项目依赖：

```bash

pnpm install
```


<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251224004018202.png" width=90%></div>

### Step 5. 开启Chat Agent UI

安装前端项目完成以后，执行下面的命令启动页面：

```bash

pnpm dev
```

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251224105242038.png" width=90%></div>

同时我们需要使用langgraph dev 命令把后端服务启动起来（没有安装的可以查看LangChain1.0第三部分安装langgraph cli）：

```bash
langgraph dev
```

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251224105911978.png" width=90%></div>

**注意**：

* `http://localhost:3000`，这是 Chat Agent UI 的访问地址，进入显示下面的页面。

* 第一个链接的URL需要填写langgraph dev启动后的服务地址，默认是`http://localhost:2024`。

* 第二个Graph ID需要填写langgraph.json文件里graphs的key，这个可以自己设置，这里是`chatbot`。

* 第三个就需要把LangSmith的API_KEY填写到对应的输入框中，这个需要和本地配置的保持一致。


<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251224105531154.png" width=90%></div>

* langgraph.json 截图
<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251224110222183.png" width=50%></div>

### Step 6.进入Chat Agent UI开始对话

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251224110845535.png" width=90%></div>
