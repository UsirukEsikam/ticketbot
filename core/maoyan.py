import time
from core.ticketbot import TicketBot
from logger.logger import logger

class MaoyanBot(TicketBot):
    """
    猫眼Bot
    看起来用text都能定位，进付款界面后可以一直点击提交订单来刷票，暂时删掉刷票流程吧

    """

    def __init__(self, app="maoyan", serial=None) -> None:
        super().__init__(app, serial)

    def alert_check(self, hint=[], timeout=10):
        """检测弹窗，默认timeout=10s"""
        now_time = time.time
        start_time = now_time()
        while True:
            for word in hint:
                if self.sel_by_text(word).exists:
                    return word
            if now_time() - start_time >= timeout:
                logger.info("弹窗检测超时")
                return None

    def order_workflow(self):
        """
        下单流程的函数
        主要功能：点击确定→下单→alter check（需再循环一次return False，下单完成、出错etc return True）

        """
        # 点击确定
        self.sel_by_text("确认").click()
        while True:
            # 等待页面载入
            self.sel_by_text("应付").wait(10)
            # 点击提交
            self.sel_by_text("立即支付").click()
            # 记得回来改
            hint = self.alert_check(["库存不足"], 10)
            if hint == "库存不足":
                logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                self.screenshot()
                self.sel_by_text("立即支付").click()
                self.sel_by_text(hint).wait_gone(3)
                continue
            else:
                logger.info("未知情况（可能抢到了，可能出错了），请查看截图")
                self.screenshot()
                return True

    def maoyan_presale(self):
        """
        猫眼预售流程
        1、预先选好场次、票档、观演人
        2、进入预售页面
        3、运行脚本
        
        """
        logger.info("进入猫眼预售流程...")
        # 定时运行
        if self.time_trigger(self.config.scheduler.trigger):
            # 点击购票（会有好几种情况，用坐标点）
            self.dev.click(612, 1960)
            while True:
                # 开始下单
                if self.order_workflow():
                    return

    def maoyan_add_buyer(self):
        """添加用户函数，需要从'我的'页面开始"""
        self.dev.swipe_ext("up", scale=0.9)
        # 点击观影人信息
        self.sel_by_text("观演人信息").click()
        for name, id in self.config.buyer.info.items():
            self.sel_by_resid("com.sankuai.movie:id/dmh").wait(10)
            time.sleep(2)
            logger.info("开始添加观演人，姓名：{0}，身份证：{1}".format(name, id))
            # 点击添加
            self.sel_by_text("添加").click()
            # 输入姓名
            input = self.dev(textContains="演出").child(index=0, className="android.view.View").child(index=1, className="android.widget.EditText")
            input.click()
            input.send_keys(name)
            self.dev.press("back")
            # 输入身份证
            input = self.dev(textContains="演出").child(index=2, className="android.view.View").child(index=1, className="android.widget.EditText")
            input.click()
            input.send_keys(id)
            self.dev.press("back")
            # 点击确定
            self.sel_by_text("确定").click()