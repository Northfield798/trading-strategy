import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

print("正在启动服务器...")
print(f"项目根目录: {project_root}")

try:
    from web.main import app
    print("成功导入app")
except Exception as e:
    print(f"导入app时出错: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("开始运行服务器...")
    import uvicorn
    uvicorn.run(
        "web.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        reload=True
    ) 