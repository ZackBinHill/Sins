# data格式:data{'db_instance', 'value'}
# field menu外键属性enable
# 子进程执行load_data
# cell_edit.py拆分
# setItemWidget单独提出来
# inner_widget将字符串改为类
# 修改dept背景色不变
# 自动修正default field name
# project thumbnail没有自动改高度
# scrollbar样式
# status 编辑
# textEdit editfinish信号
# table_config整理
# previewlabel bug
# 表的id列
# 时间段应该是TimestampField
# 时间段edit
# 转换PostgreSQL
# infield 添加widget_attr_map
# 没有group时sort问题
# 需要新的order方法
# 加密md5
# parent children 取代seq shot等
# connection表需要created等
# processEvent优化
# on update问题
# 使用触发器记录操作历史
# 历史log detail
# current user获取方法修改(多种数据库支持)
# mysql 不支持limit与prefetch
# pgsql添加user语句
# Datefield group问题 > 使用pre_group_func
# config prefetch循环问题 > 使用PrefetchConfig
# res文件移出utils
# 缩略图全部为文件id
# Test文件移出sins文件夹
# 提交github
# 测试文件类型:
# image(png, jpg),
# text(txt, py, rv, edl),
# audio(mp3, aif),
# video(mov, mp4),
# application(pdf, word),
# 需要一个错误时显示的图片

# task 添加project外键
# 常用field列出来
# 圆形头像
# 路径类数据使用TextField
# text自动高度无效
# 数字使用lineedit错误
# celltextedit分为两个
# peewee默认logging debug
# 打开shots/all出错
# 查找最上parent
# 打开新连接
# 单外键celledit
# set_core_property重复
# api_users表
# 删除git package文件夹
# asset sequence link? > 暂时不要
# note, file连接为many

# database name作为config

# user上次登陆时间
# 使用deferredmodel
# version添加step外键
# note添加type, to_group



jpg文件无法加载
# project缩略图圆角
# media字符限制
播放器使用鼠标滚轮

优化filetypes


使用label_name
celledit属性
尽量使用单行edit tooltip显示全部
field属性全部从config文件获取
新的权限方法?
多外键celledit
单个外键celledit可编辑
# status icon referred_table 编辑 >暂时用text
# cell_edit.py分文件
style统一为常量



数据表默认过滤
advanced group
数据库搜索
可选择列的搜索框



优化查询速度prefetch 需要大量数据测试
优化表格刷新速度 > refresh速度最快为0.3s(50行全部为label), 最慢为0.5s(全部为textedit)



创建数据
File,
Department,
PermissionGroup,
ApiUser,
Person,
Status,
Project,
Group,
PipelineStep,
Sequence,
AssetType,
Tag,
Asset,
Shot,
Task,
Timelog,
Playlist,
Version,
Note,

各个数据的detail页面

# status添加description
# sequence添加status

# thumbnail应该是可编辑
# Department颜色cellwidget
# colorWheel bug
# colorwheel默认值255,255,255
# group,sort,field按钮图标
# 权限组与可编辑函数
status图标
# 统一图标尺寸48px
测试数据尽量完整
保存用户配置方法QSettings json
global setting:
database host
database port
database name
数据文件路径
rv路径
提交version自动更新shot缩略图
user setting:
登陆名
密码
窗口位置大小
表的自定义过滤方法
每个表的config
media历史
最近浏览历史
最近项目

# media为flowlayout
# media MediaWidget美化
# media scrollbar样式
media可选择
# qtcharts编译
@功能
# 文件上传
# 上传用户图片生成小尺寸.thumbnail
# previewlabel加载图片时生成.thumbnail
# PreviewLabel更名
文件的权限问题


检查所有文件, 删除无用
code style
文件, 函数说明


rv集成
安装窗口
登陆窗口
邮件系统
统计
mysql trigger
api
python3支持
添加自定义字段
自定义表
# 加载gif01
# 加载gif02
# 数据库历史记录

# 主窗口去除边框?

