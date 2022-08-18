from h5py import File as h5file
from glob import glob
from re import sub
import numpy
from matplotlib import pyplot as plt

date_str='20191007T000036'
era5_files =glob('./*'+date_str+'*.mat')
tmpd_files  = glob('/media/data13/xshcn/TEMPEST-D/H5/*'+date_str+'*.h5')
cline_file ='./coastlines.mat'
with h5file(cline_file,'r') as fid:
    clon    = fid['/coastlon'][0]
    clat    = fid['/coastlat'][0]

all_tcwv    = []
all_tb      = []
fig = plt.figure()
for era5_file, tmpd_file in zip(era5_files, tmpd_files):
    with h5file(era5_file,'r') as fid:
        tcwv    = fid['/b_tcwv'][...]
        p_tcwv  = fid['/p_tcwv'][...]
    with h5file(tmpd_file,'r') as fid:
        blat    = fid['/scan/blat'][...]
        blon    = fid['/scan/blon'][...]
        asds    = fid['/scan/asds'][0]
    fig.clf()
    ax  = fig.add_subplot(1,1,1)
    h   = ax.scatter((blon[:,asds==1]+180)%360-180,blat[:,asds==1],1,tcwv[:,asds==1],vmin=0,vmax=70)
    ax.set_xlim([-180,180])
    ax.set_ylim([-80,80])
    ax.plot(clon,clat,'k')
    fig.colorbar(h,ax=ax)
    ax.set_title('Ascending, ECMWF TPW')
    fig.savefig('AD_'+date_str+'.png')
    fig.clf()
    ax  = fig.add_subplot(1,1,1)
    h   = ax.scatter((blon[:,asds==0]+180)%360-180,blat[:,asds==0],1,tcwv[:,asds==0],vmin=0,vmax=70)
    ax.set_xlim([-180,180])
    ax.set_ylim([-80,80])
    ax.plot(clon,clat,'k')
    fig.colorbar(h,ax=ax)
    ax.set_title('Descending, ECMWF TPW')
    fig.savefig('DD_'+date_str+'.png')
    fig.clf()
    ax  = fig.add_subplot(1,1,1)
    h   = ax.scatter((blon[:,asds==1]+180)%360-180,blat[:,asds==1],1,p_tcwv[:,asds==1],vmin=0,vmax=70)
    ax.set_xlim([-180,180])
    ax.set_ylim([-80,80])
    ax.plot(clon,clat,'k')
    fig.colorbar(h,ax=ax)
    ax.set_title('Ascending, Modeled TPW from TEMPEST-D')
    fig.savefig('AM_'+date_str+'.png')
    fig.clf()
    ax  = fig.add_subplot(1,1,1)
    h   = ax.scatter((blon[:,asds==0]+180)%360-180,blat[:,asds==0],1,p_tcwv[:,asds==0],vmin=0,vmax=70)
    ax.set_xlim([-180,180])
    ax.set_ylim([-80,80])
    ax.plot(clon,clat,'k')
    fig.colorbar(h,ax=ax)
    ax.set_title('Descending, Modeled TPW from TEMPEST-D')
    fig.savefig('DM_'+date_str+'.png')