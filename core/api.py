from ninja import Router
from typing import List
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login
from .models import UserProfile, Match, GymRoutine, Attendance, FundraiserCampaign, TercerTiempo
from .schemas import (LoginSchema, ManagerSchema, ProfessorSchema, PlayerSchema, 
                      MatchSchema, RoutineSchema, AttendanceSchema, CampaignSchema, TercerTiempoSchema)

router = Router()

# ==================== LOGIN ====================
@router.post("/login")
def login_user(request, data: LoginSchema):
    user = authenticate(request, username=data.username, password=data.password)
    if user:
        django_login(request, user)
        role = "admin" if user.is_superuser else (user.profile.role if hasattr(user, 'profile') else "jugador")
        return {"success": True, "role": role}
    return {"success": False, "message": "Credenciales incorrectas"}

# ==================== UTILIDAD ====================
def save_user_profile(data, role):
    user, _ = User.objects.get_or_create(username=data.documento)
    user.first_name = data.nombre
    user.last_name = data.apellido
    user.email = data.correo
    
    # ACÁ ESTÁ LA MAGIA: Seteamos la contraseña igual al documento
    user.set_password(data.documento) 
    
    user.save()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.documento = data.documento
    profile.telefono = data.telefono
    profile.fecha_nacimiento = data.fecha_nacimiento
    return profile

# ==================== MANAGERS ====================
@router.get("/managers", response=List[ManagerSchema])
def get_managers(request):
    profiles = UserProfile.objects.filter(role='manager')
    return [{
        "id": str(p.id), 
        "nombre": p.user.first_name, 
        "apellido": p.user.last_name, 
        "documento": p.documento, 
        "fecha_nacimiento": str(p.fecha_nacimiento) if p.fecha_nacimiento else "", 
        "telefono": p.telefono, 
        "correo": p.user.email, 
        "categorias": p.categorias
    } for p in profiles]

@router.post("/managers")
def save_manager(request, data: ManagerSchema):
    profile = save_user_profile(data, 'manager')
    profile.categorias = data.categorias
    profile.save()
    return {"success": True}

# ==================== PROFESORES ====================
@router.get("/professors", response=List[ProfessorSchema])
def get_professors(request):
    profiles = UserProfile.objects.filter(role='profesor')
    return [{
        "id": str(p.id), 
        "nombre": p.user.first_name, 
        "apellido": p.user.last_name, 
        "documento": p.documento, 
        "fecha_nacimiento": str(p.fecha_nacimiento) if p.fecha_nacimiento else "", 
        "telefono": p.telefono, 
        "correo": p.user.email, 
        "categorias": p.categorias
    } for p in profiles]

@router.post("/professors")
def save_professor(request, data: ProfessorSchema):
    profile = save_user_profile(data, 'profesor')
    profile.categorias = data.categorias
    profile.save()
    return {"success": True}

# ==================== JUGADORES ====================
@router.get("/players", response=List[PlayerSchema])
def get_players(request):
    profiles = UserProfile.objects.filter(role='jugador')
    return [{
        "id": str(p.id), 
        "nombre": p.user.first_name, 
        "apellido": p.user.last_name, 
        "documento": p.documento, 
        "fecha_nacimiento": str(p.fecha_nacimiento) if p.fecha_nacimiento else "", 
        "telefono": p.telefono if p.telefono else "", 
        "correo": p.user.email, 
        
        # EL SALVACAÍDAS: Si es None, devolvemos un string vacío
        "categoria": p.categoria if p.categoria else "Sin categoría", 
        "posicion": p.posicion if p.posicion else "", 
        
        "fichaMedicaUrl": getattr(p, 'fichaMedicaUrl', getattr(p, 'ficha_medica_url', "")), 
        "fichaMedicaNombre": getattr(p, 'fichaMedicaNombre', getattr(p, 'ficha_medica_nombre', "")), 
        "fichaMedicaFecha": getattr(p, 'fichaMedicaFecha', getattr(p, 'ficha_medica_fecha', "")), 
        "justificaciones": getattr(p, 'justificaciones', []), 
        "fichajeInstalments": getattr(p, 'fichajeInstalments', getattr(p, 'fichaje_instalments', []))
    } for p in profiles]

