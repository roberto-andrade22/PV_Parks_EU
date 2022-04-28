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
os.chdir('/home/roberto/Documents/Titulación/Archivos')


water = [40,39,35,34]
paises = ["Spain","Germany"]
years = [2008,2009,2010,2011,2012,2013,2014,2015,2016,2017]

def solar_year(country,year):
    cadmio = atlite.solarpanels.CdTe
    os.chdir('/home/roberto/Documents/Titulación/Archivos')
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    countries = [country]
    shapes = world[world.name.isin(countries)].set_index('name')
    bounds = shapes.unary_union.buffer(1).bounds
    name = country+str(year)+".nc"
    cutout = atlite.Cutout(name, module='era5', bounds=bounds, time=slice(str(year)+'-01-01',str(year+1)+'-01-01'))
    CORINE = 'corine.tif'
    excluder = ExclusionContainer()
    incluir = water
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
    pv = cutout.pv(matrix=capacity_matrix, panel=cadmio, 
                orientation='latitude_optimal', index=shapes.index)
    pv.to_pandas().to_csv('Output/'+country+str(year)+'.csv')
    #return(pv)

def eligible_area(country,includer):
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
    fig, ax = plt.subplots(figsize=(20,20))
    ax = show(masked, transform=transform, cmap='Greens', ax=ax)
    pais.plot(ax=ax, edgecolor='k', color='None')
    cutout.grid.to_crs(excluder.crs).plot(edgecolor='grey', color='None', ax=ax, ls=':')
    ax.set_title(f'{country}\nEligible area (green) {eligible_share * 100:2.2f}%');