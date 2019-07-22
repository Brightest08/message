#### 短信发送小助手

- 项目使用:
    - 下载项目代码 git clone https://github.com/Brightest08/message
    - 修改docker-compose.yaml文件，配置es、mysql、账号密码，也可以使用默认配置直接启动
    - docker-compose up -d 将自动下载镜像并启动服务，使用到的镜像有：
        - 1、elasticsearch - 用于收集短信发送日志，便于分析短信接口是否异常，和统计用户短信发送情况
        - 2、mysql - 存储短信接口信息、用户信息
        - 3、redis - 从mysql中读取并保存短信接口信息，用于缓存，保存用户登录信息
        - 4、kibana - 图形化展示es中的数据
        - 5、message - 短信发送镜像
    - 登录验证,默认用户名密码为admin,可以在首次启动MySQL时修改data/mysql/init/init.sql默认值
    ```
    [root@host message]# ./bin/message
    未登录或登录信息已过期
    请输入用户名:admin
    请输入密码:
    登陆成功,请继续使用
    ```
    - 运行测试 
    ```
    [root@host message]# ./bin/message -m 手机号码 -c 短信发送条数
    2019-07-22 21:58:49 morequick {"ret":1,"data":"ok"}
    ```
    - 登录kibana查看发送日志,登录需要用户认证,默认用户名密码为message,可以在docker-compose.yaml中进行修改
    
      ![image](https://github.com/Brightest08/test/blob/master/kibana.png)
	
- 目录对应说明
  - bin - 短信发送脚本
  - data - 各个数据库数据存放位置，还有mysql的初始化建表sql
  - dockerfile - 构建镜像的dockerfile
  - source - 源代码存放位置
  
- 流程图
  -! [image](https://github.com/Brightest08/test/blob/master/process.png)

- 项目声明：
  - 本项目只供学习交流使用，务作为非法用途
