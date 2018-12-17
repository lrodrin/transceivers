#!/usr/bin/python

#from __future__ import division
#import scipy as sp
#import cmath as math
import scipy.signal as sgn
import numpy as np
import matplotlib.pyplot as plt
import lib.constellationV2 as modulation
import lib.ofdm as ofdm
import lib.instruments_v16p12 as inst
import os
import subprocess
import time
# Console colors
W  = '\033[0m'  # white (normal)
RE  = '\033[91m' # red
G  = '\033[92m' # green
O  = '\033[93m' # orange
B  = '\033[94m' # blue
P  = '\033[95m' # purple
C  = '\033[96m' # cyan
GR = '\033[97m' # gray


def DSPTx(SNR_estimation, Loading_algorithm, SNR_in, sense, BitRate=20e9, gapdB=9.8):
    #=============================================
    # Parameters
    #=============================================
    
    #=============================================
    # Parameters for the OFDM signal definition
    #=============================================
    Ncarriers=512 # Number of carriers
    constellation="QAM"
    bps=2 #Bit per symbol
    CP=0.019 #Cyclic prefix
    NTS=4 #Number of training symbols 
    Nsymbols=16*3*1024 # BER[kosnr]No. of symbols without TS
    NsymbolsTS=Nsymbols+NTS*Ncarriers # No. of symbols with TS
    Nframes=NsymbolsTS/Ncarriers # No of OFDM symbols / frames
    e_fec=np.true_divide(7,100) # FEC overhead
    sps=3.2 # Samples per symbol
    fs=64e9 # Sampling frequency DAC
    BWs=fs/sps #BW electrical signal
    
    
    #=============================================
    # instrument parameters
    
    #=============================================
    tempfile='TEMP.txt'
    
    ##%%%%%%%%%%%%%Implement loading algorithm%%%%%%%%%%%%%%%%%
    if SNR_estimation==False:
        print 'Implementing loading algorithm...'
        #gapdB=11
        gap=10**(gapdB/10.)
        Load=ofdm.Loading(Ncarriers,BWs)
        if Loading_algorithm=='LCMA_QAM':
           #BitRate=20e9
           (En,bn)=Load.LCMA_QAM(gap,BitRate/float(BWs), SNR_in)      
        if Loading_algorithm=='LCRA_QAM':
            (En,bn, BitRate)=Load.LCRA_QAM(gap, SNR_in)      
        bps=np.sum(bn)/float(len(bn))  
        
    else:
        bn=bps*np.ones(Ncarriers)
        BitRate=BWs*bps # Net data rate
    #NetBitRate=BitRate/((1+np.true_divide(NTS,Nsymbols))*(1+CP)*(1+e_fec))# Gross rate
    #print G+'Electrical bandwidth of the OFDM signal %.2f Hz' % BWs, 'Gross Bit Rate', BitRate*1e-9, 'Gb/s', 'Net Bit Rate', NetBitRate*1e-9, 'Gb/s'
    #=============================================
    # Parameters for the simulation
    #=============================================
    #sps=2
    
    #fc=1.5*BWs# Electrical carrier frequency
    fc=BWs/2

    BitStream=np.ma.empty(NsymbolsTS*bps) # Initialize BitStream
    ttime=(1/fs)*np.ones((sps*Nframes*(Ncarriers+np.round(CP*Ncarriers)),))
    ttt=ttime.cumsum()
   
    #==========PllCode===================================
    
    #print G+'Generating data...'
    
    # Generate the bitstream
    np.random.seed(42)
    data=np.random.randint(0, 2, bps*Nsymbols)
   
    # Generate Training symbol
    TS=np.random.randint(0,2, NTS*bps*Ncarriers) 
    BitStream=np.array(np.zeros(Nframes*np.sum(bn)),int)
    BitStream=np.r_[TS,data]
    
    # Code/map data onto the propper constellation
    BitStream=BitStream.reshape((Nframes,np.sum(bn)))
    cdatar=np.array(np.zeros((Nframes,Ncarriers)),complex)
    cumBit=0

    for k in range(0, Ncarriers):
        (FormatM, bitOriginal)=modulation.Format(constellation, bn[k])
        cdatar[:,k]=modulation.Modulator(BitStream[:,cumBit:cumBit+bn[k]], FormatM, bitOriginal, bn[k])
        cumBit=cumBit+bn[k]

    FHTdatatx=ofdm.ifft(cdatar, Ncarriers)
    
    # add cyclic prefix
    FHTdata_cp=np.concatenate((FHTdatatx, FHTdatatx[:,0:np.round(CP*Ncarriers)]), axis=1)
    
    
    # Serialize
    Cx=FHTdata_cp.reshape(FHTdata_cp.size,)
    
    #print 'Clipping the signal...'
    deviation=np.std(Cx)
    #k_clip=3.16 # 256QAM 
    #k_clip=2.66 # optimum for 32QAM
    k_clip=2.8 # optimum for 64QAM
    Cx_clip=Cx.clip(min=-k_clip*deviation, max=k_clip*deviation)
    		
    ## resample
    Cx_up=sgn.resample(Cx_clip, sps*Cx_clip.size)

    # Upconvert to fc
    Cx_up2=Cx_up.real*np.cos(2*np.math.pi*fc*ttt)+Cx_up.imag*np.sin(2*np.math.pi*fc*ttt)
    
    #Pre-emphasis (inverted gaussian) filter
    BW=25e9;
    #BW=20e9;
    n=2;
    sigma=BW/(2*np.sqrt(2*np.log10(2)))
    stepfs=fs/len(Cx_up2)
    freq1=np.arange(stepfs,fs/2-stepfs,stepfs)
    freq2=np.arange(-fs/2,0,stepfs)
    freq=np.r_[freq1,0,freq2,fs/2-stepfs]
    emphfilt=np.exp(.5*np.abs(freq/sigma)**n);# just a gaussian filter inverted
    Cx_up2=np.real(np.fft.ifft(emphfilt*np.fft.fft(Cx_up2)))
    
    Qt=255 #Quantization steps
    Cx_bias=Cx_up2-np.min(Cx_up2)
    Cx_LEIA=np.around(Cx_bias/np.max(Cx_bias)*Qt-np.ceil(Qt/2)) #Signal to download to LEIA_DAC
    Cx_bias_up=Cx_up-np.min(Cx_up)
    Cx_up=np.around(Cx_bias_up/np.max(Cx_bias_up)*Qt-np.ceil(Qt/2)) 
        
    f=open("CLK.txt","w")
    f.write("2.0\n")   #freq. synth. control [GHz] (60GS/s--> 1.87, 64GS/s--->2GHz)
    f=open("CLK_ref.txt","w")
    f.write("10\n")   #10MHz or 50MHz Ref frequency 
    f=open("Inputs_enable.txt","w")
    f.write("0\n 1\n 0\n 0\n")   #Hi_en, Hq_en, Vi_en, Vq_en
    np.savetxt(tempfile, Cx_LEIA) #.txt with the OFDM signal
    if slice_num==1:
        os.system('"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash -nodesktop -wait -r ' "Leia_DAC_up;")
        
    else:
        os.system('"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash -nodesktop -wait -r ' "Leia_DAC_down;")
    
        
    np.save('params_tx', (bn, cdatar, data, Cx_up))
        
    return BitRate
    
