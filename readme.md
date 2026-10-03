# iris pipeline v1
空調設備管理デバイス
各空調機（エアコン）の温度を計測し、空調設備の電力効率向上を目的として、必要に応じてミストを噴射し、銅管温度を低下させるデバイスです。
温度センサから取得した測定値をもとに電磁弁を自動制御し、設定された温度条件に応じてミストの噴射・停止を行います。

※温度センサについて
各空調機に2台のセンサを使用する。
銅管と空気の吸気部分の2か所に配置して温度を測定する。
電磁弁の制御に使用する値はwebアプリ側で切り替えれるようにする。

# 配線
## 温度センサ(DS18B20)
GPIO04=sensor_A1,sensor_A2
GPIO05=sensor_B1,sensor_B2
GPIO06=sensor_C1,sensor_C2

GPIO12=sensor_D1,sensor_D2
GPIO13=sensor_E1,sensor_E2
GPIO16=sensor_F1,sensor_F2

GPIO17=sensor_G1,sensor_G2
GPIO18=sensor_H1,sensor_H2
GPIO19=sensor_I1,sensor_I2

GPIO20=sensor_J1,sensor_J2
GPIO21=sensor_K1,sensor_K2
GPIO26=sensor_L1,sensor_L2
## 電磁バルブ(12V)
リレーモジュールに接続(8つ)
## リレーモジュール(リレー*8)
GPIO07=relay_A
GPIO08=relay_B
GPIO09=relay_C
GPIO10=relay_D
GPIO11=relay_E
GPIO22=relay_F
GPIO23=relay_G
GPIO24=relay_H
## LED
GPIO25=DAEMON_LED
GPIO27=API_LED
GPIO14=NETWORK_LED
## SW
GPIO15=Reset_SW

# webアプリ
githubPagesをもちいて、ラズパイ側のッデータの受け取りや設定の書き換えなどを行う。APIを使用してユーザーが任意のタイミングでリクエストができるようにする。常時通信は行わない。

# コード
## main
tools,systemを使用して制御を行う。


## tools
・read_temp_sensor.py
read_temp_sensor(GPIO)->list(float)
任意のGPIOの温度センサーの値を取得可能できる数取得し返す。
・write_relay_module.py
write_relay_module(GPIO,bool)->bool()
リレーモジュールのGPIOのHIGH/LOWを切り替える
・write_temp_date.py
write_temp_date()->xlsx
指定の形式で温度データを渡すことでエクセルファイル追加保存する。また、エクセルファイルの新規作成などの関数もある。
・write_log.py
write_log()->txt
各、処理のログなどをすべて時間とともに保存する。
最大1000行までのログを記載し、超える場合は古い記録と入れ替える。

## api
未定

## system
・read_network.py
ネットワーク接続状態を確認する。
・read_api.py
外部アプリからの接続や編集を管理
・read_reset_switch.py
デーモンを終了し、システムを再起動
・read_system.py
OSの状態を管理

## config
・attach_pin.json
各GPIOのピン設定などを名前付けして定義づける。main.pyは起動時にこのファイルから読み込んだPINを使用して制御を行う。また、温度センサーの識別IDも記載。
・date_config.json
データの読み取り間隔などデータの記録に関する定義を保存するファイル。
・process_config.json
各電磁弁の開閉温度の設定、各空調機の制御で銅管温度と吸気温度のどちらを設定しているのかを保存しているファイル。
・config
　githubなどのアカウント関係に紐づく値を管理

# raspi
cd ~/iris_pipeline_v1/raspi
git pull
source .venv/bin/activate
pip install -r requirements.txt

## git
cd ~/iris_pipeline_v1
git add .
git commit -m "update raspi code"
git push