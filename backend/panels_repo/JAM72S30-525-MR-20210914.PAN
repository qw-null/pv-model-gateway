PVObject_=pvModule
  Version=7.1.8
  Flags=$00100043

  PVObject_Commercial=pvCommercial
    Comment=Shanghai JA Solar Technology Co., Ltd.
    Flags=$0041
    Manufacturer=JA Solar
    Model=JAM72S30-525/MR
    DataSource=TÜV SÜD Certification and Testing (China
    YearBeg=2020
    Width=1.134
    Height=2.278
    Depth=0.035
    Weight=28.600
    NPieces=100
    PriceDate=26/04/20 17:20
    Remarks, Count=5
      Str_1=Frame: Aluminum
      Str_2=Structure: 3.2 mm coating tempered glass
      Str_3=Connections: EVA/backsheet, Jbox
      Str_4
      Str_5
    End of Remarks
  End of PVObject pvCommercial

  Technol=mtSiMono
  NCelS=72
  NCelP=2
  NDiode=3
  SubModuleLayout=slTwinHalfCells
  FrontSurface=fsARCoating
  GRef=1000
  TRef=25.0
  PNom=525.0
  PNomTolLow=0.00
  PNomTolUp=0.95
  Isc=13.650
  Voc=49.15
  Imp=12.760
  Vmp=41.15
  muISC=5.87
  muVocSpec=-113.1
  muPmpReq=-0.348
  RShunt=350
  Rp_0=5200
  Rp_Exp=3.20
  RSerie=0.196
  Gamma=1.039
  muGamma=-0.0003
  VMaxIEC=1500
  VMaxUL=1500
  Absorb=0.90
  ARev=3.200
  BRev=11.496
  RDiode=0.010
  VRevDiode=-0.70
  AirMassRef=1.500
  CellArea=165.2
  SandiaAMCorr=50.000
  RelEffic800=0.29
  RelEffic600=0.04
  RelEffic400=-0.08
  RelEffic200=-1.89

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
      Point_3=50.0,1.00000
      Point_4=60.0,0.98300
      Point_5=70.0,0.94200
      Point_6=75.0,0.89800
      Point_7=80.0,0.84300
      Point_8=85.0,0.72900
      Point_9=90.0,0.00000
    End of TCubicProfile
  End of PVObject pvIAM

  OperPoints, list of=13 tOperPoint
    Point_1=False,100,15.0,1.41,0.00,0.000,0.000,0.00
    Point_2=False,200,15.0,1.49,0.00,0.000,0.000,0.00
    Point_3=False,400,15.0,3.41,0.00,0.000,0.000,0.00
    Point_4=False,600,15.0,3.63,0.00,0.000,0.000,0.00
    Point_5=False,800,15.0,3.59,0.00,0.000,0.000,0.00
    Point_6=False,1000,15.0,3.57,0.00,0.000,0.000,0.00
    Point_7=False,100,25.0,-1.83,0.00,0.000,0.000,0.00
    Point_8=False,200,25.0,-1.89,0.00,0.000,0.000,0.00
    Point_9=False,400,25.0,-0.08,0.00,0.000,0.000,0.00
    Point_10=False,600,25.0,0.04,0.00,0.000,0.000,0.00
    Point_11=False,800,25.0,0.29,0.00,0.000,0.000,0.00
    Point_12=False,1000,25.0,0.00,0.00,0.000,0.000,0.00
    Point_13=False,1100,25.0,-0.04,0.00,0.000,0.000,0.00
  End of List OperPoints
End of PVObject pvModule
