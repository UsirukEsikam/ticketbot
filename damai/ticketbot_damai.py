import time
import ntplib
import uiautomator2 as u2
from itertools import cycle
from datetime import datetime
from config import global_config
from logger import logger

class TicketBot(object):
    """
    抢票脚本
    大麦的问题：
    一些关键的元素（比如场次、票价、确定按钮etc）都没有text和desc属性（可能是图片），只能靠parent的resid+自己的index来定位

    """

    def __init__(self, serial) -> None:
        self.user_info = None
        self.buyer_info = None
        self.target_price = None
        self.target_class = None
        self.coop_price = None
        self.coop_class = None
        self.ticket_class = None
        self.buy_time = None
        self.dev = u2.connect(serial)
        # 场次的layout
        self.perform_flow = self.select_by_resid("cn.damai:id/project_detail_perform_flowlayout")
        # 价格的layout
        self.price_flow = self.select_by_resid("cn.damai:id/project_detail_perform_price_flowlayout")
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
        self.target_class = global_config.get('config','target_class')
        self.coop_price = global_config.get('config','coop_price')
        self.coop_class = global_config.get('config','coop_class')
        logger.info("目标票价：{0}-{1}档".format(self.target_price, self.target_class))
        # 读取场次信息
        self.ticket_class = global_config.get('config','ticket_class')
        logger.info("场次：{}档".format(self.ticket_class))
        # 读取预售时间信息
        self.buy_time = global_config.getRaw('config','buy_time')
        logger.info("开枪时间：{0}".format(self.buy_time))

    def click_by_text(self, text):
        """通过text字段点击（暂时没加类名，以后看情况）"""
        self.dev(textContains=text).click()

    def text_exists(self, text):
        """判断text是否出现"""
        return self.dev(textContains=text).exists

    def select_by_text(self, text):
        return self.dev(textContains=text)

    def select_by_resid(self, resource_id):
        return self.dev(resourceId=resource_id)

    def select_child_by_index(self, parent, index, class_name):
        return parent.child(index=index, className=class_name)

    def ticket_check(self, ticket_class, target_class, coop_class, break_word):
        """刷票程序（不断点击两个票价，出现break_word后break，返回True"""
        # 选择场次（从0开始编号）
        self.select_child_by_index(self.perform_flow, ticket_class, "android.view.ViewGroup").click()
        # 上滑（为了把票价都显示出来）
        self.dev.swipe_ext("up", scale=0.9)
        # 循环池子
        pool = cycle([target_class, coop_class])
        # 开始while
        while True:
            # 拿数
            nc = next(pool)
            # 点击对应的票价
            self.select_child_by_index(self.price_flow, nc, "android.widget.FrameLayout").click()
            # 如果np == target_price，做判断是否出现break_word
            if nc == target_class:
                if self.text_exists(break_word):
                    logger.info("刷出票价：{0}档，进入下单流程".format(target_class))
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

    def get_network_time(self):
        """获取网络时间"""
        client = ntplib.NTPClient()
        response = client.request("ntp.aliyun.com")
        return datetime.fromtimestamp(response.tx_time)

    def damai_presale(self):
        """
        大麦预售流程
        1、预先选好场次、票档、观演人
        2、进入预售页面
        3、运行
        
        """
        if self.timer(self.buy_time):
            # 点击立即预定
            self.select_by_resid("cn.damai:id/trade_project_detail_purchase_status_bar_container_fl").click()
            while True:
                # 点击确定
                self.select_by_resid("cn.damai:id/btn_buy").click()
                while True:
                    self.click_by_text("提交订单")
                    hint = self.alert_check(["继续尝试", "我知道了"])
                    if hint == "继续尝试":
                        logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                        self.click_by_text(hint)
                        continue
                    elif hint == "我知道了":
                        logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                        self.click_by_text(hint)
                        self.dev.press("back")
                        break
                    # 还少支付界面的提示
                    else:
                        logger.info("未知情况（可能抢到了，可能出错了），请去uiautodev截图调试")
                        return

    def damai_encore(self):
        """
        大麦回流票流程
        1、先添加好持票人
        2、进入选票（刷票）页面
        3、运行
        
        """
        ticket_num = len(self.buyer_info)
        total_price = ticket_num * int(self.target_price)
        while True:
            if self.ticket_check(self.ticket_class, self.target_class, self.coop_class, "价格明细"):
                # 点加号
                while True:
                    time.sleep(0.1)
                    if not self.text_exists(total_price):
                    # if not self.dev(textContains=total_price, resourceId="cn.damai:id/tv_price").exists:
                        logger.info("增加票数（点击+号）")
                        self.select_by_resid("cn.damai:id/img_jia").click()
                    else:
                        break
                # 点确认
                self.select_by_resid("cn.damai:id/btn_buy").click()
                # 等待页面刷新，上划
                self.dev(textContains="实名观演人").wait(10)
                self.dev.swipe_ext("up", scale=0.9)
                # 选人
                for name in self.buyer_info.keys():
                    self.click_by_text(name)
                # 提交订单
                while True:
                    self.click_by_text("提交订单")
                    hint = self.alert_check(["继续尝试", "我知道了"])
                    if hint == "继续尝试":
                        logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                        self.click_by_text(hint)
                        continue
                    elif hint == "我知道了":
                        logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                        self.click_by_text(hint)
                        self.dev.press("back")
                        break
                    # 还少支付界面的提示
                    else:
                        logger.info("未知情况（可能抢到了，可能出错了），请去uiautodev截图调试")
                        return

    def damai_add_buyer(self):
        """添加观演人的函数，需从我的界面开始"""
        self.click_by_text("观演人")
        for name, info in self.buyer_info.items():
            logger.info("开始添加观演人，姓名：{0}，身份证：{1}".format(name, info[0]))
            self.click_by_text("添加新观演人")
            self.click_by_text("请填写观演人姓名")
            self.select_by_text("请填写观演人姓名").send_keys(name)
            self.click_by_text("请填写证件号码")
            self.select_by_text("请填写证件号码").send_keys(info[0])
            self.dev.press("back")
            self.dev(index=0, className="android.widget.CheckBox").click()
            self.click_by_text("确定")
            time.sleep(1)

    def run(self):
        # 亮屏
        self.dev.screen_on()
        # self.damai_presale()
        # self.damai_encore()
        # self.damai_add_buyer()

if __name__ == "__main__":
    bot = TicketBot("6fe00acd")
    bot.run()