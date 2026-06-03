# core/models.py
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
    fecha_nacimiento = models.DateField(blank=True, null=True)
    
   # --- LA QUE ES EN PLURAL (Para Manager/Profesor) ---
    categorias = models.JSONField(default=list, blank=True)
    
    # --- LA QUE ES EN SINGULAR (Para Jugadores) -> ¡ESTA ES LA QUE TE FALTA! ---
    categoria = models.CharField(max_length=50, blank=True, null=True)
    # --- Datos de Jugador ---
    posicion = models.CharField(max_length=50, blank=True, null=True)
    peso = models.FloatField(default=0.0)
    altura = models.FloatField(default=0.0)
    activo = models.BooleanField(default=True)
    ficha_medica_url = models.URLField(blank=True, null=True)
    ficha_medica_fecha = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.last_name}, {self.user.first_name} - {self.role}"

class Match(models.Model):
    fecha = models.DateTimeField()
    rival = models.CharField(max_length=100)
    lugar = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    estado = models.CharField(max_length=50, default='Programado')
    resultado_club = models.IntegerField(default=0)
    resultado_rival = models.IntegerField(default=0)
    titulares = models.JSONField(default=list, blank=True) # Lista de IDs
    suplentes = models.JSONField(default=list, blank=True) # Lista de IDs
    estadisticas = models.JSONField(default=dict, blank=True)
    hora = models.CharField(max_length=20, blank=True, null=True)
    resultadoClub = models.IntegerField(blank=True, null=True)
    resultadoRival = models.IntegerField(blank=True, null=True)

class GymRoutine(models.Model):
    titulo = models.CharField(max_length=200)
    fecha_asignacion = models.DateField()
    ejercicios = models.JSONField(default=list) # [{nombre, series, repeticiones, notas}]

class Attendance(models.Model):
    fecha = models.DateField()
    categoria = models.CharField(max_length=50)
    jugadores_presentes = models.JSONField(default=list) # Lista de IDs de jugadores

class FundraiserCampaign(models.Model):
    titulo = models.CharField(max_length=200)
    objetivo = models.DecimalField(max_digits=10, decimal_places=2)
    recaudado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_limite = models.DateField()

class TercerTiempo(models.Model):
    partido = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='tercer_tiempo')
    costo_comida = models.FloatField(default=0)
    costo_bebida = models.FloatField(default=0)
    otros_gastos = models.FloatField(default=0)
    alias_transferencia = models.CharField(max_length=150)

    @property
    def costo_total(self):
        return self.costo_comida + self.costo_bebida + self.otros_gastos

    @property
    def costo_por_jugador(self):
        # Cuenta cuántos jugadores hay en las listas JSON de titulares y suplentes
        titulares = self.partido.titulares if isinstance(self.partido.titulares, list) else []
        suplentes = self.partido.suplentes if isinstance(self.partido.suplentes, list) else []
        
        cantidad_jugadores = len(titulares) + len(suplentes)
        
        if cantidad_jugadores > 0:
            return self.costo_total / cantidad_jugadores
        return 0

    def __str__(self):
        return f"Tercer Tiempo - {self.partido.rival}"