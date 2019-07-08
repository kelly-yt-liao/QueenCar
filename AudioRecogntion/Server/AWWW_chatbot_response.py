#coding:utf-8
from chatbot import chatbot

def Chat_with_Bot(sentence_in, AkishinoProjectBot):
    # AkishinoProjectBot = chatbot.Chatbot()
    # AkishinoProjectBot.main(['--modelTag', 'taiwa20170709', '--test', 'daemon'])
    # --modelTag    taiwa20170709
    # --test        daemon
    answer = AkishinoProjectBot.daemonPredict(sentence=sentence_in)
#    AkishinoProjectBot.daemonClose()
    del AkishinoProjectBot

    return answer

"""
if __name__ == "__main__":
    print(Chat_with_Bot(" 負面 過得 不 太 好 "))
"""