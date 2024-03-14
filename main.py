import os
from typing import Generator, List, Callable
from nicegui import ui, Tailwind
from pydantic import BaseModel
from glob import glob
from src.custompath import *
from src.file_counter import *
from src.walker import *
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



        
        

def get_list_folder():
    
    for item in glob(os.path.join(WORKSPACEDIR, "*")):
        dat = item.split("/")
        
        yield dat[-1]
    
    


def init_directory():
    os.makedirs(WORKSPACEDIR, 511, True)
  

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
            CommentFilter(),
        ]
    )
    walker_ui = WalkerUI(walk=walk, comparer=None, pathloc=None)
    
    
    
    create_filter_form(filterLine)
    
    
    
    with ui.row().classes():
        ui.button("refresh", on_click=walker_ui.refresh)
        ui.space()
        ui.button("count all", on_click=walker_ui.count_all)
        ui.space()
        ui.select(list(get_list_folder())).bind_value(diff, "source")
        ui.space()
        ui.select(list(get_list_folder())).bind_value(diff, "dest")
       
    
    with ui.row().classes('w-full'):
        ui.button('prev', on_click=walker_ui.before)
        ui.space()
        walker_ui.mount_pathloc()
        ui.space()
        ui.button('next', on_click=walker_ui.next)
    
    

    
    walker_ui.mount_comparer()
    

    
    filecounter.mount()
    ui.run()    



if __name__ in {"__main__", "__mp_main__"}:
    main()