# -*- coding: utf-8 -*-
import os
import json

PLUGIN_METADATA = {
    'id': 'json_data_api',
    'version': '0.0.1',
    'name': 'JsonDataAPI',
    'description': 'Json data API for plugin save data',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/JsonDataAPI'
}


class Json(dict):
    """
    A inheritance class of dict, use save() to save data into file.
    """
    def __init__(self, plugin_name: str, file_name: str = None):
        # Dir
        self.dir = os.path.join('config', plugin_name)
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)
        # Path
        file_name = plugin_name if file_name is None else file_name
        self.path = os.path.join(self.dir, f'{file_name}.json')
        # Data
        if os.path.isfile(self.path):
            with open(self.path, encoding='utf-8') as f:
                super().__init__(json.load(f))
        else:
            super().__init__()
            self.save()

    def save(self):
        """Save data"""
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.copy(), f, indent=4, ensure_ascii=False)
