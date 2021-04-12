# -*- coding: utf-8 -*-
import json

import requests
from decimal import Decimal
from hoshino import Service, priv
from hoshino.modules.pcr_maofen.config import Config

_help = '''
[maofen,/maofen或者毛分]查询毛分'''.strip()
sv = Service('毛分', help_=_help, bundle='公会战')

CONFIG_PATH = './hoshino/modules/pcr_maofen/config.json'
STAGE_LIST = ['A', 'B', 'C', 'a', 'b', 'c']
# boss_violent_coefficient_a = 1.0  # A面狂暴额外系数(历史产物不要了)
# boss_violent_coefficient_b = 1.0  # B面狂暴额外系数(同上)

config = Config(CONFIG_PATH)


def caculate_maofen():
    r = requests.get(config.get_yobot_url())

    # 获取权重数据
    coefficient_list = [
        config.stageA, config.stageB, config.stageC
    ]
    damage_data = json.loads(r.text, encoding="utf-8")

    # yobot数据处理
    temp_dict = {}
    members = {x.get("qqid"): x.get("nickname") for x in damage_data.get("members")}
    challenges = damage_data.get("challenges")

    for challenge in challenges:
        cycle = challenge.get("cycle")
        if (cycle >= 1) and (cycle < 4):
            point = Decimal(challenge.get("damage")) * Decimal(coefficient_list[0][challenge.get("boss_num") - 1])
        elif (cycle >= 4) and (cycle < 11):
            point = Decimal(challenge.get("damage")) * Decimal(coefficient_list[1][challenge.get("boss_num") - 1])
            # 判断是否狂暴
            # if challenge.get("boss_num") == 5 and challenge.get("health_ramain") < 10000000:
            #     point = Decimal(point) * Decimal(boss_violent_coefficient_a)
        else:
            point = Decimal(challenge.get("damage")) * Decimal(coefficient_list[2][challenge.get("boss_num") - 1])
            # 判断是否狂暴
            # if challenge.get("boss_num") == 5 and challenge.get("health_ramain") < 10000000:
            #     point = Decimal(point) * Decimal(boss_violent_coefficient_b)

        qqid = challenge.get("qqid")
        if temp_dict.get(str(qqid)):
            temp_dict[str(qqid)] = float(
                Decimal(temp_dict[str(qqid)]) + point
            )
        else:
            temp_dict[str(qqid)] = float(point)

    result = sorted(temp_dict.items(), key=lambda d: d[1], reverse=True)
    msg = "结果：\n"
    for i, r in enumerate(result):

        # msg += str(i + 1) + "," + members.get(int(r[0]))

        msg += "排名第{}位 用户 {} 的毛分为 {} \n".format(
                str(i + 1), members.get(int(r[0])), round(r[1], 2)
            )

    return msg


@sv.on_fullmatch('毛分', 'maofen', '/maofen')
async def maofen(bot, ev):
    res = caculate_maofen()
    await bot.send(res)


@sv.on_prefix('调整权重')
async def set_coeffcient(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '您无权设置权重')
    msg = ev.message.extract_plain_text()
    coefficient = msg.strip().replace(' ', '').split(',')
    coefficient_list = []

    stage = coefficient[0]
    if stage not in STAGE_LIST:
        await bot.finish(ev, '阶段无效,仅能为A,B,C(不区分大小写)之一')

    coefficient.pop(0)

    try:
        coefficient_list = [float(value) for value in coefficient]
    except ValueError as e:
        await bot.finish(ev, '值仅能为整数或小数')

    try:
        config.set_coefficient(stage, coefficient_list)
        await bot.send(ev, '权重设置完成')
    except ValueError as e:
        await bot.finish(ev, '修改失败，联系管理员')


@sv.on_prefix('查看权重')
async def get_coeffcient(bot, ev):
    stage = ev.message.extract_plain_text()
    if stage not in STAGE_LIST:
        await bot.finish(ev, '阶段无效,仅能为A,B,C(不区分大小写)之一')
    data = config.get_coefficient(stage)
    msg = '{stage}面权重为\n'.format(stage=stage.upper())
    for i, value in enumerate(data):
        msg += '{number}王: {value}\n'.format(
            number=str(i + 1), value=str(value))
    await bot.send(ev, msg)