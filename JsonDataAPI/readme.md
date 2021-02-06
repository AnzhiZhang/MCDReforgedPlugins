# JsonDataAPI

> 提供插件使用Json进行数据存储并保存到文件的功能

## 文档

该API继承了dict类, 可以直接当做字典使用

### 初始化

```python
def __init__(self, plugin_name: str, file_name: str = None)
```

plugin_name: 该插件的所有数据文件将存储在 `config\plugin_name` 目录下

file_name: 该数据文件的名称, 无需包含扩展名

例:

```python
from JsonDataAPI import Json
data = Json(PLUGIN_METADATA['name'])
```

### 保存数据

```python
data.save()
```
