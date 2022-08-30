import atlite
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterio.plot import show
from atlite.gis import shape_availability, ExclusionContainer
import os
import calendar
import pandas as pd
import numpy as np
import datetime as dt
import scipy.stats as stats
os.chdir('/home/roberto/Documents/Titulación/Archivos')

dump = [7]
countries = ["Spain","Germany"]
years = [2008,2009,2010,2011,2012,2013,2014,2015,2016,2017]

## Solar output for one day in one country using dump territories. (Output in MWh)
def solar_one_day(country,year,month,day):
    type_of_panel = atlite.solarpanels.CSi
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    countries = [country]
    shapes = world[world.name.isin(countries)].set_index('name')
    bounds = shapes.unary_union.buffer(1).bounds
    name = country+'('+str(year)+' - ' +str(month)+' - '+str(day)+").nc"
    cutout = atlite.Cutout(name, module='era5', bounds=bounds, time=slice(str(year)+'-'+str(month)+'-'+str(day),str(year)+'-'+str(month)+'-'+str(day)))
    CORINE = 'corine.tif'
    excluder = ExclusionContainer()
    incluir = dump
    excluder.add_raster(CORINE, codes=incluir,invert=True)
    pais = shapes.loc[[country]].geometry.to_crs(excluder.crs)
    masked, transform = shape_availability(pais, excluder)
    eligible_share = masked.sum() * excluder.res**2 / pais.geometry.item().area
    A = cutout.availabilitymatrix(shapes, excluder)
    cap_per_sqkm = 1.7
    area = cutout.grid.set_index(['y', 'x']).to_crs(3035).area / 1e6
    area = xr.DataArray(area, dims=('spatial'))
    capacity_matrix = A.stack(spatial=['y', 'x']) * area * cap_per_sqkm
    cutout.prepare()
    pv = cutout.pv(matrix=capacity_matrix, panel= type_of_panel, 
                orientation='latitude_optimal', index=shapes.index)
    df = pv.to_pandas()
    df.rename(columns={country:country+'[MWh]'},inplace=True)
    return(df)


## Get the output for one country during one year in dump territories
def solar_year(country,year):
    type_of_panel = atlite.solarpanels.CSi
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    countries = [country]
    shapes = world[world.name.isin(countries)].set_index('name')
    bounds = shapes.unary_union.buffer(1).bounds
    name = country+str(year)+".nc"
    cutout = atlite.Cutout(name, module='era5', bounds=bounds, time=slice(str(year)+'-01-01',str(year+1)+'-01-01'))
    CORINE = 'corine.tif'
    excluder = ExclusionContainer()
    incluir = dump
    excluder.add_raster(CORINE, codes=incluir,invert=True)
    pais = shapes.loc[[country]].geometry.to_crs(excluder.crs)
    masked, transform = shape_availability(pais, excluder)
    eligible_share = masked.sum() * excluder.res**2 / pais.geometry.item().area
    A = cutout.availabilitymatrix(shapes, excluder)
    cap_per_sqkm = 1.7
    area = cutout.grid.set_index(['y', 'x']).to_crs(3035).area / 1e6
    area = xr.DataArray(area, dims=('spatial'))
    capacity_matrix = A.stack(spatial=['y', 'x']) * area * cap_per_sqkm
    cutout.prepare()
    pv = cutout.pv(matrix=capacity_matrix, panel=type_of_panel, 
                orientation='latitude_optimal', index=shapes.index)
    pv.to_pandas().to_csv('Output/'+country+str(year)+'.csv')

## Print a map showing the eligible area for solar panels. Default will be for Dump designated territories
def eligible_area(country,includer = dump):
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    countries = [country]
    shapes = world[world.name.isin(countries)].set_index('name')
    bounds = shapes.unary_union.buffer(1).bounds
    name = country+".nc"
    cutout = atlite.Cutout(name, module='era5', bounds=bounds, time=slice('2009-01-01','2010-01-01'))
    CORINE = 'corine.tif'
    excluder = ExclusionContainer()
    excluder.add_raster(CORINE, codes=includer,invert=True)
    pais = shapes.loc[[country]].geometry.to_crs(excluder.crs)
    masked, transform = shape_availability(pais, excluder)
    eligible_share = masked.sum() * excluder.res**2 / pais.geometry.item().area
    fig, ax = plt.subplots(figsize=(15,10))
    ax = show(masked, transform=transform, cmap='Greens', ax=ax)
    pais.plot(ax=ax, edgecolor='k',color='None')
    cutout.grid.to_crs(excluder.crs).plot(edgecolor='grey', color='None', ax=ax, ls=':')
    ax.set_title(f'{country}\nEligible area (green) {eligible_share * 100:2.2f}%');

