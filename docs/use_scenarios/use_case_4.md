## Nazwa
**Konwersja przesłanej części pliku **

## Aktor główny
Worker

## Aktor pomocniczy
Serwer

## Opis
Worker otrzymuje nowy plik na wewnętrzną kolejkę przetwarzania. Zapamiętane są adresy źródłowe oraz komenda, którą należy wykonać, aby skonwertować plik.

## Wyzwalacz
Otrzymanie fragmentu pliku od serwera centralnego

## Warunki początkowe
1. Węzeł ma połączenie z serwerem
2. Węzeł ma wolne miejsce w kolejce plików do konwersji.

## Warunki końcowe
1. Węzeł odsyła plik po konwersji do centralnego serwera

## Przepływ normalny
1. Węzeł otrzymuje komunikat z procedurą, którą należy wykonać do konwersji pliku
2. Węzeł otrzymuje część pliku przeznaczoną do konwersji
3. Węzeł wykonuje konwersję pliku przy pomocy gotowej metody
4. Węzeł wysyła komunikat o gotowości pliku do przesłania
5. Węzeł wysyła plik przy pomocy protokołu

## Wyjątki
###### Nie ma połączenia z serwerem
1. System informuje użytkownika, że ze względu na błąd połaczenia sieciowego nie jest w stanie przeprowadzić konwersji
2. Po upłynięciu ustalonego timeout, w którym sprawdzana jest możliwość połączenia, program kończy działanie
###### Użytkownik przerywa pracę z systemem w czasie przetwarzania
1. Następuje czyszczenie zawartości programu. Program kończy swoje działanie.
###### Błąd systemu
1. System informuje użytkownika o błędzie i prosi o ponowienie próby za kilka minut.
