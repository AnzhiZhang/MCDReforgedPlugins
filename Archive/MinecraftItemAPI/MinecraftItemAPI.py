# -*- coding: utf-8 -*-
import json
from mcdreforged.api.rtext import *

PLUGIN_METADATA = {
    'id': 'minecraft_item_api',
    'version': '0.0.1',
    'name': 'MinecraftItemAPI',
    'description': 'Minecraft Item API',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/Archive/MinecraftItemAPI'
}

# TODO LIST
'''
BlockEntity
玩家头 base64神奇编码先不急
烟花火箭/烟火之星 因为颜色必须用[I;num] array
Attributes 属性UUID不能没有L后缀
'''


class Item:
    """物品类"""

    def __init__(self, item_id):
        if isinstance(item_id, Item):
            self.item_id = item_id.item_id
            self.data = item_id.data
            self.count = item_id.count
            self.slot = item_id.slot
        else:
            if item_id.startswith('minecraft:'):
                self.item_id = item_id
            else:
                self.item_id = f'minecraft:{item_id}'
            self.data = {}
            self.count = 1
            self.slot = 0

    # 基本属性

    def set_count(self, count: int):
        """设置堆叠在当前物品栏中的物品数量"""
        self.count = count
        return self

    def set_slot(self, slot: int):
        """设置物品槽位"""
        self.slot = slot
        return self

    def set_tag(self, *args: str):
        """设置物品标签"""
        self.data['Tags'] = [*args]
        return self

    # 通用标签/显示属性

    def set_damage(self, value: int):
        """设置物品的数据值(耐久)"""
        self.data['Damage'] = value
        return self

    def set_unbreakable(self, value: bool = True):
        """设置物品无法破坏"""
        self.data['Unbreakable'] = 1 if value else 0
        return self

    def set_can_destroy(self, *args):
        """
        设置物品可破坏列表
        :param args Item或str
        """
        self.data['CanDestroy'] = []
        for item in args:
            if isinstance(item, Item):
                self.data['CanDestroy'].append(item.item_id)
            elif isinstance(item, str):
                self.data['CanDestroy'].append(item)
        return self

    def set_custom_model_data(self, data: int):
        """设置用于物品模型的 overrides 属性中的物品标签 custom_model_data"""
        self.data['CustomModelData'] = data
        return self

    def set_color(self, red: int, green: int, blue: int):
        """
        设置皮革盔甲的颜色
        red/green/blue: 0-255
        """
        if 'display' not in self.data.keys():
            self.data['display'] = {}
        self.data['display']['color'] = (red * 65536) + (green * 256) + blue
        return self

    def set_name(self, name: str or RTextBase):
        """
        设置物品名称
        :param name: str或RTextBase
        """
        if 'display' not in self.data.keys():
            self.data['display'] = {}
        if isinstance(name, str):
            self.data['display']['Name'] = RText(name).to_json_str()
        elif isinstance(name, RTextBase):
            self.data['display']['Name'] = name.to_json_str()
        return self

    def set_lore(self, *args: str or RTextBase):
        """
        设置物品信息
        :param args: str或RTextBase
        """
        if 'display' not in self.data.keys():
            self.data['display'] = {}
        self.data['display']['Lore'] = []
        for i in args:
            if isinstance(i, str):
                self.data['display']['Lore'].append(RText(i).to_json_str())
            elif isinstance(i, RTextBase):
                self.data['display']['Lore'].append(i.to_json_str())
        return self

    def set_hide_flags(self, *args: int):
        """
        设置隐藏属性
        :param args: 属性的数值， 建议使用HideFlags的属性
        """
        flag = 0
        for i in args:
            flag += i
        self.data['HideFlags'] = flag
        return self

    # 方块标签

    def set_can_place_on(self, *args):
        """
        设置物品可放置列表
        :param args Item或str
        """
        self.data['CanPlaceOn'] = []
        for item in args:
            if isinstance(item, Item):
                self.data['CanPlaceOn'].append(item.item_id)
            elif isinstance(item, str):
                self.data['CanPlaceOn'].append(item)
        return self

    def set_block_entity_tag(self, data):
        """
        设置方块实体标签
        :param data: dict或BlockEntity
        """
        if isinstance(data, dict):
            self.data['BlockEntityTag'] = data
        elif isinstance(data, BlockEntity):
            self.data['BlockEntityTag'] = data.to_json_object()
        return self

    # 附魔

    def add_enchantment(self, enchantment, level: int = 1):
        """添加附魔属性"""
        if 'Enchantments' not in self.data.keys():
            self.data['Enchantments'] = []
        if isinstance(enchantment, Enchantments):
            self.data['Enchantments'].append(enchantment.data)
        elif isinstance(enchantment, str):
            self.data['Enchantments'].append(
                Enchantments(enchantment, level).data
            )
        return self

    def set_enchantments(self, *args):
        """设置附魔属性"""
        self.data['Enchantments'] = []
        for enchantment in args:
            if isinstance(enchantment, dict):
                self.data['Enchantments'].append(enchantment)
            elif isinstance(enchantment, Enchantments):
                self.data['Enchantments'].append(enchantment.data)
        return self

    def convert_stored_enchantments(self):
        """将附魔属性修改为存储的附魔属性"""
        self.data['StoredEnchantments'] = self.data['Enchantments']
        del self.data['Enchantments']
        return self

    def set_repair_cost(self, cost: int):
        """设置已修复次数"""
        self.data['RepairCost'] = cost
        return self

    # 属性修饰符 做不了

    def set_attribute_modifiers(self, data):
        pass

    # 药水效果

    def set_custom_potion_effect(self, *args):
        """
        设置所含的状态效果
        :param args: Status或效果id
        """
        self.data['CustomPotionEffects'] = []
        for i in args:
            self.data['CustomPotionEffects'].append(Status(i).data)
        return self

    def set_potion(self, potion: str):
        """设置默认药水效果的名称"""
        self.data['Potion'] = potion
        return self

    def set_custom_potion_color(self, red: int, green: int, blue: int):
        """
        物品使用该颜色
        范围效果云/箭/喷溅药水/滞留药水会使用该值作为其颗粒效果颜色
        red/green/blue: 0-255
        """
        self.data['CustomPotionColor'] = (red << 16) + (green << 8) + blue
        return self

    # 弩

    def set_charged_projectiles(self, *args):
        """
        设置弩装填的物品, 默认一个, 最多3个(多重射击附魔)
        :param args: dict或Item
        """
        self.data['ChargedProjectiles'] = []
        for i in args:
            if isinstance(i, dict):
                self.data['ChargedProjectiles'].append(i)
            elif isinstance(i, Item):
                self.data['ChargedProjectiles'].append(i.to_json_object())
        return self

    def set_charged(self, charged: bool = True):
        """设置弩的装填状态"""
        self.data['Charged'] = 1 if charged else 0
        return self

    # 书

    def set_generation(self, level: int):
        """
        设置成书的副本级别
        :param level:
        0表示原作; 1表示原作的副本; 2表示副本的副本; 3表示破烂不堪
        如果值大于1, 书就不可以被复制
        """
        self.data['generation'] = level
        return self

    def set_author(self, author: str):
        """设置成书的作者"""
        self.data['author'] = author
        return self

    def set_title(self, title: str):
        """设置成书的标题"""
        self.data['title'] = title
        return self

    def set_pages(self, *args: str or RTextBase):
        """设置书页"""
        self.data['pages'] = []
        for page in args:
            if self.item_id == 'minecraft:written_book':
                self.data['pages'].append(RTextList(page).to_json_str())
            elif self.item_id == 'minecraft:writable_book':
                self.data['pages'].append(RTextList(page).to_plain_text())
        return self

    # 玩家的头颅
    # 先不做

    # 烟花火箭
    # 做不了

    # 盔甲架/刷怪蛋/鱼桶

    def set_entity_tag(self, data: dict):
        """
        设置创建实体时应用于实体上的实体数据
        :param data: 实体共通标签
        """
        self.data['EntityTag'] = data
        return self

    def set_bucket_variant_tag(self, value: int):
        """设置桶中热带鱼的种类数据"""
        self.data['BucketVariantTag'] = value
        return self

    # 地图

    def set_map(self, value: int):
        """设置地图编号"""
        self.data['map'] = value
        return self

    # 迷之炖菜

    def add_effect(self, effect_id: int, duration: int):
        """添加迷之炖菜的状态效果"""
        if 'Effects' not in self.data.keys():
            self.data['Effects'] = []
        self.data['Effects'].append(
            {
                'EffectId': effect_id,
                'EffectDuration': duration
            }
        )
        return self

    # 调试棒

    def add_debug_property(self, block, state: str):
        """添加调试棒编辑的方块和其状态"""
        if 'DebugProperty' not in self.data.keys():
            self.data['DebugProperty'] = {}
        if isinstance(block, str):
            self.data['DebugProperty'][Item(block).item_id] = state
        elif isinstance(block, Item):
            self.data['DebugProperty'][block.item_id] = state
        return self

    # 指南针

    def set_lodestone_tracked(self, value: bool = True):
        """设置指南针是否绑定到一个磁石"""
        self.data['LodestoneTracked'] = 1 if value else 0
        return self

    def set_lodestone_dimension(self, dim: str):
        """设置磁石指针指向的坐标的所在维度"""
        self.data['LodestoneDimension'] = dim
        return self

    def set_lodestone_pos(self, x: int, y: int, z: int):
        """设置磁石指针指向的坐标"""
        self.data['LodestonePos'] = {
            'x': x,
            'y': y,
            'z': z
        }
        return self

    # 输出

    def to_nbt(self) -> dict:
        """获取nbt的dict"""
        return self.data

    def to_json_object(self) -> dict:
        """获取共通标签的dict象"""
        return {
            'Slot': self.slot,
            'id': self.item_id,
            'Count': self.count,
            'tag': self.data
        }

    def to_tags_common(self) -> str:
        """获取物品共通标签的str"""
        return json.dumps(
            {
                'Slot': self.slot,
                'id': self.item_id,
                'Count': self.count,
                'tag': self.data
            }
        )

    def to_give_command(self, player: str) -> str:
        """获取give指令的str"""
        return f'give {player} {self.item_id}{self.data} {self.count}'

    def to_setblock_command(self, x: int, y: int, z: int) -> str:
        """获取setblock指令的str"""
        if 'BlockEntityTag' in self.data.keys():
            return 'setblock {} {} {} {}{}'.format(
                x, y, z, self.item_id, self.data["BlockEntityTag"]
            ).replace("'", '"')
        else:
            return f'setblock {x} {y} {z} {self.item_id}'

    def give(self, server, player: str):
        """给予物品"""
        server.execute(self.to_give_command(player))

    def setblock(self, server, x: int, y: int, z: int):
        """放置方块"""
        server.execute(f'setblock {x} {y} {z} minecraft:air')
        server.execute(self.to_setblock_command(x, y, z))