## Print an easier to read map showing the eligible area for solar panels. Default will be for Dump designated territories
def area_elegible(country, includer=dump):
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    countries = [country]
    shapes = world[world.name.isin(countries)].set_index('name')
    bounds = shapes.unary_union.buffer(1).bounds
    name = country+".nc"
    cutout = atlite.Cutout(name, module='era5', bounds=bounds, time=slice('2009-01-01','2010-01-01'))
    CORINE = 'corine.tif'
    excluder = ExclusionContainer()
    incluir = dump
    excluder.add_raster(CORINE, codes=incluir,invert=True)
    pais = shapes.loc[[country]].geometry.to_crs(excluder.crs)
    masked, transform = shape_availability(pais, excluder)
    eligible_share = masked.sum() * excluder.res**2 / pais.geometry.item().area
    A = cutout.availabilitymatrix(shapes, excluder)
    fig, ax = plt.subplots(figsize=(20,15))
    A.sel(name=country).plot(cmap='Greens')
    shapes.loc[[country]].plot(ax=ax, edgecolor='k', color='None')
    cutout.grid.plot(ax=ax, color='None', edgecolor='grey', ls=':')
    ax.set_title(f'{country}\nEligible area (green) {eligible_share * 100:2.2f}%');

## Will merge output from the code into single csv file
def unite():
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    todo = {}
    for year in years:
        for country in paises:
            todo[country+str(year)]=pd.read_csv('Output/'+country+str(year)+'.csv',parse_dates=[0])
            todo[country+str(year)].set_index('time',inplace=True)
            todo[country+str(year)]=todo[country+str(year)]/1000            ## Converts to GW

    df = pd.concat([todo['Spain2008'],todo['Germany2008']],axis=1)
    for year in years[1:]:
        df_aux = pd.concat([todo['Spain'+str(year)],todo['Germany'+str(year)]],axis=1)
        df = pd.concat([df,df_aux])  
    df.to_csv('Output/Combinado.csv')
    os.chdir('/home/roberto/Documents/Titulación/Archivos')

## Runs Atlite's functions for Spain and Germany from 2008 to 2017 and unifies the output into single csv file (Output in GWh)
def execute_order_66():
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    for country in countries:
        for year in years:
            solar_year(country,year)
    unite()

## Reads the single csv file and returns a Pandas DataFrame
def read_single_csv():
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    df = pd.read_csv('Output/Combinado.csv',parse_dates=[0])
    df = df[(df['time'] < '2018-01-01')]
    df.set_index('time',inplace=True)
    df.index.drop_duplicates(keep=False)
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    return (df)

##########################################################################

## Analyzing the output

## Plot three random consecutive days of output for one country. 
## Displays one color for each year of the ten available in our output
def three_random(country):
    df = read_single_csv()
    df['doy'] = df.index.dayofyear
    df['time']=df.index.time
    df['Year'] = df.index.year
    df['ind']= df['doy'].astype(str)+"-"+ df['time'].astype(str)
    df['ind']=pd.to_datetime(df['ind'],format='%j-%H:%M:%S')
    piv = pd.pivot_table(df, index=['ind'],columns=['Year'], values=[country])
    piv = piv[(piv.index <'1901-01-01')]
    month_numeric = np.random.choice(list(piv.index.month.unique()))
    aux = piv[piv.index.month==month_numeric]
    split = np.array_split(aux,10)
    x = np.random.choice(range(10))
    plot_name = country+"\n"+ str(calendar.month_name[month_numeric])
    split[x].plot(title = plot_name,figsize=(20,7),xlabel = 'Date',ylabel='Solar Power [GW]', ls='--')
    plt.legend(title = "Country:")
    plt.show()
    plt.close()

## Returns a DataFrame with the total PV production for each year for one country
def anual_country(country):
    df = read_single_csv()
    pais_1 = df[country]
    total = {}
    for year in years:
        total[str(year)] = pais_1.loc[str(year)].sum()
    sums = pd.DataFrame.from_dict(total,orient='index')
    title  = 'GWh ' + country
    sums.rename(columns={0:title},inplace=True)
    return(sums)

## Returns the total production for each year for one country and one specific month (Dictionary)
def sum_month(country,month): ## Insert month as integer
    auxiliar = read_single_csv()
    auxiliar['Month']=auxiliar.index.month
    auxiliar['Year']=auxiliar.index.year
    month_of_interest = auxiliar.loc[auxiliar['Month']==month]
    sums = {}
    for year in years:
        sums[year] = month_of_interest.loc[month_of_interest['Year']==year][country].sum()
    return(sums)

