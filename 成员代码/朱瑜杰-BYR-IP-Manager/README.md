# BYR_IP_manager

BYRteam后端招新第三题 by PYthok

使用python Django。

## 接口示例

(省略了很多各种奇奇怪怪的responce，在此只展示成功和典型示例)

### GET /auth/feishu/redirect

重定向至飞书授权页面完成OAuth2.0认证。

相当于登录界面，未登录OAuth2.0将会被重定向至此。

##### request: NONE

##### responce: 302

![01b00b54-6627-45ff-968d-bc63761c1558](README/01b00b54-6627-45ff-968d-bc63761c1558.png)



### GET /auth/feishu/callback

OAuth2.0回调接口，返回用户基本信息和user_access_token。

使用open_id在django调用login()并存入数据库。

![055df2fa33f49f2e244a08951d216213](README/055df2fa33f49f2e244a08951d216213.png)

##### request: 

```
code=515s9b5c0fe24f4b980ca97bc068ba0c
state=2254a527-6a5c-448d-8223-14a809f3e33e
```

##### responce:

```json
{
    "message": "Login successful",
    "user_info": {
        "avatar_big": "https://s1-imfile.feishucdn.com/static-resource/v1/v3_00b4_a178ade0-8884-4acd-aff4-53886e5ccb1g~?image_size=640x640&cut_type=&quality=&format=image&sticker_format=.webp",
        "avatar_middle": "https://s3-imfile.feishucdn.com/static-resource/v1/v3_00b4_a178ade0-8884-4acd-aff4-53886e5ccb1g~?image_size=240x240&cut_type=&quality=&format=image&sticker_format=.webp",
        "avatar_thumb": "https://s1-imfile.feishucdn.com/static-resource/v1/v3_00b4_a178ade0-8884-4acd-aff4-53886e5ccb1g~?image_size=72x72&cut_type=&quality=&format=image&sticker_format=.webp",
        "avatar_url": "https://s1-imfile.feishucdn.com/static-resource/v1/v3_00b4_a178ade0-8884-4acd-aff4-53886e5ccb1g~?image_size=72x72&cut_type=&quality=&format=image&sticker_format=.webp",
        "en_name": "pythok",
        "name": "pythok",
        "open_id": "ou_39e21847de22b42e2066d631f2bfd46b",
        "tenant_key": "",
        "union_id": "on_"
    },
    "user_access_token": "u-"
}
```



### POST /bind

绑定设备，根据当前ip写入数据库, 显示 token。

![20cd5bbb-e32d-4653-8cd1-0ece53e48a0a](README/20cd5bbb-e32d-4653-8cd1-0ece53e48a0a.png)

##### request:

```json
{
    "open_id":"ou_39e21847de22b42e2066d631f2bfd46b"
}
```

##### responce:

```json
{
"status": "success", 
"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvcGVuX2lkIjoib3VfMzllMjE4NDdkZTIyYjQyZTIwNjZkNjMxZjJiZmQ0NmIiLCJpcCI6IjEwLjEyMi4yNDcuODQiLCJleHAiOjE3MjY5MDc5NjguMjM1NzgyfQ.CHsWs3mHSrDAXHszB_lY2hU02R6nJU-hPIQtBdPwKb0"
}
```

```json
{
    "status": "failed",
    "msg": "Device already bound."
}
```



### POST /verify

解码token，查询数据库，验证设备是否被绑定。

![10af475e-a463-4d47-80a3-3248b0fc81b7](README/10af475e-a463-4d47-80a3-3248b0fc81b7.png)

##### request:

```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvcGVuaWQiOiJvdV8zOWUyMTg0N2RlMjJiNDJlMjA2NmQ2MzFmMmJmZDQ2YiIsImlwIjoiMTI3LjAuMC4xIiwiZXhwIjoxNzI2NjQ1MDkzLjAzMTQ1fQ.zOZ3TiZ_WAuwwV0vkhOgdHxrY_mGcZKCjKABaz5K424"
}

```

##### responce:

```json
{
"status": "success", 
"msg": "Device bound successfully", 
"device_id": 1
}
```

```json
{
    "msg": "Invalid token"
}
```



### DELETE  /devices/\<int:device_id>

解绑设备。![a374561a-93a7-4fb6-a929-ce3cfce5eb86](README/a374561a-93a7-4fb6-a929-ce3cfce5eb86.png)

##### request: NONE

##### responce:

```json
{
    "status": "success",
    "message": "Device unbound successfully"
}
```



### GET /devices/\<int:device_id>/login

登录设备。

由于302重定向之后视图函数本身不会再进行任何操作，所以在这里使用了thread多线程延迟发包，使得用户先重定向到监听界面，然后直接发包显示登录请求，实现了自动重定向，发包，返回改数据库的过程，全程只需要点击确定。