def DSPRx(SNR_estimation, Loading_algorithm,  BitRate=20e9, Numiter=1):    

    #=============================================
    # Parameters for the OFDM signal definition
    #=============================================
    Ncarriers=512 # Number of carriers
    constellation="QAM"
    CP=0.019 #Cyclic prefix
    NTS=4 #Number of training symbols 
    Nsymbols=16*3*1024 # BER[kosnr]No. of symbols without TS
    NsymbolsTS=Nsymbols+NTS*Ncarriers # No. of symbols with TS
    Nframes=NsymbolsTS/Ncarriers # No of OFDM symbols / frames
    sps=3.2 # Samples per symbol
    fs=64e9 # Sampling frequency DAC
    BWs=fs/sps #BW electrical signal
    f_DCO=100e9
    Tx_success=False
    #bn=params_ofdm[0]
    #cdatar=params_ofdm[1]
    #data=params_ofdm[2]
    #Cx_up=params_ofdm[3]
    (bn,cdatar, data, Cx_up)=np.load('params_tx.npy')
    
    nsamplesrx=2*sps*Nframes*(Ncarriers+np.round(CP*Ncarriers)) #nsamplesrx must be multiple of 4
        
    
    R=f_DCO/fs
    fc=BWs/2
    ttime2=(1/fs)*np.ones((nsamplesrx,))
    ttt2=ttime2.cumsum()
    Subzero=np.array(np.where(bn==0))
    SNRT=0
    SNR=0
    BERT=0
    BER=0.5
    cdatar=np.delete(cdatar,Subzero,axis=1)  
    bn=np.delete(bn,Subzero)
    Runs=0
    
    for run in range(1,Numiter+1):
        Ncarriers_eq=Ncarriers
     #Acquire from DPO
    #    print 'Acquiring...'
        data_acqT=inst.acquire(1, R*nsamplesrx,f_DCO)
        data_acqT=data_acqT-np.mean(data_acqT)

        data_acq=sgn.resample(data_acqT,len(data_acqT)/float(R))    
        #print G+ 'Downconversion...'
    
        I_rx_BB=data_acq*np.cos(2*np.math.pi*fc*ttt2)+1j*data_acq*np.sin(2*np.math.pi*fc*ttt2)
    
    
    
     #Resample reference data
       #ref=sgn.resample(Cx_up2,Cx_up2.size*R)
        #ref2=sgn.resample(Cx_up[0:NTS*(Ncarriers+Ncarriers*CP)], NTS*(Ncarriers+Ncarriers*CP)*R)
        
        ref2=Cx_up[0:sps*NTS*(Ncarriers_eq+np.round(CP*Ncarriers_eq))]
    #    # Filter
    #    #[B, A]=sgn.bessel(20, np.math.pi/sps,  btype='low', analog=False, output='ba')
    #    #B=sgn.firwin(30, BitRate/fs, None, 'flattop')
        #print G+ 'Filtering...'
        
        Bfilt=sgn.firwin(2**9, BWs/fs, 0)
        I_rx_BBf=sgn.filtfilt(Bfilt, [1], I_rx_BB)
    
    #Syncronize
    #Make the X-correlation
        #print 'Xcorrelating...', run
    #Rd=np.correlate(data_acq, ref)
    #Rdlog=20*np.log10(np.abs(Rd))
        Rd=np.correlate(I_rx_BBf[0:nsamplesrx/2], ref2)
        Rdlog=20*np.log10(np.abs(Rd))
        if(Rdlog.max(0)<np.mean(Rdlog)+20):
			print 'Warning: Not able to sync!'
			#Runs=Runs+1
        else: 
            #if run==Numiter:
            #plt.plot(Rdlog)
            #plt.show()
            
            #print 'Xcorrelation made!'
            peakind=(Rdlog==Rdlog.max(0)).nonzero()
            index=peakind[0][0]
            data_sync=I_rx_BBf[index:index+nsamplesrx/2]
        #data_sync=ref.copy()
            
        #plt.plot(data_sync.real/np.std(data_sync))
        #plt.plot(ref.reNerr+=Nerr/float(run)al/np.std(ref))
        #plt.show()Nerr+=Nerr/float(run)
            #datadown=data_sync.reshape((-1, sps))
            Cx_down=sgn.resample(data_sync,(Ncarriers_eq+np.round(CP*Ncarriers_eq))*Nframes) 
        
              
            cdatarxr_CP=Cx_down.reshape(Nframes, Ncarriers_eq+np.round(CP*Ncarriers_eq))
            
            #Remove CP
            cdatarxr=cdatarxr_CP[:,0:Ncarriers_eq]
        
            # Perform Transform
            FHTdatarx=ofdm.fft(cdatarxr, Ncarriers_eq)
        #remove subcarriers set to 0 for equalization
            
            FHTdatarx=np.delete(FHTdatarx,Subzero,axis=1)          
            Ncarriers_eq=Ncarriers_eq-Subzero.size
        
            #Equalize
            #FHTdatarx_eq=ofdm.equalize_fft(FHTdatarx, cdatar, Ncarriers_eq, NTS)
            #print FHTdatarx.size
            #print Ncarriers
            #print cdatar.size
            FHTdatarx_eq=ofdm.equalize_MMSE_LE(FHTdatarx, cdatar, Ncarriers_eq, NTS)
               #FHTdatarx_eq=ofdm.equalize_LMS(FHTdatarx, cdatar, Ncarriers, NTS) 
        #FHTdatarx_eq=FHTdatarx_eq
            #FHTdatarx_eq=np.delete(FHTdatarx_eq,Subzero,axis=1)          
            #cdatar_eq=np.delete(cdatar,Subzero,axis=1)  
            #Ncarriers_eq=Ncarriers_eq-Subzero.size
            #SNR estimation
            #if SNR_estimation==True:
            SNR=ofdm.SNR_estimation(cdatar[NTS:,],FHTdatarx_eq,Nframes-NTS,Ncarriers_eq)
            SNRT=SNR+SNRT
            if run==Numiter:
                SNR=SNRT/Numiter
                np.save('ChannelGain', SNR)
                    #x=np.arange(0,Ncarriers_eq)
                    #plt.figure()
                    #plt.plot(x,10*np.log10(SNR))
        #        plt.show()
            #just a trick for not taking into account 
            #Neither the N/2 carrier nor the first carrier
            FHTdatarx_eq[:,Ncarriers_eq/2]=cdatar[NTS:,Ncarriers_eq/2]
            FHTdatarx_eq[:,0]=cdatar[NTS:,0]
            
            # Serialize
            bps2=np.sum(bn)/float(len(bn))
            datarx=np.array(np.zeros((Nframes-NTS,np.round(Ncarriers_eq*bps2))))
            cumbit=0
            # Bit decision
            for i in range(0,Ncarriers_eq):
                (FormatM, bitOriginal)=modulation.Format(constellation, bn[i])
                datarx[:,cumbit:cumbit+bn[i]]=modulation.Demod(FHTdatarx_eq[:,i],FormatM.reshape(1,-1),bitOriginal,bn[i])
                #datarx[:,cumbit:cumbit+bn[i]]=modulation.Demod(FHTdatarx_eq[:,i],FormatM,bitOriginal,bn[i])
                cumbit=cumbit+bn[i]
            datarx=datarx.reshape(np.round(Ncarriers_eq*(Nframes-NTS)*bps2,))
           # modulation.dibuixar_constelacions(np.real(RxConst),np.imag(RxConst))
            diff=datarx-data
            
            #BER calculus
            Nerr=np.sum(np.sqrt(diff.real**2+diff.imag**2))
            BER=np.true_divide(Nerr,data.size)  
            #print 'BER=',BER, 'iteration=', run
            #if BER< 1e-1:
            BERT=BERT+BER
            Runs=Runs+1
        
        
            BER=BERT/Runs 
        #print'Average BER=', BER
        #print 'BER size', BERT.size
        
        if BER > 3e-3:
            Tx_success=False
        else:
            Tx_success=True
    
    return (Tx_success, BER, SNR)

    
if __name__ == '__main__':
    
    estimate_SNR=True
    Algorithm='LCMA_QAM' # 0 == Rate adaptiv if SNR_estimation==True:e , 1 == Margin adaptive
    BitRate=20e29 # BitRate (bps)
    Niterations=10 # Number of iterations
    SNRT=np.zeros((512,), dtype=float)
    slice_num=1
    BitRate=DSPTx(estimate_SNR, Algorithm, SNRT, slice_num, BitRate)
    #(Tx_success, BERactual,SNRactual)=DSPRx(True, Algorithm, BitRate, 1)