## Boxplot yearly production for each month for one country
def box_plots_monthly(country):
    dictionary = {}
    for i in range(1,13):
        suma = sum_month(country,i)
        aux = []
        for value in suma.values():
            aux.append(value)
        dictionary[i]=aux
    prod_tot_month = pd.DataFrame.from_dict(dictionary)
    prod_tot_month['Year']=years
    prod_tot_month.set_index('Year',inplace=True)
    months = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
    prod_tot_month.rename(columns= months,inplace=True)
    plt.figure(figsize=(15,8))
    plt.boxplot(prod_tot_month,labels=list(prod_tot_month.columns))
    plt.grid('True')
    plt.ylabel('Production [GWh]')
    plt.title(country)
    plt.ylim(0,max(prod_tot_month.max()))
    plt.show()

###############################################################################

## Extracting the economic value of the production (prices)

## Lee archivos de precios de generación por cada mes. Se debe llamar desde ventas_spain()
def precios_spain():
    os.chdir('/home/roberto/Documents/Titulación/Precios España')
    files = ['PFMMESES_CUR_20200101_20200131.xls','PFMMESES_CUR_20200201_20200229.xls','PFMMESES_CUR_20200301_20200331.xls','PFMMESES_CUR_20200401_20200430.xls',
            'PFMMESES_CUR_20200501_20200531.xls','PFMMESES_CUR_20200601_20200630.xls','PFMMESES_CUR_20200701_20200731.xls','PFMMESES_CUR_20200801_20200831.xls',
            'PFMMESES_CUR_20200901_20200930.xls','PFMMESES_CUR_20201001_20201031.xls','PFMMESES_CUR_20201101_20201130.xls','PFMMESES_CUR_20201201_20201231.xls']
    precios = {}
    aux = 1
    for i in files:
        precios[aux] = pd.read_excel(i,header=3)['Total\n€/MWh'][0]
        aux = aux+1
    precios = pd.DataFrame.from_dict(precios,orient='index')

    months = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
    precios.rename(index = months,inplace=True,columns={0:'Precios (Euros/MWh)'})
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    return(precios)

## Regresa DataFrame con las ventas por cada mes de España
def ventas_spain():
    mes_espana = produccion_por_mes('Spain')
    spain = precios_spain()
    mes_espana.drop(index='Total',inplace=True)
    spain['Produccion [GWh]']=mes_espana['Mean [GW]']
    spain['Ventas (Euros)']=spain['Precios (Euros/MWh)']*1000*spain['Produccion [GWh]']
    anuales = spain['Ventas (Euros)'].sum()
    spain['Precios (Euros/MWh)']= spain['Precios (Euros/MWh)'].apply(lambda x: "€{:,.2f}".format(x))
    spain.loc['Annual']=['','',anuales]
    spain['Ventas (Euros)']=np.round(spain['Ventas (Euros)'],2)
    spain['Ventas (Euros)']= spain['Ventas (Euros)'].apply(lambda x: "€{:,.2f}".format(x))
    return(spain)

## Regresa DataFrame con las ventas por cada mes de Alemania
def ventas_germany():
    mes_alemania = produccion_por_mes('Germany')
    prices_germany = {'January': 49.39,'February':42.82,'March':30.63,'April':39.96,
                'May':37.84,'June':32.52,'July':39.69,'August':36.85,'September':35.75,'October':36.94,'November':41,'December':31.97}
    mes_alemania.drop(index='Total',inplace=True)
    precios = pd.DataFrame.from_dict(prices_germany,orient='index')
    precios.rename(columns={0:'Precios (Euros/MWh)'},inplace=True)
    precios['Produccion [GWh]']= mes_alemania['Mean [GW]']
    precios['Ventas (Euros)']=precios['Precios (Euros/MWh)']*1000*precios['Produccion [GWh]']
    anuales = precios['Ventas (Euros)'].sum()
    precios['Precios (Euros/MWh)']= precios['Precios (Euros/MWh)'].apply(lambda x: "€{:,.2f}".format(x))
    precios.loc['Annual']=['','',anuales]
    precios['Ventas (Euros)']=np.round(precios['Ventas (Euros)'],2)
    precios['Ventas (Euros)']= precios['Ventas (Euros)'].apply(lambda x: "€{:,.2f}".format(x))
    return(precios)

