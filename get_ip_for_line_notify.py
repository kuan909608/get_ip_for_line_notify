import os
import time

import requests
import schedule

get_ip_url = 'https://api.ipify.org/'  # IP查詢的爬蟲網址
line_notify_api_url = 'https://notify-api.line.me/api/notify'   # Line Notify的爬蟲網址
request_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}

notify_token = ''  # Line Notify Token

ip_txt_path = 'IP.txt'


def main():
    check_ip(get_ip())


def get_ip():
    try:
        r = requests.get(get_ip_url, headers=request_headers, timeout=10)
        ip = r.text

        return ip
    except requests.exceptions.RequestException as e:
        return 'RequestsError：' + str(e)
    except Exception as e:
        return 'Error：' + str(e)


def check_ip(ip):
    try:
        if ip.find('Error') != -1:
            print_and_write_log('check_ip()', 'get_ip() ' + ip)
            return

        file = open(ip_txt_path, mode='a+', encoding='UTF-8')
        file.seek(0)
        original_ip = file.read()
        file.close()

        if ip != original_ip:
            print_and_write_log('check_ip()', '浮動IP異動：' + ip)
            file = open(ip_txt_path, mode='w', encoding='UTF-8')
            file.write(ip)
            file.close()

            msg = '\n現在IP：' + ip

            send_line_notify(notify_token, msg)
    except Exception as e:
        print_and_write_log('check_ip()', str(e))


def send_line_notify(token, msg):
    try:
        notify_headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        notify_payload = {'message': msg}
        r = requests.post(line_notify_api_url,
                          headers=notify_headers, params=notify_payload)

        if r.status_code != 200:
            time.sleep(10)
            send_line_notify(token, msg)
    except Exception as e:
        print_and_write_log('send_line_notify()', str(e))


def print_and_write_log(function, msg):
    try:
        now_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        msg = '[' + now_time + ']　' + function + ' > ' + msg

        print(msg)

        if not os.path.isdir('Log'):
            os.makedirs('Log')
        log_path = 'Log\get_ip_for_line_notify_' + \
            time.strftime("%Y-%m-%d", time.localtime()) + '.txt'
        file = open(log_path, mode='a', encoding='UTF-8')
        file.write(msg + '\n')
        file.close()
    except Exception as e:
        now_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        print('[' + now_time + ']　' + 'print_and_write_log() > ' + str(e))

        if not os.path.isdir('Log'):
            os.makedirs('Log')
        log_path = 'Log\get_ip_for_line_notify_' + \
            time.strftime("%Y-%m-%d", time.localtime()) + '.txt'
        file = open(log_path, mode='a', encoding='UTF-8')
        file.write('[' + now_time + ']　' +
                   'print_and_write_log() > ' + str(e) + '\n')
        file.close()


schedule.every(1).minutes.do(main)

# 開始主Function
if __name__ == '__main__':
    print_and_write_log('初始程序', '現在IP：' + get_ip())
    main()
    while True:
        schedule.run_pending()
        time.sleep(1)
