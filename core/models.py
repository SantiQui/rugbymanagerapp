from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('MANAGER', 'Manager'),
        ('COACH', 'Profesor'),
        ('PLAYER', 'Jugador'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    documento = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=15, choices=ROLES)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    fecha_nacimiento = models.CharField(max_length=50, blank=True, null=True) # Pasado a CharField para evitar fallos de formato
    
    # --- Para Manager/Profesor ---
    categorias = models.JSONField(default=list, blank=True, null=True)
    
    # --- Para Jugadores ---
    categoria = models.CharField(max_length=50, blank=True, null=True)
    posicion = models.CharField(max_length=50, blank=True, null=True)
    peso = models.FloatField(default=0.0)
    altura = models.FloatField(default=0.0)
    activo = models.BooleanField(default=True)
    
    # --- Variables exactas como las manda React ---
    fichaMedicaUrl = models.CharField(max_length=255, blank=True, null=True)
    fichaMedicaNombre = models.CharField(max_length=255, blank=True, null=True)
    fichaMedicaFecha = models.CharField(max_length=50, blank=True, null=True)
    justificaciones = models.JSONField(default=list, blank=True, null=True)
    fichajeInstalments = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f"{self.user.last_name}, {self.user.first_name} - {self.role}"


class Match(models.Model):
    fecha = models.CharField(max_length=50, blank=True, null=True)
    hora = models.CharField(max_length=20, blank=True, null=True)
    rival = models.CharField(max_length=100, blank=True, null=True)
    lugar = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=50, default='Programado')
    resultadoClub = models.IntegerField(blank=True, null=True)
    resultadoRival = models.IntegerField(blank=True, null=True)
    titulares = models.JSONField(default=list, blank=True, null=True)
    suplentes = models.JSONField(default=list, blank=True, null=True)
    estadisticas = models.JSONField(default=dict, blank=True, null=True)


class GymRoutine(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    ejercicios = models.JSONField(default=list, blank=True, null=True)
    profesorId = models.CharField(max_length=50, blank=True, null=True)
    profesorNombre = models.CharField(max_length=150, blank=True, null=True)
    jugadorId = models.CharField(max_length=50, blank=True, null=True)
    posicion = models.CharField(max_length=50, blank=True, null=True)
    fechaAsignacion = models.CharField(max_length=50, blank=True, null=True)


class Attendance(models.Model):
    fecha = models.CharField(max_length=50, blank=True, null=True)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    tipo = models.CharField(max_length=100, blank=True, null=True)
    asistentes = models.JSONField(default=list, blank=True, null=True)
    justificados = models.JSONField(default=list, blank=True, null=True)


class FundraiserCampaign(models.Model):
    titulo = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fechaDesde = models.CharField(max_length=50, blank=True, null=True)
    fechaHasta = models.CharField(max_length=50, blank=True, null=True)
    fotoFlyer = models.CharField(max_length=50, blank=True, null=True)
    cantidadPorJugador = models.IntegerField(default=10)
    ventasRegistradas = models.JSONField(default=dict, blank=True, null=True)


class TercerTiempo(models.Model):
    partido = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='tercer_tiempo')
    costo_comida = models.FloatField(default=0)
    costo_bebida = models.FloatField(default=0)
    otros_gastos = models.FloatField(default=0)
    alias_transferencia = models.CharField(max_length=150, blank=True, null=True)

    @property
    def costo_total(self):
        return self.costo_comida + self.costo_bebida + self.otros_gastos

    @property
    def costo_por_jugador(self):
        titulares = self.partido.titulares if isinstance(self.partido.titulares, list) else []
        suplentes = self.partido.suplentes if isinstance(self.partido.suplentes, list) else []
        cantidad_jugadores = len(titulares) + len(suplentes)
        if cantidad_jugadores > 0:
            return self.costo_total / cantidad_jugadores
        return 0

    def __str__(self):
        return f"Tercer Tiempo - {self.partido.rival}"