class HideFlags:
    """存储隐藏属性的数值"""
    Enchantments = 1
    AttributeModifiers = 2
    Unbreakable = 4
    CanDestroy = 8
    CanPlaceOn = 16
    Other = 32


class Color:
    """存储颜色对应的数值"""
    white = 0
    orange = 1
    magenta = 2
    light_blue = 3
    yellow = 4
    lime = 5
    pink = 6
    gray = 7
    light_gray = 8
    cyan = 9
    purple = 10
    blue = 11
    brown = 12
    green = 13
    red = 14
    black = 15


class Pattern:
    """
    存储旗帜的图案类型
    https://minecraft-zh.gamepedia.com/旗帜#.E6.96.B9.E5.9D.97.E5.AE.9E.E4.BD.93
    """
    bottom_stripe = 'bs'
    top_stripe = 'ts'
    left_stripe = 'ls'
    right_stripe = 'rs'
    center_stripe = 'cs'
    middle_stripe = 'ms'
    down_right_stripe = 'drs'
    down_left_stripe = 'dls'
    small_stripes = 'ss'
    diagonal_cross = 'cr'
    square_cross = 'sc'
    left_of_diagonal = 'ld'
    right_of_upside_down_diagonal = 'rud'
    left_of_upside_down_diagonal = 'lud'
    right_of_diagonal = 'rd'
    vertical_half_left = 'vh'
    vertical_half_right = 'vhr'
    horizontal_half_top = 'hh'
    horizontal_half_bottom = 'hhb'
    bottom_left_corner = 'bl'
    bottom_right_corner = 'br'
    top_left_corner = 'tl'
    top_right_corner = 'tr'
    bottom_triangle = 'bt'
    top_triangle = 'tt'
    bottom_triangle_sawtooth = 'bts'
    top_triangle_sawtooth = 'tts'
    middle_circle = 'mc'
    middle_rhombus = 'mr'
    border = 'bo'
    curly_border = 'cbo'
    brick = 'bri'
    gradient = 'gra'
    gradient_upside_down = 'gru'
    creeper = 'cre'
    skull = 'sku'
    flower = 'flo'
    mojang = 'moj'
    globe = 'glb'
    piglin = 'pig'


