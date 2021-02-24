# GXU_Spider

>多进程无脑爆杀流脚本

## 使用脚本你可以做到
:heavy_check_mark: 多服务器尝试登录\
:heavy_check_mark: 无人值守自动抢课\
:heavy_check_mark: 并发抢课提升成功率




## 说明

### 环境安装
```python
pip install -r requirements.txt
```
进入main.py 填写相应字段
```python
XUANXIUKE_TARGET = ['走进东盟', '东南亚风情', '东南亚戏剧文化',] # 支持模糊，和教务系统上面那个搜索框用法基本一致
PE_TARGET = ['游泳']
BIXIU_TARGET = ['数据库原理','计算机网络原理','	算法设计与分析（全英）']

test = SpiderOfGxu(user='1907316666', pwd='password123') #在此处填写用户名和密码 然后运行

```
## 示例

![](./img/test1.png)

