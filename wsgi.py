import os

from dotenv import load_dotenv

# 手动导入.env中的环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from bluelog import create_app

# 为生产环境创建程序实例
app = create_app('production')
