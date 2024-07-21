import os
from core.damai import DaimaiBot
from core.livelab import LivelabBot

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
        self.option1_menu = Menu("大麦网", [
            {"description": "抢预售票", "function": self.damai_presale},
            {"description": "刷回流票", "function": self.damai_encore},
            {"description": "添加金主信息", "function": self.damai_add_buyer}
        ])
        
        self.option2_menu = Menu("纷玩岛", [
            {"description": "抢预售票", "function": self.livelab_presale},
            {"description": "刷回流票", "function": self.livelab_encore},
            {"description": "添加金主信息", "function": self.livelab_add_buyer}
        ])

        self.main_menu = Menu("请选择相应的数字", [
            {"description": "大麦网", "function": self.option1_menu.display},
            {"description": "纷玩岛", "function": self.option2_menu.display}
        ])

    def damai_presale(self):
        print("")
        print("=== 大麦预售流程 ===")
        print("0、请在config.yaml中配置好相关信息")
        print("1、请预选好场次、票档、观演人")
        print("2、进入APP预售页面")
        input("Press Enter to continue...")
        bot_damai = DaimaiBot("6fe00acd", "damai")
        bot_damai.damai_presale()

    def damai_encore(self):
        print("")
        print("=== 大麦预售流程 ===")
        print("0、请在config.yaml中配置好相关信息")
        print("1、请预选好场次、票档、观演人")
        print("2、进入APP选票页面")
        input("Press Enter to continue...")
        bot_damai = DaimaiBot("6fe00acd", "damai")
        bot_damai.damai_encore()

    def damai_add_buyer(self):
        bot_damai = DaimaiBot("6fe00acd", "damai")
        bot_damai.damai_add_buyer()

    def livelab_presale(self):
        print("")
        print("=== 纷玩岛预售流程 ===")
        print("0、请在config.yaml中配置好相关信息")
        print("1、请预选好场次、票档、观演人")
        print("2、进入APP预售页面")
        input("Press Enter to continue...")
        bot_livelab = LivelabBot("6fe00acd", "livelab")
        bot_livelab.livelab_presale()

    def livelab_encore(self):
        print("")
        print("=== 纷玩岛预售流程 ===")
        print("0、请在config.yaml中配置好相关信息")
        print("1、请预选好场次、票档、观演人")
        print("2、进入APP选票页面")
        input("Press Enter to continue...")
        bot_livelab = LivelabBot("6fe00acd", "livelab")
        bot_livelab.livelab_encore()

    def livelab_add_buyer(self):
        bot_livelab = LivelabBot("6fe00acd", "livelab")
        bot_livelab.livelab_add_buyer()

    def run(self):
        self.main_menu.display()

if __name__ == "__main__":
    app = CommandLineApp()
    app.run()