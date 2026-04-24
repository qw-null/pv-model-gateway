PVObject_=pvModule
  Version=8.0.7
  Flags=$00108543

  PVObject_Commercial=pvCommercial
    Comment=DAS SOLAR CO., LTD.
    Flags=$0041
    Manufacturer=DAS SOLAR CO., LTD.
    Model=DAS-DH96NE.A-460
    DataSource=DAS SOLAR CO., LTD.
    YearBeg=2023
    Width=1.134
    Height=1.762
    Depth=0.030
    Weight=21.600
    NPieces=100
    PriceDate=10/05/16 10:41
    Currency=€
    Remarks, Count=6
      Str_1=- All measurements and PAN file creation have been
      Str_2=completed by T¨¹V NORD
      Str_3=information.
      Str_4=Anodized aluminium alloy
      Str_5=1.6mm Glass / Encapsulation / 1.6mm Glass
      Str_6=Jbox IP 68, 3 diodes
    End of Remarks=Jbox IP 68, 3 diodes
  End of PVObject pvCommercial

  Technol=mtSiMono
  NCelS=48
  NCelP=2
  NDiode=3
  SubModuleLayout=slTwinHalfCells
  FrontSurface=fsARCoating
  GRef=1000
  TRef=25.0
  PNom=460.0
  PNomTolLow=0.00
  PNomTolUp=3.00
  BifacialityFactor=0.000
  Isc=16.220
  Voc=35.68
  Imp=15.130
  Vmp=30.41
  muISC=7.15
  muVocSpec=-85.5
  muPmpReq=-0.274
  RShunt=500
  Rp_0=2000
  Rp_Exp=5.50
  RSerie=0.111
  Gamma=1.057
  muGamma=-0.0002
  VMaxIEC=1500
  Absorb=0.90
  ARev=3.200
  BRev=11.400
  RDiode=0.010
  VRevDiode=-0.70
  AirMassRef=1.500
  CellWidth=0.182
  CellHeight=0.105
  SandiaAMCorr=50.000
  RelEffic800=-0.31
  RelEffic600=-0.68
  RelEffic400=-1.31
  RelEffic200=-1.97

  PVObject_IAM=pvIAM
    Flags=$00
    IAMMode=UserProfile
    IAMProfile=TCubicProfile
      NPtsMax=9
      NPtsEff=9
      LastCompile=$008D
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
    Point_1=False,100,25.0,-4.77,0.00,0.000,0.000,0.00,43.50
    Point_2=False,200,25.0,-1.97,0.00,0.000,0.000,0.00,89.56
    Point_3=False,400,25.0,-1.31,0.00,0.000,0.000,0.00,180.32
    Point_4=False,600,25.0,-0.68,0.00,0.000,0.000,0.00,272.21
    Point_5=False,800,25.0,-0.31,0.00,0.000,0.000,0.00,364.29
    Point_6=True,1000,25.0,0.00,35.68,16.220,15.130,30.41,460.10
    Point_7=False,1100,25.0,0.10,0.00,0.000,0.000,0.00,502.96
  End of List OperPoints
End of PVObject pvModule
