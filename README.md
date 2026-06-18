# 📋 Seguimiento de Personal Consorcio EBD - Control 21x10

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![SQLite](https://img.shields.io/badge/SQLite-3-green?logo=sqlite)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

Sistema de escritorio desarrollado en Python para la gestión, rotación y control de asistencia de personal en operaciones de campo bajo el esquema **21x10** (21 días de trabajo en campo / 10 días de descanso).

---

## 🎯 Descripción del Problema

En operaciones de campo (minería, construcción, proyectos remotos), el personal suele trabajar bajo ciclos de rotación estrictos, como el **21x10**. Gestionar esta rotación manualmente mediante hojas de cálculo o registros en papel presenta varios desafíos críticos:

1. **Cálculo manual propenso a errores:** Determinar en qué día del ciclo se encuentra cada trabajador, si está en campo o descansando, y cuántos días le faltan para su relevo requiere cálculos constantes.
2. **Falta de alertas tempranas:** Los supervisores no reciben notificaciones automáticas cuando un trabajador está próximo a cumplir sus 21 días, lo que puede generar retrasos en los relevos y fatiga laboral.
3. **Control de cobertura deficiente:** Es difícil saber en tiempo real si se está cumpliendo con el número mínimo de personal requerido por puesto (ej. 2 Operadores, 1 Supervisor) en el lote.
4. **Histórico desorganizado:** Registrar ingresos y salidas del lote en formatos no estructurados impide generar reportes fiables para Recursos Humanos y operaciones.

---

## 💡 Solución Propuesta

Esta aplicación digitaliza y automatiza el control de rotación de personal. Permite registrar el ingreso y salida de cada trabajador al lote, calcula automáticamente su estado actual (en campo o descansando), muestra alertas visuales cuando el ciclo está por terminar y genera reportes instantáneos de cobertura operativa.  Por eso desarrollé un sistema automatizado en Python que calcula automáticamente el estado de cada trabajador, genera alertas 7 días antes del relevo y reporta cobertura en tiempo real.


### 📸 Capturas de Pantalla

**Vista Principal - Tabla de Control de Personal**
![Vista Principal](https://image.qwenlm.ai/public_source/bc9098c5-bc63-4516-a24a-89cba027295d/15b5532b3-39ed-4628-b35f-9ccbe53cd12d.png)
*Interfaz oscura con tabla de empleados, estados automáticos y alertas visuales de días restantes.*

**Reporte de Cobertura en Campo**
![Reporte Cobertura](https://image.qwenlm.ai/public_source/bc9098c5-bc63-4516-a24a-89cba027295d/104e71255-223d-45e7-b584-e89ab485da75.png)
*Modal de reporte que muestra el personal actual vs. el requerido por puesto y el estado general de la operación.*

## 📸 Captura del Sistema

![Vista de la aplicación](Screenshot_20260617-183418_Pydroid%203.png)
---

## ✨ Características Principales

- 🔄 **Cálculo Automático de Ciclos:** Algoritmo preciso que calcula el día exacto del ciclo 21x10 basándose en la fecha de inicio o el último ingreso registrado.
- ⚠️ **Sistema de Alertas:** Resaltado automático en color ámbar cuando a un trabajador le faltan 7 días o menos para terminar su turno en campo.
- ✅ **Registro de Ingreso/Salida:** Botones dedicados para registrar el movimiento del personal al lote, reiniciando el ciclo de 21 días automáticamente.
- 📊 **Reporte de Cobertura en Tiempo Real:** Visualización instantánea de si se cumple con el personal mínimo requerido por puesto (Operadores, Supervisores, etc.).
- 📂 **Importación Masiva vía CSV:** Carga rápida de múltiples empleados desde un archivo CSV, con validación automática de duplicados.
- 🌙 **Interfaz Moderna (Dark Mode):** UI limpia, profesional y con botones deslizables para optimizar el espacio en pantalla.
- 🛡️ **Prevención de Errores:** Validaciones de formularios, control de ventanas duplicadas y consultas SQL parametrizadas para evitar inyecciones.

---

## 🚀 Instalación y Uso

### Requisitos Previos
- Python 3.8 o superior
- No requiere instalación de librerías externas (usa librerías estándar: `tkinter`, `sqlite3`, `csv`, `datetime`).

### Pasos para ejecutar

1. Clona o descarga el repositorio:

   git clone https://github.com/javi1942/sisyrma_lite.git
   cd sisyrma_lite
