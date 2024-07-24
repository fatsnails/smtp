import sys
import json
import socket
import base64
import time
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QPushButton, QListWidget, QMessageBox, QStackedWidget
from PyQt5.QtWidgets import QDialog

# SMTP服务器信息
mail_server = "smtp.qq.com"
mail_port = 587
pw = "cwubourpivtibebf"
# 通讯录

# ...（上面的代码保持不变）

class LoginWidget(QWidget):
    loginSuccessful = pyqtSignal(str, str, str, dict)
    addressBookOpened = pyqtSignal(str)

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.username = None
        self.password = None
        self.from_address = None
        self.address_book = None
        self.initUI()

    def initUI(self):
        self.username_label = QLabel("用户名:")
        self.username_entry = QLineEdit()
        self.password_label = QLabel("密码:")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("登录")
        login_button.clicked.connect(self.loginClicked)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(login_button)
        self.setLayout(layout)

    def loginClicked(self):
        self.from_address = self.username_entry.text()
        self.username = base64.b64encode(self.from_address.encode()).decode()
        self.password = base64.b64encode(self.password_entry.text().encode()).decode()

        # 调用openAddressBook函数，将address_book和address_book_filename传入
        self.address_book_filename = f"{self.from_address}_address_book.json"
        print(self.address_book_filename)
        self.address_book = openAddressBook({}, self.address_book_filename)  # 初始化为一个空的字典
        self.addressBookOpened.emit(self.address_book_filename)
        self.loginSuccessful.emit(self.from_address, self.username, self.password,self.address_book)
        self.stacked_widget.setCurrentIndex(1)
        
    # ...（下面的代码保持不变）



