<!-- markdownlint-disable MD033 -->
# MinecraftItemAPI

这是一个管理Minecraft物品的API, 提供Minecraft物品的抽象类

## 使用

导入: `from plugins.MinecraftItemAPI import *`

## Item

实例化: `Item(item_id)`

`item_id`: Minecraft 物品id, 物品列表可以在[这里](https://minecraft.gamepedia.com/Item)找到

### 输出

| 函数 | 功能 | 参数 |
| - | - | - |
| to_nbt | 获取nbt的dict | 无 |
| to_json_object | 获取共通标签的dict | 无 |
| to_tags_common | 获取物品共通标签的str | 无 |
| to_give_command | 获取give指令的str | `player`: 玩家名或目标选择器 |
| to_setblock_command | 获取setblock指令的str | `x`: x轴坐标<br>`y`: y轴坐标<br>`z`: z轴坐标 |
| give | 给予物品 | `server`: MCDR提供的`server`对象<br>`player`: 玩家名或目标选择器 |
| setblock | 放置方块 | `server`: MCDR提供的`server`对象<br>`x`: x轴坐标<br>`y`: y轴坐标<br>`z`: z轴坐标

### 基本属性

| 函数 | 功能 | 参数 |
| - | - | - |
| set_count | 设置堆叠在当前物品栏中的物品数量 | `count`: 数量, 支持int |
| set_slot | 设置物品槽位 | `slot`: 槽位, 支持int |
| set_tag | 设置物品标签 | `*args`: 物品标签名, 支持str |

### 通用标签/显示属性

| 函数 | 功能 | 参数 |
| - | - | - |
| set_damage | 设置物品的数据值(耐久) | `value`: 数据值 |
| set_unbreakable | 设置物品无法破坏 | `value`: 设置为True物品无法破坏, 默认参数为True |
| set_can_destroy | 设置物品可破坏列表 | `*args`: 物品id, 支持Item或str |
| set_custom_model_data | 设置用于物品模型的 overrides 属性中的物品标签 custom_model_data | `data`: 一个int |
| set_color | 设置皮革盔甲的颜色 | `red`: 红色(0-255)<br>`green`: 绿色(0-255)<br>`blue`: 蓝色(0-255) |
| set_name | 设置物品名称 | `name`: 物品名称, 支持str或RTextBase |
| set_lore | 设置物品信息 | `*args`: 物品信息的一行, 支持str或RTextBase |
| set_hide_flags | 设置隐藏属性 | `*args`: 隐藏属性的值, 建议使用[HideFlags](#HideFlags)的属性 |

### 方块标签

| 函数 | 功能 | 参数 |
| - | - | - |
| set_can_place_on | 设置物品可放置列表 | `*args`: 物品id, 支持Item或str |
| set_block_entity_tag | 设置方块实体标签 | `data`: 标签内容, 支持dict或[BlockEntity](#BlockEntity) |

### 附魔

| 函数 | 功能 | 参数 |
| - | - | - |
| add_enchantment | 添加附魔属性 | `enchantment`: 附魔名称, 支持[Enchantments](#Enchantments)或str<br>`level`: 附魔等级
| set_enchantments | 设置附魔属性 | `enchantment`: 附魔名称, 支持[Enchantments](#Enchantments)或dict |
| convert_stored_enchantments | 将附魔属性修改为存储的附魔属性 | 无 |
| set_repair_cost | 设置已修复次数 | `cost`: 次数, 支持int |

### 属性修饰符 做不了

| 函数 | 功能 | 参数 |
| - | - | - |
| set_attribute_modifiers | 设置属性修饰符 | `data`: 修饰符属性 |

### 药水效果

| 函数 | 功能 | 参数 |
| - | - | - |
| set_custom_potion_effect | 设置所含的状态效果 | `*args`: 效果id, 支持int或[Status](#Status) |
| set_potion | 设置默认药水效果的名称 | `potion`: 效果名称, 支持str或[Potion](#Potion)的属性 |
| set_custom_potion_color | 物品使用该颜色, 范围效果云/箭/喷溅药水/滞留药水会使用该值作为其颗粒效果颜色 | `red`: 红色(0-255)<br>`green`: 绿色(0-255)<br>`blue`: 蓝色(0-255) |

### 弩

| 函数 | 功能 | 参数 |
| - | - | - |
| set_charged_projectiles | 设置弩装填的物品, 默认一个, 最多3个(多重射击附魔) | `*args`: 物品共通标签, 支持dict或Item |
| set_charged | 设置弩的装填状态 | `charged`: 装填状态, 默认为Treu, 支持bool |

### 书

| 函数 | 功能 | 参数 |
| - | - | - |
| set_generation | 设置成书的副本级别 | `level`: 0表示原作; 1表示原作的副本; 2表示副本的副本; 3表示破烂不堪<br>如果值大于1, 书就不可以被复制<br>支持int |
| set_author | 设置成书的作者 | `author`: 作者, 支持str |
| set_title | 设置成书的标题 | `title`: 标题, 支持str |
| set_pages | 设置书页 | `*args`: 每页的内容, 支持str或RTextBase |

### 玩家的头颅

暂时不做

### 烟花火箭

做不了

### 盔甲架/刷怪蛋/鱼桶

| 函数 | 功能 | 参数 |
| - | - | - |
| set_entity_tag | 设置创建实体时应用于实体上的实体数据 | `data`: 实体共通标签, 支持dict |
| set_bucket_variant_tag | 设置桶中热带鱼的种类数据 | `value`: [种类数据](https://minecraft-zh.gamepedia.com/%E7%83%AD%E5%B8%A6%E9%B1%BC#.E5.AE.9E.E4.BD.93.E6.95.B0.E6.8D.AE), 支持int |

### 地图

| 函数 | 功能 | 参数 |
| - | - | - |
| set_map | 设置地图编号 | `value`: 地图编号, 支持int |

### 迷之炖菜

| 函数 | 功能 | 参数 |
| - | - | - |
| add_effect | 添加迷之炖菜的状态效果 | `effect_id`: 状态效果的id, 支持int或[Status](#Status)的属性<br>`duration`: 效果持续的刻数 |

### 调试棒

| 函数 | 功能 | 参数 |
| - | - | - |
| add_debug_property | 添加调试棒编辑的方块和其状态 | `block`: 方块名, 支持str或Item<br>`state`: 状态, 支持str |

### 指南针

| 函数 | 功能 | 参数 |
| - | - | - |
| set_lodestone_tracked | 设置指南针是否绑定到一个磁石 | `value`: 绑定状态, 默认为True, 支持bool |
| set_lodestone_dimension | 设置磁石指针指向的坐标的所在维度 | `dim`: 维度名, 支持str |
| set_lodestone_pos | 设置磁石指针指向的坐标 | `x`: x坐标<br>`y`: y坐标<br>`z`: z坐标 |

## HideFlags

存储隐藏属性的数值

| 属性 | 值 | 说明 |
| - | - | - |
| Enchantments | 1 | 附魔 |
| AttributeModifiers | 2 | 属性 |
| Unbreakable | 4 | 无法破坏 |
| CanDestroy | 8 | 可破坏列表 |
| CanPlaceOn | 16 | 可放置列表 |
| Other | 32 | 其他 |

## Color

存储颜色对应的数值

| 属性 | 值 |
| - | - |
| white | 0 |
| orange | 1 |
| magenta | 2 |
| light_blue | 3 |
| yellow | 4 |
| lime | 5 |
| pink | 6 |
| gray | 7 |
| light_gray | 8 |
| cyan | 9 |
| purple | 10 |
| blue | 11 |
| brown | 12 |
| green | 13 |
| red | 14 |
| black | 15 |

## Pattern

存储旗帜的图案类型

[参考资料](https://minecraft-zh.gamepedia.com/%E6%97%97%E5%B8%9C#.E6.96.B9.E5.9D.97.E5.AE.9E.E4.BD.93)

| 属性 | 值 | 图案名称 | 游戏内中文名称 | 游戏内英文名称 |
| - | - | - | - | - |
| bottom_stripe | 'bs' | Bottom Stripe | 底横条 | Base |
| top_stripe | 'ts' | Top Stripe | 顶横条 | Chief |
| left_stripe | 'ls' | Left Stripe | 右竖条 | Pale dexter |
| right_stripe | 'rs' | Right Stripe | 左竖条 | Pale sinister |
| center_stripe | 'cs' | Center Stripe (Vertical) | 中竖条 | Pale |
| middle_stripe | 'ms' | Middle Stripe (Horizontal) | 中横条 | Fess |
| down_right_stripe | 'drs' | Down Right Stripe | 右斜条 | Bend |
| down_left_stripe | 'dls' | Down Left Stripe | 左斜条 | Bend sinister |
| small_stripes | 'ss' | Small (Vertical) Stripes | 竖条纹 | Paly |
| diagonal_cross | 'cr' | Diagonal Cross | 斜十字 | Saltire |
| square_cross | 'sc' | Square Cross | 正十字 | Cross |
| left_of_diagonal | 'ld' | Left of Diagonal | 右上三角 | Per bend sinister |
| right_of_upside_down_diagonal | 'rud' | Right of upside-down Diagonal | 左上三角 | Per bend |
| left_of_upside_down_diagonal | 'lud' | Left of upside-down Diagonal | 右下三角 | Per bend inverted |
| right_of_diagonal | 'rd' | Right of Diagonal | 左下三角 | Per bend sinister inverted |
| vertical_half_left | 'vh' | Vertical Half (left) | 右半方形 | Per pale |
| vertical_half_right | 'vhr' | Vertical Half (right) | 左半方形 | Per pale inverted |
| horizontal_half_top | 'hh' | Horizontal Half (top) | 上半方形 | Per fess |
| horizontal_half_bottom | 'hhb' | Horizontal Half (bottom) | 下半方形 | Per fess inverted |
| bottom_left_corner | 'bl' | Bottom Left Corner | 右底方 | Base dexter canton |
| bottom_right_corner | 'br' | Bottom Right Corner | 左底方 | Base sinister canton |
| top_left_corner | 'tl' | Top Left Corner | 右顶方 | Chief dexter canton |
| top_right_corner | 'tr' | Top Right Corner | 左顶方 | Chief sinister canton |
| bottom_triangle | 'bt' | Bottom Triangle | 底三角 | Chevron |
| top_triangle | 'tt' | Top Triangle | 顶三角 | Inverted chevron |
| bottom_triangle_sawtooth | 'bts' | Bottom Triangle Sawtooth | 底波纹 | Base indented |
| top_triangle_sawtooth | 'tts' | Top Triangle Sawtooth | 顶波纹 | Chief indented |
| middle_circle | 'mc' | Middle Circle | 圆形 | Roundel |
| middle_rhombus | 'mr' | Middle Rhombus | 菱形 | Lozenge |
| border | 'bo' | Border | 方框边 | Bordure |
| curly_border | 'cbo' | Curly Border | 波纹边 | Bordure indented |
| brick | 'bri' | Brick | 砖纹 | Field masoned |
| gradient | 'gra' | Gradient | 自上渐淡 | Gradient |
| gradient_upside_down | 'gru' | Gradient upside-down | 自下渐淡 | Base gradient |
| creeper | 'cre' | Creeper | 苦力怕盾徽 | Creeper charge |
| skull | 'sku' | Skull | 头颅盾徽 | Skull charge |
| flower | 'flo' | Flower | 花朵盾徽 | Flower charge |
| mojang | 'moj' | Mojang | Mojang徽标 | Thing |
| globe | 'glb' | Globe | 地球盾徽 | Globe |
| piglin | 'pig' | Piglin | 猪鼻 | Snout |

## StructureBlockRotation

存储结构方块的旋转角度

| 属性 | 值 | 角度 |
| - | - | - |
| none | 'NONE' | 0 |
| clockwise_90 | 'CLOCKWISE_90' | 90 |
| clockwise_180 | 'CLOCKWISE_180' | 180 |
| clockwise_270 | 'COUNTERCLOCKWISE_90' | 270 |

## StructureBlockMirror

存储结构方块的镜像方法

| 属性 | 值 |
| - | - |
| none | 'NONE' |
| left_right | 'LEFT_RIGHT' |
| front_back | 'FRONT_BACK' |

## StructureBlockMode

存储结构方块的模式

| 属性 | 值 | 名称 |
| - | - | - |
| save | 'SAVE' | 储存模式 |
| load | 'LOAD' | 加载模式 |
| corner | 'CORNER' | 角落模式 |
| data | 'DATA' | 数据模式 |

## BlockEntity

方块实体的基类

不同类型的方块实体由此类继承

[参考资料](https://minecraft-zh.gamepedia.com/%E6%96%B9%E5%9D%97%E5%AE%9E%E4%BD%93#.E6.96.B9.E5.9D.97.E5.AE.9E.E4.BD.93.E5.88.97.E8.A1.A8)

| 函数 | 功能 | 参数 |
| - | - | - |
| to_json_object | 获取数据的dict | 无 |

### Beehive

蜂箱和蜂巢

| 函数 | 功能 | 参数 |
| - | - | - |
| set_flower_pos | 设置花的坐标 | `x`: x坐标<br>`y`: y坐标<br>`z`: z坐标 |
| set_bees | 设置巢内存在的实体 | `*args`: 实体共通标签, 支持dict |

### Sign

告示牌

| 函数 | 功能 | 参数 |
| - | - | - |
| set_text | 设置单行文本 | `line`: 行数, 支持int<br>`text`: 内容, 支持str或RTextBase |
| set_color | 设置告示牌颜色 | `color`: 颜色, 支持str |

### Banner

旗帜

| 函数 | 功能 | 参数 |
| - | - | - |
| set_custom_name | 设置名称 | `name`: 名称, 支持str或RTextBase |
| add_pattern | 添加旗帜上的图案 | `color`: 颜色的值, 支持int或[Color](#Color)的属性<br>`pattern`: 图案类型, 支持str或[Pattern](#Pattern)的属性 |

### Container

容器

| 函数 | 功能 | 参数 |
| - | - | - |
| set_custom_name | 设置名称 | `name`: 名称, 支持str或RTextBase |
| set_lock | 设置容器锁 | `lock`: 钥匙的名字, 支持str |
| set_items | 设置容器内物品列表 | `*args`: 物品共通标签, 支持dict或Item |
| set_loot_table | 设置战利品表 | `table`: 战利品表路径, 支持str, [参考资料](https://minecraft-zh.gamepedia.com/%E6%88%98%E5%88%A9%E5%93%81%E8%A1%A8) |
| set_loot_table_seed | 设置战利品表种子 | `seed`: 种子, 支持int |
| set_burn_time | 设置距离燃料烧完的刻数 | `time`: 刻数, 支持int |
| set_cook_time | 设置物品已烧炼的刻数 | `time`: 刻数, 支持int |
| set_cook_time_total | 设置烧炼物品的所需的总刻数 | `time`: 刻数, 支持int |
| add_recipes | 设置熔炉已烧制物品列表 | `recipe`: 配方名称, 支持str或Item<br>`time`: 烧制次数 |
| set_crew_time | 设置酿造剩余时间 | `time`: 刻数, 支持int |
| set_fuel | 设置酿造台剩余能量 | `fuel`: 剩余燃料(0-20), 支持int |
| set_transfer_cooldown | 设置漏斗距离下次运输的刻数 | `time`: 刻数, 支持int |
| set_book | 设置讲台上放置的书 | `book`: 书的物品共通标签, 支持dict或Item |
| set_page | 设置当前书页 | `page`: 页码, 支持int |

### Beacon

信标

| 函数 | 功能 | 参数 |
| - | - | - |
| set_level | 设置信标等级 | `level`: 等级, 支持int |
| set_primary | 设置主效果 | `status`: 效果id, 支持int或[Status](#Status)的属性 |
| set_secondary | 设置辅助效果 | `status`: 效果id, 支持int或[Status](#Status)的属性 |

### Spawner

刷怪笼

| 函数 | 功能 | 参数 |
| - | - | - |
| add_spawn_potentials | 添加实体到可能生成实体的列表 | `weight`: 权重, 支持int<br>`entity`: 实体共通标签, 支持dict |
| set_spawn_data | 设置下一组即将生成的实体的标签 | `data`: 实体共通标签, 支持dict |
| set_spawn_count | 设置每次尝试生成生物的数量 | `count`: 每次生成的数量, 支持int |
| set_spawn_range | 设置刷怪笼可以随机生成实体的范围 | `value`: 范围, 支持int |
| set_delay | 设置距离下次生成的刻数 | `delay`: 刻数, 支持int |
| set_min_spawn_delay | 设置生成延迟的随机范围的下限 | `delay`: 刻数, 支持int |
| set_max_spawn_delay | 设置生成延迟的随机范围的上限 | `delay`: 刻数, 支持int |
| set_max_nearby_entities | 设置刷怪笼周遭最大相同实体存在数量 | `value`: 数量, 支持int |
| set_required_player_range | 设置刷怪笼起效所需玩家与刷怪笼之间的最近距离 | `value`: 距离, 支持int |

### Jukebox

唱片机

| 函数 | 功能 | 参数 |
| - | - | - |
| set_record_item | 设置唱片 | `data`: 唱片的物品共通标签, 支持dict或Item |

### EnchantingTable

附魔台

| 函数 | 功能 | 参数 |
| - | - | - |
| set_custom_name | 设置名称 | `name`: 名称, 支持str或RTextBase |

### Skull

生物头颅

先不做

### CommandBlock

命令方块

| 函数 | 功能 | 参数 |
| - | - | - |
| set_custom_name | 设置名称, 在执行某些命令时替代@ | `name`: 名称, 支持str或RTextBase |
| set_command | 设置命令方块中的命令 | `command`: 命令, 支持str |
| set_success_count | 设置红石比较器输出的模拟信号强度 | `value`: 信号强度, 支持int |
| set_last_output | 设置上一个输出 | `message`: 上一个输出的信息, 支持str |
| set_track_output | 设置LastOutput是否储存 | `value`: 是否储存, 支持bool |
| set_powered | 设置是否被红石所激活 | `value`: 是否被激活, 支持bool |
| set_auto | 设置是否允许在没有红石信号的情况下激活命令(保持开启) | `value`: 是否允许, 支持bool |
| set_condition_met | 设置条件命令块在上次激活时是否满足其条件 | `value`: 是否满足, 支持bool |
| set_update_last_execution | 如果设为否, 创建循环后同一个命令方块可以在一刻内运行多次 | `value`: 是否允许, 默认为False, 支持bool |
| set_last_execution | 设置连锁型命令方块最后被执行的游戏刻 | `time`: 刻数, 支持int |

### EndGateway

末地折跃门

| 函数 | 功能 | 参数 |
| - | - | - |
| set_age | 设置末地折跃门方块的年龄 | `age`: 刻数, 支持int |
| set_exact_teleport | 设置是否把实体准确传送到指定的坐标 | `value`: 是否允许, 默认为True, 支持bool |
| set_exit_portal | 设置要传送到的位置 | `x`: x坐标<br>`y`: y坐标<br>`z`: z坐标 |

### StructureBlock

结构方块

| 函数 | 功能 | 参数 |
| - | - | - |
| set_name | 设置结构名称 | `name`: 名称, 支持str |
| set_author | 设置结构作者 | `author`: 作者, 支持str |
| set_metadata | 似乎没用 | `value`: 该属性的值, 支持str |
| set_pos | 设置结构起始坐标 | `x`: x坐标<br>`y`: y坐标<br>`z`: z坐标 |
| set_size | 设置结构大小 | `x`: x距离<br>`y`: y距离<br>`z`: z距离 |
| set_rotation | 设置旋转角度 | `value`: 角度, 支持str或[StructureBlockRotation](#StructureBlockRotation)的属性 |
| set_mirror | 设置镜像方法 |`value`: 方法, 支持str或[StructureBlockMirror](#StructureBlockMirror)的属性 |
| set_mode | 设置模式 | `value`: 模式, 支持str或[StructureBlockMode](#StructureBlockMode)的属性
| set_ignore_entities | 设置是否忽略实体 | `value`: 是否忽略, 默认为True, 支持bool |
| set_showboundingbox | 设置是否显示结构边框 | `value`: 是否显示, 默认为True, 支持bool |
| set_powered | 设置是否被红石激活 | `value`: 是否激活, 默认为True, 支持bool |

### RedstoneComparator

比较器

| 函数 | 功能 | 参数 |
| - | - | - |
| set_output_signal | 设置信号输出强度 | `strength`: 信号强度, 支持int |

### Conduit

潮涌核心

| 函数 | 功能 | 参数 |
| - | - | - |
| set_target | 设置正在攻击的生物UUID | `uuid`: UUID, 支持麻将牌list |

### Bell

钟

无特殊属性

## Enchantments

存储所有的附魔和创建附魔属性对象

[参考资料](https://minecraft-zh.gamepedia.com/%E9%99%84%E9%AD%94)

| 属性 | 值 | 名称 |
| - | - | - |
| aqua_affinity | 'minecraft:aqua_affinity' | 水下速掘 |
| bane_of_arthropods | 'minecraft:bane_of_arthropods' | 节肢杀手 |
| blast_protection | 'minecraft:blast_protection' | 爆炸保护 |
| channeling | 'minecraft:channeling' | 引雷 |
| curse_of_binding | 'minecraft:curse_of_binding' | 绑定诅咒 |
| curse_of_vanishing | 'minecraft:curse_of_vanishing' | 消失诅咒 |
| depth_strider | 'minecraft:depth_strider' | 深海探索者 |
| efficiency | 'minecraft:efficiency' | 效率 |
| feather_falling | 'minecraft:feather_falling' | 摔落保护 |
| fire_aspect | 'minecraft:fire_aspect' | 火焰附加 |
| fire_protection | 'minecraft:fire_protection' | 火焰保护 |
| flame | 'minecraft:flame' | 火矢 |
| fortune | 'minecraft:fortune' | 时运 |
| frost_walker | 'minecraft:frost_walker' | 冰霜行者 |
| impaling | 'minecraft:impaling' | 穿刺 |
| infinity | 'minecraft:infinity' | 无限 |
| knockback | 'minecraft:knockback' | 击退 |
| looting | 'minecraft:looting' | 抢夺 |
| loyalty | 'minecraft:loyalty' | 忠诚 |
| luck_of_the_sea | 'minecraft:luck_of_the_sea' | 海之眷顾 |
| lure | 'minecraft:lure' | 饵钓 |
| mending | 'minecraft:mending' | 经验修补 |
| multishot | 'minecraft:multishot' | 多重射击 |
| piercing | 'minecraft:piercing' | 穿透 |
| power | 'minecraft:power' | 力量 |
| projectile_protection | 'minecraft:projectile_protection' | 弹射物保护 |
| protection | 'minecraft:protection' | 保护 |
| punch | 'minecraft:punch' | 冲击 |
| quick_charge | 'minecraft:quick_charge' | 快速装填 |
| respiration | 'minecraft:respiration' | 水下呼吸 |
| riptide | 'minecraft:riptide' | 激流 |
| sharpness | 'minecraft:sharpness' | 锋利 |
| silk_touch | 'minecraft:silk_touch' | 精准采集 |
| smite | 'minecraft:smite' | 亡灵杀手 |
| soul_speed | 'minecraft:soul_speed' | 灵魂疾行 |
| sweeping_edge | 'minecraft:sweeping_edge' | 横扫之刃 |
| thorns | 'minecraft:thorns' | 荆棘 |
| unbreaking | 'minecraft:unbreaking' | 耐久 |

实例化: `Enchantments(enchantment, level)`

`enchantment`: 为一个附魔名称, 可以使用本类的属性

`level`: 为附魔的等级数值

## AttributesSlots

存储槽位名称

| 属性 | 值 | 名称 |
| - | - | - |
| mainhand | 'mainhand' | 主手 |
| offhand | 'offhand' | 副手 |
| feet | 'feet' | 足部 |
| legs | 'legs' | 腿部 |
| chest | 'chest' | 胸部 |
| head | 'head' | 头部 |

## Attributes

暂时做不了

## Status

存储状态效果

[参考资料](https://minecraft-zh.gamepedia.com/%E7%8A%B6%E6%80%81%E6%95%88%E6%9E%9C)

| 属性 | 值 | 名称 |
| - | - | - |
| speed | 1 | 速度 |
| slowness | 2 | 缓慢 |
| haste | 3 | 急迫 |
| mining_fatigue | 4 | 挖掘疲劳 |
| strength | 5 | 力量 |
| instant_health | 6 | 瞬间治疗 |
| instant_damage | 7 | 瞬间伤害 |
| jump_boost | 8 | 跳跃提升 |
| nausea | 9 | 反胃 |
| regeneration | 10 | 生命恢复 |
| resistance | 11 | 抗性提升 |
| fire_resistance | 12 | 防火 |
| water_breathing | 13 | 水下呼吸 |
| invisibility | 14 | 隐身 |
| blindness | 15 | 失明 |
| night_vision | 16 | 夜视 |
| hunger | 17 | 饥饿 |
| weakness | 18 | 虚弱 |
| poison | 19 | 中毒 |
| wither | 20 | 凋零 |
| health_boost | 21 | 生命提升 |
| absorption | 22 | 伤害吸收 |
| saturation | 23 | 饱和 |
| glowing | 24 | 发光‌‌ |
| levitation | 25 | 飘浮 |
| luck | 26 | 幸运‌‌ |
| unluck | 27 | 霉运‌‌ |
| slow_falling | 28 | 缓降 |
| conduit_power | 29 | 潮涌能量 |
| dolphins_grace | 30 | 海豚的恩惠‌‌ |
| bad_omen | 31 | 不祥之兆 |
| hero_of_the_village | 32 | 村庄英雄 |

实例化: `Status(status_id, amplifier: int = 0, duration: int = 200, ambient: bool = False, show_particles: bool = True, show_icon: bool = True)`

`status_id`: 效果的数字ID, 可使用该类的属性

`amplifier`: 效果的倍率, 等级1的值为0

`duration`: 效果的持续时长刻数

`ambient`: 如果效果由信标施加, 那么为true

`show_particles`: 如果显示颗粒效果, 那么为true

`show_icon`: 如果效果图标显示, 那么为true

## Potion

存储默认药水效果的名称

[参考资料](https://minecraft-zh.gamepedia.com/%E8%8D%AF%E6%B0%B4#.E7.89.A9.E5.93.81.E6.95.B0.E6.8D.AE)

| 属性 | 值 | 名称 |
| - | - | - |
| water | 'water' | 水瓶 |
| mundane | 'mundane' | 平凡的药水 |
| thick | 'thick' | 浑浊的药水 |
| awkward | 'awkward' | 粗制的药水 |
| night_vision | 'night_vision' | 夜视 |
| long_night_vision | 'long_night_vision' | 夜视延长版 |
| invisibility | 'invisibility' | 隐身 |
| long_invisibility | 'long_invisibility' | 隐身延长版 |
| leaping | 'leaping' | 跳跃 |
| strong_leaping | 'strong_leaping' | 跳跃II |
| long_leaping | 'long_leaping' | 跳跃延长版 |
| fire_resistance | 'fire_resistance' | 抗火 |
| long_fire_resistance | 'long_fire_resistance' | 抗火延长版 |
| swiftness | 'swiftness' | 迅捷 |
| strong_swiftness | 'strong_swiftness' | 迅捷II |
| long_swiftness | 'long_swiftness' | 迅捷延长版 |
| slowness | 'slowness' | 缓慢 |
| long_slowness | 'long_slowness' | 缓慢延长版 |
| water_breathing | 'water_breathing' | 水肺 |
| long_water_breathing | 'long_water_breathing' | 水肺延长版 |
| healing | 'healing' | 治疗 |
| strong_healing | 'strong_healing' | 治疗II |
| harming | 'harming' | 伤害 |
| strong_harming | 'strong_harming' | 伤害II |
| poison | 'poison' | 中毒 |
| strong_poison | 'strong_poison' | 中毒II |
| long_poison | 'long_poison' | 中毒延长版 |
| regeneration | 'regeneration' | 再生 |
| strong_regeneration | 'strong_regeneration' | 再生II |
| long_regeneration | 'long_regeneration' | 再生延长版 |
| strength | 'strength' | 力量 |
| strong_strength | 'strong_strength' | 力量II |
| long_strength | 'long_strength' | 力量延长版 |
| weakness | 'weakness' | 虚弱 |
| long_weakness | 'long_weakness' | 虚弱延长版 |
| luck | 'luck' | 幸运 |
| slow_falling | 'slow_falling' | 缓降 |
| strong_slow_falling | 'strong_slow_falling' | 缓降II |
| long_slow_falling | 'long_slow_falling' | 缓降延长版 |
| turtle_master | 'turtle_master' | 神龟 |
| strong_turtle_master | 'strong_turtle_master' | 神龟II |
| long_turtle_master | 'long_turtle_master' | 神龟延长版 |

## Explosion

暂时做不了