class StructureBlockRotation:
    """存储结构方块的旋转角度"""
    none = 'NONE'
    clockwise_90 = 'CLOCKWISE_90'
    clockwise_180 = 'CLOCKWISE_180'
    clockwise_270 = 'COUNTERCLOCKWISE_90'


class StructureBlockMirror:
    """存储结构方块的镜像方法"""
    none = 'NONE'
    left_right = 'LEFT_RIGHT'
    front_back = 'FRONT_BACK'


class StructureBlockMode:
    """存储结构方块的模式"""
    save = 'SAVE'
    load = 'LOAD'
    corner = 'CORNER'
    data = 'DATA'


# ----------------------
# Block Entity 方块实体
# ----------------------


class BlockEntity:
    """
    方块实体的基类
    https://minecraft-zh.gamepedia.com/%E6%96%B9%E5%9D%97%E5%AE%9E%E4%BD%93
    #.E6.96.B9.E5.9D.97.E5.AE.9E.E4.BD.93.E5.88.97.E8.A1.A8
    """

    def __init__(self):
        self.data = {}

    def to_json_object(self):
        """获取数据的dict"""
        return self.data


class Beehive(BlockEntity):
    """蜂箱和蜂巢"""

    def set_flower_pos(self, x: int, y: int, z: int):
        """设置花的坐标"""
        self.data['FlowerPos'] = {
            'x': x,
            'y': y,
            'z': z
        }
        return self

    def set_bees(self, *args: dict):
        """设置巢内存在的实体"""
        self.data['Bees'] = [*args]
        return self


