import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
from datetime import datetime

# 数据库连接配置
# 创建到 MySQL 数据库的连接，使用指定的主机、端口、用户名、密码和数据库名
db_connection = mysql.connector.connect(
    host="XX",
    port=3306,
    user="XX",
    password="XX",
    database="XX"
)

# 创建一个数据库游标，用于执行 SQL 查询
db_cursor = db_connection.cursor()

# 如果不存在表 `notes`，则创建该表
# 表包含以下字段：
# - id: 自增主键
# - title: 记事标题
# - content: 记事内容
# - created_at: 记事创建时间
# - updated_at: 记事更新时间（自动更新）
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
""")


# 主记事管理应用程序类
class NotesApp:
    def __init__(self, root):
        # 初始化主窗口
        self.root = root
        self.root.title("简单记事本V1.0")  # 设置窗口标题

        # 顶部按钮区域，用于放置新增、编辑和删除按钮
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # 显示记事内容的文本区域
        self.note_display = tk.Text(root, height=10, width=50)

        # 创建“新增记事”按钮并绑定事件
        self.btn_add_note = tk.Button(
            button_frame,
            text="添加记事",
            command=self.add_note
        )
        self.btn_add_note.grid(row=0, column=0, padx=10)

        # 创建“编辑记事”按钮并绑定事件
        self.btn_edit_note = tk.Button(
            button_frame,
            text="编辑记事",
            command=self.edit_note
        )
        self.btn_edit_note.grid(row=0, column=1, padx=10)

        # 创建“删除记事”按钮并绑定事件
        self.btn_delete_note = tk.Button(
            button_frame,
            text="删除记事",
            command=self.delete_note
        )
        self.btn_delete_note.grid(row=0, column=2, padx=10)

        # 列表框和文本框左右分布布局
        # 使用 PanedWindow 创建左右布局
        layout_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        layout_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧：记事列表框
        self.notes_list = tk.Listbox(layout_pane, width=30, height=20)
        layout_pane.add(self.notes_list)

        # 当用户选择列表项时，绑定查看记事详情的事件
        self.notes_list.bind('<<ListboxSelect>>', self.view_note)

        # 右侧：记事文本显示框
        self.note_display = tk.Text(layout_pane, height=20, width=50)
        layout_pane.add(self.note_display)

        # 加载现有的记事到列表框
        self.load_notes()

    # 从数据库加载所有记事并显示在列表框中
    def load_notes(self):
        # 清空列表框
        self.notes_list.delete(0, tk.END)

        # 查询所有记事，按创建时间倒序排列
        db_cursor.execute("SELECT id, title FROM notes ORDER BY created_at DESC")
        notes = db_cursor.fetchall()

        # 将查询到的每条记事添加到列表框中，格式为“id. 标题”
        for note in notes:
            self.notes_list.insert(tk.END, f"{note[0]}. {note[1]}")

        # 清空右侧文本显示区域
        self.note_display.delete(1.0, tk.END)

    # 查看选中的记事详情
    def view_note(self, event):
        # 获取用户当前选择的列表项
        selection = self.notes_list.curselection()
        if selection:
            # 提取选中项的记事 ID
            note_id = self.notes_list.get(selection[0]).split(".")[0]
            # 根据 ID 查询数据库中的标题和内容
            db_cursor.execute("SELECT title, content FROM notes WHERE id = %s", (note_id,))
            note = db_cursor.fetchone()
            # 清空文本显示区域，并显示记事的标题和内容
            self.note_display.delete(1.0, tk.END)
            self.note_display.insert(tk.END, f"标题: {note[0]}\n\n内容:\n{note[1]}")

    # 新增记事
    def add_note(self):
        # 弹出对话框，提示用户输入记事标题
        title = simpledialog.askstring("新增记事", "请输入记事标题：")
        if not title:
            # 如果标题为空，显示警告提示
            messagebox.showwarning("输入无效", "标题不能为空，请重新输入。")
            return
        # 弹出对话框，提示用户输入记事内容
        content = simpledialog.askstring("新增记事", "请输入记事内容：")
        # 向数据库中插入新的记事
        db_cursor.execute("INSERT INTO notes (title, content) VALUES (%s, %s)", (title, content))
        db_connection.commit()  # 提交更改到数据库
        self.load_notes()  # 重新加载记事列表
        messagebox.showinfo("操作成功", "记事已成功添加。")

    # 编辑现有记事
    def edit_note(self):
        # 获取用户当前选择的列表项
        selection = self.notes_list.curselection()
        if not selection:
            # 如果没有选择任何记事，显示警告提示
            messagebox.showwarning("选择无效", "请先选择一条记事进行编辑。")
            return
        # 提取选中项的记事 ID
        note_id = self.notes_list.get(selection[0]).split(".")[0]
        # 查询数据库中对应 ID 的记事标题和内容
        db_cursor.execute("SELECT title, content FROM notes WHERE id = %s", (note_id,))
        note = db_cursor.fetchone()
        # 弹出对话框，允许用户编辑标题和内容
        new_title = simpledialog.askstring("编辑记事", "修改标题：", initialvalue=note[0])
        new_content = simpledialog.askstring("编辑记事", "修改内容：", initialvalue=note[1])
        # 更新数据库中的记事
        db_cursor.execute("UPDATE notes SET title = %s, content = %s WHERE id = %s",
                          (new_title, new_content, note_id))
        db_connection.commit()  # 提交更改
        self.load_notes()  # 重新加载记事列表
        messagebox.showinfo("操作成功", "记事已成功更新。")

    # 删除选中的记事
    def delete_note(self):
        # 获取用户当前选择的列表项
        selection = self.notes_list.curselection()
        if not selection:
            # 如果没有选择任何记事，显示警告提示
            messagebox.showwarning("选择无效", "请先选择一条记事进行删除。")
            return
        # 提取选中项的记事 ID
        note_id = self.notes_list.get(selection[0]).split(".")[0]
        # 弹出确认框，询问用户是否确认删除
        confirm = messagebox.askyesno("确认删除", "确定要删除这条记事吗？")
        if confirm:
            # 从数据库中删除对应的记事
            db_cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            db_connection.commit()  # 提交更改
            self.load_notes()  # 重新加载记事列表
            self.note_display.delete(1.0, tk.END)  # 清空显示区域
            messagebox.showinfo("操作成功", "记事已成功删除。")


# 程序主入口
if __name__ == "__main__":
    root = tk.Tk()  # 创建主窗口
    app = NotesApp(root)  # 创建 NotesApp 实例
    root.mainloop()  # 运行主事件循环
