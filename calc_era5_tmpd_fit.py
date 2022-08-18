from h5py import File as h5file
from glob import glob
from re import sub
import numpy
from matplotlib import pyplot as plt

test_files  = glob('/viirs4nb/xshcn/TEMPEST-D/*.mat')
# tmpd_files  = glob('/data2/xshao/TEMPEST-D/*.h5')

all_tcwv    = []
all_tb      = []
# fig = plt.figure()
era5_files  = []
tmpd_files  = []
for test_file in test_files:
    file_root   = sub(r'.*_(20.*_20.*)_v.*',r'\1',test_file)
    tmpd_file   = glob('/media/data13/xshcn/TEMPEST-D/H5/*'+file_root+'*.h5')
    if len(tmpd_file)==1:
        tmpd_files.append(tmpd_file[0])
        era5_files.append(test_file)
for era5_file, tmpd_file in zip(era5_files, tmpd_files):
    print('Processing file {:} ...'.format(era5_file),end='')
#    if 'p_tcwv' in h5file(era5_file,'r'):
#        print('Skipped')
#        continue
    if 'b_skt' not in h5file(era5_file,'r'):
        print('No skt')
        continue
    with h5file(era5_file,'r') as fid:
        tcwv    = fid['/b_tcwv'][...]
        skt     = fid['/b_skt'][...]
    with h5file(tmpd_file,'r') as fid:
        tb      = fid['/scan/TB'][...]
        binc    = fid['/scan/binc'][...]
    dlen    = numpy.prod(tcwv.shape)
    tcwv0   = tcwv.reshape(dlen,1)
    skt0    = skt.reshape(dlen,1)
    tb0     = tb.reshape(5,dlen).transpose()
    tb0[tb0<100]     = numpy.nan
    binc0   = binc.reshape(dlen,1)
    idx0    = numpy.any(numpy.concatenate((numpy.isnan(tcwv0),numpy.isnan(skt0),numpy.isnan(tb0)),axis=1),axis=1)==False
    tcwv0   = tcwv0[idx0]
    skt0    = skt0[idx0]
    tb0     = tb0[idx0,:]
    binc0   = binc0[idx0]
    p_tcwv  = numpy.full((dlen,1),numpy.nan)
    p_tcwv0 = p_tcwv[idx0]
    
    for ii in range(-1,67,2):
        idx1    = numpy.all(numpy.concatenate((binc0>ii,binc0<ii+2),axis=1),axis=1)
        tb1     = skt0[idx1]-tb0[idx1,:3]
        tb1     = numpy.concatenate([tb1,numpy.ones((tb1.shape[0],1))],axis=1)
        coef    = numpy.matmul(numpy.linalg.pinv(tb1),tcwv0[idx1])
        p_tcwv0[idx1]   = numpy.matmul(tb1,coef)
        # tb0     = numpy.array([tb[:,2]-tb[:,3],tb[:,5]]).transpose()
        # coef0   = numpy.matmul(numpy.linalg.pinv(tb0),tcwv)
        # plt.plot(numpy.matmul(tb,coef),tcwv,'.',markersize=1)
        # plt.xlim([0,80])
        
        # fig.clf()
        # for jj in range(3):
        #     ax = fig.add_subplot(2,3,jj+1)
        #     ax.plot(tb[:,jj],tcwv,'.',markersize=1)
        #     # ax.hist2d(tb[:,jj],tcwv[:,0],bins=100)
        #     ax.set_xlim([-20,180])
        #     ax.set_ylim([0,80])
        #     ax.set_xlabel('Ts-T{:}'.format(jj+1))
        #     ax.set_ylabel('TWV')
        # ax = fig.add_subplot(2,3,6)
        # ax.plot(numpy.matmul(tb,coef),tcwv,'.',markersize=1)
        # # ax.hist2d(numpy.matmul(tb,coef)[:,0],tcwv[:,0],bins=100)
        # ax.set_xlim([0,80])
        # ax.set_ylim([0,80])
        # ax.set_xlabel('Modeled TWV')
        # ax.set_ylabel('ECMWF TWV')
        # ax = fig.add_subplot(2,3,4)
        # ax.axis('off')
        # ax.text(0.5,0.5,'{:}<binc<{:}'.format(max(ii,0),ii+2))
        # fig.savefig('{:}.png'.format(ii+2))
        # print('{:}:{:}'.format(ii,numpy.mean((tcwv0[idx1]-numpy.matmul(tb1,coef))**2)**0.5))
    p_tcwv[idx0]    = p_tcwv0
    p_tcwv          = p_tcwv.reshape(tcwv.shape)
    with h5file(era5_file,'r+') as fid:
#        dset = fid.create_dataset('p_tcwv', p_tcwv.shape, dtype='f8')      
        fid['/p_tcwv'][...]   = p_tcwv
    print('Done')