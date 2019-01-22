#!/usr/bin/python

import numpy as np
import cmath as math
from pylab import *

def fft(data, Ncarriers):
    return np.fft.fft(data, Ncarriers)

def ifft(data, Ncarriers):
    return np.fft.ifft(data, Ncarriers)

def equalize_fft(datarx, datatx, Ncarriers, NTS):
    TS2=datatx[0:NTS,:]
    
    Hs=datarx[0:NTS,:]
    
    Hs2=Hs/TS2
    
    H=sum(Hs2,axis=0)/NTS
    
    #Build diagonal
   
    W=diag(H)
    #W[0,0]=H[0]/TS2[0]
    
    #equalize
    IW=np.linalg.inv(W)
    data_eq_NTS=np.inner(datarx, IW)
    data_eq=data_eq_NTS[NTS:,]
    
    return data_eq
    
def equalize_MIMO(datarxH, datarxV, datatx,datatx2,Ncarriers, NTS):
    Data_eqH_NTS=np.array(np.zeros((len(datarxH),Ncarriers)),complex)
    Data_eqV_NTS=np.array(np.zeros((len(datarxH),Ncarriers)),complex)
    datarx=np.array(np.zeros((2,len(datarxH))),complex)
    TS=datatx[0:NTS,:]
    TS2=datatx2[0:NTS,:]
    
    Hs11=datarxH[0:NTS,:]/TS #TS
    Hs12=datarxH[NTS:2*NTS,:]/TS2 #0's
    Hs21=datarxV[0:NTS,:]/TS #0's
    Hs22=datarxV[NTS:2*NTS,:]/TS2  #TS
    
    H11=sum(Hs11,axis=0)/NTS
    H12=sum(Hs12,axis=0)/NTS
    H21=sum(Hs21,axis=0)/NTS
    H22=sum(Hs22,axis=0)/NTS
    for k in range(0, Ncarriers):
        MIMO=np.array([[H11[k], H12[k]], [H21[k], H22[k]]])
#        A=np.array([[1 ,1],[1, -1]])
#        A_inv=np.linalg.inv(A)
        IW=np.linalg.pinv(MIMO)
        datarx[0]=datarxH[:,k]
        datarx[1]=datarxV[:,k]
        data_eq=np.dot(IW,datarx)
        #data_eq=np.dot(A_inv,data_eq)
        Data_eqH_NTS[:,k]=data_eq[0]
        Data_eqV_NTS[:,k]=data_eq[1]  
    Data_eqH=Data_eqH_NTS[2*NTS:,]
    Data_eqV=Data_eqV_NTS[2*NTS:,]
    return Data_eqH,Data_eqV
def equalize_LS(datarxH, datarxV, datatx,Ncarriers, NTS):
    data_TSH=np.array(np.zeros((len(datarxH),Ncarriers)),complex)
    data_TSV=np.array(np.zeros((len(datarxV),Ncarriers)),complex)
    #weight is the optimal weight vector
    #mu is a positive step size ususally small
    u_data=datatx[0:NTS,:]
#    weight=np.array(np.ones((NTS,Ncarriers)),complex)
#    e=np.array(np.zeros((NTS,Ncarriers)),complex)
#    yd=np.array(np.zeros((NTS,Ncarriers)),complex)
#    mu=0.2
#    for i in range(0,NTS-1):
#        e[i+1] = u_data[i+1] - datarxH[i+1]*weight[i] 
#        weight[i+1] = weight[i] + mu * e[i+1] * np.conjugate(datarxH[i+1])
#    for i in range(0,len(datarxH)):
#        yd[i] = np.conjugate(weight[NTS-1]) * datarxH[i]
#    m, c = np.linalg.lstsq(datarxH, u_data)[0]
    for i in range(0,Ncarriers):
        A = np.vstack([datarxH[0:NTS,i], np.ones(NTS)]).T
        B = np.vstack([datarxV[0:NTS,i], np.ones(NTS)]).T
        mH,m2H=np.linalg.lstsq(A, u_data[0:NTS,i])[0]
        mV,m2V=np.linalg.lstsq(B, u_data[0:NTS,i])[0]
        data_TSH[:,i]=datarxH[:,i]*mH+m2H
        data_TSV[:,i]=datarxV[:,i]*mV+m2V
    data_eqH=data_TSH[NTS:,]
    data_eqV=data_TSV[NTS:,]
    return data_eqH,data_eqV
    
