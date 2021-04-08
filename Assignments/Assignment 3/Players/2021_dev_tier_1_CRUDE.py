# -? "CRUDE"
def start ():
	return "ll1l1l1l1llll1l1lll1",{}
def ll1l1l1l1llll1l1lll1 ():
	if get_if_have_weapon ():
		return "ll1l1l111lll111lll11",{"ACLT_X":0 ,"ACLT_Y":0 }
	else :
		O000O0OOO00O00O00 =[]
		for OO00OO00OO00O00O0 in range (0 ,360 ,1 ):
			(O00OO00O0O0O00000 ,OO000O00O0OOOOO00 ,_O000OO00O00OO0OOO )=get_the_radar_data (OO00OO00OO00O00O0 )
			if O00OO00O0O0O00000 =='weapon':
				O000O0OOO00O00O00 .append ((OO000O00O0OOOOO00 ,OO00OO00OO00O00O0 ))
		if len (O000O0OOO00O00O00 )==0 :
			if randint (1 ,10 )==1 :
				return "ll1l1l1l1llll1l1lll1",{"WEAPON":True ,"ACLT_X":randint (-1 ,1 ),"ACLT_Y":randint (-1 ,1 )}
			else :
				return "ll1l1l1l1llll1l1lll1",{"WEAPON":True }
		else :
			O000O0OOO00O00O00 .sort ()
			OO00OO00OO00O00O0 =O000O0OOO00O00O00 [0 ][1 ]
			return "ll1l1l1l1llll1l1lll1",{"WEAPON":True ,"ACLT_X":(cos (radians (OO00OO00OO00O00O0 ))),"ACLT_Y":(sin (radians (OO00OO00OO00O00O0 )))}
def ll1l1l111lll111lll11 ():
	for O000O0O000OO0O0O0 in range (0 ,360 ,1 ):
		(O00OOO0O00O000OOO ,OOO00O0O0O00O0OO0 ,_OO000O0000OO000O0 )=get_the_radar_data (O000O0O000OO0O0O0 )
		if O00OOO0O00O000OOO =='player':
			if OOO00O0O0O00O0OO0 <200 :
				return "l1l1l1l11l1lll1111ll",{"ACLT_X":0 ,"ACLT_Y":0 }
			else :
				return "ll1l1l111lll111lll11",{"ACLT_X":(cos (radians (O000O0O000OO0O0O0 ))),"ACLT_Y":(sin (radians (O000O0O000OO0O0O0 )))}
	if randint (1 ,10 )==1 :
		return "ll1l1l111lll111lll11",{"ACLT_X":randint (-1 ,1 ),"ACLT_Y":randint (-1 ,1 )}
	else :
		return "ll1l1l111lll111lll11",{}
def l1l1l1l11l1lll1111ll ():
	for OO0O0OOO0O00OOOO0 in range (0 ,360 ,1 ):
		(O000OOO0000O00OOO ,O0O00OOOOOO0OO0OO ,_O0OO0OOO0000OO0OO )=get_the_radar_data (OO0O0OOO0O00OOOO0 )
		if O000OOO0000O00OOO =='player':
			O00OOO00O0O00OOO0 =get_throwing_angle ()
			OOOOO0OOO0O00OOOO =((OO0O0OOO0O00OOOO0 -O00OOO00O0O00OOO0 )+360 )%360 
			if OOOOO0OOO0O00OOOO <1 or OOOOO0OOO0O00OOOO >359 :
				return "ll1l1l1l1llll1l1lll1",{"WEAPON":False }
			elif OOOOO0OOO0O00OOOO >180 :
				O000OOOOO0OO0O0O0 =0 
				OOO0000O000OOO0O0 =1 
			else :
				O000OOOOO0OO0O0O0 =1 
				OOO0000O000OOO0O0 =0 
			return "l1l1l1l11l1lll1111ll",{"ROT_CC":O000OOOOO0OO0O0O0 ,"ROT_CW":OOO0000O000OOO0O0 }
	return "ll1l1l111lll111lll11",{}
