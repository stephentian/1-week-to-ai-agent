"""
Blog API 测试脚本 - Day 3 实战项目验证
"""

import subprocess
import sys
import os
import urllib.request
import urllib.error
import json
import time

def run_test(test_name, test_func):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print('='*60)
    
    try:
        result = test_func()
        if result:
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
        return result
    except Exception as e:
        print(f"❌ {test_name} 异常: {e}")
        return False


def test_api_health():
    """测试API健康检查"""
    try:
        response = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
        data = json.loads(response.read().decode())
        
        if data.get("status") == "healthy":
            print("API健康检查通过")
            print(f"响应: {json.dumps(data, indent=2)}")
            return True
        return False
    except Exception as e:
        print(f"无法连接API: {e}")
        return False


def test_api_docs():
    """测试API文档"""
    try:
        response = urllib.request.urlopen("http://localhost:8000/docs", timeout=5)
        if response.status == 200:
            print("Swagger UI文档可访问 (http://localhost:8000/docs)")
            return True
        return False
    except:
        return False


def test_create_user():
    """测试用户注册"""
    data = {
        "email": f"test{int(time.time())}@example.com",
        "username": f"testuser{int(time.time())}",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    req = urllib.request.Request(
        "http://localhost:8000/api/users/",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            user_data = json.loads(response.read().decode())
            
            if response.status == 201 and user_data.get('id'):
                print(f"用户创建成功: {user_data['username']} (ID: {user_data['id']})")
                return True, user_data
            return False, None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"HTTP错误 {e.code}: {error_body}")
        return False, None


def test_get_users():
    """测试获取用户列表"""
    try:
        response = urllib.request.urlopen("http://localhost:8000/api/users/", timeout=5)
        users = json.loads(response.read().decode())
        
        print(f"获取到 {len(users)} 个用户")
        for user in users[:3]:  # 只显示前3个
            print(f"  - {user['username']} ({user['email']})")
        
        return len(users) > 0
    except Exception as e:
        print(f"获取用户列表失败: {e}")
        return False


def main():
    """主测试函数"""
    print("""
╔════════════════════════════════════════╗
║     🧪 Blog API 测试套件               ║
║     Day 3 后端开发技能提升验证           ║
╚════════════════════════════════════════╝
    """)
    
    # 检查API是否启动
    print("\n⏳ 检查API服务状态...")
    if not test_api_health():
        print("\n⚠️ API服务未启动！请先运行:")
        print("   cd blog-api")
        print("   pip install -r requirements.txt")
        print("   uvicorn app.main:app --reload --port 8000")
        print("\n或者使用Docker:")
        print("   docker build -t blog-api .")
        print("   docker run -p 8000:8000 blog-api")
        return 1
    
    results = []
    
    # 运行测试
    results.append(run_test("API文档访问", test_api_docs))
    results.append(run_test("用户注册", lambda: test_create_user()[0]))
    results.append(run_test("用户列表", test_get_users))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！Blog API 功能正常！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试未通过")
        return 1


if __name__ == "__main__":
    sys.exit(main())
