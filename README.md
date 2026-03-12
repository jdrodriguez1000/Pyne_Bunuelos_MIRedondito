# 🍩 Pyne Buñuelos MiRedondito

[![Incremental Daily Update](https://github.com/jdrodriguez1000/Pyne_Bunuelos_MIRedondito/actions/workflows/incremental_daily.yaml/badge.svg)](https://github.com/jdrodriguez1000/Pyne_Bunuelos_MIRedondito/actions/workflows/incremental_daily.yaml)

Sistema de gestión automatizada de datos para la pyme de Buñuelos **MiRedondito**.

## 🚀 Automatización con GitHub Actions

Este repositorio cuenta con un flujo de trabajo automatizado que:
*   **Se ejecuta diariamente a las 01:00 UTC**.
*   Utiliza **Python 3.12** para procesar actualizaciones incrementales.
*   Sincroniza datos de ventas, inventario, finanzas, clima y marketing digital con una base de datos en **Supabase**.
*   Utiliza secretos de GitHub para manejar credenciales de forma segura.

## 🛠️ Estructura del Proyecto

*   `incremental_update.py`: Script principal de actualización diaria.
*   `upload_to_supabase.py`: Utilidad para carga masiva inicial.
*   `generate_*.py`: Scripts generadores de datos sintéticos.
*   `.github/workflows/`: Directorio de automatización.

## 📊 Monitoreo

Puedes ver el historial de ejecuciones y los logs detallados haciendo clic en el **escudo de estado** arriba o entrando en la pestaña **Actions** de este repositorio.
