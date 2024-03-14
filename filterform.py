from pydantic import BaseModel
from typing import List
from nicegui import ui, Tailwind
from src.custompath import FilterLine

        

def create_filter_form(data: FilterLine):
    
    
    with ui.expansion('Filter Diff').classes('w-full'):
        ui.textarea(
            value=data.text(), 
            label='Filter Text', 
            placeholder='start typing',
            on_change=data.setdata
        )\
            .tailwind\
            .width("1/3")
        # on_change=lambda e: result.set_text('you typed: ' + e.value)
