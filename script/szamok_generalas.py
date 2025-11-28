#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segédszkript a számok melléknévi alakjának generálásához
"""

def general_melleknevi_alakok(vegig=900):
    """Generálja az 1-től a megadott számig a melléknévi alakokat"""
    
    # Alap számok - melléknévi alakok
    egyesek = ['', 'első', 'második', 'harmadik', 'negyedik', 'ötödik', 'hatodik', 'hetedik', 'nyolcadik', 'kilencedik']
    egyesek_szam = ['', 'egy', 'kettő', 'három', 'négy', 'öt', 'hat', 'hét', 'nyolc', 'kilenc']
    tizesek = ['', '', 'huszadik', 'harmincadik', 'negyvenedik', 'ötvenedik', 'hatvanedik', 'hetvenedik', 'nyolcvanedik', 'kilencvenedik']
    tizesek_szam = ['', '', 'húsz', 'harminc', 'negyven', 'ötven', 'hatvan', 'hetven', 'nyolcvan', 'kilencven']
    
    szamok_melleknevi = {}
    
    for szam in range(1, min(vegig + 1, 100)):
        if szam < 10:
            szamok_melleknevi[str(szam)] = egyesek[szam]
        elif szam == 10:
            szamok_melleknevi['10'] = 'tizedik'
        elif szam < 20:
            if szam == 11:
                szamok_melleknevi['11'] = 'tizenegyedik'
            elif szam == 12:
                szamok_melleknevi['12'] = 'tizenkettedik'
            elif szam == 13:
                szamok_melleknevi['13'] = 'tizenharmadik'
            elif szam == 14:
                szamok_melleknevi['14'] = 'tizennegyedik'
            elif szam == 15:
                szamok_melleknevi['15'] = 'tizenötödik'
            elif szam == 16:
                szamok_melleknevi['16'] = 'tizenhatodik'
            elif szam == 17:
                szamok_melleknevi['17'] = 'tizenhetedik'
            elif szam == 18:
                szamok_melleknevi['18'] = 'tizennyolcadik'
            elif szam == 19:
                szamok_melleknevi['19'] = 'tizenkilencedik'
        elif szam < 100:
            tizes = szam // 10
            egyes = szam % 10
            
            if tizes == 2:
                prefix = 'huszon'
            elif tizes == 3:
                prefix = 'harminc'
            elif tizes == 4:
                prefix = 'negyven'
            elif tizes == 5:
                prefix = 'ötven'
            elif tizes == 6:
                prefix = 'hatvan'
            elif tizes == 7:
                prefix = 'hetven'
            elif tizes == 8:
                prefix = 'nyolcvan'
            elif tizes == 9:
                prefix = 'kilencven'
            
            if egyes == 0:
                szamok_melleknevi[str(szam)] = tizesek[tizes]
            else:
                # Különleges esetek összetett számoknál
                if egyes == 1:
                    egyes_str = 'egyedik'  # 21 = huszonegyedik (nem huszonelső)
                elif egyes == 2:
                    egyes_str = 'kettedik'  # 22 = huszonkettedik (nem huszonmásodik)
                else:
                    egyes_str = egyesek[egyes]  # 3, 4, 5, stb. normális
                szamok_melleknevi[str(szam)] = prefix + egyes_str
    
    # 100-900 közötti számok
    for szam in range(100, min(vegig + 1, 1000)):
        szam_str = str(szam)
        
        # Háromjegyű számok
        szazas = szam // 100
        tizes_egyes = szam % 100
        
        if szazas == 1:
            prefix = 'száz'
        elif szazas == 2:
            prefix = 'kétszáz'
        elif szazas == 3:
            prefix = 'háromszáz'
        elif szazas == 4:
            prefix = 'négyszáz'
        elif szazas == 5:
            prefix = 'ötszáz'
        elif szazas == 6:
            prefix = 'hatszáz'
        elif szazas == 7:
            prefix = 'hétszáz'
        elif szazas == 8:
            prefix = 'nyolcszáz'
        elif szazas == 9:
            prefix = 'kilencszáz'
        
        if tizes_egyes == 0:
            szamok_melleknevi[szam_str] = prefix + 'adik'
        else:
            # Kétjegyű rész kezelése
            if tizes_egyes < 20:
                if tizes_egyes == 1:
                    suffix = 'egyedik'
                elif tizes_egyes == 2:
                    suffix = 'kettedik'
                elif tizes_egyes == 3:
                    suffix = 'harmadik'
                elif tizes_egyes == 4:
                    suffix = 'negyedik'
                elif tizes_egyes == 5:
                    suffix = 'ötödik'
                elif tizes_egyes == 6:
                    suffix = 'hatodik'
                elif tizes_egyes == 7:
                    suffix = 'hetedik'
                elif tizes_egyes == 8:
                    suffix = 'nyolcadik'
                elif tizes_egyes == 9:
                    suffix = 'kilencedik'
                elif tizes_egyes == 10:
                    suffix = 'tizedik'
                elif tizes_egyes == 11:
                    suffix = 'tizenegyedik'
                elif tizes_egyes == 12:
                    suffix = 'tizenkettedik'
                elif tizes_egyes == 13:
                    suffix = 'tizenharmadik'
                elif tizes_egyes == 14:
                    suffix = 'tizennegyedik'
                elif tizes_egyes == 15:
                    suffix = 'tizenötödik'
                elif tizes_egyes == 16:
                    suffix = 'tizenhatodik'
                elif tizes_egyes == 17:
                    suffix = 'tizenhetedik'
                elif tizes_egyes == 18:
                    suffix = 'tizennyolcadik'
                elif tizes_egyes == 19:
                    suffix = 'tizenkilencedik'
            else:
                tizes = tizes_egyes // 10
                egyes = tizes_egyes % 10
                
                if tizes == 2:
                    tizes_prefix = 'huszon'
                elif tizes == 3:
                    tizes_prefix = 'harminc'
                elif tizes == 4:
                    tizes_prefix = 'negyven'
                elif tizes == 5:
                    tizes_prefix = 'ötven'
                elif tizes == 6:
                    tizes_prefix = 'hatvan'
                elif tizes == 7:
                    tizes_prefix = 'hetven'
                elif tizes == 8:
                    tizes_prefix = 'nyolcvan'
                elif tizes == 9:
                    tizes_prefix = 'kilencven'
                
                if egyes == 0:
                    suffix = tizesek[tizes]
                else:
                    # Különleges esetek
                    if egyes == 1:
                        suffix = tizes_prefix + 'egyedik'
                    elif egyes == 2:
                        suffix = tizes_prefix + 'kettedik'  # "második" helyett "kettedik"
                    else:
                        suffix = tizes_prefix + egyesek[egyes]
            
            szamok_melleknevi[szam_str] = prefix + suffix
    
    return szamok_melleknevi

if __name__ == '__main__':
    szamok = general_melleknevi_alakok(900)
    print("# Melléknévi alakok szótára (1-900)")
    print("szamok_melleknevi = {")
    for i, (szam, alak) in enumerate(sorted(szamok.items(), key=lambda x: int(x[0])), 1):
        print(f"    '{szam}': '{alak}',", end='')
        if i % 5 == 0:
            print()
    print("\n}")

