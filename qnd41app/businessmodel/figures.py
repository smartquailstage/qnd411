import matplotlib.pyplot as plt
import pandas as pd
from businessmodel.models import Venta
import matplotlib.dates as mdates

def my_figure():
    # Obtener datos del modelo
    ventas = Venta.objects.all().values('fecha', 'monto')
    
    # Convertir los datos en un DataFrame
    df = pd.DataFrame(list(ventas))
    
    # Depuración: Verificar el contenido del DataFrame
    print("Contenido del DataFrame:")
    print(df.head())
    
    # Verificar si la columna 'fecha' está presente en el DataFrame
    if 'fecha' not in df.columns or 'monto' not in df.columns:
        raise ValueError("El DataFrame debe contener las columnas 'fecha' y 'monto'")
    
    # Asegurarse de que la columna 'fecha' es de tipo datetime
    try:
        df['fecha'] = pd.to_datetime(df['fecha'])
    except Exception as e:
        raise ValueError(f"Error al convertir 'fecha' a datetime: {e}")
    
    # Agrupar por fecha y sumar los montos
    df_grouped = df.groupby('fecha').agg({'monto': 'sum'}).reset_index()

    # Crear gráfico
    fig, ax = plt.subplots()
    ax.plot(df_grouped['fecha'], df_grouped['monto'], marker='o', linestyle='-')
    
    # Etiquetas y título
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Monto')
    ax.set_title('Ventas por Fecha')
    
    # Ajustar el formato de fecha en el eje x
    ax.xaxis.set_major_locator(mdates.MonthLocator())  # Puedes ajustar esto según tus datos
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()  # Rotar las fechas para mejor legibilidad
    
    # Ajustar el rango de los ejes para una mejor visualización
    ax.relim()
    ax.autoscale_view()

    return fig

