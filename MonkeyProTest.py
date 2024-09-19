import os
import subprocess
import re
import time
import logging
import datetime
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 初始化 colorama
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    """
    自定义日志格式化类，根据日志级别设置不同的颜色。
    """
    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.msg = Fore.CYAN + record.msg + Style.RESET_ALL
        elif record.levelno == logging.INFO:
            record.msg = Fore.GREEN + record.msg + Style.RESET_ALL
        elif record.levelno == logging.WARNING:
            record.msg = Fore.YELLOW + record.msg + Style.RESET_ALL
        elif record.levelno == logging.ERROR:
            record.msg = Fore.RED + record.msg + Style.RESET_ALL
        elif record.levelno == logging.CRITICAL:
            record.msg = Fore.RED + Style.BRIGHT + record.msg + Style.RESET_ALL
        return super().format(record)

class TimedRotatingFileHandler(logging.Handler):
    def __init__(self, log_file="device_test.log", maxBytes=10*1024*1024, maxFiles=10):
        """
        自定义日志处理器，每次文件切换时生成不同的时间戳文件名
        """
        super().__init__()
        self.log_file = log_file
        self.maxBytes = maxBytes
        self.maxFiles = maxFiles
        self.current_file = self._get_new_filename()
        self.current_size = 0
        self.file_handler = self._create_file_handler(self.current_file)
        self._manage_old_files()

    def _get_new_filename(self):
        """生成带时间戳的新日志文件名"""
        base, ext = self.log_file.rsplit('.', 1)
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return f"{base}_{now}.{ext}"

    def _create_file_handler(self, filename):
        """创建实际的 FileHandler"""
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        return file_handler

    def _manage_old_files(self):
        """管理旧的日志文件，保留最多 maxFiles 个文件"""
        log_dir = Path(self.log_file).parent
        base_name = Path(self.log_file).stem
        extension = Path(self.log_file).suffix

        # 查找所有日志文件并按创建时间排序
        log_files = sorted(log_dir.glob(f"{base_name}_*{extension}"), key=os.path.getctime)

        # 删除最旧的文件，保留最多 maxFiles 个文件
        while len(log_files) > self.maxFiles:
            oldest_file = log_files.pop(0)
            os.remove(oldest_file)
            logging.info(f"Deleted old log file: {oldest_file}")

    def emit(self, record):
        """写日志并检查是否需要切换文件"""
        msg = self.format(record)
        msg_size = len(msg.encode('utf-8')) + 1  # 计算消息大小 (包括换行符)
        
        # 判断是否需要滚动到新文件
        if self.current_size + msg_size > self.maxBytes:
            self.file_handler.close()
            self.current_file = self._get_new_filename()
            self.file_handler = self._create_file_handler(self.current_file)
            self.current_size = 0  # 重置当前文件大小

            # 管理旧文件
            self._manage_old_files()

        self.file_handler.emit(record)
        self.current_size += msg_size

    def close(self):
        """关闭文件处理器"""
        self.file_handler.close()
        super().close()
    
class TimedRotatingFileHandler_(logging.Handler):
    def __init__(self, log_file="device_test.log", maxBytes=10*1024*1024):
        """
        自定义日志处理器，每次文件切换时生成不同的时间戳文件名
        """
        super().__init__()
        self.log_file = log_file
        self.maxBytes = maxBytes
        self.current_file = self._get_new_filename()
        self.current_size = 0
        self.file_handler = self._create_file_handler(self.current_file)

    def _get_new_filename(self):
        """生成带时间戳的新日志文件名"""
        base, ext = self.log_file.rsplit('.', 1)
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return f"{base}_{now}.{ext}"

    def _create_file_handler(self, filename):
        """创建实际的 FileHandler"""
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        return file_handler

    def emit(self, record):
        """写日志并检查是否需要切换文件"""
        msg = self.format(record)
        msg_size = len(msg.encode('utf-8')) + 1  # 计算消息大小 (包括换行符)
        
        # 判断是否需要滚动到新文件
        if self.current_size + msg_size > self.maxBytes:
            self.file_handler.close()
            self.current_file = self._get_new_filename()
            self.file_handler = self._create_file_handler(self.current_file)
            self.current_size = 0  # 重置当前文件大小

        self.file_handler.emit(record)
        self.current_size += msg_size

    def close(self):
        """关闭文件处理器"""
        self.file_handler.close()
        super().close()

