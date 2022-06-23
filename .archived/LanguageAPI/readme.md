# LanguageAPI

> 语言API

## 使用

```python
LANGUAGE = {
    'zh_cn': {
        'hello': '你好',
        'bye': '再见'
    },
    'en_us': {
        'hello': 'Hello',
        'bye': 'Bye'
    }
}


def on_load(server, old):
    from LanguageAPI import Language
    language = Language(**LANGUAGE)
```

## 方法

### set_language

```python
def set_language(self, language: str) -> None
```

设置当前语言

`language`: 语言

### get_msg_str

```python
def get_msg_str(self, msg_id: str, language: str = None) -> str:
```

获取一条信息的文本

`msg_id`: 信息id

`language`: 语言

### __getitem__

```python
def __getitem__(self, msg_id: str) -> str:
        return self.get_msg_str(msg_id)
```

支持使用 `language[msg_id]` 来获取一条消息文本
