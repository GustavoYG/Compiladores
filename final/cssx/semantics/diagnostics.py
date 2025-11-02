# semantica_diagnosticos.py
# Clases para diagnósticos del análisis semántico

from dataclasses import dataclass
from typing import Optional, List, Tuple


@dataclass(slots=True)
class Diagnostic:
    """Diagnóstico emitido por el análisis semántico"""
    code: str            # p.ej., 'E030', 'W100'
    severity: str        # 'ERROR' | 'WARNING'
    message: str         # explicación clara del problema
    file: str
    line: int
    col: int
    doc_url: Optional[str] = None
    related: Optional[List[Tuple[str, int, int, str]]] = None  # (file,line,col,nota) opcional


def format_diagnostic(d: Diagnostic) -> str:
    """
    Formatea un diagnóstico para mostrar en consola
    Formato: "file:line:col: CODE: message (doc: URL)" si doc_url existe
    """
    base = f"{d.file}:{d.line}:{d.col}: {d.code}: {d.message}"
    
    if d.doc_url:
        base += f" (doc: {d.doc_url})"
    
    return base


class DiagnosticCollector:
    """Recolector de diagnósticos durante el análisis"""
    
    def __init__(self):
        self.diagnostics: List[Diagnostic] = []
    
    def error(self, code: str, message: str, file: str, line: int, col: int, 
              doc_url: Optional[str] = None, related: Optional[List[Tuple[str, int, int, str]]] = None) -> None:
        """Agrega un error al recolector"""
        self.diagnostics.append(Diagnostic(
            code=code,
            severity="ERROR",
            message=message,
            file=file,
            line=line,
            col=col,
            doc_url=doc_url,
            related=related
        ))
    
    def warning(self, code: str, message: str, file: str, line: int, col: int,
                doc_url: Optional[str] = None, related: Optional[List[Tuple[str, int, int, str]]] = None) -> None:
        """Agrega una advertencia al recolector"""
        self.diagnostics.append(Diagnostic(
            code=code,
            severity="WARNING",
            message=message,
            file=file,
            line=line,
            col=col,
            doc_url=doc_url,
            related=related
        ))
    
    def has_errors(self) -> bool:
        """Retorna True si hay al menos un error"""
        return any(d.severity == "ERROR" for d in self.diagnostics)
    
    def has_warnings(self) -> bool:
        """Retorna True si hay al menos una advertencia"""
        return any(d.severity == "WARNING" for d in self.diagnostics)
    
    def get_diagnostics(self) -> List[Diagnostic]:
        """Retorna la lista de diagnósticos ordenados por ubicación"""
        return sorted(self.diagnostics, key=lambda d: (d.file, d.line, d.col))


# Códigos de error y advertencia predefinidos
class ErrorCodes:
    """Códigos de error semántico"""
    UNDEFINED_VARIABLE = "E001"
    INVALID_PROPERTY = "E002"
    INVALID_VALUE = "E003"
    CIRCULAR_REFERENCE = "E004"
    DUPLICATE_PROPERTY = "E005"
    INVALID_VARIABLE = "E006"
    
    # Códigos para plantillas CSSX
    TEMPLATE_DUPLICATE = "E040"
    TEMPLATE_RECURSION = "E041"
    TEMPLATE_INVOCATION_ERROR = "E042"


class WarningCodes:
    """Códigos de advertencia semántica"""
    UNUSED_VARIABLE = "W001"
    DEPRECATED_PROPERTY = "W002"
    VENDOR_PREFIX_MISSING = "W003"
    UNKNOWN_PROPERTY = "W004"
    SUSPICIOUS_VALUE = "W005"
