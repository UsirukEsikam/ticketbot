import os
from core.ticketbot import TicketBot
from core.livelab import LivelabBot
from core.damai import DaimaiBot
from core.maoyan import MaoyanBot
from logger.logger import logger

class Menu:
    def __init__(self, title, options):
        self.title = title
        self.options = options

    def display(self):
        while True:
            self.clear_screen()
            print(f"\n{self.title}")
            for i, option in enumerate(self.options, start=1):
                print(f"{i}. {option['description']}")
            print(f"{len(self.options) + 1}. Back")

            choice = input("Enter your choice: ")
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(self.options):
                    self.options[choice - 1]['function']()
                elif choice == len(self.options) + 1:
                    break
                else:
                    print("Invalid choice, please try again.")
            else:
                print("Invalid choice, please try again.")

    def clear_screen(self):
        if os.name == 'nt':  # for Windows
            os.system('cls')
        else:  # for Linux and macOS
            os.system('clear')

class CommandLineApp:
    def __init__(self):
        self.init_menu()

    def init_menu(self):
        self.option1_menu = Menu("纷玩岛", [
            {"description": "抢预售票", "function": self.livelab_presale},
            {"description": "刷回流票", "function": self.livelab_encore},
            {"description": "添加金主信息", "function": self.livelab_add_buyer}
        ])

        self.option2_menu = Menu("大麦", [
            {"description": "抢预售票", "function": self.damai_presale},
            {"description": "刷回流票", "function": self.damai_encore},
            {"description": "添加金主信息", "function": self.damai_add_buyer}
        ])

        self.option3_menu = Menu("猫眼", [
            {"description": "抢预售票", "function": self.maoyan_presale},
            {"description": "刷回流票", "function": self.maoyan_encore},
            {"description": "添加金主信息", "function": self.maoyan_add_buyer}
        ])

        self.main_menu = Menu("请选择相应的数字", [
            {"description": "纷玩岛", "function": self.option1_menu.display},
            {"description": "大麦", "function": self.option2_menu.display},
            {"description": "猫眼", "function": self.option3_menu.display}
        ])

    def damai_presale(self):
        bot_damai = DaimaiBot()
        bot_damai.damai_presale()

    def damai_encore(self):
        bot_damai = DaimaiBot()
        bot_damai.damai_encore()

    def damai_add_buyer(self):
        bot_damai = DaimaiBot()
        bot_damai.damai_add_buyer()

    def livelab_presale(self):
        bot_livelab = LivelabBot()
        bot_livelab.livelab_presale()

    def livelab_encore(self):
        bot_livelab = LivelabBot()
        bot_livelab.livelab_encore()

    def livelab_add_buyer(self):
        bot_livelab = LivelabBot()
        bot_livelab.livelab_add_buyer()

    def maoyan_presale(self):
        bot_maoyan = MaoyanBot()
        bot_maoyan.maoyan_presale()

    def maoyan_encore(self):
        bot_maoyan = MaoyanBot()
        bot_maoyan.maoyan_encore()

    def maoyan_add_buyer(self):
        bot_maoyan = MaoyanBot()
        bot_maoyan.maoyan_add_buyer()

    def run(self):
        print("脚本使用流程：")
        print("1、在config.yaml中配置好金主、票价、场次等信息")
        print("2、在APP添加观演人（可用脚本自动添加）")
        print("3、在APP预选场次、票档、观演人")
        print("4、进入预售页面，运行脚本预售流程")
        print("5、（可选）没抢到，则进入APP选票界面，运行回流票流程")
        input("Press Enter to continue...")
        try:
            self.main_menu.display()
        except Exception as e:
            logger.exception(e)

if __name__ == "__main__":
    app = CommandLineApp()
    app.run()