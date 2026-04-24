PVObject_=pvModule
  Version=7.2.2
  Flags=$00100043

  PVObject_Commercial=pvCommercial
    Comment=www.trinasolar.com (China)
    Flags=$0041
    Manufacturer=ENF
    Model=DP60-260-275
    DataSource=Manufacturer 2016
    YearBeg=2015
    Width=0.992
    Height=1.650
    Depth=0.035
    Weight=18.600
    NPieces=100
    PriceDate=01/06/21 19:30
    Remarks, Count=5
      Str_1=框架: Aluminum
      Str_2=结构: Glass-Backsheet
      Str_3=连接: MC4 Compatible
      Str_4
      Str_5
    End of Remarks
  End of PVObject pvCommercial

  Technol=mtSiMono
  NCelS=60
  NCelP=1
  NDiode=3
  SubModuleLayout=slInLength
  GRef=1000
  TRef=25.0
  PNom=275.0
  PNomTolLow=0.00
  PNomTolUp=3.00
  Isc=9.260
  Voc=38.80
  Imp=8.540
  Vmp=32.20
  muISC=3.89
  muVocSpec=-116.1
  muPmpReq=-0.420
  RShunt=400
  Rp_0=1500
  Rp_Exp=20.00
  RSerie=0.259
  Gamma=1.070
  muGamma=-0.0005
  VMaxIEC=1500
  VMaxUL=1000
  Absorb=0.90
  ARev=3.200
  BRev=11.040
  RDiode=0.010
  VRevDiode=-0.70
  AirMassRef=1.500
  CellArea=242.2
  SandiaAMCorr=50.000

  PVObject_IAM=pvIAM
    Flags=$00
    IAMMode=UserProfile
    IAMProfile=TCubicProfile
      NPtsMax=9
      NPtsEff=9
      LastCompile=$B18D
      Mode=3
      Point_1=0.0,1.00000
      Point_2=30.0,0.99226
      Point_3=50.0,0.97221
      Point_4=60.0,0.95000
      Point_5=70.0,0.90381
      Point_6=75.0,0.85681
      Point_7=80.0,0.76206
      Point_8=85.0,0.47632
      Point_9=90.0,0.00000
    End of TCubicProfile
  End of PVObject pvIAM
End of PVObject pvModule