class EmailClientWidget(QMainWindow):
    draftDeleted = pyqtSignal()
    sent_emailsDeleted = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.address_book = {}
        self.initUI()
        self.draft = {}
        self.sent_emails = {}


    def updateCredentials(self, from_address, username, password,address_book):
        self.from_address = from_address
        self.username = username
        self.password = password
        self.address_book = address_book
        #print(len(self.address_book))
        for contact in self.address_book:
            self.contact_listbox.addItem(contact)
        self.contact_listbox.itemClicked.connect(self.select_contact)
        #with open(f'{from_address}_address_book.json', 'r', encoding='utf-8') as json_file:
        #    self.address_book = json.load(json_file)  # 更新类的成员变量address_book的值

    def initUI(self):
        self.setWindowTitle("邮件客户端")

        # 收件人选择
        recipient_label = QLabel("收件人:")
        self.recipient_entry = QLineEdit()
        self.recipient_entry.setText("recipient@example.com")

        # 通讯录列表
        self.contact_listbox = QListWidget()
        # 通讯录选择按钮
        select_contact_button = QPushButton("选择联系人")
        select_contact_button.clicked.connect(self.select_contact)

        # 主题输入
        subject_label = QLabel("主题:")
        self.subject_entry = QLineEdit()

        # 内容输入
        message_label = QLabel("内容:")
        self.message_text = QTextEdit()

        # 发送按钮和保存到草稿箱按钮
        send_button = QPushButton("发送邮件")
        send_button.clicked.connect(self.send_email)
        draft_button = QPushButton("保存到草稿箱")
        draft_button.clicked.connect(self.load_drafts)
        draft_button.clicked.connect(self.save_to_draft)
    
        # 添加联系人按钮    
        add_contact_button = QPushButton("添加联系人")
        add_contact_button.clicked.connect(self.add_contact_dialog)

        # 删除联系人按钮
        delete_contact_button = QPushButton("删除联系人")
        delete_contact_button.clicked.connect(self.delete_contact) 

        # 添加按钮以显示草稿箱
        drafts_button = QPushButton("草稿箱")
        drafts_button.clicked.connect(self.load_drafts)
        drafts_button.clicked.connect(self.show_drafts)

        # 添加查看已发送邮件按钮
        view_sent_button = QPushButton("查看已发送邮件")
        view_sent_button.clicked.connect(self.load_sent_emails)
        view_sent_button.clicked.connect(self.show_sent_emails)        
           
        # 设置布局
        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(send_button)
        hbox_buttons.addWidget(draft_button)
        hbox_buttons.addWidget(add_contact_button)
        hbox_buttons.addWidget(delete_contact_button)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox_buttons)  
        hbox_drafts = QHBoxLayout()
        hbox_drafts.addWidget(drafts_button)
        vbox.addLayout(hbox_drafts)  
        vbox.addWidget(view_sent_button)
        hbox_recipient = QHBoxLayout()
        hbox_recipient.addWidget(recipient_label)
        hbox_recipient.addWidget(self.recipient_entry)
        hbox_recipient.addWidget(select_contact_button)
        vbox.addLayout(hbox_recipient)

        vbox.addWidget(self.contact_listbox)

        hbox_subject = QHBoxLayout()
        hbox_subject.addWidget(subject_label)
        hbox_subject.addWidget(self.subject_entry)
        vbox.addLayout(hbox_subject)

        vbox.addWidget(message_label)
        vbox.addWidget(self.message_text)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(send_button)
        hbox_buttons.addWidget(draft_button)
        vbox.addLayout(hbox_buttons)

        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)
        
    def add_contact_dialog(self):
        dialog = AddContactDialog(self)
        if dialog.exec_():
            name = dialog.name_entry.text()
            email = dialog.email_entry.text()
            self.add_contact(name, email)

    def add_contact(self, name, email):
        self.address_book[name] = email
        self.contact_listbox.addItem(name)
        # 更新address_book.json文件
        with open(f"{self.from_address}_address_book.json", "w") as json_file:
            json.dump(self.address_book, json_file)

    def delete_contact(self):
        selected_item = self.contact_listbox.currentItem()
        if selected_item:
            name = selected_item.text()
            del self.address_book[name]
            self.contact_listbox.takeItem(self.contact_listbox.currentRow())
            # 更新address_book.json文件
            with open(f"{self.from_address}_address_book.json", "w") as json_file:
                json.dump(self.address_book, json_file)

    def select_contact(self):
        selected_contact = self.contact_listbox.currentItem().text()
        if selected_contact:
            self.recipient_entry.setText(self.address_book[selected_contact])

    def send_email(self):
        recipients = self.recipient_entry.text()
        recipients = recipients.split()
        subject = self.subject_entry.text()
        message_content = self.message_text.toPlainText()

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((mail_server, mail_port))

            recv = client_socket.recv(1024).decode()
            print(recv)
            if '220' != recv[:3]:
                print('220 reply not received from server.')

            heloCommand = 'HELO Alice\r\n'
            client_socket.send(heloCommand.encode())
            recv1 = client_socket.recv(1024).decode()
            print(recv1)
            if '250' != recv1[:3]:
                print('250 reply not received from server.')

            client_socket.sendall(f'AUTH LOGIN\r\n'.encode())
            recv2=client_socket.recv(1024).decode()
            print(recv2)
            if '334' != recv2[:3]:
                print('334 reply not received from server.')

            client_socket.sendall(f'{self.username}\r\n'.encode())
            recvName = client_socket.recv(1024).decode()
            print(recvName)
            if '334' != recvName[:3]:
                print('334 reply not received from server')
                
            client_socket.sendall(f'{self.password}\r\n'.encode())
            recvPass = client_socket.recv(1024).decode()
            print(recvPass)
            # 如果用户验证成功，服务器将返回状态码235
            if '235' != recvPass[:3]:
                print('235 reply not received from server')


            message = f'from:{self.from_address}\r\n'
            message += f'to:{", ".join(recipients)}\r\n'
            message += f'subject:{subject}\r\n'
            message += 'Content-Type:text/plain;charset=utf-8\r\n\r\n'
            message += message_content

            client_socket.sendall(f'MAIL FROM:<{self.from_address}>\r\n'.encode())
            recvFrom = client_socket.recv(1024).decode()
            print(recvFrom)
            if '250' != recvFrom[:3]:
                print('250 reply not received from server')

            for recipient in recipients:
                client_socket.sendall(f'RCPT TO:<{recipient}>\r\n'.encode())
                recvTo = client_socket.recv(1024).decode()  # 注意UDP使用sendto，recvfrom
                print(recvTo)
                if '250' != recvTo[:3]:
                    print('250 reply not received from server')
            client_socket.sendall(f'DATA\r\n'.encode())
            recvData = client_socket.recv(1024).decode()
            print(recvData)
            if '354' != recvData[:3]:
                print('354 reply not received from server')
            client_socket.sendall(message.encode())
            client_socket.sendall('\r\n.\r\n'.encode())
            recvEnd = client_socket.recv(1024).decode()
            print(recvEnd)
            if '250' != recvEnd[:3]:
                print('250 reply not received from server')
            client_socket.sendall('QUIT\r\n'.encode())
            client_socket.recv(1024)
            client_socket.close()

            self.load_sent_emails()
            self.save_to_sent_emails()
            
            QMessageBox.information(self, "邮件发送成功", "邮件发送成功！")
        except Exception as e:
            QMessageBox.critical(self, "邮件发送失败", f"邮件发送失败：{e}")

    def show_drafts(self):
        draft_dialog = DraftDialog(self.draft, self)
        draft_dialog.exec_()

    def load_drafts(self):
        # 读取现有的草稿内容并添加到地址簿
        try:
            with open(f"{self.from_address}_draft.json", "r") as json_file:
                self.draft = json.load(json_file)
        except FileNotFoundError:
            # 处理文件不存在的情况，创建一个空的 JSON 文件
            self.draft = {}
            with open(f"{self.from_address}_draft.json", "w") as json_file:
                json.dump(self.draft, json_file)
            print(f"{self.from_address}_draft.json 文件未找到，已创建一个空的 JSON 文件")
        except json.JSONDecodeError as e:
            # 处理JSON解码错误
            print(f"Error: JSON解码失败 - {e}")
            self.draft = {}
        except Exception as e:
            # 处理其他可能的异常
            print(f"Error: {e}")
            self.draft = {}

    def save_to_draft(self):
        timestamp = str(int(time.time()))  # 获取当前时间戳作为唯一标识符
        draft_content = {
            "recipient": self.recipient_entry.text(),
            "subject": self.subject_entry.text(),
            "message": self.message_text.toPlainText()
        }
        # 将草稿内容添加到地址簿的草稿字典中
        draft_key = f"draft_{timestamp}"
        self.draft[draft_key] = draft_content

        # 保存草稿到 JSON 文件
        with open(f"{self.from_address}_draft.json", "w") as json_file:
            json.dump(self.draft, json_file)

        QMessageBox.information(self, "保存成功", "邮件已保存到草稿箱！")

    def delete_specific_draft(self, draft_key):
        if draft_key in self.draft:
            del self.draft[draft_key]

            # 更新草稿箱 JSON 文件
            with open(f"{self.from_address}_draft.json", "w") as json_file:
                json.dump(self.draft, json_file)

            # 发射信号，通知视图刷新
            self.draftDeleted.emit()
            QMessageBox.information(self, "删除成功", "选定草稿已被删除！")
        else:
            QMessageBox.warning(self, "删除失败", "未找到选定的草稿。")

    def show_sent_emails(self):
        sent_emails_dialog = Sent_emailsDialog(self.sent_emails, self)
        sent_emails_dialog.exec_()

    def load_sent_emails(self):
        # 读取现有的已经发送
        try:
            with open(f"{self.from_address}_sent_emails.json", "r") as json_file:
                self.sent_emails = json.load(json_file)
        except FileNotFoundError:
            # 处理文件不存在的情况，创建一个空的 JSON 文件
            self.sent_emails = {}
            with open(f"{self.from_address}_sent_emails.json", "w") as json_file:
                json.dump(self.sent_emails, json_file)
            print(f"{self.from_address}_sent_emails.json 文件未找到，已创建一个空的 JSON 文件")
        except json.JSONDecodeError as e:
            # 处理JSON解码错误
            print(f"Error: JSON解码失败 - {e}")
            self.sent_emails = {}
        except Exception as e:
            # 处理其他可能的异常
            print(f"Error: {e}")
            self.sent_emails = {}

    def save_to_sent_emails(self):
        timestamp = str(int(time.time()))  # 获取当前时间戳作为唯一标识符
        sent_emails_content = {
            "recipient": self.recipient_entry.text(),
            "subject": self.subject_entry.text(),
            "message": self.message_text.toPlainText()
        }
        # 将草稿内容添加到地址簿的草稿字典中
        sent_emails_key = f"sent_emails_{timestamp}"
        self.sent_emails[sent_emails_key] = sent_emails_content

        # 保存草稿到 JSON 文件
        with open(f"{self.from_address}_sent_emails.json", "w") as json_file:
            json.dump(self.sent_emails, json_file)


    def delete_specific_sent_emails(self, sent_emails_key):
        if sent_emails_key in self.sent_emails:
            del self.sent_emails[sent_emails_key]

            # 更新草稿箱 JSON 文件
            with open(f"{self.from_address}_sent_emails.json", "w") as json_file:
                json.dump(self.sent_emails, json_file)

            # 发射信号，通知视图刷新
            self.sent_emailsDeleted.emit()
            QMessageBox.information(self, "删除成功", "选定草稿已被删除！")
        else:
            QMessageBox.warning(self, "删除失败", "未找到选定的草稿。")

class AddContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加联系人")

        self.name_label = QLabel("姓名:")
        self.name_entry = QLineEdit()

        self.email_label = QLabel("邮箱:")
        self.email_entry = QLineEdit()

        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_entry)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_entry)
        layout.addWidget(save_button)

        self.setLayout(layout)
        
class DraftDialog(QDialog):
    def __init__(self, draft, parent=None):
        super().__init__(parent)
        self.draft = draft
        self.setWindowTitle("草稿箱")

        self.draft_listbox = QListWidget()
        self.draft_listbox.addItems(draft.keys())

        view_button = QPushButton("查看草稿")
        view_button.clicked.connect(self.view_draft)

        delete_button = QPushButton("删除草稿")
        delete_button.clicked.connect(self.delete_draft)

        layout = QVBoxLayout()
        layout.addWidget(self.draft_listbox)
        layout.addWidget(view_button)
        layout.addWidget(delete_button)
        self.setLayout(layout)

        self.selected_draft_key = None
        parent.draftDeleted.connect(self.refresh_view)

    def view_draft(self):
        selected_item = self.draft_listbox.currentItem()
        if selected_item:
            self.selected_draft_key = selected_item.text()
            draft_content = self.draft[self.selected_draft_key]
            draft_viewer = DraftViewerDialog(draft_content, self)
            draft_viewer.exec_()

    def delete_draft(self):
        selected_item = self.draft_listbox.currentItem()
        if selected_item:
            selected_draft_key = selected_item.text()
            self.parent().delete_specific_draft(selected_draft_key)

    def refresh_view(self):
        # 清空列表框
        self.draft_listbox.clear()

        # 添加刷新后的草稿列表
        self.draft_listbox.addItems(self.draft.keys())    
                                        
