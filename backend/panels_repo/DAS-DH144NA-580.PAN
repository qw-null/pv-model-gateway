PVObject_=pvModule
  Version=7.2.3
  Flags=$00908443

  PVObject_Commercial=pvCommercial
    Comment=DAS SOLAR CO., LTD.
    Flags=$0041
    Manufacturer=DAS SOLAR CO., LTD.
    Model=DAS-DH144NA-580
    DataSource=TÜV NORD 2024
    YearBeg=2023
    Width=1.134
    Height=2.278
    Depth=0.030
    Weight=31.300
    NPieces=100
    PriceDate=10/05/16 10:41
    Currency=€
    Remarks, Count=7
      Str_1=- All measurements and PAN file creation have been
      Str_2=completed by T¨¹V NORD
      Str_3=- Refer to report TRPVP06120/24P/01_R1 for additional
      Str_4=information.
      Str_5=Anodized aluminium alloy
      Str_6=2.0mm Glass / Encapsulation / 2.0mm Glass
      Str_7=Jbox IP 68, 3 diodes
    End of Remarks=Jbox IP 68, 3 diodes
  End of PVObject pvCommercial

  Technol=mtSiMono
  NCelS=72
  NCelP=2
  NDiode=3
  SubModuleLayout=slTwinHalfCells
  FrontSurface=fsARCoating
  GRef=1000
  TRef=25.0
  PNom=580.0
  PNomTolLow=0.00
  PNomTolUp=3.00
  BifacialityFactor=0.778
  Isc=14.000
  Voc=52.20
  Imp=13.320
  Vmp=43.55
  muISC=6.30
  muVocSpec=-126.0
  muPmpReq=-0.285
  RShunt=5000
  Rp_0=20000
  Rp_Exp=5.50
  RSerie=0.219
  Gamma=1.022
  muGamma=-0.0002
  VMaxIEC=1500
  Absorb=0.90
  ARev=3.200
  BRev=11.400
  RDiode=0.010
  VRevDiode=-0.70
  AirMassRef=1.500
  SandiaAMCorr=50.000
  RelEffic800=-0.10
  RelEffic600=-0.31
  RelEffic400=-0.50
  RelEffic200=-1.50

  PVObject_IAM=pvIAM
    Flags=$00
    IAMMode=UserProfile
    IAMProfile=TCubicProfile
      NPtsMax=9
      NPtsEff=9
      LastCompile=$B18D
      Mode=3
      Point_1=0.0,1.00000
      Point_2=20.0,1.00000
      Point_3=40.0,1.00000
      Point_4=60.0,1.00000
      Point_5=65.0,0.99800
      Point_6=70.0,0.99500
      Point_7=75.0,0.98100
      Point_8=80.0,0.93000
      Point_9=85.0,0.73600
    End of TCubicProfile
  End of PVObject pvIAM

  OperPoints, list of=7 tOperPoint
    Point_1=False,100,25.0,-4.01,0.00,0.000,0.000,0.00
    Point_2=False,200,25.0,-1.50,0.00,0.000,0.000,0.00
    Point_3=False,400,25.0,-0.50,0.00,0.000,0.000,0.00
    Point_4=False,600,25.0,-0.31,0.00,0.000,0.000,0.00
    Point_5=False,800,25.0,-0.10,0.00,0.000,0.000,0.00
    Point_6=True,1000,25.0,0.00,52.60,14.140,13.440,43.91
    Point_7=False,1100,25.0,0.05,0.00,0.000,0.000,0.00
  End of List OperPoints
End of PVObject pvModule
