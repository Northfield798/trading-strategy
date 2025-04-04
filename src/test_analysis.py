import asyncio
import logging
import sys
import os
import json

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.backpack_client import BackpackClient
from src.analysis.trader_analysis import TraderAnalysis

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_data_structure(data: dict, prefix: str = ""):
    """打印数据结构"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                logger.info(f"{prefix}{key}:")
                print_data_structure(value, prefix + "  ")
            else:
                logger.info(f"{prefix}{key}: {type(value).__name__}")
    elif isinstance(data, list) and data:
        logger.info(f"{prefix}List of {len(data)} items")
        print_data_structure(data[0], prefix + "  ")

async def test_backpack_analysis():
    """测试 Backpack 分析功能"""
    client = BackpackClient()
    analyzer = TraderAnalysis()
    
    try:
        # 获取市场数据
        logger.info("获取市场数据...")
        markets = await client.get_markets()
        if markets:
            logger.info(f"获取到 {len(markets)} 个市场")
            
            # 使用第一个市场进行测试
            symbol = markets[0]['symbol']
            logger.info(f"分析市场: {symbol}")
            
            # 获取交易历史
            logger.info("获取交易历史...")
            trades = await client.get_trades(symbol)
            if trades:
                logger.info(f"获取到 {len(trades)} 条交易记录")
                # 打印第一条交易记录的结构
                logger.info("交易记录数据结构:")
                print_data_structure(trades[0])
                # 分析交易数据
                trade_analysis = analyzer.analyze_trades(trades)
                logger.info(f"交易分析结果: {trade_analysis}")
            else:
                logger.warning("未获取到交易记录")
            
            # 获取K线数据
            logger.info("获取K线数据...")
            klines = await client.get_klines(symbol)
            if klines:
                logger.info(f"获取到 {len(klines)} 条K线数据")
                # 打印第一条K线数据的结构
                logger.info("K线数据结构:")
                print_data_structure(klines[0])
            else:
                logger.warning("未获取到K线数据")
        else:
            logger.warning("未找到市场数据")
            
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")

async def main():
    """主测试函数"""
    logger.info("开始测试 Backpack 分析功能...")
    await test_backpack_analysis()

if __name__ == "__main__":
    asyncio.run(main()) 