@router.post("/players")
def save_player(request, data: PlayerSchema):
    profile = save_user_profile(data, 'jugador')
    profile.categoria = data.categoria
    profile.posicion = data.posicion
    
    # Guardado a prueba de errores
    if hasattr(profile, 'ficha_medica_url'):
        profile.ficha_medica_url = data.fichaMedicaUrl
        profile.ficha_medica_nombre = data.fichaMedicaNombre
        profile.ficha_medica_fecha = data.fichaMedicaFecha
    else:
        profile.fichaMedicaUrl = data.fichaMedicaUrl
        profile.fichaMedicaNombre = data.fichaMedicaNombre
        profile.fichaMedicaFecha = data.fichaMedicaFecha
        
    profile.justificaciones = data.justificaciones
    
    if hasattr(profile, 'fichaje_instalments'):
        profile.fichaje_instalments = data.fichajeInstalments
    else:
        profile.fichajeInstalments = data.fichajeInstalments
        
    profile.save()
    return {"success": True}
# ==================== PARTIDOS ====================
# ==================== PARTIDOS Y TERCER TIEMPO ====================
@router.get("/matches")
def get_matches(request):
    matches = Match.objects.all()
    lista = []
    for m in matches:
        datos = {k: v for k, v in m.__dict__.items() if k != '_state' and k != 'id'}
        datos["id"] = str(m.id)
        
        # Si el partido tiene un Tercer Tiempo asociado, le inyectamos los datos y la matemática
        if hasattr(m, 'tercer_tiempo'):
            datos["tercerTiempo"] = {
                "costo_comida": m.tercer_tiempo.costo_comida,
                "costo_bebida": m.tercer_tiempo.costo_bebida,
                "otros_gastos": m.tercer_tiempo.otros_gastos,
                "alias_transferencia": m.tercer_tiempo.alias_transferencia,
                "costo_total": m.tercer_tiempo.costo_total,
                "costo_por_jugador": m.tercer_tiempo.costo_por_jugador
            }
        lista.append(datos)
    return lista

@router.post("/tercer-tiempo")
def save_tercer_tiempo(request, data: TercerTiempoSchema):
    partido = Match.objects.get(id=data.partido_id)
    tt, created = TercerTiempo.objects.get_or_create(partido=partido)
    tt.costo_comida = data.costo_comida
    tt.costo_bebida = data.costo_bebida
    tt.otros_gastos = data.otros_gastos
    tt.alias_transferencia = data.alias_transferencia
    tt.save()
    return {"success": True}

@router.post("/matches")
def save_match(request, data: MatchSchema):
    Match.objects.update_or_create(id=data.id if data.id and data.id.isdigit() else None, defaults=data.dict(exclude={'id'}))
    return {"success": True}

# ==================== RUTINAS ====================
@router.get("/routines", response=List[RoutineSchema])
def get_routines(request):
    return [{"id": str(r.id), **{k: v for k, v in r.__dict__.items() if k != '_state' and k != 'id'}} for r in GymRoutine.objects.all()]

@router.post("/routines")
def save_routine(request, data: RoutineSchema):
    GymRoutine.objects.update_or_create(id=data.id if data.id and data.id.isdigit() else None, defaults=data.dict(exclude={'id'}))
    return {"success": True}

# ==================== ASISTENCIAS ====================
@router.get("/attendances", response=List[AttendanceSchema])
def get_attendances(request):
    return [{"id": str(a.id), **{k: v for k, v in a.__dict__.items() if k != '_state' and k != 'id'}} for a in Attendance.objects.all()]

@router.post("/attendances")
def save_attendance(request, data: AttendanceSchema):
    Attendance.objects.update_or_create(id=data.id if data.id and data.id.isdigit() else None, defaults=data.dict(exclude={'id'}))
    return {"success": True}

# ==================== CAMPAÑAS ====================
@router.get("/campaigns", response=List[CampaignSchema])
def get_campaigns(request):
    return [{"id": str(c.id), **{k: v for k, v in c.__dict__.items() if k != '_state' and k != 'id'}} for c in FundraiserCampaign.objects.all()]

@router.post("/campaigns")
def save_campaign(request, data: CampaignSchema):
    FundraiserCampaign.objects.update_or_create(id=data.id if data.id and data.id.isdigit() else None, defaults=data.dict(exclude={'id'}))
    return {"success": True}
