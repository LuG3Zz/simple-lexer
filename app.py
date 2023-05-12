import sys
from textual import events
from rich.syntax import Syntax
from rich.traceback import Traceback
from textual.app import App, ComposeResult, Screen
from textual.containers import Horizontal, Vertical,Container, VerticalScroll
from textual.screen import Screen
from textual.reactive import var
from textual.widgets import (Button, DataTable, Header, Input, ListItem,
    ListView, Static,DirectoryTree,Footer)

sys.path.append(r"./src")
from DFA import *
from sheet import *


class BasicTable(Screen):
    BINDINGS = [
        ("tab", "toggle_class('#sidebar', '-active')",
         "查看更多功能")
    ]
    def compose(self) -> ComposeResult:
        yield Static(id="title")
        yield DataTable(id="key")
        yield Button("返回主界面", id="btn_exit")
        with Container(id="sidebar"):
            yield Input(placeholder="请输入字符", id="word_input")
            yield Button("增加", id="btn_add")
            yield Button("搜索", id="btn_search")
            yield Button("删除", id="btn_del")
            yield Static(id="label")
        yield Footer()

    def on_button_pressed(self, event):
        input = self.query_one("#word_input", Input)
        label = self.query_one("#label",Static)
        if event.button.id == "btn_exit":
            app.pop_screen()
        if event.button.id == "btn_add":
            if input.value in self.tb :
                label.update("添加失败，值已存在或为空")
                pass
            else:
                self.tb.append(input.value)
                label.update("添加成功")
                self.on_mount()
        if event.button.id == "btn_del":
            if input.value not in self.tb :
                label.update("值不存在")
                pass
            else:
                self.tb.remove(input.value)
                label.update("删除成功")
                self.on_mount()
        if event.button.id == "btn_search":
            if input.value not in self.tb :
                label.update("值不存在")
                pass
            else:
                label.update("该值存在")
            

class KeywordTable(BasicTable):

    def on_mount(self) -> None:
        title = self.query_one("#title",Static)
        title.update("关键字表")
        table = self.query_one("#key", DataTable)
        table.clear(True)
        self.tb = RESERVED_KEYWORDS
        table.add_column("id",width = 50)
        table.add_column("关键字",width = 50)
        rows = [(i, j) for i, j in enumerate(RESERVED_KEYWORDS)]
        for row in rows:
            table.add_row(*row)


class WordsTable(BasicTable):
    def on_mount(self) -> None:
        title = self.query_one("#title",Static)
        title.update("字母表")
        table = self.query_one("#key", DataTable)
        table.clear(True)
        self.tb = alphabet 
        table.add_column("id",width = 40)
        table.add_column("字符",width = 50)
        rows = [(i, j) for i, j in enumerate(self.tb)]
        for row in rows:
            table.add_row(*row)

class SingleTable(BasicTable):

    def on_mount(self) -> None:
        title = self.query_one("#title",Static)
        title.update("单分界符表")
        table = self.query_one("#key", DataTable)
        table.clear(True)
        self.tb = single_separator
        table.add_column("id",width = 40)
        table.add_column("字符",width = 50)
        rows = [(i, j) for i, j in enumerate(self.tb)]
        for row in rows:
            table.add_row(*row)

class Filebrowser(Screen):
    BINDINGS = [
        ("q", "quit", "退出"),
    ]
    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")


    show_tree = var(True)

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        with Container(id = "left"):
            yield Static("请选择要分析的文件", expand=True)
            yield DirectoryTree(path, id="tree-view")
        with VerticalScroll(id="code-view"):
            yield Static(id="code", expand=True)
        yield DataTable(id="tokens")
        with Container(id = "right"):
            yield Button("开始识别",id="btn_start")
            yield Button("查看自动机状态转移图", id="btn_show")
            yield Button("返回主界面", id="btn_exit")
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
        ) -> None:
        """Called when the user click a file in the directory tree."""
        self.path = "./"+str(event.path)
        event.stop()
        code_view = self.query_one("#code", Static)
        try:
            syntax = Syntax.from_path(
                event.path,
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme="github-dark",
            )
        except Exception:
            code_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"
        else:
            code_view.update(syntax)
            self.query_one("#code-view").scroll_home(animate=False)
            self.sub_title = event.path 

    def on_button_pressed(self, event):
        if event.button.id == "btn_start":
            self.dfa = DFA(
                states,
                alphabet,
                transition_function,
                start_state,
                accept_states,
            )
            tb = self.query_one("#tokens", DataTable)
            tb.clear(True)
            file = self.query_one("#tree-view", DirectoryTree)
            self.dfa.graph.clear()
            tokens = self.dfa.scanfile(self.path)
            tb.add_column("单词种类",width = 10)
            tb.add_column("单词内容",width = 10)
            tb.add_column("单词所在行",width = 15)
            for i in tokens:
                tb.add_row(*i)
        if event.button.id == "btn_show":
            self.dfa.view()
        if event.button.id == "btn_exit":
            app.pop_screen()


class DFA_display(Screen):
    def compose(self) -> ComposeResult:
        yield DataTable(id="tokens")
        yield Input(placeholder="请输入单词", id="input")
        yield Button("开始识别", id="btn_start")
        yield Button("查看自动机状态转移图", id="btn_display")
        yield Button("返回主界面", id="btn_exit")

    def on_mount(self):
        self.dfa = DFA(
            states,
            alphabet,
            transition_function,
            start_state,
            accept_states,
        )

    def on_button_pressed(self, event):
        if event.button.id == "btn_exit":
            app.pop_screen()
        if event.button.id == "btn_display":
            self.dfa.view()


        if event.button.id == "btn_start":
            self.on_mount()
            tb = self.query_one("#tokens", DataTable)
            tb.clear(True)
            input = self.query_one("#input", Input)
            self.dfa.graph.clear()
            tokens = self.dfa.scan(input.value)
            tb.add_column("单词种类",width = 30)
            tb.add_column("单词内容",width = 30)
            tb.add_column("单词所在行",width = 30)
            for i in tokens:
                tb.add_row(*i)


class MainApp(App):
    SCREENS = {
        "keyword": KeywordTable(),
        "dfa": DFA_display(id="display"),
        "words": WordsTable(),
        "single": SingleTable(),
        "file":Filebrowser(id="file")
    }
    BINDINGS = [
        ("q", "quit", "退出"),
    ]
    CSS_PATH = "MainApp.css"
    TITLE = "词法分析器"


    def compose(self) -> ComposeResult:
        yield Static(DASHBOARD, id="text")
        yield Header(name="词法分析器")
        with Container(id = "btn_group"):
            yield Button("关键字表", id="btn_keyword")
            yield Button("字符表", id="btn_word")
            yield Button("单字符分界符", id="btn_single")
            yield Button("词法分析DFA", id="btn_DFA")
            yield Button("词法分析过程展示", id="btn_display")
        yield Footer()

    def on_button_pressed(self, event):
        if event.button.id == "btn_keyword":
            self.push_screen("keyword")
        if event.button.id == "btn_display":
            self.push_screen("dfa")
        if event.button.id == "btn_word":
            self.push_screen("words")
        if event.button.id == "btn_single":
            self.push_screen("single")
        if event.button.id == "btn_DFA":
            self.push_screen("file")


if __name__ == "__main__":
    app = MainApp(watch_css=True)
    app.run()
