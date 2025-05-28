# Search App 单元测试文档

## 概述

这个测试套件为 `search` 应用提供了全面的单元测试覆盖，包括所有的搜索视图类和相关功能。

## 测试文件结构

```
search/test/
├── __init__.py              # 包初始化文件
├── test_views.py           # 主要测试文件
├── test_config.py          # 测试配置和工具函数
└── README.md               # 本文档
```

## 测试覆盖范围

### 1. BaseSearchView 测试
- ✅ 搜索参数获取
- ✅ 关键词API调用（成功/失败）
- ✅ 新歌API调用（成功/失败）
- ✅ 异常处理

### 2. SearchByTitleView 测试
- ✅ 按标题搜索成功场景
- ✅ 空关键词处理
- ✅ API错误处理
- ✅ 异常处理
- ✅ 响应数据格式验证

### 3. SearchByArtistView 测试
- ✅ 按歌手搜索成功场景
- ✅ 空关键词处理
- ✅ 响应数据格式验证

### 4. SearchByAlbumView 测试
- ✅ 按专辑搜索成功场景
- ✅ 空关键词处理
- ✅ 响应数据格式验证

### 5. AdvancedSearchView 测试
- ✅ ID参数获取
- ✅ 歌手API调用
- ✅ 专辑API调用
- ✅ 歌曲API调用
- ✅ 歌词API调用

### 6. SearchByArtistSongView 测试
- ✅ 按歌手搜索歌曲成功场景
- ✅ 空ID处理
- ✅ 歌手信息和歌曲列表格式验证

### 7. SearchByAlbumSongView 测试
- ✅ 按专辑搜索歌曲成功场景
- ✅ 空ID处理
- ✅ 专辑信息和歌曲列表格式验证

### 8. SearchBySongView 测试
- ✅ 按歌曲搜索成功场景
- ✅ 空ID处理
- ✅ 无音乐URL处理
- ✅ 无歌词处理

### 9. SearchNewSongView 测试
- ✅ 新歌搜索成功场景
- ✅ API错误处理
- ✅ 异常处理

### 10. 集成测试
- ✅ 完整搜索工作流程
- ✅ 响应结构验证
- ✅ 数据格式完整性检查

### 11. 错误处理测试
- ✅ 网络超时处理
- ✅ 无效JSON响应处理
- ✅ 空响应处理

### 12. 性能测试
- ✅ 大结果集处理
- ✅ 数据完整性验证

## 运行测试

### 方法一：使用 Django 管理命令

```bash
# 运行所有搜索应用测试
python manage.py test search.test

# 运行特定测试类
python manage.py test search.test.test_views.SearchByTitleViewTest

# 运行特定测试方法
python manage.py test search.test.test_views.SearchByTitleViewTest.test_search_by_title_success

# 显示详细输出
python manage.py test search.test --verbosity=2

# 生成测试覆盖率报告（需要安装 coverage）
coverage run --source='.' manage.py test search.test
coverage report
coverage html
```

### 方法二：使用测试配置文件

```bash
cd search/test
python test_config.py
```

### 方法三：使用 pytest（如果安装了 pytest-django）

```bash
# 安装 pytest-django
pip install pytest-django

# 运行测试
pytest search/test/

# 生成覆盖率报告
pytest --cov=search search/test/
```

## 测试数据

测试使用模拟数据，不会对真实的API进行调用。所有的外部API调用都通过 `unittest.mock` 进行模拟。

### 模拟数据示例

```python
# 歌曲搜索响应
MOCK_SONG_RESPONSE = {
    'code': 200,
    'result': {
        'songs': [
            {
                'name': '测试歌曲',
                'id': 123456,
                'ar': [{'id': 1, 'name': '测试歌手', 'tns': [], 'alias': []}],
                'al': {'id': 1, 'name': '测试专辑', 'picUrl': 'http://test.jpg', 'tns': []},
                'publishTime': 1640995200000
            }
        ]
    }
}
```

## 测试最佳实践

### 1. 测试隔离
- 每个测试方法都是独立的
- 使用 `setUp()` 方法初始化测试数据
- 使用 `Mock` 对象避免外部依赖

### 2. 测试命名
- 测试方法名称清晰描述测试场景
- 使用中文注释说明测试目的

### 3. 断言验证
- 验证HTTP状态码
- 验证响应数据结构
- 验证业务逻辑正确性

### 4. 异常处理
- 测试各种错误场景
- 验证错误消息的准确性

## 持续集成

这些测试可以集成到CI/CD流水线中：

```yaml
# GitHub Actions 示例
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python manage.py test search.test
```

## 扩展测试

如果需要添加新的测试：

1. 在 `test_views.py` 中添加新的测试类或方法
2. 在 `test_config.py` 中添加相应的模拟数据
3. 确保测试覆盖成功和失败场景
4. 更新本文档

## 故障排除

### 常见问题

1. **ImportError**: 确保Django设置正确配置
2. **Database Error**: 测试使用内存数据库，确保没有数据库连接问题
3. **Mock Error**: 检查模拟对象的配置是否正确

### 调试技巧

```python
# 在测试中添加调试输出
import pdb; pdb.set_trace()

# 或使用print语句
print(f"Response data: {response.data}")
```

## 测试报告

运行测试后，可以生成详细的测试报告：

```bash
# 生成XML格式报告（适用于CI/CD）
python manage.py test search.test --debug-mode --verbosity=2

# 生成HTML覆盖率报告
coverage html --directory=htmlcov
```

## 贡献指南

在提交代码前，请确保：

1. 所有测试都通过
2. 新功能有相应的测试覆盖
3. 测试覆盖率不低于90%
4. 遵循现有的测试模式和命名约定 