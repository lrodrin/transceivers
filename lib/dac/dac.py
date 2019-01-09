import numpy as np
import scipy.signal as sgn

import lib.constellationV2 as modulation
import lib.ofdm as od


__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat> and Laia Nadal <laia.nadal@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


class Dac:

    def __init__(self, trx_mode, tx_ID):
        self.trx_mode = trx_mode # For identifying the mode of the transceiver: 0 for METRO_1 scenario or 1 for METRO_2 scenario
        self.tx_ID = tx_ID   # To identify the channel of the DAC to be used and the local files to use for storing data. Tx_id when Mode 0 (METRO_1 scenario) is equivalent to select the Openconfig client. Tx_id when Mode 1 (METRO_2 scenario) is equivalent to select the S_BVT, which includes 2 clients multiplexed in a single optical channel. Due to hardware limitations in this last case (METRO2 scenario) tx_ID will be always 0.

    def mode(self):
        tempfile='TEMP.txt'
        if self.trx_mode==0: # METRO1 scenario with BVTs to demonstrate bidirectionallity
            (Cx_up2, Cx_up) = self.transmitter()
            # Load the data in the DAC
            Qt=255 #Quantization steps
            Cx_bias=Cx_up2-np.min(Cx_up2)
            Cx_LEIA=np.around(Cx_bias/np.max(Cx_bias)*Qt-np.ceil(Qt/2)) #Signal to download to LEIA_DAC
            Cx_bias_up=Cx_up-np.min(Cx_up)
            Cx_up=np.around(Cx_bias_up/np.max(Cx_bias_up)*Qt-np.ceil(Qt/2))

			print('Initializing LEIA...')
			f=open("CLK.txt","w")
            f.write("2.0\n")   #freq. synth. control [GHz] (60GS/s--> 1.87, 64GS/s--->2GHz)
            f=open("CLK_ref.txt","w")
            f.write("10\n")   #10MHz or 50MHz Ref frequency
            f=open("Inputs_enable.txt","w")
            np.savetxt(tempfile, Cx_LEIA) #.txt with the OFDM signal
        
            if self.tx_ID==0:
                f.write("1\n 0\n 0\n 0\n")   #Hi_en, Hq_en, Vi_en, Vq_en
                #os.system('"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash -nodesktop -r ' "Leia_DAC_up;")
            else:
                f.write("0\n 1\n 0\n 0\n")   #Hi_en, Hq_en, Vi_en, Vq_en
                #os.system('"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash -nodesktop -r ' "Leia_DAC_down;")
                
            #time.sleep(100)
            print 'Leia initialized and SPI file uploaded'
            ACK=0
        elif self.trx_mode==1: #METRO2 scenario with an SBVT. In this case tx_ID can not be modified as the two slices are multiplexed in a supperchannel and are created in the same function call

            tx_ID=0
            (Cx_up2, Cx_up)=self.transmitter()
            Qt=255 #Quantization steps
            Cx_bias=Cx_up2-np.min(Cx_up2)
            Cx_LEIA=np.around(Cx_bias/np.max(Cx_bias)*Qt-np.ceil(Qt/2)) #Signal to download to LEIA_DAC
            Cx_bias_up=Cx_up-np.min(Cx_up)
            Cx_up=np.around(Cx_bias_up/np.max(Cx_bias_up)*Qt-np.ceil(Qt/2))
        
            print  'Initializing LEIA...'
            f=open("CLK.txt","w")
            f.write("2.0\n")   #freq. synth. control [GHz] (60GS/s--> 1.87, 64GS/s--->2GHz)
            f=open("CLK_ref.txt","w")
            f.write("10\n")   #10MHz or 50MHz Ref frequency
            f=open("Inputs_enable.txt","w")
            np.savetxt(tempfile, Cx_LEIA) #.txt with the OFDM signal
            f.write("1\n 0\n 0\n 0\n")   #Hi_en, Hq_en, Vi_en, Vq_en
            os.system('"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash -nodesktop -r ' "Leia_DAC_up;")
            time.sleep(100)
            print 'Leia initialized and SPI file uploaded'
            ACK=0

            tx_ID=1
            (Cx_up2, Cx_up)=self.transmitter()
            Qt=255 #Quantization steps
            Cx_bias=Cx_up2-np.min(Cx_up2)
            Cx_LEIA=np.around(Cx_bias/np.max(Cx_bias)*Qt-np.ceil(Qt/2)) #Signal to download to LEIA_DAC
            Cx_bias_up=Cx_up-np.min(Cx_up)
            Cx_up=np.around(Cx_bias_up/np.max(Cx_bias_up)*Qt-np.ceil(Qt/2))
        
            print  'Initializing LEIA...'
            f=open("CLK.txt","w")
            f.write("2.0\n")   #freq. synth. control [GHz] (60GS/s--> 1.87, 64GS/s--->2GHz)
            f=open("CLK_ref.txt","w")
            f.write("10\n")   #10MHz or 50MHz Ref frequency
            f=open("Inputs_enable.txt","w")
            np.savetxt(tempfile, Cx_LEIA) #.txt with the OFDM signal
            f.write("0\n 1\n 0\n 0\n")   #Hi_en, Hq_en, Vi_en, Vq_en
            os.system('"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash -nodesktop -r ' "Leia_DAC_down;")
            time.sleep(100)
            print 'Leia initialized and SPI file uploaded'
            ACK=0

        return(ACK)

    def transmitter(self):
        SNR_estimation=True
        Niterations=10 # Number of iterations

        Preemphasis='True'
        #=============================================
        #Algorithm parameters
        #=============================================
        gapdB=9.8
        Loading_algorithm='LCRA_QAM'

        #=============================================
        # Parameters for the OFDM signal definition
        #=============================================
        Ncarriers=512 # Number of carriers
        SNRT=np.zeros((Ncarriers,), dtype=float)
        SNR_in=np.empty((Ncarriers,), dtype=float)
        constellation="QAM"
        bps=4 #Bit per symbol
        CP=0.019 #Cyclic prefix
        NTS=4 #Number of training symbols
        Nsymbols=16*3*1024 # BER[kosnr]No. of symbols without TS
        NsymbolsTS=Nsymbols+NTS*Ncarriers # No. of symbols with TS
        Nframes=NsymbolsTS/Ncarriers # No of OFDM symbols / frames
        e_fec=np.true_divide(7,100) # FEC overhead
        sps=3.2 # Samples per symbol
        fs=64e9 # Sampling frequency DAC
        BWs=fs/sps #BW electrical signal
        print 'Signal bandwidth:', BWs/1e9, 'GHz'


        if SNR_estimation==False:
            print 'Implementing loading algorithm...'
            gap=10**(gapdB/10.)
            if self.tx_ID==0:
                SNR_in=np.load('ChannelGain.npy')
            else:
                SNR_in=np.load('ChannelGain2.npy')
            Load=od.Loading(Ncarriers, BWs)
            if Loading_algorithm=='LCMA_QAM':
                (En,bn)=Load.LCMA_QAM(gap,BitRate/float(BWs), SNR_in)
            if Loading_algorithm=='LCRA_QAM':
                (En,bn, BitRate)=Load.LCRA_QAM(gap, SNR_in)
            bps=np.sum(bn)/float(len(bn))
        else:
            bn=bps*np.ones(Ncarriers)
            bn[240:240+30]=np.zeros(30)
            bps=np.sum(bn)/float(len(bn))
            BitRate=BWs*bps # Net data rate

        fc=BWs/2
        BitStream=np.ma.empty(NsymbolsTS*bps) # Initialize BitStream
        ttime=(1/fs)*np.ones((sps*Nframes*(Ncarriers+np.round(CP*Ncarriers)),))
        ttt=ttime.cumsum()

        if self.tx_ID==0:
            np.random.seed(42)
        else:
            np.random.seed(36)
        data=np.random.randint(0, 2, bps*Nsymbols)
        TS=np.random.randint(0,2, NTS*bps*Ncarriers)
        BitStream=np.array(np.zeros(Nframes*np.sum(bn)),int)
        BitStream=np.r_[TS,data]
        BitStream=BitStream.reshape((Nframes,np.sum(bn)))
        cdatar=np.array(np.zeros((Nframes,Ncarriers)),complex)
    
        cumBit=0
        for k in range(0, Ncarriers):
            (FormatM, bitOriginal)=modulation.Format(constellation, bn[k])
            cdatar[:,k]=modulation.Modulator(BitStream[:,cumBit:cumBit+bn[k]], FormatM, bitOriginal, bn[k])
            cumBit=cumBit+bn[k]
        if SNR_estimation=='False': #Power loading
            cdatary=cdatar*np.sqrt(En)
        else:
            cdatary=cdatar

        FHTdatatx=od.ifft(cdatary, Ncarriers)
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
    
      
        #print G+ 'Upconversion...'

        Cx_up2=Cx_up.real*np.cos(2*np.math.pi*fc*ttt)+Cx_up.imag*np.sin(2*np.math.pi*fc*ttt)

        if Preemphasis=='True':
            print('Preemphasis...')
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
    

        if self.tx_ID==0:
            np.save('params_tx', (bn, cdatar, data, Cx_up, Cx_up2))
        else:
            np.save('params_tx2', (bn, cdatar, data, Cx_up, Cx_up2))

        return Cx_up, Cx_up2

    
if __name__ == '__main__':	
    Tx=DAC(0,0)
    ACK=Tx.mode()

