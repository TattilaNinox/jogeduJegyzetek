#!/bin/bash

# Diagnosztikai és daraboló szkript
# Először elemzi a fájlt és kiírja, hány darabot fog létrehozni, majd opcionálisan futtatja a darabolást

# Ellenőrzi, hogy az ffmpeg és ffprobe telepítve van-e
if ! command -v ffmpeg &> /dev/null || ! command -v ffprobe &> /dev/null
then
    echo "Az ffmpeg vagy ffprobe nem található. Kérlek, telepítsd!"
    echo "macOS rendszeren Homebrew-val: brew install ffmpeg"
    exit 1
fi

AUTO_MODE=false

# Ellenőrzi, hogy van-e --auto flag
if [[ "$*" == *"--auto"* ]]; then
    AUTO_MODE=true
fi

# Ha nincs megadva fájlnév, automatikusan az MP3 mappában lévő .webm fájlt keresi
if [ -z "$1" ] || [ ! -f "$1" ]; then
    # Keressük meg az MP3 mappában lévő .webm fájlt
    WEBM_FILES=(MP3/*.webm)
    
    if [ ! -e "${WEBM_FILES[0]}" ]; then
        echo "Hiba: Nem található .webm fájl az MP3 mappában."
        echo "Használat: $0 [fájl] [kezdő_sorszám] [szünet_hossza] [zajszint_dB] [--auto]"
        echo ""
        echo "Paraméterek:"
        echo "  [fájl]              - A feldolgozandó hangfájl (opcionális, ha nincs megadva, az MP3 mappában keresi)"
        echo "  [kezdő_sorszám]     - A fájlok sorszámozásának kezdete (alapértelmezett: 1)"
        echo "  [szünet_hossza]     - A szünet minimális hossza másodpercben (alapértelmezett: 4)"
        echo "  [zajszint_dB]       - A csend detektálás zajszintje dB-ben (alapértelmezett: -30)"
        echo "  [--auto]            - Ha megadva, automatikusan futtatja a darabolást jóváhagyás nélkül"
        echo ""
        echo "Példa:"
        echo "  $0                    # Automatikusan az MP3 mappában lévő fájlt dolgozza fel"
        echo "  $0 1 3 -20            # Automatikus fájlkeresés, egyedi beállításokkal"
        echo "  $0 fajl.webm 1 3 -20  # Fájlnév megadása"
        echo "  $0 1 3 -20 --auto     # Automatikus mód"
        exit 1
    fi
    
    # Ha több fájl van, jelezzük, de válasszuk ki az elsőt
    if [ ${#WEBM_FILES[@]} -gt 1 ]; then
        echo "Figyelem: Több .webm fájl található az MP3 mappában."
        echo "Az első fájlt használjuk: ${WEBM_FILES[0]}"
        echo ""
    fi
    
    INPUT_FILE="${WEBM_FILES[0]}"
    START_NUM=${1:-1}
    SILENCE_DURATION=${2:-4}
    NOISE_LEVEL_DB=${3:--30}
else
    INPUT_FILE="$1"
    START_NUM=${2:-1}
    SILENCE_DURATION=${3:-4}
    NOISE_LEVEL_DB=${4:--30}
fi

# Ellenőrzi, hogy a kezdő sorszám érvényes szám-e
if ! [[ "$START_NUM" =~ ^[0-9]+$ ]]; then
    echo "Hiba: A kezdő sorszámnak egy pozitív egész számnak kell lennie."
    exit 1
fi

# Ellenőrzi, hogy a szünet hossza érvényes szám-e
if ! [[ "$SILENCE_DURATION" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    echo "Hiba: A szünet hosszának egy számnak kell lennie (pl. 4 vagy 2.5)."
    exit 1
fi

# Ellenőrzi, hogy a zajszint érvényes-e (negatív szám)
if ! [[ "$NOISE_LEVEL_DB" =~ ^-[0-9]+$ ]]; then
    echo "Hiba: A zajszintnek egy negatív egész számnak kell lennie (pl. -30)."
    exit 1
fi

# Ellenőrzi, hogy a fájl létezik-e
if [ ! -f "$INPUT_FILE" ]; then
    echo "Hiba: A fájl nem található: $INPUT_FILE"
    exit 1
fi

echo "=========================================="
echo "  HANGFÁJL DIAGNOSZTIKA ÉS DARABOLÁS"
echo "=========================================="
echo ""
echo "Bemeneti fájl: $INPUT_FILE"
echo "Beállítások:"
echo "  - Kezdő sorszám: $START_NUM"
echo "  - Szünet hossza: ${SILENCE_DURATION} másodperc"
echo "  - Zajszint: ${NOISE_LEVEL_DB}dB"
echo ""

# A teljes hangfájl hosszának lekérdezése másodpercben
echo "Fájl elemzése..."
TOTAL_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$INPUT_FILE")
TOTAL_MINUTES=$(echo "scale=2; $TOTAL_DURATION / 60" | bc)
echo "  Teljes hossz: ${TOTAL_DURATION} másodperc (~${TOTAL_MINUTES} perc)"
echo ""

# A csendes részek kezdeti és végpontjainak kinyerése
SILENCE_INFO=$(ffmpeg -nostats -i "$INPUT_FILE" -af silencedetect=noise=${NOISE_LEVEL_DB}dB:d=$SILENCE_DURATION -f null - 2>&1)

# Robusztus módszer a csendek időpontjainak beolvasására
SILENCE_STARTS=()
while read -r timestamp; do
    [[ -n "$timestamp" ]] && SILENCE_STARTS+=("$timestamp")
done < <(echo "$SILENCE_INFO" | grep 'silence_start' | awk '{print $5}')

SILENCE_ENDS=()
while read -r timestamp; do
    [[ -n "$timestamp" ]] && SILENCE_ENDS+=("$timestamp")
done < <(echo "$SILENCE_INFO" | grep 'silence_end' | awk '{print $5}')

# Ellenőrzi, hogy a csendek száma megegyezik-e
if [ ${#SILENCE_STARTS[@]} -ne ${#SILENCE_ENDS[@]} ]; then
    if [ ${#SILENCE_STARTS[@]} -gt ${#SILENCE_ENDS[@]} ]; then
        echo "Figyelem: A fájl valószínűleg csenddel végződik."
        unset 'SILENCE_STARTS[${#SILENCE_STARTS[@]}-1]'
    else
        echo "Hiba: A csend-detektálás váratlan eredményt adott."
        exit 1
    fi
fi

NUM_SILENCES=${#SILENCE_ENDS[@]}
EXPECTED_SEGMENTS=$NUM_SILENCES

# Számoljuk meg, hány hangblokk lesz (a szünetek közötti részek)
if [ $NUM_SILENCES -eq 0 ]; then
    EXPECTED_SEGMENTS=1
    echo "=========================================="
    echo "  DIAGNOSZTIKA EREDMÉNYE"
    echo "=========================================="
    echo "  ❌ Nem található ${SILENCE_DURATION} másodperces vagy hosszabb szünet."
    echo "  ℹ️  A teljes fájl egyetlen MP3 fájlként lesz konvertálva."
    echo ""
else
    # Ha a fájl csenddel végződik, akkor az utolsó szünet után nincs több hanganyag
    LAST_SILENCE_END_INDEX=$((${#SILENCE_ENDS[@]} - 1))
    LAST_SILENCE_END=${SILENCE_ENDS[$LAST_SILENCE_END_INDEX]}
    
    # Ellenőrizzük, van-e hanganyag az utolsó szünet után
    HAS_LAST_SEGMENT=false
    if (( $(echo "$TOTAL_DURATION > $LAST_SILENCE_END + 0.1" | bc -l) )); then
        HAS_LAST_SEGMENT=true
        EXPECTED_SEGMENTS=$((NUM_SILENCES + 1))
    fi
    
    echo "=========================================="
    echo "  DIAGNOSZTIKA EREDMÉNYE"
    echo "=========================================="
    echo "  ✅ Talált szünetek száma: $NUM_SILENCES"
    
    if [ "$HAS_LAST_SEGMENT" = true ]; then
        echo "  ✅ Az utolsó szünet után van még hanganyag"
        echo "  📊 Összesen $EXPECTED_SEGMENTS darab MP3 fájl jön létre"
        echo "     (${NUM_SILENCES} szünet között + 1 utolsó rész)"
    else
        echo "  ✅ Az utolsó szünet után nincs több hanganyag"
        echo "  📊 Összesen $EXPECTED_SEGMENTS darab MP3 fájl jön létre"
        echo "     (${NUM_SILENCES} szünet között)"
    fi
    
    # Megjelenítjük az első pár szünet időpontját
    echo ""
    echo "  Előnézet (első 3 szünet):"
    for (( i=0; i<3 && i<${#SILENCE_ENDS[@]}; i++ )); do
        if [ $i -lt $((${#SILENCE_ENDS[@]} - 1)) ]; then
            START=${SILENCE_ENDS[$i]}
            END=${SILENCE_STARTS[$i+1]}
            DURATION=$(echo "scale=2; $END - $START" | bc)
            echo "     Blokk $((i+1)): ${START}s -> ${END}s (hossz: ~${DURATION}s)"
        fi
    done
    if [ ${#SILENCE_ENDS[@]} -gt 3 ]; then
        echo "     ..."
    fi
fi

echo ""

# Ha nincs auto mód, kérdezzen rá
if [ "$AUTO_MODE" = false ]; then
    echo "Folytassuk a darabolást? (i/n)"
    read -r answer
    if [[ ! "$answer" =~ ^[Ii]$ ]]; then
        echo "Darabolás megszakítva."
        exit 0
    fi
    echo ""
fi

# Darabolás futtatása
echo "=========================================="
echo "  DARABOLÁS INDÍTÁSA"
echo "=========================================="
echo ""

BASENAME=$(basename -- "$INPUT_FILE")
FILENAME="${BASENAME%.*}"
OUTPUT_DIR="output_${FILENAME}"

mkdir -p "$OUTPUT_DIR"

echo "Szünetek keresése a(z) '$INPUT_FILE' fájlban (${SILENCE_DURATION}mp vagy hosszabb, ${NOISE_LEVEL_DB}dB hangerő alatt)..."

# Kezeli az esetet, ha nincsenek szünetek
if [ ${#SILENCE_ENDS[@]} -eq 0 ]; then
    echo "A teljes fájl konvertálása MP3 formátumba."
    ffmpeg -i "$INPUT_FILE" -c:a libmp3lame -b:a 192k "${OUTPUT_DIR}/${START_NUM}.mp3" -y -hide_banner -loglevel error
    echo ""
    echo "Kész. A fájl a(z) '${OUTPUT_DIR}/${START_NUM}.mp3' néven mentve."
    exit 0
fi

PART_NUM=$START_NUM

# Hanganyagok kivágása a csendek között
for (( i=0; i<${#SILENCE_ENDS[@]}-1; i++ )); do
    SEGMENT_START=${SILENCE_ENDS[$i]}
    SEGMENT_END=${SILENCE_STARTS[$i+1]}

    if (( $(echo "$SEGMENT_END > $SEGMENT_START + 0.1" | bc -l) )); then
        echo "$PART_NUM. rész exportálása MP3-ként: $SEGMENT_START -> $SEGMENT_END"
        ffmpeg -i "$INPUT_FILE" -ss "$SEGMENT_START" -to "$SEGMENT_END" -c:a libmp3lame -b:a 192k "${OUTPUT_DIR}/${PART_NUM}.mp3" -y -hide_banner -loglevel error
        ((PART_NUM++))
    fi
done

# Az utolsó, szünet utáni hangrész ellenőrzése
LAST_SILENCE_END_INDEX=$((${#SILENCE_ENDS[@]} - 1))
if [ "$LAST_SILENCE_END_INDEX" -ge 0 ]; then
    LAST_SILENCE_END=${SILENCE_ENDS[$LAST_SILENCE_END_INDEX]}
    if (( $(echo "$TOTAL_DURATION > $LAST_SILENCE_END + 0.1" | bc -l) )); then
        echo "Utolsó, $PART_NUM. rész exportálása MP3-ként: $LAST_SILENCE_END -> végéig"
        ffmpeg -i "$INPUT_FILE" -ss "$LAST_SILENCE_END" -c:a libmp3lame -b:a 192k "${OUTPUT_DIR}/${PART_NUM}.mp3" -y -hide_banner -loglevel error
    fi
fi

echo ""
echo "=========================================="
echo "  KÉSZ!"
echo "=========================================="
echo "A feldarabolt fájlok a(z) '$OUTPUT_DIR' könyvtárban találhatóak."
echo "Összesen $EXPECTED_SEGMENTS darab fájl készült."
