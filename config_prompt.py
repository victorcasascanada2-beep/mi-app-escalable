# config_prompt.py

def prompt_capa_1_buscador(marca, modelo, anio, horas):
    """CAPA 1: Búsqueda quirúrgica filtrada por horas y año."""
    return f"""
    Actúa como un Scraper Especializado en Maquinaria Agrícola.
    Tu misión es encontrar 50 anuncios si es posible, anuncios reales de venta para: {marca} {modelo} del año {anio}.
    
    [FILTRO DE USO]
    Prioriza unidades que tengan aproximadamente {horas} horas de trabajo. 
    Es vital encontrar anuncios con un desgaste similar para una tasación justa.
    
    [INSTRUCCIONES]
    1. Usa Google Search para localizar anuncios en portales como Agriaffaires, Mascus, Traktorpool o MilAnuncios.
    2. Extrae de cada anuncio: Título, Precio (€), Horas Reales y Ubicación.
    3. Presenta los resultados en una TABLA Markdown clara.
    """

def prompt_capa_2_analista(datos_seleccionados):
    """CAPA 2: Recibe datos filtrados por el usuario y calcula la base de mercado."""
    return f"""
    Actúa como un Analista de Datos Financieros.
    Basándote SOLO en estos anuncios seleccionados por el usuario:
    {datos_seleccionados}
    
    [INSTRUCCIONES]
    1. Calcula el precio medio.
    2. Identifica el rango de precios (mínimo y máximo).
    3. Explica brevemente la tendencia actual para este modelo específico.
    """

def prompt_capa_3_perito(marca, modelo, precio_base, observaciones, ubicacion):
    """CAPA 3: Visión computacional y ajuste final por estado y extras."""
    return f"""
    Eres el Perito Judicial de Agrícola Noroeste. 
    Tienes un tractor {marca} {modelo} con un valor de mercado base de {precio_base}€.
    
    [DATOS ESPECÍFICOS]
    - Notas del estado: {observaciones}
    - Ubicación técnica: {ubicacion}
    
    [MISIÓN DE VISIÓN]
    1. Analiza las fotos adjuntas buscando:
       - Desgaste real de neumáticos (%).
       - Daños en chapa o cabina.
       - EXTRAS NO MENCIONADOS: Si ves pala, tripuntal o contrapesos, calcula su valor extra.
    2. Ajusta el precio base: Suma por extras y resta por desgastes.
    3. Da el VEREDICTO FINAL justificado.
    """
