# Script to write html files based on HEALPIX pixels

import os, sys, glob
import argparse
import numpy as np
from astropy.table import Table
import astropy.io.fits

import desispec.io
from desitarget.targetmask import desi_mask
import desispec.spectra
import desispec.frame
import myspecselect # special (to be edited)

import plotframes
import utils_specviewer


parser = argparse.ArgumentParser(description='Create html pages for the spectral viewer')
parser.add_argument('--datadir', help='Path to spectra relative to DESI_ROOT', type=str, default="datachallenge/reference_runs/18.6/spectro/redux/mini/spectra-64")
parser.add_argument('--nspecperfile', help='Number of spectra in each html page', type=int, default=50)
parser.add_argument('--webdir', help='Base directory for webapges', type=str, default=os.environ['HOME']+"/prospect/website")
args = parser.parse_args()

datadir = os.environ['DESI_ROOT']+"/"+args.datadir
pp=glob.glob(datadir+"/*/*")
pixels=[x[-4:] for x in pp]

pixels=pixels[0:1] # TMP

# todo : select pixels not yet selected
# Loop on pixels
for pixel in pixels :
    print("* Working on pixel "+pixel)
    group=str(int(pixel)//100)
    thefile = datadir+"/"+group+"/"+pixel+"/spectra-64-"+pixel+".fits"
    spectra = desispec.io.read_spectra(thefile)
    zbfile = thefile.replace('spectra-64-', 'zbest-64-')
    zbest = Table.read(zbfile, 'ZBEST')
    # Handle several html pages per pixel : sort by RA_TARGET
    nbpages = int(np.ceil((spectra.num_spectra()/args.nspecperfile)))
    sort_indices = np.argsort(spectra.fibermap["RA_TARGET"])
    for i_page in range(nbpages) :
        print("** Page "+str(i_page)+" / "+str(nbpages))
        the_indices = sort_indices[i_page*args.nspecperfile:(i_page+1)*args.nspecperfile]
        thespec = myspecselect.myspecselect(spectra, indices=the_indices)
        thezb = utils_specviewer.match_zbest_to_spectra(zbest,thespec)
        # VI "catalog" - location to define later ..
        vifile = os.environ['HOME']+"/prospect/vilist_prototype.fits"
        vidata = utils_specviewer.match_vi_targets(vifile, thespec.fibermap["TARGETID"])
        titlepage = "specviewer_pix"+pixel+"_"+str(i_page)
        model = plotframes.create_model(thespec, thezb)
        savedir=args.webdir+"/pixels/pix"+pixel
        if not os.path.exists(savedir) : 
            os.mkdir(savedir)
            os.mkdir(savedir+"/vignettes")
        plotframes.plotspectra(thespec, zcatalog=thezb, vidata=vidata, model=model, title=titlepage, savedir=savedir)
        for i_spec in range(thespec.num_spectra()) :
            saveplot = savedir+"/vignettes/pix"+pixel+"_"+str(i_page)+"_"+str(i_spec)+".png"
            utils_specviewer.miniplot_spectrum(thespec,i_spec,model=model,saveplot=saveplot)



