#!/bin/bash

# Ellenőrzi, hogy az ffmpeg és ffprobe telepítve van-e
if ! command -v ffmpeg &> /dev/null || ! command -v ffprobe &> /dev/null
then
    echo "Az ffmpeg vagy ffprobe nem található. Kérlek, telepítsd!"
    echo "macOS rendszeren Homebrew-val: brew install ffmpeg"
    exit 1
fi

# Ellenőrzi, hogy meg lett-e adva bemeneti fájl
if [ -z "$1" ]; then
    echo "Használat: $0 <fájl> [kezdő_sorszám] [szünet_hossza] [zajszint_dB]"
    exit 1
fi

INPUT_FILE="$1"
START_NUM=${2:-1} # A második paraméter a kezdő sorszám, alapértelmezett értéke 1
SILENCE_DURATION=${3:-4} # Harmadik paraméter a szünet hossza, alapértelmezett értéke 4 mp
NOISE_LEVEL_DB=${4:--30} # Negyedik paraméter a zajszint dB-ben, alapértelmezett: -30dB

# Ellenőrzi, hogy a kezdő sorszám érvényes szám-e
if ! [[ "$START_NUM" =~ ^[0-9]+$ ]]; then
    echo "Hiba: A kezdő sorszámnak egy pozitív egész számnak kell lennie."
    echo "Használat: $0 <fájl> [kezdő_sorszám] [szünet_hossza] [zajszint_dB]"
    exit 1
fi

# Ellenőrzi, hogy a szünet hossza érvényes szám-e
if ! [[ "$SILENCE_DURATION" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    echo "Hiba: A szünet hosszának egy számnak kell lennie (pl. 4 vagy 2.5)."
    echo "Használat: $0 <fájl> [kezdő_sorszám] [szünet_hossza] [zajszint_dB]"
    exit 1
fi

# Ellenőrzi, hogy a zajszint érvényes-e (negatív szám)
if ! [[ "$NOISE_LEVEL_DB" =~ ^-[0-9]+$ ]]; then
    echo "Hiba: A zajszintnek egy negatív egész számnak kell lennie (pl. -30)."
    echo "Használat: $0 <fájl> [kezdő_sorszám] [szünet_hossza] [zajszint_dB]"
    exit 1
fi

BASENAME=$(basename -- "$INPUT_FILE")
FILENAME="${BASENAME%.*}"
OUTPUT_DIR="output_${FILENAME}"

mkdir -p "$OUTPUT_DIR"

echo "Szünetek keresése a(z) '$INPUT_FILE' fájlban (${SILENCE_DURATION}mp vagy hosszabb, ${NOISE_LEVEL_DB}dB hangerő alatt)..."

# A teljes hangfájl hosszának lekérdezése másodpercben
TOTAL_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$INPUT_FILE")

# A csendes részek kezdeti és végpontjainak kinyerése
# A -nostats kapcsoló elnyomja a folyamatjelzőt, ami megzavarhatja a kimenet feldolgozását
SILENCE_INFO=$(ffmpeg -nostats -i "$INPUT_FILE" -af silencedetect=noise=${NOISE_LEVEL_DB}dB:d=$SILENCE_DURATION -f null - 2>&1)

# Robusztus módszer a csendek időpontjainak beolvasására (while read ciklussal)
SILENCE_STARTS=()
while read -r timestamp; do
    [[ -n "$timestamp" ]] && SILENCE_STARTS+=("$timestamp")
done < <(echo "$SILENCE_INFO" | grep 'silence_start' | awk '{print $5}')

SILENCE_ENDS=()
while read -r timestamp; do
    [[ -n "$timestamp" ]] && SILENCE_ENDS+=("$timestamp")
done < <(echo "$SILENCE_INFO" | grep 'silence_end' | awk '{print $5}')

# Ellenőrzi, hogy a csendek száma megegyezik-e. Ha a fájl csenddel végződik, a legutolsó 'start' jelet figyelmen kívül hagyja.
if [ ${#SILENCE_STARTS[@]} -ne ${#SILENCE_ENDS[@]} ]; then
    if [ ${#SILENCE_STARTS[@]} -gt ${#SILENCE_ENDS[@]} ]; then
        echo "Figyelem: A fájl valószínűleg csenddel végződik. Az utolsó, befejezetlen szünetet a szkript figyelmen kívül hagyja."
        # Kompatibilis módja az utolsó elem törlésének
        unset 'SILENCE_STARTS[${#SILENCE_STARTS[@]}-1]'
    else
        # Ez az ág nem valószínű, de biztonsági okokból itt van
        echo "Hiba: A csend-detektálás váratlan eredményt adott (${#SILENCE_STARTS[@]} start vs ${#SILENCE_ENDS[@]} end). Kilépés."
        exit 1
    fi
fi

# Kezeli az esetet, ha nincsenek szünetek
if [ ${#SILENCE_ENDS[@]} -eq 0 ]; then
    echo "Nem található ${SILENCE_DURATION} másodperces vagy hosszabb szünet."
    echo "A teljes fájl konvertálása MP3 formátumba."
    ffmpeg -i "$INPUT_FILE" -c:a libmp3lame -b:a 192k "${OUTPUT_DIR}/${START_NUM}.mp3" -y -hide_banner -loglevel error
    exit 0
fi

PART_NUM=$START_NUM

# Új logika: A hanganyagokat a csendek KÖZÖTT keresi.
# Ez feltételezi, hogy a fájl csenddel indul, és a hangblokkok a szünetek között vannak.
for (( i=0; i<${#SILENCE_ENDS[@]}-1; i++ )); do
    SEGMENT_START=${SILENCE_ENDS[$i]}
    SEGMENT_END=${SILENCE_STARTS[$i+1]}

    # Csak akkor exportál, ha a két időpont között van érdemi hanganyag (legalább 0.1 mp)
    if (( $(echo "$SEGMENT_END > $SEGMENT_START + 0.1" | bc -l) )); then
        echo "$PART_NUM. rész exportálása MP3-ként: $SEGMENT_START -> $SEGMENT_END"
        ffmpeg -i "$INPUT_FILE" -ss "$SEGMENT_START" -to "$SEGMENT_END" -c:a libmp3lame -b:a 192k "${OUTPUT_DIR}/${PART_NUM}.mp3" -y -hide_banner -loglevel error
        ((PART_NUM++))
    fi
done

# Az utolsó, szünet utáni hangrész ellenőrzése (kompatibilis módon)
LAST_SILENCE_END_INDEX=$((${#SILENCE_ENDS[@]} - 1))
if [ "$LAST_SILENCE_END_INDEX" -ge 0 ]; then
    LAST_SILENCE_END=${SILENCE_ENDS[$LAST_SILENCE_END_INDEX]}
    if (( $(echo "$TOTAL_DURATION > $LAST_SILENCE_END + 0.1" | bc -l) )); then
        echo "Utolsó, $PART_NUM. rész exportálása MP3-ként: $LAST_SILENCE_END -> végéig"
        ffmpeg -i "$INPUT_FILE" -ss "$LAST_SILENCE_END" -c:a libmp3lame -b:a 192k "${OUTPUT_DIR}/${PART_NUM}.mp3" -y -hide_banner -loglevel error
    fi
fi

echo "Kész. A feldarabolt fájlok a(z) '$OUTPUT_DIR' könyvtárban találhatóak."
