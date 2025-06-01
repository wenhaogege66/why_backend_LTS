import os
import sys
import django
from datetime import datetime
from django.conf import settings
from django.test.utils import get_runner

def run_tests():
    """运行测试并生成报告"""
    # 设置Django环境
    os.environ['DJANGO_SETTINGS_MODULE'] = 'music_recommendation.settings'
    django.setup()
    
    # 获取测试运行器
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # 创建测试报告目录
    report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_reports')
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    # 生成报告文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(report_dir, f'test_report_{timestamp}.txt')
    
    # 运行测试并捕获输出
    with open(report_file, 'w', encoding='utf-8') as f:
        # 重定向标准输出到文件
        original_stdout = sys.stdout
        sys.stdout = f
        
        try:
            # 运行测试
            failures = test_runner.run_tests(['user.tests.test_views'])
            
            # 添加测试总结
            print('\n' + '='*50)
            print('测试报告总结')
            print('='*50)
            print(f'测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            print(f'测试结果: {"成功" if failures == 0 else "失败"}')
            print(f'失败数量: {failures}')
            print('='*50)
            
        finally:
            # 恢复标准输出
            sys.stdout = original_stdout
    
    print(f'\n测试报告已生成: {report_file}')
    return failures

if __name__ == '__main__':
    failures = run_tests()
    sys.exit(bool(failures)) 