登录之后，Gateway上的login.ts会直接向10.3.8.211发包（其实还有反代），因此无需更多操作。

登录后即可连接校园网。

**关于保活(KeepAlive)** 后面会详细解释。

![QQ2024916-16646 (1)](README/QQ2024916-16646.gif)

##### request: 

```
open_id=ou_39e21847de22b42e2066d631f2bfd46b
```

##### responce: 302

（返回写入数据库由内置的另一个函数解决 其实只是简单的http.client 朴实无华 没什么好说的XD 这个应该看到的各位都会吧）



### GET /devices/\<int:device_id>/logout

登出设备断连校园网。

匹配成功后会先向10.3.8.211/logout发出请求退出登录，然后再修改数据库logged_in为False，保活也会断开。

![image-20240919205046881](README/image-20240919205046881.png)

![image-20240919205035859](README/image-20240919205035859.png)![image-20240919205245513](README/image-20240919205245513.png)

![image-20240919205222029](README/image-20240919205222029.png)

##### request: 

```json
{
    "open_id":"ou_39e21847de22b42e2066d631f2bfd46b"
}
```

##### responce:

```json
{
    "status": "success", 
    "message": "Device logged out successfully"
}
```

```json
{
    "status": "failed", 
    "message": "Method not allowed"
}
```



### GET  /devices

显示当前设备列表，无论是登录还是登出。

简单，不多说了。

##### request: 

```json
{
    "open_id":"ou_39e21847de22b42e2066d631f2bfd46b"
}
```

##### responce: 

```json
{
    "status": "success",
    "devices": [
        {
            "id": 1,
            "ip": "127.0.0.1",
            "logged_in": false
        }
    ]
}
```

## 食用指北

jwt_key记得改，settings.py里是默认。

在根目录新增.env文件，填写

```
FEISHU_APP_ID=
FEISHU_REDIRECT_URI=
FEISHU_APP_SECRET=
```

```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0
```



## 设计思路

整体上是django，django就难免用视图模型这些，太空泛了不多说。

其实没啥思路吧，就需求什么接口做什么接口就完事了，避免接口串通。

### 关于保活

题目提示，无流量就会退出校园网，所以一直有流量就不会退出，怎么保持一直有流量呢？

其实仔细留意login.conf就会发现是一个反代，在这里我修改了正则表达式，加了一个index然后重启了一下。

![6285e253-26f6-44d0-a69c-44f87a853d58](README/6285e253-26f6-44d0-a69c-44f87a853d58.png)

这个是假的，懒得找图了，就那个loginn改成index

（其实也一样的 10.3.8.211只要不是login和logout都会跳转到index，不信你试试）

![image-20240919212507679](README/image-20240919212507679.png)

所以就变成了定时向10.3.8.211/index发包，加一个定时任务就可以了，我用的是crontab，给我折腾半天。

对了，这个定时任务的断开时间是玄学问题，建议设置在1h-30min

## 实现时遇到的问题

好多道槛。

第一个是飞书授权，那个OAuth2.0不好调试，所以Apifox整个就没法用了，基本都是用浏览器或者Burp Suite调的，然后那个授权过程也挺复杂，也可能是我太傻了。

第二个是登录状态，既然把登录搞出来了，那肯定要搞登录状态，因为是飞书授权，所以整个用户类型都得自定义，没有密码，简单搞一下，然后套一个@login_request就结束了。

第三个是重定向+异步发包，众所周知Django302跳转完这个函数就结束了。我希望就是，这个接口一点进去，就可以重定向到监听界面，然后这个后端还能帮我发包，我只需要点击登录就可以了，但是这个实现其实挺复杂。当时requests试过了，celery试过了，都不太行，最后是用http.client和thread配合，然后套了一个time.sleep(3)延迟一下（太丑陋了！），实现了这个异步的发包。

第四个就是部署，其实是我太弱智了，也麻烦了youxam很久，弱智就是弱智没什么好说的。

第五个就是保活，说过了。

## TODO / 优缺点分析

1. 发openid的json来请求接口其实不太严谨？用token应该会更好，但是反应过来的时候已经快写完了，如果被采用了就重构一下吧。

2. 那个设备登录，有极小概率会看到请求两次，原因不明，回头调一下，但是不影响功能就是了。

3. 那个time.sleep(3),就是那个重定向异步发包login那个，太丑陋了！但是我也没有找到更优雅的办法 T_T

4. 毕竟是第一次写小中型后端，感觉难免在格式上和流行的习惯有出入，希望大佬多多指出。

   我个人觉得优点就是飞书鉴权，重定向异步的login，以及保活，确实花时间了。

## 心路历程

太菜了，把整个中秋干进去了，确实有很多东西是现学的，但是现在已经尽力做到最好，也算功德完满了。

非常感谢Youxam的悉心指导！