class Sign(BlockEntity):
    """告示牌"""

    def __init__(self):
        super().__init__()
        self.data = {
            'Text1': '{"text":""}',
            'Text2': '{"text":""}',
            'Text3': '{"text":""}',
            'Text4': '{"text":""}'
        }

    def set_text(self, line: int, text: str or RTextBase):
        """
        设置单行文本
        :param line: 行数 1-4
        :param text: 每行内容, 可以是str或RTextBase
        """
        if isinstance(text, str):
            self.data[f'Text{line}'] = text
        elif isinstance(text, RTextBase):
            self.data[f'Text{line}'] = text.to_json_str()
        return self

    def set_color(self, color: str):
        """设置告示牌颜色"""
        self.data['Color'] = color
        return self


class Banner(BlockEntity):
    """旗帜"""

    def __init__(self):
        super().__init__()
        self.data['Patterns'] = []

    def set_custom_name(self, name: str or RTextBase):
        """设置名称"""
        if isinstance(name, str):
            self.data['CustomName'] = RText(name).to_json_str()
        elif isinstance(name, RTextBase):
            self.data['CustomName'] = name.to_json_str()
        return self

    def add_pattern(self, color: int, pattern: str):
        """添加旗帜上的图案"""
        self.data['Patterns'].append({'Color': color, 'Pattern': pattern})
        return self


