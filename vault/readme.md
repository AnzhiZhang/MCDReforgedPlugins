# Vault

> 经济类插件前置
>
> 它为其他的需要基于经济系统的插件提供了所需的API

## 开发文档

所有的API都封装在 `Vault` 类中, Vault插件已经将 `Vault` 实例化并储存到全局变量 `vault` 变量中

### 初始化

在`on_load`中加入以下内容:

```python
global vault
vault = server.get_plugin_instance('vault').vault
```

### API列表

#### create_account

```python
def create_account(name: str) -> None
```

为 `name` 创建一个账号

#### is_account

```python
def is_account(self, name) -> bool
```

判断账号 `name` 是否存在

#### get_open_time

```python
def get_open_time(name: str) -> int
```

获取账号 `name` 的开户时间, 返回时间戳, 单位为秒

#### get_balance

```python
def get_balance(name: str) -> Decimal
```

获取账号 `name` 的余额, 返回Decimal

#### get_logs

```python
def get_logs() -> List[Tuple[str, int, str, str, float]]
```

获取所有转账日志, 玩家间转账的借贷方为玩家名, 直接调整的借方为 `Admin`

格式: `[(id, time, debit, credit, amount)]`

示例格式:

```python
[
    ('dda6b10c-db52-4508-81cb-7c3216eb350d', 1612271749, 'Admin', 'a', 1.20),
    ('4eb0b778-3394-41da-9e64-da6be5f4615c', 1612271749, 'Admin', 'a', -1.20),
    ('fc46544c-1a13-4dae-9dee-0d3c3938b48b', 1612271711, 'a', 'b', 1.00)
]
```

#### get_ranking

```python
def get_ranking() -> Dict[str, Decimal]
```

获取所有账号的余额从高到低排名

示例格式:

```python
{
    'a': Decimal('1.50'),
    'b': Decimal('1.40')
}
```

#### give

```python
def give(name: str, amount: Decimal, operator: str = 'Admin') -> None
```

将 `name` 的余额添加 `amount`

`operator`: 将会显示在日志的借方, 建议传递该参数为插件名或操作名

#### take

```python
def take(name: str, amount: Decimal, operator: str = 'Admin') -> None
```

将 `name` 的余额减少 `amount`

`operator`: 将会显示在日志的借方, 建议传递该参数为插件名或操作名

#### set

```python
def set(name: str, amount: Decimal, operator: str = 'Admin') -> None
```

将 `name` 的余额设为 `amount`

`operator`: 将会显示在日志的借方, 建议传递该参数为插件名或操作名

#### transfer

```python
def transfer(debit: str, credit: str, amount: Decimal) -> None
```

将 `debit` 的余额划 `amount` 到 `credit` 的账上

### 异常

在某些情况下, 会抛出一些异常, 下方列出所有的异常和抛出原因

使用API时应当自行处理这些异常, 所有异常已存储在 `Vault` 类的属性中

#### AccountNotExistsError

账号不存在时抛出该异常

#### AmountIllegalError

金额不合法时抛出该异常

#### InsufficientBalanceError

余额不足时抛出该异常
