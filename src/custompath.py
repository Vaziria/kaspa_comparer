import os
from pydantic import BaseModel
from typing import List

class FilterLine(BaseModel):
    datas: List[str]
    
    def text(self):
        return "\n".join(self.datas)
    
    def setdata(self, data):
        val: str = data.value
        val = val.replace("\r", "")
        self.datas = val.split("\n")
        
    def check_contain(self, text: str) -> bool:
        for dat in self.datas:
            if dat == "":
                continue
            
            if text.find(dat) != -1:
                return True
            
        return False
    
    

class Path(BaseModel):
    current_key: str
    compare_key: str
    root: str
    path: str
    is_file: bool
    is_dir: bool
    filterLine: FilterLine
    
    def relpath(self):
        return os.path.join(self.root, self.path)

    def get_compare(self) -> List[str]:
        fpath = self.relpath()
        dpath = fpath.replace(self.current_key, self.compare_key)
        data = ["diff", "-u", self.relpath(), dpath]
        result = os.popen(" ".join(data)).readlines()
        
        hasil = []
        
        if len(result) == 0:
            return hasil
        
        foundiff = False
        
        for line in result[2:]:
            line = line.strip()
            line = line.replace("\n", "")
            
            if line == "":
                continue
            
            if self.filterLine.check_contain(line):
                continue
            
            if line == "-" or line == "+":
                continue
            
            hasil.append(line)
            if line.startswith('-') or line.startswith('+'):
                foundiff = True
        
        print(hasil)
        
        if not foundiff:
            return []
        
        return hasil