class Container(BlockEntity):
    """容器"""

    def set_custom_name(self, name: str or RTextBase):
        """设置名称"""
        if isinstance(name, str):
            self.data['CustomName'] = RText(name).to_json_str()
        elif isinstance(name, RTextBase):
            self.data['CustomName'] = name.to_json_str()
        return self

    def set_lock(self, lock: str):
        """设置容器锁"""
        self.data['Lock'] = lock
        return self

    def set_items(self, *args):
        """设置容器内物品列表"""
        self.data['Items'] = []
        for i in args:
            if isinstance(i, dict):
                self.data['Items'].append(i)
            elif isinstance(i, Item):
                self.data['Items'].append(i.to_json_object())
        return self

    def set_loot_table(self, table: str):
        """
        设置战利品表
        https://minecraft-zh.gamepedia.com/战利品表
        """
        self.data['LootTable'] = table
        return self

    def set_loot_table_seed(self, seed: int):
        """设置战利品表种子"""
        self.data['LootTableSeed'] = seed
        return self

    # 熔炉

    def set_burn_time(self, time: int):
        """设置距离燃料烧完的刻数"""
        self.data['BurnTime'] = time
        return self

    def set_cook_time(self, time: int):
        """设置物品已烧炼的刻数"""
        self.data['CookTime'] = time
        return self

    def set_cook_time_total(self, time: int):
        """设置烧炼物品的所需的总刻数"""
        self.data['CookTimeTotal'] = time
        return self

    def add_recipes(self, recipe: str or Item, time: int):
        """
        设置熔炉已烧制物品列表
        :param recipe: 配方名称
        :param time: 烧制次数
        """
        if 'RecipesUsed' not in self.data.keys():
            self.data['RecipesUsed'] = {}
        self.data['RecipesUsed'][Item(recipe).item_id] = time
        return self

    # 酿造台

    def set_crew_time(self, time: int):
        """设置酿造剩余时间"""
        self.data['BrewTime'] = time
        return self

    def set_fuel(self, fuel: int):
        """
        设置酿造台剩余能量
        :param fuel: 0-20
        """
        self.data['Fuel'] = fuel
        return self

    # 漏斗

    def set_transfer_cooldown(self, time: int):
        """设置漏斗距离下次运输的刻数"""
        self.data['TransferCooldown'] = time
        return self

    # 讲台

    def set_book(self, book: dict or Item):
        """设置讲台上放置的书"""
        if isinstance(book, dict):
            self.data['Book'] = book
        elif isinstance(book, Item):
            self.data['Book'] = book.to_json_object()
        return self

    def set_page(self, page: int):
        """设置当前书页"""
        self.data['Page'] = page
        return self


class Beacon(BlockEntity):
    """信标"""

    def set_level(self, level: int):
        """设置信标等级"""
        self.data['Levels'] = level
        return self

    def set_primary(self, status: int):
        """设置主效果"""
        self.data['Primary'] = status
        return self

    def set_secondary(self, status: int):
        """设置辅助效果"""
        self.data['Secondary'] = status
        return self


class Spawner(BlockEntity):
    """刷怪笼"""

    def __init__(self):
        super().__init__()
        self.data['SpawnPotentials'] = []

    def add_spawn_potentials(self, weight: int, entity: dict):
        """
        添加实体到可能生成实体的列表
        :param weight: 权重, 至少为1
        :param entity: 实体共通标签
        """
        self.data['SpawnPotentials'].append(
            {
                'Weight': weight,
                'Entity': entity
            }
        )
        return self

    def set_spawn_data(self, data: dict):
        """设置下一组即将生成的实体的标签"""
        self.data['SpawnData'] = data
        return self

    def set_spawn_count(self, count: int):
        """设置每次尝试生成生物的数量"""
        self.data['SpawnCount'] = count
        return self

    def set_spawn_range(self, value: int):
        """设置刷怪笼可以随机生成实体的范围"""
        self.data['SpawnRange'] = value
        return self

    def set_delay(self, delay: int):
        """设置距离下次生成的刻数"""
        self.data['Delay'] = delay
        return self

    def set_min_spawn_delay(self, delay: int):
        """设置生成延迟的随机范围的下限"""
        self.data['MinSpawnDelay'] = delay
        return self

    def set_max_spawn_delay(self, delay: int):
        """设置生成延迟的随机范围的上限"""
        self.data['MaxSpawnDelay'] = delay
        return self

    def set_max_nearby_entities(self, value: int):
        """设置刷怪笼周遭最大相同实体存在数量"""
        self.data['MaxNearbyEntities'] = value
        return self

    def set_required_player_range(self, value: int):
        """设置刷怪笼起效所需玩家与刷怪笼之间的最近距离"""
        self.data['RequiredPlayerRange'] = value
        return self


