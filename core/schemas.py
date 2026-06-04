from ninja import Schema
from typing import List, Optional, Dict, Any

class LoginSchema(Schema):
    username: str
    password: str

# Esquemas comunes para Personas
class PersonBaseSchema(Schema):
    id: Optional[str] = None
    nombre: str
    apellido: str
    documento: str
    fecha_nacimiento: str
    telefono: str
    correo: str

class ManagerSchema(PersonBaseSchema):
    categorias: List[str]

class ProfessorSchema(PersonBaseSchema):
    categorias: List[str]

class FichajeInstallmentSchema(Schema):
    id: str
    numeroCuota: int
    monto: float
    pagado: bool
    fechaPago: Optional[str] = None
    medioPago: Optional[str] = None

class PlayerSchema(PersonBaseSchema):
    categoria: str
    posicion: Optional[str] = None
    fichaMedicaUrl: Optional[str] = None
    fichaMedicaNombre: Optional[str] = None
    fichaMedicaFecha: Optional[str] = None
    justificaciones: Optional[list] = []
    fichajeInstalments: Optional[List[FichajeInstallmentSchema]] = []

# Esquemas de Entidades Operativas
class MatchSchema(Schema):
    id: Optional[str] = None
    fecha: str
    hora: str
    rival: str
    categoria: str
    lugar: str
    estado: str
    resultadoClub: Optional[int] = None
    resultadoRival: Optional[int] = None
    titulares: Optional[List[str]] = []
    suplentes: Optional[List[str]] = []
    estadisticas: Optional[Dict[str, Any]] = {}

class RoutineSchema(Schema):
    id: Optional[str] = None
    titulo: str
    descripcion: Optional[str] = ""
    ejercicios: Optional[List[Dict[str, str]]] = []
    profesorId: Optional[str] = None
    profesorNombre: Optional[str] = None
    jugadorId: Optional[str] = None
    posicion: Optional[str] = None
    fechaAsignacion: str

class AttendanceSchema(Schema):
    id: Optional[str] = None
    fecha: str
    tipo: Optional[str] = None
    categoria: str
    asistentes: Optional[List[str]] = []
    justificados: Optional[List[str]] = []

class CampaignSchema(Schema):
    id: Optional[str] = None
    titulo: str
    descripcion: str
    fechaDesde: str
    fechaHasta: str
    fotoFlyer: Optional[str] = None
    cantidadPorJugador: int
    ventasRegistradas: Optional[Dict[str, int]] = {}

class TercerTiempoSchema(Schema):
    partido_id: str
    costo_comida: float
    costo_bebida: float
    otros_gastos: float
    alias_transferencia: str