Signal Container
-----

[English(英文)](README.md) | **中文**

获取指定信号强度的容器的 MCDR 插件


# 基本命令

`!!sig` 获取帮助信息

`!!sig get <信号>` 获取输出指定红石信号强度的容器

`!!sig give <玩家> <信号> [-U]` 给予其他玩家指定的容器, 使用 `-U` 参数以使用你当前的偏好生成该容器，而非使用对方的

# 自定义偏好

部分配置项可在游戏内修改，并具有全局和个人偏好值

`!!sig cfg list` 列出所有配置项

`!!sig cfg info <键>` 获取配置项信息

`!!sig cfg set <键> <值>` 设定自己的偏好配置项值

`!!sig cfg set-global <键> <值>` 设定全局配置值

游戏内可修改的配置:

`container_item`: 容器物品 ID, 默认为木桶 (`minecraft:barrel`), 此处仅指定 id, 若指定的容器格子数量与原配置项不同，则须确认 `max_slots`

`max_slots`: 指定的容器具有的格子数量

`allow_overstack_under_15`: 若此项启用，则任意情况下都可以用过堆叠的不可堆叠物品填充容器

`unstackable_fillings`: 设置填充容器的不可堆叠物品

`stackable_fillings`: 设置填充容器的可堆叠物品

# 插件配置

插件配置文件位于 `config/signal_container/config.json`

插件配置项：

`permission`: 若玩家具有低于表中值的权限等级，则不可执行对应的指令

`prefix`: 指令前缀, 默认为 `!!sig`, 这意味着上文所述的所有指令中的 `!!sig` 均会被本项配置值替换
