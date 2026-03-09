import asyncio
import io
import socket
import qrcode
from pydglab_ws import StrengthData, FeedbackButton, Channel, StrengthOperationType, RetCode, DGLabWSServer

# 一些测试用的波形数据，这里随便取了一个基本波形
PULSE_DATA_TEST = [
    ((10, 10, 10, 10), (0, 0, 0, 0)), 
    ((10, 10, 10, 10), (0, 5, 10, 20)),
    ((10, 10, 10, 10), (20, 25, 30, 40)),
    ((10, 10, 10, 10), (40, 45, 50, 60)),
    ((10, 10, 10, 10), (60, 65, 70, 80)),
    ((10, 10, 10, 10), (100, 100, 100, 100))
]

def get_local_ip():
    """获取本机局域网IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def print_qrcode(data: str):
    """在控制台打印并生成二维码"""
    print(f"二维码内容: {data}")
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1
    )
    qr.add_data(data)
    
    # 终端打印ASCII二维码
    f = io.StringIO()
    qr.print_ascii(out=f, invert=True)
    f.seek(0)
    print(f.read())
    
    # 生成图片保存
    qr.make(fit=True)
    img = qr.make_image()
    img.save("DG_MVP.png")
    print("二维码已同时保存为 DG_MVP.png，请使用App扫描以连接（确保在同一局域网下）")

async def logic_task(client):
    pulse_iterator = iter(PULSE_DATA_TEST)
    current_strength = 5  # 初始强度测试
    
    while True:
        try:
            # 1. 决定当前的波形数据
            current_pulse = next(pulse_iterator, None)
            if not current_pulse:
                pulse_iterator = iter(PULSE_DATA_TEST)  # 循环发送
                current_pulse = next(pulse_iterator)
                
            # 2. 发送波形数据
            await client.add_pulses(Channel.A, *(current_pulse * 5))
            
            # 3. 设置强度
            # 这里的业务逻辑如果是根据外界参数来定，直接修改 current_strength 即可
            print(f"[逻辑线程] 正在下发波形数据: {current_pulse}, 设置通道A强度: {current_strength}")
            await client.set_strength(
                Channel.A,
                StrengthOperationType.SET_TO,
                current_strength
            )
            
            # 4. 模拟等待外界数据或其他操作
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"[逻辑线程] 发生异常: {e}")
            break

async def main():
    ip_address = get_local_ip()
    port = 5678
    
    print(f"正在启动 WebSocket 服务 [{ip_address}:{port}] ...")
    
    # 这里初始化并开启 DG-Lab WebSocket 服务器
    async with DGLabWSServer(ip_address, port, 60) as server:
        client = server.new_local_client()

        # 生成连接二维码
        url = client.get_qrcode(f"ws://{ip_address}:{port}")
        print_qrcode(url)

        # 阻塞等待客户端（App）扫码连接
        print("等待 App 端绑定...")
        await client.bind()
        print(f"绑定成功！目标设备 ID: {client.target_id}")

        last_strength_data = None
        
        # 启动后台逻辑任务（可替代原来的 yolotask）
        custom_logic_task = asyncio.create_task(logic_task(client))
        
        try:
            # 主循环，负责接收来自于 App 端的持续反馈
            async for data in client.data_generator():
                if isinstance(data, StrengthData):
                    # 当App端调整强度时，会收到这个数据
                    print(f"[App反馈] 收到通道强度数据更新：A通最大:{data.a_limit} B通最大:{data.b_limit}")
                    last_strength_data = data
                    
                elif isinstance(data, FeedbackButton):
                    # 当App端点击圆圈、加减号时，会收到这个数据
                    print(f"[App反馈] 按下了按钮：{data.name}")
                    
                elif data == RetCode.CLIENT_DISCONNECTED:
                    # 设备断开连接
                    print("[App反馈] 设备已断开连接！你可以尝试重新扫码绑定...")
                    await client.rebind()
                    print("[App反馈] 重新绑定成功！")
                    
        except asyncio.CancelledError:
            print("任务被取消。")
            
        finally:
            if not custom_logic_task.done():
                custom_logic_task.cancel()
                try:
                    await custom_logic_task
                except asyncio.CancelledError:
                    pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序手动终止")