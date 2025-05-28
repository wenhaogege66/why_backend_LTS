#!/usr/bin/env python
"""
测试运行脚本
快速运行搜索应用的所有测试
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*50}")
    print(f"🚀 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - 成功")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} - 失败")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            if result.stdout:
                print(f"输出信息: {result.stdout}")
                
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False


def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")
    
    dependencies = [
        ('django', 'Django'),
        ('rest_framework', 'Django REST Framework'),
    ]
    
    missing_deps = []
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} - 已安装")
        except ImportError:
            print(f"❌ {name} - 未安装")
            missing_deps.append(name)
    
    if missing_deps:
        print(f"\n⚠️  缺少依赖: {', '.join(missing_deps)}")
        print("请先安装缺少的依赖包")
        return False
    
    return True


def main():
    """主函数"""
    print("🎯 Search App 测试运行器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 获取项目根目录
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    # 测试命令列表
    test_commands = [
        {
            'command': 'python manage.py test search.test --verbosity=2',
            'description': '运行所有搜索测试'
        },
        {
            'command': 'python manage.py test search.test.test_views.BaseSearchViewTest --verbosity=2',
            'description': '运行基础搜索视图测试'
        },
        {
            'command': 'python manage.py test search.test.test_views.SearchByTitleViewTest --verbosity=2',
            'description': '运行按标题搜索测试'
        },
        {
            'command': 'python manage.py test search.test.test_views.SearchByArtistViewTest --verbosity=2',
            'description': '运行按歌手搜索测试'
        },
        {
            'command': 'python manage.py test search.test.test_views.SearchByAlbumViewTest --verbosity=2',
            'description': '运行按专辑搜索测试'
        },
        {
            'command': 'python manage.py test search.test.test_views.IntegrationTest --verbosity=2',
            'description': '运行集成测试'
        },
        {
            'command': 'python manage.py test search.test.test_views.ErrorHandlingTest --verbosity=2',
            'description': '运行错误处理测试'
        },
        {
            'command': 'python manage.py test search.test.test_views.PerformanceTest --verbosity=2',
            'description': '运行性能测试'
        }
    ]
    
    # 运行测试
    success_count = 0
    total_count = len(test_commands)
    
    for test_cmd in test_commands:
        success = run_command(test_cmd['command'], test_cmd['description'])
        if success:
            success_count += 1
    
    # 显示总结
    print(f"\n{'='*50}")
    print("📊 测试总结")
    print(f"{'='*50}")
    print(f"总测试数: {total_count}")
    print(f"成功: {success_count}")
    print(f"失败: {total_count - success_count}")
    
    if success_count == total_count:
        print("🎉 所有测试都通过了！")
        return 0
    else:
        print("⚠️  有测试失败，请检查上面的错误信息")
        return 1


def run_coverage():
    """运行覆盖率测试"""
    print("\n🔍 运行测试覆盖率分析...")
    
    # 检查是否安装了coverage
    try:
        import coverage
        print("✅ Coverage 已安装")
    except ImportError:
        print("❌ Coverage 未安装，正在安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'])
    
    # 运行覆盖率测试
    commands = [
        'coverage run --source=search manage.py test search.test',
        'coverage report',
        'coverage html --directory=search/test/htmlcov'
    ]
    
    for cmd in commands:
        run_command(cmd, f"执行: {cmd}")
    
    print("\n📈 覆盖率报告已生成在 search/test/htmlcov/ 目录")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Search App 测试运行器')
    parser.add_argument('--coverage', action='store_true', help='运行测试覆盖率分析')
    parser.add_argument('--quick', action='store_true', help='只运行快速测试')
    
    args = parser.parse_args()
    
    if args.coverage:
        run_coverage()
    elif args.quick:
        # 只运行基础测试
        os.chdir(Path(__file__).parent.parent.parent)
        run_command('python manage.py test search.test.test_views.BaseSearchViewTest', '快速测试')
    else:
        sys.exit(main()) 