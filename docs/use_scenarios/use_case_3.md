## Nazwa
**Scalenie skonwertowanych części plików**

## Aktor główny
Serwer

## Aktor pomocniczy
Worker

## Opis
Serwer po otrzymaniu komunikatu o gotowości Workera do wysłania pliku po konwersji przyjmuje pliki i scala je w jedną całość.

## Wyzwalacz
Komunikat od poszczególnych węzłów rozproszonych.

## Warunki początkowe
1. Serwer ma połączenie ze zdalnymi węzłami.
2. Każdy z węzłów zakończył konwersję przydzielonej mu części pliku.

## Warunki końcowe
1. System jest w stanie scalić gotowy plik po konwersji

## Przepływ normalny
1. Serwer w trybie nasłuchiwania oczekuje na komunikaty od zdalnych węzłów.
2. Po otrzymaniu komunikatu przyjmuje porcję danych od każdego z węzłów.
3. Dane przechowywane są w nowym archiwum.
4. System scala wszystkie otrzymane pliki.
5. System zwraca odpowiedź dot. statusu operacji do użytkownika

## Wyjątki
###### Nie ma połączenia z którymś z węzłów
1. System informuje użytkownika, że ze względu na błąd połaczenia sieciowego nie jest w stanie przeprowadzić konwersji
2. Po upłynięciu ustalonego timeout, w którym sprawdzana jest możliwość połączenia, program kończy działanie
###### Użytkownik przerywa pracę z systemem w czasie przetwarzania
1. Następuje czyszczenie zawartości programu. Program kończy swoje działanie.
###### Błąd systemu
1. System informuje użytkownika o błędzie i prosi o ponowienie próby za kilka minut.
