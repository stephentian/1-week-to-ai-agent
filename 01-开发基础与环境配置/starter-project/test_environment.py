#!/usr/bin/env python3
"""
Day 1 实战项目测试脚本
验证开发环境是否正确搭建
"""

import subprocess
import sys
import os
import json
import time
import urllib.request
import urllib.error

def run_command(cmd, description):
    """执行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"🔍 测试: {description}")
    print(f"{'='*60}")
    print(f"命令: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ 成功")
            if result.stdout.strip():
                print(f"输出:\n{result.stdout}")
            return True
        else:
            print(f"❌ 失败 (返回码: {result.returncode})")
            if result.stderr.strip():
                print(f"错误:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ 超时")
        return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


def test_git():
    """测试Git环境"""
    # 检查Git版本
    success = run_command("git --version", "Git 版本检查")
    
    if success and os.path.exists(".git"):
        # 初始化Git仓库（如果不存在）
        run_command("git init", "初始化Git仓库")
        
        # 创建初始提交
        with open("test.txt", "w") as f:
            f.write("test")
        run_command("git add .", "Git add 文件")
        run_command('git commit -m "chore: 测试提交"', "Git 提交")
        os.remove("test.txt")
    
    return success


def test_python():
    """测试Python环境"""
    # 检查Python版本
    success = run_command("python --version", "Python 版本检查")
    
    if success:
        # 测试虚拟环境创建
        venv_dir = "test_venv"
        if not os.path.exists(venv_dir):
            run_command(f"python -m venv {venv_dir}", "创建虚拟环境")
        
        # 测试pip安装依赖
        if os.path.exists(venv_dir):
            pip_path = os.path.join(venv_dir, "Scripts", "pip") if os.name == 'nt' else os.path.join(venv_dir, "bin", "pip")
            run_command(f"{pip_path} install fastapi uvicorn", "安装FastAPI和Uvicorn")
            
            # 运行后端服务并测试
            print("\n" + "="*60)
            print("🚀 启动后端服务测试...")
            print("="*60)
            
            python_path = os.path.join(venv_dir, "Scripts", "python") if os.name == 'nt' else os.path.join(venv_dir, "bin", "python")
            
            # 启动服务（后台）
            import subprocess
            process = subprocess.Popen(
                f"{python_path} ../backend/main.py",
                shell=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务启动
            time.sleep(3)
            
            try:
                # 测试健康检查端点
                response = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
                data = json.loads(response.read().decode())
                
                if data.get("status") == "healthy":
                    print("✅ 后端健康检查通过")
                    print(f"   响应: {json.dumps(data, indent=2)}")
                    health_ok = True
                else:
                    print("❌ 后端健康检查失败")
                    health_ok = False
                    
            except Exception as e:
                print(f"❌ 无法连接后端服务: {e}")
                health_ok = False
            finally:
                # 停止服务
                process.terminate()
                process.wait()
                time.sleep(1)
            
            # 清理虚拟环境（可选）
            # run_command(f"rm -rf {venv_dir}", "清理虚拟环境")
    
    return success


def test_nodejs():
    """测试Node.js环境"""
    # 检查Node.js版本
    node_success = run_command("node --version", "Node.js 版本检查")
    
    # 检查npm/pnpm版本
    npm_success = run_command("npm --version", "npm 版本检查")
    pnpm_success = run_command("pnpm --version", "pnpm 版本检查")
    
    if node_success and npm_success:
        # 安装前端依赖
        frontend_dir = "../frontend"
        if os.path.exists(frontend_dir):
            original_dir = os.getcwd()
            os.chdir(frontend_dir)
            
            run_command("npm install", "安装前端依赖")
            
            # 构建测试
            build_success = run_command("npm run build", "构建前端项目")
            
            os.chdir(original_dir)
            
            return build_success
    
    return node_success or npm_success


def test_docker():
    """测试Docker环境"""
    # 检查Docker版本
    docker_success = run_command("docker --version", "Docker 版本检查")
    
    if docker_success:
        # 检查Docker Compose
        compose_success = run_command("docker-compose --version", "Docker Compose 版本检查")
        
        if compose_success:
            # 测试Docker Compose构建
            docker_dir = "./docker"
            if os.path.exists(docker_dir):
                original_dir = os.getcwd()
                os.chdir(docker_dir)
                
                print("\n" + "="*60)
                print("🐳 Docker Compose 构建测试...")
                print("="*60)
                
                build_success = run_command("docker-compose up -d --build", "构建并启动Docker服务")
                
                if build_success:
                    print("\n⏳ 等待服务启动...")
                    time.sleep(10)
                    
                    # 检查容器状态
                    status_success = run_command("docker-compose ps", "检查容器状态")
                    
                    # 测试服务访问
                    try:
                        response = urllib.request.urlopen("http://localhost:3000/", timeout=5)
                        print("✅ 前端服务可访问 (http://localhost:3000)")
                        frontend_ok = True
                    except:
                        print("❌ 前端服务不可访问")
                        frontend_ok = False
                    
                    try:
                        response = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
                        print("✅ 后端API可访问 (http://localhost:8000)")
                        backend_ok = True
                    except:
                        print("❌ 后端API不可访问")
                        backend_ok = False
                    
                    # 清理
                    print("\n清理Docker资源...")
                    run_command("docker-compose down -v", "停止并清理Docker服务")
                    
                    return frontend_ok and backend_ok
                
                os.chdir(original_dir)
    
    return docker_success


def main():
    """主测试函数"""
    print("""
╔════════════════════════════════════════╗
║     🧪 Day 1 实战项目测试套件           ║
║     开发基础与环境配置验证               ║
╚══════════════════════════════════════╝
    """)
    
    results = {
        "Git": test_git(),
        "Python": test_python(),
        "Node.js": test_nodejs(),
        "Docker": test_docker()
    }
    
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:.<20} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("-"*60)
    print(f"总计: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！Day 1 环境搭建成功！")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} 个测试未通过，请检查环境配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
