# 交易员跟踪与分析工具

## 项目概述
本项目旨在开发一个交易员跟踪与分析工具，用于识别和跟踪优秀的交易员，分析他们的交易策略，并基于他们的操作开发个人的盈利策略。目前，我们使用 Backpack 交易所的 API 来获取数据。

## 环境要求
- Python 3.10 或更高版本
- 虚拟环境（推荐）

## 安装步骤
1. 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 项目结构
```
src/
├── api/
│   ├── __init__.py
│   └── backpack_client.py  # Backpack API 客户端
├── data/
│   ├── __init__.py
│   └── data_store.py  # 数据存储模块
├── analysis/
│   ├── __init__.py
│   └── trader_analysis.py  # 交易员分析模块
├── test_api.py  # API 测试脚本
├── test_data_store.py  # 数据存储测试脚本
└── __init__.py
```

## 开发计划

### 第一阶段：数据获取和探索（当前）
- [x] 创建 Backpack API 客户端
- [x] 实现基本的市场数据获取功能
- [x] 实现交易数据获取功能
- [x] 实现K线数据获取功能
- [x] 创建数据存储模块
- [ ] 探索 API 的功能和限制
- [ ] 设计数据存储结构

### 第二阶段：分析功能开发
- [ ] 实现交易员筛选算法
- [ ] 计算关键性能指标（胜率、收益率、夏普比率、最大回撤等）
- [ ] 开发交易策略分析模块
- [ ] 实现历史数据回测功能

### 第三阶段：可视化和报告
- [ ] 开发数据可视化模块
- [ ] 创建交易员排名和评分系统
- [ ] 生成分析报告
- [ ] 实现实时数据更新功能

### 第四阶段：优化和扩展
- [ ] 优化性能和资源使用
- [ ] 添加更多分析指标
- [ ] 实现自动化交易信号生成
- [ ] 扩展支持其他交易所

## API 客户端使用示例
```python
from api.backpack_client import BackpackClient
import asyncio

async def main():
    client = BackpackClient()
    
    # 获取市场信息
    markets = await client.get_markets()
    print(f"获取到 {len(markets)} 个市场")
    
    # 获取特定市场的交易历史
    if markets:
        symbol = markets[0].get('symbol')
        trades = await client.get_trades(symbol, limit=10)
        print(f"获取到 {len(trades)} 条交易记录")
    
    # 获取特定市场的K线数据
    if markets:
        symbol = markets[0].get('symbol')
        klines = await client.get_klines(symbol, interval="1h", limit=10)
        print(f"获取到 {len(klines)} 条K线数据")

if __name__ == "__main__":
    asyncio.run(main())
```

## 数据存储使用示例
```python
from data.data_store import DataStore

# 初始化数据存储
data_store = DataStore()

# 保存市场数据
data_store.save_market_data("BTC_USDT", {"symbol": "BTC_USDT", "price": 50000})

# 加载市场数据
market_data = data_store.load_market_data("BTC_USDT")
print(f"市场数据: {market_data}")

# 保存交易数据
data_store.save_trade_data("BTC_USDT", [{"price": 50000, "quantity": 1}])

# 加载交易数据
trade_data = data_store.load_trade_data("BTC_USDT")
print(f"交易数据: {trade_data}")

# 保存K线数据
data_store.save_kline_data("BTC_USDT", "1h", [{"open": 50000, "close": 51000}])

# 加载K线数据
kline_data = data_store.load_kline_data("BTC_USDT", "1h")
print(f"K线数据: {kline_data}")
```

## API 发现和限制
1. **市场数据**
   - 可以获取所有市场的基本信息
   - 每个市场包含符号、基础货币、报价货币等信息

2. **交易数据**
   - 可以获取特定市场的交易历史
   - 包含价格、数量、时间等信息

3. **K线数据**
   - 可以获取不同时间间隔的K线数据
   - 支持的时间间隔：1m, 5m, 15m, 1h, 4h, 1d
   - 需要提供开始时间和结束时间

4. **交易员数据**
   - 目前无法通过API获取交易员列表和详细信息
   - 需要探索其他方式获取交易员数据

## 常见问题
1. **API 连接问题**
   - 确保网络连接正常
   - 检查 API 端点是否正确
   - 验证请求参数是否符合要求

2. **数据获取失败**
   - 检查 API 响应状态码
   - 查看错误日志以获取详细信息
   - 确认请求限制是否超出

3. **K线数据获取失败**
   - 确保提供了正确的时间戳格式
   - 检查时间间隔参数是否正确
   - 验证市场符号是否存在

## 下一步计划
1. 完成 API 探索和数据获取功能
2. 设计并实现数据存储结构
3. 开发交易员分析算法
4. 创建可视化模块

## 贡献指南
欢迎提交问题和改进建议。请确保在提交代码前：
1. 遵循项目的代码风格
2. 添加适当的注释和文档
3. 更新 README.md 文件
4. 测试所有新功能 