import datetime
import json
import os
import re
from typing import List, Dict, Optional

class TodoList:
    def __init__(self):
        self.tasks: Dict[str, List[Dict]] = {}
        self.next_task_id = 1
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists('tasks.json'):
            with open('tasks.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = data.get('tasks', {})
                self.next_task_id = data.get('next_task_id', 1)

    def save_tasks(self):
        data = {
            'tasks': self.tasks,
            'next_task_id': self.next_task_id
        }
        with open('tasks.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def parse_date(self, date_str: str) -> Optional[str]:
        """解析日期字符串，返回YYYY-MM-DD格式的日期"""
        today = datetime.datetime.now()
        
        # 处理相对日期
        if date_str == '今天':
            return today.strftime('%Y-%m-%d')
        elif date_str == '明天':
            return (today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        elif date_str == '后天':
            return (today + datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        
        # 处理绝对日期
        try:
            # 尝试解析YYYY-MM-DD格式
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return date.strftime('%Y-%m-%d')
        except ValueError:
            try:
                # 尝试解析MM-DD格式（默认为当前年）
                date = datetime.datetime.strptime(date_str, '%m-%d')
                date = date.replace(year=today.year)
                # 如果日期已经过去，使用下一年
                if date < today:
                    date = date.replace(year=today.year + 1)
                return date.strftime('%Y-%m-%d')
            except ValueError:
                return None

    def find_task_by_id(self, task_id: int) -> tuple[Optional[str], Optional[Dict]]:
        """通过任务ID查找任务及其日期"""
        for date, tasks in self.tasks.items():
            for task in tasks:
                if task['id'] == task_id:
                    return date, task
        return None, None

    def add_task(self, description: str, date_str: str = '今天', is_daily: bool = False):
        date = self.parse_date(date_str)
        if date is None:
            print("无效的日期格式，请使用'今天'、'明天'、'后天'或'YYYY-MM-DD'格式")
            return

        if date not in self.tasks:
            self.tasks[date] = []
        
        task = {
            'id': self.next_task_id,
            'description': description,
            'is_daily': is_daily,
            'completed': False
        }
        self.tasks[date].append(task)
        self.next_task_id += 1
        self.save_tasks()
        print(f"添加任务成功: {description} (日期: {date})")

    def show_tasks(self, date_str: str = '今天'):
        date = self.parse_date(date_str)
        if date is None:
            print("无效的日期格式，请使用'今天'、'明天'、'后天'或'YYYY-MM-DD'格式")
            return

        if date not in self.tasks or not self.tasks[date]:
            print(f"{date_str}没有待办任务")
            return

        print(f"\n{date_str}的任务 ({date}):")
        for task in self.tasks[date]:
            status = "✓" if task['completed'] else " "
            daily = " [每日]" if task['is_daily'] else ""
            print(f"{task['id']}. [{status}] {task['description']}{daily}")

    def complete_task(self, task_id: int):
        date, task = self.find_task_by_id(task_id)
        if task is None:
            print("未找到该任务")
            return

        task['completed'] = True
        self.save_tasks()
        print(f"任务 {task_id} 已完成")

    def delete_task(self, task_id: int):
        date, task = self.find_task_by_id(task_id)
        if task is None:
            print("未找到该任务")
            return

        self.tasks[date] = [t for t in self.tasks[date] if t['id'] != task_id]
        self.save_tasks()
        print(f"任务 {task_id} 已删除")

    def edit_task(self, task_id: int, new_description: str):
        date, task = self.find_task_by_id(task_id)
        if task is None:
            print("未找到该任务")
            return

        task['description'] = new_description
        self.save_tasks()
        print(f"任务 {task_id} 已更新")

def main():
    todo = TodoList()
    print("欢迎使用待办事项列表！")
    print("命令列表：")
    print("add <任务描述> [日期] [daily] - 添加任务（日期默认为今天，可选daily表示每日任务）")
    print("show [日期] - 显示指定日期的任务（默认为今天）")
    print("complete <任务ID> - 完成任务")
    print("delete <任务ID> - 删除任务")
    print("edit <任务ID> <新描述> - 编辑任务")
    print("exit - 退出程序")
    print("\n日期格式：")
    print("- 今天/明天/后天")
    print("- YYYY-MM-DD（如：2024-03-15）")
    print("- MM-DD（如：03-15，默认为当前年）")

    while True:
        command = input("\n请输入命令: ").strip().split()
        if not command:
            continue

        cmd = command[0].lower()
        
        if cmd == 'exit':
            break
        elif cmd == 'show':
            date_str = command[1] if len(command) > 1 else '今天'
            todo.show_tasks(date_str)
        elif cmd == 'add':
            if len(command) < 2:
                print("请提供任务描述")
                continue
            
            # 检查是否有日期参数
            date_str = '今天'
            is_daily = False
            description_parts = command[1:]
            
            # 检查最后一个参数是否是daily
            if description_parts[-1].lower() == 'daily':
                is_daily = True
                description_parts = description_parts[:-1]
            
            # 检查倒数第二个参数是否是日期
            if len(description_parts) > 1:
                potential_date = description_parts[-1]
                if todo.parse_date(potential_date) is not None:
                    date_str = potential_date
                    description_parts = description_parts[:-1]
            
            description = ' '.join(description_parts)
            todo.add_task(description, date_str, is_daily)
        elif cmd == 'complete':
            if len(command) != 2:
                print("请提供任务ID")
                continue
            try:
                task_id = int(command[1])
                todo.complete_task(task_id)
            except ValueError:
                print("任务ID必须是数字")
        elif cmd == 'delete':
            if len(command) != 2:
                print("请提供任务ID")
                continue
            try:
                task_id = int(command[1])
                todo.delete_task(task_id)
            except ValueError:
                print("任务ID必须是数字")
        elif cmd == 'edit':
            if len(command) < 3:
                print("请提供任务ID和新描述")
                continue
            try:
                task_id = int(command[1])
                new_description = ' '.join(command[2:])
                todo.edit_task(task_id, new_description)
            except ValueError:
                print("任务ID必须是数字")
        else:
            print("未知命令")

if __name__ == "__main__":
    main() 