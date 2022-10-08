# coding:utf-8
# 配置文件

# 测试中心产品名称 包含的 项目名称
TC_Programs = {
        '东语': ['东语','桌面端','数据仓库'],
        '新消费': ['PHP小猪','JAVA新零售'],
        '物业': ['物业','IOT'],
        '业财': ['业财']
}
# 默认产品名称
Default_Program = '东语'

# 测试中心项目名称  对应   禅道产品名称，用于访问禅道 api 自动查询项目
to_zentao_programs = {
    '东语':'HSH-东语移动用户端',
    '桌面端':'HSH-东语桌面用户端',
    '数据仓库':'HSH-东语数据仓库',
    'PHP小猪':'HSH-新零售',
    'JAVA新零售':'HSH-新零售',
    '物业':'HSH-智慧物业',
    'IOT':'HSH-物联网IOT',
    '业财':'HSH-业财系统'
}

# 禅道用户名密码
zentao_account = {
    'user':"admin",
    'password':'FWgP26uUNpXZ7lAw'
}

# 计算综合评分的系数比
# xishubi = 10

# 质量指标范围
quality_target = {
    "工作量": {"index": "0", "name": "工作量", "max": 100, "min": 0, "unity": "percent", "default_score": 100, "unity_score": 1},
    "特殊贡献": {"index": "1", "name": "特殊贡献", "max": 10, "min": 0, "unity": "float.1", "default_score": 0, "unity_score": 1},
    "完成度": {"index": "2", "name": "完成度", "max": 10, "min": 0, "unity": "percent", "default_score": 100, "unity_score": 1},
    "完成时间": {"index": "3", "name": "完成时间", "max": 10, "min": 0, "unity": "hour.4", "default_score": 0, "unity_score": 1},  #实际用延期时间计算，4小时起算
    "提测通过率": {"index": "4", "name": "提测通过率", "max": 10, "min": 0, "unity": "percent", "default_score":100, "unity_score": 1},
    "变更次数": {"index": "5", "name": "变更次数", "max": 10, "min": 0, "unity": "int", "default_score": 0, "unity_score": 1},
    "用例覆盖率": {"index": "6", "name": "用例覆盖率", "max": 10, "min": 0, "unity": "percent", "default_score": 100, "unity_score": 1},
    "冒烟通过率": {"index": "7", "name": "冒烟通过率", "max": 10, "min": 0, "unity": "percent", "default_score": 100, "unity_score": 1},
    "问题解决率": {"index": "8", "name": "问题解决率", "max": 10, "min": 0, "unity": "percent", "default_score": 100, "unity_score": 1},
    "用例评审通过率": {"index": "9", "name": "用例评审通过率", "max": 10, "min": 0, "percent": "day", "default_score": 100, "unity_score": 1},
    "用例执行率": {"index": "10", "name": "用例执行率", "max": 10, "min": 0, "unity": "percent", "default_score": 100, "unity_score": 1},
    "问题探测率": {"index": "11", "name": "问题探测率", "max": 10, "min": 0, "unity": "percent", "default_score": 100, "unity_score": 1},
    "缺陷漏测率": {"index": "12", "name": "缺陷漏测率", "max": 10, "min": 0, "unity": "percent", "default_score": 0, "unity_score": 1},
    "严重级别": {"index": "13", "name": "严重级别", "max": 10, "min": 0, "unity": "int", "default_score": 4, "unity_score": 1},
    "发布成功率": {"index": "14", "name": "发布成功率", "max": 10, "min": 0, "unity": "percent", 100: "percent", "unity_score": 1},
    "线上缺陷数量": {"index": "15", "name": "线上缺陷数量", "max": 10, "min": 0, "unity": "int", "default_score": 0, "unity_score": 2},
    "线下缺陷数量": {"index": "16", "name": "线下缺陷数量", "max": 10, "min": 0, "unity": "int", "default_score": 0, "unity_score": 1},
    "漏测缺陷数量": {"index": "17", "name": "漏测缺陷数量", "max": 10, "min": 0, "unity": "int", "default_score": 0, "unity_score": 4},
    "自动化率": {"index": "18", "name": "自动化率", "max": 10, "min": 0, "unity": "percent", "default_score": 100, "unity_score": 1},
}

# 绩效能力对比关系
performance_index_quality = {
    "学习创新": [
        {"index": "0", "name": "特殊贡献", "max": 10, "min": 0}
    ],
    "技术能力": [
        {"index": "0", "name": "特殊贡献", "max": 10, "min": 0},
        {"index": "2", "name": "特殊贡献", "max": 10, "min": 0},
        {"index": "3", "name": "特殊贡献", "max": 10, "min": 0},
        {"index": "4", "name": "特殊贡献", "max": 10, "min": 0},
        {"index": "0", "name": "特殊贡献", "max": 10, "min": 0},
        {"index": "0", "name": "特殊贡献", "max": 10, "min": 0},
        {"index": "0", "name": "特殊贡献", "max": 10, "min": 0},
    ],
    "沟通协作": [
        {"index": "0", "name": "特殊贡献", "max": 10, "min": 0},
    ],
    "积极性": [
        {"index": "0", "name": "特殊贡献", "max": 10, "min": 0},
    ],
    "责任心": [
        {"index": "0", "name": "特殊贡献", "max": 10, "min": 0},
    ],
    "执行力": [
        {"index": "0", "name": "特殊贡献", "max": 10, "min": 0},
    ],
}