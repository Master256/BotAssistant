from core.bot_core import BotCore
from core.gui import ChatGUI
from core.speech import SpeechManager

def main():
    bot = BotCore()
    
    speech = SpeechManager()
    
    gui = ChatGUI(bot, speech)
    
    gui.run()

if __name__ == "__main__":
    main()