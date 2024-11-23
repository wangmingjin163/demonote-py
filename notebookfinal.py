import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
from mysql.connector import Error


class Database:
    """数据库操作类，封装与 MySQL 的交互逻辑"""
    def __init__(self):
        try:
            # 连接数据库
            self.connection = mysql.connector.connect(
                host="XX",
                port=3306,
                user="XX",
                password="X",
                database="X"
            )
            self.cursor = self.connection.cursor()
            self.create_table()  # 确保表已创建
        except Error as e:
            # 连接失败提示
            messagebox.showerror("数据库错误", f"连接数据库失败：{e}")
            raise SystemExit

    def create_table(self):
        """创建 notes 表（如果不存在）"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        self.connection.commit()

    def query(self, query, params=None):
        """执行 SELECT 查询"""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def execute(self, query, params=None):
        """执行 INSERT、UPDATE、DELETE 操作"""
        self.cursor.execute(query, params or ())
        self.connection.commit()

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


class NotesApp:
    """记事本应用程序"""
    def __init__(self, root):
        self.db = Database()  # 数据库对象
        self.root = root  # 主窗口
        self.root.title("简单记事本 V1.0")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # 捕获窗口关闭事件，确保程序退出时关闭数据库连接
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 顶部按钮
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        self.btn_add_note = tk.Button(button_frame, text="添加记事", command=self.add_note, width=15)
        self.btn_add_note.grid(row=0, column=0, padx=10)
        self.btn_edit_note = tk.Button(button_frame, text="编辑记事", command=self.edit_note, width=15)
        self.btn_edit_note.grid(row=0, column=1, padx=10)
        self.btn_delete_note = tk.Button(button_frame, text="删除记事", command=self.delete_note, width=15)
        self.btn_delete_note.grid(row=0, column=2, padx=10)

        # 左右布局：记事列表与详情
        self.layout_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.layout_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧列表框
        self.notes_list = tk.Listbox(self.layout_pane, width=30, height=20)
        self.notes_list.bind('<<ListboxSelect>>', self.view_note)
        self.layout_pane.add(self.notes_list)

        # 右侧详情显示框
        self.note_display = tk.Text(self.layout_pane, height=20, width=50, state=tk.DISABLED)
        self.layout_pane.add(self.note_display)

        # 加载记事列表
        self.load_notes()

    def load_notes(self):
        """加载所有记事到列表框"""
        self.notes_list.delete(0, tk.END)
        notes = self.db.query("SELECT id, title FROM notes ORDER BY created_at DESC")
        for note in notes:
            self.notes_list.insert(tk.END, f"{note[0]}. {note[1]}")

         # 清空右侧文本显示区域
        self.note_display.config(state=tk.NORMAL)  # 启用文本框
        self.note_display.delete(1.0, tk.END)  # 清空内容
        self.note_display.config(state=tk.DISABLED)  # 禁用文本框

    def view_note(self, event):
        """查看选中记事详情"""
        selection = self.notes_list.curselection()
        if selection:
            note_id = self.notes_list.get(selection[0]).split(".")[0]
            note = self.db.query("SELECT title, content FROM notes WHERE id = %s", (note_id,))
            if note:
                title, content = note[0]
                self.note_display.config(state=tk.NORMAL)
                self.note_display.delete(1.0, tk.END)
                self.note_display.insert(tk.END, f"标题: {title}\n\n内容:\n{content}")
                self.note_display.config(state=tk.DISABLED)

    def add_note(self):
        """新增记事"""
        title = simpledialog.askstring("新增记事", "请输入记事标题：", parent=self.root)
        if not title:
            messagebox.showwarning("输入无效", "标题不能为空！", parent=self.root)
            return
        content = simpledialog.askstring("新增记事", "请输入记事内容：", parent=self.root)
        if content is None:  # 用户点击取消
            return
        self.db.execute("INSERT INTO notes (title, content) VALUES (%s, %s)", (title, content))
        self.load_notes()
        messagebox.showinfo("操作成功", "记事已成功添加！", parent=self.root)
        self.root.lift()  # 将主窗口提升到最前面

    def edit_note(self):
        """编辑选中记事"""
        selection = self.notes_list.curselection()
        if not selection:
            messagebox.showwarning("选择无效", "请先选择一条记事进行编辑。", parent=self.root)
            return
        note_id = self.notes_list.get(selection[0]).split(".")[0]
        note = self.db.query("SELECT title, content FROM notes WHERE id = %s", (note_id,))
        if note:
            title, content = note[0]
            new_title = simpledialog.askstring("编辑记事", "修改标题：", initialvalue=title, parent=self.root)
            if not new_title:
                messagebox.showwarning("输入无效", "标题不能为空！", parent=self.root)
                return
            new_content = simpledialog.askstring("编辑记事", "修改内容：", initialvalue=content, parent=self.root)
            if new_content is None:  # 用户点击取消
                return
            self.db.execute("UPDATE notes SET title = %s, content = %s WHERE id = %s",
                            (new_title, new_content, note_id))
            self.load_notes()
            messagebox.showinfo("操作成功", "记事已成功更新！", parent=self.root)
            self.root.lift()  # 将主窗口提升到最前面

    def delete_note(self):
        """删除选中记事"""
        selection = self.notes_list.curselection()
        if not selection:
            messagebox.showwarning("选择无效", "请先选择一条记事进行删除。")
            return
        note_id = self.notes_list.get(selection[0]).split(".")[0]
        confirm = messagebox.askyesno("确认删除", "确定要删除这条记事吗？")
        if confirm:
            self.db.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            self.load_notes()
            self.note_display.config(state=tk.NORMAL)
            self.note_display.delete(1.0, tk.END)
            self.note_display.config(state=tk.DISABLED)
            messagebox.showinfo("操作成功", "记事已成功删除！")

    def on_closing(self):
        """程序关闭时关闭数据库连接"""
        self.db.close()  # 确保数据库连接关闭
        self.root.destroy()  # 销毁主窗口


# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
