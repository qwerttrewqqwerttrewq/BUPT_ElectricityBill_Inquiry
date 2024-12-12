# BUPT_ElectricityBill_Inquiry

北邮电费查询机器人，接入


## 概要
本项目基于python开发，完成了北邮CAS Login 流程以及电费查询，以及对 [wechatbot-webhook](https://github.com/danni-cool/wechatbot-webhook)微信机器人的对接

## 部署方法
### 环境要求
Linux系统，docker，python3（requests,beautifulsoup4库）
### 1、docker配置
请确保已经按照[wechatbot-webhook](https://github.com/danni-cool/wechatbot-webhook)完成docker部署并扫码登录微信。建议的docker配置：
```bash
docker run -d --name wxBotWebhook -p 3001:3001 \
-v ~/wxBot_logs:/app/log \
-e LOGIN_API_TOKEN="qweerttrewq" \ 
dannicool/docker-wechatbot-webhook
```
### 2、首次运行
先运行一次生成config文件，请一定不要输错账号密码！(详情见24.12.11更新)如果中途选择错误请手动删除config.json中的对应项。查看是否有报错。无报错则可以直接用了，下一步持久化运行可以用你喜欢的方法，不一定用pm2
### 3、持久化
我这里使用的是pm2，因为有node环境。先运行一次npm install -g pm2，进入你放置inquiry.py和config.json的位置，运行pm2 start inquiry.py --name "mypy"，此时你的微信应该能收到一次消息并持久运行。



# 更新日志
## 2024.12.12更新
直到这时候才发现了buptelecmon这个前人已经做好的库，顿时感觉我在这做寂寞。稍微自我安慰一下吧，我自己是做前端开发的，最擅长的就是在不跟后端交流的情况下通过观察网络请求来构造API，重构前端页面，这也导致了我最开始的思路也就是一遍一遍查看CAS Login的网络请求来做的这个项目...后续是接着用这个还是说在前人基础上做，就看下一步怎么方便吧。下一步准备做主动发起查询。今天删除了代码的冗余部分。
## 2024.12.11更新
忘了修了啥。总之由于之前不小心把config.json push上去了，索性直接改了密码，这时候登录出现了验证码。。不过发现四五天之前的token拿去测试也不会过期，所以每次cas login是没必要的。但是未知原因使用原先的cookie会导致search的时候302重定向，在postman里面则表现为使用json作为payload会404，使用formdata则正常。在代码中search请求添加headers也无济于事，放弃，改回最初每次请求使用一个新的session。正常情况下你别把密码输错是不会有验证的，哪怕测试时我经常一分钟请求一次也不会触发封锁。
哦，想起来了，修复了登录后config.json部分字段消失的问题
诶，好像是上次修复的。这次能正常用就是了
## 2024.12.10更新

现在可以正式接入wechatboot-webhook了。原谅我做的仓促，只能定时查询，目前还没做发起查询的功能，但是已经可以实现消耗量、时间和功率查询了

## 2024.12.9更新

目前只是完成一个demo，解决了CAS登录认证的问题。初次需要完成配置及选择宿舍。吐槽一下先前代码谁写的……好一个drom宿舍，id和name还跟前面的不一样，而且沙河西土城公寓楼id混用（虽然目前看对我的项目没啥影响）。后续计划使用wechatbot-webhook进行开发，更多信息请见 [wechatbot-webhook](https://github.com/danni-cool/wechatbot-webhook)。
