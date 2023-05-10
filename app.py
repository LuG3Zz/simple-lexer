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


class KeywordTable(Screen):

    def compose(self) -> ComposeResult:
        yield DataTable(id="key")
        yield Button("返回主界面", id="btn_exit")

    def on_mount(self) -> None:
        table = self.query_one("#key", DataTable)
        table.add_column("id",width = 40)
        table.add_column("关键字",width = 50)
        rows = [(i, j) for i, j in enumerate(RESERVED_KEYWORDS)]
        for row in rows:
            table.add_row(*row)

    def on_button_pressed(self, event):
        if event.button.id == "btn_exit":
            app.pop_screen()


class WordsTable(Screen):

    def compose(self) -> ComposeResult:
        yield DataTable(id="wordstable")
        yield Button("返回主界面", id="btn_exit")

    def on_mount(self) -> None:
        table = self.query_one("#wordstable", DataTable)
        table.add_column("id",width = 40)
        table.add_column("字符",width = 50)
        rows = [(i, j) for i, j in enumerate(alphabet)]
        for row in rows:
            table.add_row(*row)

    def on_button_pressed(self, event):
        if event.button.id == "btn_exit":
            app.pop_screen()


class SingleTable(Screen):

    def compose(self) -> ComposeResult:
        yield DataTable(id="singletable")
        yield Button("返回主界面", id="btn_exit")

    def on_mount(self) -> None:
        table = self.query_one("#singletable", DataTable)
        table.add_column("id",width = 40)
        table.add_column("字符",width = 50)
        rows = [(i, j) for i, j in enumerate(single_separator)]
        for row in rows:
            table.add_row(*row)

    def on_button_pressed(self, event):
        if event.button.id == "btn_exit":
            app.pop_screen()


class Filebrowser(Screen):


    BINDINGS = [
        ("q", "quit", "Quit"),
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
        self.dfa = DFA(
                states,
                alphabet,
                transition_function,
                start_state,
                accept_states,
            )

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
