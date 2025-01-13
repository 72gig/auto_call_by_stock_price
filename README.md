# 股票自動通知

這是通過富果API取得資料，如果符合條件就會在終端出現通知的程式

下方說明各檔案的功能

## app.py

這是主程式，需要 python 3.9.7 以上的版本執行

在使用以前，請確保已安裝 requirements.txt 的必要的模組

並在 focus.json 跟 sleep.json 設定必要的資料

最後，請手動建立 code.txt，並將 API Key 的數值保存在裡面

## focus.json

在這裡設定需要檢查的股票

以 json 格式保存，需要用到以下參數:

### stock

要檢查的股票名稱

### use_date

設定檢查日期

### mothod

設定檢查多空

### reload

設定價格是否接觸到 up_line 跟 down_line 以後符合條件還要通知

### up_line

設定價格區間的上緣

### down_lien

設定價格區間的下緣

## sleep.json

在這裡設定不需要檢查股票的日子

如果有自行確設休市時間，可以忽略設定

以 json 的格式儲存，需要以下格式:

### date

設定不需要檢查的日子

### why

設定原因的說明

## requirements.txt

這裡是需要的模組記錄，請確保在執行前有安裝