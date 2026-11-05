# EcoTech Solutions - Trabajo Práctico Final

Proyecto académico con tres ejercicios:

- `Ejercicio1.py`: sanitización y análisis estadístico de sensores.
- `Ejercicio2.py`: modelo de productos, excepciones y persistencia JSON.
- `Ejercicio3.py`: auditoría con `unittest` e integración con Django.

## Estructura

- `catalogo_ecotech.json`: catálogo exportado por el Ejercicio 2.
- `templates/sustentabilidad/panel.html`: plantilla del panel web.
- `ecotech_web/`: proyecto Django real con `manage.py`, `settings.py`, `urls.py` y `views.py`.
- `requirements.txt`: dependencias del proyecto.

## Ejecución

```bash
python Ejercicio1.py
python Ejercicio2.py
python Ejercicio3.py
```

Para la aplicación Django:

```bash
pip install -r requirements.txt
cd ecotech_web
python manage.py runserver
```