class Jukebox(BlockEntity):
    """唱片机"""

    def set_record_item(self, data: dict or Item):
        """设置唱片"""
        if isinstance(data, dict):
            self.data['RecordItem'] = data
        elif isinstance(data, Item):
            self.data['RecordItem'] = data.to_json_object()
        return self


class EnchantingTable(BlockEntity):
    """附魔台"""

    def set_custom_name(self, name: str or RTextBase):
        """设置名称"""
        if isinstance(name, str):
            self.data['CustomName'] = RText(name).to_json_str()
        elif isinstance(name, RTextBase):
            self.data['CustomName'] = name.to_json_str()
        return self


class Skull(BlockEntity):
    """生物头颅"""
    pass


class CommandBlock(BlockEntity):
    """命令方块"""

    def set_custom_name(self, name: str or RTextBase):
        """设置名称, 在执行某些命令时替代@"""
        if isinstance(name, str):
            self.data['CustomName'] = RText(name).to_json_str()
        elif isinstance(name, RTextBase):
            self.data['CustomName'] = name.to_json_str()
        return self

    def set_command(self, command: str):
        """设置命令方块中的命令"""
        self.data['Command'] = command
        return self

    def set_success_count(self, value: int):
        """设置红石比较器输出的模拟信号强度"""
        self.data['SuccessCount'] = value
        return self

    def set_last_output(self, message: str):
        """设置上一个输出"""
        self.data['LastOutput'] = message
        return self

    def set_track_output(self, value: bool):
        """设置LastOutput是否储存"""
        self.data['TrackOutput'] = 1 if value else 0
        return self

    def set_powered(self, value: bool):
        """设置是否被红石所激活"""
        self.data['powered'] = 1 if value else 0
        return self

    def set_auto(self, value: bool):
        """设置是否允许在没有红石信号的情况下激活命令(保持开启)"""
        self.data['auto'] = 1 if value else 0
        return self

    def set_condition_met(self, value: bool):
        """设置条件命令块在上次激活时是否满足其条件"""
        self.data['conditionMet'] = 1 if value else 0
        return self

    def set_update_last_execution(self, value: bool = False):
        """如果设为否, 创建循环后同一个命令方块可以在一刻内运行多次"""
        self.data['UpdateLastExecution'] = 1 if value else 0
        return self

    def set_last_execution(self, time: int):
        """设置连锁型命令方块最后被执行的游戏刻"""
        self.data['LastExecution'] = time
        return self


class EndGateway(BlockEntity):
    """末地折跃门"""

    def set_age(self, age: int):
        """设置末地折跃门方块的年龄"""
        self.data['Age'] = age
        return self

    def set_exact_teleport(self, value: bool = True):
        """设置是否把实体准确传送到指定的坐标"""
        self.data['ExactTeleport'] = 1 if value else 0
        return self

    def set_exit_portal(self, x: int, y: int, z: int):
        """设置要传送到的位置"""
        self.data['ExitPortal'] = {'X': x, 'Y': y, 'Z': z}
        return self