def equalize_MMSE_LE(datarx,datatx, Ncarriers, NTS):
    TS2=datatx[0:NTS,:]
    a=np.array(np.zeros(Ncarriers))
    b=np.array(np.zeros(Ncarriers))
    for i in range(0,Ncarriers):
        a[i]=np.sum(np.real(datarx[0:NTS,i])*np.real(TS2[:,i])+np.imag(datarx[0:NTS,i])*np.imag(TS2[:,i]))/np.sum(np.real(datarx[0:NTS,i])**2+np.imag(datarx[0:NTS,i])**2)
        b[i]=np.sum(np.real(datarx[0:NTS,i])*np.imag(TS2[:,i])-np.imag(datarx[0:NTS,i])*np.real(TS2[:,i]))/np.sum(np.real(datarx[0:NTS,i])**2+np.imag(datarx[0:NTS,i])**2)
    data_eq_NTS=(a+1j*b)*datarx
    data_eq=data_eq_NTS[NTS:,]
    return data_eq    
def equalize_LMS_DP(datarxH, datarxV, datatx,datatx2,Ncarriers, Numiter,n, aHH,aHV,aVH, aVV, eH,eV,y):
    X=np.array(np.zeros((2,Ncarriers)),complex)
    mu=0.1
    if n<Numiter:
       X[0]=datatx[n]
       X[1]=datatx2[n]
       for i in range(0,Ncarriers):
            A=np.array([[aHH[n,i],aHV[n,i]], [aVH[n,i], aVV[n,i]]])         
            y[:,i]=np.dot(np.conj(A),X[:,i])         
       eH[n]=datarxH[n]-y[0]
       eV[n]=datarxV[n]-y[1]
         #create the filter coefficients
       aHH[n+1]=aHH[n]+mu*datatx[n]*np.conj(eH[n])
       aHV[n+1]=aHV[n]+mu*datatx2[n]*np.conj(eH[n])
       aVH[n+1]=aVH[n]+mu*datatx[n]*np.conj(eV[n])
       aVV[n+1]=aVV[n]+mu*datatx2[n]*np.conj(eV[n])
    return aHH,aHV,aVH,aVV,y,eH,eV
def fht(data, Ncarriers):
    X=np.fft.fft(data, Ncarriers)
    return (X.real-X.imag)/np.sqrt(Ncarriers)

def equalize_fht(datarx, datatx, Ncarriers, NTS):

    TS2=datatx[0,:]
    
    Hs=datarx[0:NTS,:]
    
    H=sum(Hs,axis=0)/NTS
    
    TSRxrev=flipud(H)
    
    #Build A
    A=np.zeros((Ncarriers-1,))
    A1=(H[1:Ncarriers/2])/TS2[1:Ncarriers/2]
    A[0:Ncarriers/2-1]=A1
    A[Ncarriers/2-1]=0
    A[Ncarriers/2:len(A)]=flipud(A1)
    
    #Build B
    B1=TSRxrev[0:Ncarriers/2-1]/TS2[0:Ncarriers/2-1];
    B=np.zeros((Ncarriers-1,))
    B[0:Ncarriers/2-1]=-B1
    B[Ncarriers/2-1]=0
    B[Ncarriers/2:len(A)]=flipud(B1)
    
    AA=diag(A)
    BB=fliplr(diag(B))
    A0=H[0]/TS2[0]
    
    #Build W (eq matrix)
    W=np.zeros((Ncarriers, Ncarriers))
    W[1:Ncarriers, 1:Ncarriers]=AA+BB
    W[Ncarriers/2, Ncarriers/2]=1
    W[0,0]=H[0]/TS2[0]
    
    #equalize
    IW=np.linalg.inv(W)
    data_eq_NTS=np.inner(datarx, IW)
    data_eq=data_eq_NTS[NTS:,]
    
    return data_eq

def SNR_estimation(x,yeq,NFrames,Ncarriers):
    e=np.array(np.zeros((Ncarriers,NFrames),complex))
    SNR=np.array(np.zeros(Ncarriers))
    Px=np.array(np.zeros(Ncarriers))
    Pe=np.array(np.zeros(Ncarriers))
    for k in range(0,Ncarriers):
        Px[k]=np.sum(np.abs(x[:,k])**2)/len(x) 
        e[k,:]=yeq[:,k]-x[:,k]
        Pe[k]=np.sum(np.abs(e[k,:])**2)/len(e)
        SNR[k]=Px[k]/float(Pe[k]) # Px is 1
    
    return(SNR)
