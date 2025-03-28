import streamlit as st  # Importuje bibliotekę Streamlit, która służy do tworzenia interaktywnych aplikacji webowych w Pythonie.
import pandas as pd  # Importuje bibliotekę Pandas do manipulacji i analizy danych w formie tabelarycznej (DataFrame).

st.set_page_config(page_title="Analiza ryzyka", layout="wide")  # Ustawia konfigurację strony: tytuł w przeglądarce i szeroki układ interfejsu.
st.title("🔐 Analiza ryzyka systemów teleinformatycznych")  # Wyświetla główny nagłówek aplikacji z ikoną kłódki.

# Funkcja klasyfikująca poziom ryzyka
def klasyfikuj_ryzyko(poziom):  # Definiuje funkcję, która przyjmuje poziom ryzyka jako argument i klasyfikuje go.
    if poziom <= 6:  # Jeśli poziom ryzyka jest mniejszy lub równy 6, zwraca "Niskie".
        return "Niskie"
    elif poziom <= 14:  # Jeśli poziom ryzyka jest między 7 a 14, zwraca "Średnie".
        return "Średnie"
    else:  # Jeśli poziom ryzyka przekracza 14, zwraca "Wysokie".
        return "Wysokie"

# Domyślna lista zagrożeń
default_risks = [  # Tworzy listę słowników z domyślnymi zagrożeniami, każde z nazwą, prawdopodobieństwem i wpływem.
    {"Zagrożenie": "Awaria serwera", "Prawdopodobieństwo": 4, "Wpływ": 5},  # Przykład zagrożenia 1.
    {"Zagrożenie": "Atak DDoS", "Prawdopodobieństwo": 3, "Wpływ": 4},  # Przykład zagrożenia 2.
    {"Zagrożenie": "Błąd ludzki", "Prawdopodobieństwo": 5, "Wpływ": 3},  # Przykład zagrożenia 3.
    {"Zagrożenie": "Utrata zasilania", "Prawdopodobieństwo": 2, "Wpływ": 2}  # Przykład zagrożenia 4.
]

# Wczytanie danych do sesji
if "df" not in st.session_state:  # Sprawdza, czy w stanie sesji (pamięci aplikacji) istnieje klucz "df".
    st.session_state.df = pd.DataFrame(default_risks)  # Jeśli nie istnieje, tworzy DataFrame z domyślnymi zagrożeniami i zapisuje go w sesji.

# ➕ Dodawanie nowego ryzyka
st.subheader("➕ Dodaj nowe zagrożenie")  # Wyświetla podnagłówek sekcji do dodawania nowych zagrożeń.
with st.form("add_risk_form"):  # Tworzy formularz o nazwie "add_risk_form" do wprowadzania danych.
    name = st.text_input("Opis zagrożenia")  # Pole tekstowe do wpisania opisu zagrożenia.
    prob = st.slider("Prawdopodobieństwo (1-5)", 1, 5, 3)  # Suwak do wyboru prawdopodobieństwa od 1 do 5, domyślnie 3.
    impact = st.slider("Wpływ (1-5)", 1, 5, 3)  # Suwak do wyboru wpływu od 1 do 5, domyślnie 3.
    submitted = st.form_submit_button("Dodaj")  # Przycisk do zatwierdzenia formularza.

    if submitted and name.strip() != "":  # Jeśli formularz zatwierdzony i pole opisu nie jest puste po usunięciu białych znaków:
        new_row = {"Zagrożenie": name, "Prawdopodobieństwo": prob, "Wpływ": impact}  # Tworzy nowy słownik z danymi zagrożenia.
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)  # Dodaje nowy wiersz do DataFrame w sesji, resetując indeksy.
        st.success("Zagrożenie dodane.")  # Wyświetla komunikat o powodzeniu.

# ✏️ Edytuj ryzyka w interaktywnej tabeli
st.subheader("✏️ Edytuj macierz ryzyka")  # Wyświetla podnagłówek sekcji edycji macierzy ryzyka.
edited_df = st.data_editor(  # Tworzy interaktywną tabelę do edycji danych z DataFrame.
    st.session_state.df,  # Przekazuje aktualny DataFrame z sesji do edycji.
    num_rows="dynamic",  # Pozwala na dynamiczną zmianę liczby wierszy (dodawanie/usuwanie).
    use_container_width=True,  # Rozciąga tabelę na całą szerokość kontenera.
    key="risk_editor"  # Unikalny klucz dla tego komponentu.
)

# Zapisz zmodyfikowaną tabelę do sesji
st.session_state.df = edited_df.copy()  # Aktualizuje DataFrame w sesji na podstawie edytowanej wersji.

# Oblicz poziom ryzyka i klasyfikację
edited_df["Poziom ryzyka"] = edited_df["Prawdopodobieństwo"] * edited_df["Wpływ"]  # Dodaje kolumnę "Poziom ryzyka" jako iloczyn prawdopodobieństwa i wpływu.
edited_df["Klasyfikacja"] = edited_df["Poziom ryzyka"].apply(klasyfikuj_ryzyko)  # Dodaje kolumnę "Klasyfikacja", stosując funkcję klasyfikuj_ryzyko do "Poziom ryzyka".

# 📋 Filtrowanie
st.subheader("📋 Filtruj według poziomu ryzyka")  # Wyświetla podnagłówek sekcji filtrowania.
filt = st.radio("Pokaż:", ["Wszystkie", "Niskie", "Średnie", "Wysokie"], horizontal=True)  # Tworzy przełącznik radiowy do wyboru filtra, wyświetlany poziomo.

if filt != "Wszystkie":  # Jeśli wybrano filtr inny niż "Wszystkie":
    df_filtered = edited_df[edited_df["Klasyfikacja"] == filt]  # Filtruje DataFrame, pokazując tylko wiersze z wybraną klasyfikacją.
else:  # W przeciwnym razie:
    df_filtered = edited_df  # Pokazuje cały edytowany DataFrame bez filtrowania.

# 🎨 Kolorowanie
def koloruj(val):  # Definiuje funkcję do kolorowania komórek w tabeli na podstawie wartości.
    if val == "Niskie":  # Jeśli wartość to "Niskie", ustawia zielone tło.
        return "background-color: #d4edda"
    elif val == "Średnie":  # Jeśli wartość to "Średnie", ustawia żółte tło.
        return "background-color: #fff3cd"
    elif val == "Wysokie":  # Jeśli wartość to "Wysokie", ustawia czerwone tło.
        return "background-color: #f8d7da"
    return ""  # Dla innych wartości nie stosuje koloru.

# 📊 Wyświetlenie
st.subheader("📊 Macierz ryzyka")  # Wyświetla podnagłówek sekcji z finalną tabelą.
st.dataframe(  # Wyświetla DataFrame jako tabelę w interfejsie Streamlit.
    df_filtered.style.applymap(koloruj, subset=["Klasyfikacja"]),  # Stosuje funkcję koloruj tylko do kolumny "Klasyfikacja".
    use_container_width=True  # Rozciąga tabelę na całą szerokość kontenera.
)