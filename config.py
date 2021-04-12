# -*- coding: utf-8 -*-
import json
import os

STAGE_LIST = ['A', 'B', 'C', 'a', 'b', 'c']


class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf8') as config_file:
                    self.config = json.load(config_file)
                    self.api_url = self.config.get("yobot_url")
                    self.stageA = self.config.get("stageA")
                    self.stageB = self.config.get("stageB")
                    self.stageC = self.config.get("stageC")
            else:
                self.config = {}
        except:
            self.config = {}

    def _save_config(self, data):
        with open(self.config_path, 'w', encoding='utf8') as config_file:
            json.dump(data, config_file, ensure_ascii=False, indent=4)

    def set_coefficient(self, stage: str, coefficient_list: list):
        """
        设置不同周目的权重
        :param stage:阶段（A，B，C面）
        :param coefficient_list:权重列表，元素为浮点型
        :return:
        """
        if stage not in STAGE_LIST:
            raise ValueError('stage参数无效')
        if (not coefficient_list) or (not isinstance(coefficient_list, list)):
            raise ValueError('coefficient_list无效')

        # 重载配置
        self._load_config()
        data = self.config
        key = "stage{}".format(stage.upper())
        data.update({key: coefficient_list})

        # 写入配置
        self._save_config(data)

    def get_coefficient(self, stage: str):
        """

        :param stage: 阶段（A，B，C面）
        :return: 权重列表
        """
        if stage not in STAGE_LIST:
            raise ValueError('stage参数无效')
        self._load_config()

        return getattr(self, "stage{}".format(stage.upper()))

    def set_yobot_url(self, url: str):
        """
        设置api地址
        :param url: yobot的API地址
        :return:
        """
        if not url:
            raise ValueError("无效的地址")
        self._load_config()
        data = self.config
        data.update(yobot_url=url)

    def get_yobot_url(self):
        self._load_config()
        return self.api_url
