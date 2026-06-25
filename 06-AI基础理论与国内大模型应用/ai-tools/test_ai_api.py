"""
AI API测试脚本 - Day 6 AI基础应用
验证DeepSeek和豆包API的连接和基本功能
"""

import sys
import os
import time

def test_deepseek():
    """测试DeepSeek客户端"""
    print("\n" + "="*60)
    print("🤖 测试 DeepSeek API")
    print("="*60)
    
    try:
        from deepseek_client import DeepSeekClient
        
        client = DeepSeekClient()
        
        if not client.config.api_key:
            print("⚠️ 未配置 DEEPSEEK_API_KEY，跳过测试")
            return None
        
        # 测试对话
        result = client.chat("你好，请用一句话介绍你自己")
        
        if result["success"]:
            print(f"✅ DeepSeek 对话成功")
            print(f"   回复: {result['content'][:100]}...")
            print(f"   耗时: {result['response_time_ms']}ms")
            
            # 测试代码生成
            code_result = client.generate_code("实现一个计算斐波那契数列的函数")
            if code_result["success"]:
                print(f"✅ DeepSeek 代码生成成功")
                print(f"   代码长度: {len(code_result['content'])} 字符")
            
            client.close()
            return True
        else:
            print(f"❌ DeepSeek 对话失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek 测试异常: {e}")
        return False


def test_doubao():
    """测试豆包客户端"""
    print("\n" + "="*60)
    print("🤖 测试 豆包(火山引擎) API")
    print("="*60)
    
    try:
        from doubao_client import DoubaoClient
        
        client = DoubaoClient()
        
        if not client.config.api_key:
            print("⚠️ 未配置 DOUBAO_API_KEY，跳过测试")
            return None
        
        # 测试角色扮演
        role_result = client.role_play(
            message="请用一句话说明你的核心价值观",
            character="孔子"
        )
        
        if role_result["success"]:
            print(f"✅ 豆包 角色扮演成功")
            print(f"   回复: {role_result['content'][:100]}...")
            print(f"   耗时: {role_result['response_time_ms']}ms")
            
            # 测试翻译
            trans_result = client.translate(
                text="人工智能正在改变世界",
                target_lang="英文"
            )
            if trans_result["success"]:
                print(f"✅ 豆包 翻译成功")
                print(f"   翻译结果: {trans_result['content'][:100]}...")
            
            client.close()
            return True
        else:
            print(f"❌ 豆包 角色扮演失败: {role_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 豆包 测试异常: {e}")
        return False


def test_unified_service():
    """测试统一LLM服务"""
    print("\n" + "="*60)
    print("🌐 测试 统一 LLM 服务层")
    print("="*60)
    
    try:
        from llm_service import get_llm_service
        
        service = get_llm_service()
        
        if not service.clients:
            print("⚠️ 没有可用的AI服务，请检查API密钥配置")
            return None
        
        # 查看状态
        status = service.get_status()
        print(f"📊 可用提供商数量: {status['total_providers']}")
        print(f"🎯 主服务商: {status['primary']}")
        
        # 测试智能路由
        code_task = service.generate_code("打印Hello World", "python")
        if code_task.get("success"):
            print(f"✅ 代码生成任务 → 自动选择: {code_task['provider']}")
        
        creative_task = service.chat("写一首关于AI的诗")
        if creative_task.get("success"):
            print(f"✅ 创意写作任务 → 自动选择: {creative_task['provider']}")
        
        service.close_all()
        return True
        
    except Exception as e:
        print(f"❌ 统一服务测试异常: {e}")
        return False


def main():
    """主测试函数"""
    print("""
╔════════════════════════════════════════╗
║     🧪 AI API 完整测试套件               ║
║     Day 6 AI基础理论与国内大模型应用      ║
╚════════════════════════════════════════╝
    """)
    
    results = {
        "DeepSeek": test_deepseek(),
        "豆包(火山引擎)": test_doubao(),
        "统一LLM服务": test_unified_service()
    }
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = 0
    total = 0
    
    for name, result in results.items():
        if result is None:
            status = "⏭️ 跳过"
        elif result:
            status = "✅ 通过"
            passed += 1
        else:
            status = "❌ 失败"
        
        total += 1 if result is not None else 0
        print(f"{name:<20} {status}")
    
    print("-"*60)
    
    if passed > 0:
        print(f"\n🎉 通过 {passed}/{total} 个测试！AI工具服务正常工作！")
        return 0
    elif total == 0:
        print("\n⚠️ 所有测试被跳过，请先配置API密钥")
        print("\n创建 .env 文件并添加:")
        print("  DEEPSEEK_API_KEY=your-key-here")
        print("  DOUBAO_API_KEY=your-key-here")
        print("  DOUBAO_APP_ID=your-app-id")
        return 1
    else:
        print(f"\n❌ 所有测试失败，请检查API密钥和网络连接")
        return 1


if __name__ == "__main__":
    sys.exit(main())
