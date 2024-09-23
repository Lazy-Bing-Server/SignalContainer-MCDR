from mcdreforged.api.all import *
from typing import Dict, Any
from threading import RLock

from signal_container.container import Container


psi = ServerInterface.psi()


class Config(Serializable):
    __FILE_NAME = 'config.json'

    class PermissionRequirements(Serializable):
        get: int = 1
        set: int = 1
        give: int = 1
        set_global: int = 2

    prefix: str = "!!sig"
    permission: PermissionRequirements = PermissionRequirements.get_default()

    class __BaseConfig(Serializable):
        # Do not add generic here or TypeError(xD)
        container_item: str
        max_slots: int
        allow_overstack_under_15: bool
        unstackable_fillings: str
        stackable_fillings: str

        __default = {
            "container_item": "minecraft:barrel",
            "max_slots": 27,
            "allow_overstack_under_15": False,
            "unstackable_fillings": "minecraft:shears",
            "stackable_fillings": "minecraft:iron_nugget"
        }

        @classmethod
        def get_default(cls):
            return cls.deserialize(cls.__default)

    global_config: __BaseConfig = __BaseConfig.get_default()
    preferences: Dict[str, __BaseConfig] = {}

    def __init__(self, **kwargs):
        self.__lock = RLock()
        super(Config, self).__init__(**kwargs)

    @classmethod
    def load(cls) -> "Config":
        return psi.load_config_simple(file_name=cls.__FILE_NAME, target_class=cls)

    def save(self):
        with self.__lock:
            psi.save_config_simple(self, file_name=self.__FILE_NAME)

    def get_key_lists(self):
        return list(self.get_base_config_annotations().keys())

    def get_base_config_annotations(self):
        return self.__BaseConfig.get_field_annotations()

    def __set(self, target: "__BaseConfig", key: str, value: Any):
        with self.__lock:
            if key not in self.get_key_lists():
                return False
            try:
                setattr(target, key, self.get_base_config_annotations().get(key, str)(value))
                self.__BaseConfig.deserialize(target.serialize())
            except (ValueError, TypeError):
                psi.logger.exception("Error occurred in config set")
                return False
            return True

    def set_global(self, src: "CommandSource", key: str, value: Any):
        with self.__lock:
            if src.get_permission_level() < self.permission.set_global:
                return False
            if not self.__set(self.global_config, key, value):
                return False
            self.save()
            return True

    def set_personal_preference(self, src: "PlayerCommandSource", key: "str", value: Any):
        with self.__lock:
            if src.get_permission_level() < self.permission.set:
                return False
            target = self.preferences.get(src.player, self.__BaseConfig())
            if not self.__set(target, key, value):
                return False
            self.preferences[src.player] = target
            self.save()
            return True

    def get_target_container(self, player: str):
        with self.__lock:
            pref = self.preferences.get(player, self.global_config)
            full_pref = self.global_config.serialize()
            full_pref.update(pref.serialize())
            return Container(**full_pref)
