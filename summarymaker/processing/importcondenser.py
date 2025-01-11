"""
Processor to condense import statements in file content.
"""

import re
from collections import defaultdict
from .baseprocessor import BaseProcessor

class CondenseImportsProcessor(BaseProcessor):
    """
    Condenses import statements in the file content.
    """
    def process(self, content: str, filepath: str) -> str:
        if not filepath.endswith('.py'):
            return content
        
        import_pattern = re.compile(r'^(?:from\s+(\S+)\s+import\s+([\w\s,]+)|import\s+(\S+))', re.MULTILINE)
        imports = defaultdict(set)
        
        for match in import_pattern.finditer(content):
            if match.group(1) and match.group(2):
                module, items = match.group(1), match.group(2).split(',')
                for item in items:
                    imports[module].add(item.strip())
            elif match.group(3):
                module = match.group(3)
                imports[module]
        
        if not imports:
            return content
        
        condensed_imports = []
        for module, items in imports.items():
            if items:
                condensed_imports.append(f"{module}[{', '.join(sorted(items))}]")
            else:
                condensed_imports.append(module)
        
        if not condensed_imports:
            return content
        
        condensed_imports_str = f"truncated_imports:[{', '.join(condensed_imports)}]"
        
        # Remove original import statements
        content = re.sub(import_pattern, '', content)
        
        # Add condensed import statement at the top
        return condensed_imports_str + '\n' + content.strip()