class StructureBlock(BlockEntity):
    """结构方块"""

    def set_name(self, name: str):
        """设置结构名称"""
        self.data['name'] = name
        return self

    def set_author(self, author: str):
        """设置结构作者"""
        self.data['author'] = author
        return self

    def set_metadata(self, value: str):
        """似乎没用"""
        self.data['metadata'] = value
        return self

    def set_pos(self, x: int, y: int, z: int):
        """设置结构起始坐标"""
        self.data['posX'] = x
        self.data['posY'] = y
        self.data['posZ'] = z
        return self

    def set_size(self, x: int, y: int, z: int):
        """设置结构大小"""
        self.data['sizeX'] = x
        self.data['sizeY'] = y
        self.data['sizeZ'] = z
        return self

    def set_rotation(self, value: str):
        """设置旋转角度"""
        self.data['rotation'] = value
        return self

    def set_mirror(self, value: str):
        """设置镜像方法"""
        self.data['mirror'] = value
        return self

    def set_mode(self, value: str):
        """设置模式"""
        self.data['mode'] = value
        return self

    def set_ignore_entities(self, value: bool = True):
        """设置是否忽略实体"""
        self.data['ignoreEntities'] = 1 if value else 0
        return self

    def set_showboundingbox(self, value: bool = True):
        """设置是否显示结构边框"""
        self.data['showboundingbox'] = 1 if value else 0
        return self

    def set_powered(self, value: bool = True):
        """设置是否被红石激活"""
        self.data['powered'] = 1 if value else 0
        return self


class RedstoneComparator(BlockEntity):
    """比较器"""

    def set_output_signal(self, strength: int):
        """设置信号输出强度"""
        self.data['OutputSignal'] = strength
        return self


class Conduit(BlockEntity):
    """潮涌核心"""

    def set_target(self, uuid: list):
        """设置正在攻击的生物UUID(奇怪的格式用不了)"""
        self.data['Target'] = uuid
        return self


class Bell(BlockEntity):
    """钟"""
    pass


# ----------------------
# Enchantments附魔
# ----------------------


class Enchantments:
    """
    存储所有的附魔
    https://minecraft-zh.gamepedia.com/附魔
    """
    aqua_affinity = 'minecraft:aqua_affinity'
    bane_of_arthropods = 'minecraft:bane_of_arthropods'
    blast_protection = 'minecraft:blast_protection'
    channeling = 'minecraft:channeling'
    curse_of_binding = 'minecraft:curse_of_binding'
    curse_of_vanishing = 'minecraft:curse_of_vanishing'
    depth_strider = 'minecraft:depth_strider'
    efficiency = 'minecraft:efficiency'
    feather_falling = 'minecraft:feather_falling'
    fire_aspect = 'minecraft:fire_aspect'
    fire_protection = 'minecraft:fire_protection'
    flame = 'minecraft:flame'
    fortune = 'minecraft:fortune'
    frost_walker = 'minecraft:frost_walker'
    impaling = 'minecraft:impaling'
    infinity = 'minecraft:infinity'
    knockback = 'minecraft:knockback'
    looting = 'minecraft:looting'
    loyalty = 'minecraft:loyalty'
    luck_of_the_sea = 'minecraft:luck_of_the_sea'
    lure = 'minecraft:lure'
    mending = 'minecraft:mending'
    multishot = 'minecraft:multishot'
    piercing = 'minecraft:piercing'
    power = 'minecraft:power'
    projectile_protection = 'minecraft:projectile_protection'
    protection = 'minecraft:protection'
    punch = 'minecraft:punch'
    quick_charge = 'minecraft:quick_charge'
    respiration = 'minecraft:respiration'
    riptide = 'minecraft:riptide'
    sharpness = 'minecraft:sharpness'
    silk_touch = 'minecraft:silk_touch'
    smite = 'minecraft:smite'
    soul_speed = 'minecraft:soul_speed'
    sweeping_edge = 'minecraft:sweeping_edge'
    thorns = 'minecraft:thorns'
    unbreaking = 'minecraft:unbreaking'

    def __init__(self, enchantment: str, level: int):
        self.data = {'id': f'{enchantment}', 'lvl': level}


# ----------------------
# Attributes属性
# 由于麻将奇怪的UUID后面没有L不能用也做不了
# ----------------------