class Loading():
    def __init__(self, Ncarriers,BW): 
        self.Ncarriers=Ncarriers
        self.BW=BW
    def LCMA_QAM(self,gapdB,Rate,file):
        #initialization
        gap=10**(gapdB/10.)
        gn=np.load(file)
        En=np.array(np.zeros(self.Ncarriers))
        bn=np.array(np.zeros(self.Ncarriers))
        table=np.array(np.zeros(self.Ncarriers))
    
        #decision table
        table=2*gap/gn
        while(1):
            y=np.min(table)
            index=np.argmin(table)
            if np.sum(bn)>=self.Ncarriers*Rate:
                break
            else:
                En[index]=En[index]+y
                bn[index]=bn[index]+1
                table[index]=2*table[index] 
        #check data rate
        Rate_check=self.BW*(np.sum(bn)/float(self.Ncarriers))
        #check margin
        margin=10*np.log10(self.Ncarriers/np.sum(En))
        print 'Margin=', margin, 'Rate=', Rate_check
        return En,bn
    def LCRA_QAM(self,gapdB,gn):
        #initialization
        gap=10**(gapdB/10)
        #gn=np.load(file)
        En=np.array(np.zeros(self.Ncarriers))
        bn=np.array(np.zeros(self.Ncarriers))
        table=np.array(np.zeros(self.Ncarriers))
        Enorm=1
        Eused=0 #used energy
        #decision table
        table=2*gap/gn
        #table=2*gap
        while(1):
            y=np.min(table)
            index=np.argmin(table)
            Eused=Eused+y
            if Eused>self.Ncarriers*Enorm:
                break
            else:
                En[index]=En[index]+y
                bn[index]=bn[index]+1
                table[index]=2*table[index]                   
        #check data rate
        Rate_check=self.BW*(np.sum(bn)/float(self.Ncarriers))
        #print 'Rate=', Rate_check/1e9, 'Gb/s'
        return En,bn,Rate_check
    def LCMA_PAM(self,gapdB,Rate):
        #initialization
        gap=10**(gapdB/10)
        gn=np.load('ChannelGain.npy')
        En=np.array(np.zeros(self.Ncarriers))
        bn=np.array(np.ones(self.Ncarriers))
        table=np.array(np.zeros(self.Ncarriers))
    
        #decision table
        table=gap*(2**(2*bn)-1)/gn
        while(1):
            y=np.min(table)
            index=np.argmin(table)
            if np.sum(bn)>=self.Ncarriers*Rate:
                break
            else:
                En[index]=En[index]+y
                bn[index]=bn[index]+1
                table[index]=4*table[index]
        #check data rate
        Rate_check=(1/self.Ncarriers)*np.sum(bn)
        #check margin
        margin=10*np.log10(self.Ncarriers/np.sum(En))
        print 'Margin=', margin, 'Rate=', Rate_check
        return En,bn
    
    def LCRA_PAM(self,gapdB):
        #initialization
        gap=10**(gapdB/10)
        gn=np.load('ChannelGain.npy')
        En=np.array(np.zeros(self.Ncarriers))
        bn=np.array(np.ones(self.Ncarriers))
        table=np.array(np.zeros(self.Ncarriers))
        Enorm=1
        Eused=0 #used energy
        #decision table
        table=gap*(2**(2*bn)-1)/gn
        while(1):
            y=np.min(table)
            index=np.argmin(table)
            Eused=Eused+y
            if Eused>self.Ncarriers*Enorm:
                break
            else:
                En[index]=En[index]+y
                bn[index]=bn[index]+1
                table[index]=4*table[index] 
        #check data rate
        Rate_check=(1/self.Ncarriers)*np.sum(bn)
        print 'Rate=', Rate_check
        return En,bn
    def CCBMA_QAM(self,gapdB):
        gn=np.load('ChannelGain.npy')
        gap=10**(gapdB/10)
        gnOrdered=np.sort(gn)
        gnInvOrdered=gnOrdered[::-1] #re-order gn
        #initialize
        Eaverage=1
        btemp=np.array(np.zeros(Ncarriers))
        btemp[self.Ncarriers]=0 # Tentative total bits
        i=Ncarriers  # Initial number of used carriers
        
        #Set equal energy on used tones
        while i>0:
            SNR=np.array(np.zeros(i))
            En=self.Ncarriers*Eaverage/i
            for k in range (0,i):
                SNR[k]=gn[k]*En
            btemp[i]=np.sum(np.log2(1+(SNR/gap)))            
            if i<self.Ncarriers: #In order to avoid the last subcarrier
                if btemp[i]<btemp[i+1]:
                    bn=btemp[i+1]
                    break  #close while we have the total number of bits
                else:
                    i=i-1
            else:
                i=i-1
        #check data rate
        Rate_check=(1/self.Ncarriers)*np.sum(bn)       
        return bn, En, Rate_check
        
    def CCBRA_QAM(self,gapdB):
        gn=np.load('ChannelGain.npy')
        gap=10**(gapdB/10)
        gnOrdered=np.sort(gn)
        gn=gnOrdered[::-1] #re-order gn
        #initialize
        Eaverage=1
        btemp=np.array(np.zeros(Ncarriers))
        btemp[self.Ncarriers]=0 # Tentative total bits
        i=Ncarriers  # Initial number of used carriers
        
        #Set equal energy on used tones
        while i>0:
            SNR=np.array(np.zeros(i))
            En=self.Ncarriers*Eaverage/i
            for k in range (0,i):
                SNR[k]=gn[k]*En
            btemp[i]=np.sum(np.log2(1+(SNR/gap)))            
            if i<self.Ncarriers: #In order to avoid the last subcarrier
                if btemp[i]<btemp[i+1]:
                    bn=btemp[i+1]
                    break  #close while we have the total number of bits
                else:
                    i=i-1
            else:
                i=i-1     
        #check data rate
        Rate_check=(1/self.Ncarriers)*np.sum(bn)       
        return bn, En, Rate_check
        
    def CCBMA_PAM(self,gapdB):
        gn=np.load('ChannelGain.npy')
        gap=10**(gapdB/10)
        gnOrdered=np.sort(gn)
        gn=gnOrdered[::-1] #re-order gn
        #initialize
        Eaverage=1
        btemp=np.array(np.zeros(Ncarriers))
        btemp[self.Ncarriers]=0 # Tentative total bits
        i=Ncarriers  # Initial number of used carriers
        
        #Set equal energy on used tones
        while i>0:
            SNR=np.array(np.zeros(i))
            En=self.Ncarriers*Eaverage/i
            for k in range (0,i):
                SNR[k]=gn[k]*En
            btemp[i]=np.sum((1/2.)*np.log2(1+(SNR/gap)))            
            if i<self.Ncarriers: #In order to avoid the last subcarrier
                if btemp[i]<btemp[i+1]:
                    bn=btemp[i+1]
                    break  #close while we have the total number of bits
                else:
                    i=i-1
            else:
                i=i-1   
        #check data rate
        Rate_check=(1/self.Ncarriers)*np.sum(bn)       
        return bn, En, Rate_check
        
    def CCBRA_PAM(self,gapdB):
        gn=np.load('ChannelGain.npy')
        gap=10**(gapdB/10)
        gnOrdered=np.sort(gn)
        gn=gnOrdered[::-1] #re-order gn
        #initialize
        Eaverage=1
        btemp=np.array(np.zeros(Ncarriers))
        btemp[self.Ncarriers]=0 # Tentative total bits
        i=Ncarriers  # Initial number of used carriers
        
        #Set equal energy on used tones
        while i>0:
            SNR=np.array(np.zeros(i))
            En=self.Ncarriers*Eaverage/i
            for k in range (0,i):
                SNR[k]=gn[k]*En
            btemp[i]=np.sum((1/2.)*np.log2(1+(SNR/gap)))            
            if i<self.Ncarriers: #In order to avoid the last subcarrier
                if btemp[i]<btemp[i+1]:
                    bn=btemp[i+1]
                    break  #close while we have the total number of bits
                else:
                    i=i-1
            else:
                i=i-1   
     #check data rate
        Rate_check=(1/self.Ncarriers)*np.sum(bn)       
        return bn, En, Rate_check
