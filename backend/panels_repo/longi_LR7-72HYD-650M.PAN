PVObject_=pvModule
  Version=7.2.4
  Flags=$00900043

  PVObject_Commercial=pvCommercial
    Comment=http//en.longi-solar.com   (China)
    Flags=$0041
    Manufacturer=LONGi solar
    Model=LR7-72HYD-650M
    DataSource=TüV SüD
    YearBeg=2024
    Width=1.134
    Height=2.382
    Depth=0.030
    Weight=33.500
    NPieces=100
    PriceDate=14/06/24 11:12
    Remarks, Count=4
      Str_1=Frame: Aluminum
      Str_2=Structure: Tempered AR glass
      Str_3=Connections: Doubleglass, Jbox IP 68, MC4 or mateable
      Str_4=N type, Bifacial, Half cut.
    End of Remarks=N type, Bifacial, Half cut.
  End of PVObject pvCommercial

  Technol=mtSiMono
  NCelS=72
  NCelP=2
  NDiode=3
  SubModuleLayout=slTwinHalfCells
  FrontSurface=fsARCoating
  GRef=1000
  TRef=25.0
  PNom=650.0
  PNomTolLow=0.00
  PNomTolUp=3.00
  BifacialityFactor=0.700
  Isc=15.140
  Voc=54.22
  Imp=14.490
  Vmp=44.87
  muISC=7.57
  muVocSpec=-109.0
  muPmpReq=-0.260
  RShunt=345
  Rp_0=15600
  Rp_Exp=4.50
  RSerie=0.185
  Gamma=1.073
  muGamma=-0.0002
  VMaxIEC=1500
  VMaxUL=1500
  Absorb=0.90
  ARev=3.200
  BRev=3.200
  RDiode=0.010
  VRevDiode=-0.70
  AirMassRef=1.500
  CellWidth=0.1822
  CellHeight=0.0958
  CellArea=174.5
  SandiaAMCorr=50.000
  RelEffic800=0.34
  RelEffic600=0.48
  RelEffic400=0.16
  RelEffic200=-1.57

  PVObject_IAM=pvIAM
    Flags=$00
    IAMMode=UserProfile
    IAMProfile=TCubicProfile
      NPtsMax=9
      NPtsEff=9
      LastCompile=$B18D
      Mode=3
      Point_1=0.0,1.00000
      Point_2=50.0,1.00000
      Point_3=60.0,1.00000
      Point_4=65.0,0.99000
      Point_5=70.0,0.96000
      Point_6=75.0,0.91000
      Point_7=80.0,0.84000
      Point_8=85.0,0.68000
      Point_9=90.0,0.00000
    End of TCubicProfile
  End of PVObject pvIAM

  OperPoints, list of=7 tOperPoint
    Point_1=False,100,25.0,-4.32,0.00,0.000,0.000,0.00
    Point_2=False,200,25.0,-1.57,0.00,0.000,0.000,0.00
    Point_3=False,400,25.0,0.16,0.00,0.000,0.000,0.00
    Point_4=False,600,25.0,0.48,0.00,0.000,0.000,0.00
    Point_5=False,800,25.0,0.34,0.00,0.000,0.000,0.00
    Point_6=False,1000,25.0,0.00,0.00,0.000,0.000,0.00
    Point_7=False,1100,25.0,-0.44,0.00,0.000,0.000,0.00
  End of List OperPoints
End of PVObject pvModule