class DraftViewerDialog(QDialog):
    def __init__(self, draft_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("草稿内容")

        self.draft_content = draft_content

        recipient_label = QLabel(f"收件人: {draft_content['recipient']}")
        subject_label = QLabel(f"主题: {draft_content['subject']}")
        message_label = QLabel(f"内容: {draft_content['message']}")

        import_button = QPushButton("导入草稿")
        import_button.clicked.connect(self.import_draft)

        layout = QVBoxLayout()
        layout.addWidget(recipient_label)
        layout.addWidget(subject_label)
        layout.addWidget(message_label)
        layout.addWidget(import_button)  # 添加导入按钮
        self.setLayout(layout)          

    def import_draft(self):
        # 发射信号，将草稿内容发送到主窗口，用于更新编辑区的内容
        self.parent().parent().recipient_entry.setText(self.draft_content['recipient'])
        self.parent().parent().subject_entry.setText(self.draft_content['subject'])
        self.parent().parent().message_text.setPlainText(self.draft_content['message'])
        self.accept()  # 关闭草稿查看对话框

class Sent_emailsDialog(QDialog):
    def __init__(self, sent_emails, parent=None):
        super().__init__(parent)
        self.sent_emails = sent_emails
        self.setWindowTitle("已发送")

        self.sent_emails_listbox = QListWidget()
        self.sent_emails_listbox.addItems(sent_emails.keys())

        view_button = QPushButton("查看已发送邮件")
        view_button.clicked.connect(self.view_sent_emails)

        delete_button = QPushButton("删除邮件发送记录")
        delete_button.clicked.connect(self.delete_sent_emails)

        layout = QVBoxLayout()
        layout.addWidget(self.sent_emails_listbox)
        layout.addWidget(view_button)
        layout.addWidget(delete_button)
        self.setLayout(layout)

        self.selected_sent_emails_key = None
        parent.sent_emailsDeleted.connect(self.refresh_view)

    def view_sent_emails(self):
        selected_item = self.sent_emails_listbox.currentItem()
        if selected_item:
            self.selected_sent_emails_key = selected_item.text()
            sent_emails_content = self.sent_emails[self.selected_sent_emails_key]
            sent_emails_viewer = Sent_emailsViewerDialog(sent_emails_content, self)
            sent_emails_viewer.exec_()

    def delete_sent_emails(self):
        selected_item = self.sent_emails_listbox.currentItem()
        if selected_item:
            selected_sent_emails_key = selected_item.text()
            self.parent().delete_specific_sent_emails(selected_sent_emails_key)

    def refresh_view(self):
        # 清空列表框
        self.sent_emails_listbox.clear()

        # 添加刷新后的草稿列表
        self.sent_emails_listbox.addItems(self.sent_emails.keys())    
                                        
class Sent_emailsViewerDialog(QDialog):
    def __init__(self, sent_emails_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("邮件内容")

        self.sent_emails_content = sent_emails_content

        recipient_label = QLabel(f"收件人: {sent_emails_content['recipient']}")
        subject_label = QLabel(f"主题: {sent_emails_content['subject']}")
        message_label = QLabel(f"内容: {sent_emails_content['message']}")


        layout = QVBoxLayout()
        layout.addWidget(recipient_label)
        layout.addWidget(subject_label)
        layout.addWidget(message_label)
        self.setLayout(layout)          
                                   
if __name__ == '__main__':
    def openAddressBook(address_book, address_book_filename):
        try:
            with open(address_book_filename, 'r', encoding='utf-8') as json_file:
                address_book = json.load(json_file)
        except FileNotFoundError:
            # 处理文件不存在的情况
            address_book = {}
            with open(address_book_filename, 'w', encoding='utf-8') as json_file:
                json.dump(address_book, json_file)
            print(f"Address book file '{address_book_filename}' not found. Created a new empty file.")
        except json.JSONDecodeError as e:
            # 处理JSON解码错误
            print(f"Error: JSON解码失败 - {e}")
            address_book = {}
        except Exception as e:
            # 处理其他可能的异常
            print(f"Error: {e}")
            address_book = {}
        return address_book

    app = QApplication(sys.argv)
    # 创建主窗口
    mainWindow = QMainWindow()

    # 创建StackedWidget作为主窗口的中央部件
    stackedWidget = QStackedWidget()
    loginWidget = LoginWidget(stackedWidget)
    emailClientWidget = EmailClientWidget()
    stackedWidget.addWidget(loginWidget)
    stackedWidget.addWidget(emailClientWidget)

    loginWidget.loginSuccessful.connect(emailClientWidget.updateCredentials)
    #loginWidget.loginSuccessful.connect(openAddressBook)

    mainWindow.setCentralWidget(stackedWidget)
    mainWindow.setGeometry(100, 100, 800, 600)
    mainWindow.setWindowTitle("邮件客户端")

    mainWindow.show()
    sys.exit(app.exec_())