def setup_logger(log_file="device_test.log", console_level=logging.DEBUG, file_level=logging.DEBUG):
    """
    配置日志记录器，支持控制台彩色输出，日志文件使用 UTF-8 编码，文件名包含时间戳，文件超过 10MB 会切换到新文件。
    
    参数:
        log_file (str): 基本日志文件名，时间戳将添加到该名称中。
        console_level (int): 控制台日志记录级别，默认 DEBUG。
        file_level (int): 文件日志记录级别，默认 DEBUG。
    
    返回:
        logging.Logger: 配置好的日志记录器。
    """
    # 创建日志记录器
    logger = logging.getLogger("device_test_logger")
    logger.setLevel(logging.DEBUG)
    
    # 当前日期时间，用于生成文件名
    # now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # # 在原文件名中找到 .log 的位置
    # base, ext = log_file.rsplit('.', 1)
    # # 生成新的文件名
    # log_file_with_timestamp = f"{base}_{now}.{ext}"

    # # 创建文件处理器，使用 UTF-8 编码记录日志到文件
    # file_handler = logging.FileHandler(log_file, encoding="utf-8")
    # file_handler.setLevel(file_level)
    
    # 创建文件处理器，使用 UTF-8 编码记录日志到文件，并设置最大文件大小为 10MB
    # file_handler = RotatingFileHandler(log_file_with_timestamp, maxBytes=10*1024*1024, backupCount=10, encoding="utf-8")
    # file_handler.setLevel(file_level)
    
    # 使用自定义的 TimedRotatingFileHandler，每次超过 maxBytes 切换到新的文件
    file_handler = TimedRotatingFileHandler(log_file, maxBytes=10*1024*1024, maxFiles=10)

    file_handler.setLevel(file_level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    # 设置日志格式
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 使用自定义的颜色格式化器
    color_formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(color_formatter)

    # 将处理器添加到日志记录器中
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def get_device_resolution(device_id):
    """
    获取设备的屏幕分辨率。

    参数:
        device_id (str): 设备ID

    返回:
        (int, int): 返回设备的宽度和高度，如果获取失败则返回 (None, None)
    """
    try:
        # 使用 adb 命令获取设备屏幕分辨率
        result = subprocess.run(['adb', '-s', device_id, 'shell', 'wm', 'size'], capture_output=True, text=True)
        output_lines = result.stdout.split('\n')

        # 解析分辨率信息
        for line in output_lines:
            match = re.match(r'Physical size: (\d+)x(\d+)', line)
            if match:
                width, height = match.groups()
                return int(width), int(height)
        
        logger.error("无法解析设备的屏幕分辨率")
        return None, None
    except Exception as e:
        logger.error(f"获取设备分辨率时发生错误: {e}")
        return None, None

def wake_up_and_unlock(device_id):
    """
    唤醒并解锁设备。

    参数:
        device_id (str): 设备ID
    """
    width, height = get_device_resolution(device_id)
    subprocess.run(['adb', '-s', device_id, 'shell', 'svc', 'power', 'stayon', 'true'], capture_output=True, text=True)
    logger.info(f"设备 {device_id} 已唤醒")
    unlock_device_slide(device_id, width, height)

def unlock_device_slide(device_id, width, height):
    """
    模拟滑动解锁设备屏幕。

    参数:
        device_id (str): 设备ID
        width (int): 设备屏幕的宽度
        height (int): 设备屏幕的高度
    """
    if width is None or height is None:
        logger.error(f"设备 {device_id} 的屏幕宽度或高度无效，无法解锁")
        return

    try:
        target = min(width, height)
        subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '1', str(target - 100), '1', '1', '200'])
        logger.info(f"设备 {device_id} 使用滑动解锁成功")
    except Exception as e:
        logger.error(f"解锁设备时发生错误: {e}")