class AttributesSlots:
    """存储槽位名称"""
    mainhand = 'mainhand'
    offhand = 'offhand'
    feet = 'feet'
    legs = 'legs'
    chest = 'chest'
    head = 'head'


class Attributes:
    pass


# ----------------------
# Effect 状态效果和药水名称
# ----------------------


class Status:
    """
    存储状态效果
    https://minecraft-zh.gamepedia.com/状态效果
    """
    speed = 1
    slowness = 2
    haste = 3
    mining_fatigue = 4
    strength = 5
    instant_health = 6
    instant_damage = 7
    jump_boost = 8
    nausea = 9
    regeneration = 10
    resistance = 11
    fire_resistance = 12
    water_breathing = 13
    invisibility = 14
    blindness = 15
    night_vision = 16
    hunger = 17
    weakness = 18
    poison = 19
    wither = 20
    health_boost = 21
    absorption = 22
    saturation = 23
    glowing = 24
    levitation = 25
    luck = 26
    unluck = 27
    slow_falling = 28
    conduit_power = 29
    dolphins_grace = 30
    bad_omen = 31
    hero_of_the_village = 32

    def __init__(self, status_id, amplifier: int = 0, duration: int = 200,
                 ambient: bool = False, show_particles: bool = True,
                 show_icon: bool = True):
        """
        一个状态效果
        :param status_id: 效果的数字ID, 可使用本类的属性或int或Status对象
        :param amplifier: 效果的倍率, 等级13的值为0
        :param duration: 效果的持续时长刻数
        :param ambient: 如果效果由信标施加, 那么为true
        :param show_particles: 如果显示颗粒效果, 那么为true
        :param show_icon: 如果效果图标显示, 那么为true
        show_particles 和 show_icon 由于去掉b后缀就不能用所以无效
        """
        if isinstance(status_id, Status):
            self.data = status_id.data
        else:
            self.data = {
                'Id': status_id,
                'Amplifier': amplifier,
                'Duration': duration,
                'Ambient': 1 if ambient else 0,
                'ShowParticles': 1 if show_particles else 0,
                'ShowIcon': 1 if show_icon else 0
            }


class Potion:
    """
    存储默认药水效果的名称
    https://minecraft-zh.gamepedia.com/药水#.E7.89.A9.E5.93.81.E6.95.B0.E6.8D.AE
    """
    water = 'water'
    mundane = 'mundane'
    thick = 'thick'
    awkward = 'awkward'
    night_vision = 'night_vision'
    long_night_vision = 'long_night_vision'
    invisibility = 'invisibility'
    long_invisibility = 'long_invisibility'
    leaping = 'leaping'
    strong_leaping = 'strong_leaping'
    long_leaping = 'long_leaping'
    fire_resistance = 'fire_resistance'
    long_fire_resistance = 'long_fire_resistance'
    swiftness = 'swiftness'
    strong_swiftness = 'strong_swiftness'
    long_swiftness = 'long_swiftness'
    slowness = 'slowness'
    long_slowness = 'long_slowness'
    water_breathing = 'water_breathing'
    long_water_breathing = 'long_water_breathing'
    healing = 'healing'
    strong_healing = 'strong_healing'
    harming = 'harming'
    strong_harming = 'strong_harming'
    poison = 'poison'
    strong_poison = 'strong_poison'
    long_poison = 'long_poison'
    regeneration = 'regeneration'
    strong_regeneration = 'strong_regeneration'
    long_regeneration = 'long_regeneration'
    strength = 'strength'
    strong_strength = 'strong_strength'
    long_strength = 'long_strength'
    weakness = 'weakness'
    long_weakness = 'long_weakness'
    luck = 'luck'
    slow_falling = 'slow_falling'
    strong_slow_falling = 'strong_slow_falling'
    long_slow_falling = 'long_slow_falling'
    turtle_master = 'turtle_master'
    strong_turtle_master = 'strong_turtle_master'
    long_turtle_master = 'long_turtle_master'


# ----------------------
# Explosion 烟火之星和烟花火箭
# 由于颜色必须要是个[I:int]的array所有做不了
# ----------------------


class Explosion:
    pass
