# 天猫订单数据清洗与分析

使用 Python (Pandas/Matplotlib) 完成天猫订单数据的自动化清洗、核心指标核算与可视化分析。企业实战中，清洗后的数据可无缝对接 Power BI/Tableau 搭建动态业务看板。

## 📊 核心分析维度
- **数据清洗**：列名标准化、时间格式转换、异常值/缺失值处理
- **核心指标**：GMV（成交总额）、客单价（AOV）、支付转化率、退款率
- **多维洞察**：省份 TOP5 分布、下单时段分布、订单金额段占比

## 🛠️ 技术栈
- **数据处理**：Pandas, Openpyxl
- **可视化**：Matplotlib
- **企业看板（规划/已接入）**：Power BI

## 📂 项目结构
- `天猫.py`：主程序（数据清洗 + 指标计算 + 图表输出）
- `requirements.txt`：Python 依赖清单
- `.gitignore`：忽略临时文件（如本地 Excel、缓存）
- `tmall_order_report_cleaned.xlsx`：清洗后数据（供 Power BI 消费）

## 🚀 本地运行
