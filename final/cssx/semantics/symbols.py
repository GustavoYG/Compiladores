# symbols.py
# Tabla de símbolos para variables y referencias

from typing import Dict, Any, Optional, List, Set
from cssx.ast.nodes import Loc, VariableDecl, VariableRef
from dataclasses import dataclass


@dataclass(slots=True)
class SymbolInfo:
    """Información sobre un símbolo (variable)"""
    name: str
    value: Any
    defined_at: Loc
    used_at: List[Loc]
    is_used: bool = False
    
    def mark_used(self, loc: Loc):
        """Marca el símbolo como usado en una ubicación"""
        self.is_used = True
        self.used_at.append(loc)


class SymbolTable:
    """Tabla de símbolos para el análisis semántico"""
    
    def __init__(self):
        self.symbols: Dict[str, SymbolInfo] = {}
        self.scopes: List[Dict[str, SymbolInfo]] = [{}]  # Stack de scopes
        
    def enter_scope(self):
        """Entra a un nuevo scope"""
        self.scopes.append({})
    
    def exit_scope(self):
        """Sale del scope actual"""
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def define_symbol(self, name: str, value: Any, loc: Loc) -> bool:
        """
        Define un símbolo en el scope actual
        Retorna False si ya existe en el mismo scope
        """
        current_scope = self.scopes[-1]
        
        if name in current_scope:
            return False  # Ya existe en este scope
            
        symbol_info = SymbolInfo(
            name=name,
            value=value,
            defined_at=loc,
            used_at=[]
        )
        
        current_scope[name] = symbol_info
        self.symbols[name] = symbol_info  # También en la tabla global para fácil acceso
        
        return True
    
    def lookup_symbol(self, name: str) -> Optional[SymbolInfo]:
        """Busca un símbolo en todos los scopes (desde el más reciente)"""
        # Buscar desde el scope más reciente hacia el más antiguo
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def use_symbol(self, name: str, loc: Loc) -> Optional[SymbolInfo]:
        """
        Marca un símbolo como usado y retorna su información
        Retorna None si no se encuentra
        """
        symbol = self.lookup_symbol(name)
        if symbol:
            symbol.mark_used(loc)
            return symbol
        return None
    
    def get_undefined_symbols(self) -> List[tuple[str, Loc]]:
        """Retorna lista de símbolos referenciados pero no definidos"""
        # Esta función será llamada externamente cuando se detecten referencias sin definición
        undefined = []
        return undefined
    
    def get_unused_symbols(self) -> List[SymbolInfo]:
        """Retorna lista de símbolos definidos pero no usados"""
        unused = []
        for symbol in self.symbols.values():
            if not symbol.is_used:
                unused.append(symbol)
        return unused
    
    def get_all_symbols(self) -> Dict[str, SymbolInfo]:
        """Retorna todos los símbolos definidos"""
        return self.symbols.copy()
    
    def is_defined(self, name: str) -> bool:
        """Verifica si un símbolo está definido"""
        return self.lookup_symbol(name) is not None
    
    def get_symbol_value(self, name: str) -> Any:
        """Obtiene el valor de un símbolo"""
        symbol = self.lookup_symbol(name)
        return symbol.value if symbol else None


class ReferenceTracker:
    """Rastrea referencias a símbolos para detectar problemas"""
    
    def __init__(self):
        self.references: List[tuple[str, Loc]] = []  # (nombre, ubicación)
        self.definitions: List[tuple[str, Loc]] = []  # (nombre, ubicación)
        
    def add_reference(self, name: str, loc: Loc):
        """Agrega una referencia a un símbolo"""
        self.references.append((name, loc))
    
    def add_definition(self, name: str, loc: Loc):
        """Agrega una definición de símbolo"""
        self.definitions.append((name, loc))
    
    def get_undefined_references(self) -> List[tuple[str, Loc]]:
        """Retorna referencias que no tienen definición correspondiente"""
        defined_names = {name for name, _ in self.definitions}
        undefined = []
        
        for name, loc in self.references:
            if name not in defined_names:
                undefined.append((name, loc))
                
        return undefined
    
    def get_unused_definitions(self) -> List[tuple[str, Loc]]:
        """Retorna definiciones que no tienen referencias"""
        referenced_names = {name for name, _ in self.references}
        unused = []
        
        for name, loc in self.definitions:
            if name not in referenced_names:
                unused.append((name, loc))
                
        return unused
    
    def detect_circular_references(self) -> List[List[tuple[str, Loc]]]:
        """Detecta referencias circulares (implementación básica)"""
        # Para una implementación completa, se necesitaría construir un grafo
        # y detectar ciclos. Por ahora, retornamos lista vacía.
        return []


class ScopeAnalyzer:
    """Analizador de scopes para detectar problemas de alcance"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.reference_tracker = ReferenceTracker()
        
    def analyze_variable_declaration(self, var_decl: VariableDecl):
        """Analiza una declaración de variable"""
        name = var_decl.name
        loc = var_decl.loc
        
        # Verificar si ya está definida en el scope actual
        if not self.symbol_table.define_symbol(name, var_decl.value, loc):
            # Ya existe, esto podría ser un problema
            pass
            
        self.reference_tracker.add_definition(name, loc)
    
    def analyze_variable_reference(self, var_ref: VariableRef, loc: Loc):
        """Analiza una referencia a variable"""
        name = var_ref.name
        
        # Marcar como usado si existe
        symbol = self.symbol_table.use_symbol(name, loc)
        
        # Rastrear la referencia
        self.reference_tracker.add_reference(name, loc)
        
        return symbol is not None
    
    def get_analysis_results(self) -> tuple[List[tuple[str, Loc]], List[tuple[str, Loc]]]:
        """
        Retorna los resultados del análisis
        Returns: (undefined_references, unused_definitions)
        """
        undefined = self.reference_tracker.get_undefined_references()
        unused = self.reference_tracker.get_unused_definitions()
        
        return undefined, unused
    
    def enter_new_scope(self):
        """Entra a un nuevo scope (por ejemplo, dentro de un ruleset)"""
        self.symbol_table.enter_scope()
    
    def exit_current_scope(self):
        """Sale del scope actual"""
        self.symbol_table.exit_scope()
