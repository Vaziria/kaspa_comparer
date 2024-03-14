import os
from typing import Generator, List, Callable
from nicegui import ui, Tailwind
from pydantic import BaseModel
from glob import glob
from src.custompath import *
from src.file_counter import *
from filterform import *

WORKSPACEDIR = "./workspaces"



class CheckDiff(BaseModel):
    source: str
    dest: str
    filter_line: FilterLine
    
    def walk(self):
        basepath = os.path.join(WORKSPACEDIR, self.source)
        for root, dirs, files in os.walk(basepath):
            for dirt in dirs:
                yield Path(root=root, path=dirt, is_dir=True, is_file=False, current_key=self.source, compare_key=self.dest, filterLine=self.filter_line)
            
            for file in files:
                yield Path(root=root, path=file, is_dir=False, is_file=True, current_key=self.source, compare_key=self.dest, filterLine=self.filter_line)


class WalkItem(BaseModel):
    current: str
    diff_content: List[str]
    
         
class WalkGenerator(BaseModel):
    genfunc: Callable[[], str]
    custom_walk_handler: list
    gen: Generator[Path, None, None]
    cursor: int
    datas: List[WalkItem]
    current: WalkItem

    def refresh(self):
        self.gen = self.genfunc()
        self.datas = []
        self.cursor = 0
        self.current = WalkItem(current="", diff_content=[])
    
    def before(self):
        if self.cursor == 0:
            return
        
        self.cursor -= 1
        self.current = self.datas[self.cursor]
        
    
    def next(self):
        
        if (len(self.datas) - 1) >= (self.cursor + 1):
            self.cursor += 1
            self.current = self.datas[self.cursor]

            return
        
            
        while True:
            
            pp = next(self.gen)
            
            
            if pp.is_dir == True:
                continue
            
            diff_content = pp.get_compare()
            
            if len(diff_content) == 0:
                continue
            
            for handler in self.custom_walk_handler:
                handler.process(pp)
            
            item = WalkItem(current=pp.relpath(), diff_content=diff_content)
            self.datas.append(item)
            
            self.current = item
            
            self.cursor +=1
            
            break
        
        

def get_list_folder():
    
    for item in glob(os.path.join(WORKSPACEDIR, "*")):
        dat = item.split("/")
        
        yield dat[-1]
    
    


def init_directory():
    os.makedirs(WORKSPACEDIR, 511, True)


def nextbtn(walk: WalkGenerator, fnamecontain, container, nextd: bool = True):
    if nextd:
        try:
            walk.next()
        except StopIteration:
            return
        
    else:
        walk.before()
        
    container.clear()
    fnamecontain.clear()
    
    with fnamecontain:
        ui.label("None").bind_text(walk.current, "current")
    
    with container.before:
        for l in walk.current.diff_content:
            if l.startswith('-'):
                ui.label(l).tailwind.text_color('red-600')
            elif l.startswith('+'):
                continue
            else:
                ui.label(l)
    
    with container.after:
        for l in walk.current.diff_content:
            if l.startswith('+'):
                ui.label(l).tailwind.text_color('green-600')
            elif l.startswith('-'):
                continue
            else:
                ui.label(l)
                
    
    

def main():
    
    init_directory()

    filterLine = FilterLine(datas=[
        "github.com/Pyrinpyi/pyipad",
        "github.com/kaspanet/kaspad",
    ])
    
    diff = CheckDiff(
        source="kaspad", 
        dest="pyipad",
        filter_line=filterLine
    )
    
    filecounter = FileCounter(filestats={}, change_count=0)
    walk = WalkGenerator(
        genfunc=diff.walk, 
        gen=diff.walk(), 
        cursor=0, 
        datas=[], 
        current=WalkItem(current="", diff_content=[]),
        filterLine=filterLine,
        custom_walk_handler=[
            filecounter,
        ]
    )
    
    
    
    
    container = None
    fnamecontain = None
    
    
    create_filter_form(filterLine)
    
    def refresh():
        walk.refresh()
        container.clear()
    
    with ui.row().classes():
        ui.button("refresh", on_click=refresh)
        ui.space()
        ui.select(list(get_list_folder())).bind_value(diff, "source")
        ui.space()
        ui.select(list(get_list_folder())).bind_value(diff, "dest")
       
    
    with ui.row().classes('w-full'):
        ui.button('prev', on_click=lambda: nextbtn(walk=walk, fnamecontain=fnamecontain, container=container, nextd=False))
        ui.space()
        ui.button('next', on_click=lambda: nextbtn(walk=walk, fnamecontain=fnamecontain, container=container))
    
    

    fnamecontain = ui.element('div')
    with fnamecontain:
        ui.label("None").bind_text(walk.current, "current")
    
    container = ui.splitter().classes('w-full')
    with container as splitter:
        
        with splitter.before:
            ui.label('source compare')
        with splitter.after:
            ui.label('destination compare')

    
    filecounter.mount()
    ui.run()    



if __name__ in {"__main__", "__mp_main__"}:
    main()