def execute_adb_command(device, class_path, package_name, minutes, throttle, max_workers=5):
    """
    使用ADB命令执行Monkey测试。

    参数:
        device (str): Android设备的序列号
        class_path (str): 执行Monkey的类路径
        package_name (str): 应用包名，或者'all'表示所有应用
        minutes (int): 运行时间（分钟）
        throttle (int): 命令之间的延迟（毫秒）
        max_workers (int): 最大并发线程数
    """
    
    def run_monkey_command(device, class_path, package_name, minutes, throttle):
        cmd = f"adb -s {device} shell CLASSPATH={class_path} exec app_process /system/bin com.android.commands.monkey.Monkey -p {package_name} --agent reuseq --running-minutes {minutes} --throttle {throttle} --pct-touch 30 -v -v"
        
        logger.info(f"执行命令: {cmd}")
        logger.info(f"脚本运行时长(分): {minutes}, 执行间隔(秒): {throttle / 1000}")
        
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
            
            for line in process.stdout:
                logger.info(line.strip())  # 不需要再解码，直接处理字符串
                
            # 等待子进程完成
            process.wait()

            # 检查子进程的退出状态
            if process.returncode != 0:
                stderr_output = process.stderr.read().strip()
                logger.error(f"包名 {package_name} 运行出错, 错误信息: {stderr_output}")
            else:
                logger.info(f"包名 {package_name} 执行完成")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {e}")
        except Exception as e:
            logger.error(f"未知错误: {e}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        if package_name == 'all':
            cmd = f"adb -s {device} shell pm list packages"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            packages = [line.split(':')[1] for line in stdout.decode().splitlines() if line.startswith('package:')]
        else:
            packages = [package_name]
        
        logger.info(f"设备上共安装了 {len(packages)} 个包")

        batch_size = 4  # 每批次任务数量
        delay = 10  # 批次之间的延迟，单位：秒
        
        for i in range(0, len(packages), batch_size):
            batch = packages[i:i + batch_size]
            for package in batch:
                logger.info(f"正在执行包名：{package}")
            futures = [executor.submit(run_monkey_command, device, class_path, package, minutes, throttle) for package in batch]
            for future in futures:
                future.result()
            time.sleep(delay)

def push_library(device_id):
    """
    将框架库和相关文件推送到设备。

    参数:
        device_id (str): 设备ID
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    target_path = "/sdcard/"
    base_file_path = os.path.join(dir_path, "FastBot")
    
    try:
        jar_files = [f for f in os.listdir(base_file_path) if f.endswith(".jar")]
        for jar_file in jar_files:
            file_path = os.path.join(base_file_path, jar_file)
            command = f"adb -s {device_id} push {file_path} {target_path}"
            subprocess.run(command, shell=True, check=True)
        
        local_files = os.path.join(dir_path, "FastBot", "libs")
        subprocess.run(["adb", "-s", device_id, "push", local_files, "/data/local/tmp/"], check=True)
        logger.info("成功推送库文件")
        return True
    except Exception as e:
        logger.error(f"推送库文件失败: {e}")
        return False

def get_connected_devices():
    """
    获取当前连接的设备列表。

    返回:
        list: 设备ID的列表
    """
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    devices = []
    output_lines = result.stdout.strip().split('\n')
    for line in output_lines[1:]:
        device_info = line.split('\t')
        if len(device_info) == 2 and device_info[1] == 'device':
            devices.append(device_info[0])
    return devices

def check_device_online(device_id):
    """
    检查设备是否在线。

    参数:
        device_id (str): 设备ID

    返回:
        bool: 如果设备在线返回 True，否则返回 False
    """
    try:
        device_list = get_connected_devices()
        if device_id in device_list:
            return True
    except Exception as e:
        logger.error(f"检查设备状态时发生错误: {e}")
    return False


if __name__ == "__main__":
    # 初始化日志记录器
    logger = setup_logger(log_file="device_test.log", console_level=logging.INFO, file_level=logging.DEBUG)
    
    device_id = "7NH26450903CG"
    ret = check_device_online(device_id)
    
    if not ret:
        logger.error(f"设备 {device_id} 不在线")
        exit(0)
    
    push_library(device_id)
    wake_up_and_unlock(device_id)

    execute_adb_command(
        device=device_id,
        class_path="/sdcard/monkeyq.jar:/sdcard/framework.jar:/sdcard/fastbot-thirdpart.jar",
        package_name="all",
        minutes=5,
        throttle=500,
        max_workers=1
    )

