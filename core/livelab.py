import time
from core.ticketbot import TicketBot
from logger.logger import logger

class LivelabBot(TicketBot):
    """
    纷玩岛Bot
    基本都依靠description字段来定位

    """

    def __init__(self, app="livelab", serial=None) -> None:
        super().__init__(app, serial)

    def alert_check(self, hint=[], timeout=10):
        """检测弹窗，默认timeout=10s"""
        now_time = time.time
        start_time = now_time()
        while True:
            for word in hint:
                if self.sel_by_desc(word).exists:
                    return word
            if now_time() - start_time >= timeout:
                logger.info("弹窗检测超时")
                return None

    def ticket_check(self, ticket_tier, target_tier, coop_tier, magic_word):
        """
        刷票程序V2
        V1：不断点击两个票价，出现break_word后break，返回True
        V2：逻辑同大麦，不断进出页面来刷票（V1需要两次点击才能刷一次，大概需要2-3s）

        """
        ticket_num = len(self.config.buyer.info)
        total_price = "￥{0}.".format(ticket_num * self.config.ticket.target_price)
        while True:
            # 等待页面加载、给150ms自动选择时间
            self.sel_by_desc("请选择票品").wait(3)
            time.sleep(0.15)
            # 判断magic word
            if self.sel_by_desc(magic_word).exists:
                if self.sel_by_desc(total_price).exists:
                    logger.info("刷出票价：{0}，尝试进入下单页面".format(target_tier))
                    return True
                else:
                    logger.info("余票不足{0}张，跳过".format(ticket_num))
            self.dev.press("back")
            self.sel_by_desc("立即购买").click()

    def order_workflow(self):
        """
        下单流程的函数
        主要功能：点击确定→下单→alter check，需再循环一次return False，下单完成（或未知情况）return True）

        """
        # 点击确认
        self.sel_by_desc("确认").click()
        # 点击提交订单
        self.sel_by_desc("提交订单").click()
        # 弹窗检测
        hint = self.alert_check(["请求人数多", "数量不足", "订单中包含已购买"], 10)
        if hint == "请求人数多":
            logger.info("出现'{0}'弹窗，继续运行...".format(hint))
            # self.sel_by_desc("重新选择").click()
            self.dev.click(534, 1538)
            return False
        elif hint == "数量不足":
            logger.info("出现'{0}'弹窗，继续运行...".format(hint))
            # self.sel_by_desc("重新选择").click()
            self.dev.click(534, 1538)
            return False
        elif hint == "订单中包含已购买":
            logger.info("出现'{0}'弹窗，脚本结束".format(hint))
            return True
        elif self.sel_by_desc("确认并支付").exists:
            logger.info("出现支付窗口，脚本结束")
            return True
        else:
            logger.info("未知情况，请查看截图")
            self.screenshot()
            return True

    def livelab_presale(self):
        """
        纷玩岛预售流程
        1、预先选好场次、票档、观演人（重要！）
        2、进入预售页面
        3、运行脚本

        """
        logger.info("进入纷玩岛预售流程...")
        # 定时启动
        if self.trigger(self.config.scheduler.trigger):
            logger.info("到达设定时间，开始抢票")
            # 点击立即购买
            self.sel_by_desc("立即购买").click()
            while True:
                # 运行下单流程
                if self.order_workflow():
                    return

    def livelab_encore(self):
        """
        纷玩岛回流票流程V2
        1、需在预售时选好了场次、票档、观演人（重要！）
        2、进入选票（刷票）页面
        3、运行脚本

        """
        logger.info("进入纷玩岛回流票流程...")
        while True:
            # 查余票
            if self.ticket_check(self.config.ticket.ticket_tier, self.config.ticket.target_tier, self.config.ticket.coop_tier, "购买数量"):
                # 开始下单流程
                if self.order_workflow():
                    return

    def livelab_add_buyer(self):
        """添加用户函数，需要从'我的'页面开始"""
        self.sel_by_desc("持票人").click()
        for name, info in self.config.buyer.info.items():
            logger.info("开始添加观演人，姓名：{0}，身份证：{1}".format(name, info[0]))
            self.sel_by_desc("新增持票人").click()
            # 输入姓名
            input = self.dev(index=1, className="android.view.View").child(index=2, className="android.view.View").child(className="android.widget.EditText")
            input.click()
            input.send_keys(name)
            self.dev.press("back")
            # 选择身份证类型
            self.dev(index=4, className="android.view.View").click()
            self.sel_by_desc("确认").click()
            # 输入身份证
            input = self.dev(index=1, className="android.view.View").child(index=6, className="android.view.View").child(className="android.widget.EditText")
            input.click()
            input.send_keys(info[0])
            self.dev.press("back")
            # 勾选协议
            self.dev(index=9, className="android.view.View").click()
            # 确定
            self.sel_by_desc("确定").click()
            time.sleep(1)