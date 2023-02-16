HELP_TEXT = """嗨！我是LineGPT，很高興為您服務。以下是我的使用說明：
@LineGPT <指令>

* 顯示使用說明
@LineGPT help

* 開始對話階段
@LineGPT start

* 顯示過往對話紀錄
@LineGPT log

* 提問
@LineGPT ask <your question> 
Example:
@LineGPT ask 請告訴我怎麼變有錢人

* 關閉對話階段，過往紀錄將會被刪除
@LineGPT close

* 重啟對話階段
@LineGPT restart
"""

SELECT_COMMAND_ERROR = '錯誤: 未知的指令. 請重新輸入一次或輸入"@LineGPT help"以取得更多資訊。'

START_GREETING = "對話階段已開始，您可以開始問問題了。在每次的對話階段中，您最多可以詢問十個問題。"
START_FOUND_SESSION = "存在舊有的對話階段，您可以查看紀錄、繼續對話、或是重啟對話階段。"

ASK_NO_SESSION_WARNING = '警告： 尚未開啟對話階段，請先使用"@LineGPT start"開啟對話。'
ASK_EXPIRED_WARNING = '警告: 當前對話階段已過期。請先使用"@LineGPT restart"重新開啟對話階段。'
ASK_QUESTION_RUNTIME_ERROR = "錯誤: RuntimeError. 請稍後再試一次"

CLOSE_MESSAGE = "關閉對話階段。"

RESTART_MESSAGE = "重新啟動對話階段"

LOG_MESSAGE = "以下是對話紀錄："
