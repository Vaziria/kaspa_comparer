import os
from pydantic import BaseModel
from nicegui import ui, Tailwind
from typing import Dict, Optional, List

from src.custompath import Path

from .custompath import *

class WalkHandler:
    def process(self, path: Path, diff: List[str]) -> bool:
        return True
    
    def reset(self):
        pass

class FileCounter(WalkHandler):
    filestats: Dict[str, int]
    change_count: int
    
    container: Optional[ui.element]
    
    def __init__(self, 
        filestats: Dict[str, int],
        change_count: int,
        container: Optional[ui.element] = None
    ) -> None:
        
        self.filestats = filestats
        self.change_count = change_count
        self.container = container
    
    container: Optional[ui.element]
    
    def process(self, path: Path, diff: List[str]):
        if not path.is_file:
            return
        
        fname, ext = os.path.splitext(path.path)
        count = self.filestats.get(ext, 0)
        self.filestats[ext] = count + 1
        
        self.change_count += 0
        
        self.render()
        
        return True
        
    def reset(self):
        self.change_count = 0
        self.filestats = {}
        self.render()
        
    
    def render(self):
        if not self.container:
            return
        
        self.container.clear()
        with self.container:
            columns = [
                {'name': 'extension', 'label': 'Extension', 'field': 'ext', 'required': True, 'align': 'left'},
                {'name': 'count', 'label': 'Count', 'field': 'count', 'sortable': True},
            ]
            
            rows = []
            
            for key, count in self.filestats.items():
                rows.append({
                    "ext": key,
                    "count": count
                })
            ui.table(columns=columns, rows=rows, row_key='name')
    
    
    def mount(self):
        
        self.container = ui.element("div")
        with self.container:
            ui.label("file stat")
            
            
    
class CommentFilter(WalkHandler):
    
    def process(self, path: Path, diff: List[str]) -> bool:
        c = 0
        
        for line in diff:
            if not (line.startswith("+") or line.startswith("-")):
                continue
            
            line = line.lstrip("-")
            line = line.lstrip("+")
            line = line.lstrip("\t")
            line = line.lstrip(" ")
            
            if not line.startswith("//"):
                c += 1
            
        return c > 0
        
        



