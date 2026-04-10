class CaseRelation:
    def __init__(self):
        self.variables = {}
    
    def set_variable(self, key, value):
        self.variables[key] = value
    
    def get_variable(self, key, default=None):
        return self.variables.get(key, default)
    
    def update_variables(self, variables):
        self.variables.update(variables)
    
    def clear_variables(self):
        self.variables.clear()
    
    def get_all_variables(self):
        return self.variables.copy()

case_relation = CaseRelation()
