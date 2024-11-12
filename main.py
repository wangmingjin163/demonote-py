import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
from datetime import datetime

# 连接数据库
conn = mysql.connector.connect(
    host="XXX.wxcsxy.top",
    port=33060,
    user="root", 
    password="XXX@SSD",
    database="exam"
)

cursor = conn.cursor()

# 创建表（如果尚未创建）
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
""")

# 主应用程序窗口
class NotebookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("简单记事本")
        
        # 顶部按钮布局
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        # 记事内容显示区域
        self.note_content = tk.Text(root, height=10, width=50)
        
        self.btn_add = tk.Button(
            button_frame,
            text="添加记事",
            command=self.add_note
        )
        self.btn_add.grid(row=0, column=0, padx=10)
        
        self.btn_edit = tk.Button(
            button_frame,
            text="编辑记事",
            command=self.edit_note
        )
        self.btn_edit.grid(row=0, column=1, padx=10)
        
        self.btn_delete = tk.Button(
            button_frame,
            text="删除记事",
            command=self.delete_note
        )
        self.btn_delete.grid(row=0, column=2, padx=10)
        
        # 记事列表
        self.notes_listbox = tk.Listbox(root, width=50, height=15)
        self.notes_listbox.pack(pady=10)
        self.notes_listbox.bind('<<ListboxSelect>>', self.view_note)
        self.note_content.pack(pady=10)
        
        self.load_notes()
    
    # 加载所有记事
    def load_notes(self):
        self.notes_listbox.delete(0, tk.END)
        cursor.execute("SELECT id, title FROM notes ORDER BY created_at DESC")
        notes = cursor.fetchall()
        for note in notes:
            self.notes_listbox.insert(tk.END, f"{note[0]}. {note[1]}")
    
    # 查看选中的记事
    def view_note(self, event):
        selection = self.notes_listbox.curselection()
        if selection:
            note_id = self.notes_listbox.get(selection[0]).split(".")[0]
            cursor.execute("SELECT title, content FROM notes WHERE id = %s", (note_id,))
            note = cursor.fetchone()
            self.note_content.delete(1.0, tk.END)
            self.note_content.insert(tk.END, f"标题: {note[0]}\n\n内容:\n{note[1]}")
    
    # 添加新记事
    def add_note(self):
        title = simpledialog.askstring("添加记事", "请输入记事标题：")
        if not title:
            messagebox.showwarning("输入错误", "标题不能为空！")
            return
        content = simpledialog.askstring("添加记事", "请输入记事内容：")
        cursor.execute("INSERT INTO notes (title, content) VALUES (%s, %s)", (title, content))
        conn.commit()
        self.load_notes()
        messagebox.showinfo("添加成功", "记事已添加。")
    
    # 编辑记事
    def edit_note(self):
        selection = self.notes_listbox.curselection()
        if not selection:
            messagebox.showwarning("选择错误", "请先选择一个记事进行编辑。")
            return
        note_id = self.notes_listbox.get(selection[0]).split(".")[0]
        cursor.execute("SELECT title, content FROM notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        new_title = simpledialog.askstring("编辑记事", "修改标题：", initialvalue=note[0])
        new_content = simpledialog.askstring("编辑记事", "修改内容：", initialvalue=note[1])
        cursor.execute("UPDATE notes SET title = %s, content = %s WHERE id = %s", 
                      (new_title, new_content, note_id))
        conn.commit()
        self.load_notes()
        messagebox.showinfo("编辑成功", "记事已更新。")
    
    # 删除记事
    def delete_note(self):
        selection = self.notes_listbox.curselection()
        if not selection:
            messagebox.showwarning("选择错误", "请先选择一个记事进行删除。")
            return
        note_id = self.notes_listbox.get(selection[0]).split(".")[0]
        confirm = messagebox.askyesno("确认删除", "确定要删除该记事吗？")
        if confirm:
            cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            conn.commit()
            self.load_notes()
            self.note_content.delete(1.0, tk.END)
            messagebox.showinfo("删除成功", "记事已删除。")

# 启动应用程序
if __name__ == "__main__":
    root = tk.Tk()
    app = NotebookApp(root)
    root.mainloop()