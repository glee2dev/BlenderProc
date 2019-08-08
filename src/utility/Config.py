import json
import re
import os


class Config:

    def __init__(self, data):
        self.data = data

    def _get_value(self, name, block=None):
        if block is None:
            block = self.data

        if "/" in name:
            delimiter_pos = name.find("/")
            block_name = name[:delimiter_pos]
            if block_name in block and type(block[block_name]) is dict:
                return self._get_value_with_fallback(name[delimiter_pos + 1:], block[block_name])
            else:
                raise NotFoundError("No such configuration block '" + block_name + "'!")
        else:
            if name in block:
                return block[name]
            else:
                raise NotFoundError("No such configuration '" + name + "'!")
            
    def _get_value_with_fallback(self, name, fallback=None):
        try:
            return self._get_value(name)
        except NotFoundError:
            if fallback is not None:
                return fallback
            else:
                raise

    def get_raw_dict(self, name, fallback=None):
        return self._get_value_with_fallback(name, fallback)

    def get_int(self, name, fallback=None):
        value = self._get_value_with_fallback(name, fallback)
        try:
            return int(value)
        except ValueError:
            raise TypeError("Cannot convert '" + str(value) + "' to int!")

    def get_bool(self, name, fallback=None):
        value = self._get_value_with_fallback(name, fallback)
        try:
            return bool(value)
        except ValueError:
            raise TypeError("Cannot convert '" + str(value) + "' to bool!")

    def get_float(self, name, fallback=None):
        value = self._get_value_with_fallback(name, fallback)
        try:
            return float(value)
        except ValueError:
            raise TypeError("Cannot convert '" + str(value) + "' to float!")

    def get_string(self, name, fallback=None):
        value = self._get_value_with_fallback(name, fallback)
        try:
            return str(value)
        except ValueError:
            raise TypeError("Cannot convert '" + str(value) + "' to string!")

    def get_list(self, name, fallback=None):
        value = self._get_value_with_fallback(name, fallback)
        if not isinstance(value, list):
            raise TypeError("Cannot convert '" + str(value) + "' to list!")

        return value

    @staticmethod
    def read_config_dict(config_path, args):
        with open(config_path, "r") as f:
            json_text = f.read()

            # Remove comments
            json_text = re.sub(r'^//.*\n?', '', json_text, flags=re.MULTILINE)
            # Replace arguments
            for i, arg in enumerate(args):
                json_text = json_text.replace("<args:" + str(i) + ">", arg)
            # Replace env variables
            for key in os.environ.keys():
                json_text = json_text.replace("$" + key, os.environ[key])

            if "<args:" in json_text:
                raise Exception("Too less arguments given")

            config = json.loads(json_text)
        return config


class NotFoundError(Exception):
    pass