import time
import uiautomator2 as u2
from itertools import cycle
from datetime import datetime
from config import global_config
from logger import logger

class TicketBot(object):
    """
    抢票脚本

    """

    def __init__(self, serial) -> None:
        self.user_info = None
        self.buyer_info = None
        self.target_price = None
        self.coop_price = None
        self.ticket_date = None
        self.buy_time = None
        self.dev = u2.connect(serial)
        self._read_config()

    def _read_config(self):
        logger.info("=== 读取配置文件 ===")
        # 读取脚本用户信息
        user_name = global_config.get("config", "user_name")
        user_mobile = global_config.get("config", "user_mobile")
        self.user_info = dict(zip([user_name], [user_mobile]))
        logger.info("脚本用户信息：{0}".format(self.user_info))
        # 读取金主信息
        buyer_name = global_config.get("config", "buyer_name")
        buyer_id = global_config.get("config", "buyer_id")
        buyer_mobile = global_config.get("config", "buyer_mobile")
        self.buyer_info = dict(zip(buyer_name.split(" "),zip(buyer_id.split(" "), buyer_mobile.split(" "))))
        logger.info("金主信息：{0}".format(self.buyer_info))
        # 读取票价
        self.target_price = global_config.get('config','target_price')
        self.coop_price = global_config.get('config','coop_price')
        logger.info("目标票价：{0}".format(self.target_price))
        # 读取场次信息
        self.ticket_date = global_config.get('config','ticket_date')
        logger.info("场次：{}".format(self.ticket_date))
        # 读取预售时间信息
        self.buy_time = global_config.getRaw('config','buy_time')

    def click_by_text(self, text):
        """通过text字段点击（暂时没加类名，以后看情况）"""
        self.dev(descriptionContains=text).click()

    def text_exists(self, text):
        """判断text是否出现"""
        return self.dev(descriptionContains=text).exists

    def ticket_check(self, date, target_price, coop_price, break_word):
        """刷票程序（不断点击两个票价，出现break_word后break，返回True"""
        # 选择场次(格式：2024-07-18)
        self.click_by_text(date)
        # 上滑（为了把票价都显示出来）
        self.dev.swipe_ext("up", scale=0.9)
        # 循环池子
        pool = cycle([target_price, coop_price])
        # 开始while
        while True:
            # 拿数
            np = next(pool)
            # 点击对应的票价
            self.click_by_text(np)
            # 如果np == target_price，做判断是否出现break_word
            if np == target_price:
                if self.text_exists(break_word):
                    logger.info("刷出票价：{0}，进入下单流程".format(target_price))
                    return True

    def alert_check(self, hint=[], timeout=10):
        """检测弹窗函数，带timeout，单位s"""
        start_time = time.time()
        while True:
            for word in hint:
                if self.text_exists(word):
                    return word
            now_time = time.time()
            if now_time - start_time >= timeout:
                return None

    def timer(self, buy_time):
        """时间格式：'2018-09-28 22:45:50.000'"""
        now_time = datetime.now
        buy_time = datetime.strptime(buy_time, "%Y-%m-%d %H:%M:%S.%f")
        while True:
            if now_time() >= buy_time:
                logger.info("到达预定时间，开始抢票...")
                self.dev.screen_on()
                return True
            else:
                time.sleep(0.2)

    def livelab_presale(self):
        """
        纷玩岛预售流程
        1、先添加好持票人
        2、去预售页面，选好预售信息
        3、运行
        
        """
        if self.timer(self.buy_time):
            self.click_by_text("立即购买")
            while True:
                self.click_by_text("确认")
                self.click_by_text("提交订单")
                hint = self.alert_check(["重新选择"], 5)
                if hint == "重新选择":
                    logger.info("出现'{0}'弹窗，继续运行...")
                    continue
                elif self.text_exists("确认并支付"):
                    logger.info("出现支付窗口，脚本结束")
                    return
                else:
                    logger.info("未知情况，请去uiautodev截图调试")
                    return

    def livelab_encore(self):
        """
        纷玩岛回流票流程
        1、先添加好持票人
        2、进入选票（刷票）页面
        3、运行
        
        """
        ticket_num = len(self.buyer_info)
        # 凑出来总票价的显示，用来做+号和选人时候的判定
        total_price = "￥{0}.00".format(ticket_num * int(self.target_price))
        while True:
            if self.ticket_check(self.ticket_date, self.target_price, self.coop_price, "购买数量"):
                # 点加号
                while True:
                    time.sleep(0.1)
                    if not self.text_exists(total_price):
                        # 加号是NAF的，只能用坐标
                        logger.info("增加票数（点击+号）")
                        self.dev.click(992, 1892)
                    else:
                        break
                # 点确认
                self.click_by_text("确认")
                # 上划
                self.dev(descriptionContains="票品信息").wait(5)
                self.dev.swipe_ext("up", scale=0.9)
                # 选人
                while True:
                    # 逻辑：点选之后总票价会跟转变，所以：先点选一遍，判断下总票价对不对，对：说明选上了，不对说明反选空了再来一遍
                    # 潜在BUG：1、页面显示的是：名字最后的一个文字，要是俩名字最后一个字一样的话就得再想别的办法
                    # 潜在BUG：2、历史人员多的话记得删掉，免得触发BUG
                    for name in self.buyer_info.keys():
                        self.click_by_text(name[-1])
                    if self.text_exists(total_price):
                        break
                    else:
                        for name in self.buyer_info.keys():
                            self.click_by_text(name[-1])
                        break
                # 输入联系人
                self.dev(index=1, className="android.widget.EditText").click()
                self.dev(index=1, className="android.widget.EditText").send_keys("朱建飞")
                # 关掉输入法
                self.dev.press("back")
                # 提交订单
                self.click_by_text("提交订单")
                hint = self.alert_check(["重新选择"], 5)
                if hint == "重新选择":
                    logger.info("出现'{0}'弹窗，继续运行...")
                    continue
                elif self.text_exists("确认并支付"):
                    logger.info("出现支付窗口，脚本结束")
                    return
                else:
                    logger.info("未知情况，请去uiautodev截图调试")
                    return

    def livelab_add_buyer(self):
        """添加用户函数，需要从'我的'页面开始"""
        self.click_by_text("持票人")
        for name, info in self.buyer_info.items():
            logger.info("开始添加观演人，姓名：{0}，身份证：{1}".format(name, info[0]))
            self.click_by_text("新增持票人")
            # 输入姓名
            input = self.dev(index=1, className="android.view.View").child(index=2, className="android.view.View").child(className="android.widget.EditText")
            input.click()
            self.dev.press("back")
            input.send_keys(name)
            # 选择身份证类型
            self.dev(index=4, className="android.view.View").click()
            self.click_by_text("确认")
            # 输入身份证
            input = self.dev(index=1, className="android.view.View").child(index=6, className="android.view.View").child(className="android.widget.EditText")
            input.click()
            self.dev.press("back")
            input.send_keys(info[0])
            # 勾选协议
            self.dev(index=9, className="android.view.View").click()
            # 确定
            self.click_by_text("确定")
            time.sleep(1)

    def run(self):
        # 亮屏
        self.dev.screen_on()
        # self.livelab_presale()
        # self.livelab_encore()
        # self.livelab_add_buyer()

if __name__ == "__main__":
    bot = TicketBot("6fe00acd")
    bot.run()