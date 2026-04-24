PVObject_=pvModule
  Version=7.4
  Flags=$00108743

  PVObject_Commercial=pvCommercial
    Comment=https://www.longi.com/en/
    Flags=$0041
    Manufacturer=Longi Solar
    Model=LR5-72HTH-600M
    DataSource=Manufacturer 2023
    YearBeg=2023
    Width=1.134
    Height=2.278
    Depth=0.035
    Weight=27.500
    NPieces=100
    PriceDate=08/11/24 17:46
    Remarks, Count=5
      Str_1=??: Aluminum
      Str_2=??: Tempered AR glass
      Str_3=??: Glass-Foil, Jbox IP 68, MC4 EVO2 or mateable
      Str_4=HPBC Half-Cut
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
  PNom=600.0
  PNomTolLow=0.00
  PNomTolUp=3.00
  BifacialityFactor=0.000
  Isc=14.460
  Voc=52.81
  Imp=13.440
  Vmp=44.66
  muISC=7.23
  muVocSpec=-121.5
  muPmpReq=-0.290
  RShunt=400
  Rp_0=1600
  Rp_Exp=5.50
  RSerie=0.209
  Gamma=1.048
  muGamma=-0.0003
  VMaxIEC=1500
  VMaxUL=1500
  Absorb=0.90
  ARev=3.200
  BRev=3.200
  RDiode=0.010
  VRevDiode=-0.70
  AirMassRef=1.500
  CellWidth=0.182
  CellHeight=0.091
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
      Point_2=30.0,0.99892
      Point_3=50.0,0.98708
      Point_4=60.0,0.96244
      Point_5=70.0,0.89222
      Point_6=75.0,0.81569
      Point_7=80.0,0.68108
      Point_8=85.0,0.44008
      Point_9=90.0,0.00000
    End of TCubicProfile
  End of PVObject pvIAM
End of PVObject pvModule
