import pandas as pd
import numpy as np
import re

# 1. 读取数据
df = pd.read_excel('tmall_order_report.xlsx')

# 2. 列名强力清洗（关键！解决隐藏空格/不可见字符）
def clean_col_name(col):
    col = str(col).strip()                 # 去首尾空格
    col = re.sub(r'\s+', '', col)          # 去除所有空白字符（含换行、制表符）
    col = col.replace('\xa0', '')          # 去除 Excel 常见不间断空格
    col = col.replace('　', '')            # 去除全角空格
    return col

df.columns = [clean_col_name(c) for c in df.columns]

# （调试用）打印清洗后的列名，确认是否准确
print("清洗后列名：", df.columns.tolist())

# 3. 安全转换时间（此时列名已干净，不会再 KeyError）
df['订单创建时间'] = pd.to_datetime(df['订单创建时间'], errors='coerce')#如果某行数据格式乱码或为空，普通转换会直接报错中断；
# 设为 coerce 后，遇到无法转换的值会强制转为空值（NaT），保证整列代码顺利跑通。
df['订单付款时间'] = pd.to_datetime(df['订单付款时间'], errors='coerce')  # 保留 NaT

# 4. 数据清洗（承接上一轮分析逻辑）
df['有效支付'] = df['订单付款时间'].notna() & (df['买家实际支付金额'] > 0)#判断订单是否成交
valid_df = df[df['有效支付']].copy()
df['净支付'] = df['买家实际支付金额'] - df['退款金额'].fillna(0)

# 5. 基础分析验证
total_orders = len(df)
paid_orders = df['有效支付'].sum()
unpaid_orders = total_orders - paid_orders
pay_rate = paid_orders / total_orders * 100#计算支付转化率

actual_gmv = valid_df['买家实际支付金额'].sum()
refund_gmv = df['退款金额'].sum()
net_gmv = actual_gmv - refund_gmv#最终实际到手金额（净收入）

print(f"数据读取与清洗成功")
print(f"总订单: {total_orders} | 付款: {paid_orders} | 未付: {unpaid_orders} | 转化率: {pay_rate:.2f}%")
print(f"实际GMV: {actual_gmv:.2f} | 退款: {refund_gmv:.2f} | 净GMV: {net_gmv:.2f}")

df.to_excel('tmall_order_report_cleaned.xlsx', index=False)

df = pd.read_excel('tmall_order_report_cleaned.xlsx')

# 定义有效支付
df['有效支付'] = df['订单付款时间'].notna() & (df['买家实际支付金额'] > 0)
valid = df[df['有效支付']]

total = len(df)                          # 总订单
paid = len(valid)                        # 已付款订单
pay_rate = paid / total * 100            # 支付转化率（%）
gmv = valid['买家实际支付金额'].sum()    # GMV（实际成交总额）
refund_rate = (df['退款金额'] > 0).mean() * 100   # 退款率（%）
avg_price = valid['买家实际支付金额'].mean()       # 客单价（均值）

print(f"总订单：{total}")
print(f"支付转化率：{pay_rate:.1f}%")
print(f"GMV：¥{gmv:,.2f}")
print(f"退款率：{refund_rate:.1f}%")
print(f"客单价：¥{avg_price:.2f}")

# 5. 维度分析（接在核心指标打印之后）
print("\n===== 维度分析 =====")

# 5.1 省份 TOP5（按付款订单数）
top5_provinces = valid['收货地址'].value_counts().head(5)
print("省份 TOP5（付款订单）：")
print(top5_provinces)

# 5.2 时段分布（按订单创建小时，需确保'订单创建时间'已转datetime）
df['创建小时'] = df['订单创建时间'].dt.hour
hourly_orders = df['创建小时'].value_counts().sort_index()
print("\n各时段订单分布：")
print(hourly_orders)

# 5.3 金额段分布（客单价分层）
bins = [0, 50, 100, 200, 500, 10000]
labels = ['0-50', '50-100', '100-200', '200-500', '500+']
valid['金额段'] = pd.cut(valid['买家实际支付金额'], bins=bins, labels=labels)
price_seg = valid['金额段'].value_counts().sort_index()
print("\n金额段分布（付款订单）：")
print(price_seg)

# 6. 可视化（可选，需确保前面已 import matplotlib）
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows 常用黑体
plt.rcParams['axes.unicode_minus'] = False    # 避免负号显示为方块
top5_provinces.plot(kind='bar', color='skyblue', title='省份 TOP5（付款订单）')
plt.ylabel('订单数')
plt.xticks(rotation=45)
plt.title('省份 TOP5')
plt.show()

# 图2：时段分布
plt.figure()  # 开启新画布
hourly_orders.plot(kind='line', marker='o', color='orange', title='各时段订单分布')
plt.xlabel('小时')
plt.ylabel('订单数')
plt.tight_layout()
plt.show()

# 图3：金额段分布
plt.figure()
price_seg.plot(kind='bar', color='green', title='金额段分布（付款订单）')
plt.xlabel('金额段')
plt.ylabel('订单数')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# 7. 最终结论与建议输出
print("\n===== 分析结论与建议 =====")
print("1. 整体转化：总订单28010，支付转化率67.7%，未付款流失32.3%（9055单），退款率20.2%，需关注支付提醒与售后。")
print("2. 客单结构：客单价¥100.37，GMV主力在0-200元区间（占比超90%），高客单（500+）仅107单。")
print("3. 地域聚焦：上海、广东、北京、江苏、浙江为TOP5，订单集中，适合定向投放与包邮策略。")
print("4. 时段运营：结合各时段分布，在高峰时段（可看折线图）做限时促销/催付，提升转化。")
print("5. 建议：优化未付款短信提醒降低流失，针对0-200元主力区间推组合套餐拉升客单。")