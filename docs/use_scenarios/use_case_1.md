## Nazwa
**Wstawienie pliku do systemu**

## Aktor główny
Użytkownik

## Aktor pomocniczy
Klasa obsługująca linię poleceń

## Opis
Użytkownik przesyła do systemu wybrany plik, wybiera docelowy format i rozdzielczość, system poprzez odpowiedni status i komunikat powiadamia o wyniku operacji.

## Wyzwalacz
Użytkownik rozpoczyna przesyłanie pliku do systemu poprzez wpisanie odpowiedniego polecenia wraz z wymaganymi opcjami.

## Warunki początkowe
1. Użytkownik ma połączenie z serwerem nadzorczym.
2. Użytkownik wybiera plik wejściowy o właściwym rozszerzeniu
3. Użytkownik wybiera właściwe opcje konwersji

## Warunki końcowe
1. System jest w stanie przetworzyć żądanie konwersji

## Przepływ normalny
1. Użytkownik w linii poleceń uruchamia program.
2. Użytkownik wybiera wejściowy program do konwersji.
3. Użytkownik wybiera opcje konwersji.
4. System przetwarza żądanie.
5. System zwraca odpowiedź dot. statusu operacji załadowania pliku.

## Wyjątki
###### Plik wybrany przez użytkownika ma nieobsługiwany format lub za duży rozmiar
1. System informuje użytkownika, że format wybranego pliku jest nieobsługiwany lub że ma za duży rozmiar (komunikat błędu pokazuje dostępne formaty i maksymalny rozmiar pliku) i przerywa procedurę.
2. Użytkownik może wybrać inny plik.

###### Użytkownik wpisuje za duże albo za małe wartości rozdzielczości docelowej
1. System informuje użytkownika, że rozdzielczość docelowa jest nieprawidłowa (komunikat błędu pokazuje przedziały, w jakich musi się zawrzeć rozdzielczość).
2. Użytkownik może wpisać inne wartości rozdzielczości.

###### Użytkownik przerywa pracę z systemem w czasie przetwarzania
1. Następuje czyszczenie zawartości programu. Program kończy swoje działanie.
###### Błąd systemu
1. System informuje użytkownika o błędzie i prosi o ponowienie próby za kilka minut.
