PVObject_=pvModule
  Version=7.2.4
  Flags=$00900043

  PVObject_Commercial=pvCommercial
    Comment=www.trinasolar.com (China)
    Flags=$0041
    Manufacturer=Trina Solar
    Model=TSM-660NEG21C.20
    DataSource=UL 2022
    YearBeg=2022
    Width=1.303
    Height=2.384
    Depth=0.033
    Weight=38.300
    NPieces=100
    PriceDate=24/04/19 10:39
    Currency=EUR
    Remarks, Count=2
      Str_1
      Str_2
    End of Remarks
  End of PVObject pvCommercial

  Technol=mtSiMono
  NCelS=66
  NCelP=2
  NDiode=3
  SubModuleLayout=slTwinHalfCells
  GRef=1000
  TRef=25.0
  PNom=660.0
  PNomTolLow=0.00
  PNomTolUp=3.00
  BifacialityFactor=0.809
  Isc=18.030
  Voc=46.60
  Imp=17.020
  Vmp=38.80
  muISC=6.47
  muVocSpec=-115.8
  muPmpReq=-0.303
  RShunt=800
  Rp_0=80000
  Rp_Exp=10.00
  RSerie=0.167
  Gamma=0.999
  muGamma=-0.0001
  VMaxIEC=1500
  VMaxUL=1500
  Absorb=0.90
  ARev=3.200
  BRev=12.168
  RDiode=0.010
  VRevDiode=-0.70
  AirMassRef=1.500
  CellArea=220.5
  SandiaAMCorr=50.000
  RelEffic800=0.41
  RelEffic600=0.70
  RelEffic400=0.32
  RelEffic200=-0.97

  PVObject_IAM=pvIAM
    Flags=$00
    IAMMode=UserProfile
    IAMProfile=TCubicProfile
      NPtsMax=9
      NPtsEff=9
      LastCompile=$B18D
      Mode=3
      Point_1=0.0,1.00000
      Point_2=30.0,1.00000
      Point_3=50.0,0.99900
      Point_4=60.0,0.99400
      Point_5=70.0,0.96900
      Point_6=75.0,0.92800
      Point_7=80.0,0.82900
      Point_8=85.0,0.58500
      Point_9=90.0,0.00000
    End of TCubicProfile
  End of PVObject pvIAM

  OperPoints, list of=4 tOperPoint
    Point_1=False,800,25.0,0.41,0.00,0.000,0.000,0.00
    Point_2=False,600,25.0,0.70,0.00,0.000,0.000,0.00
    Point_3=False,400,25.0,0.32,0.00,0.000,0.000,0.00
    Point_4=False,200,25.0,-0.97,0.00,0.000,0.000,0.00
  End of List OperPoints
End of PVObject pvModule