## Genera DataFrame con índice de las horas del día y columnas con algunas estadísticas de un mes y un país. (Perc. 0.75, median, perc. 0.25)
def Por_mes(Pais,Mes):
    df = leer()
    df['Month']=df.index.month
    df['Time']=df.index.time
    Country = df[[Pais,'Month','Time']]
    mes = Country.loc[Country['Month']== Mes]
    aux = mes.groupby('Time')
    hora =aux[Pais].agg([np.median, lambda x: np.quantile(x,0.75),lambda x: np.quantile(x,0.25)])
    hora.rename(columns={'<lambda_0>':'Perc. 0.75','<lambda_1>':'Perc. 0.25'},inplace=True)
    return(hora)

## Gráficas por cuatrimestre. Perc.0.75, median y perc. 0.25
def cuatrimestre(num_cuatrimestre,num_primer_mes,country):
    import calendar
    df = leer()
    max = df[country].max()
    titulo_sup =country+"\n"+str(num_primer_mes)+" - "+str(num_primer_mes+3)
    plt.figure(figsize=(60,35))
    plt.suptitle(titulo_sup,fontsize=50)

    plt.subplot(2,2,1)

    month_1 = Por_mes(country,num_primer_mes)

    x_axis = month_1.index.astype(str)

    plt.plot(x_axis,month_1['Perc. 0.75'],ls='dashdot',label="Perc. 0.75")
    plt.plot(x_axis,month_1['median'],ls='solid',label="Median")
    plt.plot(x_axis,month_1['Perc. 0.25'],ls='dashed',label="Perc. 0.25")
    titulo = str(calendar.month_name[num_primer_mes])
    plt.title(titulo,fontsize = 35)
    plt.legend(loc='upper left',fontsize='xx-large')
    plt.ylabel('Solar Power [GW]',fontsize = 35)
    plt.xlabel('Hour of day',fontsize=35)
    plt.tick_params(axis='y',labelsize=25)
    plt.minorticks_off()
    plt.ylim(bottom = 0,top = max)

    plt.subplot(2,2,2)

    month_2 = Por_mes(country,num_primer_mes+1)
    plt.plot(x_axis,month_2['Perc. 0.75'],ls='dashdot',label="Perc. 0.75")
    plt.plot(x_axis,month_2['median'],ls='solid',label="Median")
    plt.plot(x_axis,month_2['Perc. 0.25'],ls='dashed',label="Perc. 0.25")
    titulo = str(calendar.month_name[num_primer_mes+1])
    plt.title(titulo,fontsize = 35)
    plt.legend(loc='upper left',fontsize='xx-large')
    plt.ylabel('Solar Power [GW]',fontsize = 35)
    plt.tick_params(axis='y',labelsize=25)
    plt.xlabel('Hour of day',fontsize=35)
    plt.minorticks_off()
    plt.ylim(bottom = 0,top = max)

    plt.subplot(2,2,3)

    month_3 = Por_mes(country,num_primer_mes+2)
    plt.plot(x_axis,month_3['Perc. 0.75'],ls='dashdot',label="Perc. 0.75")
    plt.plot(x_axis,month_3['median'],ls='solid',label="Median")
    plt.plot(x_axis,month_3['Perc. 0.25'],ls='dashed',label="Perc. 0.25")
    titulo = str(calendar.month_name[num_primer_mes+2])
    plt.title(titulo,fontsize = 35)
    plt.legend(loc='upper left',fontsize='xx-large')
    plt.ylabel('Solar Power [GW]',fontsize = 35)
    plt.tick_params(axis='y',labelsize=25)
    plt.xlabel('Hour of day',fontsize=35)
    plt.minorticks_off()
    plt.ylim(bottom = 0,top = max)

    plt.subplot(2,2,4)

    month_4 = Por_mes(country,num_primer_mes+3)
    plt.plot(x_axis,month_4['Perc. 0.75'],ls='dashdot',label="Perc. 0.75")
    plt.plot(x_axis,month_4['median'],ls='solid',label="Median")
    plt.plot(x_axis,month_4['Perc. 0.25'],ls='dashed',label="Perc. 0.25")
    titulo = str(calendar.month_name[num_primer_mes+3])
    plt.title(titulo,fontsize = 35)
    plt.legend(loc='upper left',fontsize='xx-large')
    plt.ylabel('Solar Power [GW]',fontsize = 35)
    plt.tick_params(axis='y',labelsize=25)
    plt.xlabel('Hour of day',fontsize=35)
    plt.minorticks_off()
    plt.ylim(bottom = 0,top = max)
    
    plt.show()

## Llama a cuatrimestre
def graficas_cuatrimestre(country):
    cuatrimestre(1,1,country)
    cuatrimestre(2,5,country)
    cuatrimestre(3,9,country)