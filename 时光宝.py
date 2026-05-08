import flet as ft
import sqlite3
import os
import sys
from datetime import datetime

def get_data_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'turning_points.db')

def query_points(keyword, market, db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT 名称, 代码, D₁, D₂, X1, X2, X3, X4, X5, X6, X7, X8
        FROM points
        WHERE 市场=? AND (代码=? OR 名称=?)
    """, (market, keyword, keyword))
    row = cur.fetchone()
    conn.close()
    return row

def main(page: ft.Page):
    page.title = "时光宝"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.bgcolor = ft.Colors.WHITE

    markets = [
        "A股", "美股", "港股", 
        "国内期货", "美期货", 
        "外汇", "虚拟货币", 
        "东财板块", "ETF", "指数"
    ]

    keyword_input = ft.TextField(label="代码或名称", hint_text="例如 600519 或 贵州茅台", width=280)
    market_dropdown = ft.Dropdown(label="市场", width=280, options=[ft.dropdown.Option(m) for m in markets], value="A股")
    result_text = ft.Text("", size=16, color=ft.Colors.BLUE_900, selectable=True)

    def on_query(e):
        keyword = keyword_input.value.strip()
        market = market_dropdown.value
        if not keyword:
            result_text.value = "请输入代码或名称"
            page.update()
            return

        db_path = get_data_path()
        if not os.path.exists(db_path):
            result_text.value = "数据库文件缺失，请先导入数据"
            page.update()
            return

        row = query_points(keyword, market, db_path)
        if row:
            name, code, d1, d2, *x_list = row
            x_vals = [x for x in x_list if x and str(x) != 'nan']
            result = f"📈 {name} ({code}) - {market}\n"
            result += f"📅 上穿日 D₁: {d1}\n"
            result += f"📅 下穿日 D₂: {d2}\n"
            if d1 and d2:
                delta = (datetime.strptime(d2, '%Y-%m-%d') - datetime.strptime(d1, '%Y-%m-%d')).days
                result += f"⏱️ 间隔: {delta}天\n"
            result += f"🔮 本月拐点日: {', '.join(x_vals) if x_vals else '无'}"
            result_text.value = result
        else:
            result_text.value = f"❌ 未找到“{keyword}”在 {market} 市场的数据"
        page.update()

    query_btn = ft.ElevatedButton("查询拐点日", on_click=on_query, width=280)

    help_text = ft.Text(
        "📖 使用说明\n"
        "1. 选择市场\n"
        "2. 输入代码或名称\n"
        "3. 点击查询\n"
        "4. 每月更新数据：替换 turning_points.db",
        size=12,
        color=ft.Colors.GREY_700,
        selectable=True
    )

    page.add(
        ft.Column([
            ft.Text("时光宝", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            ft.Divider(height=20),
            market_dropdown,
            keyword_input,
            query_btn,
            ft.Divider(height=20),
            result_text,
            ft.Divider(height=20),
            help_text,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)