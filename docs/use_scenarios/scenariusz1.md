## Nazwa
**Przekonwertuj plik video do żądanego formatu i rozdzielczości**

## Opis
Użytkownik przesyła do systemu wybrany plik, wybiera docelowy format i rozdzielczość, po czym system dokonuje konwersji i udostępnia skonwertowany plik do pobrania. Na koniec użytkownik pobiera plik.

## Wyzwalacz
Użytkownik rozpoczyna przesyłanie pliku do systemu.

## Warunki początkowe
1. Użytkownik ma połączenie z serwerem nadzorczym.

## Warunki końcowe
1. Użytkownik pobrał skonwertowany plik.

## Przepływ normalny
1. Użytkownik wybiera plik i przesyła go do systemu.
2. Po zakończeniu przesyłania użytkownik wybiera z listy rozwijanej format docelowy oraz wpisuje w pola tekstowe rozdzielczość docelową (dwie wartości - wysokość i szerokość), po czym zatwierdza wybór.
3. System konwertuje plik do żądanego formatu i rozdzielczości.
4. System udostępnia skonwertowany plik do pobrania użytkownikowi.
5. Użytkownik pobiera skonwertowany plik.

## Wyjątki
###### Plik wybrany przez użytkownika ma nieobsługiwany format lub za duży rozmiar
1. System informuje użytkownika, że format wybranego pliku jest nieobsługiwany lub że ma za duży rozmiar (komunikat błędu pokazuje dostępne formaty i maksymalny rozmiar pliku) i przerywa procedurę.
2. Użytkownik może wybrać inny plik.

###### Użytkownik wpisuje za duże albo za małe wartości rozdzielczości docelowej
1. System informuje użytkownika, że rozdzielczość docelowa jest nieprawidłowa (komunikat błędu pokazuje przedziały, w jakich musi się zawrzeć rozdzielczość).
2. Użytkownik może wpisać inne wartości rozdzielczości.

###### Użytkownik przerywa pracę z systemem przed pobraniem skonwertowanego pliku
1. Przesłany przez użytkownika plik, jak również plik skonwertowany - o ile konwersja miała miejsce - są usuwane z systemu.

###### Błąd systemu
1. System informuje użytkownika o błędzie i prosi o ponowienie próby za kilka minut.