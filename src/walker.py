from nicegui import ui
from typing import Any, Callable, Dict, Generator, Optional

from pydantic import BaseModel

from .custompath import *

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
        for handler in self.custom_walk_handler:
            handler.reset()
    
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
            
            is_continue = False
            for handler in self.custom_walk_handler:
                if not handler.process(pp, diff_content):
                    is_continue = True
                    break
                
            if is_continue:
                continue
            
            item = WalkItem(current=pp.relpath(), diff_content=diff_content)
            self.datas.append(item)
            
            self.current = item
            
            self.cursor +=1
            
            break
        

class WalkerUI(BaseModel):
    walk: WalkGenerator
    
    pathloc: Optional[Any]
    comparer: Optional[Any]
    
    def count_all(self):
        while True:
            try:
                self.walk.next()
            except StopIteration:
                return
            
            self.render_pathloc()
            self.render_comparer()
        
    
    def refresh(self):
        self.walk.refresh()
        self.comparer.clear()
        self.pathloc.clear()
        
    def before(self):
        self.walk.before()
        
        self.render_pathloc()
        self.render_comparer()
    
    def next(self):
        try:
            self.walk.next()
        except StopIteration:
            return
        
        self.render_pathloc()
        self.render_comparer()
    
    
    def render_pathloc(self):
        if self.pathloc == None:
            return
        
        self.pathloc.clear()
        with self.pathloc:
            ui.label(self.walk.current.current)
            

    def render_comparer(self):
        if self.comparer == None:
            return
        
        self.comparer.clear()
        
        with self.comparer.before:
            for l in self.walk.current.diff_content:
                if l.startswith('-'):
                    ui.label(l).tailwind.text_color('red-600')
                elif l.startswith('+'):
                    continue
                else:
                    ui.label(l)
        
        with self.comparer.after:
            for l in self.walk.current.diff_content:
                if l.startswith('+'):
                    ui.label(l).tailwind.text_color('green-600')
                elif l.startswith('-'):
                    continue
                else:
                    ui.label(l)
            
        
    def mount_pathloc(self):
        self.pathloc = ui.element('div')
        with self.pathloc:
            ui.label(self.walk.current.current)
            
    def mount_comparer(self):
        self.comparer = ui.splitter().classes('w-full')
        with self.comparer as splitter:
        
            with splitter.before:
                ui.label('source compare')
            with splitter.after:
                ui.label('destination compare')